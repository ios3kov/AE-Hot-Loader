// Owned experiment: hold explicitly enumerated callback images until the factory
// reference has been destroyed. This is not a complete AE dependency/host lease.
#pragma once
#include "NativeClassRefCallLease.hpp"
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
namespace owned_factory_dependency {
using namespace factory_code_identity;
constexpr const char* Anchor = "_AEHL_OwnedDependencyVersion";
constexpr const char* Teardown = "_AEHL_OwnedDependencyTeardown";
constexpr std::uint64_t Version = 0x4145484c00000003ULL;
class Lease {
    std::vector<ImageLease> dependencies_;
    classref_call_lease::Lease factory_;
    bool resetting_ = false;
    static std::vector<ImageLease> Transfer(Lease& other) noexcept {
        if (pthread_main_np() != 1 || other.resetting_) std::terminate();
        return std::move(other.dependencies_);
    }
    void Check() const {
        Require(pthread_main_np() == 1 && !resetting_ && !dependencies_.empty());
        for (const auto& d : dependencies_) d.Check();
    }
public:
    Lease() = default;
    Lease(const Lease&) = delete; Lease& operator=(const Lease&) = delete;
    Lease(Lease&& other) noexcept : dependencies_(Transfer(other)), factory_(std::move(other.factory_)) {}
    Lease& operator=(Lease&& other) noexcept {
        if (this == &other) return *this;
        if (pthread_main_np() != 1 || resetting_ || other.resetting_) std::terminate();
        Reset(); dependencies_ = Transfer(other); factory_ = std::move(other.factory_); return *this;
    }
    ~Lease() { Reset(); }
    void Reset() noexcept {
        if (pthread_main_np() != 1) std::terminate();
        if (resetting_) return; // same-thread callbacks cannot release twice
        resetting_ = true;
        // Cleanup may dispatch into dependencies: hold EVERY listed image first.
        factory_.Reset();
        while (!dependencies_.empty()) dependencies_.pop_back();
        resetting_ = false;
    }
    static Lease Acquire(const Profile& factory, const std::vector<Profile>& supplied) {
        // No Adobe profile or unbounded/request-derived dependency graph is accepted.
        Require(pthread_main_np() == 1 && factory.anchor == classref_call_lease::Anchor &&
                factory.spans.size() == 2 && !supplied.empty() && supplied.size() <= 8);
        std::set<std::string> paths{factory.pin.path};
        for (const auto& p : supplied)
            Require(p.anchor == Anchor && p.spans.size() == 2 && paths.insert(p.pin.path).second);
        Lease result;
        for (const auto& p : supplied) {
            auto image = ImageLease::Retain(p.pin, p.uuid, {Anchor, Teardown});
            const auto code = Bind(p);
            Require(code.spans.size() == 2 && code.spans.count("version") && code.spans.count("teardown"));
            Require(reinterpret_cast<void*>(code.spans.at("version").address) == image.Function(Anchor));
            Require(reinterpret_cast<void*>(code.spans.at("teardown").address) == image.Function(Teardown));
            const auto version = reinterpret_cast<std::uint64_t (*)() noexcept>(image.Function(Anchor));
            Require(version() == Version);
            result.dependencies_.push_back(std::move(image));
        }
        result.Check();
        result.factory_ = classref_call_lease::Lease::Acquire(factory);
        (void)result.Diagnostic(); return result;
    }
    factory_receiver_reference::Decoded Diagnostic() const { Check(); return factory_.Diagnostic(); }
    std::uintptr_t SlotAddress() const { Check(); return factory_.SlotAddress(); }
};
} // namespace owned_factory_dependency
#endif
