#include "../experiments/ordinary_discovery/PicaProbeContract.hpp"
#include <iostream>
#include <map>
#include <functional>
using namespace pica_probe;
struct Fake : Backend {
    std::uint64_t time = 1;
    std::map<std::string, std::string> records;
    std::vector<std::string> calls;
    std::function<void(const std::string&)> inject;
    int acquisitions = 0, next = 0, created = 0, deleted = 0, observed = 0;
    bool absent = false, contradictory = false, changed = false, endless = false, invalid = false;
    void event(const std::string& name) { calls.push_back(name); if (inject) inject(name); }
    std::uint64_t now_ms() override { return time; }
    void record(const std::string& n, const std::string& s) override {
        event("record:" + n); if (!records.emplace(n, s).second) throw std::runtime_error("duplicate-record");
    }
    Observation observe() override {
        event("observe"); ++observed;
        return {"owned-synthetic-host", "blank-project", changed && observed > 1 ? "changed" : "registry"};
    }
    Acquired acquire(const Spec&) override { event("acquire"); ++acquisitions;
        return contradictory ? Acquired{0, false} : absent ? Acquired{-1, false} : Acquired{0, true}; }
    void new_iterator() override { event("new"); ++created; }
    bool next_adapter(Adapter& a) override { event("next");
        if (!endless && next++ == 2) return false;
        a = {invalid ? std::string(257, 'x') : "owned-adapter", 3}; return true; }
    void delete_iterator() override { ++deleted; event("delete"); }
};
void Need(bool value) { if (!value) throw std::runtime_error("test-failed"); }
int main() {
    try {
        int cases = 0;
        { Fake b; Diagnostic d; auto r=d.run(b,"owned-claim");
          Need(r.status=="COMPLETE" && r.enumeration_complete && r.adapters.size()==2 &&
               b.acquisitions==4 && b.created==1 && b.deleted==1 && b.observed==2);
          Need(d.run(b,"owned-claim").reason=="already-consumed" && b.acquisitions==4); ++cases; }
        { Fake b; b.absent=true; Diagnostic d; auto r=d.run(b,"owned-claim");
          Need(r.status=="COMPLETE" && !r.enumeration_complete && b.created==0 && b.deleted==0); ++cases; }
        for (int mode=0; mode<4; ++mode) {
            Fake b; b.contradictory=mode==0; b.changed=mode==1; b.endless=mode==2; b.invalid=mode==3;
            Diagnostic d; auto r=d.run(b,"owned-claim"); Need(r.status=="STOPPED");
            Need(b.deleted==b.created && b.deleted<=1); ++cases;
        }
        for (const std::string event : {"record:claim","observe","acquire","new","next","delete",
                                       "record:before","record:acquire-finished-0","record:after","record:result"}) {
            Fake b; b.inject=[&](const auto& n){if(n==event)throw std::runtime_error("injected");};
            Diagnostic d; auto r=d.run(b,"owned-claim"); Need(r.status=="STOPPED");
            Need(b.deleted<=1); if(event=="record:claim")Need(b.acquisitions==0 && b.observed==0); ++cases;
        }
        for (const std::string event : {"record:before","acquire","next","delete"}) {
            Fake b; b.inject=[&](const auto& n){if(n==event)b.time=10001;};
            Diagnostic d; auto r=d.run(b,"owned-claim"); Need(r.status=="STOPPED" && r.reason.find("deadline")!=r.reason.npos);
            Need(b.deleted==b.created && b.deleted<=1); ++cases;
        }
        { Fake b; Diagnostic d; Need(d.run(b,"").status=="STOPPED" && b.acquisitions==0); ++cases; }
        { Fake b; Diagnostic d; Need(d.run(b,"owned",0).status=="STOPPED" && b.acquisitions==0); ++cases; }
        { Config c{"owned-run",std::string(40,'a'),"owned-build","/owned/host","/owned/module",
                   "/owned/control",std::string(32,'b'),std::string(64,'c')};
          const auto bytes=Request(c,73,"1.2",std::string(64,'d'));
          Need(Approve(c,73,"1.2",bytes)==std::string(64,'d'));
          for(std::size_t i=0;i<bytes.size();++i){auto bad=bytes;bad[i]='!';bool refused=false;
              try{(void)Approve(c,73,"1.2",bad);}catch(...){refused=true;}
              // Digest bytes may vary only within the validated hex alphabet.
              Need(refused);}
          bool refused=false;try{(void)Approve(c,74,"1.2",bytes);}catch(...){refused=true;}Need(refused);
          refused=false;try{(void)Approve(c,73,"1.3",bytes);}catch(...){refused=true;}Need(refused);++cases; }
        std::cout << "PICA policy " << cases << " owned/synthetic cases PASS; AE NOT RUN\n";
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
