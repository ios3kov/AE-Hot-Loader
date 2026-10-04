#pragma once
#include <cstddef>
#include <cstdint>
#include <limits>

namespace startup_marker {
// Fixed 8-bit opaque pattern; the independently implemented oracle lives in Python.
inline bool Render(void* data, std::int64_t width, std::int64_t height,
                   std::int64_t stride, std::uint32_t seed) noexcept {
    if (!data || width < 1 || height < 1 || width > 4096 || height > 4096 ||
        stride < width * 4 || stride > 65536 ||
        static_cast<std::uint64_t>(stride) * static_cast<std::uint64_t>(height) >
            static_cast<std::uint64_t>(std::numeric_limits<std::ptrdiff_t>::max())) return false;
    auto* bytes = static_cast<std::uint8_t*>(data);
    for (std::int64_t y = 0; y < height; ++y) {
        auto* row = bytes + y * stride;
        for (std::int64_t x = 0; x < width; ++x) {
            const auto u = static_cast<std::uint32_t>(x);
            const auto v = static_cast<std::uint32_t>(y);
            row[x * 4] = 255;
            row[x * 4 + 1] = static_cast<std::uint8_t>(17 * u + 3 * v + seed);
            row[x * 4 + 2] = static_cast<std::uint8_t>(5 * u + 29 * v + (seed >> 8));
            row[x * 4 + 3] = static_cast<std::uint8_t>((u ^ (v * 7)) + (seed >> 16));
        }
    }
    return true;
}
} // namespace startup_marker
