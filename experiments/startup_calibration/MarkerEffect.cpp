// Ordinary PiPL-discovered control effect. No late registration or private calls.
#include "AEConfig.h"
#include "AE_Effect.h"
#include "AE_PluginData.h"
#include "MarkerCore.hpp"
#include "MarkerIdentity.hpp"
#include "MarkerStartupState.hpp"
#include <cstring>
#include <cstddef>
#include <atomic>
#ifndef AEHL_MARKER_SEED
#define AEHL_MARKER_SEED 0x345678u
#endif
#ifndef AEHL_BUILD_ID
#define AEHL_BUILD_ID "offline-test-only"
#endif
#ifndef AEHL_MARKER_NAME
#define AEHL_MARKER_NAME "AEHL Offline Marker"
#endif
#ifndef AEHL_MARKER_MATCH
#define AEHL_MARKER_MATCH "AEHL.Offline.Marker"
#endif
static std::atomic<std::uint64_t> registration_started{0}, registration_completed{0};
static std::atomic<std::int32_t> last_callback_result{0};
static std::atomic<std::uint64_t> global_setup_calls{0}, parameter_setup_calls{0};
// The exact same immutable byte arrays are passed to the host callback and
// exposed by the own diagnostic getter. Counter observations remain separate.
static constexpr char registration_name[] = AEHL_MARKER_NAME;
static constexpr char registration_match[] = AEHL_MARKER_MATCH;
static_assert(sizeof(registration_name) <= 64 && sizeof(registration_match) <= 64,
              "bounded registration metadata");

extern "C" __attribute__((visibility("default")))
bool AEHL_MarkerStartupState(startup_marker::StartupState* state) noexcept {
    if (!state || state->magic != 0x41454853 || state->version != 2 || state->reserved != 0) return false;
    state->registration_completed = registration_completed.load(std::memory_order_acquire);
    state->last_callback_result = last_callback_result.load(std::memory_order_acquire);
    state->registration_started = registration_started.load(std::memory_order_acquire);
    state->global_setup_calls = global_setup_calls.load(std::memory_order_acquire);
    state->parameter_setup_calls = parameter_setup_calls.load(std::memory_order_acquire);
    std::memset(state->registration_name, 0, sizeof(state->registration_name));
    std::memset(state->registration_match, 0, sizeof(state->registration_match));
    std::memcpy(state->registration_name, registration_name, sizeof(registration_name));
    std::memcpy(state->registration_match, registration_match, sizeof(registration_match));
    return true;
}

// Standard SDK host-invoked startup callback only. Never called by the observer.
extern "C" __attribute__((visibility("default")))
PF_Err PluginDataEntryFunction2(PF_PluginDataPtr data, PF_PluginDataCB2 callback,
                              struct SPBasicSuite*, const char*, const char*) noexcept {
    registration_started.fetch_add(1, std::memory_order_release);
    const auto result = callback ? callback(data, reinterpret_cast<const A_u_char*>(registration_name),
        reinterpret_cast<const A_u_char*>(registration_match),
        reinterpret_cast<const A_u_char*>("AE Hot Loader Diagnostic"),
        reinterpret_cast<const A_u_char*>("EffectMain"), 0x65464b54,
        PF_AE_PLUG_IN_VERSION, PF_AE_PLUG_IN_SUBVERS, 0,
        reinterpret_cast<const A_u_char*>("https://github.com/ios3kov/AE-Hot-Loader")) : PF_Err_INVALID_CALLBACK;
    last_callback_result.store(result, std::memory_order_release);
    registration_completed.fetch_add(1, std::memory_order_release);
    return result;
}

static_assert(AEHL_MARKER_SEED <= 0xffffffu, "24-bit marker seed required");
static_assert(sizeof(PF_Pixel8) == 4 && offsetof(PF_Pixel8, alpha) == 0 &&
              offsetof(PF_Pixel8, red) == 1 && offsetof(PF_Pixel8, green) == 2 &&
              offsetof(PF_Pixel8, blue) == 3, "exact SDK ARGB8 layout required");
static std::atomic<std::uint64_t> render_calls{0};

extern "C" __attribute__((visibility("default")))
const char* AEHL_MarkerBuildIdentity() noexcept { return AEHL_BUILD_ID; }

extern "C" __attribute__((visibility("default")))
PF_Err EffectMain(PF_Cmd command, PF_InData*, PF_OutData* out,
                  PF_ParamDef*[], PF_LayerDef* output, void* extra) noexcept {
    switch (command) {
    case PF_Cmd_GLOBAL_SETUP:
        global_setup_calls.fetch_add(1, std::memory_order_release);
        if (!out) return PF_Err_BAD_CALLBACK_PARAM;
        out->my_version = 0x8001; // Identical to the PiPL eVER.
        out->out_flags = 0;
        out->out_flags2 = 0; // No MFR, SmartFX or deep-color claim.
        return PF_Err_NONE;
    case PF_Cmd_PARAMS_SETUP:
        parameter_setup_calls.fetch_add(1, std::memory_order_release);
        if (!out) return PF_Err_BAD_CALLBACK_PARAM;
        out->num_params = 1;
        return PF_Err_NONE;
    case PF_Cmd_RENDER:
        if (!output || (output->world_flags & PF_WorldFlag_DEEP) ||
            !startup_marker::Render(output->data, output->width, output->height,
                                    output->rowbytes, AEHL_MARKER_SEED))
            return PF_Err_BAD_CALLBACK_PARAM;
        render_calls.fetch_add(1, std::memory_order_release);
        return PF_Err_NONE;
    case PF_Cmd_SMART_RENDER:
    case PF_Cmd_SMART_PRE_RENDER:
        return PF_Err_INVALID_CALLBACK;
    case PF_Cmd_COMPLETELY_GENERAL: {
        auto* identity = static_cast<startup_marker::Identity*>(extra);
        if (!identity || identity->magic != 0x4145484d || identity->version != 2)
            return PF_Err_BAD_CALLBACK_PARAM;
        static_assert(sizeof(AEHL_BUILD_ID) <= sizeof(identity->build), "bounded build identity");
        std::memset(identity->build, 0, sizeof(identity->build));
        std::memcpy(identity->build, AEHL_BUILD_ID, sizeof(AEHL_BUILD_ID));
        identity->seed = AEHL_MARKER_SEED;
        identity->render_calls = render_calls.load(std::memory_order_acquire);
        return PF_Err_NONE;
    }
    default:
        return PF_Err_NONE;
    }
}
