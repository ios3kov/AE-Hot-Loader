// Synthetic contract tests. No Adobe binary, SDK or installed component is used.
#include "../experiments/ordinary_discovery/ResourcePassGate.hpp"
#include <functional>
#include <iostream>
#include <set>

using namespace resource_pass;
static void Check(bool value) { if (!value) throw std::runtime_error("test assertion"); }
static Plan TestPlan() {
    Plan p;
    p.run_id = "resource-pass-" + std::string(32, '1');
    p.source_commit = std::string(40, '2');
    p.bridge_sha256 = std::string(64, '3');
    p.fixture_manifest_sha256 = std::string(64, '4');
    p.executable = "/owned/host/After Effects";
    p.root = "/owned/fresh/scan-root";
    p.match = "AEHL.Embedded.123456789abc";
    for (const auto& key : {"AfterEffects", "FILE", "FLT", "MEE", "PLUG", "PluginSupport", "aelib"})
        p.images[key] = std::string(64, '5');
    return p;
}
struct Model final : Backend {
    Plan p = TestPlan();
    Approval a{p, true, true};
    Observation base;
    std::uint64_t clock = 1;
    int creates = 0, releases = 0, searches = 0, observations = 0, checks = 0;
    bool claimed = false, marker = false, fail_create = false, fail_path = false;
    bool fail_marker = false, fail_search = false, release_ok = true, late = false;
    bool backclock = false, null_spec = false, mutate_fixture = false, fail_post = false;
    bool fail_claim = false, fail_before_save = false, fail_search_save = false, fail_after_save = false;
    SearchResult answer{0, 0, false};
    std::function<void(Observation&, int)> change = [](Observation&, int) {};
    std::vector<std::string> events;
    Model() {
        base.pid = 42; base.process_start = "new-process-start"; base.executable = p.executable;
        base.version = "25.6x101"; base.arch = "arm64"; base.bridge_sha256 = p.bridge_sha256;
        base.images = p.images;
        base.runtime_images = {
            {p.executable, 0x1000, 0},
            {"/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/PLUG.dylib", 0x2000, 16}
        };
        base.build = 101; base.main_thread = true;
        base.unsaved = true; base.dirty = false; base.rendering = false; base.revision = 1;
        base.registry = {"ADBE.A", "ADBE.B"};
    }
    std::uint64_t now_ms() override { return clock; }
    Observation observe() override {
        ++observations; events.push_back("observe");
        if (searches && fail_post) throw std::runtime_error("observer failed");
        auto o = base;
        if (searches) o.registry.push_back(p.match);
        change(o, observations);
        return o;
    }
    void verify_fixture(const Plan& q) override {
        Check(q.root == p.root); ++checks;
        if (mutate_fixture && checks == 2) throw std::runtime_error("changed fixture");
    }
    void claim(const Plan&, const Observation&) override {
        if (claimed || fail_claim) throw std::runtime_error("exclusive claim exists/failed");
        claimed = true; events.push_back("claim");
    }
    void save_observation(const char* name, const Observation&) override {
        events.push_back(name);
        if ((std::string(name) == "before" && fail_before_save) ||
            (std::string(name) == "after" && fail_after_save)) throw std::runtime_error("save failed");
    }
    void mark_call_started(const Plan&, const Observation&) override {
        if (fail_marker) throw std::runtime_error("marker failed");
        marker = true; events.push_back("marker");
    }
    Spec create_spec(const std::string& root) override {
        Check(root == p.root && claimed); ++creates; events.push_back("create");
        if (fail_create) throw std::runtime_error("construction failed");
        return {null_spec ? nullptr : this};
    }
    std::string spec_path(Spec s) override { Check(s.value == this); return fail_path ? "/wrong" : p.root; }
    SearchResult search_one_root(Spec s, std::uint64_t deadline) override {
        Check(s.value == this && marker && claimed); ++searches; events.push_back("search");
        if (late) clock = deadline;
        if (backclock) clock = 0;
        if (fail_search) throw std::runtime_error("private call failed with secret path");
        return answer;
    }
    void save_search_result(const SearchResult&) override {
        events.push_back("native");
        if (fail_search_save) throw std::runtime_error("search evidence failed");
    }
    bool release_spec(Spec s) noexcept override {
        if (s.value != this) return false;
        ++releases;
        return release_ok;
    }
    Result run() { return Run(p, a, *this); }
};
int main() {
    using Mutate = std::function<void(Model&)>;
    const std::vector<std::pair<std::string, Mutate>> preblocked = {
        {"no-new-authorization", [](Model& m) { m.a.new_private_call_authorized = false; }},
        {"unreviewed-native-contract", [](Model& m) { m.a.native_contract_reviewed = false; }},
        {"old-permission-run", [](Model& m) { m.a.scope.run_id.back() = '2'; }},
        {"different-approved-root", [](Model& m) { m.a.scope.root = "/different/scan-root"; }},
        {"different-approved-host", [](Model& m) { m.a.scope.executable += "2"; }},
        {"different-approved-images", [](Model& m) { m.a.scope.images["FILE"][0] = '1'; }},
        {"different-approved-source", [](Model& m) { m.a.scope.source_commit[0] = '1'; }},
        {"different-approved-deadline", [](Model& m) { ++m.a.scope.timeout_ms; }},
        {"missing-file-image-pin", [](Model& m) { m.p.images.erase("FILE"); }},
        {"malformed-image-pin", [](Model& m) { m.p.images["FILE"] = "unknown"; }},
        {"traversal-root", [](Model& m) { m.p.root = "/owned/../scan-root"; }},
        {"shared-root", [](Model& m) { m.p.root = "/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"; }},
        {"historical-fixture-reuse", [](Model& m) { m.p.match = "AEHL.Embedded.88019a1a01a7"; }},
        {"wrong-architecture", [](Model& m) { m.base.arch = "x86_64"; }},
        {"wrong-version", [](Model& m) { m.base.version = "25.6x100"; }},
        {"wrong-build", [](Model& m) { m.base.build = 100; }},
        {"off-main-thread", [](Model& m) { m.base.main_thread = false; }},
        {"saved-project", [](Model& m) { m.base.unsaved = false; }},
        {"dirty-project", [](Model& m) { m.base.dirty = true; }},
        {"nonempty-project", [](Model& m) { m.base.items = 1; }},
        {"queued-item", [](Model& m) { m.base.queued = 1; }},
        {"rendering", [](Model& m) { m.base.rendering = true; }},
        {"unloaded-host", [](Model& m) { m.base.pid = 0; }},
        {"missing-process-start", [](Model& m) { m.base.process_start.clear(); }},
        {"wrong-loaded-bridge", [](Model& m) { m.base.bridge_sha256[0] = '2'; }},
        {"wrong-loaded-module", [](Model& m) { m.base.images["PLUG"][0] = '2'; }},
        {"preexisting-fixture", [](Model& m) { m.base.registry.push_back(m.p.match); }},
        {"duplicate-registry", [](Model& m) { m.base.registry.push_back("ADBE.A"); }},
        {"empty-registry", [](Model& m) { m.base.registry.clear(); }},
        {"invalid-registry-name", [](Model& m) { m.base.registry.push_back("bad\nname"); }},
        {"clock-overflow", [](Model& m) { m.clock = UINT64_MAX; }},
        {"used-claim", [](Model& m) { m.claimed = true; }},
        {"claim-write-failure", [](Model& m) { m.fail_claim = true; }},
    };
    int count = 0;
    auto passed = [&](const std::string& name) { ++count; std::cout << "PASS " << name << '\n'; };
    try {
        for (const auto& test : preblocked) {
            Model m; test.second(m); auto r = m.run();
            Check(r.status == "BLOCKED" && !r.call_started && m.creates == 0 && m.searches == 0);
            passed(test.first);
        }
        const std::vector<std::pair<std::string, Mutate>> fails = {
            {"constructor-exception", [](Model& m) { m.fail_create = true; }},
            {"constructor-null", [](Model& m) { m.null_spec = true; }},
            {"path-roundtrip-mismatch", [](Model& m) { m.fail_path = true; }},
            {"fixture-changed-before-call", [](Model& m) { m.mutate_fixture = true; }},
            {"before-save-failure", [](Model& m) { m.fail_before_save = true; }},
            {"call-marker-failure", [](Model& m) { m.fail_marker = true; }},
            {"search-exception", [](Model& m) { m.fail_search = true; }},
            {"search-evidence-write-failure", [](Model& m) { m.fail_search_save = true; }},
            {"negative-search-result", [](Model& m) { m.answer.code = -1; }},
            {"positive-search-result", [](Model& m) { m.answer.code = 1; }},
            {"error-count", [](Model& m) { m.answer.errors = 1; }},
            {"cancelled-search", [](Model& m) { m.answer.cancelled = true; }},
            {"file-spec-release-failure", [](Model& m) { m.release_ok = false; }},
            {"deadline-expired", [](Model& m) { m.late = true; }},
            {"clock-reversed", [](Model& m) { m.backclock = true; }},
            {"postflight-unavailable", [](Model& m) { m.fail_post = true; }},
            {"after-save-failure", [](Model& m) { m.fail_after_save = true; }},
            {"process-replaced-before-call", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 2) o.pid++; }; }},
            {"pid-reused-after-call", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 3) o.process_start = "reused"; }; }},
            {"revision-changed-before-call", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 2) o.revision++; }; }},
            {"revision-changed-after-call", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 3) o.revision++; }; }},
            {"registry-changed-before-call", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 2) o.registry[0] = "Other"; }; }},
            {"image-only-no-registration", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 3) o.registry.pop_back(); }; }},
            {"unrelated-addition", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 3) o.registry.push_back("Other"); }; }},
            {"removed-effect", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 3) o.registry.erase(o.registry.begin()); }; }},
            {"duplicate-target", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 3) o.registry.push_back(o.registry.back()); }; }},
            {"module-changed-after-call", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 3) o.images["MEE"][0] = '1'; }; }},
            {"runtime-image-removed", [](Model& m) { m.change = [](Observation& o, int n) { if (n == 3) o.runtime_images.erase(o.runtime_images.begin()); }; }},
            {"unrelated-runtime-image-added", [](Model& m) { m.change = [](Observation& o, int n) {
                if (n == 3) o.runtime_images.push_back({"/Users/test/Unexpected.plugin/Contents/MacOS/Unexpected", 0x3000, 0});
            }; }},
        };
        for (const auto& test : fails) {
            Model m; test.second(m); auto r = m.run();
            Check(r.status == "FAIL" && r.claimed && m.searches <= 1);
            Check(m.releases == (m.creates && !m.fail_create && !m.null_spec ? 1 : 0));
            const auto first_searches = m.searches;
            Check(m.run().status == "BLOCKED" && m.searches == first_searches);
            passed(test.first);
        }
        Model good; auto r = good.run();
        Check(r.status == "PASS" && r.claimed && r.call_started && r.search_observed &&
              r.postflight_observed && r.cleanup_ok);
        Check(good.searches == 1 && good.creates == 1 && good.releases == 1 && good.checks == 3);
        Check(good.events == std::vector<std::string>{"observe", "claim", "before", "create", "observe", "marker", "search", "native", "observe", "after"});
        passed("exact-success-and-operation-order");
        Check(good.run().status == "BLOCKED" && good.searches == 1 && good.creates == 1);
        passed("successful-request-cannot-replay");
        Model system_lazy;
        system_lazy.change = [](Observation& o, int n) {
            if (n == 3) o.runtime_images.push_back({
                "/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/SafariPlatformSupport",
                0x3000, 0});
        };
        Check(system_lazy.run().status == "PASS"); passed("system-lazy-runtime-image-allowed");
        Model fixture_image;
        fixture_image.change = [](Observation& o, int n) {
            if (n == 3) o.runtime_images.push_back({
                "/owned/fresh/scan-root/AEHLPairEmbedded.plugin/Contents/MacOS/AEHLPairEmbedded",
                0x4000, 0});
        };
        Check(fixture_image.run().status == "PASS"); passed("fixture-runtime-image-allowed");
        Model missing_post; missing_post.fail_post = true; auto missing = missing_post.run();
        Check(missing.status == "FAIL" && !missing.postflight_observed && missing_post.observations == 3);
        passed("failed-postflight-not-retried");
        Model unicode; unicode.p.root = "/owned/тест с пробелами/scan-root"; unicode.a.scope = unicode.p;
        Check(unicode.run().status == "PASS"); passed("unicode-root");
        std::cout << "RESOURCE_GATE_TESTS=" << count << " PASS; scope=synthetic-unbound-backend\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "FAIL after " << count << " cases: " << e.what() << '\n';
        return 1;
    }
}
