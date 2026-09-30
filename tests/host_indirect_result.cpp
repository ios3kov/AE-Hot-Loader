// Real arm64 ABI test using ONLY this owned C++ producer. No Adobe libraries.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <new>
#include <stdexcept>

extern "C" void AEHL_Arm64_IndirectResult(const void* callee, const void* argument,
                                          void* result_storage);
namespace {
int constructed = 0, destroyed = 0, unwound = 0;
struct Request { std::size_t count; std::uint64_t seed; bool fail; };
struct DeliberateFailure { int value; };
struct Result {
    std::uint64_t cookie;
    std::size_t count;
    std::uint64_t* owned;
    Result(const Request& q) : cookie(q.seed), count(q.count), owned(new std::uint64_t[q.count]) {
        for (std::size_t i = 0; i < count; ++i) owned[i] = q.seed + i;
        ++constructed;
    }
    Result(const Result&) = delete;
    Result(Result&&) = delete;
    ~Result() { delete[] owned; ++destroyed; }
};
static_assert(sizeof(Result) == 24 && alignof(Result) == 8, "test ABI changed");
__attribute__((noinline)) Result Produce(const void* input) {
    const auto& q = *static_cast<const Request*>(input);
    if (q.fail) throw DeliberateFailure{37};
    return Result(q); // guaranteed C++17 elision into the indirect result
}
struct alignas(16) Storage {
    unsigned char before[16];
    alignas(Result) unsigned char object[sizeof(Result)];
    unsigned char after[16];
};
static_assert(offsetof(Storage, after) == offsetof(Storage, object) + sizeof(Result), "guard gap");
void Need(bool condition) {
    if (!condition) throw std::runtime_error("owned ABI test failed");
}
void Guards(const Storage& s) {
    for (const auto c : s.before) Need(c == 0xa5);
    for (const auto c : s.after) Need(c == 0xa5);
}
void Normal(const Request& q) {
    Storage storage;
    std::memset(&storage, 0xa5, sizeof(storage));
    const auto made = constructed, gone = destroyed;
    AEHL_Arm64_IndirectResult(reinterpret_cast<const void*>(&Produce), &q, storage.object);
    auto* result = std::launder(reinterpret_cast<Result*>(storage.object));
    // This cast is to the actual OWNED producer type, not an Adobe string layout.
    Need(constructed == made + 1 && destroyed == gone);
    try {
        Guards(storage);
        Need(result->cookie == q.seed && result->count == q.count);
        for (std::size_t i = 0; i < result->count; ++i) Need(result->owned[i] == q.seed + i);
    } catch (...) { result->~Result(); throw; }
    result->~Result();
    Guards(storage);
    Need(constructed == destroyed && destroyed == gone + 1);
}
void Exceptional() {
    struct Fence { ~Fence() { ++unwound; } };
    const auto made = constructed, gone = destroyed, fences = unwound;
    Storage storage;
    std::memset(&storage, 0xa5, sizeof(storage));
    const Request q{4, 55, true};
    bool caught = false;
    try {
        Fence fence;
        AEHL_Arm64_IndirectResult(reinterpret_cast<const void*>(&Produce), &q, storage.object);
    } catch (const DeliberateFailure& e) { caught = e.value == 37; }
    Need(caught && unwound == fences + 1 && constructed == made && destroyed == gone);
    Guards(storage);
    for (const auto c : storage.object) Need(c == 0xa5);
    // A failed construction has no object to destroy; no destructor/retry here.
}
void Case(const char* name, void (*test)()) {
    test(); std::printf("PASS %s\n", name);
}
} // namespace
int main() {
    try {
        Case("indirect-result-and-argument", [] { Normal({4, 0x123456789abcdef0ULL, false}); });
        Case("empty-owned-result", [] { Normal({0, 11, false}); });
        Case("larger-owned-result", [] { Normal({64, 0xf001, false}); });
        Case("repeated-explicit-destruction", [] {
            for (unsigned i = 0; i < 64; ++i) Normal({i, i * 17, false});
        });
        Case("exception-through-tail-transfer", Exceptional);
        Case("subsequent-owned-call-after-exception", [] { Normal({3, 0xdead, false}); });
        Need(constructed == destroyed);
        std::printf("6/6 OWNED ABI CASES PASS; Adobe calls=0\n");
        return 0;
    } catch (...) { std::fprintf(stderr, "FAIL owned ABI test\n"); return 1; }
}
