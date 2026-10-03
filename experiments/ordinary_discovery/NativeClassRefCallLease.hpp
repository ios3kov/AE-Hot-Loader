// Owned native ABI experiment only. Bind point-in-time reviewed code to an image
// lease, then call a nontrivial 24-byte result through the narrow machine carrier.
// The MEE identity-only profile is refused. No Adobe invocation/gate integration.
#pragma once
#include "NativeFactoryCodeIdentity.hpp"
#include "ResidentImageLease.hpp"
#include "FactoryReceiverReference.hpp"
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <memory>
extern "C" void AEHL_CallExistingClassRef(void* entry, void* result);
extern "C" void AEHL_DestroyClassRef(void* entry, void* result) noexcept;
namespace classref_call_lease {
using namespace factory_code_identity;
constexpr const char* Anchor = "_AEHL_ClassRefBridgeVersion";
constexpr const char* AcquireSymbol = "__ZN21aehl_classref_control7AcquireEb";
constexpr const char* DestroySymbol = "_AEHL_ClassRefControlDestroy";
constexpr std::uint64_t Version = 0x4145484c00000002ULL;
struct Slot {
    // Raw allocation: the owned callee constructs its actual C++ reference here.
    // No caller-side invented C++ class/shared_ptr ever occupies these bytes.
    void* allocation = ::operator new(40);
    Slot() { std::memset(allocation, 0xa5, 40); std::memset(Data(), 0, 24); }
    Slot(const Slot&) = delete; Slot& operator=(const Slot&) = delete;
    ~Slot() { ::operator delete(allocation); }
    void* Data() const { return static_cast<unsigned char*>(allocation) + 8; }
    void Check() const {
        const auto* p = static_cast<const unsigned char*>(allocation);
        for (unsigned i = 0; i < 8; ++i) Require(p[i] == 0xa5 && p[32+i] == 0xa5);
    }
};
class Lease {
    ImageLease image_;
    Profile profile_{};
    BoundCode code_{};
    std::unique_ptr<Slot> slot_;
    bool constructed_ = false;
    void Destroy() noexcept {
        if (!constructed_) return;
        if (pthread_main_np() != 1 || !slot_) std::terminate();
        // The originally bound owned destructor operates on the ENTIRE result.
        // Lifetime release must still run if disk bytes changed after acquisition.
        AEHL_DestroyClassRef(reinterpret_cast<void*>(code_.spans.at("destroy").address), slot_->Data());
        constructed_ = false;
    }
public:
    Lease() = default;
    Lease(const Lease&) = delete; Lease& operator=(const Lease&) = delete;
    Lease(Lease&& other) noexcept : image_(std::move(other.image_)), profile_(std::move(other.profile_)),
        code_(std::move(other.code_)), slot_(std::move(other.slot_)), constructed_(other.constructed_) {
        other.constructed_ = false;
    }
    Lease& operator=(Lease&& other) noexcept {
        if (this == &other) return *this;
        if (pthread_main_np() != 1 && (constructed_ || other.constructed_)) std::terminate();
        Destroy(); slot_.reset(); image_ = std::move(other.image_);
        profile_ = std::move(other.profile_); code_ = std::move(other.code_);
        slot_ = std::move(other.slot_); constructed_ = other.constructed_; other.constructed_ = false; return *this;
    }
    ~Lease() { Destroy(); } // raw slot freed, then image lease closes after destructor
    void Reset() noexcept { Destroy(); slot_.reset(); image_ = ImageLease{}; }
    static Lease Acquire(const Profile& p) {
        Require(pthread_main_np() == 1 && p.anchor == Anchor && p.spans.size() == 2);
        Lease result; result.profile_ = p;
        result.image_ = ImageLease::Retain(p.pin, p.uuid, {Anchor, AcquireSymbol, DestroySymbol});
        result.code_ = Bind(p);
        Require(result.code_.spans.size() == 2 && result.code_.spans.count("acquire") && result.code_.spans.count("destroy"));
        Require(reinterpret_cast<void*>(result.code_.spans.at("acquire").address) == result.image_.Function(AcquireSymbol));
        Require(reinterpret_cast<void*>(result.code_.spans.at("destroy").address) == result.image_.Function(DestroySymbol));
        const auto version = reinterpret_cast<std::uint64_t (*)() noexcept>(result.image_.Function(Anchor));
        Require(version() == Version);
        result.slot_ = std::make_unique<Slot>();
        AEHL_CallExistingClassRef(reinterpret_cast<void*>(result.code_.spans.at("acquire").address), result.slot_->Data());
        result.constructed_ = true; // only a NORMAL completed result may be destroyed
        result.slot_->Check(); (void)result.Diagnostic(); result.image_.Check(); return result;
    }
    factory_receiver_reference::Decoded Diagnostic() const {
        Require(pthread_main_np() == 1 && constructed_ && slot_); image_.Check(); slot_->Check();
        factory_receiver_reference::Bytes bytes{}; std::memcpy(bytes.data(), slot_->Data(), bytes.size());
        return factory_receiver_reference::Decode(bytes, factory_receiver_reference::ReviewedAE256Layout());
        // This shape/read of own output is not initial liveness proof for AE.
    }
    std::uintptr_t SlotAddress() const {
        Require(pthread_main_np() == 1 && constructed_ && slot_); return reinterpret_cast<std::uintptr_t>(slot_->Data());
    }
};
} // namespace classref_call_lease
#endif
