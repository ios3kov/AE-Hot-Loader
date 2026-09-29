// Standalone public-API experiment. Header-only callback, NOT a PiPL parser.
#include <Carbon/Carbon.h>
#include <CoreFoundation/CoreFoundation.h>
#include <cstdint>
#include <cstdio>
#include <cstring>

struct Counts { unsigned fromDisk = 0; unsigned toDisk = 0; };

static OSStatus flipHeader(OSType domain, OSType type, SInt16 id, void* data,
                          ByteCount size, Boolean native, void* context) {
    if (domain != kCoreEndianResourceManagerDomain || type != 'PiPL' ||
        id != 16000 || !data || size < 8 || size > 1024 * 1024 || !context)
        return paramErr;
    std::uint32_t header[2];
    std::memcpy(header, data, sizeof(header));
    const auto count = native ? header[1] : CFSwapInt32BigToHost(header[1]);
    if (count != 12) return paramErr; // This exact synthetic fixture only.
    auto& calls = *static_cast<Counts*>(context);
    if (native) ++calls.toDisk; else ++calls.fromDisk;
    for (auto& value : header)
        value = native ? CFSwapInt32HostToBig(value) : CFSwapInt32BigToHost(value);
    std::memcpy(data, header, sizeof(header));
    return noErr;
}

int main(int argc, char** argv) {
    if (argc != 3 || (std::strcmp(argv[2], "baseline") &&
                      std::strcmp(argv[2], "callback"))) return 2;
    const bool enabled = !std::strcmp(argv[2], "callback");
    Counts calls;
    CoreEndianFlipProc old = nullptr;
    void* oldContext = nullptr;
    const auto lookup = CoreEndianGetFlipper(kCoreEndianResourceManagerDomain,
                                            'PiPL', &old, &oldContext);
    if (old || lookup != handlerNotFoundErr) return 2;
    if (enabled && CoreEndianInstallFlipper(kCoreEndianResourceManagerDomain,
                                            'PiPL', flipHeader, &calls) != noErr)
        return 2;
    auto url = CFURLCreateFromFileSystemRepresentation(nullptr,
        reinterpret_cast<const UInt8*>(argv[1]), std::strlen(argv[1]), true);
    if (!url) return 2;
    auto bundle = CFBundleCreate(nullptr, url);
    CFRelease(url);
    if (!bundle) return 2;
    const bool loadedBefore = CFBundleIsExecutableLoaded(bundle);
    const auto saved = CurResFile();
    CFBundleRefNum base = -1, localized = -1;
    const auto opened = CFBundleOpenBundleResourceFiles(bundle, &base, &localized);
    std::uint32_t count = 0;
    bool read = false;
    if (opened == noErr) {
        UseResFile(base);
        auto resource = Get1Resource('PiPL', 16000);
        if (resource) {
            const auto size = GetHandleSize(resource);
            if (size >= 8 && size <= 1024 * 1024) {
                HLock(resource);
                std::memcpy(&count, *resource + 4, sizeof(count));
                HUnlock(resource);
                read = true;
            }
            ReleaseResource(resource);
        }
        UseResFile(saved);
        if (localized != -1 && localized != base)
            CFBundleCloseBundleResourceMap(bundle, localized);
        if (base != -1) CFBundleCloseBundleResourceMap(bundle, base);
    }
    const bool loadedAfter = CFBundleIsExecutableLoaded(bundle);
    const bool pass = read && !loadedBefore && !loadedAfter &&
        (enabled ? (count == 12 && calls.fromDisk > 0) :
                   (count == CFSwapInt32HostToBig(12) && calls.fromDisk == 0));
    std::printf("{\"status\":\"%s\",\"native_count\":%u,"
                "\"from_disk_calls\":%u,\"to_disk_calls\":%u,"
                "\"loaded_before\":%s,\"loaded_after\":%s}\n",
                pass ? "PASS" : "FAIL", count, calls.fromDisk, calls.toDisk,
                loadedBefore ? "true" : "false", loadedAfter ? "true" : "false");
    CFRelease(bundle);
    // Registration is process-local; no host state or disk resource is written.
    return pass ? 0 : 1;
}
