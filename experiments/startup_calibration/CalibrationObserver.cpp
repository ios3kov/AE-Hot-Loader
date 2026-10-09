// Separate public-SDK startup calibration. Inert unless explicitly activated.
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "CalibrationCore.hpp"
#include "MarkerIdentity.hpp"
#include "MarkerStartupState.hpp"
#include "NameProjection.hpp"
#include "ColorPreparation.hpp"
#include "AsyncFrameCapture.hpp"
#include "QueueControl.hpp"
#include "ImageProvenance.hpp"
#include <memory>
#include "CalibrationConfig.hpp" // Generated only by the offline builder.
#include "../ordinary_discovery/ResourcePassJournal.hpp"
#include "../ordinary_discovery/ResidentImageBinding.hpp"
#include <chrono>
#include <cstdint>
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

#ifdef AEHL_TRACE_IDENTITY
extern "C" __attribute__((visibility("default"), noinline))
void AEHL_TraceReaderBoundary(unsigned stage, AEGP_InstalledEffectKey key,
    std::uintptr_t function, unsigned status, unsigned main_thread) noexcept {
    asm volatile("" : : "r"(stage), "r"(key), "r"(function), "r"(status), "r"(main_thread) : "memory");
}
#endif

namespace {
namespace io = resource_pass::journal_detail;
SPBasicSuite* basic = nullptr;
AEGP_PluginID plugin_id = 0;
startup_calibration::Once once;
bool consumed = false;
bool idle_active = false;
bool cleanup_ok = true;
bool queue_control = false; // Explicit separate request; never an async fallback.
bool registry_observation = false; // Read-only; cannot fall through to Apply/frame.
const char* diagnostic_stage = "authorization";
const char* diagnostic_suite = nullptr;
A_long diagnostic_suite_version = 0;
SPErr diagnostic_host_error = 0;
bool diagnostic_host_error_known = false;
void DiagnosticStage(const char* stage) noexcept {
    diagnostic_stage = stage;
    diagnostic_suite = nullptr; diagnostic_suite_version = 0;
    diagnostic_host_error_known = false;
}
void Require(bool okay) { if (!okay) throw std::runtime_error("calibration refused"); }
std::uint64_t Now() {
    return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch()).count());
}
std::uint64_t MonotonicMillis() {
    return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count());
}
std::string Hex(const std::string& text) {
    constexpr char digits[] = "0123456789abcdef";
    std::string result; result.reserve(text.size() * 2);
    for (unsigned char c : text) { result.push_back(digits[c >> 4]); result.push_back(digits[c & 15]); }
    return result;
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
// Optional fixed metadata. Failure cannot change the SDK operation's result.
void DescribeProvider(const char* leaf, std::uintptr_t address) noexcept {
    try {
        const auto image = startup_image::Inspect(address, [](std::uintptr_t pointer, startup_image::Facts& facts) {
            Dl_info info{};
            if (!dladdr(reinterpret_cast<void*>(pointer), &info)) return false;
            facts.path = info.dli_fname;
            facts.base = reinterpret_cast<std::uintptr_t>(info.dli_fbase);
            return true;
        });
        Save(leaf, std::string("AEHL-CAL-PROVIDER-1\nbuild=") + calibration_build +
            "\npid=" + std::to_string(getpid()) + "\nbirth=" + std::to_string(Birth()) +
            "\nstatus=" + (image.known ? "IMAGE_DESCRIBED" : "UNKNOWN") +
            "\naddress=" + std::to_string(address) + "\nbase=" + std::to_string(image.base) +
            "\noffset=" + std::to_string(image.offset) + "\npath_hex=" + image.path_hex +
            "\nownership=NOT_ACQUIRED\n");
    } catch (...) {}
}
// Fixed own startup facts only; diagnostics cannot change registration outcome.
void StartupStage(unsigned stage) noexcept {
    static constexpr const char* leaves[] = {
        "startup-entry", "startup-acquire-before", "startup-acquire-after",
        "startup-register-before", "startup-register-after", "startup-release-after",
        "startup-ready-before", "startup-ready-after"};
    if (stage >= sizeof(leaves) / sizeof(leaves[0])) return;
    try {
        const auto wall = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        Save(leaves[stage], std::string("AEHL-CAL-STARTUP-STAGE-1\nbuild=") + calibration_build +
            "\npid=" + std::to_string(getpid()) + "\nbirth=" + std::to_string(Birth()) +
            "\nstage=" + std::to_string(stage) + "\nwall_ms=" + std::to_string(wall) +
            "\nmonotonic_ms=" + std::to_string(MonotonicMillis()) + "\n");
    } catch (...) { /* A missing stage remains unknown, never acceptance. */ }
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
        DiagnosticStage("sdk-suite-acquire");
        diagnostic_suite = name_; diagnostic_suite_version = version_;
        Require(basic && basic->AcquireSuite && basic->ReleaseSuite);
        const auto error = basic->AcquireSuite(name_, version_, reinterpret_cast<const void**>(&value));
        diagnostic_host_error = error; diagnostic_host_error_known = true;
        if (error || !value) {
            diagnostic_stage = error ? "sdk-suite-acquire" : "sdk-suite-empty";
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
    if (!/^25\.6(?:\.0)?x101$/.test(app.version) || app.buildNumber !== 101) return 'REFUSED:host-version';
    if (!p || p.file !== null) return 'REFUSED:unsaved-project';
    if (p.dirty !== false || p.numItems !== 0) return 'REFUSED:blank-project';
    if (p.renderQueue.numItems !== 0 || p.renderQueue.rendering !== false) return 'REFUSED:render-queue';
    if (typeof p.workingSpace !== 'string' || typeof p.linearBlending !== 'boolean' ||
        typeof p.linearizeWorkingSpace !== 'boolean') return 'REFUSED:color-route';
    if (typeof p.revision !== 'number' || p.revision < 1 || Math.floor(p.revision) !== p.revision)
        return 'REFUSED:revision';
    return 'AEHL-CAL-BLANK-1\n' + p.revision + '\n';
})())JS";

