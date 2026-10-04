#pragma once
#include <algorithm>
#include <cstdint>
#include <string>
#include <vector>

namespace startup_calibration {
struct Authorization {
    std::string token;
    int pid = 0;
    std::uint64_t birth = 0;
    std::uint64_t deadline = 0;
    bool owned_blank_project = false;
};
enum class Outcome { Refused, ListedApplied, PartialUnknown };
struct Result {
    Outcome outcome = Outcome::Refused;
    std::int32_t key = 0;
    const char* stage = "authorization";
};

// Backend owns acquired suites/handles. Keys are opaque cursors, never indices.
// Consume before every callback: recursive entry and replay cannot repeat Apply.
class Once {
    bool consumed_ = false;
public:
    template<class Backend>
    Result Run(const Authorization& request, const Authorization& bound, Backend& backend) {
        if (consumed_) return {};
        consumed_ = true;
        Result result;
        auto time_ok = [&]() {
            const auto now = backend.Now();
            return request.deadline > now && request.deadline - now <= 120;
        };
        if (!backend.MainThread() || !request.owned_blank_project ||
            request.token.empty() || request.token != bound.token ||
            request.pid <= 0 || request.pid != bound.pid || request.birth == 0 ||
            request.birth != bound.birth || !time_ok() || !backend.Consume()) return result;
        result.stage = "project-guard";
        auto revision = backend.BlankProjectRevision();
        if (revision <= 0 || !time_ok()) return result;
        result.stage = "enumeration";
        const auto count = backend.Count();
        if (count < 1 || count > 8192) { result.stage = "enumeration-count-range"; return result; }
        std::vector<std::int32_t> seen;
        seen.reserve(static_cast<std::size_t>(count));
        std::int32_t cursor = 0;
        int matches = 0;
        for (int i = 0; i < count; ++i) {
            if (!time_ok()) { result.stage = "enumeration-deadline"; return result; }
            cursor = backend.Next(cursor);
            if (!cursor) { result.stage = "enumeration-early-end"; return result; }
            if (std::find(seen.begin(), seen.end(), cursor) != seen.end()) {
                result.stage = "enumeration-repeated-key"; return result;
            }
            seen.push_back(cursor);
            if (backend.Match(cursor) == backend.Target()) { result.key = cursor; ++matches; }
        }
        if (matches != 1) { result.stage = matches == 0 ? "enumeration-marker-absent" :
            "enumeration-marker-duplicate"; return result; }
        if (backend.Next(cursor) != 0) { result.stage = "enumeration-missing-end"; return result; }
        if (backend.Count() != count) { result.stage = "enumeration-count-changed"; return result; }
        if (!time_ok()) { result.stage = "enumeration-deadline"; return result; }
        if (backend.BlankProjectRevision() != revision) {
            result.stage = "enumeration-project-changed"; return result;
        }
        result.stage = "before-mutation";
        if (!backend.BeforeMutation() || !time_ok()) return result;
        // Any failure after entering a mutating SDK call may leave owned host state.
        // Do not claim rollback and never delete a partially created fixture here.
        result.outcome = Outcome::PartialUnknown;
        result.stage = "create-fixture";
        if (!backend.CreateFixture()) return result;
        result.stage = "apply";
        if (!time_ok() || !backend.Apply(result.key)) return result;
        result.stage = "loaded-marker-identity";
        if (!time_ok() || !backend.VerifyBuild()) return result;
        result.stage = "reverse-key";
        if (!time_ok() || backend.Reverse() != result.key) return result;
        result.stage = "dispose-reference";
        if (!backend.Dispose()) return result;
        result.stage = "listed-applied-frame-not-run";
        result.outcome = Outcome::ListedApplied;
        return result;
    }
};
} // namespace startup_calibration
