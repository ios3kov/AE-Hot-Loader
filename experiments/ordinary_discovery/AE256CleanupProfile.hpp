// Fixed read-only diagnostic roots. Static offsets are not live lifetime/consent.
#pragma once
#include "AE256ResourceProfile.hpp"
#include "CleanupObserver.hpp"
#include <string_view>
namespace ae256_cleanup {
struct RootPin {
    std::string_view path, sha256, uuid, anchor, section;
    std::uint64_t vm = 0, size = 0;
};
inline constexpr RootPin kPlug{
    ae256_resource::kImages[6].path, ae256_resource::kImages[6].sha256,
    "d4ddb055e565378fb8f433ac0bb2253d",
    "__Z11PLUG_SearchPP9PLUG_SacksPP9FILE_SpectsPKcPFisS6_PvPhES7_RiS8_",
    "__common", 0x18490, 8};
inline constexpr RootPin kMee{
    ae256_resource::kImages[5].path, ae256_resource::kImages[5].sha256,
    "74a30dbaa08b367bbd9915d6d77e9d52", "__Z13MEE_GetGPListv", "__bss", 0x10fd70, 16};
} // namespace ae256_cleanup
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
namespace ae256_cleanup {
template<std::size_t N> inline std::array<unsigned char, N> Decode(std::string_view s) {
    cleanup_snapshot::Need(s.size() == N * 2, "cleanup-profile-hex-length");
    std::array<unsigned char, N> out{};
    const std::string_view digits = "0123456789abcdef";
    for (std::size_t i = 0; i < N; ++i) {
        const auto a = digits.find(s[i * 2]), b = digits.find(s[i * 2 + 1]);
        cleanup_snapshot::Need(a != digits.npos && b != digits.npos, "cleanup-profile-invalid-hex");
        out[i] = static_cast<unsigned char>(a * 16 + b);
    }
    return out;
}
inline resident_data_root::Profile Profile(const RootPin& p) {
    return {{std::string(p.path), Decode<32>(p.sha256)}, std::string(p.anchor),
            {p.vm, p.size, std::string(p.section)}, Decode<16>(p.uuid)};
}
inline cleanup_observer::Profiles Reviewed() { return {Profile(kPlug), Profile(kMee)}; }
} // namespace ae256_cleanup
#endif
