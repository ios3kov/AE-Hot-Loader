// Ordinary PiPL-discovered control effect. No dynamic registration or host calls.
#include "AEConfig.h"
#include "AE_Effect.h"
#include "MarkerCore.hpp"
#include "MarkerIdentity.hpp"
#include <cstring>
#include <cstddef>
#include <atomic>
#ifndef AEHL_MARKER_SEED
#define AEHL_MARKER_SEED 0x345678u
#endif
#ifndef AEHL_BUILD_ID
#define AEHL_BUILD_ID "offline-test-only"
#endif
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
        if (!out) return PF_Err_BAD_CALLBACK_PARAM;
        out->my_version = 0x8001; // Identical to the PiPL eVER.
        out->out_flags = 0;
        out->out_flags2 = 0; // No MFR, SmartFX or deep-color claim.
        return PF_Err_NONE;
    case PF_Cmd_PARAMS_SETUP:
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
