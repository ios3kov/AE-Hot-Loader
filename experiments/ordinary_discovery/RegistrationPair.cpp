// Registration-only fixture: never apply/render this no-op effect.
#include <cstdint>

using Callback = std::int32_t (*)(void*, const char*, const char*, const char*,
                                const char*, std::int32_t, std::int32_t,
                                std::int32_t, std::int32_t, const char*);

extern "C" __attribute__((visibility("default")))
std::int32_t EffectMain(std::int32_t, void*, void*, void*, void*, void*) {
    return 0;
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
