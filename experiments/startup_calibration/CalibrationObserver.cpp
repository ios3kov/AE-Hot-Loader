// Separate public-SDK startup calibration. Inert unless explicitly activated.
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "CalibrationCore.hpp"
#include "MarkerIdentity.hpp"
#include "CalibrationConfig.hpp" // Generated only by the offline builder.
#include "../ordinary_discovery/ResourcePassJournal.hpp"
#include "../ordinary_discovery/ResidentImageBinding.hpp"
#include <chrono>
#include <climits>
#include <cstring>
#include <cstdlib>
#include <dlfcn.h>
#include <filesystem>
#include <libproc.h>
#include <mach-o/dyld.h>
#include <pthread.h>
#include <sstream>

extern "C" __attribute__((visibility("default")))
const char* AEHL_CalibrationBuildIdentity() noexcept { return calibration_build; }

namespace {
namespace io = resource_pass::journal_detail;
SPBasicSuite* basic = nullptr;
AEGP_PluginID plugin_id = 0;
startup_calibration::Once once;
bool consumed = false;
bool cleanup_ok = true;
void Require(bool okay) { if (!okay) throw std::runtime_error("calibration refused"); }
std::uint64_t Now() {
    return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch()).count());
}
std::uint64_t Birth() {
    proc_bsdinfo info{};
    Require(proc_pidinfo(getpid(), PROC_PIDTBSDINFO, 0, &info, sizeof(info)) == sizeof(info));
    return info.pbi_start_tvsec * 1000000ULL + info.pbi_start_tvusec;
}
std::string Executable() {
    char value[PATH_MAX]; std::uint32_t size = sizeof(value);
    Require(_NSGetExecutablePath(value, &size) == 0);
    return std::filesystem::canonical(value).string();
}
std::string Module() {
    Dl_info info{};
    Require(dladdr(reinterpret_cast<void*>(&AEHL_CalibrationBuildIdentity), &info) && info.dli_fname);
    return std::filesystem::canonical(info.dli_fname).string();
}
io::Fd Directory() {
    auto dir = io::Directory(calibration_control);
    const auto st = io::Stat(dir.get());
    Require(st.st_uid == geteuid() && (st.st_mode & 07777) == 0700);
    return dir;
}
bool Exists(const char* name) {
    auto dir = Directory(); struct stat st{};
    if (fstatat(dir.get(), name, &st, AT_SYMLINK_NOFOLLOW) == 0) return true;
    Require(errno == ENOENT); return false;
}
void Save(const char* name, const std::string& text) {
    auto dir = Directory();
    io::Fd fd(openat(dir.get(), name, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600));
    Require(fd.get() >= 0 && fchmod(fd.get(), 0600) == 0);
    for (std::size_t offset = 0; offset < text.size();) {
        const auto n = write(fd.get(), text.data() + offset, text.size() - offset);
        if (n < 0 && errno == EINTR) continue;
        Require(n > 0); offset += static_cast<std::size_t>(n);
    }
    Require(fsync(fd.get()) == 0 && fd.close_checked() && fsync(dir.get()) == 0);
}
std::string Read(const char* name) {
    auto dir = Directory();
    io::Fd fd(openat(dir.get(), name, O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC));
    Require(fd.get() >= 0); const auto before = io::Stat(fd.get());
    Require(S_ISREG(before.st_mode) && before.st_uid == geteuid() && before.st_nlink == 1 &&
            (before.st_mode & 07777) == 0600 && before.st_size > 0 && before.st_size <= 512);
    std::string text(static_cast<std::size_t>(before.st_size), '\0');
    for (std::size_t offset = 0; offset < text.size();) {
        const auto n = read(fd.get(), text.data() + offset, text.size() - offset);
        if (n < 0 && errno == EINTR) continue;
        Require(n > 0); offset += static_cast<std::size_t>(n);
    }
    char extra;
    Require(read(fd.get(), &extra, 1) == 0 && io::Same(before, io::Stat(fd.get())));
    return text;
}
template<class T> class Suite {
    const char* name_; A_long version_;
public:
    const T* value = nullptr;
    Suite(const char* name, A_long version) : name_(name), version_(version) {
        Require(basic && basic->AcquireSuite && basic->ReleaseSuite);
        const auto error = basic->AcquireSuite(name_, version_, reinterpret_cast<const void**>(&value));
        if (error || !value) {
            if (value) cleanup_ok = false; // No ownership contract for a failed acquisition.
            value = nullptr; throw std::runtime_error("suite unavailable");
        }
    }
    ~Suite() { if (value && basic->ReleaseSuite(name_, version_)) cleanup_ok = false; }
    Suite(const Suite&) = delete; Suite& operator=(const Suite&) = delete;
};

