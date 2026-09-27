#include <cstddef>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <string>
#include <vector>

namespace {

using ShellReloadFn = int (*)(char*, std::size_t);

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
    if (!image_name) {
        return false;
    }
    return std::strstr(image_name, ".plugin/Contents/MacOS/") != nullptr;
}

}  // namespace

extern "C" int AEHotLoader_ReloadShells(char* output, std::size_t output_capacity) {
    try {
        int discovered = 0;
        int reloaded = 0;
        int unchanged = 0;
        int failed = 0;
        std::vector<std::string> details;

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
            char shell_message[768]{};
            const int result = reload(shell_message, sizeof(shell_message));

            std::string detail = image_name;
            detail += " => ";
            detail += shell_message[0] ? shell_message : "(no message)";
            details.push_back(detail);

            if (result == 0) {
                ++reloaded;
            } else if (result == 1) {
                ++unchanged;
            } else {
                ++failed;
            }

            dlclose(handle);
        }

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

        Log(summary);
        CopyMessage(output, output_capacity, summary);

        if (discovered == 0) {
            return -4202;
        }
        if (failed > 0) {
            return -4201;
        }
        if (reloaded == 0) {
            return 1;
        }
        return 0;
    } catch (...) {
        if (output && output_capacity > 0) {
            std::snprintf(output, output_capacity, "%s", "Unhandled shell reloader exception.");
        }
        return -4299;
    }
}
