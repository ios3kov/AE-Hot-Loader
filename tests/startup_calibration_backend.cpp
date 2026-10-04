// Compile against the real SDK and actual observer; callbacks below are ours.
// Tests SDK adapter refusal between operations, not behavior inside After Effects.
#include "../experiments/startup_calibration/CalibrationObserver.cpp"
#include <iostream>
#include <thread>

namespace {
int mode = 0, comp_calls = 0, solid_calls = 0;
AEGP_ProjectH current_project = reinterpret_cast<AEGP_ProjectH>(0x1000);
template<class R, class... Args> R Stub(Args...) { return R{}; }
AEGP_EffectSuite5 effects{}; AEGP_CompSuite12 comps{};
AEGP_UtilitySuite6 utilities{}; AEGP_MemorySuite1 memory{}; AEGP_ProjSuite6 projects{};
SPErr Acquire(const char* name, int32, const void** value) {
    if (std::strcmp(name, kAEGPEffectSuite) == 0) *value = &effects;
    else if (std::strcmp(name, kAEGPCompSuite) == 0) *value = &comps;
    else if (std::strcmp(name, kAEGPUtilitySuite) == 0) *value = &utilities;
    else if (std::strcmp(name, kAEGPMemorySuite) == 0) *value = &memory;
    else if (std::strcmp(name, kAEGPProjSuite) == 0) *value = &projects;
    else return 1;
    return 0;
}
void Check(bool okay) { if (!okay) throw std::runtime_error("backend refusal assertion"); }
}
int main(int argc, char** argv) {
    try {
        Check(argc == 2);
        SPBasicSuite provider{}; provider.AcquireSuite = Acquire; provider.ReleaseSuite = Stub;
        basic = &provider;
        effects.AEGP_GetNumInstalledEffects = Stub; effects.AEGP_GetNextInstalledEffect = Stub;
        effects.AEGP_GetEffectMatchName = Stub; effects.AEGP_ApplyEffect = Stub;
        effects.AEGP_GetInstalledKeyFromLayerEffect = Stub; effects.AEGP_DisposeEffect = Stub;
        effects.AEGP_EffectCallGeneric = Stub;
        utilities.AEGP_ExecuteScript = Stub; utilities.AEGP_IsScriptingAvailable = Stub;
        memory.AEGP_GetMemHandleSize = Stub; memory.AEGP_LockMemHandle = Stub;
        memory.AEGP_UnlockMemHandle = Stub; memory.AEGP_FreeMemHandle = Stub;
        projects.AEGP_GetNumProjects = [](A_long* out) -> A_Err { *out = 1; return 0; };
        projects.AEGP_GetProjectByIndex = [](A_long, AEGP_ProjectH* out) -> A_Err { *out = current_project; return 0; };
        projects.AEGP_ProjectIsDirty = [](AEGP_ProjectH, A_Boolean* out) -> A_Err { *out = FALSE; return 0; };
        projects.AEGP_GetProjectBitDepth = [](AEGP_ProjectH, AEGP_ProjBitDepth* out) -> A_Err { *out = AEGP_ProjBitDepth_8; return 0; };
        projects.AEGP_GetProjectRootFolder = [](AEGP_ProjectH, AEGP_ItemH* out) -> A_Err {
            *out = reinterpret_cast<AEGP_ItemH>(0x2000); return 0; };
        comps.AEGP_CreateComp = [](AEGP_ItemH root, const A_UTF16Char*, A_long, A_long,
            const A_Ratio*, const A_Time*, const A_Ratio*, AEGP_CompH* out) -> A_Err {
            Check(root == reinterpret_cast<AEGP_ItemH>(0x2000)); ++comp_calls;
            *out = reinterpret_cast<AEGP_CompH>(0x3000);
            if (mode == 1) current_project = reinterpret_cast<AEGP_ProjectH>(0x4000);
            if (mode == 2) std::this_thread::sleep_for(std::chrono::seconds(4));
            return 0;
        };
        comps.AEGP_CreateSolidInComp = [](const A_UTF16Char*, A_long, A_long, const AEGP_ColorVal*,
            AEGP_CompH, const A_Time*, AEGP_LayerH* out) -> A_Err {
            ++solid_calls; *out = reinterpret_cast<AEGP_LayerH>(0x5000); return 0; };
        const std::string base = std::filesystem::canonical(argv[1]).string();
        for (mode = 0; mode < 4; ++mode) {
            const auto path = base + "/case-" + std::to_string(mode);
            Check(std::filesystem::create_directory(path)); Check(chmod(path.c_str(), 0700) == 0);
            calibration_control = path.c_str(); // test-only generated config has a mutable path pointer
            current_project = reinterpret_cast<AEGP_ProjectH>(0x1000); comp_calls = solid_calls = 0;
            { Backend backend(::Now() + (mode == 2 ? 3 : 120)); Check(backend.BeforeMutation());
              if (mode == 3) current_project = reinterpret_cast<AEGP_ProjectH>(0x4000);
              Check(backend.CreateFixture() == (mode == 0)); }
            Check(comp_calls == (mode == 3 ? 0 : 1) && solid_calls == (mode == 0 ? 1 : 0));
            Check(cleanup_ok);
        }
        std::cout << "PASS: 4 SDK-backend cases; changed-project/deadline refuse later mutation; Adobe_calls=0\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