// Read-only scripting is only a safety check. It is not registry evidence.
constexpr const char* blank_script = R"JS((function () {
    var p = app.project;
    if (app.version !== '25.6x101' || app.buildNumber !== 101 || !p ||
        p.file !== null || p.dirty !== false || p.numItems !== 0 ||
        p.renderQueue.numItems !== 0 ||
        p.renderQueue.rendering !== false || typeof p.revision !== 'number' ||
        p.revision < 1 || Math.floor(p.revision) !== p.revision) return 'REFUSED';
    return 'AEHL-CAL-BLANK-1\n' + p.revision + '\n';
})())JS";

class Backend {
    Suite<AEGP_EffectSuite5> effect_{kAEGPEffectSuite, kAEGPEffectSuiteVersion5};
    Suite<AEGP_CompSuite12> comp_{kAEGPCompSuite, kAEGPCompSuiteVersion12};
    Suite<AEGP_UtilitySuite6> utility_{kAEGPUtilitySuite, kAEGPUtilitySuiteVersion6};
    Suite<AEGP_MemorySuite1> memory_{kAEGPMemorySuite, kAEGPMemorySuiteVersion1};
    Suite<AEGP_ProjSuite6> project_suite_{kAEGPProjSuite, kAEGPProjSuiteVersion6};
    AEGP_ProjectH project_ = nullptr;
    AEGP_ItemH root_ = nullptr;
    AEGP_CompH fixture_ = nullptr;
    AEGP_LayerH layer_ = nullptr;
    AEGP_EffectRefH reference_ = nullptr;
    void GuardProject() {
        const auto* p = project_suite_.value;
        A_long count = 0; AEGP_ProjectH current = nullptr; A_Boolean dirty = TRUE;
        AEGP_ProjBitDepth depth{};
        Require(p->AEGP_GetNumProjects(&count) == 0 && count == 1 &&
            p->AEGP_GetProjectByIndex(0, &current) == 0 && current && (!project_ || current == project_) &&
            p->AEGP_ProjectIsDirty(current, &dirty) == 0 && !dirty &&
            p->AEGP_GetProjectBitDepth(current, &depth) == 0 && depth == AEGP_ProjBitDepth_8);
        project_ = current;
    }
public:
    Backend() {
        const auto* e = effect_.value; const auto* m = memory_.value;
        Require(e->AEGP_GetNumInstalledEffects && e->AEGP_GetNextInstalledEffect &&
            e->AEGP_GetEffectMatchName && e->AEGP_ApplyEffect &&
            e->AEGP_GetInstalledKeyFromLayerEffect && e->AEGP_DisposeEffect && e->AEGP_EffectCallGeneric &&
            comp_.value->AEGP_CreateComp && comp_.value->AEGP_CreateSolidInComp &&
            utility_.value->AEGP_ExecuteScript && utility_.value->AEGP_IsScriptingAvailable &&
            m->AEGP_GetMemHandleSize && m->AEGP_LockMemHandle && m->AEGP_UnlockMemHandle && m->AEGP_FreeMemHandle);
        const auto* p = project_suite_.value;
        Require(p->AEGP_GetNumProjects && p->AEGP_GetProjectByIndex && p->AEGP_ProjectIsDirty &&
            p->AEGP_GetProjectBitDepth && p->AEGP_GetProjectRootFolder);
        std::ostringstream out;
        out << "AEHL-CAL-SUITE-1\nname=" << kAEGPEffectSuite << "\nversion=" << kAEGPEffectSuiteVersion5
            << "\ntable=" << reinterpret_cast<std::uintptr_t>(e)
            << "\ncount=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetNumInstalledEffects)
            << "\nnext=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetNextInstalledEffect)
            << "\nmatch=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetEffectMatchName)
            << "\napply=" << reinterpret_cast<std::uintptr_t>(e->AEGP_ApplyEffect)
            << "\nreverse=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetInstalledKeyFromLayerEffect) << '\n';
        Save("suite", out.str());
    }
    ~Backend() { if (reference_) { auto ref = reference_; reference_ = nullptr;
        if (effect_.value->AEGP_DisposeEffect(ref)) cleanup_ok = false; } }
    bool MainThread() { return pthread_main_np() == 1; }
    std::uint64_t Now() { return ::Now(); }
    bool Consume() { Save("consumed", std::string(calibration_build) + "\n"); return true; }
    std::string Target() { return calibration_match; }
    std::int64_t BlankProjectRevision() {
        GuardProject();
        A_Boolean available = FALSE;
        Require(utility_.value->AEGP_IsScriptingAvailable(&available) == 0 && available);
        struct Handles {
            const AEGP_MemorySuite1* memory; AEGP_MemHandle result = nullptr, error = nullptr;
            ~Handles() { if (result && memory->AEGP_FreeMemHandle(result)) cleanup_ok = false;
                if (error && memory->AEGP_FreeMemHandle(error)) cleanup_ok = false; }
        } handles{memory_.value};
        Require(utility_.value->AEGP_ExecuteScript(plugin_id, blank_script, FALSE,
            &handles.result, &handles.error) == 0 && handles.result);
        AEGP_MemSize size = 0;
        Require(memory_.value->AEGP_GetMemHandleSize(handles.result, &size) == 0 && size > 0 && size <= 128);
        void* ptr = nullptr; Require(memory_.value->AEGP_LockMemHandle(handles.result, &ptr) == 0 && ptr);
        std::string text;
        try { const auto length = strnlen(static_cast<const char*>(ptr), size);
            Require(length < size); text.assign(static_cast<const char*>(ptr), length);
        } catch (...) { if (memory_.value->AEGP_UnlockMemHandle(handles.result)) cleanup_ok = false; throw; }
        Require(memory_.value->AEGP_UnlockMemHandle(handles.result) == 0);
        const std::string prefix = "AEHL-CAL-BLANK-1\n";
        Require(text.rfind(prefix, 0) == 0 && text.back() == '\n');
        const auto number = text.substr(prefix.size(), text.size() - prefix.size() - 1);
        Require(!number.empty() && number.find_first_not_of("0123456789") == number.npos);
        const auto revision = std::stoll(number);
        GuardProject();
        return revision;
    }
    std::int32_t Count() { A_long value = -1;
        Require(effect_.value->AEGP_GetNumInstalledEffects(&value) == 0); return value; }
    std::int32_t Next(std::int32_t cursor) { AEGP_InstalledEffectKey value = 0;
        Require(effect_.value->AEGP_GetNextInstalledEffect(cursor, &value) == 0); return value; }
    std::string Match(std::int32_t key) { char text[AEGP_MAX_EFFECT_MATCH_NAME_SIZE];
        std::memset(text, 0xff, sizeof(text));
        Require(effect_.value->AEGP_GetEffectMatchName(key, text) == 0);
        const auto length = strnlen(text, sizeof(text)); Require(length > 0 && length < sizeof(text));
        return std::string(text, length); }
    bool BeforeMutation() { if (!cleanup_ok) return false;
        GuardProject();
        Require(project_suite_.value->AEGP_GetProjectRootFolder(project_, &root_) == 0 && root_);
        Save("begin", std::string(calibration_build) + "\n"); return true; }
    bool CreateFixture() {
        const A_Ratio aspect{1, 1}, fps{24, 1}; const A_Time duration{1, 1};
        std::vector<A_UTF16Char> name;
        for (const char* p = calibration_fixture; *p; ++p) name.push_back(static_cast<A_UTF16Char>(*p));
        name.push_back(0);
        if (comp_.value->AEGP_CreateComp(root_, name.data(), 64, 48, &aspect, &duration, &fps, &fixture_) || !fixture_) return false;
        const AEGP_ColorVal color{1, 0, 0, 0};
        return comp_.value->AEGP_CreateSolidInComp(name.data(), 64, 48, &color,
                                                 fixture_, &duration, &layer_) == 0 && layer_;
    }
    bool Apply(std::int32_t key) { return effect_.value->AEGP_ApplyEffect(plugin_id, layer_, key, &reference_) == 0 && reference_; }
    bool VerifyBuild() {
        startup_marker::Identity identity; const A_Time time{0, 1};
        if (effect_.value->AEGP_EffectCallGeneric(plugin_id, reference_, &time,
                PF_Cmd_COMPLETELY_GENERAL, &identity) != 0 ||
            strnlen(identity.build, sizeof(identity.build)) == sizeof(identity.build) ||
            std::strcmp(identity.build, calibration_build) != 0 || identity.seed != calibration_seed) return false;
        Save("marker-identity", std::string("AEHL-MARKER-IDENTITY-1\nbuild=") + identity.build +
             "\nseed=" + std::to_string(identity.seed) + "\n"); return true;
    }
    std::int32_t Reverse() { AEGP_InstalledEffectKey value = 0;
        Require(effect_.value->AEGP_GetInstalledKeyFromLayerEffect(reference_, &value) == 0); return value; }
    bool Dispose() { auto ref = reference_; reference_ = nullptr;
        const bool okay = ref && effect_.value->AEGP_DisposeEffect(ref) == 0;
        if (!okay) cleanup_ok = false;
        return okay; }
};

