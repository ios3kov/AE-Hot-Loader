// Separate inert one-shot name diagnostic; no private Adobe calls or retention.
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "RetainedProbeContract.hpp"
#include "AE256CleanupProfile.hpp"
#include "RetainedIdentityConfig.hpp"
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
#include "RetainedProbeHost.hpp"

extern "C" __attribute__((visibility("default")))
const char* AEHL_RetainedBuildIdentity() { return research_identity; }
namespace {
class LiveBackend final : public retained_transaction::HostJournaledBackend,
                          public retained_probe::BindingBackend {
    const retained_probe::Config config_;
    const std::string binary_;
    retained_probe::Capture capture_;
public:
    LiveBackend(const retained_probe::Config& c, std::string binary)
        : HostJournaledBackend(c.journal), config_(c), binary_(std::move(binary)) {}
    std::uint64_t now_ms() override {
        return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count());
    }
    retained_probe::Binding measure() override {
        Require(pthread_main_np() == 1, "binding off main thread");
        const auto before = resident_binding::Snapshot();
        const auto module = ModulePath();
        Require(module == config_.module && CanonicalExecutable() == config_.executable,
                "measured module/host changed");
        // Final signed SHA comes from the exact request; verify loaded self before using it.
        const auto self = resident_binding::Resolve({module, ae256_cleanup::Decode<32>(binary_)},
                                                   {"_AEHL_RetainedBuildIdentity"});
        Require(self.functions.at("_AEHL_RetainedBuildIdentity") ==
                reinterpret_cast<void*>(&AEHL_RetainedBuildIdentity), "self export address changed");
        const auto root = resident_data_root::Bind(ae256_cleanup::Profile(ae256_cleanup::kMee));
        proc_bsdinfo info{};
        Require(proc_pidinfo(getpid(), PROC_PIDTBSDINFO, 0, &info, sizeof(info)) == sizeof(info),
                "measured process start unavailable");
        retained_probe::Binding out;
        out.scope = {config_.run, config_.source, config_.build, binary_,
            retained_journal::HexBytes(retained_identity::Bytes(root.pin.sha256.begin(), root.pin.sha256.end())),
            retained_journal::HexBytes(retained_identity::Bytes(root.uuid.begin(), root.uuid.end())),
            "ae-diagnostic", static_cast<std::uint64_t>(getpid()), info.pbi_start_tvsec,
            info.pbi_start_tvusec, root.address};
        Require(root.size == 16 && before == resident_binding::Snapshot(), "binding inventory changed");
        for (const auto& image : before) out.images.push_back({image.path, image.header, image.slide});
        return out;
    }
    retained_transaction::Observation observe() override {
        Require(pthread_main_np() == 1, "observation off main thread");
        const auto project = SnapshotProject(); // SDK script validates each state flag below.
        const auto bound = measure();
        retained_transaction::Observation o; o.measured = bound.scope;
        auto& h = o.host;
        h.pid = getpid(); h.process_start = StartIdentity(); h.executable = CanonicalExecutable();
        h.module_path = ModulePath(); h.version = "25.6x101"; h.build = 101; h.arch = "arm64";
        h.main_thread = true; h.unsaved = true; h.dirty = false; h.rendering = false;
        h.items = 0; h.queued = 0; h.revision = project.revision;
        h.registry = project.registry; h.images = bound.images; return o;
    }
    retained_capture::Diagnostic capture(const retained_transaction::Plan& p) override {
        mapped_memory::SelfBackend memory;
        return capture_.run(p, *this, memory);
    }
};
A_Err Idle(AEGP_GlobalRefcon, AEGP_IdleRefcon, A_long* max_sleep) {
    if (consumed) return 0;
    if (max_sleep && *max_sleep > 15) *max_sleep = 15;
    try {
        Require(pthread_main_np() == 1, "idle off main thread");
        const auto& c = research_config;
        PrivateDirectory(c.control);
        if (!ExistsControl(c.control, "request.txt")) return 0;
        consumed = true; // Consume before reading/parsing/request or binding access.
        const auto binary = retained_probe::ApproveRequest(c, getpid(), StartIdentity(),
            ReadControl(c.control, "request.txt", 4096));
        LiveBackend backend(c, binary);
        const retained_transaction::Plan plan{backend.measure().scope,
            c.executable, c.module, c.journal, 15000};
        retained_transaction::Transaction transaction;
        const auto result = transaction.run(plan, {plan, true, true}, backend);
        if (result.status != "PASS")
            SaveControl(c.control, "adapter-stopped.txt", "status=" + result.status + "\nstage=" + result.stage + "\n");
    } catch (...) {
        consumed = true;
        try {
            if (!ExistsControl(research_config.control, "adapter-stopped.txt"))
                SaveControl(research_config.control, "adapter-stopped.txt", "status=FAIL\n");
        } catch (...) {}
    }
    return 0;
}
} // namespace
extern "C" __attribute__((visibility("default")))
A_Err EntryPointFunc(SPBasicSuite* suites, A_long, A_long, AEGP_PluginID id, AEGP_GlobalRefcon*) {
    try {
        const auto& c = research_config;
        if (!suites || Token() != c.token || CanonicalExecutable() != c.executable ||
            ModulePath() != c.module) return 0;
        if (consumed) return 0;
        PrivateDirectory(c.control); PrivateDirectory(c.journal);
        if (ExistsControl(c.control, "ready.txt") || ExistsControl(c.control, "request.txt")) return 0;
        basic = suites; plugin_id = id;
        Suite<AEGP_RegisterSuite5> registration(basic, kAEGPRegisterSuite, kAEGPRegisterSuiteVersion5);
        Require(registration.value->AEGP_RegisterIdleHook(id, Idle, nullptr) == 0, "idle registration failed");
        registration.release_checked();
        SaveControl(c.control, "ready.txt", std::string(research_identity) + "\npid=" +
            std::to_string(getpid()) + "\nimage=" + ModulePath() + "\nstart=" + StartIdentity() + "\n");
    } catch (...) { consumed = true; return 1; }
    return 0;
}
