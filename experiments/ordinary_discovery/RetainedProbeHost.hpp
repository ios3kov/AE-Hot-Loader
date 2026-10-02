// Public SDK snapshot/control primitives copied from the reviewed observer.
#pragma once
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
    void release_checked() {
        if (!value) return;
        value = nullptr; // consume release attempt before calling SDK
        Require(provider->ReleaseSuite(name, version) == 0, "SDK suite release failed");
    }
    Suite(const Suite&) = delete;
    Suite& operator=(const Suite&) = delete;
};
struct Handles {
    const AEGP_MemorySuite1* memory;
    AEGP_MemHandle result = nullptr, error = nullptr;
    void release_checked() {
        const auto r = result, e = error; result = error = nullptr;
        const auto result_error = r ? memory->AEGP_FreeMemHandle(r) : 0;
        const auto script_error = e ? memory->AEGP_FreeMemHandle(e) : 0;
        Require(result_error == 0 && script_error == 0, "SDK result handle release failed");
    }
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
    return 'AEHL-CLEANUP-SNAPSHOT-1\n' + p.revision + '\n' + names.join('\n') + '\n';
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
    const std::string prefix = "AEHL-CLEANUP-SNAPSHOT-1\n";
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
    handles.release_checked(); memory.release_checked(); utility.release_checked();
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
    const char* value = std::getenv("AEHL_RETAINED_IDENTITY_TOKEN");
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

} // namespace
