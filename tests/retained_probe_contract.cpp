#include "../experiments/ordinary_discovery/RetainedProbeContract.hpp"
#include <functional>
#include <iostream>
namespace {
using namespace retained_probe;
unsigned cases = 0;
void Check(bool v) { if (!v) throw std::runtime_error("probe-fixture-assertion"); }
retained_transaction::Plan Plan() {
    return {{"retained-identity-" + std::string(32, 'a'), std::string(40, 'b'),
        "identity-" + std::string(12, 'c'), std::string(64, 'd'), std::string(64, 'e'),
        std::string(32, 'f'), "owned-fixture", 73, 1, 2, 0x1000},
        "/Applications/AE/AE", "/tmp/probe.plugin", "/tmp/private-journal", 15000};
}
struct Bound : BindingBackend {
    Binding value{Plan().scope, {{"/tmp/probe.plugin",0x9000,0},{"/Applications/AE/MEE",0x8000,0}}};
    unsigned calls = 0; std::function<void(Bound&)> change;
    Binding measure() override { ++calls; if(change)change(*this); return value; }
};
struct Memory : mapped_memory::Backend {
    retained_identity::Bytes data = retained_identity::Bytes(0x2000,0);
    unsigned copies = 0; bool fail = false;
    static void Put(retained_identity::Bytes& b, std::size_t at, std::uint64_t v) {
        for(unsigned i=0;i<8;++i)b.at(at+i)=static_cast<unsigned char>(v>>(8*i));
    }
    Memory() { Put(data,0,0x2000); Put(data,8,0x20b0); Put(data,0x1000,0x9000);
        data[0x1090]='N'; data[0x1091]=0xff; data[0x10a7]=2; }
    mapped_memory::Region query(retained_identity::Address) override { return {0x1000,0x2000,0,1,2,0,3,3}; }
    retained_identity::Bytes copy(retained_identity::Address at,std::size_t size) override {
        ++copies; if(fail && copies==2)throw std::runtime_error("fixture-copy-failed");
        Check(at>=0x1000 && at-0x1000+size<=data.size());
        return {data.begin()+(at-0x1000), data.begin()+(at-0x1000)+size};
    }
};
void Replay(Capture& c, Bound& b, Memory& m) {
    const auto reads=m.copies, bindings=b.calls; const auto d=c.run(Plan(),b,m);
    Check(!d.success && d.failure=="retained-probe-capture-consumed" &&
          m.copies==reads && b.calls==bindings);
}
} // namespace
int main() {
    try {
        { Capture c;Bound b;Memory m;auto d=c.run(Plan(),b,m);
          Check(d.success && b.calls==2 && m.copies==6 && d.frames.size()==6 &&
                d.identities.size()==1 && d.identities[0].name==retained_identity::Bytes({'N',0xff}));
          Replay(c,b,m); ++cases; }
        const std::vector<std::function<void(Binding&)>> changes = {
            [](Binding&b){b.scope.binary=std::string(64,'1');}, [](Binding&b){b.scope.source=std::string(40,'1');},
            [](Binding&b){++b.scope.pid;}, [](Binding&b){++b.scope.start_usec;}, [](Binding&b){b.scope.root+=8;},
            [](Binding&b){b.scope.provider_sha=std::string(64,'1');}, [](Binding&b){b.scope.provider_uuid=std::string(32,'1');},
            [](Binding&b){b.scope.run.back()='1';}, [](Binding&b){b.scope.build.back()='1';},
            [](Binding&b){b.scope.origin="ae-diagnostic";}
        };
        for(unsigned when : {1U,2U})for(const auto&change:changes) {
            Capture c;Bound b;Memory m;b.change=[&](Bound&v){if(v.calls==when)change(v.value);};
            auto d=c.run(Plan(),b,m);Check(!d.success && d.identities.empty() && d.snapshot.vector.empty() &&
                m.copies==(when==1?0U:6U) && d.frames.size()==m.copies);Replay(c,b,m);++cases;
        }
        const std::vector<std::function<void(Binding&)>> images = {
            [](Binding&b){++b.images[0].header;}, [](Binding&b){++b.images[1].slide;},
            [](Binding&b){b.images[1].path+="-changed";}, [](Binding&b){b.images.pop_back();},
            [](Binding&b){b.images.push_back({"/System/Library/late",0xa000,0});},
            [](Binding&b){std::swap(b.images[0],b.images[1]);}
        };
        for(const auto&change:images) {
            Capture c;Bound b;Memory m;b.change=[&](Bound&v){if(v.calls==2)change(v.value);};
            auto d=c.run(Plan(),b,m);Check(!d.success && d.frames.size()==6 && d.identities.empty());
            Replay(c,b,m);++cases;
        }
        for(unsigned when : {1U,2U})for(bool unknown : {false,true}) {
            Capture c;Bound b;Memory m;b.change=[&](Bound&v){if(v.calls==when){if(unknown)throw 1;
                throw std::runtime_error("fixture-binding-failed");}};
            auto d=c.run(Plan(),b,m);Check(!d.success && d.frames.size()==(when==1?0U:6U) &&
                d.identities.empty() && !d.failure.empty());Replay(c,b,m);++cases;
        }
        { Capture c;Bound b;Memory m;m.fail=true;auto d=c.run(Plan(),b,m);
          Check(!d.success && b.calls==2 && d.frames.size()==1 && d.identities.empty());
          Replay(c,b,m);++cases; }
        { Capture c;Bound b;Memory m;auto bad=Plan();bad.timeout_ms=1;auto d=c.run(bad,b,m);
          Check(!d.success && !b.calls && !m.copies);Replay(c,b,m);++cases; }
        { Capture c;Bound b;Memory m;b.change=[&](Bound&v){if(v.calls==1) {
            auto inner=c.run(Plan(),b,m);Check(inner.failure=="retained-probe-capture-consumed");}};
          Check(c.run(Plan(),b,m).success && m.copies==6);Replay(c,b,m);++cases; }
        const auto p=Plan();Config config{p.scope.run,p.scope.source,p.scope.build,p.executable,p.module_path,
            p.journal_directory,"/tmp/private-control",std::string(32,'a')};
        const auto bytes=Request(config,73,"1.2",p.scope.binary);
        Check(ApproveRequest(config,73,"1.2",bytes)==p.scope.binary);++cases;
        // Every non-digest byte is exact: mutations cannot retarget identity/approval/token.
        const auto digest=bytes.find("binary_sha256=")+14;
        for(std::size_t i=0;i<bytes.size();++i) {
            if(i>=digest && i<digest+64)continue;
            auto edited=bytes;edited[i]=edited[i]=='X'?'Y':'X';bool rejected=false;
            try{(void)ApproveRequest(config,73,"1.2",edited);}catch(...){rejected=true;}
            Check(rejected);
        } ++cases;
        for(const auto&edited:std::vector<std::string>{bytes+"\n",bytes.substr(1),
              Request(config,74,"1.2",p.scope.binary),Request(config,73,"1.3",p.scope.binary),
              bytes.substr(0,digest)+std::string(64,'z')+bytes.substr(digest+64)}) {
            bool rejected=false;try{(void)ApproveRequest(config,73,"1.2",edited);}catch(...){rejected=true;}
            Check(rejected);++cases;
        }
        std::cout<<"RETAINED_PROBE_CASES="<<cases<<" PASS; Adobe_calls=0; installs=0\n";return 0;
    } catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
