// Narrow legacy-API control matching the selected Adobe producer's API family.
// Own files only; no debugger, target getters, foreign memory, or AE execution.
#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>
#include <cstring>
#include <iostream>
#include <stdexcept>

struct Url {
    CFURLRef value;
    explicit Url(const char* path): value(CFURLCreateFromFileSystemRepresentation(
        nullptr,reinterpret_cast<const UInt8*>(path),std::strlen(path),false)) {
        if(!value) throw std::runtime_error("URL_CREATE_FAILED");
    }
    ~Url() { CFRelease(value); }
    Url(const Url&)=delete; Url& operator=(const Url&)=delete;
};
int main(int argc,char** argv) {
    static_assert(sizeof(FSRef)==80,"reviewed FSRef output extent");
    static_assert(sizeof(FSIORefNum)==4,"fork reference is a separate API type");
    static_assert(sizeof(ByteCount)==8,"actual-count output is 64-bit");
    try {
        if(argc!=3) throw std::runtime_error("ARGUMENTS");
        Url a(argv[1]),b(argv[2]); FSRef first{},twin{};
        // These deprecated APIs are probed because the pinned host calls them.
        // Their observed success does not confer a current supported host ABI.
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
        if(!CFURLGetFSRef(a.value,&first) || !CFURLGetFSRef(b.value,&twin))
            throw std::runtime_error("FSREF_CREATE_FAILED");
        FSRef copy=first;
        const OSErr self=FSCompareFSRefs(&first,&copy);
        const OSErr other=FSCompareFSRefs(&first,&twin);
#pragma clang diagnostic pop
        if(self!=noErr || other!=errFSRefsDifferent) throw std::runtime_error("FSREF_IDENTITY_DIFFERS");
        std::cout << "{\"status\":\"OWNED_FSREF_OBSERVED\",\"fsref_bytes\":80,"
            "\"fork_ref_bytes\":4,\"actual_count_bytes\":8,\"copied_ref_equal\":true,"
            "\"same_bytes_file_twin_equal\":false,\"AE_admission\":\"BLOCKED\"}\n";
        return 0;
    } catch(const std::exception& e) { std::cerr << e.what() << '\n'; return 2; }
}
