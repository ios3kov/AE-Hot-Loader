// Uses real supplied SDK declarations; synthetic worlds are NOT an AE render.
#include "AEConfig.h"
#include "AE_Effect.h"
#include "../experiments/startup_calibration/MarkerIdentity.hpp"
#include <cstring>
#include <dlfcn.h>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>
extern "C" PF_Err EffectMain(PF_Cmd, PF_InData*, PF_OutData*, PF_ParamDef*[], PF_LayerDef*, void*) noexcept;
void Check(bool value) { if (!value) throw std::runtime_error("adapter assertion"); }
int main(int argc, char** argv) {
    try {
        auto effect = &EffectMain;
        void* library = nullptr;
        if (argc == 3) {
            library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); Check(library);
            effect = reinterpret_cast<decltype(effect)>(dlsym(library, "EffectMain")); Check(effect);
            using Identity = const char* (*)();
            auto identity = reinterpret_cast<Identity>(dlsym(library, "AEHL_MarkerBuildIdentity"));
            Check(identity && std::strcmp(identity(), argv[2]) == 0);
        } else Check(argc == 1);
        PF_OutData out{};
        Check(effect(PF_Cmd_GLOBAL_SETUP, nullptr, &out, nullptr, nullptr, nullptr) == 0);
        Check(out.my_version == 0x8001 && !out.out_flags && !out.out_flags2);
        Check(effect(PF_Cmd_PARAMS_SETUP, nullptr, &out, nullptr, nullptr, nullptr) == 0 && out.num_params == 1);
        Check(effect(PF_Cmd_GLOBAL_SETUP, nullptr, nullptr, nullptr, nullptr, nullptr) != 0);
        startup_marker::Identity identity;
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, &identity) == 0);
        Check(std::strcmp(identity.build, argc == 3 ? argv[2] : "offline-test-only") == 0);
        identity.version = 2;
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, &identity) != 0);
        identity.version = 1; identity.magic = 0;
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, &identity) != 0);
        Check(effect(PF_Cmd_COMPLETELY_GENERAL, nullptr, nullptr, nullptr, nullptr, nullptr) != 0);
        std::vector<unsigned char> pixels(32 * 3 + 16, 0xA5); PF_LayerDef world{};
        world.data = reinterpret_cast<PF_PixelPtr>(pixels.data() + 8);
        world.width = 5; world.height = 3; world.rowbytes = 32;
        Check(effect(PF_Cmd_RENDER, nullptr, nullptr, nullptr, &world, nullptr) == 0);
        for (int y = 0; y < 3; ++y) for (int x = 20; x < 32; ++x) Check(pixels[8 + y * 32 + x] == 0xA5);
        for (int x = 0; x < 8; ++x) Check(pixels[x] == 0xA5 && pixels[pixels.size() - 1 - x] == 0xA5);
        const auto before = pixels; world.world_flags = PF_WorldFlag_DEEP;
        Check(effect(PF_Cmd_RENDER, nullptr, nullptr, nullptr, &world, nullptr) != 0 && pixels == before);
        world.world_flags = 0; world.rowbytes = -32;
        Check(effect(PF_Cmd_RENDER, nullptr, nullptr, nullptr, &world, nullptr) != 0 && pixels == before);
        Check(effect(PF_Cmd_SMART_RENDER, nullptr, nullptr, nullptr, &world, nullptr) != 0);
        Check(effect(PF_Cmd_RENDER, nullptr, nullptr, nullptr, nullptr, nullptr) != 0);
        if (library) {
            std::cout << "FRAME_ARGB8_HEX=";
            for (std::size_t i = 8; i < pixels.size() - 8; ++i)
                std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(pixels[i]);
            std::cout << '\n'; Check(dlclose(library) == 0);
        }
        std::cout << "PASS: real SDK adapter, synthetic worlds; AE_render=NOT_RUN\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
