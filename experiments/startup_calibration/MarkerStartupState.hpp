#pragma once
#include <cstdint>

namespace startup_marker {
// Own diagnostic ABI only. Independently sampled counters are not a drain or
// descriptor lifetime proof. Reading this state never invokes an AE selector.
struct StartupState {
    std::uint32_t magic = 0x41454853;
    std::uint32_t version = 3;
    std::uint64_t registration_started = 0;
    std::uint64_t registration_completed = 0;
    std::int32_t last_callback_result = 0;
    std::uint32_t reserved = 0;
    std::uint64_t global_setup_calls = 0;
    std::uint64_t parameter_setup_calls = 0;
    std::uint64_t callback_address = 0;
    std::uint32_t registration_on_main = 0;
    std::uint32_t reserved2 = 0;
    char registration_name[64]{};
    char registration_match[64]{};
};
using ReadStartupState = bool (*)(StartupState*) noexcept;
} // namespace startup_marker
