#pragma once
#include <algorithm>
#include <cstdint>
#include <string>
#include <vector>

namespace startup_names {
struct Entry { std::int32_t key; std::string name, match; };
struct Snapshot {
    bool complete = false;
    const char* stage = "name-observation-guard";
    std::int32_t count = 0, traversed = 0, exact = 0;
    std::int64_t revision = 0;
    std::vector<Entry> own;
};
// Read-only evidence, never an Apply decision. Only our identifiable names are
// retained; all other names are transient. Keys remain opaque cursor values.
template<class Backend>
Snapshot Observe(Backend& b, const std::string& own_name, const std::string& target) {
    Snapshot s;
    s.revision = b.BlankProjectRevision();
    if (s.revision <= 0 || !b.ObservationAllowed()) return s;
    s.count = b.Count();
    s.stage = "name-observation-count";
    if (s.count < 1 || s.count > 8192) return s;
    std::vector<std::int32_t> seen;
    seen.reserve(static_cast<std::size_t>(s.count));
    std::int32_t cursor = 0;
    for (int i = 0; i < s.count; ++i) {
        s.stage = "name-observation-deadline";
        if (!b.ObservationAllowed()) return s;
        cursor = b.Next(cursor);
        s.stage = "name-observation-cursor";
        if (!cursor || std::find(seen.begin(), seen.end(), cursor) != seen.end()) return s;
        seen.push_back(cursor); ++s.traversed;
        const auto match = b.Match(cursor);
        const auto name = b.Name(cursor);
        if (match == target) ++s.exact;
        if (name == own_name || match.rfind("AEHL.Marker.", 0) == 0 || match.rfind("AEHL.M.", 0) == 0) {
            s.stage = "name-observation-own-bound";
            if (s.own.size() >= 16) return s;
            s.own.push_back({cursor, name, match});
        }
    }
    s.stage = "name-observation-end";
    if (!b.ObservationAllowed() || b.Next(cursor) != 0) return s;
    s.stage = "name-observation-count-changed";
    if (b.Count() != s.count) return s;
    s.stage = "name-observation-project-changed";
    if (!b.ObservationAllowed() || b.BlankProjectRevision() != s.revision) return s;
    s.complete = true; s.stage = "name-observation-complete";
    return s;
}

// Monotonic scheduling only. No sleeps, SDK calls, worker-thread calls or retry
// of registration/Apply. A sample may arrive later than its requested offset.
class Schedule {
    const std::uint64_t start_;
    unsigned index_ = 0;
public:
    explicit Schedule(std::uint64_t start) : start_(start) {}
    bool Due(std::uint64_t now) const {
        constexpr std::uint64_t offsets[] = {0, 1000, 3000};
        return index_ < 3 && now >= start_ && now - start_ >= offsets[index_];
    }
    unsigned Index() const { return index_; }
    bool Done() const { return index_ == 3; }
    void Advance() { if (index_ < 3) ++index_; }
};
} // namespace startup_names
