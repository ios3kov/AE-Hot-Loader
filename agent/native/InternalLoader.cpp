#include <CoreFoundation/CoreFoundation.h>
#include <cxxabi.h>
#include <fcntl.h>
#include <libkern/OSByteOrder.h>
#include <mach-o/dyld.h>
#include <mach-o/fat.h>
#include <mach-o/loader.h>
#include <mach-o/nlist.h>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include <atomic>
#include <climits>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dispatch/dispatch.h>
#include <dlfcn.h>

namespace {

constexpr const char* kLogPath = "/tmp/ae-hot-loader-agent.log";
constexpr const char* kPluginSupportMarker = "/PluginSupport.framework/";
constexpr const char* kLoadPluginsPrefix = "ML::LoadPlugins(";
std::atomic<std::uint64_t> gLoadGeneration{0};

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
    if (!f) {
        return;
    }

    va_list args;
    va_start(args, fmt);
    std::vfprintf(f, fmt, args);
    std::fprintf(f, "\n");
    va_end(args);
    std::fclose(f);
}

bool HostIsAE256() {
    CFBundleRef main = CFBundleGetMainBundle();
    if (!main) {
        return false;
    }

    CFTypeRef value = CFBundleGetValueForInfoDictionaryKey(
        main,
        CFSTR("CFBundleShortVersionString"));
    if (!value || CFGetTypeID(value) != CFStringGetTypeID()) {
        return false;
    }

    char buffer[128]{};
    if (!CFStringGetCString(
            static_cast<CFStringRef>(value),
            buffer,
            sizeof(buffer),
            kCFStringEncodingUTF8)) {
        return false;
    }

    Log("internal-loader: host version=%s", buffer);
    return std::strncmp(buffer, "25.6", 4) == 0;
}

std::uint64_t CapacityFlags(std::size_t chars) {
    std::size_t cap = 16;
    while (cap <= chars) {
        cap *= 2;
    }

    return 0x8000000000000000ULL | static_cast<std::uint64_t>(cap);
}

RawString MakeRawUTF16(const char* utf8) {
    RawString out{};
    if (!utf8) {
        return out;
    }

    CFStringRef str = CFStringCreateWithCString(
        kCFAllocatorDefault,
        utf8,
        kCFStringEncodingUTF8);
    if (!str) {
        return out;
    }

    const CFIndex len = CFStringGetLength(str);
    const std::uint64_t capacity_flags = CapacityFlags(static_cast<std::size_t>(len));
    const std::size_t capacity = static_cast<std::size_t>(
        capacity_flags & ~0x8000000000000000ULL);

    auto* buffer = static_cast<std::uint16_t*>(
        std::calloc(capacity, sizeof(std::uint16_t)));
    if (!buffer) {
        CFRelease(str);
        return out;
    }

    CFStringGetCharacters(
        str,
        CFRangeMake(0, len),
        reinterpret_cast<UniChar*>(buffer));
    CFRelease(str);

    out.data = buffer;
    out.size = static_cast<std::uint64_t>(len);
    out.capacity_flags = capacity_flags;
    return out;
}

bool ReadWholeFile(const char* path, void** mapped, std::size_t* size) {
    *mapped = nullptr;
    *size = 0;

    const int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return false;
    }

    struct stat st {};
    if (fstat(fd, &st) != 0 || st.st_size <= 0) {
        close(fd);
        return false;
    }

    void* p = mmap(
        nullptr,
        static_cast<std::size_t>(st.st_size),
        PROT_READ,
        MAP_PRIVATE,
        fd,
        0);
    close(fd);

    if (p == MAP_FAILED) {
        return false;
    }

    *mapped = p;
    *size = static_cast<std::size_t>(st.st_size);
    return true;
}

const mach_header_64* FindArm64Slice(const void* mapped, std::size_t mapped_size) {
    if (mapped_size < sizeof(std::uint32_t)) {
        return nullptr;
    }

    const auto* bytes = static_cast<const std::uint8_t*>(mapped);
    const std::uint32_t magic = *reinterpret_cast<const std::uint32_t*>(bytes);

    if (magic == MH_MAGIC_64) {
        if (mapped_size < sizeof(mach_header_64)) {
            return nullptr;
        }
        return reinterpret_cast<const mach_header_64*>(bytes);
    }

    if (magic != FAT_CIGAM && magic != FAT_MAGIC) {
        return nullptr;
    }
    if (mapped_size < sizeof(fat_header)) {
        return nullptr;
    }

    const auto* fh = reinterpret_cast<const fat_header*>(bytes);
    const bool swapped = (magic == FAT_CIGAM);
    const std::uint32_t nfat =
        swapped ? OSSwapInt32(fh->nfat_arch) : fh->nfat_arch;

    const std::size_t table_bytes =
        sizeof(fat_header) + static_cast<std::size_t>(nfat) * sizeof(fat_arch);
    if (table_bytes > mapped_size) {
        return nullptr;
    }

    const auto* arch =
        reinterpret_cast<const fat_arch*>(bytes + sizeof(fat_header));

    for (std::uint32_t i = 0; i < nfat; ++i) {
        const std::uint32_t raw_cpu =
            static_cast<std::uint32_t>(arch[i].cputype);
        const cpu_type_t cpu = static_cast<cpu_type_t>(
            swapped ? OSSwapInt32(raw_cpu) : raw_cpu);
        if (cpu != CPU_TYPE_ARM64) {
            continue;
        }

        const std::uint32_t off =
            swapped ? OSSwapInt32(arch[i].offset) : arch[i].offset;
        if (off > mapped_size ||
            mapped_size - off < sizeof(mach_header_64)) {
            return nullptr;
        }

        const auto* slice =
            reinterpret_cast<const mach_header_64*>(bytes + off);
        return slice->magic == MH_MAGIC_64 ? slice : nullptr;
    }

    return nullptr;
}

