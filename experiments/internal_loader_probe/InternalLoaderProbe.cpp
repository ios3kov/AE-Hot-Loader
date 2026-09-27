#include <CoreFoundation/CoreFoundation.h>
#include <cxxabi.h>
#include <fcntl.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <mach-o/nlist.h>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace {

constexpr const char* kLogPath = "/tmp/ae-hot-loader-internal-probe.log";
constexpr const char* kPluginSupportMarker = "/PluginSupport.framework/";
constexpr const char* kLoadPluginsPrefix = "ML::LoadPlugins(";

struct RawString {
    void* data;
    std::uint64_t size;
    std::uint64_t capacity_flags;
};
static_assert(sizeof(RawString) == 24, "Unexpected RawString size");

struct RawVector {
    void* begin;
    void* end;
    void* capacity_end;
};
static_assert(sizeof(RawVector) == 24, "Unexpected RawVector size");

using LoadPluginsFn = std::size_t (*)(
    RawVector*,
    const RawString*,
    std::uint32_t,
    const RawVector*,
    const RawVector*,
    bool);

void Log(const char* fmt, ...) {
    FILE* f = std::fopen(kLogPath, "a");
    if (!f) return;
    va_list args;
    va_start(args, fmt);
    std::vfprintf(f, fmt, args);
    std::fprintf(f, "\n");
    va_end(args);
    std::fclose(f);
}

bool HostIsAE256() {
    CFBundleRef main = CFBundleGetMainBundle();
    if (!main) return false;
    CFTypeRef value = CFBundleGetValueForInfoDictionaryKey(main, CFSTR("CFBundleShortVersionString"));
    if (!value || CFGetTypeID(value) != CFStringGetTypeID()) return false;
    char buffer[128]{};
    if (!CFStringGetCString(static_cast<CFStringRef>(value), buffer, sizeof(buffer), kCFStringEncodingUTF8)) {
        return false;
    }
    Log("host version=%s", buffer);
    return std::strncmp(buffer, "25.6", 4) == 0;
}

std::uint64_t CapacityFlags(std::size_t chars) {
    std::size_t cap = 16;
    while (cap <= chars) cap *= 2;
    return 0x8000000000000000ULL | static_cast<std::uint64_t>(cap);
}

RawString MakeRawUTF16(const char* utf8) {
    RawString out{};
    if (!utf8) return out;

    CFStringRef str = CFStringCreateWithCString(kCFAllocatorDefault, utf8, kCFStringEncodingUTF8);
    if (!str) return out;

    const CFIndex len = CFStringGetLength(str);
    auto* buffer = static_cast<std::uint16_t*>(std::calloc(static_cast<std::size_t>(len) + 1, sizeof(std::uint16_t)));
    if (!buffer) {
        CFRelease(str);
        return out;
    }

    CFStringGetCharacters(str, CFRangeMake(0, len), reinterpret_cast<UniChar*>(buffer));
    CFRelease(str);

    out.data = buffer;
    out.size = static_cast<std::uint64_t>(len);
    out.capacity_flags = CapacityFlags(static_cast<std::size_t>(len));
    return out;
}

