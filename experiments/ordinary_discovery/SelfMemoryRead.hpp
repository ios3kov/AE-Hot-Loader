// Read only the CURRENT process. No attach, task_for_pid, target selection or load.
#pragma once
#include <cstddef>
#include <cstdint>
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <mach/mach.h>
#include <mach/mach_vm.h>
namespace directory_spec {
inline bool ReadSelfMemory(const void* source, void* destination, std::size_t size) noexcept {
    constexpr std::size_t limit = 8194; // maximum path including UTF-16 terminator
    const auto address = reinterpret_cast<std::uintptr_t>(source);
    if (!source || !destination || !size || size > limit || address > UINTPTR_MAX - size)
        return false;
    mach_vm_size_t copied = 0;
    const auto status = mach_vm_read_overwrite(mach_task_self(),
        static_cast<mach_vm_address_t>(address), static_cast<mach_vm_size_t>(size),
        reinterpret_cast<mach_vm_address_t>(destination), &copied);
    return status == KERN_SUCCESS && copied == size;
}
} // namespace directory_spec
#endif
