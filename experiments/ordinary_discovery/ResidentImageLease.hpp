// Main-thread continuous code residency. Only retain an ALREADY resident image.
// Acquiring/releasing this handle is a lifecycle operation, not a read-only bind
// or permission to unload a host library. No integration into the AE gate.
#pragma once
#include "ResidentImageBinding.hpp"
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <dlfcn.h>
#include <exception>
namespace resident_binding {
class ImageLease {
    void* handle_ = nullptr;
    BoundImage bound_{};
    std::vector<std::string> names_;
    void Close() noexcept {
        if (!handle_) return;
        if (pthread_main_np() != 1) std::terminate();
        if (dlclose(handle_) != 0) std::terminate();
        handle_ = nullptr;
    }
public:
    ImageLease() = default;
    ImageLease(const ImageLease&) = delete;
    ImageLease& operator=(const ImageLease&) = delete;
    ImageLease(ImageLease&& other) noexcept {
        if (other.handle_ && pthread_main_np() != 1) std::terminate();
        handle_ = other.handle_; other.handle_ = nullptr;
        bound_ = std::move(other.bound_); names_ = std::move(other.names_);
    }
    ImageLease& operator=(ImageLease&& other) noexcept {
        if (this == &other) return *this;
        if (other.handle_ && pthread_main_np() != 1) std::terminate();
        Close(); handle_ = other.handle_; other.handle_ = nullptr;
        bound_ = std::move(other.bound_); names_ = std::move(other.names_); return *this;
    }
    ~ImageLease() { Close(); }
    static ImageLease Retain(const Pin& pin, const std::array<unsigned char, 16>& uuid,
                             const std::vector<std::string>& names) {
        Require(pthread_main_np() == 1);
        Require(std::any_of(uuid.begin(), uuid.end(), [](unsigned char c) { return c; }));
        const auto before = Snapshot();
        const auto bound = Resolve(pin, names); Require(bound.image.uuid == uuid);
        ImageLease lease;
        // NOLOAD forbids absent loading; FIRST avoids dependency symbol fallback.
        lease.handle_ = dlopen(pin.path.c_str(), RTLD_NOLOAD | RTLD_NOW | RTLD_LOCAL | RTLD_FIRST);
        Require(lease.handle_);
        lease.bound_ = bound; lease.names_ = names;
        for (const auto& e : bound.functions) {
            Require(e.first.size() > 1 && e.first.front() == '_');
            Require(dlsym(lease.handle_, e.first.c_str() + 1) == e.second);
        }
        lease.Check(); Require(before == Snapshot()); return lease;
    }
    void Check() const {
        Require(pthread_main_np() == 1 && handle_);
        const auto now = Resolve(bound_.pin, names_);
        Require(now.image.uuid == bound_.image.uuid && now.functions == bound_.functions);
    }
    void* Function(const std::string& name) const {
        // Caller must keep this lease alive throughout every use of the address.
        Check(); // continuous handle lifetime does not replace source identity
        const auto it = bound_.functions.find(name); Require(it != bound_.functions.end()); return const_cast<void*>(it->second);
    }
};
} // namespace resident_binding
#endif
