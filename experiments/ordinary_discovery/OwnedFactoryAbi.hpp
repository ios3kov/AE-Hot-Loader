// Isolated repo-owned research ABI. NOT Adobe InterfaceRef/shared_ptr layout.
// All calls are main-thread-only, nonthrowing, and implemented in the same module.
// Acquire never creates a factory. A nonnull owner is one releasable acquisition,
// including on malformed-result refusal. Absent is exactly three zero fields.
#pragma once
#include <cstdint>
#include <type_traits>
namespace owned_factory_abi {
constexpr std::uint64_t Version = 0x4145484c00000001ULL;
struct Ref { void* object; void* owner; std::uint64_t generation; };
static_assert(std::is_standard_layout<Ref>::value && std::is_trivially_copyable<Ref>::value);
static_assert(sizeof(void*) == 8 && sizeof(Ref) == 24);
using VersionFn = std::uint64_t (*)() noexcept;
using AcquireFn = Ref (*)() noexcept;
using ReleaseFn = void (*)(void*) noexcept;
using ValueFn = std::int64_t (*)(void*, std::uint64_t) noexcept;
} // namespace owned_factory_abi
extern "C" {
std::uint64_t AEHL_OwnedFactoryVersion() noexcept;
owned_factory_abi::Ref AEHL_OwnedFactoryAcquire() noexcept;
void AEHL_OwnedFactoryRelease(void*) noexcept;
std::int64_t AEHL_OwnedFactoryValue(void*, std::uint64_t) noexcept;
}
