#pragma once

#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <vector>

// Research interpretation of one pinned MEE file, not a portable std::string ABI.
// Inputs must be caller-owned immutable copies. No host reads, pointer casts,
// callbacks, provider retention or ResourcePassGate eligibility are exposed.
namespace retained_identity {
using Address = std::uint64_t;
using Bytes = std::vector<unsigned char>;
enum class Layout { Mee256Arm64 = 1 };
constexpr std::size_t kStride = 0xb0;
constexpr std::size_t kMaxRecords = 8;
constexpr std::size_t kMaxNameBytes = 255;

struct NameRequest {
    std::size_t index;
    Address address;  // Diagnostic integer only; never dereferenced here.
    std::size_t size; // Includes one terminating NUL.
};
struct NameCopy {
    std::size_t index;
    Address address;
    Bytes bytes;
};
struct Record {
    Address descriptor;
    Address control;
    Address opaque_state;
    Address teardown;
    Address finish;
    unsigned char marker;
    bool external_name;
    Bytes name; // Raw bytes: encoding and module/provider attribution unproven.
};

inline void Need(bool condition, const char* reason) {
    if (!condition) throw std::runtime_error(reason);
}

inline Address Word(const Bytes& bytes, std::size_t offset) {
    Need(offset <= bytes.size() && bytes.size() - offset >= 8, "word bounds");
    Address value = 0;
    for (std::size_t i = 0; i < 8; ++i)
        value |= static_cast<Address>(bytes[offset + i]) << (8 * i);
    return value;
}

inline void Validate(Layout layout, const Bytes& records, std::size_t count) {
    Need(layout == Layout::Mee256Arm64, "unsupported layout");
    Need(count <= kMaxRecords, "record count limit");
    Need(records.size() == count * kStride, "record payload size");
}

// Produces a bounded copy inventory only. A separate authorized adapter must
// establish live identity, ownership, readable ranges and matching captures.
inline std::vector<NameRequest> Plan(Layout layout, const Bytes& records,
                                     std::size_t count) {
    Validate(layout, records, count);
    std::vector<NameRequest> requests;
    for (std::size_t i = 0; i < count; ++i) {
        const auto base = i * kStride;
        const auto tag = records[base + 0xa7];
        if ((tag & 0x80) == 0) {
            Need(tag <= 22, "inline name length");
            Need(records[base + 0x90 + tag] == 0, "inline name terminator");
            continue;
        }
        const auto length = Word(records, base + 0x98);
        Need(length <= kMaxNameBytes, "external name length limit");
        const auto address = Word(records, base + 0x90);
        Need(address != 0, "external name address");
        const auto size = static_cast<std::size_t>(length) + 1;
        Need(address <= std::numeric_limits<Address>::max() - size,
             "external name range overflow");
        requests.push_back({i, address, size});
    }
    return requests;
}

inline std::vector<Record> Decode(Layout layout, const Bytes& records,
                                  std::size_t count,
                                  const std::vector<NameCopy>& names) {
    const auto requests = Plan(layout, records, count);
    Need(names.size() == requests.size(), "external name inventory");
    std::vector<const NameCopy*> copies(count, nullptr);
    for (const auto& copy : names) {
        Need(copy.index < count, "external name index");
        Need(copies[copy.index] == nullptr, "duplicate external name copy");
        copies[copy.index] = &copy;
    }
    for (const auto& request : requests) {
        const auto* copy = copies[request.index];
        Need(copy != nullptr, "missing external name copy");
        Need(copy->address == request.address, "external name address mismatch");
        Need(copy->bytes.size() == request.size, "external name payload size");
        Need(copy->bytes.back() == 0, "external name terminator");
    }
    // Aliased/overlapping copies must describe the same byte snapshot. This is
    // consistency of supplied data, not proof of atomic capture or live lifetime.
    for (std::size_t i = 0; i < requests.size(); ++i) {
        for (std::size_t j = i + 1; j < requests.size(); ++j) {
            const auto& a = requests[i];
            const auto& b = requests[j];
            for (std::size_t offset = 0; offset < a.size; ++offset) {
                const auto address = a.address + offset;
                if (address >= b.address && address - b.address < b.size)
                    Need(copies[a.index]->bytes[offset] ==
                         copies[b.index]->bytes[static_cast<std::size_t>(address - b.address)],
                         "overlapping external name copies differ");
            }
        }
    }
    std::vector<Record> result;
    for (std::size_t i = 0; i < count; ++i) {
        const auto base = i * kStride;
        const bool external = (records[base + 0xa7] & 0x80) != 0;
        Bytes name;
        if (external) {
            const auto& bytes = copies[i]->bytes;
            name.assign(bytes.begin(), bytes.end() - 1);
        } else {
            Need(copies[i] == nullptr, "unexpected inline name copy");
            const auto start = records.begin() + base + 0x90;
            name.assign(start, start + records[base + 0xa7]);
        }
        result.push_back({Word(records, base), Word(records, base + 8),
                          Word(records, base + 0x10), Word(records, base + 0x58),
                          Word(records, base + 0x80), records[base + 0xa8],
                          external, name});
    }
    return result;
}
} // namespace retained_identity
