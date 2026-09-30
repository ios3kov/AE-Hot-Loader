// Executable OWNED producer/FILE substitute, never Adobe code or a live AE test.
#include "../experiments/ordinary_discovery/DirectorySpecAdapter.hpp"
#include "../experiments/ordinary_discovery/SelfMemoryRead.hpp"
#include <cstdio>
#include <map>
#include <new>
#include <vector>
#ifdef AEHL_TEST_REAL_ARM64
extern "C" void AEHL_Arm64_IndirectResult(const void*, const void*, void*);
#endif
namespace {
using namespace directory_spec;
struct State {
    std::string mode, path;
    std::vector<std::string> trace;
    std::map<const void*, std::size_t> ranges;
    std::map<const void*, std::uint16_t*> allocations;
    int made = 0, destroyed = 0, new_calls = 0, disposals = 0;
} s;
void Check(bool ok) { if (!ok) throw std::runtime_error("owned adapter test failed"); }
struct alignas(8) OwnedString {
    unsigned char bytes[24]{};
    explicit OwnedString(const std::string& value) {
        if (value.size() <= 10) {
            for (std::size_t i = 0; i < value.size(); ++i) bytes[i * 2] = static_cast<unsigned char>(value[i]);
            bytes[23] = static_cast<unsigned char>(value.size());
        } else {
            auto* data = new std::uint16_t[value.size() + 1]{};
            for (std::size_t i = 0; i < value.size(); ++i) data[i] = static_cast<unsigned char>(value[i]);
            const auto pointer = reinterpret_cast<std::uintptr_t>(data);
            const std::uint64_t size = value.size(), capacity = (1ULL << 63) | (size + 1);
            std::memcpy(bytes, &pointer, 8);
            std::memcpy(bytes + 8, &size, 8);
            std::memcpy(bytes + 16, &capacity, 8);
            s.allocations[this] = data;
            s.ranges[data] = (value.size() + 1) * 2;
        }
        s.ranges[this] = 24;
        ++s.made;
        // Malformed data is ONLY in our own synthetic producer, never an Adobe object.
        if (s.mode == "bad-short") bytes[23] = 11;
        if (s.mode == "bad-size") { const std::uint64_t huge = UINT64_MAX; std::memcpy(bytes + 8, &huge, 8); }
        if (s.mode == "bad-pointer") { const std::uint64_t bad = 2; std::memcpy(bytes, &bad, 8); }
        if (s.mode == "unaligned-pointer") bytes[0] |= 1;
        if (s.mode == "non-ascii-unit") {
            if (value.size() <= 10) bytes[1] = 1; else s.allocations[this][0] = 0x1234;
        }
        if (s.mode == "missing-null") {
            if (value.size() <= 10) bytes[value.size() * 2] = 1;
            else s.allocations[this][value.size()] = 1;
        }
    }
    OwnedString(const OwnedString&) = delete;
    OwnedString(OwnedString&&) = delete;
    ~OwnedString() {
        const auto found = s.allocations.find(this);
        if (found != s.allocations.end()) {
            s.ranges.erase(found->second); delete[] found->second; s.allocations.erase(found);
        }
        s.ranges.erase(this); ++s.destroyed;
    }
};
static_assert(sizeof(OwnedString) == 24 && alignof(OwnedString) == 8, "owned fixture ABI");
struct OwnedSpec { std::string path; };
OwnedString Produce(const void* argument) {
    s.trace.push_back("input");
    if (s.mode == "input-throw") throw 1;
    s.path = static_cast<const char*>(argument);
    return OwnedString(s.mode == "input-mismatch" ? "/different" : s.path);
}
OwnedString Inquire(const void* argument) {
    s.trace.push_back("output");
    if (s.mode == "path-throw") throw 2;
    const auto* spec = static_cast<const OwnedSpec*>(argument);
    return OwnedString(s.mode == "output-mismatch" ? "/different" : spec->path);
}
void Destroy(void* storage) {
    s.trace.push_back("destroy");
    std::launder(reinterpret_cast<OwnedString*>(storage))->~OwnedString();
    if ((s.mode == "input-destroy-throw" && s.destroyed == 1) ||
        (s.mode == "output-destroy-throw" && s.destroyed == 2)) throw 3;
}
void* Create(const void* argument) {
    s.trace.push_back("new"); ++s.new_calls;
    Check(s.ranges.count(argument) == 1 && s.destroyed == 0);
    if (s.mode == "new-throw") throw 4;
    if (s.mode == "new-null") return nullptr;
    return new OwnedSpec{s.path};
}
bool IsDir(const void* argument) {
    s.trace.push_back("isdir"); Check(argument && s.destroyed == 1);
    if (s.mode == "isdir-throw") throw 5;
    return s.mode != "not-directory";
}
int Dispose(void* argument) {
    s.trace.push_back("dispose"); Check(argument != nullptr);
    ++s.disposals; delete static_cast<OwnedSpec*>(argument);
    // Caller cannot know whether a failed release freed the object. No retry.
    if (s.mode == "dispose-throw") throw 6;
    return s.mode == "dispose-error" ? 7 : 0;
}
bool Read(const void* from, void* into, std::size_t bytes) noexcept {
    if (s.mode == "unreadable") return false;
    const auto pos = s.ranges.find(from);
    if (pos == s.ranges.end() || bytes > pos->second) return false;
#ifdef AEHL_TEST_REAL_ARM64
    return directory_spec::ReadSelfMemory(from, into, bytes);
#else
    std::memcpy(into, from, bytes); return true;
#endif
}
void Indirect(const void* function, const void* argument, void* output) {
#ifdef AEHL_TEST_REAL_ARM64
    AEHL_Arm64_IndirectResult(function, argument, output);
#else
    const auto producer = reinterpret_cast<OwnedString(*)(const void*)>(const_cast<void*>(function));
    new (output) OwnedString(producer(argument)); // C++17 guaranteed elision
#endif
}
Functions API() { return {Indirect, reinterpret_cast<const void*>(&Produce),
    reinterpret_cast<const void*>(&Inquire), Destroy, Create, IsDir, Dispose, Read}; }
unsigned cases = 0;
void Trial(const char* name, const char* mode, const std::string& path,
           bool completed, int made, int new_calls, int disposed, bool clean = true) {
    s = State{}; s.mode = mode;
    const auto result = CreateRoundtripRelease(API(), path);
    Check(result.completed == completed && result.cleanup_ok == clean);
    Check(s.made == made && s.destroyed == made && s.new_calls == new_calls && s.disposals == disposed);
    Check(result.strings_created == static_cast<unsigned>(made) &&
          result.string_release_attempts == static_cast<unsigned>(made) &&
          result.spec_release_attempts == static_cast<unsigned>(disposed));
    Check(s.ranges.empty() && s.allocations.empty());
    if (completed) Check(s.trace == std::vector<std::string>{"input", "new", "destroy", "isdir", "output", "destroy", "dispose"});
    ++cases; std::printf("PASS %s\n", name);
}
} // namespace
int main() {
    try {
        const std::string long_path = "/owned/research/empty-directory";
        Trial("short-path", "", "/owned", true, 2, 1, 1);
        Trial("long-path-with-spaces", "", long_path + " with spaces", true, 2, 1, 1);
        Trial("maximum-path", "", "/" + std::string(kMaxPath - 1, 'a'), true, 2, 1, 1);
        Trial("non-ascii-rejected-before-call", "", "/\xd1\x82\xd0\xb5\xd1\x81\xd1\x82", false, 0, 0, 0);
        Trial("too-long-rejected-before-call", "", "/" + std::string(kMaxPath, 'a'), false, 0, 0, 0);
        Trial("traversal-rejected-before-call", "", "/owned/../other", false, 0, 0, 0);
        Trial("embedded-nul-rejected", "", std::string("/owned\0hidden", 13), false, 0, 0, 0);
        Trial("input-constructor-throws", "input-throw", long_path, false, 0, 0, 0);
        Trial("input-mismatch", "input-mismatch", long_path, false, 1, 0, 0);
        Trial("invalid-short-length", "bad-short", "/owned", false, 1, 0, 0);
        Trial("oversized-return-length", "bad-size", long_path, false, 1, 0, 0);
        Trial("unreadable-return-pointer", "bad-pointer", long_path, false, 1, 0, 0);
        Trial("unaligned-return-pointer", "unaligned-pointer", long_path, false, 1, 0, 0);
        Trial("non-ascii-return-unit", "non-ascii-unit", long_path, false, 1, 0, 0);
        Trial("missing-terminator", "missing-null", long_path, false, 1, 0, 0);
        Trial("reader-failure", "unreadable", long_path, false, 1, 0, 0);
        Trial("spec-creation-throws", "new-throw", long_path, false, 1, 1, 0);
        Trial("null-spec-not-disposed", "new-null", long_path, false, 1, 1, 0);
        Trial("input-release-fails-no-retry", "input-destroy-throw", long_path, false, 1, 1, 1, false);
        Trial("not-a-directory", "not-directory", long_path, false, 1, 1, 1);
        Trial("directory-query-throws", "isdir-throw", long_path, false, 1, 1, 1);
        Trial("path-construction-throws", "path-throw", long_path, false, 1, 1, 1);
        Trial("path-roundtrip-mismatch", "output-mismatch", long_path, false, 2, 1, 1);
        Trial("output-release-fails-no-retry", "output-destroy-throw", long_path, false, 2, 1, 1, false);
        Trial("dispose-error-no-retry", "dispose-error", long_path, false, 2, 1, 1, false);
        Trial("dispose-throws-no-retry", "dispose-throw", long_path, false, 2, 1, 1, false);
        s = State{};
        const auto unbound = CreateRoundtripRelease(Functions{}, long_path);
        Check(!unbound.completed && !unbound.invoked && s.trace.empty());
        ++cases; std::puts("PASS unbound-api-inert");
#ifdef AEHL_TEST_REAL_ARM64
        unsigned char output[24]{};
        Check(!ReadSelfMemory(reinterpret_cast<const void*>(2), output, sizeof(output)));
        Check(!ReadSelfMemory(output, output, 8195));
        Check(!ReadSelfMemory(output, output, 0));
        Check(!ReadSelfMemory(nullptr, output, sizeof(output)));
        std::puts("SELF READER invalid-pointer/bounds PASS");
#endif
        std::printf("%u/%u OWNED DIRECTORY CASES PASS; Adobe calls=0\n", cases, cases);
        return 0;
    } catch (...) { std::fputs("FAIL owned directory adapter\n", stderr); return 1; }
}
