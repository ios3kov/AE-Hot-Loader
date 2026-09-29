// Research-only gate. No AE API or broad-root enumeration in this layer.
#pragma once
#include <CommonCrypto/CommonDigest.h>
#include <algorithm>
#include <cerrno>
#include <cstdio>
#include <fcntl.h>
#include <filesystem>
#include <functional>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace scoped {
namespace fs = std::filesystem;
inline void Require(bool ok, const char* reason) {
    if (!ok) throw std::runtime_error(reason);
}
struct Config {
    std::string build_id, commit, token, host_executable, root, bundle, evidence, match;
    std::map<std::string, std::string> files;
};
inline void NoLinks(const fs::path& path) {
    Require(path.is_absolute() && path.lexically_normal() == path, "noncanonical path");
    fs::path part;
    for (const auto& component : path) {
        part /= component;
        Require(!fs::is_symlink(fs::symlink_status(part)), "symlink path");
    }
}
inline std::string Read(const fs::path& path, std::size_t limit) {
    NoLinks(path);
    const int fd = open(path.c_str(), O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
    Require(fd >= 0, "file open failed");
    struct stat st {};
    if (fstat(fd, &st) || !S_ISREG(st.st_mode) || st.st_uid != getuid() ||
        st.st_nlink != 1 || st.st_size < 0 || static_cast<std::size_t>(st.st_size) > limit) {
        close(fd);
        throw std::runtime_error("file ownership/type/size rejected");
    }
    std::string value(static_cast<std::size_t>(st.st_size), '\0');
    std::size_t offset = 0;
    while (offset < value.size()) {
        const auto n = read(fd, value.data() + offset, value.size() - offset);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) { close(fd); throw std::runtime_error("file read failed"); }
        offset += static_cast<std::size_t>(n);
    }
    char extra;
    const bool complete = read(fd, &extra, 1) == 0;
    close(fd);
    Require(complete, "file changed while reading");
    return value;
}
inline std::string Hash(const std::string& value) {
    unsigned char digest[CC_SHA256_DIGEST_LENGTH];
    CC_SHA256(value.data(), static_cast<CC_LONG>(value.size()), digest);
    static constexpr char hex[] = "0123456789abcdef";
    std::string result;
    for (auto c : digest) { result += hex[c >> 4]; result += hex[c & 15]; }
    return result;
}
inline void OwnedEvidence(const fs::path& path) {
    NoLinks(path);
    struct stat st {};
    Require(lstat(path.c_str(), &st) == 0 && S_ISDIR(st.st_mode) &&
            st.st_uid == getuid() && (st.st_mode & 0777) == 0700,
            "evidence directory must be owned and private");
}
inline void Save(const Config& c, const char* name, const std::string& value) {
    OwnedEvidence(c.evidence);
    const auto path = fs::path(c.evidence) / name;
    const auto temporary = fs::path(path.string() + ".writing");
    const int fd = open(temporary.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    Require(fd >= 0, "evidence already exists or cannot be created");
    std::size_t offset = 0;
    while (offset < value.size()) {
        const auto n = write(fd, value.data() + offset, value.size() - offset);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) { close(fd); throw std::runtime_error("evidence write failed"); }
        offset += static_cast<std::size_t>(n);
    }
    const int sync_result = fsync(fd);
    const int close_result = close(fd);
    Require(sync_result == 0 && close_result == 0, "evidence flush failed");
    Require(renamex_np(temporary.c_str(), path.c_str(), RENAME_EXCL) == 0,
            "evidence publication failed or already exists");
}
inline void VerifyScope(const Config& c) {
    NoLinks(c.root);
    Require(!c.files.empty() && fs::is_directory(c.root), "empty/missing scan root");
    const auto bundle = fs::path(c.root) / c.bundle;
    Require(fs::path(c.bundle).filename() == c.bundle &&
            fs::path(c.bundle).extension() == ".plugin", "invalid bundle name");
    std::set<fs::path> top;
    for (const auto& entry : fs::directory_iterator(c.root)) top.insert(entry.path());
    Require(top == std::set<fs::path>{bundle}, "extra entry in scan root");
    NoLinks(bundle);
    std::set<std::string> expected_dirs, actual_dirs;
    for (const auto& entry : c.files) {
        fs::path relative(entry.first);
        Require(!relative.is_absolute() && relative.lexically_normal() == relative &&
                entry.first.find("..") == std::string::npos, "invalid pinned file path");
        for (auto parent = relative.parent_path(); !parent.empty(); parent = parent.parent_path())
            expected_dirs.insert(parent.string());
    }
    std::map<std::string, std::string> actual;
    for (const auto& entry : fs::recursive_directory_iterator(bundle)) {
        Require(!entry.is_symlink(), "symlink in fixture");
        auto relative = entry.path().lexically_relative(bundle).string();
        if (entry.is_directory()) actual_dirs.insert(relative);
        else actual[relative] = Hash(Read(entry.path(), 16 * 1024 * 1024));
    }
    Require(actual == c.files && actual_dirs == expected_dirs, "fixture inventory/hash mismatch");
}
struct Snapshot {
    std::string revision;
    std::vector<std::string> registry;
};
inline Snapshot ParseSnapshot(const std::string& text) {
    const std::string prefix = "AEHL-SNAPSHOT-1\n";
    Require(text.size() <= 1024 * 1024 && text.rfind(prefix, 0) == 0 &&
            text.back() == '\n', "unsafe or malformed host snapshot");
    Snapshot s;
    const auto end = text.find('\n', prefix.size());
    Require(end != std::string::npos, "missing revision");
    s.revision = text.substr(prefix.size(), end - prefix.size());
    Require(!s.revision.empty() && s.revision.find_first_not_of("0123456789") == std::string::npos,
            "invalid revision");
    for (auto pos = end + 1; pos < text.size();) {
        const auto next = text.find('\n', pos);
        auto name = text.substr(pos, next - pos);
        Require(!name.empty() && name.find_first_of("\r\0", 0, 2) == std::string::npos,
                "invalid registry entry");
        s.registry.push_back(name);
        Require(s.registry.size() <= 20000, "registry too large");
        pos = next + 1;
    }
    std::sort(s.registry.begin(), s.registry.end());
    return s;
}
inline std::string Request(const Config& c, int pid) {
    return "version=1\nbuild_id=" + c.build_id + "\npid=" + std::to_string(pid) +
           "\ntoken=" + c.token + "\n";
}
// Caller provides SDK read-only snapshot and the existing single-root loader.
// The exclusive claim survives restart; there is no retry after any failure.
inline void Run(const Config& c, const std::string& request, int pid,
                const std::string& executable, const std::string& token,
                const std::function<std::string()>& snapshot,
                const std::function<int(const char*)>& load) {
    Require(pid > 0 && request == Request(c, pid), "wrong process/request identity");
    Require(executable == c.host_executable && token == c.token, "host activation mismatch");
    Save(c, "claim.txt", request);
    const char* stage = "scope";
    try {
        VerifyScope(c);
        stage = "baseline";
        const auto before_text = snapshot();
        const auto before = ParseSnapshot(before_text);
        Require(std::count(before.registry.begin(), before.registry.end(), c.match) == 0,
                "fixture already registered");
        Save(c, "before.txt", before_text);
        // Recheck after the host callback, immediately before the private call.
        VerifyScope(c);
        stage = "loader";
        Save(c, "call-started.txt", "root=" + c.root + "\npid=" + std::to_string(pid) + "\n");
        const int result = load(c.root.c_str());
        Save(c, "loader-result.txt", std::to_string(result) + "\n");
        // Obtain postflight even when the loader returned an error.
        stage = "postflight";
        const auto after_text = snapshot();
        const auto after = ParseSnapshot(after_text);
        Save(c, "after.txt", after_text);
        Require(before.revision == after.revision, "project revision changed");
        auto expected = before.registry;
        expected.push_back(c.match);
        std::sort(expected.begin(), expected.end());
        Require(after.registry == expected, "registry delta is not exactly the fixture");
        Require(result >= 0, "loader returned an error");
        VerifyScope(c);
        Save(c, "result.txt", "status=PASS\nscope=registration-only\nbuild_id=" + c.build_id +
             "\nsource=" + c.commit + "\npid=" + std::to_string(pid) + "\n");
    } catch (...) {
        Save(c, "result.txt", std::string("status=FAIL\nstage=") + stage + "\n");
        throw;
    }
}
} // namespace scoped
