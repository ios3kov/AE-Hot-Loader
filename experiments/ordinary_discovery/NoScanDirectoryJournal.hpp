// Durable one-shot evidence wiring for NoScanDirectoryGate. Reuses the existing
// reviewed DiskJournal mechanics; no Adobe API is bound or invoked in this file.
#pragma once
#include "NoScanDirectoryGate.hpp"
#include "ResourcePassJournal.hpp"

namespace no_scan_directory {
namespace journal_detail {
inline void Field(std::string& text, const std::string& name, const std::string& value) {
    resource_pass::journal_detail::Field(text, name, value);
}
inline std::string PlanBytes(const Plan& p) {
    std::string s;
    Field(s, "scope", "no-scan-directory");
    Field(s, "run", p.run_id); Field(s, "source", p.source_commit); Field(s, "build", p.build_id);
    Field(s, "executable", p.executable); Field(s, "module", p.module_path);
    Field(s, "directory", p.directory); Field(s, "timeout_ms", std::to_string(p.timeout_ms));
    return s;
}
inline std::string ObservationBytes(const Observation& o) {
    std::string s;
    Field(s, "pid", std::to_string(o.pid)); Field(s, "start", o.process_start);
    Field(s, "executable", o.executable); Field(s, "module", o.module_path);
    Field(s, "version", o.version); Field(s, "arch", o.arch); Field(s, "build", std::to_string(o.build));
    Field(s, "main_thread", std::to_string(o.main_thread)); Field(s, "unsaved", std::to_string(o.unsaved));
    Field(s, "dirty", std::to_string(o.dirty)); Field(s, "rendering", std::to_string(o.rendering));
    Field(s, "items", std::to_string(o.items)); Field(s, "queued", std::to_string(o.queued));
    Field(s, "revision", std::to_string(o.revision));
    Field(s, "registry_count", std::to_string(o.registry.size()));
    for (const auto& name : o.registry) Field(s, "effect", name);
    Field(s, "image_count", std::to_string(o.images.size()));
    for (const auto& image : o.images) {
        Field(s, "image_path", image.path);
        Field(s, "image_header", std::to_string(image.header));
        Field(s, "image_slide", std::to_string(image.slide));
    }
    return s;
}
} // namespace journal_detail

class JournaledBackend : public Backend {
    resource_pass::DiskJournal journal_;
    std::string plan_, before_;
    bool claimed_ = false, before_saved_ = false, marked_ = false, native_saved_ = false, after_saved_ = false;
public:
    explicit JournaledBackend(std::string directory) : journal_(std::move(directory)) {}
    void claim(const Plan& p, const Observation& o) final {
        Need(!claimed_, "journal-claim-already-consumed");
        const auto plan = journal_detail::PlanBytes(p), observation = journal_detail::ObservationBytes(o);
        journal_.Append("claim.txt", plan + observation);
        plan_ = plan; before_ = observation; claimed_ = true;
    }
    void save_observation(const char* name, const Observation& o) final {
        Need(claimed_ && name, "journal-no-owned-claim");
        const std::string label(name), bytes = journal_detail::ObservationBytes(o);
        if (label == "before") {
            Need(!before_saved_ && !marked_ && !after_saved_ && bytes == before_,
                 "journal-before-mismatch-or-replay");
            journal_.Append("before.txt", bytes); before_saved_ = true;
        } else {
            Need(label == "after" && !after_saved_, "journal-invalid-observation-or-replay");
            journal_.Append("after.txt", bytes); after_saved_ = true;
        }
    }
    void mark_call_started(const Plan& p, const Observation& o) final {
        Need(claimed_ && before_saved_ && !marked_ && !native_saved_ && !after_saved_ &&
             journal_detail::PlanBytes(p) == plan_, "journal-call-marker-unbound-or-replayed");
        journal_.Append("call-started.txt", plan_ + journal_detail::ObservationBytes(o));
        marked_ = true;
    }
    void save_native_result(const NativeResult& n) final {
        Need(claimed_ && before_saved_ && marked_ && !native_saved_ && !after_saved_,
             "journal-native-result-unbound-or-replayed");
        std::string bytes;
        journal_detail::Field(bytes, "scope", "no-scan-directory");
        journal_detail::Field(bytes, "invoked", std::to_string(n.invoked));
        journal_detail::Field(bytes, "completed", std::to_string(n.completed));
        journal_detail::Field(bytes, "cleanup_ok", std::to_string(n.cleanup_ok));
        journal_detail::Field(bytes, "strings_created", std::to_string(n.strings_created));
        journal_detail::Field(bytes, "string_release_attempts", std::to_string(n.string_release_attempts));
        journal_detail::Field(bytes, "specs_created", std::to_string(n.specs_created));
        journal_detail::Field(bytes, "spec_release_attempts", std::to_string(n.spec_release_attempts));
        journal_detail::Field(bytes, "retained_references", std::to_string(n.retained_references));
        journal_.Append("native.txt", bytes);
        native_saved_ = true;
    }
    void finish(const Result& r) {
        Need(claimed_ && r.claimed && (r.status == "PASS" || r.status == "FAIL"),
             "journal-invalid-final-result");
        Need(r.status != "PASS" || (before_saved_ && marked_ && native_saved_ && after_saved_ &&
             r.call_started && r.native_observed && r.postflight_observed &&
             r.cleanup_ok && r.stage == "complete"), "journal-incomplete-pass");
        std::string bytes;
        journal_detail::Field(bytes, "scope", "no-scan-directory");
        journal_detail::Field(bytes, "status", r.status); journal_detail::Field(bytes, "stage", r.stage);
        journal_detail::Field(bytes, "reason", r.reason);
        journal_detail::Field(bytes, "claimed", std::to_string(r.claimed));
        journal_detail::Field(bytes, "call_started", std::to_string(r.call_started));
        journal_detail::Field(bytes, "native_observed", std::to_string(r.native_observed));
        journal_detail::Field(bytes, "postflight_observed", std::to_string(r.postflight_observed));
        journal_detail::Field(bytes, "cleanup_ok", std::to_string(r.cleanup_ok));
        journal_.Append("result.txt", bytes);
    }
};
inline Result RunJournaled(const Plan& p, const Approval& a, JournaledBackend& backend) {
    auto result = Run(p, a, backend);
    if (result.claimed) {
        try { backend.finish(result); }
        catch (...) {
            result.status = "FAIL"; result.stage = "evidence";
            result.reason = "final-evidence-not-confirmed";
        }
    }
    return result;
}
} // namespace no_scan_directory
