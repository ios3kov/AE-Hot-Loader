#include "../experiments/ordinary_discovery/OwnedFactoryAbi.hpp"
#include <memory>
#include <mutex>
#include <cstdlib>
#ifndef AEHL_TEST_VERSION
#define AEHL_TEST_VERSION owned_factory_abi::Version
#endif
namespace {
using Event = void (*)(int) noexcept;
Event event = nullptr;
std::uint64_t created = 0, destroyed = 0, acquired = 0, released = 0;
int malformed = 0;
struct Factory {
    std::uint64_t generation;
    explicit Factory(std::uint64_t g) : generation(g) { ++created; }
    ~Factory() { ++destroyed; if (event) event(1); }
};
std::mutex mutex;
std::weak_ptr<Factory> singleton;
std::shared_ptr<Factory> original;
struct Owner { std::shared_ptr<Factory> factory; };
}
extern "C" std::uint64_t AEHL_OwnedFactoryVersion() noexcept { return AEHL_TEST_VERSION; }
extern "C" owned_factory_abi::Ref AEHL_OwnedFactoryAcquire() noexcept {
    try {
        std::lock_guard<std::mutex> lock(mutex);
        auto factory = singleton.lock(); // NEVER make_shared or replace singleton here
        if (!factory) return {};
        auto* owner = new Owner{factory}; ++acquired;
        return {malformed == 1 ? nullptr : factory.get(), owner,
                malformed == 2 ? 0 : factory->generation};
    } catch (...) { return {}; } // owned ABI defines allocation failure as absent
}
#ifndef AEHL_TEST_MISSING_RELEASE
extern "C" void AEHL_OwnedFactoryRelease(void* opaque) noexcept {
    if (!opaque) std::abort();
    ++released; if (event) event(2);
    delete static_cast<Owner*>(opaque);
}
#endif
extern "C" std::int64_t AEHL_OwnedFactoryValue(void* opaque, std::uint64_t generation) noexcept {
    auto* factory = static_cast<Factory*>(opaque);
    if (!factory || factory->generation != generation) std::abort();
    return 73;
}
// Explicit fixture lifecycle controls; never part of the consumer's ABI.
extern "C" void AEHL_TestSeed() {
    std::lock_guard<std::mutex> lock(mutex);
    original = std::make_shared<Factory>(created + 1); singleton = original;
}
extern "C" void AEHL_TestDropOriginal() noexcept { original.reset(); }
extern "C" std::uint64_t AEHL_TestCount(unsigned i) noexcept {
    const std::uint64_t values[]{created, destroyed, acquired, released};
    return i < 4 ? values[i] : 0;
}
extern "C" void AEHL_TestMalformed(int value) noexcept { malformed = value; }
extern "C" void AEHL_TestEvent(Event value) noexcept { event = value; }
__attribute__((destructor)) static void OnUnload() { if (event) event(3); }
