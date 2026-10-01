// Research AEGP for one no-scan FILE directory lifecycle probe.
// Inert without the exact startup token + one-shot supervisor request.
// It never calls PLUG_Search, InternalLoader, plugin enumeration or registration.
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "NoScanDirectoryJournal.hpp"
#include "ResidentDirectorySession.hpp"
#include "NoScanDirectoryConfig.hpp"
#include <cerrno>
#include <chrono>
#include <climits>
#include <cstring>
#include <dirent.h>
#include <dlfcn.h>
#include <filesystem>
#include <fcntl.h>
#include <libproc.h>
#include <mach-o/dyld.h>
#include <pthread.h>
#include <sys/stat.h>
#include <unistd.h>

namespace {
namespace fs = std::filesystem;
SPBasicSuite* basic = nullptr;
AEGP_PluginID plugin_id = 0;
bool consumed = false;
void ImageMarker() {}

void Require(bool value, const char* reason) {
    if (!value) throw std::runtime_error(reason);
}

template<class T> struct Suite {
    SPBasicSuite* provider;
    const char* name;
    A_long version;
    const T* value = nullptr;
    Suite(SPBasicSuite* p, const char* n, A_long v) : provider(p), name(n), version(v) {
        Require(provider && provider->AcquireSuite(name, version,
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
    return 'AEHL-NOSCAN-SNAPSHOT-1\n' + p.revision + '\n' + names.join('\n') + '\n';
})())JS";

struct ProjectSnapshot { std::uint64_t revision = 0; std::vector<std::string> registry; };
ProjectSnapshot SnapshotProject() {
    Suite<AEGP_UtilitySuite6> utility(basic, kAEGPUtilitySuite, kAEGPUtilitySuiteVersion6);
    Suite<AEGP_MemorySuite1> memory(basic, kAEGPMemorySuite, kAEGPMemorySuiteVersion1);
    Handles handles{memory.value};
    A_Boolean available = FALSE;
    Require(utility.value->AEGP_IsScriptingAvailable(&available) == 0 && available,
            "scripting unavailable");
    Require(utility.value->AEGP_ExecuteScript(plugin_id, snapshot_script, FALSE,
                                              &handles.result, &handles.error) == 0 && handles.result,
            "host snapshot failed");
    AEGP_MemSize size = 0;
    Require(memory.value->AEGP_GetMemHandleSize(handles.result, &size) == 0 &&
            size > 0 && size <= 1024 * 1024, "invalid snapshot size");
    void* ptr = nullptr;
    Require(memory.value->AEGP_LockMemHandle(handles.result, &ptr) == 0 && ptr,
            "snapshot lock failed");
    std::string text;
    try {
        const auto length = strnlen(static_cast<const char*>(ptr), size);
        Require(length < size, "snapshot missing terminator");
        text.assign(static_cast<const char*>(ptr), length);
    } catch (...) {
        memory.value->AEGP_UnlockMemHandle(handles.result);
        throw;
    }
    Require(memory.value->AEGP_UnlockMemHandle(handles.result) == 0,
            "snapshot unlock failed");
    const std::string prefix = "AEHL-NOSCAN-SNAPSHOT-1\n";
    Require(text.rfind(prefix, 0) == 0 && text.back() == '\n', "unsafe host snapshot");
    const auto end = text.find('\n', prefix.size());
    Require(end != std::string::npos, "missing project revision");
    const auto revision = text.substr(prefix.size(), end - prefix.size());
    Require(!revision.empty() && revision.find_first_not_of("0123456789") == std::string::npos,
            "invalid project revision");
    ProjectSnapshot result;
    result.revision = std::stoull(revision);
    for (auto pos = end + 1; pos < text.size();) {
        const auto next = text.find('\n', pos);
        Require(next != std::string::npos, "unterminated registry entry");
        const auto name = text.substr(pos, next - pos);
        if (name.empty()) break;
        Require(name.size() <= 1024 && name.find_first_of("\r\0", 0, 2) == std::string::npos,
                "invalid registry entry");
        result.registry.push_back(name);
        Require(result.registry.size() <= 20000, "registry too large");
        pos = next + 1;
    }
    Require(!result.registry.empty(), "empty registry");
    return result;
}

std::string CanonicalExecutable() {
    char path[PATH_MAX];
    std::uint32_t size = sizeof(path);
    Require(_NSGetExecutablePath(path, &size) == 0, "host path unavailable");
    return fs::canonical(path).string();
}
std::string ModulePath() {
    Dl_info info{};
    Require(dladdr(reinterpret_cast<const void*>(&ImageMarker), &info) && info.dli_fname,
            "module path unavailable");
    return fs::canonical(info.dli_fname).string();
}
std::string StartIdentity() {
    proc_bsdinfo info{};
    const int count = proc_pidinfo(getpid(), PROC_PIDTBSDINFO, 0, &info, sizeof(info));
    Require(count == static_cast<int>(sizeof(info)), "process start unavailable");
    return std::to_string(info.pbi_start_tvsec) + "." + std::to_string(info.pbi_start_tvusec);
}
std::string Token() {
    const char* value = std::getenv("AEHL_NOSCAN_GATE_TOKEN");
    return value ? value : "";
}

void PrivateDirectory(const std::string& path) {
    auto fd = resource_pass::journal_detail::Directory(path);
    const auto st = resource_pass::journal_detail::Stat(fd.get());
    Require(S_ISDIR(st.st_mode) && st.st_uid == geteuid() && (st.st_mode & 07777) == 0700,
            "directory must be owned/private");
}
std::string ReadControl(const std::string& directory, const char* name, std::size_t limit) {
    PrivateDirectory(directory);
    auto dir = resource_pass::journal_detail::Directory(directory);
    resource_pass::journal_detail::Fd fd(::openat(dir.get(), name,
        O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC));
    Require(fd.get() >= 0, "control file unavailable");
    const auto before = resource_pass::journal_detail::Stat(fd.get());
    Require(S_ISREG(before.st_mode) && before.st_uid == geteuid() && before.st_nlink == 1 &&
            (before.st_mode & 07777) == 0600 && before.st_size >= 0 &&
            static_cast<std::size_t>(before.st_size) <= limit, "unsafe control file");
    std::string bytes(static_cast<std::size_t>(before.st_size), '\0');
    std::size_t offset = 0;
    while (offset < bytes.size()) {
        const auto n = ::read(fd.get(), bytes.data() + offset, bytes.size() - offset);
        if (n < 0 && errno == EINTR) continue;
        Require(n > 0, "control read failed");
        offset += static_cast<std::size_t>(n);
    }
    char extra;
    Require(::read(fd.get(), &extra, 1) == 0 &&
            resource_pass::journal_detail::Same(before, resource_pass::journal_detail::Stat(fd.get())),
            "control file changed");
    return bytes;
}
void SaveControl(const std::string& directory, const char* name, const std::string& bytes) {
    PrivateDirectory(directory);
    auto dir = resource_pass::journal_detail::Directory(directory);
    resource_pass::journal_detail::Fd fd(::openat(dir.get(), name,
        O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600));
    Require(fd.get() >= 0, "control evidence already exists");
    Require(::fchmod(fd.get(), 0600) == 0, "control evidence mode failed");
    std::size_t offset = 0;
    while (offset < bytes.size()) {
        const auto n = ::write(fd.get(), bytes.data() + offset, bytes.size() - offset);
        if (n < 0 && errno == EINTR) continue;
        Require(n > 0, "control evidence write failed");
        offset += static_cast<std::size_t>(n);
    }
    Require(::fsync(fd.get()) == 0 && fd.close_checked() && ::fsync(dir.get()) == 0,
            "control evidence sync failed");
}
bool ExistsControl(const std::string& directory, const char* name) {
    PrivateDirectory(directory);
    auto dir = resource_pass::journal_detail::Directory(directory);
    struct stat st{};
    if (::fstatat(dir.get(), name, &st, AT_SYMLINK_NOFOLLOW) == 0) return true;
    if (errno == ENOENT) return false;
    throw std::runtime_error("control existence check failed");
}

std::string ExpectedRequest(const no_scan_directory::Config& c, pid_t pid) {
    return "version=1\nkind=no-scan-directory\nbuild_id=" + c.plan.build_id +
           "\nrun_id=" + c.plan.run_id + "\npid=" + std::to_string(pid) +
           "\ntoken=" + c.token +
           "\nprivate_file_call=authorized\nprovider_retention=authorized\ncontract=reviewed\n";
}

class LiveBackend final : public no_scan_directory::JournaledBackend {
    bool directory_identity_set_ = false;
    struct stat directory_identity_{};
public:
    explicit LiveBackend(const std::string& journal) : JournaledBackend(journal) {}
    std::uint64_t now_ms() override {
        return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count());
    }
    no_scan_directory::Observation observe() override {
        Require(pthread_main_np() == 1, "observation off main thread");
        const auto project = SnapshotProject();
        no_scan_directory::Observation o;
        o.pid = getpid(); o.process_start = StartIdentity();
        o.executable = CanonicalExecutable(); o.module_path = ModulePath();
        o.version = "25.6x101"; o.build = 101; o.arch = "arm64";
        o.main_thread = true; o.unsaved = true; o.dirty = false; o.rendering = false;
        o.items = 0; o.queued = 0; o.revision = project.revision; o.registry = project.registry;
        for (const auto& image : resident_binding::Snapshot())
            o.images.push_back({image.path, image.header, image.slide});
        return o;
    }
    void verify_directory(const no_scan_directory::Plan& p) override {
        Require(directory_spec::AsciiDirectoryPath(p.directory), "probe directory is not ASCII/canonical");
        auto dir = resource_pass::journal_detail::Directory(p.directory);
        const auto st = resource_pass::journal_detail::Stat(dir.get());
        Require(S_ISDIR(st.st_mode) && st.st_uid == geteuid() && (st.st_mode & 07777) == 0700,
                "probe directory must be owned/private");
        if (!directory_identity_set_) {
            directory_identity_ = st; directory_identity_set_ = true;
        } else {
            Require(st.st_dev == directory_identity_.st_dev && st.st_ino == directory_identity_.st_ino &&
                    st.st_uid == directory_identity_.st_uid && st.st_mode == directory_identity_.st_mode,
                    "probe directory identity changed");
        }
        const int duplicate = ::openat(dir.get(), ".", resource_pass::journal_detail::directory_flags);
        Require(duplicate >= 0, "probe directory list failed");
        DIR* listing = ::fdopendir(duplicate);
        if (!listing) { ::close(duplicate); throw std::runtime_error("probe directory list failed"); }
        std::size_t entries = 0;
        try {
            for (;;) {
                errno = 0;
                const auto* entry = ::readdir(listing);
                if (!entry) { Require(errno == 0, "probe directory read failed"); break; }
                const std::string name(entry->d_name);
                if (name != "." && name != "..") ++entries;
                Require(entries == 0, "probe directory is not empty");
            }
        } catch (...) { ::closedir(listing); throw; }
        Require(::closedir(listing) == 0, "probe directory close failed");
    }
    no_scan_directory::NativeResult run_directory_probe(
        const no_scan_directory::Plan& p, const no_scan_directory::Approval& approval) override {
        Require(approval.private_file_call_authorized &&
                approval.provider_reference_retention_authorized && approval.native_contract_reviewed,
                "native approval missing");
        auto functions = native_directory::BindRetainedOnce(
            native_directory::ReviewedAE256Profile(), approval.provider_reference_retention_authorized);
        const auto result = directory_spec::CreateRoundtripRelease(functions, p.directory, false);
        no_scan_directory::NativeResult out;
        out.completed = result.completed; out.invoked = result.invoked; out.cleanup_ok = result.cleanup_ok;
        out.strings_created = result.strings_created;
        out.string_release_attempts = result.string_release_attempts;
        out.specs_created = result.specs_created;
        out.spec_release_attempts = result.spec_release_attempts;
        out.retained_references = native_directory::RetainedDirectoryReferences();
        return out;
    }
};

A_Err Idle(AEGP_GlobalRefcon, AEGP_IdleRefcon, A_long* max_sleep) {
    if (consumed) return 0;
    if (max_sleep && *max_sleep > 15) *max_sleep = 15;
    try {
        Require(pthread_main_np() == 1, "idle callback off main thread");
        const auto& c = research_config;
        PrivateDirectory(c.control_directory);
        if (!ExistsControl(c.control_directory, "request.txt")) return 0;
        consumed = true;
        const auto request = ReadControl(c.control_directory, "request.txt", 4096);
        Require(request == ExpectedRequest(c, getpid()), "request identity mismatch");
        no_scan_directory::Approval approval{c.plan, true, true, true};
        LiveBackend backend(c.journal_directory);
        const auto result = no_scan_directory::RunJournaled(c.plan, approval, backend);
        if (result.status != "PASS" && !ExistsControl(c.control_directory, "adapter-stopped.txt"))
            SaveControl(c.control_directory, "adapter-stopped.txt",
                        "status=" + result.status + "\nstage=" + result.stage + "\n");
    } catch (...) {
        consumed = true;
        try {
            if (!ExistsControl(research_config.control_directory, "adapter-stopped.txt"))
                SaveControl(research_config.control_directory, "adapter-stopped.txt", "status=FAIL\n");
        } catch (...) {}
    }
    return 0;
}
} // namespace

