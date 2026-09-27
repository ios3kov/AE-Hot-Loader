#include <atomic>
#include <cstdint>
#include <cstdio>
#include <dlfcn.h>
#include <dispatch/dispatch.h>
#include <mutex>
#include <string>

using A_Err = std::int32_t;
using A_long = std::int32_t;
using PF_Err = std::int32_t;
using PF_Cmd = std::int32_t;

struct PF_PluginData;
using PF_PluginDataPtr = PF_PluginData*;
struct SPBasicSuite;
struct PF_InData;
struct PF_OutData;
struct PF_ParamDef;
struct PF_LayerDef;

using PF_PluginDataCB2 = A_Err (*)(
    PF_PluginDataPtr,
    const std::uint8_t*,
    const std::uint8_t*,
    const std::uint8_t*,
    const std::uint8_t*,
    A_long,
    A_long,
    A_long,
    A_long,
    const std::uint8_t*);

using CoreEffectMainFn = PF_Err (*)(
    PF_Cmd,
    PF_InData*,
    PF_OutData*,
    PF_ParamDef**,
    PF_LayerDef*,
    void*);

namespace {

constexpr A_long FourCC(char a, char b, char c, char d) {
    return (static_cast<A_long>(static_cast<std::uint8_t>(a)) << 24) |
           (static_cast<A_long>(static_cast<std::uint8_t>(b)) << 16) |
           (static_cast<A_long>(static_cast<std::uint8_t>(c)) << 8) |
            static_cast<A_long>(static_cast<std::uint8_t>(d));
}

constexpr A_long kAEEffectKind = FourCC('e', 'F', 'K', 'T');
constexpr A_long kApiMajor = 13;
constexpr A_long kApiMinor = 29;
constexpr A_long kRegistrationReservedInfo = 8;

std::atomic<int> g_plugin_data_calls{0};
std::once_flag g_core_once;
void* g_core_handle = nullptr;
CoreEffectMainFn g_core_effect_main = nullptr;
PF_PluginDataPtr g_saved_plugin_data = nullptr;
PF_PluginDataCB2 g_saved_callback = nullptr;

void Log(const char* message) {
    if (FILE* f = std::fopen("/tmp/ae-hot-loader-dualpipl.log", "a")) {
        std::fprintf(f, "%s\n", message);
        std::fclose(f);
    }
}

std::string CorePath() {
    Dl_info info{};
    if (dladdr(reinterpret_cast<const void*>(&CorePath), &info) == 0 || !info.dli_fname) {
        return {};
    }

    std::string binary_path(info.dli_fname);
    const std::string marker = "/Contents/MacOS/";
    const auto pos = binary_path.rfind(marker);
    if (pos == std::string::npos) {
        return {};
    }

    return binary_path.substr(0, pos) +
           "/Contents/Frameworks/libae_hot_loader_core.dylib";
}

void LoadCore() {
    std::call_once(g_core_once, [] {
        const std::string path = CorePath();
        if (path.empty()) {
            Log("core path resolution failed");
            return;
        }

        g_core_handle = dlopen(path.c_str(), RTLD_NOW | RTLD_LOCAL);
        if (!g_core_handle) {
            const char* error = dlerror();
            std::string msg = "core dlopen failed: ";
            msg += error ? error : "unknown";
            Log(msg.c_str());
            return;
        }

        g_core_effect_main = reinterpret_cast<CoreEffectMainFn>(
            dlsym(g_core_handle, "EffectMain"));

        Log(g_core_effect_main ? "core EffectMain resolved" : "core EffectMain missing");
    });
}

PF_Err ForwardEffectMain(
    PF_Cmd cmd,
    PF_InData* in_data,
    PF_OutData* out_data,
    PF_ParamDef** params,
    PF_LayerDef* output,
    void* extra) {
    LoadCore();
    if (!g_core_effect_main) {
        return -3001;
    }
    return g_core_effect_main(cmd, in_data, out_data, params, output, extra);
}

}  // namespace

