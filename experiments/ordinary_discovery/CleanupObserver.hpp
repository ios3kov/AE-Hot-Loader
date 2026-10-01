// Research-only diagnostic composition. No callback invocation, provider retain,
// registration, complete observation or ResourcePassGate approval conversion.
#pragma once
#include "MappedMemoryRead.hpp"
#include <string>

namespace cleanup_observer {
using namespace cleanup_snapshot;
struct Roots { Address plug_slot = 0, mee_vector = 0; };
struct Diagnostic {
    bool success = false;
    std::string failure;
    Snapshot snapshot;
    Frame global; // PLUG slot bytes for independent diagnostic chain verification
    std::vector<mapped_memory::ReadRecord> reads;
    std::vector<mapped_memory::ReadRecord> containment_only;
    std::size_t calls = 0, bytes = 0;
};
inline std::vector<Region> Clip(std::vector<Region> spans) {
    Need(!spans.empty() && spans.size() <= 16, "observer-span-count");
    std::sort(spans.begin(), spans.end(), [](const Region& a, const Region& b) {
        return a.address < b.address;
    });
    std::vector<Region> result;
    for (const auto& span : spans) {
        const auto end = End(span.address, span.size);
        if (!result.empty() && span.address <= End(result.back().address, result.back().size)) {
            auto& last = result.back();
            last.size = std::max(end, End(last.address, last.size)) - last.address;
        } else result.push_back(span);
    }
    return result;
}
class Observer {
    bool consumed_ = false;
public:
    Diagnostic run(const Roots& supplied, mapped_memory::Backend& backend) {
        Diagnostic result;
        if (consumed_) { result.failure = "observer-consumed"; return result; }
        consumed_ = true; // failure consumes the attempt too
        const Roots roots = supplied;
        mapped_memory::Reader reader(backend);
        try {
            Need(roots.plug_slot && roots.mee_vector && roots.plug_slot % 8 == 0 &&
                 roots.mee_vector % 8 == 0 && roots.plug_slot != roots.mee_vector,
                 "observer-invalid-roots");
            std::vector<Region> spans;
            std::vector<Frame> bootstrap;
            auto read = [&](Address address, std::size_t size) {
                auto bytes = reader.read(address, size);
                spans.push_back({address, size}); bootstrap.push_back({address, bytes});
                return bytes;
            };
            auto pointer = [](Address address) {
                Need(address && address % 8 == 0, "observer-invalid-pointer");
                return address;
            };
            const auto global = read(roots.plug_slot, 8);
            result.global = {roots.plug_slot, global};
            const auto sack_slot = pointer(Word(global, 0, 8));
            const auto sack = pointer(Word(read(sack_slot, 8), 0, 8));
            const auto list_handle = pointer(Word(read(sack, 24), 16, 8));
            const auto list = pointer(Word(read(list_handle, 8), 0, 8));
            const auto header = read(list, 0x48);
            Need(Word(header, 0, 4) == 0x00d00bee, "observer-list-magic");
            const auto count = Word(header, 0x10, 4);
            Need(count <= kMaxCallbacks && Word(header, 0x18, 4) == 16,
                 "observer-list-count-or-stride");
            if (count) (void)read(End(list, 0x48), std::size_t(count) * 16);
            const auto vector = read(roots.mee_vector, 16);
            const auto begin = Word(vector, 0, 8), end = Word(vector, 8, 8);
            Need(begin % 8 == 0 && end % 8 == 0 && end >= begin &&
                 (end - begin) % 0xb0 == 0 && (end - begin) / 0xb0 <= kMaxRecords &&
                 ((begin == 0 && end == 0) || begin != 0), "observer-invalid-vector");
            mapped_memory::Region record_mapping{};
            const auto record_size = begin ? (end == begin ? Address(1) : end - begin) : 0;
            if (begin) {
                record_mapping = backend.query(begin);
                mapped_memory::Validate(record_mapping, begin, record_size);
                spans.push_back({begin, record_size}); // containment only; never copy records
                result.containment_only.push_back({begin, std::size_t(record_size), record_mapping});
            }
            const Scope scope{sack_slot, roots.mee_vector, Clip(std::move(spans))};
            auto sampled = Capture(scope, reader);
            Need(bootstrap.size() == sampled.frames.size() + 1, "observer-bootstrap-frame-count");
            for (std::size_t i = 0; i < sampled.frames.size(); ++i)
                Need(bootstrap[i + 1] == sampled.frames[i], "observer-bootstrap-changed");
            Need(reader.read(roots.plug_slot, 8) == global, "observer-global-changed");
            if (begin) {
                const auto after = backend.query(begin);
                mapped_memory::Validate(after, begin, record_size);
                Need(record_mapping == after, "observer-record-mapping-changed");
            }
            result.snapshot = std::move(sampled);
            result.success = true;
        } catch (const std::exception& e) { result.failure = e.what(); }
        catch (...) { result.failure = "observer-unknown-failure"; }
        result.reads = reader.records(); result.calls = reader.calls(); result.bytes = reader.bytes();
        return result; // diagnostic matching captures, never atomic/complete/eligible
    }
};
} // namespace cleanup_observer

#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include "ResidentDataRootBinding.hpp"
namespace cleanup_observer {
struct Profiles { resident_data_root::Profile plug, mee; };
class ResidentObserver {
    bool consumed_ = false;
public:
    Diagnostic run(const Profiles& supplied) {
        Diagnostic result;
        if (consumed_) { result.failure = "resident-observer-consumed"; return result; }
        consumed_ = true;
        const Profiles profiles = supplied;
        try {
            Need(profiles.plug.root.size == 8 && profiles.mee.root.size == 16 &&
                 profiles.plug.pin.path != profiles.mee.pin.path, "resident-observer-profiles");
            const auto images = resident_binding::Snapshot();
            const auto plug = resident_data_root::Bind(profiles.plug);
            const auto mee = resident_data_root::Bind(profiles.mee);
            mapped_memory::SelfBackend backend;
            Observer observer;
            result = observer.run({plug.address, mee.address}, backend);
            Need(result.success, "resident-observer-capture-refused");
            const auto plug_after = resident_data_root::Bind(profiles.plug);
            const auto mee_after = resident_data_root::Bind(profiles.mee);
            Need(plug.header == plug_after.header && plug.address == plug_after.address &&
                 mee.header == mee_after.header && mee.address == mee_after.address &&
                 images == resident_binding::Snapshot(), "resident-observer-identity-changed");
        } catch (const std::exception& e) {
            result.success = false;
            if (result.failure.empty()) result.failure = e.what();
            result.snapshot = {}; // preserve partial read provenance, not successful state
        } catch (...) {
            result.success = false; result.failure = "resident-observer-unknown-failure";
            result.snapshot = {};
        }
        return result;
    }
};
} // namespace cleanup_observer
#endif
