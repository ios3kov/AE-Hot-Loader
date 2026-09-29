// Research AEGP; activated only in the pinned owned host with its build token.
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "ScopedDiscoveryGate.hpp"
#include "ScopedDiscoveryConfig.hpp"
#include <climits>
#include <cstring>
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <pthread.h>

extern "C" int AEHotLoader_LoadPluginFolder(const char*);

namespace {
SPBasicSuite* basic = nullptr;
AEGP_PluginID plugin_id = 0;
bool consumed = false;
void ImageMarker() {}

template<class T> struct Suite {
    SPBasicSuite* provider;
    const char* name;
    A_long version;
    const T* value = nullptr;
    Suite(SPBasicSuite* p, const char* n, A_long v) : provider(p), name(n), version(v) {
        scoped::Require(provider->AcquireSuite(name, version,
            reinterpret_cast<const void**>(&value)) == 0 && value, "SDK suite unavailable");
    }
    ~Suite() { if (value) provider->ReleaseSuite(name, version); }
    Suite(const Suite&) = delete;
    Suite& operator=(const Suite&) = delete;
};
struct Handles {
    const AEGP_MemorySuite1* memory;
    AEGP_MemHandle result = nullptr, error = nullptr;
    ~Handles() {
        if (result) memory->AEGP_FreeMemHandle(result);
        if (error) memory->AEGP_FreeMemHandle(error);
    }
};

// The script reads registry/project state only. URI-encoding keeps each effect
// identity on one line; no project names or paths enter the evidence.
constexpr const char* snapshot_script = R"JS((function () {
    var p = app.project;
    if (app.version !== '25.6x101' || app.buildNumber !== 101 || !p ||
        p.file !== null || p.dirty !== false || p.numItems !== 0 ||
        p.renderQueue.numItems !== 0 || p.renderQueue.rendering !== false ||
        typeof p.revision !== 'number' || p.revision < 1 ||
        Math.floor(p.revision) !== p.revision) return 'BLOCKED';
    var names = [], effects = app.effects;
    for (var i = 0; i < effects.length; i++) {
        if (typeof effects[i].matchName !== 'string' || !effects[i].matchName) return 'BLOCKED';
        names.push(encodeURIComponent(effects[i].matchName));
    }
    names.sort();
    return 'AEHL-SNAPSHOT-1\n' + p.revision + '\n' + names.join('\n') + '\n';
})())JS";

std::string Snapshot() {
    Suite<AEGP_UtilitySuite6> utility(basic, kAEGPUtilitySuite, kAEGPUtilitySuiteVersion6);
    Suite<AEGP_MemorySuite1> memory(basic, kAEGPMemorySuite, kAEGPMemorySuiteVersion1);
    Handles handles{memory.value};
    A_Boolean available = FALSE;
    scoped::Require(utility.value->AEGP_IsScriptingAvailable(&available) == 0 && available,
                    "scripting unavailable");
    const auto err = utility.value->AEGP_ExecuteScript(plugin_id, snapshot_script, FALSE,
                                                      &handles.result, &handles.error);
    scoped::Require(err == 0 && handles.result, "host snapshot failed");
    AEGP_MemSize size = 0;
    scoped::Require(memory.value->AEGP_GetMemHandleSize(handles.result, &size) == 0 &&
                    size > 0 && size <= 1024 * 1024, "invalid snapshot handle size");
    void* ptr = nullptr;
    scoped::Require(memory.value->AEGP_LockMemHandle(handles.result, &ptr) == 0 && ptr,
                    "snapshot lock failed");
    std::string text;
    try {
        const auto length = strnlen(static_cast<const char*>(ptr), size);
        scoped::Require(length < size, "snapshot missing terminator");
        text.assign(static_cast<const char*>(ptr), length);
    } catch (...) {
        memory.value->AEGP_UnlockMemHandle(handles.result);
        throw;
    }
    scoped::Require(memory.value->AEGP_UnlockMemHandle(handles.result) == 0,
                    "snapshot unlock failed");
    return text;
}
std::string Executable() {
    char path[PATH_MAX];
    std::uint32_t size = sizeof(path);
    scoped::Require(_NSGetExecutablePath(path, &size) == 0, "host path unavailable");
    return scoped::fs::canonical(path).string();
}
std::string Token() {
    const char* value = std::getenv("AEHL_SCOPED_GATE_TOKEN");
    return value ? value : "";
}
A_Err Idle(AEGP_GlobalRefcon, AEGP_IdleRefcon, A_long* max_sleep) {
    if (consumed) return 0;
    if (max_sleep && *max_sleep > 15) *max_sleep = 15;
    try {
        scoped::Require(pthread_main_np(), "idle callback off main thread");
        const auto& c = research_config;
        scoped::OwnedEvidence(c.evidence);
        const auto request = scoped::fs::path(c.evidence) / "request.txt";
        if (!scoped::fs::exists(scoped::fs::symlink_status(request))) return 0;
        consumed = true;
        scoped::Run(c, scoped::Read(request, 1024), getpid(), Executable(), Token(),
                    Snapshot, AEHotLoader_LoadPluginFolder);
    } catch (...) {
        consumed = true;
        // Never show a modal dialog or retry a failed native operation.
        try { scoped::Save(research_config, "adapter-stopped.txt", "status=FAIL\n"); }
        catch (...) {}
    }
    return 0;
}
} // namespace

extern "C" __attribute__((visibility("default")))
const char* AEHL_ScopedBuildIdentity() { return research_identity; }

extern "C" __attribute__((visibility("default")))
A_Err EntryPointFunc(SPBasicSuite* suites, A_long, A_long, AEGP_PluginID id,
                     AEGP_GlobalRefcon*) {
    try {
        if (!suites || Token() != research_config.token ||
            Executable() != research_config.host_executable) return 0;
        scoped::NoLinks(research_config.host_executable);
        scoped::OwnedEvidence(research_config.evidence);
        if (scoped::fs::exists(scoped::fs::path(research_config.evidence) / "claim.txt")) return 0;
        basic = suites;
        plugin_id = id;
        Suite<AEGP_RegisterSuite5> registration(basic, kAEGPRegisterSuite, kAEGPRegisterSuiteVersion5);
        scoped::Require(registration.value->AEGP_RegisterIdleHook(id, Idle, nullptr) == 0,
                        "idle hook registration failed");
        Dl_info image{};
        scoped::Require(dladdr(reinterpret_cast<const void*>(&ImageMarker), &image) &&
                        image.dli_fname, "research image identity unavailable");
        scoped::Save(research_config, "ready.txt", std::string(research_identity) +
                     "\npid=" + std::to_string(getpid()) + "\nimage=" + image.dli_fname + "\n");
    } catch (...) { consumed = true; return 1; }
    return 0;
}
