#pragma once
#include "RetainedIdentityTransaction.hpp"

// Disk adapter only. Native observation, measured binding and capture stay injected.
namespace retained_transaction {
namespace host_journal {
constexpr std::size_t kPayloadLimit = 4 * 1024 * 1024;
constexpr std::size_t kObservationLimit = 2 * 1024 * 1024;
inline void Field(std::string& out, const std::string& key, const std::string& value) {
    Need(value.size() <= kPayloadLimit && out.size() <= kPayloadLimit - value.size(),
         "retained-host-payload-limit");
    resource_pass::journal_detail::Field(out, key, value);
    Need(out.size() <= kPayloadLimit, "retained-host-payload-limit");
}
inline std::string HexText(const std::string& text) {
    Need(text.size() <= kObservationLimit, "retained-host-text-limit");
    static constexpr char hex[] = "0123456789abcdef";
    std::string out; out.reserve(text.size() * 2);
    for (const unsigned char c : text) { out += hex[c >> 4]; out += hex[c & 15]; }
    return out;
}
inline std::string PlanBytes(const Plan& p) {
    Validate(p, {p, true, true}); // Technical validity only; never grants authority.
    std::string out = retained_journal::ScopeBytes(p.scope);
    Field(out, "protocol", "retained-host-1");
    Field(out, "executable_hex", HexText(p.executable));
    Field(out, "module_hex", HexText(p.module_path));
    Field(out, "journal_hex", HexText(p.journal_directory));
    Field(out, "timeout_ms", std::to_string(p.timeout_ms)); return out;
}
inline std::string ObservationBytes(const Observation& o) {
    const auto& h = o.host;
    Need(h.registry.size() <= 20000 && h.images.size() <= 8192 &&
         h.process_start.size() <= 128 && h.executable.size() <= directory_spec::kMaxPath &&
         h.module_path.size() <= directory_spec::kMaxPath && h.version.size() <= 128 &&
         h.arch.size() <= 128, "retained-host-observation-bounds");
    std::string out = retained_journal::ScopeBytes(o.measured);
    Field(out, "observed_pid", std::to_string(h.pid)); Field(out, "observed_start", h.process_start);
    Field(out, "observed_executable_hex", HexText(h.executable));
    Field(out, "observed_module_hex", HexText(h.module_path));
    Field(out, "version", h.version); Field(out, "arch", h.arch); Field(out, "build_number", std::to_string(h.build));
    Field(out, "main_thread", std::to_string(h.main_thread)); Field(out, "unsaved", std::to_string(h.unsaved));
    Field(out, "dirty", std::to_string(h.dirty)); Field(out, "rendering", std::to_string(h.rendering));
    Field(out, "items", std::to_string(h.items)); Field(out, "queued", std::to_string(h.queued));
    Field(out, "revision", std::to_string(h.revision));
    Field(out, "registry_count", std::to_string(h.registry.size()));
    for (const auto& effect : h.registry) {
        Need(effect.size() <= 1024, "retained-host-effect-limit");
        Field(out, "effect_hex", HexText(effect));
    }
    Field(out, "image_count", std::to_string(h.images.size()));
    for (const auto& image : h.images) {
        Need(image.path.size() <= directory_spec::kMaxPath, "retained-host-image-path-limit");
        Field(out, "image_path_hex", HexText(image.path));
        Field(out, "image_header", std::to_string(image.header));
        Field(out, "image_slide", std::to_string(image.slide));
    }
    Need(out.size() <= kObservationLimit, "retained-host-observation-limit"); return out;
}
inline std::string ResultBytes(const Plan& p, const Result& r) {
    Need(r.stage.size() <= 64 && r.reason.size() <= 256 && r.evidence_failure.size() <= 256,
         "retained-host-result-limit");
    std::string out = PlanBytes(p);
    Field(out, "status", r.status); Field(out, "stage", r.stage); Field(out, "reason", r.reason);
    Field(out, "evidence_failure", r.evidence_failure);
    Field(out, "consumed", std::to_string(r.consumed));
    Field(out, "claim_attempted", std::to_string(r.claim_attempted)); Field(out, "claimed", std::to_string(r.claimed));
    Field(out, "marker_attempted", std::to_string(r.marker_attempted)); Field(out, "read_started", std::to_string(r.read_started));
    Field(out, "diagnostic_saved", std::to_string(r.diagnostic_saved));
    Field(out, "postflight_attempted", std::to_string(r.postflight_attempted)); Field(out, "postflight_saved", std::to_string(r.postflight_saved));
    Field(out, "host_execution_verified", std::to_string(r.host_execution_verified));
    Field(out, "claim", "provisional-guarded-diagnostic-only"); return out;
}
} // namespace host_journal

// Serialized calls in the owning process, like DiskJournal. Any mutation error
// consumes/poisons this adapter. On uncertainty it preserves all existing files.
class HostJournaledBackend : public Backend {
    resource_pass::DiskJournal disk_;
    const std::string directory_;
    enum class Stage { Fresh, Claimed, Marked, Saved, After, Finished, Poisoned };
    Stage stage_ = Stage::Fresh;
    Plan plan_;
    Observation before_, after_;
    bool diagnostic_ok_ = false, marked_ = false, saved_ = false;
    template<class F> void Mutate(Stage next, F action) {
        Need(stage_ != Stage::Poisoned, "retained-host-journal-poisoned");
        stage_ = Stage::Poisoned;
        action(); stage_ = next;
    }
public:
    explicit HostJournaledBackend(const std::string& directory) : disk_(directory), directory_(directory) {}
    void claim(const Plan& p, const Observation& before) final {
        const auto previous = stage_;
        Mutate(Stage::Claimed, [&] {
            Need(previous == Stage::Fresh && p.journal_directory == directory_, "retained-host-claim-path-or-order");
            Safe(p, before);
            auto out = host_journal::PlanBytes(p);
            host_journal::Field(out, "before_hex", host_journal::HexText(host_journal::ObservationBytes(before)));
            disk_.Append("claim.txt", out); plan_ = p; before_ = before;
        });
    }
    void mark_read(const Plan& p, const Observation& immediate) final {
        const auto previous = stage_;
        Mutate(Stage::Marked, [&] {
            Need(previous == Stage::Claimed && SamePlan(p, plan_), "retained-host-marker-order-or-plan");
            Safe(p, immediate);
            Need(no_scan_directory::SameRuntime(before_.host, immediate.host), "retained-host-marker-baseline");
            auto out = host_journal::PlanBytes(plan_);
            host_journal::Field(out, "immediate_hex", host_journal::HexText(host_journal::ObservationBytes(immediate)));
            disk_.Append("call-started.txt", out); marked_ = true;
        });
    }
    void save_diagnostic(const retained_capture::Diagnostic& d) final {
        const auto previous = stage_;
        Mutate(Stage::Saved, [&] {
            Need(previous == Stage::Marked, "retained-host-native-order");
            disk_.Append("native.txt", retained_journal::DiagnosticBytes(plan_.scope, d));
            diagnostic_ok_ = d.success && d.failure.empty(); saved_ = true;
        });
    }
    void save_postflight(const Observation& after) final {
        const auto previous = stage_;
        Mutate(Stage::After, [&] {
            Need(previous == Stage::Claimed || previous == Stage::Marked || previous == Stage::Saved,
                 "retained-host-after-order");
            auto out = host_journal::PlanBytes(plan_);
            host_journal::Field(out, "after_hex", host_journal::HexText(host_journal::ObservationBytes(after)));
            // Unsafe but bounded after-state remains evidence of a failed run.
            disk_.Append("after.txt", out); after_ = after;
        });
    }
    void save_result(const Result& r) final {
        const auto previous = stage_;
        Mutate(Stage::Finished, [&] {
            Need(previous == Stage::Claimed || previous == Stage::Marked || previous == Stage::Saved || previous == Stage::After,
                 "retained-host-final-order");
            Need(r.consumed && r.claim_attempted && r.claimed && !r.host_execution_verified &&
                 (r.status == "PASS" || r.status == "FAIL"), "retained-host-final-binding");
            if (r.status == "PASS") {
                Need(previous == Stage::After && marked_ && saved_ && diagnostic_ok_ &&
                     r.marker_attempted && r.read_started && r.diagnostic_saved && r.postflight_attempted &&
                     r.postflight_saved && r.stage == "complete" && r.evidence_failure.empty() &&
                     r.reason == "guarded-copied-byte-diagnostic-only", "retained-host-incomplete-pass");
                Safe(plan_, after_);
                Need(no_scan_directory::SameRuntime(before_.host, after_.host), "retained-host-final-host-changed");
            }
            disk_.Append("result.txt", host_journal::ResultBytes(plan_, r));
        });
    }
};
} // namespace retained_transaction
