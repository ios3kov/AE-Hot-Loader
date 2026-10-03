// Separate potentially-loading public-suite diagnostic. Inert without exact scope.
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "SP/SPPlugs.h"
#include "SP/SPAccess.h"
#include "SP/SPAdapts.h"
#include "ResourcePassJournal.hpp"
#include "ResidentImageBinding.hpp"
#include "PicaProbeContract.hpp"
#include "PicaAvailabilityConfig.hpp"
#include <cerrno>
#include <chrono>
#include <climits>
#include <cstring>
#include <cstdlib>
#include <dlfcn.h>
#include <filesystem>
#include <libproc.h>
#include <mach-o/dyld.h>
#include <pthread.h>
#include <sys/stat.h>
#include <unistd.h>
#include <type_traits>
static_assert(kSPPluginsSuiteVersion == 4 && kSPAdaptersSuiteVersion == 3 && kSPAccessSuiteVersion == 3);
static_assert(std::is_same_v<decltype(SPBasicSuite::AcquireSuite), SPErr (*)(const char*,int32,const void**)>);
static_assert(std::is_same_v<decltype(SPAdaptersSuite::NewAdapterListIterator), SPErr (*)(SPAdapterListRef,SPAdapterListIteratorRef*)>);
static_assert(std::is_same_v<decltype(SPAdaptersSuite::NextAdapter), SPErr (*)(SPAdapterListIteratorRef,SPAdapterRef*)>);
static_assert(std::is_same_v<decltype(SPAdaptersSuite::DeleteAdapterListIterator), SPErr (*)(SPAdapterListIteratorRef)>);
static_assert(std::is_same_v<decltype(SPAdaptersSuite::GetAdapterName), SPErr (*)(SPAdapterRef,const char**)>);
static_assert(std::is_same_v<decltype(SPAdaptersSuite::GetAdapterVersion), SPErr (*)(SPAdapterRef,int32*)>);
#include "PicaProbeHost.hpp"