extern "C" __attribute__((visibility("default")))
A_Err PluginDataEntryFunction2(
    PF_PluginDataPtr in_ptr,
    PF_PluginDataCB2 in_callback,
    SPBasicSuite* in_basic_suite,
    const char* in_host_name,
    const char* in_host_version) {

    const int call = g_plugin_data_calls.fetch_add(1) + 1;

    const char* name = nullptr;
    const char* match_name = nullptr;

    if (call == 1) {
        name = "AE Hot Loader Dual PiPL Fresh A";
        match_name = "OS3KOV.AEHotLoader.DualPiPL.Fresh.A";
    } else if (call == 2) {
        name = "AE Hot Loader Dual PiPL Fresh B";
        match_name = "OS3KOV.AEHotLoader.DualPiPL.Fresh.B";
    } else {
        char unexpected[256]{};
        std::snprintf(
            unexpected,
            sizeof(unexpected),
            "UNEXPECTED call=%d data=%p callback=%p suite=%p",
            call,
            static_cast<void*>(in_ptr),
            reinterpret_cast<void*>(in_callback),
            static_cast<void*>(in_basic_suite));
        Log(unexpected);
        return 1;
    }

    char before[768]{};
    std::snprintf(
        before,
        sizeof(before),
        "call=%d effect=%s data=%p callback=%p suite=%p host=%s version=%s",
        call,
        name,
        static_cast<void*>(in_ptr),
        reinterpret_cast<void*>(in_callback),
        static_cast<void*>(in_basic_suite),
        in_host_name ? in_host_name : "(null)",
        in_host_version ? in_host_version : "(null)");
    Log(before);

    if (!in_callback) {
        Log("registration callback null");
        return 1;
    }

    g_saved_plugin_data = in_ptr;
    g_saved_callback = in_callback;

    const A_Err result = in_callback(
        in_ptr,
        reinterpret_cast<const std::uint8_t*>(name),
        reinterpret_cast<const std::uint8_t*>(match_name),
        reinterpret_cast<const std::uint8_t*>("AE Hot Loader Diagnostic"),
        reinterpret_cast<const std::uint8_t*>("EffectMain"),
        kAEEffectKind,
        kApiMajor,
        kApiMinor,
        kRegistrationReservedInfo,
        reinterpret_cast<const std::uint8_t*>("https://github.com/ios3kov/AE-Hot-Loader"));

    char after[256]{};
    std::snprintf(
        after,
        sizeof(after),
        "call=%d effect=%s registration_result=%d",
        call,
        name,
        result);
    Log(after);

    if (call == 1) {
        const char* second_name = "AE Hot Loader Dual PiPL Fresh B";
        const char* second_match = "OS3KOV.AEHotLoader.DualPiPL.Fresh.B";

        const A_Err second_result = in_callback(
            in_ptr,
            reinterpret_cast<const std::uint8_t*>(second_name),
            reinterpret_cast<const std::uint8_t*>(second_match),
            reinterpret_cast<const std::uint8_t*>("AE Hot Loader Diagnostic"),
            reinterpret_cast<const std::uint8_t*>("EffectMain"),
            kAEEffectKind,
            kApiMajor,
            kApiMinor,
            kRegistrationReservedInfo,
            reinterpret_cast<const std::uint8_t*>("https://github.com/ios3kov/AE-Hot-Loader"));

        char second[320]{};
        std::snprintf(
            second,
            sizeof(second),
            "call=%d SECOND_REGISTRATION effect=%s data=%p registration_result=%d",
            call,
            second_name,
            static_cast<void*>(in_ptr),
            second_result);
        Log(second);

        dispatch_async(dispatch_get_main_queue(), ^{
            Log("DEFERRED_REGISTRATION begin");

            if (!g_saved_callback || !g_saved_plugin_data) {
                Log("DEFERRED_REGISTRATION missing saved state");
                return;
            }

            const char* deferred_name = "AE Hot Loader Deferred C";
            const char* deferred_match = "OS3KOV.AEHotLoader.Deferred.C";

            const A_Err deferred_result = g_saved_callback(
                g_saved_plugin_data,
                reinterpret_cast<const std::uint8_t*>(deferred_name),
                reinterpret_cast<const std::uint8_t*>(deferred_match),
                reinterpret_cast<const std::uint8_t*>("AE Hot Loader Diagnostic"),
                reinterpret_cast<const std::uint8_t*>("EffectMain"),
                kAEEffectKind,
                kApiMajor,
                kApiMinor,
                kRegistrationReservedInfo,
                reinterpret_cast<const std::uint8_t*>("https://github.com/ios3kov/AE-Hot-Loader"));

            char deferred[384]{};
            std::snprintf(
                deferred,
                sizeof(deferred),
                "DEFERRED_REGISTRATION effect=%s data=%p registration_result=%d",
                deferred_name,
                static_cast<void*>(g_saved_plugin_data),
                deferred_result);
            Log(deferred);
        });
    }

    return result;
}

extern "C" __attribute__((visibility("default")))
PF_Err EffectMain(
    PF_Cmd cmd,
    PF_InData* in_data,
    PF_OutData* out_data,
    PF_ParamDef** params,
    PF_LayerDef* output,
    void* extra) {
    return ForwardEffectMain(cmd, in_data, out_data, params, output, extra);
}
