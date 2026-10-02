#include "../experiments/ordinary_discovery/RetainedHostJournal.hpp"
#include <filesystem>
#include <iostream>
namespace {
using namespace retained_transaction;
namespace fs = std::filesystem;
void Check(bool v) { if(!v)throw std::runtime_error("host-journal-fixture-assertion"); }
void Put(retained_identity::Bytes& b, std::size_t at, std::uint64_t value) {
    for(unsigned i=0;i<8;++i)b.at(at+i)=static_cast<unsigned char>(value>>(8*i));
}
struct Memory : mapped_memory::Backend {
    retained_identity::Bytes data = retained_identity::Bytes(0x5000, 0);
    bool fail = false;
    Memory(unsigned count, bool external) {
        Put(data,0,count?0x2000:0);Put(data,8,count?0x2000+count*0xb0:0);
        for(unsigned i=0;i<count;++i) {
            const auto at=0x1000+i*0xb0;
            if(external) { Put(data,at+0x90,0x3000);Put(data,at+0x98,255);data[at+0xa7]=0x80;
                std::fill(data.begin()+0x2000,data.begin()+0x20ff,0xff);data[0x2001]=0; }
            else { data[at+0x90]='O';data[at+0x91]=0xff;data[at+0x92]=0;data[at+0x93]='Z';data[at+0xa7]=4; }
        }
    }
    mapped_memory::Region query(std::uint64_t) override { return {0x1000,0x5000,0,1,2,0,3,3}; }
    retained_identity::Bytes copy(std::uint64_t at,std::size_t n) override {
        if(fail)throw std::runtime_error("owned-copy-failed");
        Check(at>=0x1000 && at-0x1000+n<=data.size());
        const auto start=data.begin()+at-0x1000;return {start,start+n};
    }
};
Plan MakePlan(const fs::path& directory) {
    return {{"retained-identity-"+std::string(32,'a'),std::string(40,'b'),"identity-"+std::string(12,'c'),
        std::string(64,'d'),std::string(64,'e'),std::string(32,'f'),"owned-fixture",73,1,2,0x1000},
        "/Applications/AE/AE","/tmp/identity.plugin",directory.string(),15000};
}
Observation MakeObservation(const Plan& p) {
    Observation o;o.measured=p.scope;
    auto& h=o.host;h.pid=73;h.process_start="1.2";h.executable=p.executable;h.module_path=p.module_path;
    h.version="25.6x101";h.arch="arm64";h.build=101;h.main_thread=true;h.unsaved=true;
    h.dirty=false;h.rendering=false;h.revision=1;
    h.registry={"effect-a",std::string("effect-")+static_cast<char>(0xff)};
    h.images={{p.module_path,0x9000,-4096},{"/Applications/AE/MEE",0x8000,0}};
    return o;
}
struct Producer : HostJournaledBackend {
    Plan plan;Observation current;Memory memory;
    std::string scenario;unsigned observations=0,captures=0;
    Producer(const fs::path& directory,unsigned count=0,bool external=false)
        :HostJournaledBackend(directory.string()),plan(MakePlan(directory)),current(MakeObservation(plan)),memory(count,external) {}
    std::uint64_t now_ms() override {
        if(scenario=="expired-marker" && fs::exists(fs::path(plan.journal_directory)/"call-started.txt"))return 15010;
        if(scenario=="expired-final" && fs::exists(fs::path(plan.journal_directory)/"result.txt"))return 15010;
        return 10;
    }
    Observation observe() override {
        ++observations;
        if(observations==2 && scenario=="changed-before")++current.host.revision;
        if(observations==3 && scenario=="changed-after")current.host.dirty=true;
        if(observations==3 && scenario=="failed-post")throw std::runtime_error("owned-post-failed");
        if(observations==2 && scenario=="lazy-system")current.host.images.push_back({"/System/Library/Lazy",0xa000,0});
        return current;
    }
    retained_capture::Diagnostic capture(const Plan& p) override {
        ++captures;retained_capture::Observer observer;
        memory.fail=scenario=="failed-capture";
        return observer.run(retained_identity::Layout::Mee256Arm64,p.scope.root,memory);
    }
};
fs::path Folder(const fs::path& base,const std::string& name) {
    const auto path=base/name;Check(fs::create_directory(path));fs::permissions(path,fs::perms::owner_all);return path;
}
template<class F> void Refuse(F f) { bool bad=false;try{f();}catch(const std::exception&){bad=true;}Check(bad); }
} // namespace
int main(int argc,char** argv) {
    try {
        Check(argc==2);const fs::path base(argv[1]);unsigned cases=0;
        for(const auto& sample: {std::make_pair(0U,false),std::make_pair(2U,false),std::make_pair(8U,true)}) {
            const auto name=sample.first==0?"empty":sample.first==2?"inline":"maximum";
            Producer b(Folder(base,name),sample.first,sample.second);Transaction t;
            const auto r=t.run(b.plan,{b.plan,true,true},b);
            Check(r.status=="PASS" && r.result_saved && b.captures==1);
            Check(t.run(b.plan,{b.plan,true,true},b).status=="BLOCKED" && b.captures==1);++cases;
        }
        for(const auto& name: {"changed-before","changed-after","failed-post","failed-capture","expired-marker","expired-final","lazy-system"}) {
            Producer b(Folder(base,name),2);b.scenario=name;Transaction t;
            const auto r=t.run(b.plan,{b.plan,true,true},b);
            Check(r.status==(b.scenario=="lazy-system"?"PASS":"FAIL"));
            if(b.scenario=="changed-before" || b.scenario=="expired-marker")Check(b.captures==0);
            else Check(b.captures==1);
            Check(t.run(b.plan,{b.plan,true,true},b).status=="BLOCKED");++cases;
        }
        { Producer b(Folder(base,"large-host"),2);b.current.host.registry.clear();
          for(unsigned i=0;i<785;++i)b.current.host.registry.push_back("effect-"+std::to_string(i));
          for(unsigned i=0;i<80;++i)b.current.host.images.push_back({"/Applications/AE/image-"+std::to_string(i),0xa000+i,0});
          Transaction t;Check(t.run(b.plan,{b.plan,true,true},b).status=="PASS");++cases; }
        { Producer b(Folder(base,"large-bytes"));b.current.host.registry.clear();
          for(unsigned i=0;i<2500;++i){auto name=std::to_string(i);name.resize(1024,'x');b.current.host.registry.push_back(name);}
          Refuse([&]{b.claim(b.plan,b.current);});Check(fs::is_empty(b.plan.journal_directory));++cases; }
        { Producer b(Folder(base,"poison"));Refuse([&]{b.mark_read(b.plan,b.current);});
          Refuse([&]{b.claim(b.plan,b.current);});Check(fs::is_empty(b.plan.journal_directory));++cases; }
        { Producer b(Folder(base,"path"));auto p=b.plan;p.journal_directory+="-elsewhere";
          Refuse([&]{b.claim(p,b.current);});Refuse([&]{b.claim(b.plan,b.current);});++cases; }
        { Producer b(Folder(base,"replayed-marker"));b.claim(b.plan,b.current);b.mark_read(b.plan,b.current);
          Refuse([&]{b.mark_read(b.plan,b.current);});Refuse([&]{b.save_postflight(b.current);});++cases; }
        { Producer b(Folder(base,"changed-plan"));b.claim(b.plan,b.current);auto p=b.plan;p.scope.binary=std::string(64,'0');
          Refuse([&]{b.mark_read(p,b.current);});Refuse([&]{b.mark_read(b.plan,b.current);});++cases; }
        { Producer b(Folder(base,"oversize"));b.current.host.registry.assign(20001,"effect");
          Refuse([&]{b.claim(b.plan,b.current);});Check(fs::is_empty(b.plan.journal_directory));++cases; }
        { Producer b(Folder(base,"invalid-native"));b.claim(b.plan,b.current);b.mark_read(b.plan,b.current);
          retained_capture::Diagnostic d;d.calls=23;
          Refuse([&]{b.save_diagnostic(d);});Refuse([&]{b.save_postflight(b.current);});++cases; }
        { Producer b(Folder(base,"forged-pass"));b.claim(b.plan,b.current);b.save_postflight(b.current);
          Result r;r.status="PASS";r.consumed=r.claim_attempted=r.claimed=true;
          Refuse([&]{b.save_result(r);});++cases; }
        std::cout<<"RETAINED_HOST_JOURNAL_CASES="<<cases<<" PASS; Adobe_calls=0; installs=0\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
