#include <cstdint>
#include <cstdio>

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

constexpr A_long FourCC(char a, char b, char c, char d) {
    return (static_cast<A_long>(static_cast<std::uint8_t>(a)) << 24) |
           (static_cast<A_long>(static_cast<std::uint8_t>(b)) << 16) |
           (static_cast<A_long>(static_cast<std::uint8_t>(c)) << 8) |
            static_cast<A_long>(static_cast<std::uint8_t>(d));
}

extern "C" __attribute__((visibility("default")))
A_Err PluginDataEntryFunction2(
    PF_PluginDataPtr in_ptr,
    PF_PluginDataCB2 in_callback,
    SPBasicSuite* in_basic_suite,
    const char* in_host_name,
    const char* in_host_version) {
    if (FILE* f = std::fopen("/tmp/ae-hot-loader-singlepipl-cpp.log", "a")) {
        std::fprintf(
            f,
            "ENTRY data=%p callback=%p suite=%p host=%s version=%s\n",
            static_cast<void*>(in_ptr),
            reinterpret_cast<void*>(in_callback),
            static_cast<void*>(in_basic_suite),
            in_host_name ? in_host_name : "(null)",
            in_host_version ? in_host_version : "(null)");
        std::fclose(f);
    }

    if (!in_callback) {
        return 1;
    }

    const A_Err result = in_callback(
        in_ptr,
        reinterpret_cast<const std::uint8_t*>("AE Hot Loader Single PiPL C++ Fresh"),
        reinterpret_cast<const std::uint8_t*>("OS3KOV.AEHotLoader.SinglePiPLCpp.Fresh"),
        reinterpret_cast<const std::uint8_t*>("AE Hot Loader Diagnostic"),
        reinterpret_cast<const std::uint8_t*>("EffectMain"),
        FourCC('e','F','K','T'),
        13,
        29,
        8,
        reinterpret_cast<const std::uint8_t*>("https://github.com/ios3kov/AE-Hot-Loader"));

    if (FILE* f = std::fopen("/tmp/ae-hot-loader-singlepipl-cpp.log", "a")) {
        std::fprintf(f, "REGISTRATION_RESULT=%d\n", result);
        std::fclose(f);
    }
    return result;
}

extern "C" __attribute__((visibility("default")))
PF_Err EffectMain(
    PF_Cmd,
    PF_InData*,
    PF_OutData*,
    PF_ParamDef**,
    PF_LayerDef*,
    void*) {
    return 0;
}
