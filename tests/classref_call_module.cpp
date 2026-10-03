#include <array>
#include <cstdint>
#include <cstddef>
#include <cstdlib>
#include <map>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <type_traits>
#ifndef AEHL_TEST_BRIDGE_VERSION
#define AEHL_TEST_BRIDGE_VERSION 0x4145484c00000002ULL
#endif
namespace {
using Event = void (*)(int) noexcept;
Event event = nullptr;
std::uint64_t created=0, destroyed=0, acquired=0, released=0, destructor_calls=0, true_calls=0;
int mode=0;
struct Factory { std::uint64_t value=73; ~Factory() { ++destroyed; if(event) event(1); } };
struct Block { std::array<unsigned char,24> prefix{}; Factory factory; };
static_assert(offsetof(Block,factory)==24);
std::shared_ptr<Block> original;
std::weak_ptr<Block> singleton;
std::map<const void*,std::shared_ptr<Block>> slots; // owns typed lifetime entirely inside module
std::mutex mutex;
}
namespace aehl_classref_control {
struct Reference {
    void* primary;
    void* unknown;
    void* control;
    explicit Reference(std::shared_ptr<Block> b) : primary(b ? &b->factory : nullptr),
        unknown(primary),control(b.get()) {
        if(b) { slots.emplace(this,std::move(b)); ++acquired; }
        if(mode==1) primary=nullptr;
        if(mode==2 && unknown) unknown=static_cast<unsigned char*>(unknown)+8;
    }
    Reference(const Reference&)=delete;
    Reference(Reference&&)=delete; // guaranteed C++17 prvalue result construction
    ~Reference() noexcept {
        ++destructor_calls;
        const auto it=slots.find(this);
        if(it==slots.end()) { if(control) std::abort(); return; }
        if(it->second.get()!=control) std::abort(); // wrong destructor base/memcpy move is rejected
        ++released; if(event) event(2); slots.erase(it);
    }
};
static_assert(sizeof(Reference)==24 && alignof(Reference)==8 && std::is_standard_layout<Reference>::value);
static_assert(!std::is_trivially_destructible<Reference>::value);
__attribute__((noinline)) Reference Acquire(bool create) {
    if(create) { ++true_calls; throw std::runtime_error("creation-request-forbidden"); }
    std::lock_guard<std::mutex> lock(mutex);
    if(mode==3) throw std::runtime_error("owned-before-construction");
    return Reference(singleton.lock());
}
} // namespace aehl_classref_control
extern "C" std::uint64_t AEHL_ClassRefBridgeVersion() noexcept { return AEHL_TEST_BRIDGE_VERSION; }
#ifndef AEHL_TEST_MISSING_DESTROY
extern "C" void AEHL_ClassRefControlDestroy(void* p) noexcept {
    static_cast<aehl_classref_control::Reference*>(p)->~Reference();
}
#endif
extern "C" void AEHL_TestSeed() { original=std::make_shared<Block>(); ++created; singleton=original; }
extern "C" void AEHL_TestDrop() noexcept { original.reset(); }
extern "C" void AEHL_TestMode(int m) noexcept { mode=m; }
extern "C" std::uint64_t AEHL_TestCount(unsigned n) noexcept {
    const std::uint64_t values[]{created,destroyed,acquired,released,destructor_calls,true_calls,slots.size()};
    return n<7 ? values[n] : 0;
}
extern "C" std::uint64_t AEHL_TestUse(std::uintptr_t slot) noexcept {
    const auto it=slots.find(reinterpret_cast<void*>(slot)); if(it==slots.end()) std::abort();
    return it->second->factory.value;
}
extern "C" void AEHL_TestEvent(Event e) noexcept { event=e; }
__attribute__((destructor)) static void OnUnload() { if(event) event(3); }
