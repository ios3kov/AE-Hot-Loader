#pragma once
#include "RetainedIdentityJournal.hpp"
#include "NoScanDirectoryGate.hpp"

// One-shot core only: injected observations/storage are not native attestation.
// No Adobe call, process control, private function or provider reference operation.
namespace retained_transaction {
using retained_identity::Need;
struct Plan {
    retained_journal::Scope scope;
    std::string executable, module_path, journal_directory;
    std::uint64_t timeout_ms = 15000;
};
struct Approval { Plan plan; bool read_authorized = false, contract_reviewed = false; };
struct Observation {
    no_scan_directory::Observation host;
    retained_journal::Scope measured;
};
struct Result {
    std::string status = "BLOCKED", stage = "validate", reason, evidence_failure;
    bool consumed = false, claim_attempted = false, claimed = false;
    bool marker_attempted = false, read_started = false, diagnostic_saved = false;
    bool postflight_attempted = false, postflight_saved = false, result_saved = false;
    bool host_execution_verified = false; // Always requires independent live verification.
};
struct Backend {
    virtual ~Backend() = default;
    virtual std::uint64_t now_ms() = 0;
    virtual Observation observe() = 0;
    // claim stores plan+baseline atomically/exclusively before returning.
    virtual void claim(const Plan&, const Observation&) = 0;
    virtual void mark_read(const Plan&, const Observation&) = 0;
    virtual retained_capture::Diagnostic capture(const Plan&) = 0;
    virtual void save_diagnostic(const retained_capture::Diagnostic&) = 0;
    virtual void save_postflight(const Observation&) = 0;
    // Provisional producer evidence, never sufficient for external live PASS.
    virtual void save_result(const Result&) = 0;
};
inline bool SamePlan(const Plan& a, const Plan& b) {
    return retained_journal::ScopeBytes(a.scope) == retained_journal::ScopeBytes(b.scope) &&
        a.executable == b.executable && a.module_path == b.module_path &&
        a.journal_directory == b.journal_directory && a.timeout_ms == b.timeout_ms;
}
inline void Validate(const Plan& p, const Approval& a) {
    retained_journal::Validate(p.scope);
    Need(no_scan_directory::Canonical(p.executable) &&
         no_scan_directory::Canonical(p.module_path) &&
         no_scan_directory::Canonical(p.journal_directory) && p.timeout_ms == 15000,
         "retained-transaction-path-or-timeout");
    Need(a.read_authorized && a.contract_reviewed && SamePlan(p, a.plan),
         "retained-transaction-exact-authority");
}
inline void Safe(const Plan& p, const Observation& o) {
    const no_scan_directory::Plan host_plan{p.scope.run, p.scope.source, p.scope.build,
        p.executable, p.module_path, p.journal_directory, p.timeout_ms};
    no_scan_directory::Safe(host_plan, o.host);
    Need(retained_journal::ScopeBytes(o.measured) == retained_journal::ScopeBytes(p.scope),
         "retained-transaction-binding-changed");
    const auto start = std::to_string(p.scope.start_sec) + "." +
                       std::to_string(p.scope.start_usec);
    Need(o.host.pid == static_cast<std::int64_t>(p.scope.pid) && o.host.process_start == start,
         "retained-transaction-process-changed");
}
inline std::string BoundedReason(const char* text) {
    if (!text) return "retained-transaction-unknown-failure";
    std::string out;
    for (std::size_t i = 0; i < 256 && text[i]; ++i) {
        const auto c = static_cast<unsigned char>(text[i]);
        out += c >= 32 && c <= 126 ? static_cast<char>(c) : '?';
    }
    return out.empty() ? "retained-transaction-empty-failure" : out;
}
class Transaction {
    std::atomic<bool> consumed_{false};
public:
    Result run(const Plan& supplied, const Approval& supplied_approval, Backend& b) {
        Result r;
        if (consumed_.exchange(true)) { r.reason = "retained-transaction-consumed"; return r; }
        r.consumed = true;
        std::uint64_t previous = 0, deadline = 0;
        auto tick = [&] {
            const auto now = b.now_ms();
            Need(now >= previous && now < deadline, "retained-transaction-deadline");
            previous = now;
        };
        auto fail = [&](const std::string& reason) {
            r.status = r.claim_attempted ? "FAIL" : "BLOCKED"; r.reason = reason;
        };
        try {
            // Copy before any boundary call; a backend cannot retarget caller input.
            const Plan p = supplied; const Approval a = supplied_approval;
            Validate(p, a);
            previous = b.now_ms();
            Need(previous <= UINT64_MAX - p.timeout_ms, "retained-transaction-clock-overflow");
            deadline = previous + p.timeout_ms;
            r.stage = "baseline"; tick(); const auto before = b.observe(); tick(); Safe(p, before);
            r.stage = "claim"; tick(); r.claim_attempted = true;
            b.claim(p, before); r.claimed = true; tick();
            r.stage = "preread"; tick(); const auto immediate = b.observe(); tick(); Safe(p, immediate);
            Need(no_scan_directory::SameRuntime(before.host, immediate.host),
                 "retained-transaction-baseline-changed");
            r.stage = "marker"; tick(); r.marker_attempted = true;
            b.mark_read(p, immediate); r.read_started = true; tick();
            r.stage = "capture"; tick(); const auto diagnostic = b.capture(p);
            // Preserve completed copies even if capture exhausted the deadline.
            r.stage = "diagnostic"; b.save_diagnostic(diagnostic); r.diagnostic_saved = true; tick();
            r.stage = "postflight"; tick(); r.postflight_attempted = true;
            const auto after = b.observe(); b.save_postflight(after); r.postflight_saved = true; tick();
            Safe(p, after);
            Need(no_scan_directory::SameRuntime(before.host, after.host),
                 "retained-transaction-host-changed");
            Need(diagnostic.success && diagnostic.failure.empty(), "retained-transaction-capture-failed");
            r.status = "PASS"; r.stage = "complete"; r.reason = "guarded-copied-byte-diagnostic-only";
        } catch (const std::exception& e) { fail(BoundedReason(e.what())); }
        catch (...) { fail("retained-transaction-unknown-failure"); }
        // Evidence recovery only, even after timeout; never repeat capture or an
        // already-attempted postflight. Exceptions do not erase the original reason.
        if (r.claim_attempted && !r.postflight_attempted) {
            r.postflight_attempted = true;
            try { const auto after = b.observe(); b.save_postflight(after); r.postflight_saved = true; }
            catch (const std::exception& e) { r.evidence_failure = BoundedReason(e.what()); }
            catch (...) { r.evidence_failure = "retained-transaction-postflight-unknown"; }
        }
        if (r.claim_attempted) {
            try {
                // Save FAIL evidence past deadline too. A provisional PASS still
                // needs a fresh tick before/after persistence and external checks.
                if (r.status == "PASS") {
                    try { tick(); } catch (const std::exception& e) {
                        r.status = "FAIL"; r.stage = "result"; r.reason = BoundedReason(e.what());
                    }
                }
                b.save_result(r); r.result_saved = true;
                if (r.status == "PASS") tick();
            } catch (const std::exception& e) {
                if (r.status == "PASS") { r.status = "FAIL"; r.stage = "result"; r.reason = BoundedReason(e.what()); }
                r.evidence_failure = BoundedReason(e.what());
            } catch (...) {
                if (r.status == "PASS") { r.status = "FAIL"; r.stage = "result"; r.reason = "retained-transaction-result-unknown"; }
                r.evidence_failure = "retained-transaction-result-unknown";
            }
        }
        return r;
    }
};
} // namespace retained_transaction
