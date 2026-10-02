#pragma once
#include "RetainedIdentityCapture.hpp"
#include "ResourcePassJournal.hpp"

// Storage only. Does not supply operation authority, resident identity or host
// pre/postflight. Producer PASS must be independently verified by the supervisor.
namespace retained_journal {
using retained_identity::Need;
struct Scope {
    std::string run, source, build, binary, provider_sha, provider_uuid, origin;
    std::uint64_t pid = 0, start_sec = 0, start_usec = 0, root = 0;
};
constexpr std::size_t kPayloadLimit = 65536;
inline void Field(std::string& text, const std::string& name, const std::string& value) {
    resource_pass::journal_detail::Field(text, name, value);
    Need(text.size() <= kPayloadLimit, "identity-journal-payload-limit");
}
inline void Validate(const Scope& s) {
    using resource_pass::Hex;
    const std::string run_prefix = "retained-identity-", build_prefix = "identity-";
    Need(s.run.rfind(run_prefix, 0) == 0 &&
         Hex(s.run.substr(run_prefix.size()), 32) &&
         s.build.rfind(build_prefix, 0) == 0 &&
         Hex(s.build.substr(build_prefix.size()), 12) && Hex(s.source, 40) &&
         Hex(s.binary, 64) && Hex(s.provider_sha, 64) && Hex(s.provider_uuid, 32),
         "identity-journal-scope-identity");
    Need(s.pid > 0 && s.pid <= 0x7fffffff && s.start_sec > 0 && s.start_usec < 1000000 &&
         s.root > 0 && s.root % 8 == 0 && s.root <= UINT64_MAX - 16,
         "identity-journal-process-or-root");
    Need(s.origin == "owned-fixture" || s.origin == "ae-diagnostic", "identity-journal-origin");
    if (s.origin == "ae-diagnostic")
        Need(s.provider_sha == "18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344" &&
             s.provider_uuid == "74a30dbaa08b367bbd9915d6d77e9d52", "identity-journal-provider-pin");
}
inline std::string ScopeBytes(const Scope& s) {
    Validate(s);
    std::string out;
    Field(out, "scope", "retained-identity"); Field(out, "layout", "mee-25.6-arm64-1");
    Field(out, "origin", s.origin); Field(out, "run", s.run); Field(out, "source", s.source);
    Field(out, "build", s.build); Field(out, "binary", s.binary);
    Field(out, "pid", std::to_string(s.pid)); Field(out, "start_sec", std::to_string(s.start_sec));
    Field(out, "start_usec", std::to_string(s.start_usec));
    Field(out, "provider_sha", s.provider_sha); Field(out, "provider_uuid", s.provider_uuid);
    Field(out, "root", std::to_string(s.root)); return out;
}
inline std::string HexBytes(const retained_identity::Bytes& bytes) {
    static constexpr char hex[] = "0123456789abcdef";
    std::string out; out.reserve(bytes.size() * 2);
    for (auto b : bytes) { out += hex[b >> 4]; out += hex[b & 15]; } return out;
}
inline std::string MappingBytes(const mapped_memory::Region& m) {
    return std::to_string(m.address) + "," + std::to_string(m.size) + "," +
        std::to_string(m.offset) + "," + std::to_string(m.object_id) + "," +
        std::to_string(m.user_tag) + "," + std::to_string(m.depth) + "," +
        std::to_string(m.protection) + "," + std::to_string(m.maximum);
}
inline std::string DiagnosticBytes(const Scope& s, const retained_capture::Diagnostic& d) {
    Need(d.calls <= retained_capture::Observer::kCalls && d.bytes <= retained_capture::Observer::kBytes &&
         d.frames.size() == d.reads.size() && d.frames.size() <= d.calls &&
         d.failure.size() <= 256, "identity-journal-diagnostic-bounds");
    for (unsigned char c : d.failure) Need(c >= 32 && c < 127, "identity-journal-failure-text");
    Need(!d.success || (d.failure.empty() && d.frames.size() == d.calls),
         "identity-journal-invalid-success");
    std::string out = ScopeBytes(s);
    Field(out, "success", std::to_string(d.success)); Field(out, "failure", d.failure);
    Field(out, "read_calls", std::to_string(d.calls)); Field(out, "read_bytes", std::to_string(d.bytes));
    Field(out, "frame_count", std::to_string(d.frames.size()));
    std::size_t copied = 0;
    for (std::size_t i = 0; i < d.frames.size(); ++i) {
        const auto& f = d.frames[i]; const auto& r = d.reads[i];
        Need(f.address == r.address && f.bytes.size() == r.size && r.size > 0 &&
             r.size <= mapped_memory::Reader::kChunk && copied <= d.bytes &&
             r.size <= d.bytes - copied, "identity-journal-frame-binding");
        copied += r.size;
        Field(out, "frame_address", std::to_string(f.address));
        Field(out, "frame_size", std::to_string(f.bytes.size()));
        Field(out, "frame_hex", HexBytes(f.bytes)); Field(out, "frame_mapping", MappingBytes(r.mapping));
    }
    Need(!d.success || copied == d.bytes, "identity-journal-byte-count");
    return out;
}
class Journal {
    resource_pass::DiskJournal disk_;
    enum class Stage { Fresh, Claimed, Marked, Saved, Finished, Poisoned };
    Stage stage_ = Stage::Fresh;
    Scope scope_;
    bool capture_ok_ = false;
    template<class F> void Mutate(Stage required, Stage next, F action) {
        const auto old = stage_; stage_ = Stage::Poisoned;
        Need(old == required, "identity-journal-order-or-consumed");
        action(); stage_ = next;
    }
public:
    explicit Journal(const std::string& directory) : disk_(directory) {}
    void claim(const Scope& supplied) {
        const Scope s = supplied;
        Mutate(Stage::Fresh, Stage::Claimed, [&] {
            disk_.Append("claim.txt", ScopeBytes(s)); scope_ = s;
        });
    }
    void mark_read() {
        Mutate(Stage::Claimed, Stage::Marked, [&] {
            disk_.Append("call-started.txt", ScopeBytes(scope_));
        });
    }
    void save(const retained_capture::Diagnostic& d) {
        Mutate(Stage::Marked, Stage::Saved, [&] {
            disk_.Append("native.txt", DiagnosticBytes(scope_, d));
            capture_ok_ = d.success && d.failure.empty();
        });
    }
    void finish() {
        Mutate(Stage::Saved, Stage::Finished, [&] {
            std::string out = ScopeBytes(scope_);
            Field(out, "status", capture_ok_ ? "PASS" : "FAIL");
            Field(out, "claim", "copied-byte-diagnostic-only");
            disk_.Append("result.txt", out);
        });
    }
};
} // namespace retained_journal