class Backend {
    static std::chrono::seconds Budget(std::uint64_t deadline) {
        const auto now=::Now(); return std::chrono::seconds(deadline>now ?
            std::min<std::uint64_t>(deadline-now,120) : 0);
    }
    const std::uint64_t deadline_;
    const std::chrono::steady_clock::time_point monotonic_stop_;
    Suite<AEGP_EffectSuite5> effect_{kAEGPEffectSuite, kAEGPEffectSuiteVersion5};
    Suite<AEGP_CompSuite12> comp_{kAEGPCompSuite, kAEGPCompSuiteVersion12};
    Suite<AEGP_UtilitySuite6> utility_{kAEGPUtilitySuite, kAEGPUtilitySuiteVersion6};
    Suite<AEGP_MemorySuite1> memory_{kAEGPMemorySuite, kAEGPMemorySuiteVersion1};
    Suite<AEGP_ProjSuite6> project_suite_{kAEGPProjSuite, kAEGPProjSuiteVersion6};
    Suite<AEGP_ColorSettingsSuite6> color_suite_{kAEGPColorSettingsSuite, kAEGPColorSettingsSuiteVersion6};
    AEGP_ProjectH project_ = nullptr;
    AEGP_ItemH root_ = nullptr;
    AEGP_CompH fixture_ = nullptr;
    AEGP_LayerH layer_ = nullptr;
    AEGP_EffectRefH reference_ = nullptr;
    std::string queue_snapshot_; // Exact post-render revision; user edits revoke shutdown proof.
    bool SameProject() {
        if (pthread_main_np() != 1) return false;
        A_long count = 0; AEGP_ProjectH current = nullptr;
        return project_suite_.value->AEGP_GetNumProjects(&count) == 0 && count == 1 &&
            project_suite_.value->AEGP_GetProjectByIndex(0, &current) == 0 && current == project_;
    }
    bool OperationAllowed() { return std::chrono::steady_clock::now() < monotonic_stop_ &&
        Now() < deadline_ && SameProject() && Now() < deadline_; }
    bool NonOCIO() {
        A_Boolean ocio=TRUE;
        return OperationAllowed() && color_suite_.value->AEGP_IsOCIOColorManagementUsed(plugin_id,&ocio)==0 &&
            ocio==FALSE && OperationAllowed();
    }
    void GuardProject() {
        const auto* p = project_suite_.value;
        A_long count = 0; AEGP_ProjectH current = nullptr; A_Boolean dirty = TRUE;
        AEGP_ProjBitDepth depth{};
        diagnostic_stage="native-project-count";
        Require(p->AEGP_GetNumProjects(&count) == 0 && count == 1);
        diagnostic_stage="native-project-handle";
        Require(p->AEGP_GetProjectByIndex(0, &current) == 0 && current && (!project_ || current == project_));
        diagnostic_stage="native-project-clean";
        Require(p->AEGP_ProjectIsDirty(current, &dirty) == 0 && !dirty);
        diagnostic_stage="native-project-depth-valid";
        Require(p->AEGP_GetProjectBitDepth(current, &depth) == 0 &&
            (depth == AEGP_ProjBitDepth_8 || depth == AEGP_ProjBitDepth_16 || depth == AEGP_ProjBitDepth_32));
        project_ = current;
    }
public:
    explicit Backend(std::uint64_t deadline) : deadline_(deadline), monotonic_stop_(
        std::chrono::steady_clock::now()+Budget(deadline)) {
        DiagnosticStage("backend-function-table");
        const auto* e = effect_.value; const auto* m = memory_.value;
        Require(e->AEGP_GetNumInstalledEffects && e->AEGP_GetNextInstalledEffect &&
            e->AEGP_GetEffectMatchName && e->AEGP_GetEffectName && e->AEGP_ApplyEffect &&
            e->AEGP_GetInstalledKeyFromLayerEffect && e->AEGP_DisposeEffect && e->AEGP_EffectCallGeneric &&
            e->AEGP_GetLayerEffectByIndex && e->AEGP_GetLayerNumEffects &&
            comp_.value->AEGP_CreateComp && comp_.value->AEGP_CreateSolidInComp &&
            utility_.value->AEGP_ExecuteScript && utility_.value->AEGP_IsScriptingAvailable &&
            m->AEGP_GetMemHandleSize && m->AEGP_LockMemHandle && m->AEGP_UnlockMemHandle && m->AEGP_FreeMemHandle);
        const auto* p = project_suite_.value;
        DiagnosticStage("backend-project-table");
        Require(p->AEGP_GetNumProjects && p->AEGP_GetProjectByIndex && p->AEGP_ProjectIsDirty &&
            p->AEGP_GetProjectBitDepth && p->AEGP_SetProjectBitDepth && p->AEGP_GetProjectRootFolder);
        DiagnosticStage("backend-color-table");
        Require(color_suite_.value->AEGP_IsOCIOColorManagementUsed);
        std::ostringstream out;
        out << "AEHL-CAL-SUITE-1\nname=" << kAEGPEffectSuite << "\nversion=" << kAEGPEffectSuiteVersion5
            << "\ntable=" << reinterpret_cast<std::uintptr_t>(e)
            << "\ncount=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetNumInstalledEffects)
            << "\nnext=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetNextInstalledEffect)
            << "\nmatch=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetEffectMatchName)
            << "\nname_slot=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetEffectName)
            << "\napply=" << reinterpret_cast<std::uintptr_t>(e->AEGP_ApplyEffect)
            << "\nreverse=" << reinterpret_cast<std::uintptr_t>(e->AEGP_GetInstalledKeyFromLayerEffect) << '\n';
        DiagnosticStage("backend-suite-journal");
        Save("suite", out.str());
        DescribeProvider("provider-count", reinterpret_cast<std::uintptr_t>(e->AEGP_GetNumInstalledEffects));
        DescribeProvider("provider-next", reinterpret_cast<std::uintptr_t>(e->AEGP_GetNextInstalledEffect));
        DescribeProvider("provider-match", reinterpret_cast<std::uintptr_t>(e->AEGP_GetEffectMatchName));
        DescribeProvider("provider-name", reinterpret_cast<std::uintptr_t>(e->AEGP_GetEffectName));
        DescribeProvider("provider-apply", reinterpret_cast<std::uintptr_t>(e->AEGP_ApplyEffect));
        DescribeProvider("provider-reverse", reinterpret_cast<std::uintptr_t>(e->AEGP_GetInstalledKeyFromLayerEffect));
    }
    ~Backend() { if (reference_) { auto ref = reference_; reference_ = nullptr;
        if (effect_.value->AEGP_DisposeEffect(ref)) cleanup_ok = false; } }
    bool MainThread() { return pthread_main_np() == 1; }
    std::uint64_t Now() { return ::Now(); }
    bool Consume() { Save("consumed", std::string(calibration_build) + "\n"); return true; }
    std::string Target() { return calibration_match; }
    std::string Script(const std::string& program) {
        diagnostic_stage="scripting-available";
        A_Boolean available = FALSE;
        Require(utility_.value->AEGP_IsScriptingAvailable(&available) == 0 && available);
        struct Handles {
            const AEGP_MemorySuite1* memory; AEGP_MemHandle result = nullptr, error = nullptr;
            ~Handles() { if (result && memory->AEGP_FreeMemHandle(result)) cleanup_ok = false;
                if (error && memory->AEGP_FreeMemHandle(error)) cleanup_ok = false; }
        } handles{memory_.value};
        diagnostic_stage="script-execution";
        Require(utility_.value->AEGP_ExecuteScript(plugin_id, program.c_str(), FALSE,
            &handles.result, &handles.error) == 0 && handles.result);
        diagnostic_stage="script-result";
        AEGP_MemSize size = 0;
        Require(memory_.value->AEGP_GetMemHandleSize(handles.result, &size) == 0 && size > 0 && size <= 4096);
        void* ptr = nullptr; Require(memory_.value->AEGP_LockMemHandle(handles.result, &ptr) == 0 && ptr);
        std::string text;
        try { const auto length = strnlen(static_cast<const char*>(ptr), size);
            Require(length < size); text.assign(static_cast<const char*>(ptr), length);
        } catch (...) { if (memory_.value->AEGP_UnlockMemHandle(handles.result)) cleanup_ok = false; throw; }
        Require(memory_.value->AEGP_UnlockMemHandle(handles.result) == 0);
        return text;
    }
    std::int64_t BlankProjectRevision() {
        GuardProject();
        const auto text = Script(blank_script);
        diagnostic_stage="blank-script";
        for (const auto* reason : {"host-version", "unsaved-project", "blank-project", "render-queue", "color-route", "revision"})
            if (text == std::string("REFUSED:")+reason) diagnostic_stage=reason;
        const std::string prefix = "AEHL-CAL-BLANK-1\n";
        Require(text.rfind(prefix, 0) == 0 && text.back() == '\n');
        const auto number = text.substr(prefix.size(), text.size() - prefix.size() - 1);
        Require(!number.empty() && number.find_first_not_of("0123456789") == number.npos);
        const auto revision = std::stoll(number);
        GuardProject();
        return revision;
    }
    std::int32_t Count() { diagnostic_stage="enumeration-sdk-count"; A_long value = -1;
        Require(effect_.value->AEGP_GetNumInstalledEffects(&value) == 0); return value; }
    std::int32_t Next(std::int32_t cursor) { diagnostic_stage="enumeration-sdk-next"; AEGP_InstalledEffectKey value = 0;
        Require(effect_.value->AEGP_GetNextInstalledEffect(cursor, &value) == 0); return value; }
    std::string Match(std::int32_t key) { diagnostic_stage="enumeration-sdk-match"; char text[AEGP_MAX_EFFECT_MATCH_NAME_SIZE];
        std::memset(text, 0xff, sizeof(text));
        Require(effect_.value->AEGP_GetEffectMatchName(key, text) == 0);
        const auto length = strnlen(text, sizeof(text)); Require(length > 0 && length < sizeof(text));
#ifdef AEHL_TRACE_IDENTITY
        if (registry_observation && std::string(text, length) == calibration_match) {
            Require(MainThread() && OperationAllowed());
            const auto function = reinterpret_cast<std::uintptr_t>(effect_.value->AEGP_GetEffectMatchName);
            AEHL_TraceReaderBoundary(1, key, function, 0, 1);
            char repeated[AEGP_MAX_EFFECT_MATCH_NAME_SIZE]; std::memset(repeated, 0xff, sizeof(repeated));
            const auto error = effect_.value->AEGP_GetEffectMatchName(key, repeated);
            const auto repeated_length = strnlen(repeated, sizeof(repeated));
            const bool same = error == 0 && repeated_length == length &&
                repeated_length < sizeof(repeated) && std::memcmp(text, repeated, length) == 0;
            AEHL_TraceReaderBoundary(2, key, function, same ? 0u : 1u, 1);
            Require(same && OperationAllowed());
        }
#endif
        return std::string(text, length); }
    std::string Name(std::int32_t key) { diagnostic_stage="enumeration-sdk-name";
        char text[AEGP_MAX_EFFECT_NAME_SIZE]; std::memset(text, 0xff, sizeof(text));
        Require(effect_.value->AEGP_GetEffectName(key, text) == 0);
        const auto length = strnlen(text, sizeof(text)); Require(length > 0 && length < sizeof(text));
        return std::string(text, length); }
    bool ObservationAllowed() { return MainThread() && OperationAllowed(); }
    bool BeforeMutation() { if (!cleanup_ok) return false;
        GuardProject();
        Require(project_suite_.value->AEGP_GetProjectRootFolder(project_, &root_) == 0 && root_);
        Save("begin", std::string(calibration_build) + "\n"); return true; }
    bool CreateFixture() {
        if (!OperationAllowed()) return false;
        diagnostic_stage="color-engine";
        if (!NonOCIO()) return false;
        Save("color-engine","AEHL-CAL-COLOR-ENGINE-1\nocio=FALSE\n");
        // Once has already proved blank/unsaved/unchanged, recorded begin and
        // entered PartialUnknown. This changes only that owned diagnostic project.
        AEGP_ProjBitDepth depth{};
        if (project_suite_.value->AEGP_GetProjectBitDepth(project_, &depth)) return false;
        if (depth != AEGP_ProjBitDepth_8) {
            Save("depth-started",std::string("AEHL-CAL-DEPTH-1\nbuild=")+calibration_build+
                "\nfrom_sdk_enum="+std::to_string(depth)+"\nto=8\n");
            if (!OperationAllowed() || project_suite_.value->AEGP_SetProjectBitDepth(project_,AEGP_ProjBitDepth_8)) return false;
            if (!OperationAllowed() || project_suite_.value->AEGP_GetProjectBitDepth(project_, &depth) ||
                depth != AEGP_ProjBitDepth_8) return false;
            Save("depth-adjusted","AEHL-CAL-DEPTH-8\n");
        }
        if (!OperationAllowed()) return false;
        Save("color-started","AEHL-CAL-COLOR-PREPARE-1\nworking_space=NONE\nlinear_blending=FALSE\nlinearized=FALSE\n");
        std::string color_route;
        try { color_route=Script(startup_color::script); }
        catch (...) { Save("color-diagnostic",startup_color::SDKFailure(diagnostic_stage)); throw; }
        if (color_route!="AEHL-CAL-COLOR-1\n") {
            Save("color-diagnostic",startup_color::Diagnostic(color_route)); return false;
        }
        if (!OperationAllowed()) return false;
        Save("color-adjusted",color_route);
        const A_Ratio aspect{1, 1}, fps{24, 1}; const A_Time duration{1, 1};
        std::vector<A_UTF16Char> name;
        for (const char* p = calibration_fixture; *p; ++p) name.push_back(static_cast<A_UTF16Char>(*p));
        name.push_back(0);
        if (comp_.value->AEGP_CreateComp(root_, name.data(), 64, 48, &aspect, &duration, &fps, &fixture_) || !fixture_) return false;
        if (!OperationAllowed()) return false;
        const AEGP_ColorVal color{1, 0, 0, 0};
        return comp_.value->AEGP_CreateSolidInComp(name.data(), 64, 48, &color,
                                                 fixture_, &duration, &layer_) == 0 && layer_;
    }
    bool Apply(std::int32_t key) { return OperationAllowed() &&
        effect_.value->AEGP_ApplyEffect(plugin_id, layer_, key, &reference_) == 0 && reference_; }
    bool VerifyBuild() {
        if (!OperationAllowed()) return false;
        startup_marker::Identity identity; const A_Time time{0, 1};
        if (effect_.value->AEGP_EffectCallGeneric(plugin_id, reference_, &time,
                PF_Cmd_COMPLETELY_GENERAL, &identity) != 0 ||
            strnlen(identity.build, sizeof(identity.build)) == sizeof(identity.build) ||
            std::strcmp(identity.build, calibration_build) != 0 || identity.seed != calibration_seed) return false;
        Save("marker-identity", std::string("AEHL-MARKER-IDENTITY-1\nbuild=") + identity.build +
             "\nseed=" + std::to_string(identity.seed) + "\nrender_calls=" +
             std::to_string(identity.render_calls) + "\n"); return true;
    }
    std::int32_t Reverse() { AEGP_InstalledEffectKey value = 0;
        Require(OperationAllowed());
        Require(effect_.value->AEGP_GetInstalledKeyFromLayerEffect(reference_, &value) == 0); return value; }
    bool Allowed() { return OperationAllowed(); }
    AEGP_LayerH Layer() const { return layer_; }
    std::string OwnedSnapshot(bool complete, bool queue_done=false) {
        Require(SameProject() && NonOCIO());
        const auto script = std::string(R"JS((function () {
            var p=app.project, c=null, f=null, folders=0;
            var n=')JS") + calibration_fixture + "', m='" + calibration_match + "', complete=" +
            (complete ? "true" : "false") + ", queueDone=" + (queue_done ? "true" : "false") +
            ", output=" + startup_queue::Quote(std::string(calibration_control)+"/queue-output/control[#####].png") + R"JS(;
            if (!p || p.file!==null || (complete ? p.bitsPerChannel!==8 :
                (p.bitsPerChannel!==8 && p.bitsPerChannel!==16 && p.bitsPerChannel!==32)) ||
                (p.workingSpace!=='' && p.workingSpace!=='None') ||
                p.linearBlending!==false || p.linearizeWorkingSpace!==false ||
                p.renderQueue.numItems!==(queueDone?1:0) || p.renderQueue.rendering!==false ||
                p.numItems>3) return 'REFUSED';
            for (var i=1;i<=p.numItems;i++) {
                var x=p.item(i);
                if (x instanceof CompItem && x.name===n && !c && x.width===64 && x.height===48 &&
                    x.frameRate===24 && x.duration===1 && x.pixelAspect===1 && x.numLayers<=1) c=x;
                else if (x instanceof FootageItem && x.name===n && !f && x.width===64 && x.height===48) f=x;
                else if (x instanceof FolderItem && x.parentFolder===p.rootFolder && x.numItems===1 &&
                    x.item(1) instanceof FootageItem && x.item(1).name===n) folders++;
                else return 'REFUSED';
            }
            if (folders>1 || (complete && (!c || !f || c.numLayers!==1))) return 'REFUSED';
            if (c && c.numLayers===1) {
                var l=c.layer(1), effects=l.property('ADBE Effect Parade');
                if (!f || l.source!==f || l.name!==n || effects.numProperties>1 ||
                    (complete && effects.numProperties!==1) ||
                    (effects.numProperties===1 && effects.property(1).matchName!==m)) return 'REFUSED';
            } else if (f) return 'REFUSED';
            if(queueDone) {
                var q=p.renderQueue.item(1);
                if(!complete || !c || q.comp!==c || q.status!==RQItemStatus.DONE ||
                    q.timeSpanStart!==1/24 || q.timeSpanDuration!==1/24 || q.numOutputModules!==1)
                    return 'REFUSED';
                var om=q.outputModule(1);
                if(om.postRenderAction!==PostRenderAction.NONE || om.file.fsName!==new File(output).fsName)
                    return 'REFUSED';
            }
            return 'AEHL-CAL-OWNED-1\n'+p.revision+'\n';
        })())JS";
        const auto text=Script(script);
        Require(text.rfind("AEHL-CAL-OWNED-1\n",0)==0 && SameProject());
        return text;
    }
    bool CleanupSafe(bool queue_done=false) noexcept {
        try { const auto text=OwnedSnapshot(queue_done,queue_done);
            Require(!queue_done || (!queue_snapshot_.empty() && text==queue_snapshot_));
            Save("cleanup-safe", std::string("AEHL-CAL-CLEANUP-1\nbuild=")+calibration_build+
                "\npid="+std::to_string(getpid())+"\nbirth="+std::to_string(Birth())+"\n"+text);
            return true;
        } catch (...) { return false; }
    }
    bool ObservationSafe(std::int64_t revision) noexcept {
        try {
            Require(OperationAllowed() && revision > 0 && BlankProjectRevision() == revision);
            Save("cleanup-safe", std::string("AEHL-CAL-CLEANUP-1\nbuild=") + calibration_build +
                "\npid=" + std::to_string(getpid()) + "\nbirth=" + std::to_string(Birth()) +
                "\nAEHL-CAL-OWNED-1\n" + std::to_string(revision) + "\n");
            return true;
        } catch (...) { return false; }
    }
    std::uint64_t MarkerCounter(std::int32_t key) {
        Require(OperationAllowed() && !reference_);
        A_long count=0; Require(effect_.value->AEGP_GetLayerNumEffects(layer_, &count)==0 && count==1);
        Require(effect_.value->AEGP_GetLayerEffectByIndex(plugin_id, layer_, 0, &reference_)==0 && reference_);
        startup_marker::Identity identity; const A_Time time{1,24};
        Require(Reverse()==key && effect_.value->AEGP_EffectCallGeneric(plugin_id,reference_,&time,
            PF_Cmd_COMPLETELY_GENERAL,&identity)==0 &&
            strnlen(identity.build,sizeof(identity.build))<sizeof(identity.build) &&
            std::strcmp(identity.build,calibration_build)==0 && identity.seed==calibration_seed);
        Require(Dispose()); return identity.render_calls;
    }
    bool Dispose() { auto ref = reference_; reference_ = nullptr;
        const bool okay = ref && effect_.value->AEGP_DisposeEffect(ref) == 0;
        if (!okay) cleanup_ok = false;
        return okay; }
    bool QueueControl(std::int32_t key, std::uint64_t deadline) {
        Require(OperationAllowed());
        const auto before=MarkerCounter(key);
        const auto snapshot=OwnedSnapshot(true);
        const auto revision=std::stoll(snapshot.substr(std::strlen("AEHL-CAL-OWNED-1\n")));
        const auto program=startup_queue::Script(calibration_fixture,calibration_match,
            std::string(calibration_control)+"/queue-output",deadline,revision);
        Save("queue-started",std::string("AEHL-CAL-QUEUE-START-1\nbuild=")+calibration_build+
            "\nroute=SCRIPT_RENDER_QUEUE\ncounter_before="+std::to_string(before)+"\n");
        Require(OperationAllowed());
        const auto response=Script(program); Save("queue-result",response);
        Require(response.rfind("AEHL-CAL-QUEUE-1\nstatus=DONE\n",0)==0 && OperationAllowed());
        const auto revision_text=startup_queue::RevisionLine(response);
        const auto expected_snapshot=std::string("AEHL-CAL-OWNED-1\n")+revision_text;
        const auto after=MarkerCounter(key); Require(after>before);
        Require(OwnedSnapshot(true,true)==expected_snapshot);
        queue_snapshot_=expected_snapshot;
        Save("queue-metadata",std::string("AEHL-CAL-QUEUE-FRAME-1\nbuild=")+calibration_build+
            "\nkey="+std::to_string(key)+"\ncounter_before="+std::to_string(before)+
            "\ncounter_after="+std::to_string(after)+"\nworking_space=NONE\nrevision="+revision_text);
        return true;
    }
};

