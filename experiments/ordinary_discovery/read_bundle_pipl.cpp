// Offline resource inspection. Never loads the bundle executable or contacts AE.
#include <CoreFoundation/CoreFoundation.h>
#include <Carbon/Carbon.h>
#include <CommonCrypto/CommonDigest.h>
#include <cstdio>
#include <cstring>

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    auto url = CFURLCreateFromFileSystemRepresentation(nullptr,
        reinterpret_cast<const UInt8*>(argv[1]), std::strlen(argv[1]), true);
    if (!url) return 2;
    auto bundle = CFBundleCreate(nullptr, url);
    CFRelease(url);
    if (!bundle) return 2;
    const bool loadedBefore = CFBundleIsExecutableLoaded(bundle);
    auto urls = CFBundleCopyResourceURLsOfType(bundle, CFSTR("PiPL"), nullptr);
    const auto urlCount = urls ? CFArrayGetCount(urls) : 0;
    if (urls) CFRelease(urls);
    CFBundleRefNum base = -1, localized = -1;
    const auto saved = CurResFile();
    const auto status = CFBundleOpenBundleResourceFiles(bundle, &base, &localized);
    long size = 0;
    char hash[CC_SHA256_DIGEST_LENGTH * 2 + 1] = {};
    if (status == 0) {
        UseResFile(base);
        auto resource = Get1Resource('PiPL', 16000);
        if (resource) {
            size = GetHandleSize(resource);
            if (size > 0 && size <= 1024 * 1024) {
                unsigned char digest[CC_SHA256_DIGEST_LENGTH];
                HLock(resource);
                CC_SHA256(*resource, static_cast<CC_LONG>(size), digest);
                HUnlock(resource);
                for (unsigned i = 0; i < sizeof(digest); ++i)
                    std::snprintf(hash + 2*i, 3, "%02x", digest[i]);
            }
            ReleaseResource(resource);
        }
        UseResFile(saved);
        if (localized != -1 && localized != base)
            CFBundleCloseBundleResourceMap(bundle, localized);
        if (base != -1) CFBundleCloseBundleResourceMap(bundle, base);
    }
    const bool loadedAfter = CFBundleIsExecutableLoaded(bundle);
    const bool pass = status == 0 && hash[0] && !loadedBefore && !loadedAfter;
    std::printf("{\"status\":\"%s\",\"resource_open_status\":%d,"
        "\"pipl_url_count\":%ld,\"resource_bytes\":%ld,\"sha256\":\"%s\","
        "\"executable_loaded_before\":%s,\"executable_loaded_after\":%s}\n",
        pass ? "PASS" : "FAIL", static_cast<int>(status), urlCount, size, hash,
        loadedBefore ? "true" : "false", loadedAfter ? "true" : "false");
    CFRelease(bundle);
    return pass ? 0 : 1;
}
