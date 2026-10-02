#include "../experiments/ordinary_discovery/RetainedIdentityTransaction.hpp"
#include <functional>
#include <iostream>
#include <thread>
namespace {
using namespace retained_transaction;
unsigned cases = 0;
void Check(bool value) { if (!value) throw std::runtime_error("transaction-test-assertion"); }
Plan MakePlan() {
    return {{"retained-identity-" + std::string(32, 'a'), std::string(40, 'b'),
        "identity-" + std::string(12, 'c'), std::string(64, 'd'),
        std::string(64, 'e'), std::string(32, 'f'), "owned-fixture", 73, 1, 2, 0x1000},
        "/Applications/AE/AE", "/tmp/identity.plugin", "/tmp/private-identity", 15000};
}
Observation MakeObservation(const Plan& p) {
    Observation o; o.measured = p.scope;
    o.host.pid = 73; o.host.process_start = "1.2"; o.host.executable = p.executable;
    o.host.module_path = p.module_path; o.host.version = "25.6x101"; o.host.build = 101;
    o.host.arch = "arm64"; o.host.main_thread = true; o.host.unsaved = true;
    o.host.dirty = false; o.host.rendering = false; o.host.revision = 1;
    o.host.registry = {"effect-a", "effect-b"};
    o.host.images = {{"/tmp/identity.plugin", 0x9000, 0}, {"/Applications/AE/MEE", 0x8000, 0}};
    return o;
}
struct EmptyMemory : mapped_memory::Backend {
    unsigned copies = 0;
    mapped_memory::Region query(retained_identity::Address) override { return {0x1000,16,0,1,2,0,3,3}; }
    retained_identity::Bytes copy(retained_identity::Address at, std::size_t size) override {
        Check(at == 0x1000 && size == 16); ++copies; return retained_identity::Bytes(16,0);
    }
};
struct Fake : Backend {
    Plan plan = MakePlan(); Observation observation = MakeObservation(plan);
    std::uint64_t time = 10;
    unsigned boundary = 0, observations = 0, claims = 0, markers = 0, captures = 0;
    unsigned saves = 0, posts = 0, finals = 0;
    std::string throw_at, expire_at, rollback_at;
    std::function<void(Fake&, unsigned)> change;
    std::function<void()> reenter;
    bool capture_fail = false; Result recorded;
    void Step(const std::string& name) {
        ++boundary;
        if (name == expire_at) time = 15010;
        if (name == rollback_at) time = 0;
        if (name == throw_at) throw std::runtime_error("injected-" + name);
    }
    std::uint64_t now_ms() override { ++boundary; return time; }
    Observation observe() override {
        ++observations; Step("observe" + std::to_string(observations));
        if (change) change(*this, observations);
        return observation;
    }
    void claim(const Plan& p, const Observation&) override {
        ++claims; Check(SamePlan(p, plan)); Step("claim"); if (reenter) reenter();
    }
    void mark_read(const Plan& p, const Observation&) override {
        ++markers; Check(SamePlan(p, plan)); Step("marker");
    }
    retained_capture::Diagnostic capture(const Plan& p) override {
        ++captures; Check(SamePlan(p, plan)); Step("capture");
        EmptyMemory memory; retained_capture::Observer observer;
        auto d = observer.run(retained_identity::Layout::Mee256Arm64, p.scope.root, memory);
        Check(d.success && memory.copies == 4 && d.frames.size() == 4);
        if (capture_fail) { d.success = false; d.failure = "injected-copy-failed"; }
        return d; // Actual capture core on owned fixture bytes; no host attestation.
    }
    void save_diagnostic(const retained_capture::Diagnostic&) override { ++saves; Step("save"); }
    void save_postflight(const Observation&) override { ++posts; Step("post"); }
    void save_result(const Result& r) override { ++finals; recorded = r; Step("final"); }
};
Result Run(Transaction& t, Fake& b) { return t.run(b.plan, {b.plan, true, true}, b); }
void Replay(Transaction& t, Fake& b) {
    const auto count = b.boundary; const auto r = Run(t, b);
    Check(r.status == "BLOCKED" && r.reason == "retained-transaction-consumed" && b.boundary == count);
}
} // namespace
int main() {
    try {
        { Transaction t; Fake b; const auto r = Run(t,b);
          Check(r.status == "PASS" && r.result_saved && !r.host_execution_verified &&
              b.observations == 3 && b.claims == 1 && b.markers == 1 && b.captures == 1 &&
              b.saves == 1 && b.posts == 1 && b.finals == 1); Replay(t,b); ++cases; }
        const std::vector<std::function<void(Plan&)>> invalid = {
            [](Plan& p){p.scope.run += "x";}, [](Plan& p){p.scope.root = 1;},
            [](Plan& p){p.scope.pid = 0;}, [](Plan& p){p.timeout_ms = 1;},
            [](Plan& p){p.executable = "relative";}, [](Plan& p){p.module_path += "/../x";},
            [](Plan& p){p.journal_directory += "/";}, [](Plan& p){p.scope.origin = "ae-diagnostic";}
        };
        for (const auto& edit : invalid) { Transaction t; Fake b; edit(b.plan);
            const auto r = Run(t,b); Check(r.status == "BLOCKED" && b.boundary == 0); Replay(t,b); ++cases; }
        for (unsigned i=0;i<4;++i) { Transaction t; Fake b; Approval a{b.plan,true,true};
            if(i==0)a.read_authorized=false; if(i==1)a.contract_reviewed=false;
            if(i==2)a.plan.scope.binary=std::string(64,'0'); if(i==3)a.plan.scope.root+=8;
            const auto r=t.run(b.plan,a,b); Check(r.status=="BLOCKED" && b.boundary==0); Replay(t,b); ++cases; }
        const std::vector<std::function<void(Observation&)>> corrupt = {
            [](Observation& o){++o.host.pid;}, [](Observation& o){o.host.process_start="1.3";},
            [](Observation& o){o.host.main_thread=false;}, [](Observation& o){o.host.dirty=true;},
            [](Observation& o){o.host.rendering=true;}, [](Observation& o){o.host.unsaved=false;},
            [](Observation& o){++o.host.items;}, [](Observation& o){++o.host.queued;},
            [](Observation& o){o.host.version="25.5";}, [](Observation& o){o.host.arch="x86_64";},
            [](Observation& o){o.host.registry.clear();}, [](Observation& o){o.host.images.clear();},
            [](Observation& o){o.measured.root+=8;}, [](Observation& o){o.measured.binary=std::string(64,'0');},
            [](Observation& o){o.measured.provider_uuid=std::string(32,'0');},
            [](Observation& o){o.measured.origin="ae-diagnostic";}
        };
        for (const auto& edit : corrupt) for(unsigned phase=1;phase<=3;++phase) {
            Transaction t; Fake b; b.change=[&](Fake& f,unsigned n){if(n==phase)edit(f.observation);};
            const auto r=Run(t,b); Check(r.status==(phase==1?"BLOCKED":"FAIL") && b.captures==(phase==3?1U:0U));
            Check(b.posts<=1 && b.finals<=1); Replay(t,b); ++cases;
        }
        for (unsigned phase : {2U,3U}) for (unsigned change=0;change<3;++change) {
            Transaction t; Fake b; b.change=[&](Fake& f,unsigned n){ if(n!=phase)return;
                if(change==0)++f.observation.host.revision;
                if(change==1)f.observation.host.registry.push_back("effect-c");
                if(change==2)f.observation.host.images.push_back({"/tmp/alien.plugin",0xa000,0}); };
            const auto r=Run(t,b); Check(r.status=="FAIL" && b.captures==(phase==3?1U:0U)); Replay(t,b); ++cases;
        }
        const std::vector<std::string> boundaries={"observe1","claim","observe2","marker","capture","save","observe3","post","final"};
        for (const auto& name:boundaries) for(unsigned mode=0;mode<3;++mode) {
            Transaction t; Fake b;
            if(mode==0)b.throw_at=name; if(mode==1)b.expire_at=name; if(mode==2)b.rollback_at=name;
            const auto r=Run(t,b); Check(r.status!="PASS" && b.claims<=1 && b.markers<=1 &&
                b.captures<=1 && b.posts<=1 && b.finals<=1);
            if(name=="marker" && mode!=0)Check(b.captures==0);
            if(name=="capture" && mode!=0)Check(b.saves==1);
            Replay(t,b); ++cases;
        }
        { Transaction t; Fake b; b.time=UINT64_MAX-14999; const auto r=Run(t,b);
          Check(r.status=="BLOCKED" && b.observations==0); Replay(t,b); ++cases; }
        { Transaction t; Fake b; b.capture_fail=true; const auto r=Run(t,b);
          Check(r.status=="FAIL" && b.saves==1 && b.posts==1 && b.finals==1); Replay(t,b); ++cases; }
        { Transaction t; Fake b; b.throw_at="marker"; b.change=[](Fake&,unsigned n){
              if(n==3)throw std::runtime_error("post\nsecret");};
          const auto r=Run(t,b); Check(r.reason=="injected-marker" && r.evidence_failure=="post?secret" && b.finals==1); ++cases; }
        { Transaction t; Fake b; Result nested;
          b.reenter=[&]{nested=Run(t,b);}; const auto r=Run(t,b);
          Check(r.status=="PASS" && nested.status=="BLOCKED" && b.captures==1); ++cases; }
        { Transaction t; Fake b; // Unique lazy image is retained.
          b.change=[](Fake& f,unsigned n){if(n==2)f.observation.host.images.push_back({"/System/Library/Lazy",0xa000,0});};
          Check(Run(t,b).status=="PASS"); ++cases; }
        { Transaction t; Fake b; Plan p=b.plan; Approval a{p,true,true};
          b.reenter=[&]{p.scope.root+=8;a.plan.scope.root+=8;};
          Check(t.run(p,a,b).status=="PASS" && b.captures==1); ++cases; }
        { Transaction t; Fake one,two; Result a,b;
          std::thread x([&]{a=Run(t,one);}), y([&]{b=Run(t,two);}); x.join();y.join();
          Check((a.status=="PASS")!=(b.status=="PASS") && one.captures+two.captures==1 &&
                ((a.status=="BLOCKED" && one.boundary==0)||(b.status=="BLOCKED" && two.boundary==0))); ++cases; }
        std::cout<<"RETAINED_TRANSACTION_CASES="<<cases<<" PASS; Adobe_calls=0; captures_one_shot=1\n";
    } catch(const std::exception& e) { std::cerr<<e.what()<<" after "<<cases<<" cases\n";return 1; }
}