bool ReadWholeFile(const char* path, void** mapped, std::size_t* size) {
    *mapped = nullptr;
    *size = 0;
    const int fd = open(path, O_RDONLY);
    if (fd < 0) return false;

    struct stat st {};
    if (fstat(fd, &st) != 0 || st.st_size <= 0) {
        close(fd);
        return false;
    }

    void* p = mmap(nullptr, static_cast<std::size_t>(st.st_size), PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (p == MAP_FAILED) return false;

    *mapped = p;
    *size = static_cast<std::size_t>(st.st_size);
    return true;
}

void* ResolveLoadPlugins() {
    const std::uint32_t count = _dyld_image_count();

    for (std::uint32_t i = 0; i < count; ++i) {
        const char* image_name = _dyld_get_image_name(i);
        if (!image_name || !std::strstr(image_name, kPluginSupportMarker)) continue;

        const mach_header* header = _dyld_get_image_header(i);
        if (!header || header->magic != MH_MAGIC_64) {
            Log("PluginSupport found but not MH_MAGIC_64");
            return nullptr;
        }

        void* mapped = nullptr;
        std::size_t mapped_size = 0;
        if (!ReadWholeFile(image_name, &mapped, &mapped_size)) {
            Log("failed to mmap PluginSupport: %s", image_name);
            return nullptr;
        }

        const auto* file_header = static_cast<const mach_header_64*>(mapped);
        const auto* cmd = reinterpret_cast<const load_command*>(file_header + 1);
        const symtab_command* symtab = nullptr;

        for (std::uint32_t c = 0; c < file_header->ncmds; ++c) {
            if (reinterpret_cast<const std::uint8_t*>(cmd) + sizeof(load_command) >
                static_cast<const std::uint8_t*>(mapped) + mapped_size) {
                break;
            }
            if (cmd->cmd == LC_SYMTAB) {
                symtab = reinterpret_cast<const symtab_command*>(cmd);
                break;
            }
            cmd = reinterpret_cast<const load_command*>(
                reinterpret_cast<const std::uint8_t*>(cmd) + cmd->cmdsize);
        }

        if (!symtab) {
            Log("PluginSupport has no LC_SYMTAB");
            munmap(mapped, mapped_size);
            return nullptr;
        }

        const std::size_t nlist_bytes = static_cast<std::size_t>(symtab->nsyms) * sizeof(nlist_64);
        if (symtab->symoff + nlist_bytes > mapped_size || symtab->stroff + symtab->strsize > mapped_size) {
            Log("PluginSupport symbol table bounds invalid");
            munmap(mapped, mapped_size);
            return nullptr;
        }

        const auto* symbols = reinterpret_cast<const nlist_64*>(
            static_cast<const std::uint8_t*>(mapped) + symtab->symoff);
        const char* strings = reinterpret_cast<const char*>(
            static_cast<const std::uint8_t*>(mapped) + symtab->stroff);

        const std::intptr_t slide = _dyld_get_image_vmaddr_slide(i);

        for (std::uint32_t s = 0; s < symtab->nsyms; ++s) {
            const auto& symbol = symbols[s];
            if (symbol.n_un.n_strx == 0 || symbol.n_un.n_strx >= symtab->strsize || symbol.n_value == 0) continue;

            const char* raw_name = strings + symbol.n_un.n_strx;
            if (!raw_name || !*raw_name) continue;

            const char* mangled = raw_name[0] == '_' ? raw_name + 1 : raw_name;
            int status = 0;
            char* demangled = abi::__cxa_demangle(mangled, nullptr, nullptr, &status);
            if (status != 0 || !demangled) {
                std::free(demangled);
                continue;
            }

            const bool match = std::strncmp(
                demangled,
                kLoadPluginsPrefix,
                std::strlen(kLoadPluginsPrefix)) == 0;

            if (match) {
                void* address = reinterpret_cast<void*>(
                    static_cast<std::uintptr_t>(slide) + static_cast<std::uintptr_t>(symbol.n_value));
                Log("resolved %s at %p", demangled, address);
                std::free(demangled);
                munmap(mapped, mapped_size);
                return address;
            }

            std::free(demangled);
        }

        Log("ML::LoadPlugins symbol not found in %s", image_name);
        munmap(mapped, mapped_size);
        return nullptr;
    }

    Log("PluginSupport.framework not loaded");
    return nullptr;
}

int RunProbe(const char* utf8_folder) {
#if !defined(__aarch64__)
    Log("refusing: non-arm64 build");
    return -100;
#endif

    if (!pthread_main_np()) {
        Log("refusing: must run on main thread");
        return -101;
    }

    if (!HostIsAE256()) {
        Log("refusing: host is not After Effects 25.6.x");
        return -102;
    }

    if (!utf8_folder || !*utf8_folder) {
        Log("refusing: empty folder path");
        return -103;
    }

    void* raw_fn = ResolveLoadPlugins();
    if (!raw_fn) return -104;

    const auto fn = reinterpret_cast<LoadPluginsFn>(raw_fn);

    RawVector output{};
    RawString root = MakeRawUTF16(utf8_folder);
    RawString player_media_core = MakeRawUTF16("PlayerMediaCore");
    if (!root.data || !player_media_core.data) {
        Log("failed to build ABI strings");
        return -105;
    }

    RawVector x3{
        &player_media_core,
        reinterpret_cast<void*>(reinterpret_cast<std::uintptr_t>(&player_media_core) + sizeof(RawString)),
        reinterpret_cast<void*>(reinterpret_cast<std::uintptr_t>(&player_media_core) + sizeof(RawString))
    };
    RawVector x4{};

    Log("calling ML::LoadPlugins root=%s fn=%p", utf8_folder, raw_fn);
    const std::size_t result = fn(&output, &root, 1u, &x3, &x4, false);
    Log("ML::LoadPlugins returned=%zu output=[%p,%p,%p]",
        result, output.begin, output.end, output.capacity_end);

    // Deliberately do not destroy/free the ABI shim objects after the call.
    // This is an isolated one-shot research probe; leaking a few bytes is safer
    // than mixing std::allocator with Adobe's private dvacore allocator.

    return static_cast<int>(result);
}

}  // namespace

extern "C" __attribute__((visibility("default")))
int AEHotLoader_InternalLoaderProbe(const char* utf8_folder) {
    return RunProbe(utf8_folder);
}
