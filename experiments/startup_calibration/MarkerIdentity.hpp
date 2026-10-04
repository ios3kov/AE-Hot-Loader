#pragma once
#include <cstdint>
namespace startup_marker {
// Private to our control effect, transported by the documented generic selector.
struct Identity {
    std::uint32_t magic = 0x4145484d;
    std::uint32_t version = 1;
    char build[96]{};
    std::uint32_t seed = 0;
};
} // namespace startup_marker
