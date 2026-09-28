#include <cstddef>
#include <cstring>
#include <dlfcn.h>

// Address lookup uses this hidden function, so it cannot resolve a different
// Agent's interposed export. No AE/private API or filesystem operation occurs.
extern "C" __attribute__((visibility("hidden")))
int AEHotLoader_CopyAgentImagePath(char* output, std::size_t capacity) noexcept {
    if (!output || capacity == 0) return -1;
    output[0] = '\0';
    Dl_info info{};
    if (dladdr(reinterpret_cast<const void*>(&AEHotLoader_CopyAgentImagePath), &info) == 0 ||
        !info.dli_fname) return -3;
    const auto length = std::strlen(info.dli_fname);
    if (length >= capacity) return -2;
    std::memcpy(output, info.dli_fname, length + 1);
    return 0;
}
