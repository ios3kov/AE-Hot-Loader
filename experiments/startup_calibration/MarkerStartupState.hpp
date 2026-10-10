#pragma once
#include <cstdint>
#include <cstddef>

namespace startup_marker {
// Own diagnostic ABI only. Independently sampled counters are not a drain or
// descriptor lifetime proof. Reading this state never invokes an AE selector.
struct StartupState {
    std::uint32_t magic = 0x41454853;
    std::uint32_t version = 4;
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
    std::uint32_t metadata_entry_present = 1;
    std::uint32_t context_ready = 0;
    std::uint32_t host_name_status = 0;
    std::uint32_t host_version_status = 0;
    char host_name[96]{};
    char host_version[96]{};
};
using ReadStartupState = bool (*)(StartupState*) noexcept;

// Own host-supplied SDK strings only. No pointers survive the callback.
// Status: 0 unavailable/null, 1 complete, 2 truncated (never a complete fact).
template<std::size_t N> inline std::uint32_t CopyContext(char (&out)[N], const char* value) noexcept {
    static_assert(N > 1, "bounded context buffer");
    for (auto& byte : out) byte = 0;
    if (!value) return 0;
    for (std::size_t i = 0; i < N; ++i) {
        if (!value[i]) return 1;
        if (i == N - 1) return 2;
        out[i] = value[i];
    }
    return 2;
}
inline bool ResourceOnlyWitness(const StartupState& state) noexcept {
    return state.magic == 0x41454853 && state.version == 4 &&
        state.reserved == 0 && state.reserved2 == 0 &&
        state.metadata_entry_present == 0 && state.registration_started == 0 &&
        state.registration_completed == 0 && state.last_callback_result == 0 &&
        state.callback_address == 0 && state.registration_on_main == 0 && state.context_ready == 0 &&
        state.host_name_status == 0 && state.host_version_status == 0 &&
        state.host_name[0] == 0 && state.host_version[0] == 0;
}
} // namespace startup_marker