void* ResolveLoadPlugins() {
    const std::uint32_t count = _dyld_image_count();

    for (std::uint32_t i = 0; i < count; ++i) {
        const char* image_name = _dyld_get_image_name(i);
        if (!image_name ||
            !std::strstr(image_name, kPluginSupportMarker)) {
            continue;
        }

        const mach_header* header = _dyld_get_image_header(i);
        if (!header || header->magic != MH_MAGIC_64) {
            Log("internal-loader: PluginSupport is not MH_MAGIC_64");
            return nullptr;
        }

        void* mapped = nullptr;
        std::size_t mapped_size = 0;
        if (!ReadWholeFile(image_name, &mapped, &mapped_size)) {
            Log("internal-loader: failed to mmap %s", image_name);
            return nullptr;
        }

        const auto* file_header = FindArm64Slice(mapped, mapped_size);
        if (!file_header) {
            Log("internal-loader: arm64 slice not found");
            munmap(mapped, mapped_size);
            return nullptr;
        }

        const auto* file_bytes =
            reinterpret_cast<const std::uint8_t*>(file_header);
        const auto* cmd =
            reinterpret_cast<const load_command*>(file_header + 1);
        const symtab_command* symtab = nullptr;

        for (std::uint32_t c = 0; c < file_header->ncmds; ++c) {
            if (cmd->cmd == LC_SYMTAB) {
                symtab = reinterpret_cast<const symtab_command*>(cmd);
                break;
            }

            cmd = reinterpret_cast<const load_command*>(
                reinterpret_cast<const std::uint8_t*>(cmd) + cmd->cmdsize);
        }

        if (!symtab) {
            Log("internal-loader: LC_SYMTAB missing");
            munmap(mapped, mapped_size);
            return nullptr;
        }

        const std::size_t nlist_bytes =
            static_cast<std::size_t>(symtab->nsyms) * sizeof(nlist_64);
        if (symtab->symoff + nlist_bytes > mapped_size ||
            symtab->stroff + symtab->strsize > mapped_size) {
            Log("internal-loader: symbol table bounds invalid");
            munmap(mapped, mapped_size);
            return nullptr;
        }

        const auto* symbols =
            reinterpret_cast<const nlist_64*>(file_bytes + symtab->symoff);
        const char* strings =
            reinterpret_cast<const char*>(file_bytes + symtab->stroff);
        const std::intptr_t slide = _dyld_get_image_vmaddr_slide(i);

        for (std::uint32_t s = 0; s < symtab->nsyms; ++s) {
            const auto& symbol = symbols[s];
            if (symbol.n_un.n_strx == 0 ||
                symbol.n_un.n_strx >= symtab->strsize ||
                symbol.n_value == 0) {
                continue;
            }

            const char* raw_name = strings + symbol.n_un.n_strx;
            if (!raw_name || !*raw_name) {
                continue;
            }

            const char* mangled =
                raw_name[0] == '_' ? raw_name + 1 : raw_name;
            int status = 0;
            char* demangled =
                abi::__cxa_demangle(mangled, nullptr, nullptr, &status);
            if (status != 0 || !demangled) {
                std::free(demangled);
                continue;
            }

            const bool match =
                std::strncmp(
                    demangled,
                    kLoadPluginsPrefix,
                    std::strlen(kLoadPluginsPrefix)) == 0;

            if (match) {
                void* address = reinterpret_cast<void*>(
                    static_cast<std::uintptr_t>(slide) +
                    static_cast<std::uintptr_t>(symbol.n_value));
                Log("internal-loader: resolved %s at %p", demangled, address);
                std::free(demangled);
                munmap(mapped, mapped_size);
                return address;
            }

            std::free(demangled);
        }

        Log("internal-loader: ML::LoadPlugins not found in %s", image_name);
        munmap(mapped, mapped_size);
        return nullptr;
    }

    Log("internal-loader: PluginSupport.framework not loaded");
    return nullptr;
}


