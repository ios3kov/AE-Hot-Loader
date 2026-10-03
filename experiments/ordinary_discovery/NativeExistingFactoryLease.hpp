// Repo-owned explicitly declared ABI prototype only. No MEE/private Adobe call,
// InterfaceRef construction, copied-control mutation or ResourcePassGate approval.
#pragma once
#include "ResidentImageLease.hpp"
#include "OwnedFactoryAbi.hpp"
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
namespace owned_factory_lease {
using namespace resident_binding;
class Lease {
    ImageLease image_;
    owned_factory_abi::Ref ref_{};
    owned_factory_abi::ReleaseFn release_ = nullptr;
    owned_factory_abi::ValueFn value_ = nullptr;
    void ReleaseReference() noexcept {
        if (!ref_.owner) return;
        if (pthread_main_np() != 1 || !release_) std::terminate();
        release_(ref_.owner); ref_ = {};
    }
public:
    Lease() = default;
    Lease(const Lease&) = delete;
    Lease& operator=(const Lease&) = delete;
    Lease(Lease&& other) noexcept : image_(std::move(other.image_)), ref_(other.ref_),
                                  release_(other.release_), value_(other.value_) { other.ref_ = {}; }
    Lease& operator=(Lease&& other) noexcept {
        if (this == &other) return *this;
        ReleaseReference(); image_ = std::move(other.image_);
        ref_ = other.ref_; release_ = other.release_; value_ = other.value_; other.ref_ = {}; return *this;
    }
    ~Lease() { ReleaseReference(); } // image_ closes AFTER release/destruction
    void Reset() noexcept { ReleaseReference(); image_ = ImageLease{}; release_ = nullptr; value_ = nullptr; }
    static Lease Acquire(const Pin& pin, const std::array<unsigned char, 16>& uuid) {
        Lease result;
        result.image_ = ImageLease::Retain(pin, uuid, {"_AEHL_OwnedFactoryVersion", "_AEHL_OwnedFactoryAcquire",
                                                      "_AEHL_OwnedFactoryRelease", "_AEHL_OwnedFactoryValue"});
        const auto version = reinterpret_cast<owned_factory_abi::VersionFn>(result.image_.Function("_AEHL_OwnedFactoryVersion"));
        const auto acquire = reinterpret_cast<owned_factory_abi::AcquireFn>(result.image_.Function("_AEHL_OwnedFactoryAcquire"));
        result.release_ = reinterpret_cast<owned_factory_abi::ReleaseFn>(result.image_.Function("_AEHL_OwnedFactoryRelease"));
        result.value_ = reinterpret_cast<owned_factory_abi::ValueFn>(result.image_.Function("_AEHL_OwnedFactoryValue"));
        Require(version() == owned_factory_abi::Version);
        result.ref_ = acquire(); // typed 24-byte return; module owns opaque reference operations
        if (!result.ref_.object && !result.ref_.owner && !result.ref_.generation) return {};
        // Destructor balances any nonnull owner even when the returned shape refuses.
        Require(result.ref_.object && result.ref_.owner && result.ref_.generation);
        result.image_.Check(); return result;
    }
    explicit operator bool() const noexcept { return ref_.object && ref_.owner && ref_.generation; }
    std::uint64_t Generation() const { Require(bool(*this) && pthread_main_np() == 1); return ref_.generation; }
    std::int64_t Value() const {
        Require(bool(*this) && pthread_main_np() == 1); image_.Check();
        return value_(ref_.object, ref_.generation);
    }
};
} // namespace owned_factory_lease
#endif
