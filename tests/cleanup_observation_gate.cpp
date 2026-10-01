#include "../experiments/ordinary_discovery/CleanupObservationGate.hpp"
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
using namespace cleanup_observation;
static unsigned cases = 0;
static void Check(bool v) { if (!v) throw std::runtime_error("gate-test-assertion"); }
static Plan PlanFor(const std::string& journal = "/owned/journal") {
    return {"cleanup-observer-" + std::string(32, 'a'), std::string(40, 'b'), "observe-" + std::string(12, 'c'),
            "/owned/AE", "/owned/helper", journal, 15000};
}
static Observation SafeObservation() {
    Observation o; o.pid = 73; o.process_start = "1.2"; o.executable = "/owned/AE"; o.module_path = "/owned/helper";
    o.version = "25.6x101"; o.build = 101; o.arch = "arm64"; o.main_thread = o.unsaved = true;
    o.dirty = o.rendering = false; o.revision = 1; o.registry = {"Owned"}; o.images = {{"/owned/helper", 4096, 0}}; return o;
}
struct Fake : Backend {
    unsigned observations = 0, reads = 0, claims = 0, markers = 0, saved = 0, after = 0, finishes = 0;
    std::uint64_t clock = 1, step = 1;
    bool fail_read = false, fail_diagnostic = false, fail_claim = false, fail_finish = false;
    std::function<void(Fake&, Observation&)> on_observe;
    std::uint64_t now_ms() override { const auto n = clock; clock += step; return n; }
    Observation observe() override { ++observations; auto o = SafeObservation(); if (on_observe) on_observe(*this, o); return o; }
    void claim(const Plan&, const Observation&) override { Check(!claims++ && !fail_claim); }
    void save_before(const Observation&) override {}
    void mark_read(const Plan&, const Observation&) override { ++markers; }
    cleanup_observer::Diagnostic read() override {
        ++reads; Check(!fail_read); cleanup_observer::Diagnostic d; d.success = !fail_diagnostic; return d;
    }
    void save_diagnostic(const cleanup_observer::Diagnostic&) override { ++saved; }
    void save_after(const Observation&) override { ++after; }
    void finish(const Result&) override { ++finishes; Check(!fail_finish); }
};
static Result RunFake(Fake& f) { const auto p = PlanFor(); return Run(p, {p, true, true}, f); }
struct Disk : JournaledBackend {
    unsigned reads = 0;
    explicit Disk(const std::string& path) : JournaledBackend(path) {}
    std::uint64_t now_ms() override { return 1; }
    Observation observe() override { return SafeObservation(); }
    cleanup_observer::Diagnostic read() override { ++reads; cleanup_observer::Diagnostic d; d.success = true; return d; }
};
int main(int argc, char** argv) {
    try {
        { Fake f; const auto r = RunFake(f); Check(r.status == "PASS" && f.reads == 1 && f.observations == 3 &&
            r.read_started && r.diagnostic_saved && r.postflight_saved); const auto replay = RunFake(f);
          Check(replay.status == "BLOCKED" && f.reads == 1); ++cases; }
        for (unsigned bad = 0; bad < 8; ++bad) {
            Fake f; auto p = PlanFor(); Approval a{p, true, true};
            if (bad == 0) a.read_authorized = false; if (bad == 1) a.contract_reviewed = false;
            if (bad == 2) a.scope.source_commit[0] = 'a'; if (bad == 3) p.run_id = "directory-probe-" + std::string(32, 'a');
            if (bad == 4) p.build_id = "noscan-" + std::string(12, 'c'); if (bad == 5) p.timeout_ms = 1;
            if (bad == 6) p.executable = "/owned/../AE"; if (bad == 7) p.source_commit[0] = 'x';
            Check(Run(p, a, f).status == "BLOCKED" && f.reads == 0 && f.observations == 0); ++cases;
        }
        for (unsigned when : {1U, 2U, 3U}) {
            Fake f; f.on_observe = [when](Fake& x, Observation& o) { if (x.observations == when) ++o.revision; };
            const auto r = RunFake(f); Check(r.status != "PASS" && f.reads == (when == 3 ? 1U : 0U)); ++cases;
        }
        { Fake f; f.on_observe = [](Fake&, Observation& o) { o.dirty = true; };
          Check(RunFake(f).status == "BLOCKED" && f.claims == 0); ++cases; }
        { Fake f; f.fail_read = true; const auto r = RunFake(f);
          Check(r.status == "FAIL" && r.read_started && !r.diagnostic_saved && r.postflight_saved && f.reads == 1); ++cases; }
        { Fake f; f.fail_diagnostic = true; const auto r = RunFake(f);
          Check(r.status == "FAIL" && r.diagnostic_saved && r.postflight_saved); ++cases; }
        { Fake f; f.fail_finish = true; Check(RunFake(f).stage == "evidence"); ++cases; }
        { Fake f; f.step = 15000; Check(RunFake(f).status == "BLOCKED" && f.reads == 0); ++cases; }
        { Fake f; f.step = 5000; const auto r = RunFake(f); Check(r.status == "FAIL" && r.read_started && f.reads == 0); ++cases; }
        { Fake f; auto p = PlanFor(); const Approval a{p, true, true};
          f.on_observe = [&](Fake&, Observation&) { p.module_path = "/mutated/helper"; };
          Check(Run(p, a, f).status == "PASS"); ++cases; }
        Check(argc == 2); const std::filesystem::path root(argv[1]);
        { const auto folder = root / "complete"; std::filesystem::create_directory(folder);
          std::filesystem::permissions(folder, std::filesystem::perms::owner_all);
          Disk disk(folder.string()); const auto p = PlanFor(folder.string());
          Check(Run(p, {p, true, true}, disk).status == "PASS");
          Check(Run(p, {p, true, true}, disk).status == "BLOCKED" && disk.reads == 1);
          Check(std::distance(std::filesystem::directory_iterator(folder), {}) == 6); ++cases; }
        { const auto folder = root / "failed-diagnostic"; std::filesystem::create_directory(folder);
          std::filesystem::permissions(folder, std::filesystem::perms::owner_all);
          Disk disk(folder.string()); const auto p = PlanFor(folder.string()); auto o = SafeObservation();
          disk.claim(p, o); disk.save_before(o); disk.mark_read(p, o);
          cleanup_observer::Diagnostic d; disk.save_diagnostic(d); disk.save_after(o);
          bool refused = false; try { disk.finish({"PASS", "complete", "matching-diagnostic-only", true, true, true, true}); }
          catch (const std::exception&) { refused = true; } Check(refused); ++cases; }
        std::cout << "CLEANUP_OBSERVATION_GATE_CASES=" << cases << " PASS; synthetic_transport_only; Adobe_calls=0\n";
        return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
