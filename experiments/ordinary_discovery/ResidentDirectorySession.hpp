// Research-only one-shot resident reference retention. NOT an AEGP entrypoint.
// Call only AFTER the separately authorized/supervised probe has durably claimed
// its run and checked the live host/project/root. A bool is not consent evidence.
// No dlsym, RTLD_NODELETE, new-image load, startup replay or Adobe call occurs here.
#pragma once
#include "NativeDirectoryBinding.hpp"
#include "AE256DirectoryProfile.hpp"
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <crt_externs.h>
#include <dlfcn.h>
#include <unistd.h>
namespace native_directory {
inline Profile ReviewedAE256Profile() {
    return {ae256_directory::kFrameworks, ae256_directory::kFile,
            ae256_directory::kUtility, ae256_directory::kCore};
}
namespace retention_detail {
struct State {
    pid_t pid = ::getpid();
    bool attempted = false;
    unsigned count = 0;
    std::array<void*, 3> handles{};
    // Intentionally NO dlclose/destructor: at most three references live until
    // process exit, including partial failure. Releasing the last reference could
    // unload host code. This bounded retention is part of future required consent.
};
inline State& Get() { static State state; return state; }
inline bool CleanLoaderEnvironment() {
    char** env = *_NSGetEnviron();
    if (!env) return false;
    for (std::size_t i = 0; env[i]; ++i) {
        if (i == 8192) return false;
        const char* entry = env[i];
        if (std::strncmp(entry, "DYLD_", 5) == 0 ||
            std::strncmp(entry, "LD_LIBRARY_PATH=", 16) == 0) return false;
    }
    return true;
}
} // namespace retention_detail
inline unsigned RetainedDirectoryReferences() {
    resident_binding::Require(pthread_main_np() == 1);
    auto& state = retention_detail::Get();
    resident_binding::Require(state.pid == ::getpid());
    return state.count;
}
inline directory_spec::Functions BindRetainedOnce(const Profile& supplied,
                                                 bool retention_authorized = false) {
    using namespace resident_binding;
    const Profile profile = supplied;
    Require(pthread_main_np() == 1 && retention_authorized);
    auto& state = retention_detail::Get();
    Require(state.pid == ::getpid() && !state.attempted);
    Require(retention_detail::CleanLoaderEnvironment());
    // First validate the exact resident exports/file bytes before changing any
    // loader reference count. Resolve refuses an absent image without loading it.
    const auto before = Snapshot();
    (void)Bind(profile);
    Require(before == Snapshot());
    const std::array<std::string, 3> paths{
        profile.frameworks + "/FILE.dylib", profile.frameworks + "/U.dylib",
        profile.frameworks + "/dvacore.framework/Versions/A/dvacore"};
    state.attempted = true; // consume before first reference change; never retry
    for (std::size_t i = 0; i < paths.size(); ++i) {
        void* handle = ::dlopen(paths[i].c_str(), RTLD_NOLOAD | RTLD_LAZY | RTLD_LOCAL);
        Require(handle != nullptr);
        state.handles[i] = handle; // store immediately; no allocation/exception here
        ++state.count;
        Require(before == Snapshot());
    }
    // Bind AGAIN under the retained references. Never expose the pre-retention
    // pointers if removal/replacement occurred during acquisition.
    auto result = Bind(profile);
    Require(before == Snapshot() && state.count == 3);
    return result;
    // Protects lifetime under the public dyld reference-count contract, assuming
    // stable loader configuration and no hostile loader interposition. Snapshots
    // do not lock unrelated images or certify thread safety of an Adobe function.
}
} // namespace native_directory
#endif
