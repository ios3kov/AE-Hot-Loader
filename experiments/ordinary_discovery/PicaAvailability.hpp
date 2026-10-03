#pragma once
// Bounded availability/enumeration policy, never ordinary-effect registration.
#include <array>
#include <atomic>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace pica_probe {
struct Spec { const char* name; std::int32_t version; };
inline constexpr std::array<Spec, 4> kSpecs{{
    {"SP Plug-ins Suite", 4}, {"SP Plug-ins Suite", 6},
    {"SP Access Suite", 3}, {"SP Adapters Suite", 3}
}};
struct Acquired { std::int32_t error = 0; bool present = false; };
struct Adapter { std::string name; std::int32_t version = 0; };
struct Observation { std::string identity, project, registry; };
struct Result {
    std::string status = "STOPPED", stage = "not-started", reason;
    std::vector<Acquired> suites;
    std::vector<Adapter> adapters;
    bool enumeration_complete = false;
};
struct Backend {
    virtual ~Backend() = default;
    virtual std::uint64_t now_ms() = 0;
    virtual void record(const std::string&, const std::string&) = 0;
    virtual Observation observe() = 0;
    virtual Acquired acquire(const Spec&) = 0;
    virtual void new_iterator() = 0;
    virtual bool next_adapter(Adapter&) = 0; // false only for documented NULL end
    virtual void delete_iterator() = 0;
};
inline std::string Hex(const std::string& value) {
    std::string out; const char* digits = "0123456789abcdef";
    for (unsigned char c : value) { out += digits[c >> 4]; out += digits[c & 15]; }
    return out;
}
inline std::string Serialize(const Result& r) {
    std::string out = "schema=PICA-AVAILABILITY-1\nstatus=" + r.status +
        "\nstage=" + r.stage + "\nreason_hex=" + Hex(r.reason) +
        "\nsuite_count=" + std::to_string(r.suites.size()) + "\n";
    for (std::size_t i = 0; i < r.suites.size(); ++i)
        out += "suite_name_hex=" + Hex(kSpecs[i].name) + "\nsuite_version=" +
            std::to_string(kSpecs[i].version) + "\nacquire_error=" +
            std::to_string(r.suites[i].error) + "\nprovider_present=" +
            (r.suites[i].present ? "1\n" : "0\n");
    out += "enumeration_complete=" + std::string(r.enumeration_complete ? "1\n" : "0\n") +
        "adapter_count=" + std::to_string(r.adapters.size()) + "\n";
    for (const auto& a : r.adapters)
        out += "adapter_name_hex=" + Hex(a.name) + "\nadapter_version=" + std::to_string(a.version) + "\n";
    return out;
}
class Diagnostic {
    std::atomic<bool> consumed_{false};
public:
    Result run(Backend& b, const std::string& claim, std::uint64_t timeout_ms = 10000) {
        Result r;
        if (consumed_.exchange(true)) { r.reason = "already-consumed"; return r; }
        bool iterator = false;
        const auto start = b.now_ms();
        auto check = [&]() {
            const auto now = b.now_ms();
            if (!timeout_ms || timeout_ms > 15000 || now < start || now - start >= timeout_ms)
                throw std::runtime_error("deadline");
        };
        auto stage = [&](const std::string& name, const std::string& data = "") {
            check(); r.stage = name; b.record(name, data); check();
        };
        try {
            if (claim.empty() || claim.size() > 4096) throw std::runtime_error("invalid-claim");
            stage("claim", claim);
            stage("before-started"); const auto before = b.observe(); check();
            if (before.identity.empty() || before.project.empty() || before.registry.empty())
                throw std::runtime_error("empty-baseline");
            stage("before", Hex(before.identity) + "\n" + Hex(before.project) + "\n" + Hex(before.registry));
            for (std::size_t i = 0; i < kSpecs.size(); ++i) {
                stage("acquire-started-" + std::to_string(i));
                const auto value = b.acquire(kSpecs[i]);
                r.suites.push_back(value); check();
                stage("acquire-finished-" + std::to_string(i), Serialize(r));
                if ((value.error == 0) != value.present) throw std::runtime_error("acquire-contract");
            }
            if (r.suites.back().present) {
                stage("iterator-started"); b.new_iterator(); iterator = true; check();
                for (std::size_t i = 0; i <= 64; ++i) {
                    stage("next-started-" + std::to_string(i)); Adapter a;
                    if (!b.next_adapter(a)) { r.enumeration_complete = true; check(); break; }
                    check();
                    if (i == 64) throw std::runtime_error("adapter-limit");
                    if (a.name.empty() || a.name.size() > 256 || a.name.find('\0') != std::string::npos)
                        throw std::runtime_error("adapter-name");
                    r.adapters.push_back(a); stage("next-finished-" + std::to_string(i), Serialize(r));
                }
                stage("iterator-delete-started"); iterator = false;
                b.delete_iterator(); check(); stage("iterator-deleted");
            }
            stage("after-started"); const auto after = b.observe(); check();
            stage("after", Hex(after.identity) + "\n" + Hex(after.project) + "\n" + Hex(after.registry));
            if (before.identity != after.identity || before.project != after.project ||
                before.registry != after.registry) throw std::runtime_error("host-state-changed");
            r.status = "COMPLETE"; r.stage = "complete";
        } catch (const std::exception& e) {
            r.reason = std::string(e.what()).substr(0, 256);
        } catch (...) { r.reason = "unknown-exception"; }
        if (iterator) {
            // Own iterator cleanup only; suite leases deliberately remain held.
            iterator = false;
            try { b.record("iterator-delete-started", "failure-path"); b.delete_iterator();
                  b.record("iterator-deleted", "failure-path"); }
            catch (...) { r.reason += ";iterator-cleanup-failed"; }
        }
        try { b.record("result", Serialize(r)); }
        catch (...) { r.status = "STOPPED"; r.reason += ";result-not-durable"; }
        return r;
    }
};
} // namespace pica_probe
