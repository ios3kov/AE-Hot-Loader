// Compile against the real SDK and actual observer; callbacks below are ours.
// Tests SDK adapter refusal between operations, not behavior inside After Effects.
#include "../experiments/startup_calibration/CalibrationObserver.cpp"
#include <iostream>
#include <thread>

namespace {
int mode = 0, comp_calls = 0, solid_calls = 0, depth_calls = 0;
AEGP_ProjBitDepth current_depth = AEGP_ProjBitDepth_8;
AEGP_ProjectH current_project = reinterpret_cast<AEGP_ProjectH>(0x1000);
std::string script_response = "AEHL-CAL-COLOR-1\n";
template<class R, class... Args> R Stub(Args...) { return R{}; }
AEGP_EffectSuite5 effects{}; AEGP_CompSuite12 comps{};
AEGP_UtilitySuite6 utilities{}; AEGP_MemorySuite1 memory{}; AEGP_ProjSuite6 projects{};
AEGP_ColorSettingsSuite6 colors{};
SPErr Acquire(const char* name, int32 version, const void** value) {
    if (std::strcmp(name, kAEGPEffectSuite) == 0) *value = &effects;
    else if (std::strcmp(name, kAEGPCompSuite) == 0) *value = &comps;
    else if (std::strcmp(name, kAEGPUtilitySuite) == 0) *value = &utilities;
    else if (std::strcmp(name, kAEGPMemorySuite) == 0) *value = &memory;
    else if (std::strcmp(name, kAEGPProjSuite) == 0) *value = &projects;
    else if (std::strcmp(name, kAEGPColorSettingsSuite) == 0) {
        if (version!=7 || version!=kAEGPColorSettingsSuiteVersion6) return 1;
        *value=&colors;
    }
    else return 1;
    return 0;
}
void Check(bool okay) { if (!okay) throw std::runtime_error("backend refusal assertion"); }
}
int main(int argc, char** argv) {
    try {
        Check(argc == 2);
        for (const auto* category : {"null", "undefined", "empty", "none-token", "other-string", "other"}) {
            const auto fixed=std::string("AEHL-CAL-COLOR-FACTS-1\nstage=final\nreason=working-space-mismatch\nvalue=")+category+"\n";
            Check(startup_color::Diagnostic(fixed)==fixed);
            Check(startup_color::Diagnostic(fixed+"private-profile-name") == startup_color::Diagnostic("invalid"));
        }
        SPBasicSuite provider{}; provider.AcquireSuite = Acquire; provider.ReleaseSuite = Stub;
        basic = &provider;
        effects.AEGP_GetNumInstalledEffects = Stub; effects.AEGP_GetNextInstalledEffect = Stub;
        effects.AEGP_GetEffectMatchName = Stub; effects.AEGP_GetEffectName = Stub; effects.AEGP_ApplyEffect = Stub;
        effects.AEGP_GetInstalledKeyFromLayerEffect = Stub; effects.AEGP_DisposeEffect = Stub;
        effects.AEGP_EffectCallGeneric = Stub;
        effects.AEGP_GetLayerNumEffects = Stub; effects.AEGP_GetLayerEffectByIndex = Stub;
        utilities.AEGP_ExecuteScript = [](AEGP_PluginID, const A_char* script, A_Boolean, AEGP_MemHandle* result, AEGP_MemHandle*) -> A_Err {
            Check(std::strstr(script,"p.workingSpace=''") != nullptr);
            if (mode == 6) return 1;
            *result=reinterpret_cast<AEGP_MemHandle>(0x6000); return 0;
        };
        utilities.AEGP_IsScriptingAvailable = [](A_Boolean* value)->A_Err { *value=mode==10?FALSE:TRUE;return 0; };
        colors.AEGP_IsOCIOColorManagementUsed = [](AEGP_PluginID, A_Boolean* value)->A_Err {
            *value=mode==11?TRUE:FALSE;return mode==12?1:0;
        };
        memory.AEGP_GetMemHandleSize = [](AEGP_MemHandle, AEGP_MemSize* size)->A_Err {
            *size=script_response.size()+1;return 0; };
        memory.AEGP_LockMemHandle = [](AEGP_MemHandle, void** data)->A_Err {
            *data=const_cast<char*>(script_response.c_str());return 0; };
        memory.AEGP_UnlockMemHandle = Stub; memory.AEGP_FreeMemHandle = Stub;
        projects.AEGP_GetNumProjects = [](A_long* out) -> A_Err { *out = 1; return 0; };
        projects.AEGP_GetProjectByIndex = [](A_long, AEGP_ProjectH* out) -> A_Err { *out = current_project; return 0; };
        projects.AEGP_ProjectIsDirty = [](AEGP_ProjectH, A_Boolean* out) -> A_Err { *out = FALSE; return 0; };
        projects.AEGP_GetProjectBitDepth = [](AEGP_ProjectH, AEGP_ProjBitDepth* out) -> A_Err { *out = current_depth; return 0; };
        projects.AEGP_SetProjectBitDepth = [](AEGP_ProjectH p, AEGP_ProjBitDepth depth) -> A_Err {
            Check(p == current_project && depth == AEGP_ProjBitDepth_8); ++depth_calls;
            if (mode == 5) return 1;
            current_depth = depth; return 0;
        };
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
        for (mode = 0; mode < 13; ++mode) {
            const auto path = base + "/case-" + std::to_string(mode);
            Check(std::filesystem::create_directory(path)); Check(chmod(path.c_str(), 0700) == 0);
            calibration_control = path.c_str(); // test-only generated config has a mutable path pointer
            current_project = reinterpret_cast<AEGP_ProjectH>(0x1000); comp_calls = solid_calls = depth_calls = 0;
            current_depth = mode >= 4 ? AEGP_ProjBitDepth_32 : AEGP_ProjBitDepth_8;
            script_response = mode==7 ? "AEHL-CAL-COLOR-DIAG-1\nstage=final\nreason=linearize-mismatch\n" :
                mode==8 ? "must-not-persist-private-error" :
                mode==9 ? "AEHL-CAL-COLOR-DIAG-1\nstage=working-space\nreason=project-changed\n" : "AEHL-CAL-COLOR-1\n";
            { Backend backend(::Now() + (mode == 2 ? 3 : 120)); Check(backend.BeforeMutation());
              if (mode == 3) current_project = reinterpret_cast<AEGP_ProjectH>(0x4000);
              bool failed=false;
              try { Check(backend.CreateFixture() == (mode == 0 || mode == 4)); }
              catch (...) { Check(mode==6 || mode==10);failed=true; }
              Check(failed==(mode==6 || mode==10)); }
            Check(comp_calls == (mode == 3 || mode == 5 || mode >= 6 ? 0 : 1) && solid_calls == (mode == 0 || mode == 4 ? 1 : 0));
            Check(depth_calls == (mode >= 4 && mode<11 ? 1 : 0));
            Check(current_depth == (mode == 5 || mode>=11 ? AEGP_ProjBitDepth_32 : AEGP_ProjBitDepth_8));
            Check(cleanup_ok);
            if (mode>=6 && mode<11) {
                const auto data=Read("color-diagnostic");
                const auto expected=(mode==6 || mode==10) ? startup_color::SDKFailure(mode==6?"script-execution":"scripting-available") : startup_color::Diagnostic(script_response);
                Check(data==expected && data.find("must-not-persist-private-error")==std::string::npos);
            }
            if (mode>=11) Check(!Exists("color-started") && !Exists("color-diagnostic") && !Exists("color-engine"));
        }
        std::cout << "PASS:13 SDK-backend cases; project/deadline/color refusals stop later mutation; fixed diagnostics only; Adobe_calls=0\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