A_Err Idle(AEGP_GlobalRefcon, AEGP_IdleRefcon, A_long*) noexcept {
    if (pthread_main_np() != 1 || consumed) return 0;
    try {
        if (!Exists("request")) return 0;
        consumed = true; // before parsing, acquisition, reentry or any host operation
        startup_calibration::Authorization request;
        std::string schema, ownership, binary, trailing;
        std::istringstream input(Read("request"));
        Require(static_cast<bool>(input >> schema >> request.token >> request.pid >> request.birth >> request.deadline >> ownership >> binary));
        Require(!(input >> trailing) && schema == "AEHL-CAL-REQUEST-1" && ownership == "OWNED-BLANK-PROJECT");
        request.owned_blank_project = true;
        const startup_calibration::Authorization bound{calibration_token, getpid(), Birth(), 0, true};
        Require(request.token == bound.token && request.pid == bound.pid && request.birth == bound.birth &&
                request.deadline > Now() && request.deadline - Now() <= 120 &&
                Module() == calibration_module && Executable() == calibration_executable);
        resident_binding::Digest digest{};
        Require(binary.size() == 64); const std::string digits = "0123456789abcdef";
        for (std::size_t i = 0; i < 32; ++i) {
            const auto a = digits.find(binary[i * 2]), b = digits.find(binary[i * 2 + 1]);
            Require(a < 16 && b < 16); digest[i] = static_cast<unsigned char>(a * 16 + b);
        }
        const auto self = resident_binding::Resolve({calibration_module, digest}, {"_AEHL_CalibrationBuildIdentity"});
        Require(self.functions.at("_AEHL_CalibrationBuildIdentity") == reinterpret_cast<void*>(&AEHL_CalibrationBuildIdentity));
        startup_calibration::Result result;
        { Backend backend; result = once.Run(request, bound, backend); }
        const char* status = result.outcome == startup_calibration::Outcome::ListedApplied && cleanup_ok
            ? "LISTED_APPLIED_FRAME_NOT_RUN" : result.outcome == startup_calibration::Outcome::PartialUnknown ||
              (result.outcome == startup_calibration::Outcome::ListedApplied && !cleanup_ok)
                ? "PARTIAL_UNKNOWN" : "REFUSED";
        Save("result", std::string("AEHL-CAL-RESULT-1\nbuild=") + calibration_build + "\nstatus=" + status +
            "\nstage=" + result.stage + "\nkey=" + std::to_string(result.key) +
            "\ncleanup=" + (cleanup_ok ? "PASS" : "FAIL") + "\nrender=NOT_RUN\n");
    } catch (...) {
        consumed = true;
        try { Save("result", std::string("AEHL-CAL-RESULT-1\nbuild=") + calibration_build +
            "\nstatus=" + (Exists("begin") ? "PARTIAL_UNKNOWN" : "REFUSED") +
            "\ncleanup=" + (cleanup_ok ? "PASS" : "FAIL") + "\nrender=NOT_RUN\n"); } catch (...) {}
    }
    return 0;
}
} // namespace

extern "C" __attribute__((visibility("default")))
A_Err EntryPointFunc(SPBasicSuite* suites, A_long, A_long, AEGP_PluginID id, AEGP_GlobalRefcon*) noexcept {
    try {
        const char* token = std::getenv("AEHL_STARTUP_CALIBRATION_TOKEN");
        if (!suites || !token || std::string(token) != calibration_token || pthread_main_np() != 1 || consumed ||
            Executable() != calibration_executable || Module() != calibration_module)
            return 0;
        if (Exists("ready") || Exists("consumed") || Exists("result") || Exists("begin")) return 0;
        basic = suites; plugin_id = id;
        { Suite<AEGP_RegisterSuite5> registration(kAEGPRegisterSuite, kAEGPRegisterSuiteVersion5);
          Require(registration.value->AEGP_RegisterIdleHook &&
            registration.value->AEGP_RegisterIdleHook(plugin_id, Idle, nullptr) == 0); }
        Require(cleanup_ok);
        Save("ready", std::string("AEHL-CAL-READY-1\nbuild=") + calibration_build + "\npid=" +
             std::to_string(getpid()) + "\nbirth=" + std::to_string(Birth()) + "\n");
    } catch (...) { consumed = true; }
    return 0;
}
