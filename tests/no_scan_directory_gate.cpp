// Real journal files; synthetic host and directory call. No Adobe code.
#include "../experiments/ordinary_discovery/NoScanDirectoryJournal.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <sys/stat.h>
using namespace no_scan_directory;
namespace fs = std::filesystem;

static std::string current_case = "bootstrap";
static void Check(bool value) { if (!value) throw std::runtime_error("assertion:" + current_case); }
template<class F> static void Reject(F f) { bool failed=false; try { f(); } catch (...) { failed=true; } Check(failed); }
static std::string Read(const fs::path& p) { std::ifstream f(p, std::ios::binary); return {std::istreambuf_iterator<char>(f), {}}; }
static Plan TestPlan(const fs::path& directory) {
    Plan p;
    p.run_id = "directory-probe-" + std::string(32, '1');
    p.source_commit = std::string(40, '2');
    p.build_id = "noscan-123456789abc";
    p.executable = "/owned/Adobe After Effects";
    p.module_path = "/owned/AEHLNoScan.plugin/Contents/MacOS/AEHLNoScan";
    p.directory = directory.string();
    p.timeout_ms = 1000;
    return p;
}
struct Model final : JournaledBackend {
    Plan p;
    Approval a;
    Observation base;
    int calls=0, observations=0, directory_checks=0;
    std::uint64_t clock=1;
    bool throw_call=false;
    NativeResult native{true,true,true,2,2,1,1,3};
    std::function<void()> on_call;
    explicit Model(const fs::path& journal, const fs::path& directory)
        : JournaledBackend(journal.string()), p(TestPlan(directory)), a{p,true,true,true} {
        base.pid=123; base.process_start="123.456"; base.executable=p.executable;
        base.module_path=p.module_path; base.version="25.6x101"; base.build=101;
        base.arch="arm64"; base.main_thread=true; base.unsaved=true; base.dirty=false;
        base.rendering=false; base.items=0; base.queued=0; base.revision=7;
        base.registry={"ADBE.A","ADBE.B"};
        base.images={{"/owned/After Effects",0x1000,0},{"/owned/FILE.dylib",0x2000,16}};
    }
    std::uint64_t now_ms() override { return clock++; }
    Observation observe() override { ++observations; return base; }
    void verify_directory(const Plan& q) override {
        ++directory_checks; Check(q.directory==p.directory && fs::is_directory(q.directory));
    }
    NativeResult run_directory_probe(const Plan& q, const Approval& approval) override {
        Check(SamePlan(q,p) && SamePlan(approval.scope,p)); ++calls;
        if (on_call) on_call();
        if (throw_call) throw std::runtime_error("synthetic native failure");
        return native;
    }
    Result run() { return RunJournaled(p,a,*this); }
};

int main() {
    char tmp[]="/tmp/aehl-noscan-tests-XXXXXX";
    const char* made=mkdtemp(tmp); assert(made);
    const fs::path root = fs::canonical(fs::path(made));
    int cases=0;
    auto fixture=[&](const std::string& name) {
        current_case = name;
        const auto base=root/name; Check(fs::create_directory(base));
        const auto journal=base/"journal", directory=base/"probe-directory";
        Check(fs::create_directory(journal)); Check(fs::create_directory(directory));
        Check(::chmod(journal.c_str(),0700)==0); Check(::chmod(directory.c_str(),0700)==0);
        return std::pair<fs::path,fs::path>{journal,directory};
    };
    {
        auto [journal,directory]=fixture("pass"); Model m(journal,directory);
        const auto r=m.run();
        current_case="pass-result"; Check(r.status=="PASS" && r.stage=="complete" && r.cleanup_ok && r.native_observed);
        current_case="pass-counts"; Check(m.calls==1 && m.observations==3 && m.directory_checks==3);
        for (const auto& name : {"claim.txt","before.txt","call-started.txt","native.txt","after.txt","result.txt"}) {
            current_case=std::string("pass-file-")+name; Check(fs::is_regular_file(journal/name));
        }
        current_case="pass-result-bytes"; Check(Read(journal/"result.txt").find("no-scan-directory")!=std::string::npos);
        ++cases;
    }
    {
        auto [journal,directory]=fixture("approval"); Model m(journal,directory);
        m.a.private_file_call_authorized=false; const auto r=m.run();
        Check(r.status=="BLOCKED" && m.calls==0 && fs::is_empty(journal)); ++cases;
    }
    {
        auto [journal,directory]=fixture("dirty"); Model m(journal,directory);
        m.base.dirty=true; const auto r=m.run(); Check(r.status=="BLOCKED" && m.calls==0); ++cases;
    }
    {
        auto [journal,directory]=fixture("registry"); Model m(journal,directory);
        m.on_call=[&]{m.base.registry.push_back("AEHL.Unexpected");}; const auto r=m.run();
        Check(r.status=="FAIL" && r.call_started && m.calls==1 && m.observations==3); ++cases;
    }
    {
        auto [journal,directory]=fixture("images"); Model m(journal,directory);
        m.on_call=[&]{m.base.images.push_back({"/owned/new.dylib",0x3000,0});}; const auto r=m.run();
        Check(r.status=="FAIL" && m.calls==1); ++cases;
    }
    {
        auto [journal,directory]=fixture("system-lazy-image"); Model m(journal,directory);
        m.on_call=[&]{m.base.images.push_back(
            {"/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/SafariPlatformSupport",
             0x3000,0});};
        const auto r=m.run();
        Check(r.status=="PASS" && r.native_observed && m.calls==1);
        ++cases;
    }
    {
        auto [journal,directory]=fixture("project"); Model m(journal,directory);
        m.on_call=[&]{++m.base.revision;}; const auto r=m.run();
        Check(r.status=="FAIL" && m.calls==1); ++cases;
    }
    {
        auto [journal,directory]=fixture("lifetime"); Model m(journal,directory);
        m.native.spec_release_attempts=2; const auto r=m.run();
        Check(r.status=="FAIL" && m.calls==1); ++cases;
    }
    {
        auto [journal,directory]=fixture("retention"); Model m(journal,directory);
        m.native.retained_references=2; const auto r=m.run();
        Check(r.status=="FAIL" && m.calls==1); ++cases;
    }
    {
        auto [journal,directory]=fixture("throw"); Model m(journal,directory);
        m.throw_call=true; const auto r=m.run();
        Check(r.status=="FAIL" && r.call_started && !r.native_observed && r.postflight_observed && m.calls==1);
        Check(fs::is_regular_file(journal/"result.txt"));
        Check(!fs::exists(journal/"native.txt")); ++cases;
    }
    {
        auto [journal,directory]=fixture("timeout"); Model m(journal,directory);
        m.clock=1000; m.p.timeout_ms=1; m.a.scope=m.p; const auto r=m.run();
        Check(r.status=="BLOCKED" && m.calls==0); ++cases;
    }
    {
        auto [journal,directory]=fixture("replay"); Model first(journal,directory);
        Check(first.run().status=="PASS");
        Model second(journal,directory); const auto replay=second.run();
        Check(replay.status=="BLOCKED" && second.calls==0); ++cases;
    }
    fs::remove_all(root);
    std::cout << "NO_SCAN_DIRECTORY_GATE_TESTS=" << cases << " PASS; Adobe calls=0\n";
}
