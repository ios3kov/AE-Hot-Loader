// Separate potentially-loading public-suite diagnostic. Inert without exact scope.
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "SP/SPPlugs.h"
#include "SP/SPAccess.h"
#include "SP/SPAdapts.h"
#include "ResourcePassJournal.hpp"
#include "ResidentImageBinding.hpp"
#include "PicaInventoryContract.hpp"
#include "PicaInventoryConfig.hpp"
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
static_assert(kSPPluginsSuiteVersion4==4 && kSPAdaptersSuiteVersion==3);
static_assert(std::is_same_v<decltype(SPPlatformFileSpecification{}.mReference),FSRef>);
static_assert(std::is_same_v<decltype(SPPluginsSuite::GetPluginFileSpecification),SPErr (*)(SPPluginRef,SPPlatformFileSpecification*)>);
static_assert(std::is_same_v<decltype(SPXPlatPluginsSuite::GetPluginXplatFileSpec),SPErr (*)(SPPluginRef,XPlatFileSpec*)>);
static_assert(std::is_same_v<decltype(SPPluginsSuite::NewPluginListIterator),SPErr (*)(SPPluginListRef,SPPluginListIteratorRef*)>);
static_assert(std::is_same_v<decltype(SPPluginsSuite::NextPlugin),SPErr (*)(SPPluginListIteratorRef,SPPluginRef*)>);
static_assert(std::is_same_v<decltype(SPPluginsSuite::DeletePluginListIterator),SPErr (*)(SPPluginListIteratorRef)>);
static_assert(std::is_same_v<decltype(SPPluginsSuite::GetPluginAdapter),SPErr (*)(SPPluginRef,SPAdapterRef*)>);
#include "PicaProbeHost.hpp"

