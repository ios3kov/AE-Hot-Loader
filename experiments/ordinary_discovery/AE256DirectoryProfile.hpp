// Research-only input identity for the supplied AE 25.6x101 arm64 files.
// Hashes identify files, NOT a proven live ABI or permission to execute it.
// No installation, resolver, constructor, host operation or automatic invocation.
#pragma once
#include <array>
#include <cstdint>
#include <string>
namespace ae256_directory {
using Digest = std::array<unsigned char, 32>;
template<std::size_t N> constexpr Digest FromHex(const char (&text)[N]) {
    static_assert(N == 65, "A SHA-256 literal is required");
    if (text[64] != '\0') throw "invalid SHA-256 literal";
    Digest result{};
    for (unsigned i = 0; i < 32; ++i) {
        const auto nibble = [](char c) constexpr -> unsigned {
            if (c >= '0' && c <= '9') return unsigned(c - '0');
            if (c >= 'a' && c <= 'f') return unsigned(c - 'a' + 10);
            throw "invalid SHA-256 literal";
        };
        result[i] = static_cast<unsigned char>((nibble(text[i * 2]) << 4) | nibble(text[i * 2 + 1]));
    }
    return result;
}
inline constexpr Digest kFile = FromHex("df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864");
inline constexpr Digest kUtility = FromHex("aecabb33c5ac5948ad742848c46588398bc690411b70aae7ca3f08a919362daa");
inline constexpr Digest kCore = FromHex("cb6faaf5b745903b80b44105b658ab68186d5065ae47c8a57c9b23e26aa8ecb0");
inline constexpr const char* kFrameworks =
    "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks";
inline constexpr const char* kReview = "U_DVACORE_CONTRACT_2026-10-01";
} // namespace ae256_directory