resident_binding::Digest Digest(const std::string& binary) {
    resident_binding::Digest digest{}; Require(binary.size()==64);
    const std::string digits="0123456789abcdef";
    for (std::size_t i=0;i<32;++i) { const auto a=digits.find(binary[i*2]), b=digits.find(binary[i*2+1]);
        Require(a<16 && b<16); digest[i]=static_cast<unsigned char>(a*16+b); }
    return digest;
}

// Optional diagnostic of our exact already-resident marker only. Never loads
// a module or calls its registration/EffectMain. Failure does not change the
// original refusal or resource cleanup outcome.
void ObserveMarkerStartup() noexcept {
    try {
    std::string text = std::string("AEHL-CAL-MARKER-STARTUP-1\nbuild=") + calibration_build +
        "\nsampling=INDEPENDENT_COUNTERS_NOT_LIFETIME_PROOF\n";
    try {
        const auto marker = resident_binding::Resolve({calibration_marker_module, Digest(calibration_marker_sha256)},
            {"_AEHL_MarkerBuildIdentity", "_AEHL_MarkerStartupState"});
        using Build = const char* (*)();
        Require(std::strcmp(reinterpret_cast<Build>(const_cast<void*>(
            marker.functions.at("_AEHL_MarkerBuildIdentity")))(), calibration_build) == 0);
        startup_marker::StartupState state;
        Require(reinterpret_cast<startup_marker::ReadStartupState>(const_cast<void*>(
            marker.functions.at("_AEHL_MarkerStartupState")))(&state));
        Require(strnlen(state.registration_name, sizeof(state.registration_name)) < sizeof(state.registration_name) &&
                strnlen(state.registration_match, sizeof(state.registration_match)) < sizeof(state.registration_match));
        text += "binding=EXACT_OWN_RESIDENT_IMAGE\nregistration_started=" + std::to_string(state.registration_started) +
            "\nregistration_completed=" + std::to_string(state.registration_completed) +
            "\nlast_callback_result=" + std::to_string(state.last_callback_result) +
            "\nglobal_setup_calls=" + std::to_string(state.global_setup_calls) +
            "\nparameter_setup_calls=" + std::to_string(state.parameter_setup_calls) +
            "\ncallback_address=" + std::to_string(state.callback_address) +
            "\nregistration_on_main=" + std::to_string(state.registration_on_main) +
            "\nregistration_name_hex=" + Hex(state.registration_name) +
            "\nregistration_match_hex=" + Hex(state.registration_match) +
            "\narguments_equal_config=" + (std::string(state.registration_name)==calibration_name &&
                std::string(state.registration_match)==calibration_match ? "YES" : "NO") + "\n";
        DescribeProvider("provider-registration", static_cast<std::uintptr_t>(state.callback_address));
    } catch (...) { text += "binding=UNKNOWN\n"; }
    Save("marker-startup", text);
    } catch (...) {}
}
// Existing main-thread operations only; missing facts do not alter acceptance.
void FrameBoundary(unsigned stage) noexcept {
    if (stage > 31) return;
    try { Save(("frame-boundary-" + std::to_string(stage)).c_str(),
        std::string("AEHL-CAL-FRAME-BOUNDARY-1\nbuild=") + calibration_build +
        "\nstage=" + std::to_string(stage) + "\nmonotonic_ms=" +
        std::to_string(MonotonicMillis()) + "\n"); } catch (...) {}
}
void FrameSDKBoundary(unsigned stage) noexcept {
    if (stage > 17) return;
    try { Save(("frame-sdk-" + std::to_string(stage)).c_str(),
        std::string("AEHL-CAL-FRAME-SDK-1\nbuild=") + calibration_build +
        "\nstage=" + std::to_string(stage) + "\nmonotonic_ms=" +
        std::to_string(MonotonicMillis()) + "\n"); } catch (...) {}
}
struct PendingFrame {
    std::unique_ptr<Backend> backend;
    Suite<AEGP_LayerRenderOptionsSuite2> options{kAEGPLayerRenderOptionsSuite,kAEGPLayerRenderOptionsSuiteVersion2};
    Suite<AEGP_RenderSuite5> render{kAEGPRenderSuite,kAEGPRenderSuiteVersion5};
    Suite<AEGP_WorldSuite3> world{kAEGPWorldSuite,kAEGPWorldSuiteVersion3};
    startup_frame::Capture capture{*options.value,*render.value,*world.value,FrameSDKBoundary};
    startup_calibration::Result result;
    std::uint64_t deadline=0, before=0;
    std::string project;
    bool canceled=false, poll_logged=false;
    PendingFrame(std::unique_ptr<Backend> b, startup_calibration::Result r, std::uint64_t d)
        : backend(std::move(b)), result(r), deadline(d) {}
    void Start() {
        Require(backend->Allowed());
        const auto marker=resident_binding::Resolve({calibration_marker_module,Digest(calibration_marker_sha256)},
            {"_EffectMain","_AEHL_MarkerBuildIdentity"});
        using Build=const char* (*)();
        Require(std::strcmp(reinterpret_cast<Build>(const_cast<void*>(
            marker.functions.at("_AEHL_MarkerBuildIdentity")))(),calibration_build)==0);
        before=backend->MarkerCounter(result.key); project=backend->OwnedSnapshot(true);
        Save("render-started", std::string("AEHL-CAL-RENDER-1\nroute=AEGP_RenderAndCheckoutLayerFrame_Async\n")+
            "build="+calibration_build+"\nbefore="+std::to_string(before)+"\ntime=1/24\n");
        std::ostringstream slots;
        slots << "AEHL-CAL-RENDER-SUITE-1\nlayer_options_version=" << kAEGPLayerRenderOptionsSuiteVersion2
              << "\nrender_version=" << kAEGPRenderSuiteVersion5 << "\nworld_version=" << kAEGPWorldSuiteVersion3
              << "\nrender_table=" << reinterpret_cast<std::uintptr_t>(render.value)
              << "\nasync=" << reinterpret_cast<std::uintptr_t>(render.value->AEGP_RenderAndCheckoutLayerFrame_Async)
              << "\nreceipt_world=" << reinterpret_cast<std::uintptr_t>(render.value->AEGP_GetReceiptWorld)
              << "\ncheckin=" << reinterpret_cast<std::uintptr_t>(render.value->AEGP_CheckinFrame) << '\n';
        Save("render-suite",slots.str());
        Require(backend->Allowed()); capture.Start(plugin_id,backend->Layer());
        Save("render-options",capture.OptionsDiagnostic());
    }
};
// A submitted context is never destroyed on timeout; late callback needs it.
// Unresolved contexts/suites remain pinned until the owned host exits.
PendingFrame* pending=nullptr;
void FrameDiagnostic(PendingFrame& frame,const char* phase) noexcept {
    try { Save("render-diagnostic",frame.capture.Diagnostic()+"observer_phase="+phase+"\n"); }
    catch (...) {} // A missing diagnostic never bypasses the original refusal/cleanup.
}
void Publish(startup_calibration::Result result, bool frame, bool safe) {
    const auto status=result.outcome==startup_calibration::Outcome::ListedApplied && frame && cleanup_ok
        ? "LISTED_APPLIED_FRAME_CAPTURED" : result.outcome==startup_calibration::Outcome::Refused
            ? "REFUSED" : "PARTIAL_UNKNOWN";
    Save("result",std::string("AEHL-CAL-RESULT-2\nbuild=")+calibration_build+"\nstatus="+status+
        "\nstage="+result.stage+"\nkey="+std::to_string(result.key)+"\ncleanup="+(cleanup_ok?"PASS":"FAIL")+
        "\ncleanup_safe="+(safe?"YES":"NO")+"\nrender="+(frame?"CAPTURED_PIXEL_CHECK_PENDING":"NOT_RUN_OR_UNKNOWN")+"\n");
}
bool PollFrame() {
    if (!pending) return false;
    auto* p=pending;
    const bool first_poll=!p->poll_logged;
    if(first_poll) {
        p->poll_logged=true;
        try { Save("render-poll",p->capture.Diagnostic()+"phase=before-allowed\n"); }
        catch (...) {} // Diagnostic failure does not change frame acceptance.
    }
    if (!p->capture.Done()) {
        const bool allowed=p->backend->Allowed();
        if(first_poll) {
            try { Save("render-poll-allowed",std::string("AEHL-CAL-POLL-1\nallowed=")+(allowed?"YES":"NO")+"\n"); }
            catch (...) {}
        }
        if (!allowed && !p->canceled) { p->canceled=true;
            const bool okay=p->capture.Cancel();
            Save("render-cancel",std::string("AEHL-CAL-CANCEL-1\nack=")+(okay?"YES":"NO")+"\n"); }
        return true;
    }
    bool frame=false;
    std::string bytes;
    std::uint64_t after=0;
    const char* phase="before-copy";
    try {
        FrameBoundary(0); Require(p->backend->Allowed()); FrameBoundary(1);
        phase="copy"; FrameBoundary(2); bytes=p->capture.Copy(); FrameBoundary(3);
        phase="marker-after";
        FrameBoundary(4); after=p->backend->MarkerCounter(p->result.key); FrameBoundary(5);
        Require(after>p->before); phase="owned-snapshot";
        FrameBoundary(6); const bool owned=p->backend->OwnedSnapshot(true)==p->project; FrameBoundary(7);
        Require(owned); FrameBoundary(8); Require(p->backend->Allowed()); FrameBoundary(9);
        frame=true;
    } catch (...) { p->result.outcome=startup_calibration::Outcome::PartialUnknown; FrameDiagnostic(*p,phase); }
    bool released=false;
    try { FrameBoundary(10); released=p->capture.Release(); FrameBoundary(11); } catch (...) { cleanup_ok=false; }
    if (!released) cleanup_ok=false;
    pending=nullptr; // completion consumed before any fallible journal write
    try {
    if (frame) {
        Save("frame.argb",bytes);
        Save("frame-metadata",std::string("AEHL-CAL-FRAME-1\nbuild=")+calibration_build+
            "\nwidth=64\nheight=48\norder=ARGB8\nstride=256\nsource_rowbytes="+
            std::to_string(p->capture.rowbytes)+"\nworld_type=8\ntime=1/24\nworking_space=NONE\n"+
            "counter_before="+std::to_string(p->before)+"\ncounter_after="+std::to_string(after)+"\n");
    }
    } catch (...) { frame=false; p->result.outcome=startup_calibration::Outcome::PartialUnknown; }
    auto result=p->result;
    if (frame) result.stage="public-async-frame-captured";
    FrameBoundary(12); const bool safe=released && p->backend->CleanupSafe(); FrameBoundary(13);
    if (released) { FrameBoundary(14); delete p; FrameBoundary(15); } // after checked cleanup
    FrameBoundary(16); Publish(result,frame,safe); FrameBoundary(17);
    return true;
}

