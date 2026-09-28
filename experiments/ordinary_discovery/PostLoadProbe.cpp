#include <CoreFoundation/CoreFoundation.h>
#include <dispatch/dispatch.h>
#include <dlfcn.h>
#include <pthread.h>
#include <unistd.h>

#include <atomic>
#include <cstdio>
#include <cstring>
#include <exception>
#include <stdexcept>
#include <string>
#include <vector>

// Research only: layouts observed in AE 25.6x101 arm64, not SDK types.
// Keep host-owned references alive for this one-shot experiment. Never run
// libc++ destructors on Adobe's private InterfaceRef or allocator objects.
struct RawString {
    void* data;
    size_t size;
    size_t capacity;
};
struct InterfaceRef { void* interface; void* owner; void* control; };
struct RawVector { void* begin; void* end; void* capacity; };
static_assert(sizeof(RawString) == 24 && sizeof(InterfaceRef) == 24);
static_assert(sizeof(RawVector) == 24);

namespace {
constexpr const char* kLoad = "_ZN2ML11LoadPluginsERNSt3__16vectorINS0_12basic_stringItNS0_11char_traitsItEEN7dvacore9allocator12STLAllocatorItEEEENS7_IS9_EEEERKS9_NS_15ModuleOwnershipERKSB_SH_b";
constexpr const char* kGet = "_Z25MEE_GetVideoFilterModulesRNSt3__16vectorIN7dvacore8classref12InterfaceRefIN2ML18IVideoFilterModuleEEENS_9allocatorIS6_EEEE";
constexpr const char* kNotify = "_Z27FLT_NotifyFilterLoadingDoneRKNSt3__16vectorIN7dvacore8classref12InterfaceRefIN2ML18IVideoFilterModuleEEENS_9allocatorIS6_EEEE";
using Load = size_t (*)(RawVector*, const RawString*, unsigned, const RawVector*, const RawVector*, bool);
using Get = void (*)(RawVector*);
using Notify = void (*)(const RawVector*);
std::atomic<bool> started{false};

struct Context {
    std::string root;
    std::string log;
    RawString path{};
    RawVector before{}, after{}, output{};
    std::vector<InterfaceRef> added;
};

size_t Count(const RawVector& v) {
    const auto begin = reinterpret_cast<uintptr_t>(v.begin);
    const auto end = reinterpret_cast<uintptr_t>(v.end);
    const auto capacity = reinterpret_cast<uintptr_t>(v.capacity);
    if (end < begin || capacity < end || (end - begin) % sizeof(InterfaceRef) ||
        (end - begin) / sizeof(InterfaceRef) > 10000) {
        throw std::runtime_error("invalid module vector");
    }
    return (end - begin) / sizeof(InterfaceRef);
}

void Run(void* opaque) {
    auto& c = *static_cast<Context*>(opaque);
    FILE* log = std::fopen(c.log.c_str(), "a");
    if (!log) return;
    std::setvbuf(log, nullptr, _IONBF, 0);
    std::fprintf(log, "pid=%d main=%d build=%s\n", getpid(), pthread_main_np(), AEHL_PROBE_BUILD);
    try {
        auto load = reinterpret_cast<Load>(dlsym(RTLD_DEFAULT, kLoad));
        auto get = reinterpret_cast<Get>(dlsym(RTLD_DEFAULT, kGet));
        auto notify = reinterpret_cast<Notify>(dlsym(RTLD_DEFAULT, kNotify));
        if (!load || !get || !notify || !pthread_main_np())
            throw std::runtime_error("missing symbols or wrong thread");
        get(&c.before);
        const size_t before = Count(c.before);
        std::fprintf(log, "modules_before=%zu\n", before);
        RawVector empty{};
        // Match LoadAEPlugins: empty exclusions and final flag=true.
        const size_t loaded = load(&c.output, &c.path, 1, &empty, &empty, true);
        std::fprintf(log, "loader_return=%zu\n", loaded);
        get(&c.after);
        const size_t after = Count(c.after);
        auto* old = static_cast<InterfaceRef*>(c.before.begin);
        auto* current = static_cast<InterfaceRef*>(c.after.begin);
        for (size_t i = 0; i < after; ++i) {
            bool found = false;
            for (size_t j = 0; j < before; ++j)
                if (current[i].interface == old[j].interface) found = true;
            if (!found) c.added.push_back(current[i]);
        }
        std::fprintf(log, "modules_after=%zu added=%zu\n", after, c.added.size());
        if (c.added.empty()) throw std::runtime_error("no new modules; notification skipped");
        RawVector delta{c.added.data(), c.added.data() + c.added.size(), c.added.data() + c.added.size()};
        std::fprintf(log, "notify_begin\n");
        notify(&delta);
        std::fprintf(log, "notify_returned; registry/apply/render still require verification\n");
    } catch (const std::exception& error) {
        std::fprintf(log, "ERROR %s\n", error.what());
    } catch (...) {
        std::fprintf(log, "ERROR private ABI exception\n");
    }
    std::fclose(log);
}
} // namespace

extern "C" __attribute__((visibility("default")))
int AEHotLoader_PostLoadProbe(const char* root, const char* log) {
    try {
        if (!root || !log || started.load()) return -1;
        CFBundleRef bundle = CFBundleGetMainBundle();
        auto version = CFBundleGetValueForInfoDictionaryKey(bundle, CFSTR("CFBundleShortVersionString"));
        if (!version || CFGetTypeID(version) != CFStringGetTypeID() ||
            !CFEqual(version, CFSTR("25.6.0"))) return -2;
        auto* c = new Context;
        c->root = root;
        c->log = log;
        CFStringRef text = CFStringCreateWithCString(nullptr, root, kCFStringEncodingUTF8);
        if (!text) return -3;
        const size_t length = static_cast<size_t>(CFStringGetLength(text));
        auto* data = new UniChar[length + 1]{};
        CFStringGetCharacters(text, CFRangeMake(0, length), data);
        CFRelease(text);
        c->path = {data, length, (length + 1) | (size_t{1} << 63)};
        if (started.exchange(true)) return -1;
        dispatch_async_f(dispatch_get_main_queue(), c, Run);
        return 0;
    } catch (...) { return -4; }
}