void DiagnoseLoadedBundles(const char* root) {
    if (!root || !*root) {
        return;
    }

    const std::size_t root_len = std::strlen(root);
    const std::uint32_t count = _dyld_image_count();
    int matched = 0;

    for (std::uint32_t i = 0; i < count; ++i) {
        const char* image_name = _dyld_get_image_name(i);
        if (!image_name) {
            continue;
        }

        if (std::strncmp(image_name, root, root_len) != 0) {
            continue;
        }

        ++matched;
        void* handle = dlopen(image_name, RTLD_NOW | RTLD_NOLOAD);
        void* plugin_data = nullptr;
        void* effect_main = nullptr;
        if (handle) {
            plugin_data = dlsym(handle, "PluginDataEntryFunction2");
            effect_main = dlsym(handle, "EffectMain");
            dlclose(handle);
        }

        Log(
            "internal-loader: dyld image=%s PluginDataEntryFunction2=%p EffectMain=%p",
            image_name,
            plugin_data,
            effect_main);
    }

    Log(
        "internal-loader: dyld root=%s matched_images=%d",
        root,
        matched);
}

int LoadPluginFolder(const char* utf8_folder) {
#if !defined(__aarch64__)
    Log("internal-loader: refusing non-arm64 build");
    return -3001;
#endif

    if (!pthread_main_np()) {
        Log("internal-loader: refusing off-main-thread call");
        return -3002;
    }

    if (!HostIsAE256()) {
        Log("internal-loader: unsupported AE version");
        return -3003;
    }

    if (!utf8_folder || !*utf8_folder) {
        Log("internal-loader: empty folder");
        return -3004;
    }

    char resolved_folder[PATH_MAX]{};
    if (!realpath(utf8_folder, resolved_folder)) {
        Log("internal-loader: realpath failed for %s", utf8_folder);
        return -3005;
    }

    struct stat folder_stat {};
    if (stat(resolved_folder, &folder_stat) != 0 ||
        !S_ISDIR(folder_stat.st_mode)) {
        Log("internal-loader: not a directory: %s", resolved_folder);
        return -3006;
    }

    void* raw_fn = ResolveLoadPlugins();
    if (!raw_fn) {
        return -3007;
    }

    const auto fn = reinterpret_cast<LoadPluginsFn>(raw_fn);

    RawVector output{};
    RawString root = MakeRawUTF16(resolved_folder);
    RawString player_media_core = MakeRawUTF16("PlayerMediaCore");
    if (!root.data || !player_media_core.data) {
        std::free(root.data);
        std::free(player_media_core.data);
        Log("internal-loader: failed to build ABI strings");
        return -3008;
    }

    RawVector filters{
        &player_media_core,
        reinterpret_cast<void*>(
            reinterpret_cast<std::uintptr_t>(&player_media_core) +
            sizeof(RawString)),
        reinterpret_cast<void*>(
            reinterpret_cast<std::uintptr_t>(&player_media_core) +
            sizeof(RawString))};
    RawVector extra{};

    Log(
        "internal-loader: calling ML::LoadPlugins root=%s fn=%p",
        resolved_folder,
        raw_fn);

    const std::size_t result =
        fn(&output, &root, 1u, &filters, &extra, false);

    Log(
        "internal-loader: returned=%zu output=[%p,%p,%p]",
        result,
        output.begin,
        output.end,
        output.capacity_end);

    DiagnoseLoadedBundles(resolved_folder);

    // Intentionally keep the private-ABI string storage alive after ML::LoadPlugins.
    // The successful isolated LLDB probe does the same. AE may retain references
    // to this dvacore-compatible storage beyond the immediate call.
    if (result > static_cast<std::size_t>(INT_MAX)) {
        return -3009;
    }

    return static_cast<int>(result);
}

void QueueLoadCallback(void* context) {
    auto* folder = static_cast<char*>(context);
    if (!folder) {
        return;
    }

    Log("internal-loader: async begin root=%s", folder);
    const int result = LoadPluginFolder(folder);
    Log("internal-loader: async end root=%s result=%d", folder, result);
    const auto generation = gLoadGeneration.fetch_add(1, std::memory_order_release) + 1;
    Log("internal-loader: generation=%llu", static_cast<unsigned long long>(generation));
    std::free(folder);
}

}  // namespace

extern "C" int AEHotLoader_LoadPluginFolder(const char* utf8_folder) {
    const int result = LoadPluginFolder(utf8_folder);
    const auto generation =
        gLoadGeneration.fetch_add(1, std::memory_order_release) + 1;
    Log(
        "internal-loader: sync generation=%llu result=%d",
        static_cast<unsigned long long>(generation),
        result);
    return result;
}

extern "C" unsigned long long AEHotLoader_GetLoadGeneration() {
    return static_cast<unsigned long long>(gLoadGeneration.load(std::memory_order_acquire));
}

extern "C" int AEHotLoader_QueuePluginFolder(const char* utf8_folder) {
    if (!utf8_folder || !*utf8_folder) {
        return -3201;
    }

    char* copy = ::strdup(utf8_folder);
    if (!copy) {
        return -3202;
    }

    Log("internal-loader: queued root=%s", copy);
    dispatch_async_f(dispatch_get_main_queue(), copy, QueueLoadCallback);
    return 0;
}
