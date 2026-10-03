// Research-only transaction policy. NO AE implementation, symbols or entrypoint.
// Backend is an unbound integration seam; tests use a synthetic implementation.
// Its attestations are not evidence of user consent or of a real host by themselves.
#pragma once
#include <algorithm>
#include <cstdint>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace resource_pass {
using Images = std::map<std::string, std::string>;
struct RuntimeImage {
    std::string path;
    std::uintptr_t header = 0;
    std::intptr_t slide = 0;
    bool operator==(const RuntimeImage& other) const {
        return path == other.path && header == other.header && slide == other.slide;
    }
};
struct Plan {
    std::string run_id, source_commit, bridge_sha256, fixture_manifest_sha256;
    // Digest of the complete reviewed callback target/context inventory, bound
    // by the external supervisor to this run and resident provider identities.
    std::string cleanup_inventory_sha256;
    // Exact review receipts: provider/interface ownership through dispatch,
    // exclusive publication window (including readers/MFR), and completion /
    // partial-failure stop-and-preserve semantics. Supervisor must verify their
    // contents and scope; a digest or synthetic attestation proves neither.
    std::string provider_contract_sha256, isolation_contract_sha256, completion_contract_sha256;
    std::string executable, root, match;
    Images images;
    std::uint64_t timeout_ms = 15000;
};
struct Approval {
    // Supplied by a separately reviewed supervisor, never inferred from a plan.
    Plan scope;
    bool new_private_call_authorized = false;
    bool native_contract_reviewed = false;
    // Independent, mandatory reviews; old aggregate approvals default to refusal.
    bool provider_contract_reviewed = false;
    bool isolation_contract_reviewed = false;
    bool completion_contract_reviewed = false;
};
struct CleanupObservation {
    // Missing information must never be interpreted as an empty vector.
    // These are unbound backend observations, not an implemented private reader.
    bool observed = false, complete = false;
    std::string inventory_sha256;
    std::uint64_t general_plugin_records = 0;
};
struct Observation {
    std::int64_t pid = 0;
    std::string process_start, executable, version, arch, bridge_sha256;
    Images images;
    std::vector<RuntimeImage> runtime_images;
    int build = 0;
    bool main_thread = false, unsaved = false, dirty = true, rendering = true;
    std::uint64_t items = 0, queued = 0, revision = 0;
    std::vector<std::string> registry;
    CleanupObservation cleanup;
};
struct SearchResult { int code = -1; int errors = -1; bool cancelled = true; };
struct Spec { const void* value = nullptr; }; // opaque token, NOT a FILE_Spec layout
struct Result {
    std::string status = "BLOCKED", stage = "validate", reason;
    bool claimed = false, call_started = false, search_observed = false, postflight_observed = false;
    bool cleanup_ok = true;
    // No apply/render conclusion is represented by this registration-only gate.
};
struct Backend {
    virtual ~Backend() = default;
    // Implementations must enforce limits and return fresh observations, not cache.
    virtual std::uint64_t now_ms() = 0; // monotonic clock, same units throughout
    virtual Observation observe() = 0;
    // Reuse scoped::VerifyScope with an exact manifest; no extra entries/links.
    virtual void verify_fixture(const Plan&) = 0;
    // Reuse scoped::Save: durable exclusive claim; existing/partial claims fail.
    virtual void claim(const Plan&, const Observation&) = 0;
    virtual void save_observation(const char*, const Observation&) = 0;
    virtual void mark_call_started(const Plan&, const Observation&) = 0;
    // Native adapter MUST use host-owned creation, exact path roundtrip and release.
    virtual Spec create_spec(const std::string& root) = 0;
    virtual std::string spec_path(Spec) = 0;
    virtual SearchResult search_one_root(Spec, std::uint64_t deadline_ms) = 0;
    virtual void save_search_result(const SearchResult&) = 0;
    virtual bool release_spec(Spec) noexcept = 0;
};
inline void Need(bool ok, const char* reason) {
    if (!ok) throw std::runtime_error(reason);
}
inline bool Hex(const std::string& s, std::size_t n) {
    return s.size() == n && s.find_first_not_of("0123456789abcdef") == std::string::npos;
}
inline bool Canonical(const std::string& s) {
    if (s.size() < 2 || s.size() > 4096 || s[0] != '/' || s.back() == '/') return false;
    std::size_t start = 1;
    while (start < s.size()) {
        const auto end = s.find('/', start);
        const auto part = s.substr(start, end == std::string::npos ? end : end - start);
        if (part.empty() || part == "." || part == "..") return false;
        for (const unsigned char c : part) if (c < 32 || c == 127) return false;
        if (end == std::string::npos) break;
        start = end + 1;
    }
    return true; // lexical only; backend must reject symlinks and verify ownership
}
inline void Validate(const Plan& p, const Approval& a) {
    Need(p.run_id.size() == 46 && p.run_id.rfind("resource-pass-", 0) == 0 &&
         Hex(p.run_id.substr(14), 32), "invalid-run-id");
    Need(Hex(p.source_commit, 40) && Hex(p.bridge_sha256, 64) &&
         Hex(p.fixture_manifest_sha256, 64), "invalid-source-or-artifact-identity");
    Need(Hex(p.cleanup_inventory_sha256, 64), "reviewed-cleanup-inventory-required");
    Need(Hex(p.provider_contract_sha256, 64) && a.provider_contract_reviewed,
         "provider-contract-required");
    Need(Hex(p.isolation_contract_sha256, 64) && a.isolation_contract_reviewed,
         "isolation-contract-required");
    Need(Hex(p.completion_contract_sha256, 64) && a.completion_contract_reviewed,
         "completion-contract-required");
    Need(Canonical(p.root) && Canonical(p.executable) &&
         p.root.size() >= 10 && p.root.substr(p.root.size() - 10) == "/scan-root",
         "invalid-owned-root-or-executable");
    Need(p.match.size() == 26 && p.match.rfind("AEHL.Embedded.", 0) == 0 &&
         Hex(p.match.substr(14), 12) && p.match != "AEHL.Embedded.88019a1a01a7",
         "fresh-embedded-fixture-required");
    Need(p.timeout_ms >= 1 && p.timeout_ms <= 15000, "invalid-deadline");
    const std::vector<std::string> keys = {
        "AfterEffects", "FILE", "U", "dvacore", "FLT", "MEE", "PLUG", "PluginSupport", "aelib"};
    Need(p.images.size() == keys.size(), "missing-image-pins");
    for (const auto& key : keys) {
        const auto it = p.images.find(key);
        Need(it != p.images.end() && Hex(it->second, 64), "missing-image-pins");
    }
    Need(a.native_contract_reviewed, "native-contract-not-reviewed");
    const auto& q = a.scope;
    Need(a.new_private_call_authorized && q.run_id == p.run_id &&
         q.source_commit == p.source_commit && q.bridge_sha256 == p.bridge_sha256 &&
         q.fixture_manifest_sha256 == p.fixture_manifest_sha256 && q.executable == p.executable &&
         q.cleanup_inventory_sha256 == p.cleanup_inventory_sha256 &&
         q.provider_contract_sha256 == p.provider_contract_sha256 &&
         q.isolation_contract_sha256 == p.isolation_contract_sha256 &&
         q.completion_contract_sha256 == p.completion_contract_sha256 &&
         q.root == p.root && q.match == p.match && q.images == p.images && q.timeout_ms == p.timeout_ms,
         "fresh-exact-authorization-required");
}
inline void ValidateRuntimeImages(const std::vector<RuntimeImage>& images) {
    Need(!images.empty() && images.size() <= 8192, "invalid-runtime-images");
    for (const auto& image : images)
        Need(Canonical(image.path) && image.header != 0, "invalid-runtime-images");
    auto sorted = images;
    std::sort(sorted.begin(), sorted.end(), [](const RuntimeImage& a, const RuntimeImage& b) {
        if (a.path != b.path) return a.path < b.path;
        if (a.header != b.header) return a.header < b.header;
        return a.slide < b.slide;
    });
    Need(std::adjacent_find(sorted.begin(), sorted.end()) == sorted.end(),
         "ambiguous-runtime-images");
}
inline bool AllowedNewRuntimeImage(const Plan& p, const RuntimeImage& image) {
    const std::string fixture_prefix = p.root + "/";
    return image.path.rfind("/System/Library/", 0) == 0 ||
           image.path.rfind(fixture_prefix, 0) == 0;
}
inline bool CompatibleRuntimeImages(const Plan& p,
                                    const std::vector<RuntimeImage>& before,
                                    const std::vector<RuntimeImage>& after) {
    for (const auto& image : before)
        if (std::find(after.begin(), after.end(), image) == after.end()) return false;
    for (const auto& image : after)
        if (std::find(before.begin(), before.end(), image) == before.end() &&
            !AllowedNewRuntimeImage(p, image)) return false;
    return true;
}
inline bool SameHost(const Plan& p, const Observation& a, const Observation& b) {
    return a.pid == b.pid && a.process_start == b.process_start &&
           a.executable == b.executable && a.bridge_sha256 == b.bridge_sha256 &&
           a.images == b.images && CompatibleRuntimeImages(p, a.runtime_images, b.runtime_images);
}
inline std::vector<std::string> Names(const Observation& o) {
    Need(!o.registry.empty() && o.registry.size() <= 20000, "invalid-registry");
    auto names = o.registry;
    for (const auto& name : names) {
        Need(!name.empty() && name.size() <= 1024, "invalid-registry");
        for (const unsigned char c : name) Need(c >= 32 && c != 127, "invalid-registry");
    }
    std::sort(names.begin(), names.end());
    Need(std::adjacent_find(names.begin(), names.end()) == names.end(), "ambiguous-registry");
    return names;
}
inline void Safe(const Plan& p, const Observation& o) {
    Need(o.pid > 0 && !o.process_start.empty() && o.process_start.size() <= 128 &&
         o.executable == p.executable && o.bridge_sha256 == p.bridge_sha256 &&
         o.images == p.images, "host-or-loaded-identity-mismatch");
    Need(o.version == "25.6x101" && o.build == 101 && o.arch == "arm64" &&
         o.main_thread, "wrong-host-or-thread");
    Need(o.unsaved && !o.dirty && !o.rendering && o.items == 0 && o.queued == 0 &&
         o.revision > 0, "project-not-blank-clean-idle");
    ValidateRuntimeImages(o.runtime_images);
}
inline void SafeCleanup(const Plan& p, const Observation& o) {
    Need(o.cleanup.observed && o.cleanup.complete &&
         Hex(o.cleanup.inventory_sha256, 64) &&
         o.cleanup.inventory_sha256 == p.cleanup_inventory_sha256,
         "cleanup-state-not-observed-or-reviewed");
    // PLUG_PrepRoutine success does not suppress MEE's saved entrypoint call.
    // No exception for "already prepped", KeepLoaded or null progress exists.
    Need(o.cleanup.general_plugin_records == 0, "retained-general-plugins-block-resource-pass");
    // Empty observed state is necessary, not sufficient: all callback effects,
    // readers and the private call still require separate native-contract review.
}
// A returned Result is NOT durable evidence until the external supervisor saves
// it and independently verifies the same PID/start, bytes and postflight.
inline Result Run(const Plan& supplied, const Approval& supplied_approval, Backend& backend) {
    // Freeze inputs: callbacks cannot retarget the current transaction by mutation.
    const Plan p = supplied;
    const Approval approval = supplied_approval;
    Result r;
    Spec spec;
    Observation before;
    std::vector<std::string> expected;
    std::uint64_t previous = 0, deadline = 0;
    bool postflight_attempted = false;
    auto tick = [&]() {
        const auto value = backend.now_ms();
        Need(value >= previous && value < deadline, "deadline-or-clock-failure");
        previous = value;
    };
    try {
        Validate(p, approval);
        previous = backend.now_ms();
        Need(previous <= UINT64_MAX - p.timeout_ms, "invalid-clock");
        deadline = previous + p.timeout_ms;
        r.stage = "baseline";
        backend.verify_fixture(p);
        before = backend.observe();
        Safe(p, before);
        SafeCleanup(p, before);
        expected = Names(before);
        Need(!std::binary_search(expected.begin(), expected.end(), p.match), "fixture-already-present");
        tick();
        r.stage = "claim";
        backend.claim(p, before);
        r.claimed = true;
        // Claim covers any later failure, including construction without a scan.
        backend.save_observation("before", before);
        r.stage = "file-spec";
        tick();
        spec = backend.create_spec(p.root);
        Need(spec.value != nullptr, "file-spec-creation-failed");
        Need(backend.spec_path(spec) == p.root, "file-spec-roundtrip-failed");
        backend.verify_fixture(p);
        const auto immediately_before = backend.observe();
        Safe(p, immediately_before);
        SafeCleanup(p, immediately_before);
        Need(SameHost(p, before, immediately_before) && before.revision == immediately_before.revision &&
             expected == Names(immediately_before), "baseline-changed-before-call");
        tick();
        r.stage = "call-marker";
        backend.mark_call_started(p, immediately_before);
        tick();
        r.call_started = true; // persisted marker exists; exception cannot authorize retry
        r.stage = "search";
        const auto search = backend.search_one_root(spec, deadline);
        backend.save_search_result(search);
        r.search_observed = true;
        r.cleanup_ok = backend.release_spec(spec);
        spec.value = nullptr;
        r.stage = "postflight";
        postflight_attempted = true;
        const auto after = backend.observe();
        r.postflight_observed = true;
        backend.save_observation("after", after);
        Safe(p, after);
        SafeCleanup(p, after);
        Need(SameHost(p, before, after) && before.revision == after.revision, "host-or-project-changed");
        tick();
        Need(search.code == 0 && search.errors == 0 && !search.cancelled, "search-error-or-cancel");
        Need(r.cleanup_ok, "file-spec-release-failed");
        r.stage = "registry";
        expected.push_back(p.match);
        std::sort(expected.begin(), expected.end());
        Need(Names(after) == expected, "registry-delta-not-exact-fixture");
        backend.verify_fixture(p);
        tick();
        r.stage = "complete";
        r.status = "PASS";
        r.reason = "registration-observation-only";
    } catch (const std::exception&) {
        // Do not expose exception text from backend: it may contain paths/tokens.
        r.status = r.claimed ? "FAIL" : "BLOCKED";
        r.reason = r.call_started ? "resource-pass-or-postflight-failed" : "precall-gate-failed";
    } catch (...) {
        r.status = r.claimed ? "FAIL" : "BLOCKED";
        r.reason = "unclassified-backend-failure";
    }
    if (spec.value) r.cleanup_ok = backend.release_spec(spec);
    if (r.claimed && !postflight_attempted) {
        // Retain a postflight even when construction/search threw. Never promotes FAIL.
        try {
            const auto after = backend.observe();
            r.postflight_observed = true;
            backend.save_observation("after", after);
        } catch (...) {}
    }
    return r;
}
} // namespace resource_pass
