#pragma once
// Public inventory only; no plug-in registration, acquisition or messages.
#include "PicaAvailability.hpp"
namespace pica_inventory {
using pica_probe::Acquired;
using pica_probe::Observation;
using pica_probe::Spec;
using pica_probe::Hex;
inline constexpr std::array<Spec,2> kSpecs{{{"SP Plug-ins Suite",4},{"SP Adapters Suite",3}}};
struct Plugin {
    std::int32_t file_error=0,path_error=0,adapter_error=0,name_error=0,version_error=0,version=0;
    std::string path,adapter;
};
struct Result {
    std::string status="STOPPED",stage="not-started",reason;
    std::vector<Acquired> suites;
    std::vector<Plugin> plugins;
    bool enumeration_complete=false;
};
struct Backend {
    virtual ~Backend()=default;
    virtual std::uint64_t now_ms()=0;
    virtual void record(const std::string&,const std::string&)=0;
    virtual Observation observe()=0;
    virtual Acquired acquire(const Spec&)=0;
    virtual void new_iterator()=0;
    virtual bool next_plugin(Plugin&)=0; // false only for documented NULL end
    virtual void delete_iterator()=0;
};
inline void Validate(const Plugin& p) {
    if(p.path.size()>4095||p.path.find('\0')!=p.path.npos||p.adapter.size()>256||
       p.adapter.find('\0')!=p.adapter.npos||
       ((p.file_error==0&&p.path_error==0)!=( !p.path.empty()))||
       (!p.path.empty()&&p.path.front()!='/')||
       ((p.adapter_error==0&&p.name_error==0&&p.version_error==0)!=(!p.adapter.empty())))
        throw std::runtime_error("plugin-getter-contract");
    if(p.file_error!=0&&p.path_error!=0)throw std::runtime_error("conversion-without-file");
    if(p.adapter_error!=0&&(p.name_error!=0||p.version_error!=0))
        throw std::runtime_error("getters-without-adapter");
}
inline std::string SerializePlugin(const Plugin& p) {
    return "file_error="+std::to_string(p.file_error)+"\npath_error="+std::to_string(p.path_error)+
      "\npath_hex="+Hex(p.path)+"\nadapter_error="+std::to_string(p.adapter_error)+"\nname_error="+std::to_string(p.name_error)+
      "\nversion_error="+std::to_string(p.version_error)+"\nadapter_name_hex="+Hex(p.adapter)+
      "\nadapter_version="+std::to_string(p.version)+"\n";
}
inline std::string Serialize(const Result& r) {
    std::string out="schema=PICA-INVENTORY-1\nstatus="+r.status+"\nstage="+r.stage+
      "\nreason_hex="+Hex(r.reason)+"\nsuite_count="+std::to_string(r.suites.size())+"\n";
    for(std::size_t i=0;i<r.suites.size();++i)out+="suite_name_hex="+Hex(kSpecs[i].name)+
      "\nsuite_version="+std::to_string(kSpecs[i].version)+"\nacquire_error="+std::to_string(r.suites[i].error)+
      "\nprovider_present="+(r.suites[i].present?std::string("1\n"):std::string("0\n"));
    out+="enumeration_complete="+std::string(r.enumeration_complete?"1\n":"0\n")+
      "plugin_count="+std::to_string(r.plugins.size())+"\n";
    for(const auto& p:r.plugins)out+=SerializePlugin(p);
    return out;
}
class Diagnostic {
    std::atomic<bool> consumed_{false};
public:
    Result run(Backend& b,const std::string& claim,std::uint64_t timeout=10000) {
        Result r;if(consumed_.exchange(true)){r.reason="already-consumed";return r;}
        bool iterator=false;std::uint64_t start=0;std::size_t payload=0;
        auto check=[&](){const auto now=b.now_ms();if(!timeout||timeout>15000||now<start||now-start>=timeout)
            throw std::runtime_error("deadline");};
        auto stage=[&](const std::string& name,const std::string& data=""){
            check();r.stage=name;b.record(name,data);check();};
        try {
            start=b.now_ms();
            if(claim.empty()||claim.size()>4096)throw std::runtime_error("invalid-claim");
            stage("claim",claim);stage("before-started");const auto before=b.observe();check();
            if(before.identity.empty()||before.project.empty()||before.registry.empty())throw std::runtime_error("empty-baseline");
            stage("before",Hex(before.identity)+"\n"+Hex(before.project)+"\n"+Hex(before.registry));
            for(std::size_t i=0;i<kSpecs.size();++i){stage("acquire-started-"+std::to_string(i));
                const auto value=b.acquire(kSpecs[i]);r.suites.push_back(value);check();
                stage("acquire-finished-"+std::to_string(i),Serialize(r));
                if(value.error!=0||!value.present)throw std::runtime_error("inventory-suite-unavailable");}
            stage("iterator-started");b.new_iterator();iterator=true;check();
            for(std::size_t i=0;i<=2048;++i){stage("next-started-"+std::to_string(i));Plugin p;
                if(!b.next_plugin(p)){r.enumeration_complete=true;check();break;}
                check();if(i==2048)throw std::runtime_error("plugin-limit");Validate(p);
                const auto delta=SerializePlugin(p);payload+=delta.size();
                if(payload>1024*1024)throw std::runtime_error("inventory-payload-limit");
                r.plugins.push_back(p);stage("next-finished-"+std::to_string(i),delta);}
            stage("iterator-delete-started");iterator=false;b.delete_iterator();check();stage("iterator-deleted");
            stage("after-started");const auto after=b.observe();check();
            stage("after",Hex(after.identity)+"\n"+Hex(after.project)+"\n"+Hex(after.registry));
            if(before.identity!=after.identity||before.project!=after.project||before.registry!=after.registry)
                throw std::runtime_error("host-state-changed");
            r.status="COMPLETE";r.stage="complete";
        }catch(const std::exception& e){r.reason=std::string(e.what()).substr(0,256);}
         catch(...){r.reason="unknown-exception";}
        if(iterator){iterator=false;try{b.record("iterator-delete-started","failure-path");b.delete_iterator();
            b.record("iterator-deleted","failure-path");}catch(...){r.reason+=";iterator-cleanup-failed";}}
        try{b.record("result",Serialize(r));}catch(...){r.status="STOPPED";r.reason+=";result-not-durable";}
        return r;
    }
};
} // namespace pica_inventory