struct PendingNames {
    std::unique_ptr<Backend> backend;
    startup_calibration::Authorization request, bound;
    startup_names::Schedule schedule;
    std::uint64_t start;
    std::int64_t revision = 0;
    std::int32_t key = 0, count = 0;
    explicit PendingNames(std::uint64_t time = MonotonicMillis()) : schedule(time), start(time) {}
};
std::unique_ptr<PendingNames> names;
void FinishCalibration(std::unique_ptr<Backend> backend,
                       const startup_calibration::Authorization& request,
                       const startup_calibration::Authorization& bound) {
        const auto result=once.Run(request,bound,*backend);
        ObserveMarkerStartup();
        if(queue_control) {
            bool done=false;
            if(result.outcome==startup_calibration::Outcome::ListedApplied && cleanup_ok) {
                try {done=backend->QueueControl(result.key,request.deadline);} catch (...) {}
            }
            const bool safe=done && backend->CleanupSafe(true);
            backend.reset(); // Release native suites before asserting cleanup PASS.
            Save("result",std::string("AEHL-CAL-RESULT-2\nbuild=")+calibration_build+
                "\nstatus="+(done && cleanup_ok ? "LISTED_APPLIED_QUEUE_EXPORTED" :
                    result.outcome==startup_calibration::Outcome::Refused ? "REFUSED" : "PARTIAL_UNKNOWN")+
                "\nstage=queue-control\nkey="+std::to_string(result.key)+
                "\ncleanup="+(cleanup_ok?"PASS":"FAIL")+"\ncleanup_safe="+(safe?"YES":"NO")+
                "\nrender="+(done?"QUEUE_PIXEL_CHECK_PENDING":"NOT_RUN_OR_UNKNOWN")+"\n");
            return;
        }
        if (result.outcome==startup_calibration::Outcome::ListedApplied && cleanup_ok) {
            pending=new PendingFrame(std::move(backend),result,request.deadline);
            try { pending->Start(); } catch (...) {
                FrameDiagnostic(*pending,"start");
                Save("render-submit-failed","AEHL-CAL-SUBMIT-UNKNOWN\n");
                if (pending->capture.Pending()) return;
                const bool safe=pending->backend->CleanupSafe();
                if (!pending->capture.Release()) cleanup_ok=false;
                delete pending; pending=nullptr;
                auto failed=result; failed.outcome=startup_calibration::Outcome::PartialUnknown;
                Publish(failed,false,safe);
            }
        } else {
            const bool safe=backend->CleanupSafe(); backend.reset(); Publish(result,false,safe);
        }
}
bool PollNames() {
    if (!names) return false;
    diagnostic_stage="name-observation-deadline";
    Require(names->request.deadline > Now());
    const auto now=MonotonicMillis();
    if (!names->schedule.Due(now)) return true;
    const auto index=names->schedule.Index();
    const auto snapshot=startup_names::Observe(*names->backend,calibration_name,calibration_match);
    std::ostringstream text;
    text << "AEHL-CAL-NAMES-1\nbuild=" << calibration_build << "\nsample=" << index
        << "\nelapsed_ms=" << now-names->start << "\ncount=" << snapshot.count
        << "\ntraversed=" << snapshot.traversed << "\nexact=" << snapshot.exact
        << "\nrevision=" << snapshot.revision << "\ncomplete=" << (snapshot.complete?"YES":"NO")
        << "\nstage=" << snapshot.stage << "\nown_observations=" << snapshot.own.size() << '\n';
    for (std::size_t i=0;i<snapshot.own.size();++i) {
        const auto& entry=snapshot.own[i];
        text << "own_" << i << "_key=" << entry.key
             << "\nown_" << i << "_name_hex=" << Hex(entry.name)
             << "\nown_" << i << "_match_hex=" << Hex(entry.match) << '\n';
    }
    const auto file="names-"+std::to_string(index); Save(file.c_str(),text.str());
    diagnostic_stage=snapshot.stage;
    Require(snapshot.complete);
    if (index==0) names->revision=snapshot.revision;
    diagnostic_stage="name-observation-between-samples-project-changed";
    Require(names->revision==snapshot.revision);
    if (registry_observation) {
        diagnostic_stage="registry-observation-own-marker";
        Require(snapshot.exact == 1);
        std::int32_t key = 0;
        for (const auto& entry : snapshot.own)
            if (entry.match == calibration_match && entry.name == calibration_name) key = entry.key;
        Require(key != 0);
        if (index == 0) { names->key = key; names->count = snapshot.count; }
        Require(key == names->key && snapshot.count == names->count);
    }
    names->schedule.Advance();
    if (names->schedule.Done()) {
        auto ready=std::move(names); // consumed before any fallible host operation
        if (registry_observation) {
            ObserveMarkerStartup();
            const bool safe = ready->backend->ObservationSafe(ready->revision);
            ready->backend.reset(); // Suite releases precede resource-cleanup assertion.
            Save("result",std::string("AEHL-CAL-RESULT-2\nbuild=")+calibration_build+
                "\nstatus="+(safe && cleanup_ok ? "LISTED_OBSERVED" : "PARTIAL_UNKNOWN")+
                "\nstage=registry-observation\nkey="+std::to_string(ready->key)+
                "\ncleanup="+(cleanup_ok?"PASS":"FAIL")+"\ncleanup_safe="+(safe?"YES":"NO")+
                "\nrender=NOT_RUN\napply=NOT_RUN\n");
            return true;
        }
        FinishCalibration(std::move(ready->backend),ready->request,ready->bound);
    }
    return true;
}

