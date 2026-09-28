#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <set>
#include <string>
#include <vector>

namespace {

using ShellReloadFn = int (*)(char*, std::size_t);
using ShellAbiFn = std::uint32_t (*)();
using ShellKeyFn = int (*)(char*, std::size_t);

constexpr std::uint32_t kShellAbi = 1;

struct ShellRecord {
    void* handle = nullptr;
    std::string image;
    std::string key;
    ShellReloadFn reload = nullptr;
};

void Log(const std::string& message) {
    if (FILE* f = std::fopen("/tmp/ae-hot-loader-shell-reloader.log", "a")) {
        std::fprintf(f, "%s\n", message.c_str());
        std::fclose(f);
    }
}

void CopyMessage(char* output, std::size_t capacity, const std::string& message) {
    if (!output || capacity == 0) {
        return;
    }
    std::snprintf(output, capacity, "%s", message.c_str());
}

bool IsPluginMainImage(const char* image_name) {
    return image_name &&
           std::strstr(image_name, ".plugin/Contents/MacOS/") != nullptr;
}

void CloseRecords(std::vector<ShellRecord>& records) {
    for (auto& record : records) {
        if (record.handle) {
            dlclose(record.handle);
            record.handle = nullptr;
        }
    }
}

std::string BuildSummary(
    int discovered,
    int reloaded,
    int unchanged,
    int failed,
    const std::vector<std::string>& details) {

    std::string summary =
        "shells=" + std::to_string(discovered) +
        " reloaded=" + std::to_string(reloaded) +
        " unchanged=" + std::to_string(unchanged) +
        " failed=" + std::to_string(failed);

    if (!details.empty()) {
        summary += "; ";
        for (std::size_t i = 0; i < details.size() && i < 3; ++i) {
            if (i != 0) {
                summary += " | ";
            }
            summary += details[i];
        }
        if (details.size() > 3) {
            summary += " | ...";
        }
    }
    return summary;
}

}  // namespace

extern "C" int AEHotLoader_ReloadShells(char* output, std::size_t output_capacity) {
    try {
        int discovered = 0;
        int reloaded = 0;
        int unchanged = 0;
        int failed = 0;
        std::vector<std::string> details;
        std::vector<ShellRecord> records;
        std::set<std::string> keys;

        // Phase 1: discover and validate every hot-loader shell. No reload is
        // allowed until the complete loaded set has passed ABI/key validation.
        const std::uint32_t count = _dyld_image_count();
        for (std::uint32_t i = 0; i < count; ++i) {
            const char* image_name = _dyld_get_image_name(i);
            if (!IsPluginMainImage(image_name)) {
                continue;
            }

            void* handle = dlopen(image_name, RTLD_NOW | RTLD_NOLOAD);
            if (!handle) {
                continue;
            }

            auto reload = reinterpret_cast<ShellReloadFn>(
                dlsym(handle, "AEHotLoader_ShellReload"));
            if (!reload) {
                dlclose(handle);
                continue;
            }

            ++discovered;

            auto shell_abi = reinterpret_cast<ShellAbiFn>(
                dlsym(handle, "AEHotLoader_ShellABI"));
            auto shell_key = reinterpret_cast<ShellKeyFn>(
                dlsym(handle, "AEHotLoader_ShellKey"));

            if (!shell_abi || !shell_key || shell_abi() != kShellAbi) {
                ++failed;
                details.push_back(
                    std::string(image_name) +
                    " => incompatible or missing AE Hot Loader shell ABI");
                dlclose(handle);
                continue;
            }

            char key_buffer[256]{};
            const int key_result = shell_key(key_buffer, sizeof(key_buffer));
            const auto* terminator = static_cast<const char*>(
                std::memchr(key_buffer, '\0', sizeof(key_buffer)));
            if (key_result != 0 || !terminator || key_buffer[0] == '\0') {
                ++failed;
                details.push_back(
                    std::string(image_name) +
                    " => invalid AE Hot Loader shell key");
                dlclose(handle);
                continue;
            }

            std::string key(
                key_buffer,
                static_cast<std::size_t>(terminator - key_buffer));

            if (!keys.insert(key).second) {
                ++failed;
                details.push_back(
                    std::string(image_name) +
                    " => duplicate AE Hot Loader shell key: " + key);
                dlclose(handle);
                continue;
            }

            records.push_back(ShellRecord{
                handle,
                image_name,
                key,
                reload,
            });
        }

        if (discovered == 0) {
            const std::string summary =
                BuildSummary(0, 0, 0, 1, {"no compatible hot-loader shells loaded"});
            Log(summary);
            CopyMessage(output, output_capacity, summary);
            return -4202;
        }

        if (failed > 0) {
            CloseRecords(records);
            const std::string summary =
                BuildSummary(discovered, 0, 0, failed, details);
            Log(summary);
            CopyMessage(output, output_capacity, summary);
            return -4203;
        }

        // Phase 2: only a fully validated, duplicate-free shell set may reload.
        for (auto& record : records) {
            char shell_message[768]{};
            const int result = record.reload(shell_message, sizeof(shell_message));

            std::string detail =
                record.key + " @ " + record.image + " => " +
                (shell_message[0] ? shell_message : "(no message)");
            details.push_back(detail);

            if (result == 0) {
                ++reloaded;
            } else if (result == 1) {
                ++unchanged;
            } else {
                ++failed;
            }
        }

        CloseRecords(records);

        const std::string summary =
            BuildSummary(discovered, reloaded, unchanged, failed, details);
        Log(summary);
        CopyMessage(output, output_capacity, summary);

        if (failed > 0) {
            return -4201;
        }
        if (reloaded == 0) {
            return 1;
        }
        return 0;
    } catch (...) {
        if (output && output_capacity > 0) {
            std::snprintf(
                output,
                output_capacity,
                "%s",
                "Unhandled shell reloader exception.");
        }
        return -4299;
    }
}