extern "C" __attribute__((visibility("default")))
const char* AEHL_NoScanBuildIdentity() { return research_identity; }

extern "C" __attribute__((visibility("default")))
A_Err EntryPointFunc(SPBasicSuite* suites, A_long, A_long, AEGP_PluginID id,
                     AEGP_GlobalRefcon*) {
    try {
        const auto& c = research_config;
        if (!suites || Token() != c.token || CanonicalExecutable() != c.plan.executable ||
            ModulePath() != c.plan.module_path) return 0;
        PrivateDirectory(c.control_directory);
        PrivateDirectory(c.journal_directory);
        PrivateDirectory(c.plan.directory);
        if (ExistsControl(c.control_directory, "ready.txt") ||
            ExistsControl(c.control_directory, "request.txt")) return 0;
        basic = suites; plugin_id = id;
        Suite<AEGP_RegisterSuite5> registration(basic, kAEGPRegisterSuite, kAEGPRegisterSuiteVersion5);
        Require(registration.value->AEGP_RegisterIdleHook(id, Idle, nullptr) == 0,
                "idle hook registration failed");
        SaveControl(c.control_directory, "ready.txt", std::string(research_identity) +
                    "\npid=" + std::to_string(getpid()) + "\nimage=" + ModulePath() + "\n");
    } catch (...) { consumed = true; return 1; }
    return 0;
}