A_Err Idle(AEGP_GlobalRefcon, AEGP_IdleRefcon, A_long*) noexcept {
    if (pthread_main_np() != 1 || idle_active) return 0;
    idle_active=true;
    struct IdleReset { ~IdleReset() { idle_active=false; } } reset;
    try {
        if (PollFrame() || PollNames() || consumed) return 0;
        DiagnosticStage("request-discovery");
        if (!Exists("request")) return 0;
        consumed = true; // before parsing, acquisition, reentry or any host operation
        startup_calibration::Authorization request;
        std::string schema, ownership, binary, trailing;
        DiagnosticStage("request-read");
        std::istringstream input(Read("request"));
        DiagnosticStage("request-parse-fields");
        Require(static_cast<bool>(input >> schema >> request.token >> request.pid >> request.birth >> request.deadline >> ownership >> binary));
        DiagnosticStage("request-parse-contract");
        Require(!(input >> trailing) && schema == "AEHL-CAL-REQUEST-2" &&
            (ownership == "OWNED-STARTUP-APPLY-RENDER" || ownership == "OWNED-STARTUP-QUEUE-CONTROL" ||
             ownership == "OWNED-STARTUP-REGISTRY-OBSERVATION"));
        queue_control=ownership == "OWNED-STARTUP-QUEUE-CONTROL";
        registry_observation=ownership == "OWNED-STARTUP-REGISTRY-OBSERVATION";
        request.owned_blank_project = true;
        DiagnosticStage("request-process-birth");
        const startup_calibration::Authorization bound{calibration_token, getpid(), Birth(), 0, true};
        DiagnosticStage("request-token"); Require(request.token == bound.token);
        DiagnosticStage("request-process"); Require(request.pid == bound.pid && request.birth == bound.birth);
        DiagnosticStage("request-deadline"); Require(request.deadline > Now() && request.deadline - Now() <= 120);
        DiagnosticStage("request-module-path"); Require(Module() == calibration_module);
        DiagnosticStage("request-executable-path"); Require(Executable() == calibration_executable);
        DiagnosticStage("request-resident-binding");
        const auto self = resident_binding::Resolve({calibration_module, Digest(binary)}, {"_AEHL_CalibrationBuildIdentity"});
        DiagnosticStage("request-resident-symbol");
        Require(self.functions.at("_AEHL_CalibrationBuildIdentity") == reinterpret_cast<void*>(&AEHL_CalibrationBuildIdentity));
        DiagnosticStage("request-names-allocation");
        names=std::make_unique<PendingNames>();
        names->request=request; names->bound=bound;
        DiagnosticStage("backend-prepare");
        names->backend=std::make_unique<Backend>(request.deadline);
        PollNames();
    } catch (...) {
        consumed = true;
        names.reset();
        ObserveMarkerStartup();
        try {
          std::string details;
          if (diagnostic_suite) details += std::string("suite=") + diagnostic_suite +
              "\nsuite_version=" + std::to_string(diagnostic_suite_version) + "\n";
          if (diagnostic_host_error_known) details += "host_error=" + std::to_string(diagnostic_host_error) + "\n";
          Save("result", std::string("AEHL-CAL-RESULT-2\nbuild=") + calibration_build +
            "\nstatus=" + (Exists("begin") ? "PARTIAL_UNKNOWN" : "REFUSED") +
            "\nstage=" + diagnostic_stage + "\ncleanup=" + (cleanup_ok ? "PASS" : "FAIL") + "\nrender=UNKNOWN\n" + details);
        } catch (...) {}
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
        StartupStage(0);
        DiagnosticStage("idle-registration"); basic = suites; plugin_id = id;
        StartupStage(1);
        { Suite<AEGP_RegisterSuite5> registration(kAEGPRegisterSuite, kAEGPRegisterSuiteVersion5);
          StartupStage(2); StartupStage(3);
          DiagnosticStage("idle-registration");
          Require(registration.value->AEGP_RegisterIdleHook);
          const auto error = registration.value->AEGP_RegisterIdleHook(plugin_id, Idle, nullptr);
          diagnostic_host_error = error; diagnostic_host_error_known = true;
          Require(error == 0);
          StartupStage(4); }
        StartupStage(5);
        Require(cleanup_ok);
        StartupStage(6);
        Save("ready", std::string("AEHL-CAL-READY-1\nbuild=") + calibration_build + "\npid=" +
             std::to_string(getpid()) + "\nbirth=" + std::to_string(Birth()) + "\n");
        StartupStage(7);
    } catch (...) { consumed = true; }
    return 0;
}