extern "C" __attribute__((visibility("default")))
const char* AEHL_PicaBuildIdentity() { return research_identity; }
namespace {
resident_binding::Digest Digest(const std::string& hex) {
    Require(pica_probe::HexValue(hex,64),"invalid-digest");
    resident_binding::Digest out{}; const std::string digits="0123456789abcdef";
    for(std::size_t i=0;i<32;++i)out[i]=static_cast<unsigned char>(
        (digits.find(hex[i*2])<<4)|digits.find(hex[i*2+1]));
    return out;
}
void VerifySelf(const std::string& sha) {
    const auto bound=resident_binding::Resolve({research_config.module,Digest(sha)},
                                              {"_AEHL_PicaBuildIdentity"});
    Require(bound.functions.at("_AEHL_PicaBuildIdentity")==
            reinterpret_cast<void*>(&AEHL_PicaBuildIdentity),"loaded-self-export");
    (void)resident_binding::ReadPinned({research_config.executable,Digest(research_config.host_sha256)});
}
std::string Images() {
    std::string out;
    for(const auto& im:resident_binding::Snapshot())out+=pica_probe::Hex(im.path)+","+
        std::to_string(im.header)+","+std::to_string(im.slide)+"\n";
    return out;
}
class PublicBackend final : public pica_probe::Backend {
    const std::string sha_;
    const SPAdaptersSuite* adapters_=nullptr;
    SPAdapterListIteratorRef iterator_=nullptr;
    unsigned snapshots_=0;
    std::array<const void*,4> retained_{};
public:
    explicit PublicBackend(std::string sha):sha_(std::move(sha)){}
    std::uint64_t now_ms() override {
        return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count());
    }
    void record(const std::string& phase,const std::string& data) override {
        Require(!phase.empty()&&phase.size()<64&&phase.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789-")==phase.npos,
                "invalid-record-name");
        SaveControl(research_config.control,(phase+".txt").c_str(),
            "schema=PICA-JOURNAL-1\nrun="+research_config.run+"\nsource="+research_config.source+
            "\nbuild="+research_config.build+"\npid="+std::to_string(getpid())+"\nstart="+StartIdentity()+
            "\nmodule_hex="+pica_probe::Hex(ModulePath())+"\nbinary_sha256="+sha_+
            "\nphase="+phase+"\ndata_hex="+pica_probe::Hex(data)+"\n");
    }
    pica_probe::Observation observe() override {
        Require(pthread_main_np()==1,"off-main-thread");
        Require(CanonicalExecutable()==research_config.executable&&ModulePath()==research_config.module,"host-module-changed");
        VerifySelf(sha_);
        const auto project=SnapshotProject(); std::string registry;
        for(const auto& n:project.registry)registry+=n+"\n";
        SaveControl(research_config.control,("images-"+std::to_string(snapshots_++)+".txt").c_str(),Images());
        return {std::to_string(getpid())+":"+StartIdentity()+":"+CanonicalExecutable()+":"+ModulePath()+":"+sha_,
                "25.6x101:blank-clean-idle:"+std::to_string(project.revision),registry};
    }
    pica_probe::Acquired acquire(const pica_probe::Spec& spec) override {
        Require(pthread_main_np()==1,"off-main-thread");
        const void* ptr=nullptr; const auto err=basic->AcquireSuite(spec.name,spec.version,&ptr);
        for(std::size_t i=0;i<pica_probe::kSpecs.size();++i)
            if(std::strcmp(spec.name,pica_probe::kSpecs[i].name)==0&&spec.version==pica_probe::kSpecs[i].version)
                retained_[i]=ptr;
        if(err==0&&ptr&&std::strcmp(spec.name,kSPAdaptersSuite)==0)
            adapters_=static_cast<const SPAdaptersSuite*>(ptr);
        // Deliberately no ReleaseSuite: bounded successful leases stay until host exit.
        return {err,ptr!=nullptr};
    }
    void new_iterator() override {
        Require(adapters_&&adapters_->NewAdapterListIterator&&adapters_->NextAdapter&&
                adapters_->DeleteAdapterListIterator&&adapters_->GetAdapterName&&adapters_->GetAdapterVersion,
                "adapter-suite-methods");
        const auto err=adapters_->NewAdapterListIterator(kSPRuntimeAdapterList,&iterator_);
        Require(err==0&&iterator_,"iterator-create");
    }
    bool next_adapter(pica_probe::Adapter& out) override {
        SPAdapterRef adapter=nullptr;
        Require(iterator_&&adapters_->NextAdapter(iterator_,&adapter)==0,"iterator-next");
        if(!adapter)return false;
        const char* name=nullptr; int32 version=0;
        Require(adapters_->GetAdapterName(adapter,&name)==0&&name&&
                adapters_->GetAdapterVersion(adapter,&version)==0,"adapter-getters");
        // Copy only the public getter's borrowed name, bounded and mapping-safe.
        for(std::size_t i=0;i<=256;++i){char c=0;
            const auto address=reinterpret_cast<std::uintptr_t>(name);
            Require(address<=UINTPTR_MAX-i&&directory_spec::ReadSelfMemory(
                reinterpret_cast<const void*>(address+i),&c,1),"adapter-name-read");
            if(!c){out.version=version;return true;} out.name+=c;
        }
        throw std::runtime_error("adapter-name-limit");
    }
    void delete_iterator() override {
        const auto own=iterator_; iterator_=nullptr; // Consume exactly once before SDK.
        Require(own&&adapters_->DeleteAdapterListIterator(own)==0,"iterator-delete");
    }
};
pica_probe::Diagnostic diagnostic;
A_Err Idle(AEGP_GlobalRefcon,AEGP_IdleRefcon,A_long* max_sleep) {
    if(consumed)return 0;
    if(max_sleep&&*max_sleep>15)*max_sleep=15;
    try {
        Require(pthread_main_np()==1,"idle-thread");
        if(!ExistsControl(research_config.control,"request.txt"))return 0;
        consumed=true;
        const auto request=ReadControl(research_config.control,"request.txt",4096);
        const auto sha=pica_probe::Approve(research_config,getpid(),StartIdentity(),request);
        VerifySelf(sha); PublicBackend backend(sha);
        const auto result=diagnostic.run(backend,request);
        SaveControl(research_config.control,"terminal.txt",pica_probe::Serialize(result));
    } catch (...) {
        consumed=true;
        try{if(!ExistsControl(research_config.control,"terminal.txt"))
                SaveControl(research_config.control,"terminal.txt","schema=PICA-AVAILABILITY-1\nstatus=STOPPED\n");}
        catch(...){}
    }
    return 0;
}
static_assert(std::is_same_v<decltype(&Idle), AEGP_IdleHook>);
} // namespace
extern "C" __attribute__((visibility("default")))
A_Err EntryPointFunc(SPBasicSuite* suites,A_long,A_long,AEGP_PluginID id,AEGP_GlobalRefcon*) {
    try {
        const char* token=std::getenv("AEHL_PICA_AVAILABILITY_TOKEN");
        if(!suites||!token||research_config.token!=token||consumed||
           CanonicalExecutable()!=research_config.executable||ModulePath()!=research_config.module)return 0;
        PrivateDirectory(research_config.control);
        if(ExistsControl(research_config.control,"ready.txt")||ExistsControl(research_config.control,"request.txt"))return 0;
        basic=suites;plugin_id=id;
        Suite<AEGP_RegisterSuite5> registration(basic,kAEGPRegisterSuite,kAEGPRegisterSuiteVersion5);
        Require(registration.value->AEGP_RegisterIdleHook(id,Idle,nullptr)==0,"idle-register");
        registration.release_checked();
        SaveControl(research_config.control,"ready.txt",std::string(research_identity)+"\npid="+
            std::to_string(getpid())+"\nstart="+StartIdentity()+"\nmodule_hex="+pica_probe::Hex(ModulePath())+"\n");
    } catch (...) {consumed=true;return 1;}
    return 0;
}
