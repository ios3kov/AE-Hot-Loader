#pragma once
#include "RetainedHostJournal.hpp"
namespace retained_probe {
using retained_identity::Need;
struct Config { std::string run, source, build, executable, module, journal, control, token; };
inline std::string Request(const Config& c, std::uint64_t pid, const std::string& start,
                           const std::string& binary) {
    retained_journal::Validate({c.run, c.source, c.build, binary, std::string(64, 'a'),
        std::string(32, 'b'), "owned-fixture", pid, 1, 0, 8});
    Need(resource_pass::Hex(c.token, 32) && no_scan_directory::Canonical(c.executable) &&
         no_scan_directory::Canonical(c.module) && no_scan_directory::Canonical(c.control) &&
         no_scan_directory::Canonical(c.journal) && !start.empty() && start.size() <= 32 &&
         start.find_first_not_of("0123456789.") == std::string::npos,
         "retained-request-config");
    return "version=1\nkind=retained-identity\nbuild_id=" + c.build +
        "\nrun_id=" + c.run + "\nsource=" + c.source + "\npid=" + std::to_string(pid) +
        "\nstart=" + start + "\ntoken=" + c.token + "\nbinary_sha256=" + binary +
        "\nread_only=authorized\ncontract=reviewed\n";
}
inline std::string ApproveRequest(const Config& c, std::uint64_t pid,
                                 const std::string& start, const std::string& bytes) {
    const auto prefix = Request(c, pid, start, std::string(64, '0'));
    const auto offset = prefix.find("binary_sha256=") + std::string("binary_sha256=").size();
    Need(bytes.size() == prefix.size(), "retained-request-length");
    const auto digest = bytes.substr(offset, 64);
    Need(bytes == Request(c, pid, start, digest), "retained-request-identity");
    return digest; // Syntax/review flags only. Loaded self hash still must be measured.
}
struct Binding {
    retained_journal::Scope scope;
    std::vector<no_scan_directory::RuntimeImage> images;
};
struct BindingBackend { virtual ~BindingBackend() = default; virtual Binding measure() = 0; };
class Capture {
    std::atomic<bool> consumed_{false};
    retained_capture::Observer observer_;
public:
    retained_capture::Diagnostic run(const retained_transaction::Plan& supplied,
                                    BindingBackend& binding, mapped_memory::Backend& memory) {
        retained_capture::Diagnostic d;
        if (consumed_.exchange(true)) { d.failure = "retained-probe-capture-consumed"; return d; }
        try {
            const auto p = supplied;
            retained_transaction::Validate(p, {p, true, true});
            const auto before = binding.measure();
            Need(retained_journal::ScopeBytes(before.scope) == retained_journal::ScopeBytes(p.scope),
                 "retained-probe-before-binding");
            d = observer_.run(retained_identity::Layout::Mee256Arm64, p.scope.root, memory);
            const auto after = binding.measure();
            Need(retained_journal::ScopeBytes(after.scope) == retained_journal::ScopeBytes(p.scope) &&
                 before.images == after.images, "retained-probe-after-binding");
        } catch (const std::exception& e) {
            d.success = false; d.failure = retained_transaction::BoundedReason(e.what());
            d.snapshot = {}; d.identities.clear();
        } catch (...) {
            d.success = false; d.failure = "retained-probe-unknown-binding";
            d.snapshot = {}; d.identities.clear();
        }
        return d; // Completed frames survive a failed post-binding; no retry/lease.
    }
};
} // namespace retained_probe
