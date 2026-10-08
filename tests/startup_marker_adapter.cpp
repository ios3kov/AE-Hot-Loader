// Uses real supplied SDK declarations; synthetic worlds are NOT an AE render.
#include "AEConfig.h"
#include "AE_Effect.h"
#include "AE_PluginData.h"
#include "../experiments/startup_calibration/MarkerIdentity.hpp"
#include "../experiments/startup_calibration/MarkerStartupState.hpp"
#include <cstring>
#include <dlfcn.h>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>
extern "C" PF_Err EffectMain(PF_Cmd, PF_InData*, PF_OutData*, PF_ParamDef*[], PF_LayerDef*, void*) noexcept;
void Check(bool value) { if (!value) throw std::runtime_error("adapter assertion"); }
extern "C" PF_Err PluginDataEntryFunction2(PF_PluginDataPtr, PF_PluginDataCB2,
    struct SPBasicSuite*, const char*, const char*) noexcept;
extern "C" bool AEHL_MarkerStartupState(startup_marker::StartupState*) noexcept;
static const char* expected_name = "AEHL Offline Marker";
static const char* expected_match = "AEHL.Offline.Marker";
static int registrations = 0;
static A_Err callback_result = 0;
static PF_PluginDataPtr expected_data = nullptr;
A_Err Registration(PF_PluginDataPtr data, const A_u_char* name,
    const A_u_char* match, const A_u_char* category, const A_u_char* entry,
    A_long kind, A_long major, A_long minor, A_long reserved, const A_u_char* support) {
    ++registrations;
    Check(data == expected_data && std::strcmp(reinterpret_cast<const char*>(name), expected_name) == 0 &&
        std::strcmp(reinterpret_cast<const char*>(match), expected_match) == 0 &&
        std::strcmp(reinterpret_cast<const char*>(category), "AE Hot Loader Diagnostic") == 0 &&
        std::strcmp(reinterpret_cast<const char*>(entry), "EffectMain") == 0 &&
        kind == 0x65464b54 && major == PF_AE_PLUG_IN_VERSION && minor == PF_AE_PLUG_IN_SUBVERS && reserved == 0 &&
        std::strcmp(reinterpret_cast<const char*>(support), "https://github.com/ios3kov/AE-Hot-Loader") == 0);
    return callback_result;
}
int main(int argc, char** argv) {
    try {
        auto effect = &EffectMain;
        PluginDataEntryFunction2Ptr registration = &PluginDataEntryFunction2;
        startup_marker::ReadStartupState startup = &AEHL_MarkerStartupState;
        void* library = nullptr;
        if (argc == 5) {
            library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); Check(library);
            effect = reinterpret_cast<decltype(effect)>(dlsym(library, "EffectMain")); Check(effect);
            registration = reinterpret_cast<decltype(registration)>(dlsym(library, "PluginDataEntryFunction2")); Check(registration);
            startup = reinterpret_cast<decltype(startup)>(dlsym(library, "AEHL_MarkerStartupState")); Check(startup);
            expected_name = argv[3]; expected_match = argv[4];
            using Identity = const char* (*)();
            auto identity = reinterpret_cast<Identity>(dlsym(library, "AEHL_MarkerBuildIdentity"));
            Check(identity && std::strcmp(identity(), argv[2]) == 0);
        } else Check(argc == 1);
        startup_marker::StartupState state;
        Check(!startup(nullptr));
        state.magic = 0; Check(!startup(&state)); state.magic = 0x41454853;
        state.version = 1; Check(!startup(&state)); state.version = 3;
        state.reserved = 1; Check(!startup(&state)); state.reserved = 0;
        Check(startup(&state) && state.registration_started == 0 && state.registration_completed == 0 &&
              state.global_setup_calls == 0 && state.parameter_setup_calls == 0 && state.callback_address == 0);
        Check(std::strcmp(state.registration_name, expected_name) == 0 &&
              std::strcmp(state.registration_match, expected_match) == 0);
        Check(registration(nullptr, nullptr, nullptr, nullptr, nullptr) == PF_Err_INVALID_CALLBACK && registrations == 0);
        int sentinel = 1; expected_data = reinterpret_cast<PF_PluginDataPtr>(&sentinel);
        Check(registration(expected_data, Registration, nullptr, "test-host", "test-version") == 0 && registrations == 1);
        callback_result = 37;
        Check(registration(expected_data, Registration, nullptr, nullptr, nullptr) == 37 && registrations == 2);
        Check(startup(&state) && state.registration_started == 3 && state.registration_completed == 3 &&
              state.last_callback_result == 37 && registrations == 2 &&
              state.callback_address == reinterpret_cast<std::uintptr_t>(&Registration) && state.registration_on_main == 1);
        Check(std::strcmp(state.registration_name, expected_name) == 0 &&
              std::strcmp(state.registration_match, expected_match) == 0);
        PF_OutData out{};
        Check(effect(PF_Cmd_GLOBAL_SETUP, nullptr, &out, nullptr, nullptr, nullptr) == 0);
        Check(out.my_version == 0x8001 && !out.out_flags && !out.out_flags2);
        Check(effect(PF_Cmd_PARAMS_SETUP, nullptr, &out, nullptr, nullptr, nullptr) == 0 && out.num_params == 1);
        Check(effect(PF_Cmd_GLOBAL_SETUP, nullptr, nullptr, nullptr, nullptr, nullptr) != 0);
        startup_marker::Identity identity;
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, &identity) == 0);
        Check(std::strcmp(identity.build, argc == 5 ? argv[2] : "offline-test-only") == 0);
        identity.version = 1;
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, &identity) != 0);
        identity.version = 2; identity.magic = 0;
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, &identity) != 0);
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, nullptr) != 0);
        std::vector<unsigned char> pixels(32 * 3 + 16, 0xA5); PF_LayerDef world{};
        world.data = reinterpret_cast<PF_PixelPtr>(pixels.data() + 8);
        world.width = 5; world.height = 3; world.rowbytes = 32;
        Check(effect(PF_Cmd_RENDER, nullptr, nullptr, nullptr, &world, nullptr) == 0);
        startup_marker::Identity rendered;
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, &rendered) == 0);
        Check(rendered.render_calls == 1);
        for (int y = 0; y < 3; ++y) for (int x = 20; x < 32; ++x) Check(pixels[8 + y * 32 + x] == 0xA5);
        for (int x = 0; x < 8; ++x) Check(pixels[x] == 0xA5 && pixels[pixels.size() - 1 - x] == 0xA5);
        const auto before = pixels; world.world_flags = PF_WorldFlag_DEEP;
        Check(effect(PF_Cmd_RENDER, nullptr, nullptr, nullptr, &world, nullptr) != 0 && pixels == before);
        world.world_flags = 0; world.rowbytes = -32;
        Check(effect(PF_Cmd_RENDER, nullptr, nullptr, nullptr, &world, nullptr) != 0 && pixels == before);
        Check(effect(PF_Cmd_SMART_RENDER, nullptr, nullptr, nullptr, &world, nullptr) != 0);
        Check(effect(PF_Cmd_RENDER, nullptr, nullptr, nullptr, nullptr, nullptr) != 0);
        Check(startup(&state) && state.global_setup_calls == 2 && state.parameter_setup_calls == 1 && registrations == 2);
        if (library) {
            std::cout << "FRAME_ARGB8_HEX=";
            for (std::size_t i = 8; i < pixels.size() - 8; ++i)
                std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(pixels[i]);
            std::cout << '\n'; Check(dlclose(library) == 0);
        }
        std::cout << "PASS: real SDK adapter, three startup registration checks, read-only state/refusal checks, synthetic worlds; AE_render=NOT_RUN\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
