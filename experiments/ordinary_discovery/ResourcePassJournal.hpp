// Research-only POSIX evidence journal. Does not bind or invoke any Adobe API.
// A dedicated, existing, empty 0700 directory is required. Never deletes evidence.
#pragma once
#include "ResourcePassGate.hpp"
#include <cerrno>
#include <dirent.h>
#include <fcntl.h>
#include <set>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace resource_pass {
namespace journal_detail {
class Fd {
    int fd_;
public:
    explicit Fd(int fd = -1) : fd_(fd) {}
    ~Fd() { if (fd_ >= 0) ::close(fd_); }
    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;
    Fd(Fd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    Fd& operator=(Fd&& other) noexcept {
        if (this != &other) { if (fd_ >= 0) ::close(fd_); fd_ = std::exchange(other.fd_, -1); }
        return *this;
    }
    int get() const { return fd_; }
    bool close_checked() { return ::close(std::exchange(fd_, -1)) == 0; }
};
constexpr int directory_flags = O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC;
constexpr std::size_t max_record = 24 * 1024 * 1024;
inline Fd Directory(const std::string& path) {
    Need(Canonical(path), "journal-path-not-canonical");
    Fd fd(::open("/", directory_flags));
    Need(fd.get() >= 0, "journal-root-open-failed");
    // Walk every component using directory FDs. Never follow a parent symlink.
    for (std::size_t start = 1; start < path.size();) {
        const auto end = path.find('/', start);
        const auto part = path.substr(start, end == std::string::npos ? end : end - start);
        Fd next(::openat(fd.get(), part.c_str(), directory_flags));
        Need(next.get() >= 0, "journal-parent-open-failed");
        fd = std::move(next);
        if (end == std::string::npos) break;
        start = end + 1;
    }
    return fd;
}
inline struct stat Stat(int fd) {
    struct stat value {};
    Need(::fstat(fd, &value) == 0, "journal-stat-failed");
    return value;
}
inline bool Same(const struct stat& a, const struct stat& b) {
    return a.st_dev == b.st_dev && a.st_ino == b.st_ino && a.st_uid == b.st_uid &&
           a.st_mode == b.st_mode && a.st_nlink == b.st_nlink && a.st_size == b.st_size;
}
inline void Field(std::string& text, const std::string& name, const std::string& value) {
    text += name + "=" + std::to_string(value.size()) + ":" + value + "\n";
    Need(text.size() <= max_record, "journal-record-too-large");
}
inline std::string PlanBytes(const Plan& p) {
    std::string s;
    Field(s, "run", p.run_id); Field(s, "source", p.source_commit);
    Field(s, "bridge", p.bridge_sha256); Field(s, "fixture", p.fixture_manifest_sha256);
    Field(s, "cleanup_inventory", p.cleanup_inventory_sha256);
    Field(s, "provider_contract", p.provider_contract_sha256);
    Field(s, "isolation_contract", p.isolation_contract_sha256);
    Field(s, "completion_contract", p.completion_contract_sha256);
    Field(s, "publication_window_id", p.publication_window_id);
    Field(s, "executable", p.executable); Field(s, "root", p.root); Field(s, "match", p.match);
    Field(s, "timeout_ms", std::to_string(p.timeout_ms));
    for (const auto& image : p.images) { Field(s, "image_name", image.first); Field(s, "image_hash", image.second); }
    return s;
}
inline std::string ObservationBytes(const Observation& o) {
    std::string s;
    Field(s, "pid", std::to_string(o.pid)); Field(s, "start", o.process_start);
    Field(s, "executable", o.executable); Field(s, "bridge", o.bridge_sha256);
    Field(s, "version", o.version); Field(s, "arch", o.arch); Field(s, "build", std::to_string(o.build));
    Field(s, "main_thread", std::to_string(o.main_thread)); Field(s, "unsaved", std::to_string(o.unsaved));
    Field(s, "dirty", std::to_string(o.dirty)); Field(s, "rendering", std::to_string(o.rendering));
    Field(s, "items", std::to_string(o.items)); Field(s, "queued", std::to_string(o.queued));
    Field(s, "revision", std::to_string(o.revision));
    Field(s, "cleanup_observed", std::to_string(o.cleanup.observed));
    Field(s, "cleanup_complete", std::to_string(o.cleanup.complete));
    Field(s, "cleanup_inventory", o.cleanup.inventory_sha256);
    Field(s, "general_plugin_records", std::to_string(o.cleanup.general_plugin_records));
    Field(s, "publication_observed", std::to_string(o.publication.observed));
    Field(s, "publication_complete", std::to_string(o.publication.complete));
    Field(s, "publication_exclusive", std::to_string(o.publication.exclusive));
    Field(s, "publication_contract", o.publication.isolation_contract_sha256);
    Field(s, "publication_window_id", o.publication.window_id);
    Field(s, "publication_lease_epoch", std::to_string(o.publication.lease_epoch));
    Field(s, "active_render_scopes", std::to_string(o.publication.active_render_scopes));
    Field(s, "registry_loading_done", std::to_string(o.publication.registry_loading_done));
    for (const auto& image : o.images) { Field(s, "image_name", image.first); Field(s, "image_hash", image.second); }
    Field(s, "runtime_image_count", std::to_string(o.runtime_images.size()));
    for (const auto& image : o.runtime_images) {
        Field(s, "runtime_image_path", image.path);
        Field(s, "runtime_image_header", std::to_string(image.header));
        Field(s, "runtime_image_slide", std::to_string(image.slide));
    }
    Field(s, "registry_count", std::to_string(o.registry.size()));
    for (const auto& name : o.registry) Field(s, "effect", name);
    return s;
}
} // namespace journal_detail

// Process-crash/replay protection on a local filesystem, NOT a power-loss or
// hostile-same-UID security guarantee. Caller must retain the parent directory.
class DiskJournal {
    struct Entry { std::string bytes; struct stat identity; };
    const std::string path_;
    const pid_t owner_ = ::getpid();
    journal_detail::Fd dir_;
    struct stat identity_ {};
    std::map<std::string, Entry> entries_;
    bool poisoned_ = false;
    void CheckDirectory() const {
        Need(::getpid() == owner_, "journal-inherited-across-fork");
        const auto original = journal_detail::Stat(dir_.get());
        Need(S_ISDIR(original.st_mode) && original.st_uid == ::geteuid() &&
             (original.st_mode & 07777) == 0700, "journal-not-owned-private-directory");
        auto fresh = journal_detail::Directory(path_);
        const auto current = journal_detail::Stat(fresh.get());
        Need(current.st_dev == identity_.st_dev && current.st_ino == identity_.st_ino &&
             original.st_dev == current.st_dev && original.st_ino == current.st_ino,
             "journal-directory-replaced");
    }
    std::set<std::string> NamesOnDisk() const {
        const int fd = ::openat(dir_.get(), ".", journal_detail::directory_flags);
        Need(fd >= 0, "journal-directory-list-open-failed");
        DIR* listing = ::fdopendir(fd);
        if (!listing) { ::close(fd); Need(false, "journal-directory-list-failed"); }
        std::set<std::string> names;
        try {
            for (;;) {
                errno = 0;
                const auto* entry = ::readdir(listing);
                if (!entry) { Need(errno == 0, "journal-directory-read-failed"); break; }
                const std::string name(entry->d_name);
                if (name != "." && name != "..") names.insert(name);
                Need(names.size() <= 6, "journal-unexpected-entries");
            }
        } catch (...) { ::closedir(listing); throw; }
        Need(::closedir(listing) == 0, "journal-directory-close-failed");
        return names;
    }
    void Verify() const {
        CheckDirectory();
        std::set<std::string> expected;
        for (const auto& item : entries_) expected.insert(item.first);
        Need(NamesOnDisk() == expected, "journal-not-empty-or-records-changed");
        for (const auto& item : entries_) {
            journal_detail::Fd fd(::openat(dir_.get(), item.first.c_str(), O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC));
            Need(fd.get() >= 0, "journal-record-open-failed");
            const auto before = journal_detail::Stat(fd.get());
            Need(S_ISREG(before.st_mode) && before.st_nlink == 1 && before.st_uid == ::geteuid() &&
                 (before.st_mode & 07777) == 0600 && journal_detail::Same(before, item.second.identity),
                 "journal-record-identity-changed");
            std::string bytes(item.second.bytes.size(), '\0');
            std::size_t offset = 0;
            while (offset < bytes.size()) {
                const auto n = ::read(fd.get(), bytes.data() + offset, bytes.size() - offset);
                if (n < 0 && errno == EINTR) continue;
                Need(n > 0, "journal-record-read-failed"); offset += static_cast<std::size_t>(n);
            }
            char extra;
            const auto end = ::read(fd.get(), &extra, 1);
            Need(end == 0 && bytes == item.second.bytes &&
                 journal_detail::Same(before, journal_detail::Stat(fd.get())), "journal-record-content-changed");
            Need(fd.close_checked(), "journal-record-close-failed");
        }
    }
public:
    explicit DiskJournal(std::string directory) : path_(std::move(directory)), dir_(journal_detail::Directory(path_)) {
        identity_ = journal_detail::Stat(dir_.get()); CheckDirectory();
    }
    DiskJournal(const DiskJournal&) = delete;
    DiskJournal& operator=(const DiskJournal&) = delete;
    // Called only by the transaction adapter below; fixed names, not arbitrary paths.
    void Append(const std::string& name, const std::string& payload) {
        Need(!poisoned_, "journal-poisoned");
        poisoned_ = true; // any exception consumes this instance; partial files remain
        const bool first = entries_.empty();
        Need((first && name == "claim.txt") || (!first && name != "claim.txt" &&
             (name == "before.txt" || name == "call-started.txt" || name == "native.txt" ||
              name == "after.txt" || name == "result.txt")),
             "journal-invalid-record-order-or-name");
        Need(entries_.find(name) == entries_.end(), "journal-record-already-written");
        Need(payload.size() <= journal_detail::max_record, "journal-record-too-large");
        Verify();
        const auto bytes = "AEHL-RESOURCE-JOURNAL-1\n" + name + "\n" +
                           std::to_string(payload.size()) + "\n" + payload + "\nEND-AEHL-RECORD\n";
        journal_detail::Fd fd(::openat(dir_.get(), name.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600));
        Need(fd.get() >= 0, "journal-record-exists-or-create-failed");
        Need(::fchmod(fd.get(), 0600) == 0, "journal-private-mode-failed");
        std::size_t offset = 0;
        while (offset < bytes.size()) {
            const auto n = ::write(fd.get(), bytes.data() + offset, bytes.size() - offset);
            if (n < 0 && errno == EINTR) continue;
            Need(n > 0, "journal-write-failed"); offset += static_cast<std::size_t>(n);
        }
        Need(::fsync(fd.get()) == 0, "journal-file-sync-failed");
        const auto written = journal_detail::Stat(fd.get());
        Need(fd.close_checked(), "journal-write-close-failed");
        Need(::fsync(dir_.get()) == 0, "journal-directory-sync-failed");
        entries_.emplace(name, Entry{bytes, written});
        Verify();
        poisoned_ = false;
    }
};

// Concrete disk-backed methods for ResourcePassGate::Backend. Native observation,
// fixture verification and FILE/PLUG operations remain abstract and unbound.
class JournaledBackend : public Backend {
    DiskJournal journal_;
    std::string plan_, before_;
    bool claimed_ = false, before_saved_ = false, marked_ = false, native_saved_ = false, after_saved_ = false;
public:
    explicit JournaledBackend(std::string directory) : journal_(std::move(directory)) {}
    void claim(const Plan& p, const Observation& o) final {
        Need(!claimed_, "journal-claim-already-consumed");
        const auto plan = journal_detail::PlanBytes(p), observation = journal_detail::ObservationBytes(o);
        journal_.Append("claim.txt", plan + observation);
        // Keep immutable bindings for subsequent callbacks; no user consent is inferred.
        plan_ = plan; before_ = observation; claimed_ = true;
    }
    void save_observation(const char* name, const Observation& o) final {
        Need(claimed_ && name, "journal-no-owned-claim");
        const std::string label(name), bytes = journal_detail::ObservationBytes(o);
        if (label == "before") {
            Need(!before_saved_ && !marked_ && !native_saved_ && !after_saved_ && bytes == before_, "journal-before-mismatch-or-replay");
            journal_.Append("before.txt", bytes); before_saved_ = true;
        } else {
            Need(label == "after" && !after_saved_, "journal-invalid-observation-or-replay");
            journal_.Append("after.txt", bytes); after_saved_ = true;
        }
    }
    void mark_call_started(const Plan& p, const Observation& o) final {
        Need(claimed_ && before_saved_ && !marked_ && !native_saved_ && !after_saved_ &&
             journal_detail::PlanBytes(p) == plan_, "journal-call-marker-unbound-or-replayed");
        journal_.Append("call-started.txt", plan_ + journal_detail::ObservationBytes(o)); marked_ = true;
    }
    void save_search_result(const SearchResult& result) final {
        Need(claimed_ && before_saved_ && marked_ && !native_saved_ && !after_saved_,
             "journal-native-result-unbound-or-replayed");
        std::string bytes;
        journal_detail::Field(bytes, "scope", "resource-registration");
        journal_detail::Field(bytes, "code", std::to_string(result.code));
        journal_detail::Field(bytes, "errors", std::to_string(result.errors));
        journal_detail::Field(bytes, "cancelled", std::to_string(result.cancelled));
        journal_.Append("native.txt", bytes);
        native_saved_ = true;
    }
    void finish(const Result& r) {
        Need(claimed_ && r.claimed && (r.status == "PASS" || r.status == "FAIL"), "journal-invalid-final-result");
        Need(r.status != "PASS" || (before_saved_ && marked_ && native_saved_ && after_saved_ &&
             r.call_started && r.search_observed && r.postflight_observed &&
             r.cleanup_ok && r.stage == "complete"), "journal-incomplete-pass");
        std::string bytes;
        journal_detail::Field(bytes, "status", r.status); journal_detail::Field(bytes, "stage", r.stage);
        journal_detail::Field(bytes, "reason", r.reason);
        journal_detail::Field(bytes, "claimed", std::to_string(r.claimed));
        journal_detail::Field(bytes, "call_started", std::to_string(r.call_started));
        journal_detail::Field(bytes, "search_observed", std::to_string(r.search_observed));
        journal_detail::Field(bytes, "postflight_observed", std::to_string(r.postflight_observed));
        journal_detail::Field(bytes, "cleanup_ok", std::to_string(r.cleanup_ok));
        journal_.Append("result.txt", bytes);
    }
};
inline Result RunJournaled(const Plan& p, const Approval& a, JournaledBackend& backend) {
    auto result = Run(p, a, backend);
    if (result.claimed) {
        try { backend.finish(result); }
        catch (...) {
            // A successful in-memory decision is insufficient when evidence fails.
            result.status = "FAIL"; result.stage = "evidence";
            result.reason = "final-evidence-not-confirmed";
        }
    }
    return result;
}
} // namespace resource_pass
