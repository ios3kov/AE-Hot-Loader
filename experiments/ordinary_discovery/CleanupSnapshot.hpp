// Isolated research sampler over an injected reader. No process selection,
// resolver, host API, function invocation or conversion to ResourcePassGate.
// Two matching bounded captures are NOT atomicity/completeness/consent proof.
#pragma once
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <vector>

namespace cleanup_snapshot {
using Address = std::uint64_t;
using Bytes = std::vector<unsigned char>;
struct Region { Address address = 0, size = 0; };
struct Scope {
    Address sack_slot = 0, vector_slot = 0;
    std::vector<Region> readable;
};
struct Reader {
    virtual ~Reader() = default;
    // Trusted adapter: return exactly size bytes or fail, with its own time bound.
    // This synchronous sampler limits calls/bytes; it cannot preempt a reader.
    // Never invoke code at an input address.
    virtual Bytes read(Address address, std::size_t size) = 0;
};
struct Callback { Address target = 0, context = 0; };
struct Frame {
    Address address = 0;
    Bytes bytes;
    bool operator==(const Frame& other) const {
        return address == other.address && bytes == other.bytes;
    }
};
struct Snapshot {
    std::vector<Callback> callbacks; // preserve order and duplicates
    std::uint64_t general_plugin_records = 0;
    std::vector<Frame> frames; // one capture; the second matched every byte
    std::size_t bytes_read = 0, read_calls = 0;
    // Deliberately no observed/complete flag, approval digest or eligibility.
};
inline constexpr std::size_t kMaxCallbacks = 256, kMaxRecords = 8192;
inline constexpr std::size_t kReadBudget = 16384, kCallBudget = 12;
inline void Need(bool value, const char* reason) {
    if (!value) throw std::runtime_error(reason);
}
inline Address End(Address start, Address size) {
    Need(start != 0 && size != 0 && size <= UINT64_MAX - start, "snapshot-address-overflow");
    return start + size;
}
inline bool Contains(const Scope& scope, Address address, Address size) {
    const auto end = End(address, size);
    return std::any_of(scope.readable.begin(), scope.readable.end(), [&](const Region& r) {
        return address >= r.address && end <= r.address + r.size;
    });
}
inline void Validate(const Scope& scope) {
    Need(!scope.readable.empty() && scope.readable.size() <= 16, "snapshot-region-count");
    auto regions = scope.readable;
    std::sort(regions.begin(), regions.end(), [](const Region& a, const Region& b) {
        return a.address < b.address;
    });
    Address previous = 0, total = 0;
    for (const auto& r : regions) {
        const auto end = End(r.address, r.size);
        Need(r.size <= 2 * 1024 * 1024 && total <= 8 * 1024 * 1024 - r.size,
             "snapshot-region-budget");
        Need(r.address >= previous, "snapshot-overlapping-regions");
        previous = end; total += r.size;
    }
    Need(scope.sack_slot % 8 == 0 && scope.vector_slot % 8 == 0 &&
         Contains(scope, scope.sack_slot, 8) && Contains(scope, scope.vector_slot, 16),
         "snapshot-root-outside-scope");
}
inline Address Word(const Bytes& bytes, std::size_t offset, unsigned size) {
    Need((size == 4 || size == 8) && offset <= bytes.size() && size <= bytes.size() - offset,
         "snapshot-truncated-word");
    Address value = 0;
    for (unsigned i = 0; i < size; ++i) value |= Address(bytes[offset + i]) << (8 * i);
    return value; // recorded arm64 little-endian bytes, no pointer normalization
}
inline Snapshot Capture(const Scope& supplied, Reader& reader) {
    const Scope scope = supplied; // reader cannot retarget caller-owned inputs
    Validate(scope);
    std::size_t bytes_read = 0, read_calls = 0;
    auto once = [&]() {
        Snapshot result;
        auto read = [&](Address address, std::size_t size) {
            Need(size && size <= 4096 && Contains(scope, address, size),
                 "snapshot-read-outside-scope");
            Need(read_calls < kCallBudget && bytes_read <= kReadBudget - size,
                 "snapshot-read-budget");
            ++read_calls; bytes_read += size;
            Bytes bytes = reader.read(address, size);
            Need(bytes.size() == size, "snapshot-short-or-extra-read");
            result.frames.push_back({address, bytes});
            return bytes;
        };
        const auto root = read(scope.sack_slot, 8);
        const auto sack = Word(root, 0, 8);
        Need(sack && sack % 8 == 0, "snapshot-unavailable-sack");
        const auto sack_bytes = read(sack, 24);
        const auto handle = Word(sack_bytes, 16, 8);
        Need(handle && handle % 8 == 0, "snapshot-unavailable-list");
        const auto handle_bytes = read(handle, 8);
        const auto list = Word(handle_bytes, 0, 8);
        Need(list && list % 8 == 0, "snapshot-unavailable-list-header");
        const auto header = read(list, 0x48);
        Need(Word(header, 0, 4) == 0x00d00bee, "snapshot-list-magic");
        const auto count = Word(header, 0x10, 4);
        Need(count <= kMaxCallbacks && Word(header, 0x18, 4) == 16,
             "snapshot-list-count-or-stride");
        if (count) {
            const auto payload = read(End(list, 0x48), std::size_t(count) * 16);
            for (std::size_t i = 0; i < count; ++i) {
                Callback pair{Word(payload, i * 16, 8), Word(payload, i * 16 + 8, 8)};
                Need(pair.target && pair.target % 4 == 0, "snapshot-invalid-callback-target");
                result.callbacks.push_back(pair);
            }
        }
        const auto vector = read(scope.vector_slot, 16);
        const auto begin = Word(vector, 0, 8), end = Word(vector, 8, 8);
        Need(begin % 8 == 0 && end % 8 == 0 && end >= begin &&
             (end - begin) % 0xb0 == 0 && (end - begin) / 0xb0 <= kMaxRecords,
             "snapshot-invalid-vector");
        Need((begin == 0 && end == 0) || (begin != 0 &&
             Contains(scope, begin, end == begin ? 1 : end - begin)),
             "snapshot-vector-outside-scope");
        result.general_plugin_records = (end - begin) / 0xb0;
        return result;
    };
    auto before = once();
    const auto after = once();
    Need(before.frames == after.frames, "snapshot-changed-no-retry");
    before.bytes_read = bytes_read; before.read_calls = read_calls;
    return before;
}
} // namespace cleanup_snapshot
