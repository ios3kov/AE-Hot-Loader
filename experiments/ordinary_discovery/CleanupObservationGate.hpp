// One-shot DIAGNOSTIC transaction; no private call and no registration consent.
#pragma once
#include "CleanupObserver.hpp"
#include "NoScanDirectoryJournal.hpp"
namespace cleanup_observation {
using no_scan_directory::Plan;
using no_scan_directory::Observation;
struct Config { Plan plan; std::string token, control_directory, journal_directory; };
struct Approval { Plan scope; bool read_authorized = false, contract_reviewed = false; };
struct Result {
    std::string status = "BLOCKED", stage = "validate", reason;
    bool claimed = false, read_started = false, diagnostic_saved = false, postflight_saved = false;
};
struct Backend {
    virtual ~Backend() = default;
    virtual std::uint64_t now_ms() = 0;
    virtual Observation observe() = 0;
    virtual void claim(const Plan&, const Observation&) = 0;
    virtual void save_before(const Observation&) = 0;
    virtual void mark_read(const Plan&, const Observation&) = 0;
    virtual cleanup_observer::Diagnostic read() = 0;
    virtual void save_diagnostic(const cleanup_observer::Diagnostic&) = 0;
    virtual void save_after(const Observation&) = 0;
    virtual void finish(const Result&) = 0;
};
inline void Validate(const Plan& p, const Approval& a) {
    using namespace no_scan_directory;
    const std::string run_prefix = "cleanup-observer-", build_prefix = "observe-";
    Need(p.run_id.rfind(run_prefix, 0) == 0 && p.run_id.size() == run_prefix.size() + 32 &&
         Hex(p.run_id.substr(run_prefix.size()), 32) && Hex(p.source_commit, 40), "observer-plan-identity");
    Need(p.build_id.rfind(build_prefix, 0) == 0 && p.build_id.size() == build_prefix.size() + 12 &&
         Hex(p.build_id.substr(build_prefix.size()), 12), "observer-build-identity");
    Need(Canonical(p.executable) && Canonical(p.module_path) && Canonical(p.directory) &&
         p.timeout_ms == 15000, "observer-plan-path-or-timeout");
    Need(a.read_authorized && a.contract_reviewed && SamePlan(p, a.scope), "observer-exact-authority");
}
inline Result Run(const Plan& supplied, const Approval& supplied_approval, Backend& backend) {
    const Plan p = supplied; const Approval approval = supplied_approval;
    Result r; Observation before; bool after_attempted = false;
    std::uint64_t previous = 0, deadline = 0;
    auto tick = [&] { const auto now = backend.now_ms();
        no_scan_directory::Need(now >= previous && now < deadline, "observer-deadline"); previous = now; };
    try {
        Validate(p, approval); previous = backend.now_ms();
        no_scan_directory::Need(previous <= UINT64_MAX - p.timeout_ms, "observer-clock"); deadline = previous + p.timeout_ms;
        r.stage = "baseline"; before = backend.observe(); no_scan_directory::Safe(p, before); tick();
        r.stage = "claim"; backend.claim(p, before); r.claimed = true; backend.save_before(before);
        r.stage = "preread"; const auto immediate = backend.observe(); no_scan_directory::Safe(p, immediate);
        no_scan_directory::Need(no_scan_directory::SameRuntime(before, immediate), "observer-baseline-changed"); tick();
        r.stage = "read-marker"; backend.mark_read(p, immediate); r.read_started = true; tick();
        r.stage = "read"; const auto diagnostic = backend.read(); backend.save_diagnostic(diagnostic); r.diagnostic_saved = true;
        r.stage = "postflight"; after_attempted = true; const auto after = backend.observe();
        backend.save_after(after); r.postflight_saved = true; no_scan_directory::Safe(p, after);
        no_scan_directory::Need(no_scan_directory::SameRuntime(before, after), "observer-host-changed"); tick();
        no_scan_directory::Need(diagnostic.success && diagnostic.failure.empty(), "observer-capture-failed");
        r.status = "PASS"; r.stage = "complete"; r.reason = "matching-diagnostic-only";
    } catch (...) { r.status = r.claimed ? "FAIL" : "BLOCKED"; r.reason = "observer-gate-or-evidence-failed"; }
    if (r.claimed && !after_attempted) {
        try { const auto after = backend.observe(); backend.save_after(after); r.postflight_saved = true; } catch (...) {}
    }
    if (r.claimed) {
        try { backend.finish(r); } catch (...) { r.status = "FAIL"; r.stage = "evidence"; r.reason = "observer-result-not-durable"; }
    }
    return r;
}
namespace detail {
using no_scan_directory::journal_detail::Field;
using no_scan_directory::journal_detail::ObservationBytes;
inline std::string PlanBytes(const Plan& p) {
    std::string s; Field(s, "scope", "cleanup-observer"); Field(s, "run", p.run_id);
    Field(s, "source", p.source_commit); Field(s, "build", p.build_id);
    Field(s, "executable", p.executable); Field(s, "module", p.module_path);
    Field(s, "journal", p.directory); Field(s, "timeout_ms", std::to_string(p.timeout_ms)); return s;
}
inline std::string HexBytes(const cleanup_snapshot::Bytes& bytes) {
    static constexpr char hex[] = "0123456789abcdef"; std::string s; s.reserve(bytes.size() * 2);
    for (unsigned char b : bytes) { s += hex[b >> 4]; s += hex[b & 15]; } return s;
}
inline std::string DiagnosticBytes(const cleanup_observer::Diagnostic& d) {
    std::string s; Field(s, "scope", "cleanup-observer");
    Field(s, "success", std::to_string(d.success)); Field(s, "failure", d.failure);
    Field(s, "read_calls", std::to_string(d.calls)); Field(s, "read_bytes", std::to_string(d.bytes));
    Field(s, "global_address", std::to_string(d.global.address)); Field(s, "global_hex", HexBytes(d.global.bytes));
    Field(s, "general_plugin_records", std::to_string(d.snapshot.general_plugin_records));
    Field(s, "callback_count", std::to_string(d.snapshot.callbacks.size()));
    for (const auto& c : d.snapshot.callbacks) {
        Field(s, "callback_target", std::to_string(c.target)); Field(s, "callback_context", std::to_string(c.context));
    }
    Field(s, "frame_count", std::to_string(d.snapshot.frames.size()));
    for (const auto& f : d.snapshot.frames) {
        Field(s, "frame_address", std::to_string(f.address)); Field(s, "frame_hex", HexBytes(f.bytes));
    }
    auto mapping = [&](const mapped_memory::ReadRecord& r, const std::string& prefix) {
        const auto& m = r.mapping;
        Field(s, prefix + "address", std::to_string(r.address)); Field(s, prefix + "size", std::to_string(r.size));
        Field(s, prefix + "mapping", std::to_string(m.address) + "," + std::to_string(m.size) + "," +
            std::to_string(m.offset) + "," + std::to_string(m.object_id) + "," + std::to_string(m.user_tag) + "," +
            std::to_string(m.depth) + "," + std::to_string(m.protection) + "," + std::to_string(m.maximum));
    };
    Field(s, "read_count", std::to_string(d.reads.size())); for (const auto& r : d.reads) mapping(r, "read_");
    Field(s, "containment_count", std::to_string(d.containment_only.size()));
    for (const auto& r : d.containment_only) mapping(r, "containment_"); return s;
}
} // namespace detail
class JournaledBackend : public Backend {
    resource_pass::DiskJournal journal_;
    std::string plan_, before_;
    bool claimed_ = false, before_saved_ = false, marked_ = false, diagnostic_saved_ = false, after_saved_ = false, finished_ = false, diagnostic_ok_ = false;
public:
    explicit JournaledBackend(const std::string& directory) : journal_(directory) {}
    void claim(const Plan& p, const Observation& o) final {
        no_scan_directory::Need(!claimed_, "observer-claim-consumed");
        const auto plan = detail::PlanBytes(p), before = detail::ObservationBytes(o);
        journal_.Append("claim.txt", plan + before); plan_ = plan; before_ = before; claimed_ = true;
    }
    void save_before(const Observation& o) final {
        no_scan_directory::Need(claimed_ && !before_saved_ && !marked_ && !after_saved_ &&
            detail::ObservationBytes(o) == before_, "observer-before-unbound");
        journal_.Append("before.txt", before_); before_saved_ = true;
    }
    void mark_read(const Plan& p, const Observation& o) final {
        no_scan_directory::Need(claimed_ && before_saved_ && !marked_ && !after_saved_ &&
            detail::PlanBytes(p) == plan_ && detail::ObservationBytes(o) == before_, "observer-marker-unbound");
        // Diagnostic marker uses the existing fixed-name journal container only.
        journal_.Append("call-started.txt", plan_ + detail::ObservationBytes(o)); marked_ = true;
    }
    void save_diagnostic(const cleanup_observer::Diagnostic& d) final {
        no_scan_directory::Need(marked_ && !diagnostic_saved_ && !after_saved_, "observer-diagnostic-unbound");
        journal_.Append("native.txt", detail::DiagnosticBytes(d)); diagnostic_saved_ = true;
        diagnostic_ok_ = d.success && d.failure.empty();
    }
    void save_after(const Observation& o) final {
        no_scan_directory::Need(claimed_ && !after_saved_, "observer-after-replay");
        journal_.Append("after.txt", detail::ObservationBytes(o)); after_saved_ = true;
    }
    void finish(const Result& r) final {
        no_scan_directory::Need(claimed_ && r.claimed && !finished_ && (r.status == "PASS" || r.status == "FAIL"),
                               "observer-final-unbound");
        no_scan_directory::Need(r.status != "PASS" || (before_saved_ && marked_ && diagnostic_saved_ && diagnostic_ok_ && after_saved_ &&
            r.read_started && r.diagnostic_saved && r.postflight_saved && r.stage == "complete" &&
            r.reason == "matching-diagnostic-only"), "observer-incomplete-pass");
        std::string s; detail::Field(s, "scope", "cleanup-observer"); detail::Field(s, "status", r.status);
        detail::Field(s, "stage", r.stage); detail::Field(s, "reason", r.reason);
        detail::Field(s, "claimed", std::to_string(r.claimed)); detail::Field(s, "read_started", std::to_string(r.read_started));
        detail::Field(s, "diagnostic_saved", std::to_string(r.diagnostic_saved));
        detail::Field(s, "postflight_saved", std::to_string(r.postflight_saved));
        journal_.Append("result.txt", s); finished_ = true;
    }
};
} // namespace cleanup_observation