extern "C" __attribute__((visibility("default")))
const char* AEHL_PicaInventoryIdentity() { return research_identity; }
namespace {
resident_binding::Digest Digest(const std::string& hex) {
    Require(pica_inventory::HexValue(hex,64),"invalid-digest");
    resident_binding::Digest out{}; const std::string digits="0123456789abcdef";
    for(std::size_t i=0;i<32;++i)out[i]=static_cast<unsigned char>(
        (digits.find(hex[i*2])<<4)|digits.find(hex[i*2+1]));
    return out;
}
void VerifySelf(const std::string& sha) {
    const auto bound=resident_binding::Resolve({research_config.module,Digest(sha)},
                                              {"_AEHL_PicaInventoryIdentity"});
    Require(bound.functions.at("_AEHL_PicaInventoryIdentity")==
            reinterpret_cast<void*>(&AEHL_PicaInventoryIdentity),"loaded-self-export");
    (void)resident_binding::ReadPinned({research_config.executable,Digest(research_config.host_sha256)});
}
std::string Images() {
    std::string out;
    for(const auto& im:resident_binding::Snapshot())out+=pica_inventory::Hex(im.path)+","+
        std::to_string(im.header)+","+std::to_string(im.slide)+"\n";
    return out;
}
class PublicBackend final : public pica_inventory::Backend {
    const std::string sha_;
    const SPAdaptersSuite* adapters_=nullptr;
    const SPPluginsSuite* plugins_=nullptr;
    SPPluginListIteratorRef iterator_=nullptr;
    unsigned snapshots_=0;
    std::array<const void*,2> retained_{};
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
            "\nmodule_hex="+pica_inventory::Hex(ModulePath())+"\nbinary_sha256="+sha_+
            "\nphase="+phase+"\ndata_hex="+pica_inventory::Hex(data)+"\n");
    }
    pica_inventory::Observation observe() override {
        Require(pthread_main_np()==1,"off-main-thread");
        Require(CanonicalExecutable()==research_config.executable&&ModulePath()==research_config.module,"host-module-changed");
        VerifySelf(sha_);
        const auto project=SnapshotProject(); std::string registry;
        std::string known_evidence;
        for(const auto& known:research_known){
            (void)resident_binding::ReadPinned({known.module,Digest(known.sha)});
            (void)resident_binding::ReadPinned({known.resource,Digest(known.resource_sha)});
            Require(std::find(project.registry.begin(),project.registry.end(),known.match)!=project.registry.end(),"known-effect-not-registered");
            known_evidence+=pica_inventory::Hex(known.module)+","+known.sha+","+known.resource_sha+","+pica_inventory::Hex(known.match)+"\n";
        }
        record(snapshots_==0?"known-before":"known-after",known_evidence);
        for(const auto& n:project.registry)registry+=n+"\n";
        SaveControl(research_config.control,("images-"+std::to_string(snapshots_++)+".txt").c_str(),Images());
        return {std::to_string(getpid())+":"+StartIdentity()+":"+CanonicalExecutable()+":"+ModulePath()+":"+sha_,
                "25.6x101:blank-clean-idle:"+std::to_string(project.revision),registry};
    }
    pica_inventory::Acquired acquire(const pica_inventory::Spec& spec) override {
        Require(pthread_main_np()==1,"off-main-thread");
        const void* ptr=nullptr; const auto err=basic->AcquireSuite(spec.name,spec.version,&ptr);
        for(std::size_t i=0;i<pica_inventory::kSpecs.size();++i)
            if(std::strcmp(spec.name,pica_inventory::kSpecs[i].name)==0&&spec.version==pica_inventory::kSpecs[i].version)
                retained_[i]=ptr;
        if(err==0&&ptr&&std::strcmp(spec.name,kSPAdaptersSuite)==0)
            adapters_=static_cast<const SPAdaptersSuite*>(ptr);
        if(err==0&&ptr&&std::strcmp(spec.name,kSPPluginsSuite)==0)
            plugins_=static_cast<const SPPluginsSuite*>(ptr);
        // Deliberately no ReleaseSuite: bounded successful leases stay until host exit.
        return {err,ptr!=nullptr};
    }
    void new_iterator() override {
        Require(plugins_&&adapters_&&plugins_->NewPluginListIterator&&plugins_->NextPlugin&&
          plugins_->DeletePluginListIterator&&plugins_->GetPluginFileSpecification&&plugins_->GetPluginAdapter&&
          adapters_->GetAdapterName&&adapters_->GetAdapterVersion,"inventory-suite-methods");
        Require(plugins_->NewPluginListIterator(kSPRuntimePluginList,&iterator_)==0&&iterator_,"plugin-iterator-create");
    }
    bool next_plugin(pica_inventory::Plugin& out) override {
        SPPluginRef plugin=nullptr;
        Require(iterator_&&plugins_->NextPlugin(iterator_,&plugin)==0,"plugin-iterator-next");
        if(!plugin)return false;
        SPPlatformFileSpecification spec{};
        out.file_error=plugins_->GetPluginFileSpecification(plugin,&spec);
        if(out.file_error==0){
            std::array<UInt8,4096> path{};
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
            out.path_error=FSRefMakePath(&spec.mReference,path.data(),static_cast<UInt32>(path.size()));
#pragma clang diagnostic pop
            if(out.path_error==0){const auto n=strnlen(reinterpret_cast<const char*>(path.data()),path.size());
                Require(n>0&&n<path.size(),"file-path-termination");out.path.assign(reinterpret_cast<const char*>(path.data()),n);}
        }
        SPAdapterRef adapter=nullptr;
        out.adapter_error=plugins_->GetPluginAdapter(plugin,&adapter);
        if(out.adapter_error==0){Require(adapter,"null-plugin-adapter");const char* name=nullptr;int32 version=0;
            out.name_error=adapters_->GetAdapterName(adapter,&name);
            out.version_error=adapters_->GetAdapterVersion(adapter,&version);
            if(out.name_error==0&&out.version_error==0){Require(name,"null-adapter-name");
                for(std::size_t i=0;i<=256;++i){char c=0;const auto address=reinterpret_cast<std::uintptr_t>(name);
                    Require(address<=UINTPTR_MAX-i&&directory_spec::ReadSelfMemory(reinterpret_cast<const void*>(address+i),&c,1),"adapter-name-read");
                    if(!c){out.version=version;return true;}out.adapter+=c;}
                throw std::runtime_error("adapter-name-limit");}
        }
        return true;
    }
    void delete_iterator() override {
        const auto own=iterator_;iterator_=nullptr;
        Require(own&&plugins_->DeletePluginListIterator(own)==0,"plugin-iterator-delete");
    }
};
pica_inventory::Diagnostic diagnostic;
A_Err Idle(AEGP_GlobalRefcon,AEGP_IdleRefcon,A_long* max_sleep) {
    if(consumed)return 0;
    if(max_sleep&&*max_sleep>15)*max_sleep=15;
    try {
        Require(pthread_main_np()==1,"idle-thread");
        if(!ExistsControl(research_config.control,"request.txt"))return 0;
        consumed=true;
        const auto request=ReadControl(research_config.control,"request.txt",4096);
        const auto sha=pica_inventory::Approve(research_config,getpid(),StartIdentity(),request);
        VerifySelf(sha); PublicBackend backend(sha);
        const auto result=diagnostic.run(backend,request);
        SaveControl(research_config.control,"terminal.txt",pica_inventory::Serialize(result));
    } catch (...) {
        consumed=true;
        try{if(!ExistsControl(research_config.control,"terminal.txt"))
                SaveControl(research_config.control,"terminal.txt","schema=PICA-INVENTORY-1\nstatus=STOPPED\n");}
        catch(...){}
    }
    return 0;
}
static_assert(std::is_same_v<decltype(&Idle), AEGP_IdleHook>);
} // namespace
extern "C" __attribute__((visibility("default")))
A_Err EntryPointFunc(SPBasicSuite* suites,A_long,A_long,AEGP_PluginID id,AEGP_GlobalRefcon*) {
    try {
        const char* token=std::getenv("AEHL_PICA_INVENTORY_TOKEN");
        if(!suites||!token||research_config.token!=token||consumed||
           CanonicalExecutable()!=research_config.executable||ModulePath()!=research_config.module)return 0;
        PrivateDirectory(research_config.control);
        if(ExistsControl(research_config.control,"ready.txt")||ExistsControl(research_config.control,"request.txt"))return 0;
        basic=suites;plugin_id=id;
        Suite<AEGP_RegisterSuite5> registration(basic,kAEGPRegisterSuite,kAEGPRegisterSuiteVersion5);
        Require(registration.value->AEGP_RegisterIdleHook(id,Idle,nullptr)==0,"idle-register");
        registration.release_checked();
        SaveControl(research_config.control,"ready.txt",std::string(research_identity)+"\npid="+
            std::to_string(getpid())+"\nstart="+StartIdentity()+"\nmodule_hex="+pica_inventory::Hex(ModulePath())+"\n");
    } catch (...) {consumed=true;return 1;}
    return 0;
}
