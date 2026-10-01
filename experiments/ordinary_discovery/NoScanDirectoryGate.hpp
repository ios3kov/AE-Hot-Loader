// Research-only no-scan directory probe transaction. No plugin search/registration.
// The gate does not grant consent: approval fields must be bound by an external,
// separately reviewed supervisor before any retained reference or private FILE call.
#pragma once
#include "DirectorySpecAdapter.hpp"
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace no_scan_directory {
struct RuntimeImage {
    std::string path;
    std::uintptr_t header = 0;
    std::intptr_t slide = 0;
    bool operator==(const RuntimeImage& other) const {
        return path == other.path && header == other.header && slide == other.slide;
    }
};
struct Plan {
    std::string run_id, source_commit, build_id;
    std::string executable, module_path, directory;
    std::uint64_t timeout_ms = 15000;
};
struct Config {
    Plan plan;
    std::string token, control_directory, journal_directory;
};
struct Approval {
    Plan scope;
    bool private_file_call_authorized = false;
    bool provider_reference_retention_authorized = false;
    bool native_contract_reviewed = false;
};
struct Observation {
    std::int64_t pid = 0;
    std::string process_start, executable, module_path, version, arch;
    int build = 0;
    bool main_thread = false, unsaved = false, dirty = true, rendering = true;
    std::uint64_t items = 0, queued = 0, revision = 0;
    std::vector<std::string> registry;
    std::vector<RuntimeImage> images;
};
struct NativeResult {
    bool completed = false, invoked = false, cleanup_ok = false;
    unsigned strings_created = 0, string_release_attempts = 0;
    unsigned specs_created = 0, spec_release_attempts = 0;
    unsigned retained_references = 0;
};
struct Result {
    std::string status = "BLOCKED", stage = "validate", reason;
    bool claimed = false, call_started = false, native_observed = false, postflight_observed = false;
    bool cleanup_ok = false;
};
struct Backend {
    virtual ~Backend() = default;
    virtual std::uint64_t now_ms() = 0;
    virtual Observation observe() = 0;
    virtual void verify_directory(const Plan&) = 0;
    virtual void claim(const Plan&, const Observation&) = 0;
    virtual void save_observation(const char*, const Observation&) = 0;
    virtual void mark_call_started(const Plan&, const Observation&) = 0;
    virtual NativeResult run_directory_probe(const Plan&, const Approval&) = 0;
    virtual void save_native_result(const NativeResult&) = 0;
};
inline void Need(bool ok, const char* reason) {
    if (!ok) throw std::runtime_error(reason);
}
inline bool Hex(const std::string& s, std::size_t n) {
    return s.size() == n && s.find_first_not_of("0123456789abcdef") == std::string::npos;
}
inline bool Canonical(const std::string& s) {
    if (s.size() < 2 || s.size() > directory_spec::kMaxPath || s.front() != '/' || s.back() == '/')
        return false;
    std::size_t start = 1;
    while (start < s.size()) {
        const auto end = s.find('/', start);
        const auto part = s.substr(start, end == std::string::npos ? end : end - start);
        if (part.empty() || part == "." || part == "..") return false;
        for (const unsigned char c : part) if (c < 32 || c == 127) return false;
        if (end == std::string::npos) break;
        start = end + 1;
    }
    return true;
}
inline bool SamePlan(const Plan& a, const Plan& b) {
    return a.run_id == b.run_id && a.source_commit == b.source_commit &&
           a.build_id == b.build_id && a.executable == b.executable &&
           a.module_path == b.module_path && a.directory == b.directory &&
           a.timeout_ms == b.timeout_ms;
}
inline void Validate(const Plan& p, const Approval& a) {
    constexpr const char* prefix = "directory-probe-";
    Need(p.run_id.rfind(prefix, 0) == 0 && p.run_id.size() == 48 &&
         Hex(p.run_id.substr(16), 32), "invalid-run-id");
    Need(Hex(p.source_commit, 40), "invalid-source-identity");
    Need(p.build_id.size() == 19 && p.build_id.rfind("noscan-", 0) == 0 &&
         Hex(p.build_id.substr(7), 12), "invalid-build-id");
    Need(Canonical(p.executable) && Canonical(p.module_path) &&
         directory_spec::AsciiDirectoryPath(p.directory), "invalid-path-scope");
    Need(p.timeout_ms >= 1 && p.timeout_ms <= 15000, "invalid-deadline");
    Need(a.native_contract_reviewed && a.private_file_call_authorized &&
         a.provider_reference_retention_authorized && SamePlan(p, a.scope),
         "fresh-exact-authorization-required");
}
inline std::vector<std::string> Registry(const Observation& o) {
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
inline void ValidateImages(const std::vector<RuntimeImage>& images) {
    Need(!images.empty() && images.size() <= 8192, "invalid-image-list");
    for (const auto& image : images) {
        Need(Canonical(image.path) && image.header != 0, "invalid-image-list");
    }
    auto sorted = images;
    std::sort(sorted.begin(), sorted.end(), [](const RuntimeImage& a, const RuntimeImage& b) {
        if (a.path != b.path) return a.path < b.path;
        if (a.header != b.header) return a.header < b.header;
        return a.slide < b.slide;
    });
    Need(std::adjacent_find(sorted.begin(), sorted.end()) == sorted.end(), "ambiguous-image-list");
}
inline void Safe(const Plan& p, const Observation& o) {
    Need(o.pid > 0 && !o.process_start.empty() && o.process_start.size() <= 128 &&
         o.executable == p.executable && o.module_path == p.module_path,
         "host-or-module-identity-mismatch");
    Need(o.version == "25.6x101" && o.build == 101 && o.arch == "arm64" &&
         o.main_thread, "wrong-host-or-thread");
    Need(o.unsaved && !o.dirty && !o.rendering && o.items == 0 && o.queued == 0 &&
         o.revision > 0, "project-not-blank-clean-idle");
    (void)Registry(o);
    ValidateImages(o.images);
}
inline bool SystemLazyImage(const RuntimeImage& image) {
    return image.path.rfind("/System/Library/", 0) == 0;
}
inline bool CompatibleImages(const std::vector<RuntimeImage>& before,
                             const std::vector<RuntimeImage>& after) {
    // Existing images may not move, unload or change identity. New images are
    // tolerated only from the immutable Apple system framework root, because
    // AE/macOS can lazily load those during otherwise unrelated host activity.
    // User, Adobe and plug-in paths remain exact and additions still fail.
    for (const auto& image : before) {
        if (std::find(after.begin(), after.end(), image) == after.end()) return false;
    }
    for (const auto& image : after) {
        if (std::find(before.begin(), before.end(), image) == before.end() &&
            !SystemLazyImage(image)) return false;
    }
    return true;
}
inline bool SameRuntime(const Observation& a, const Observation& b) {
    return a.pid == b.pid && a.process_start == b.process_start &&
           a.executable == b.executable && a.module_path == b.module_path &&
           a.revision == b.revision && Registry(a) == Registry(b) &&
           CompatibleImages(a.images, b.images);
}
inline void RequireNativeSuccess(const NativeResult& n) {
    Need(n.invoked && n.completed && n.cleanup_ok, "directory-operation-failed");
    Need(n.strings_created == 2 && n.string_release_attempts == 2 &&
         n.specs_created == 1 && n.spec_release_attempts == 1,
         "directory-lifetime-count-mismatch");
    Need(n.retained_references == 3, "provider-retention-count-mismatch");
}

// A PASS means only that one newly owned directory specification completed an
// exact path roundtrip and single release while host/project/registry/images
// stayed unchanged. It never means ordinary plug-in registration works.
inline Result Run(const Plan& supplied, const Approval& supplied_approval, Backend& backend) {
    const Plan p = supplied;
    const Approval approval = supplied_approval;
    Result r;
    Observation before;
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
        backend.verify_directory(p);
        before = backend.observe();
        Safe(p, before);
        tick();
        r.stage = "claim";
        backend.claim(p, before);
        r.claimed = true;
        backend.save_observation("before", before);
        r.stage = "precall";
        backend.verify_directory(p);
        const auto immediately_before = backend.observe();
        Safe(p, immediately_before);
        Need(SameRuntime(before, immediately_before), "baseline-changed-before-call");
        tick();
        r.stage = "call-marker";
        backend.mark_call_started(p, immediately_before);
        r.call_started = true; // durable marker exists; no retry after this point
        tick();
        r.stage = "directory-call";
        const auto native = backend.run_directory_probe(p, approval);
        r.cleanup_ok = native.cleanup_ok;
        backend.save_native_result(native);
        r.native_observed = true;
        r.stage = "postflight";
        postflight_attempted = true;
        const auto after = backend.observe();
        r.postflight_observed = true;
        backend.save_observation("after", after);
        Safe(p, after);
        Need(SameRuntime(before, after), "host-project-registry-or-images-changed");
        backend.verify_directory(p);
        tick();
        RequireNativeSuccess(native);
        r.stage = "complete";
        r.status = "PASS";
        r.reason = "directory-roundtrip-release-only";
    } catch (const std::exception&) {
        r.status = r.claimed ? "FAIL" : "BLOCKED";
        r.reason = r.call_started ? "no-scan-native-or-postflight-failed" : "precall-gate-failed";
    } catch (...) {
        r.status = r.claimed ? "FAIL" : "BLOCKED";
        r.reason = "unclassified-backend-failure";
    }
    if (r.claimed && !postflight_attempted) {
        try {
            const auto after = backend.observe();
            r.postflight_observed = true;
            backend.save_observation("after", after);
        } catch (...) {}
    }
    return r;
}
} // namespace no_scan_directory
