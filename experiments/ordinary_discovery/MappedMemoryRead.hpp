// Bounded diagnostic memory reader. The native backend targets CURRENT process
// only. Mapping equality is NOT allocation/lifetime/atomicity/completeness proof.
#pragma once
#include "CleanupSnapshot.hpp"

namespace mapped_memory {
using cleanup_snapshot::Address;
using cleanup_snapshot::Bytes;
using cleanup_snapshot::Need;
struct Region {
    Address address = 0, size = 0, offset = 0;
    std::uint32_t object_id = 0, user_tag = 0, depth = 0;
    int protection = 0, maximum = 0;
    bool operator==(const Region& b) const {
        return address == b.address && size == b.size && offset == b.offset &&
               object_id == b.object_id && user_tag == b.user_tag && depth == b.depth &&
               protection == b.protection && maximum == b.maximum;
    }
};
struct Backend {
    virtual ~Backend() = default;
    virtual Region query(Address address) = 0;
    virtual Bytes copy(Address address, std::size_t size) = 0;
};
struct ReadRecord { Address address = 0; std::size_t size = 0; Region mapping; };
inline void Validate(const Region& r, Address address, std::size_t size) {
    Need(r.address && r.size && r.address <= UINT64_MAX - r.size &&
         address >= r.address && address - r.address < r.size &&
         size <= r.size - (address - r.address), "mapped-read-outside-region");
    Need((r.protection & 1) != 0 && (r.protection & 4) == 0 &&
         (r.protection & ~7) == 0 && (r.maximum & ~7) == 0 &&
         (r.protection & ~r.maximum) == 0 && r.depth <= 16,
         "mapped-read-invalid-protection-or-depth");
}
class Reader final : public cleanup_snapshot::Reader {
    Backend& backend_;
    std::size_t calls_ = 0, bytes_ = 0;
    bool failed_ = false;
    std::vector<ReadRecord> records_;
public:
    // Bootstrap + two snapshot chains; fixed limits, never caller-configurable.
    static constexpr std::size_t kCalls = 24, kBytes = 16384, kChunk = 4096;
    explicit Reader(Backend& backend) : backend_(backend) {}
    Bytes read(Address address, std::size_t size) override {
        try {
            Need(!failed_, "mapped-read-consumed-failure");
            Need(address && size && size <= kChunk && address <= UINT64_MAX - size,
                 "mapped-read-invalid-request");
            Need(calls_ < kCalls && bytes_ <= kBytes - size, "mapped-read-budget");
            ++calls_; bytes_ += size; // count failed attempts, never retry/reuse their budget
            const auto before = backend_.query(address);
            Validate(before, address, size);
            const auto bytes = backend_.copy(address, size);
            Need(bytes.size() == size, "mapped-read-short-or-extra-copy");
            const auto after = backend_.query(address);
            Validate(after, address, size);
            Need(before == after, "mapped-read-region-changed");
            records_.push_back({address, size, before});
            return bytes;
        } catch (...) { failed_ = true; throw; }
    }
    std::size_t calls() const { return calls_; }
    std::size_t bytes() const { return bytes_; }
    const std::vector<ReadRecord>& records() const { return records_; }
};
} // namespace mapped_memory

#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include "SelfMemoryRead.hpp"
#include <mach/vm_region.h>
#include <pthread.h>
namespace mapped_memory {
class SelfBackend final : public Backend {
public:
    Region query(Address wanted) override {
        Need(pthread_main_np() == 1 && wanted && wanted <= UINTPTR_MAX,
             "mapped-self-wrong-thread-or-address");
        natural_t depth = 0;
        for (unsigned step = 0; step < 16; ++step) {
            mach_vm_address_t address = wanted;
            mach_vm_size_t size = 0;
            vm_region_submap_info_data_64_t info{};
            mach_msg_type_number_t count = VM_REGION_SUBMAP_INFO_V0_COUNT_64;
            const auto status = mach_vm_region_recurse(mach_task_self(), &address, &size, &depth,
                reinterpret_cast<vm_region_recurse_info_t>(&info), &count);
            Need(status == KERN_SUCCESS && count == VM_REGION_SUBMAP_INFO_V0_COUNT_64 && depth <= 16,
                 "mapped-self-query-failed");
            if (info.is_submap) { ++depth; continue; }
            return {address, size, info.offset, info.object_id, info.user_tag, depth,
                    info.protection, info.max_protection};
        }
        throw std::runtime_error("mapped-self-depth-limit");
    }
    Bytes copy(Address address, std::size_t size) override {
        Need(pthread_main_np() == 1 && address && size && size <= Reader::kChunk &&
             address <= UINTPTR_MAX - size, "mapped-self-copy-refused");
        Bytes bytes(size);
        Need(directory_spec::ReadSelfMemory(reinterpret_cast<const void*>(address), bytes.data(), size),
             "mapped-self-copy-failed");
        return bytes;
    }
};
} // namespace mapped_memory
#endif
