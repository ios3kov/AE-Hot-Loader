// OWNED test providers sharing a deliberately constructed test-only string ABI.
// Not an Adobe implementation; compile three separate libraries with ROLE=1/2/3.
#include <cstdint>
#include <cstring>
#include <string>
#include <sys/stat.h>
struct OwnedString {
    std::uint16_t* data;
    std::uint64_t size;
    std::uint64_t tag;
    explicit OwnedString(const char* text) : data(nullptr), size(std::strlen(text)), tag(1ULL << 63) {
        data = new std::uint16_t[size + 1];
        for (std::uint64_t i = 0; i <= size; ++i) data[i] = static_cast<unsigned char>(text[i]);
    }
    OwnedString(const OwnedString&) = delete;
    ~OwnedString() { delete[] data; }
};
static_assert(sizeof(OwnedString) == 24, "owned test ABI changed");
#define EXPORTED __attribute__((visibility("default")))
#if ROLE == 1
struct OwnedSpec { std::string path; };
EXPORTED void* Create(const void*) __asm__("__Z8FILE_NewRKNSt3__112basic_stringItNS_11char_traitsItEEN7dvacore9allocator12STLAllocatorItEEEE");
void* Create(const void* p) {
    const auto& s = *static_cast<const OwnedString*>(p); std::string value;
    for (std::uint64_t i = 0; i < s.size; ++i) value += char(s.data[i]);
    return new OwnedSpec{value};
}
EXPORTED bool IsDir(const void*) __asm__("__Z10FILE_IsDirPK9FILE_Spec");
bool IsDir(const void* p) { struct stat st{}; return ::stat(static_cast<const OwnedSpec*>(p)->path.c_str(), &st) == 0 && S_ISDIR(st.st_mode); }
EXPORTED OwnedString Inquire(const void*) __asm__("__Z19FILE_InqUnicodePathPK9FILE_Spec");
OwnedString Inquire(const void* p) { return OwnedString(static_cast<const OwnedSpec*>(p)->path.c_str()); }
EXPORTED int Dispose(void*) __asm__("_FILE_Dispose");
int Dispose(void* p) { delete static_cast<OwnedSpec*>(p); return 0; }
#elif ROLE == 2
EXPORTED OwnedString Produce(const char*) __asm__("__Z20U_AsciiToUTF16StringPKc");
OwnedString Produce(const char* p) { return OwnedString(p); }
#elif ROLE == 3
EXPORTED void Destroy(void*) __asm__("__ZNSt3__112basic_stringItNS_11char_traitsItEEN7dvacore9allocator12STLAllocatorItEEED1Ev");
void Destroy(void* p) { static_cast<OwnedString*>(p)->~OwnedString(); }
#else
#error "Choose one owned test role"
#endif
