#include "../experiments/ordinary_discovery/PicaInventoryContract.hpp"
#include <functional>
#include <iostream>
#include <map>
using namespace pica_inventory;
struct Fake:Backend {
    std::uint64_t time=1;
    std::map<std::string,std::string> records;
    std::function<void(const std::string&)> inject;
    int acquired=0,created=0,next=0,deleted=0,observed=0;
    bool unavailable=false,changed=false,empty=false,endless=false,path_error=false,adapter_error=false,invalid=false,large=false;
    void event(const std::string& n){if(inject)inject(n);}
    std::uint64_t now_ms()override{return time;}
    void record(const std::string& n,const std::string& data)override{
        event("record:"+n);if(!records.emplace(n,data).second)throw std::runtime_error("duplicate");}
    Observation observe()override{event("observe");++observed;return {"synthetic-host","owned-blank",changed&&observed>1?"changed":"registry"};}
    Acquired acquire(const Spec&)override{event("acquire");++acquired;return unavailable?Acquired{-1,false}:Acquired{0,true};}
    void new_iterator()override{event("new");++created;}
    bool next_plugin(Plugin& p)override{
        event("next");if(empty||(!endless&&next++==2))return false;
        p.path=invalid?std::string(4096,'x'):"/owned/fixture.plugin";if(large)p.path="/"+std::string(4094,'x');p.adapter="owned-adapter";p.version=1;
        if(path_error){p.path_error=-43;p.path.clear();}
        if(adapter_error){p.adapter_error=-1;p.adapter.clear();}
        return true;
    }
    void delete_iterator()override{++deleted;event("delete");}
};
void Need(bool b){if(!b)throw std::runtime_error("inventory-test");}
int main(){try{int cases=0;
    for(int mode=0;mode<5;++mode){Fake b;b.empty=mode==1;b.path_error=mode==2;b.adapter_error=mode==3;
        if(mode==4){b.path_error=true;b.adapter_error=true;}
        Diagnostic d;const auto r=d.run(b,"owned-claim");Need(r.status=="COMPLETE"&&r.enumeration_complete&&b.deleted==1);
        Need(d.run(b,"owned-claim").reason=="already-consumed"&&b.acquired==2);
        if(!b.empty)Need(b.records.at("next-finished-0")==SerializePlugin(r.plugins[0]));++cases;}
    for(int mode=0;mode<5;++mode){Fake b;b.unavailable=mode==0;b.changed=mode==1;b.endless=mode==2;b.invalid=mode==3;if(mode==4){b.endless=true;b.large=true;}
        Diagnostic d;const auto r=d.run(b,"owned-claim");Need(r.status=="STOPPED"&&b.deleted<=1&&b.created==b.deleted);
        if(mode==2)Need(r.reason=="plugin-limit");
        if(mode==4)Need(r.reason=="inventory-payload-limit");++cases;}
    for(const std::string n:{"record:claim","observe","acquire","new","next","delete",
                            "record:before","record:next-finished-0","record:after","record:result"}){
        Fake b;b.inject=[&](const auto& x){if(x==n)throw std::runtime_error("injected");};
        Diagnostic d;const auto r=d.run(b,"owned-claim");Need(r.status=="STOPPED"&&b.deleted<=1);
        if(n=="record:claim")Need(b.acquired==0&&b.observed==0);++cases;}
    for(const std::string n:{"record:before","acquire","next","delete"}){Fake b;b.inject=[&](const auto& x){if(x==n)b.time=10001;};
        Diagnostic d;const auto r=d.run(b,"owned-claim");Need(r.status=="STOPPED"&&r.reason.find("deadline")!=r.reason.npos&&b.deleted==b.created);++cases;}
    {Fake b;Diagnostic d;Need(d.run(b,"").status=="STOPPED"&&b.acquired==0);++cases;}
    {Fake b;Diagnostic d;Need(d.run(b,"owned",0).status=="STOPPED"&&b.acquired==0);++cases;}
    {Config c{"owned-run",std::string(40,'a'),"owned-build","/owned/host","/owned/module","/owned/control",std::string(32,'b'),std::string(64,'c')};
     auto body=pica_inventory::Request(c,12,"1.2",std::string(64,'d'));Need(body.find("kind=pica-inventory\n")!=body.npos&&body.find("plugin_inventory=authorized\n")!=body.npos);
     Need(pica_inventory::Approve(c,12,"1.2",body)==std::string(64,'d'));
     for(std::size_t i=0;i<body.size();++i){auto bad=body;bad[i]='!';bool refused=false;try{(void)pica_inventory::Approve(c,12,"1.2",bad);}catch(...){refused=true;}Need(refused);}
     bool refused=false;try{(void)pica_inventory::Approve(c,13,"1.2",body);}catch(...){refused=true;}Need(refused);++cases;}
    std::cout<<"PICA inventory policy "<<cases<<" owned/synthetic scenarios PASS; AE NOT RUN\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
