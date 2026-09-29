// Registration-only fixture. Rendering is explicitly unsupported.
#include "AEConfig.h"
#include "AE_Effect.h"
#include <cstdint>

using Callback = std::int32_t (*)(void*, const char*, const char*, const char*,
                                const char*, std::int32_t, std::int32_t,
                                std::int32_t, std::int32_t, const char*);

extern "C" __attribute__((visibility("default")))
PF_Err EffectMain(PF_Cmd cmd, PF_InData*, PF_OutData* out,
                  PF_ParamDef*[], PF_LayerDef*, void*) {
    switch (cmd) {
    case PF_Cmd_GLOBAL_SETUP:
        if (!out) return PF_Err_BAD_CALLBACK_PARAM;
        out->my_version = 0x8001; // Matches this fixture's PiPL eVER.
        out->out_flags = 0;
        out->out_flags2 = 0;
        return PF_Err_NONE;
    case PF_Cmd_PARAMS_SETUP:
        if (!out) return PF_Err_BAD_CALLBACK_PARAM;
        out->num_params = 1; // The host-provided input layer, index zero.
        return PF_Err_NONE;
    case PF_Cmd_RENDER:
        return PF_Err_INVALID_CALLBACK;
    default:
        return PF_Err_NONE;
    }
}

#if DYNAMIC_REGISTRATION
extern "C" __attribute__((visibility("default")))
std::int32_t PluginDataEntryFunction2(void* data, Callback callback, void*,
                                     const char*, const char*) {
    if (!callback) return 1;
    return callback(data, PROBE_NAME, PROBE_MATCH, "AE Hot Loader Diagnostic",
                    "EffectMain", 0x65464b54, 13, 29, 0,
                    "https://github.com/ios3kov/AE-Hot-Loader");
}
#endif
