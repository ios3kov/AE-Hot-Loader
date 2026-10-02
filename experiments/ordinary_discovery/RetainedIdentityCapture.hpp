#pragma once
#include "MappedMemoryRead.hpp"
#include "RetainedRecordIdentity.hpp"
#include <atomic>
#include <string>
#include <utility>

// Separate diagnostic core. Caller must supply an independently bound root and
// authorized backend. Matching copies do not establish atomicity, allocation,
// provider identity, repeat safety or ResourcePassGate eligibility.
namespace retained_capture {
using retained_identity::Address;
using retained_identity::Bytes;
using retained_identity::Layout;
using retained_identity::NameCopy;
using retained_identity::Need;
using retained_identity::Word;
struct Snapshot {
    Bytes vector;
    Bytes records;
    std::vector<NameCopy> names;
};
struct Diagnostic {
    bool success = false;
    std::string failure;
    Snapshot snapshot;
    std::vector<retained_identity::Record> identities;
    std::vector<mapped_memory::ReadRecord> reads;
    std::size_t calls = 0, bytes = 0;
};
class Observer {
    std::atomic<bool> consumed_{false};
public:
    // Four vector reads + two record reads + sixteen name reads at maximum.
    static constexpr std::size_t kCalls = 22, kBytes = 6976;
    Diagnostic run(Layout layout, Address vector_root, mapped_memory::Backend& backend) {
        Diagnostic result;
        // Claim before any backend access, including concurrent callers.
        if (consumed_.exchange(true)) {
            result.failure = "retained-capture-consumed"; return result;
        } // Invalid input, copy failure and mismatch consume too.
        mapped_memory::Reader reader(backend);
        try {
            retained_identity::Validate(layout, {}, 0);
            Need(vector_root && vector_root % 8 == 0 && vector_root <= UINT64_MAX - 16,
                 "retained-capture-invalid-root");
            auto read = [&](Address address, std::size_t size) {
                Need(reader.calls() < kCalls && size <= kBytes &&
                     reader.bytes() <= kBytes - size, "retained-capture-budget");
                auto bytes = reader.read(address, size);
                const auto& current = reader.records().back();
                for (const auto& prior : reader.records())
                    if (prior.address == current.address)
                        Need(prior.mapping == current.mapping,
                             "retained-capture-mapping-changed");
                return bytes;
            };
            const auto overlaps = [](Address a, std::size_t as, Address b, std::size_t bs) {
                // All callers validated representable end-exclusive ranges.
                return as && bs && a < b + bs && b < a + as;
            };
            auto capture = [&](const Snapshot* expected) {
                Snapshot snapshot;
                snapshot.vector = read(vector_root, 16);
                if (expected) Need(snapshot.vector == expected->vector,
                                   "retained-capture-vector-changed");
                const auto begin = Word(snapshot.vector, 0), end = Word(snapshot.vector, 8);
                Need(begin % 8 == 0 && end % 8 == 0 && end >= begin &&
                     (end - begin) % retained_identity::kStride == 0 &&
                     (end - begin) / retained_identity::kStride <= retained_identity::kMaxRecords &&
                     ((begin == 0 && end == 0) || begin != 0),
                     "retained-capture-invalid-vector");
                const auto size = static_cast<std::size_t>(end - begin);
                const auto count = size / retained_identity::kStride;
                Need(!overlaps(vector_root, 16, begin, size),
                     "retained-capture-record-root-overlap");
                if (size) snapshot.records = read(begin, size);
                if (expected) Need(snapshot.records == expected->records,
                                   "retained-capture-records-changed");
                const auto plan = retained_identity::Plan(layout, snapshot.records, count);
                for (const auto& name : plan) {
                    Need(!overlaps(name.address, name.size, vector_root, 16) &&
                         !overlaps(name.address, name.size, begin, size),
                         "retained-capture-name-state-overlap");
                    auto bytes = read(name.address, name.size);
                    if (expected) {
                        const auto i = snapshot.names.size();
                        Need(i < expected->names.size() &&
                             expected->names[i].index == name.index &&
                             expected->names[i].address == name.address &&
                             expected->names[i].bytes == bytes,
                             "retained-capture-name-changed");
                    }
                    snapshot.names.push_back({name.index, name.address, std::move(bytes)});
                }
                Need(read(vector_root, 16) == snapshot.vector,
                     "retained-capture-vector-changed");
                // Refuse malformed strings/overlap inconsistencies in each pass.
                (void)retained_identity::Decode(layout, snapshot.records, count, snapshot.names);
                return snapshot;
            };
            auto first = capture(nullptr);
            (void)capture(&first); // No retry; retargeting refused before derived reads.
            result.identities = retained_identity::Decode(layout, first.records,
                first.records.size() / retained_identity::kStride, first.names);
            result.snapshot = std::move(first);
            result.success = true;
        } catch (const std::exception& error) { result.failure = error.what(); }
        catch (...) { result.failure = "retained-capture-unknown-failure"; }
        result.reads = reader.records(); result.calls = reader.calls(); result.bytes = reader.bytes();
        return result; // Failed attempts expose read provenance, no successful snapshot.
    }
};
} // namespace retained_capture
