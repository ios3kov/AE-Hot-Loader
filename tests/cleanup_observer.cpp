#include "../experiments/ordinary_discovery/CleanupObserver.hpp"
#include <functional>
#include <fstream>
#include <iterator>
#include <iostream>
#include <map>
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <dlfcn.h>
#include <thread>
#endif
using namespace cleanup_observer;
static unsigned cases = 0;
static void Check(bool value) { if (!value) throw std::runtime_error("test-assertion"); }
static void Put(Bytes& b, std::size_t at, Address word, unsigned size = 8) {
    for (unsigned i = 0; i < size; ++i) b.at(at + i) = static_cast<unsigned char>(word >> (8 * i));
}
struct Fake : mapped_memory::Backend {
    Bytes bytes = Bytes(0x5000);
    unsigned queries = 0, copies = 0;
    std::map<Address, unsigned> reads;
    std::function<void(Fake&, Address)> on_copy, on_query;
    mapped_memory::Region mapping{0x1000, 0x5000, 0, 1, 2, 0, 3, 3};
    Fake(unsigned count = 2) {
        Put(bytes, 0, 0x1200); Put(bytes, 0x200, 0x1300); Put(bytes, 0x310, 0x1400);
        Put(bytes, 0x400, 0x1500); Put(bytes, 0x500, 0x00d00bee, 4);
        Put(bytes, 0x510, count, 4); Put(bytes, 0x518, 16, 4);
        for (unsigned i = 0; i < count; ++i) {
            Put(bytes, 0x548 + i * 16, 0x9000 + i * 4); Put(bytes, 0x550 + i * 16, 42 + i);
        }
    }
    mapped_memory::Region query(Address at) override {
        ++queries; if (on_query) on_query(*this, at); return mapping;
    }
    Bytes copy(Address at, std::size_t size) override {
        ++copies; ++reads[at]; if (on_copy) on_copy(*this, at);
        Check(at >= 0x1000 && at - 0x1000 + size <= bytes.size());
        return Bytes(bytes.begin() + (at - 0x1000), bytes.begin() + (at - 0x1000 + size));
    }
};
static void Refuse(const std::function<void(Fake&)>& setup, const char* reason) {
    Fake f; setup(f); Observer observer;
    const auto r = observer.run({0x1000, 0x1100}, f);
    Check(!r.success && r.failure == reason && r.snapshot.frames.empty());
    const auto calls = f.copies;
    Check(observer.run({0x1000, 0x1100}, f).failure == "observer-consumed" && f.copies == calls);
    ++cases;
}
static void Synthetic() {
    for (unsigned count : {0U, 2U, 256U}) {
        Fake f(count); Observer observer; auto r = observer.run({0x1000, 0x1100}, f);
        Check(r.success && r.failure.empty() && r.snapshot.callbacks.size() == count &&
              r.snapshot.general_plugin_records == 0 && r.calls == (count ? 20 : 17) &&
              r.bytes <= mapped_memory::Reader::kBytes && r.reads.size() == r.calls);
        const auto calls = f.copies;
        Check(observer.run({0x1000, 0x1100}, f).failure == "observer-consumed" && f.copies == calls); ++cases;
    }
    for (bool empty : {false, true}) {
        Fake f; Put(f.bytes, 0x100, 0x4000); Put(f.bytes, 0x108, 0x4000 + (empty ? 0 : 2 * 0xb0));
        Observer observer; const auto r = observer.run({0x1000, 0x1100}, f);
        Check(r.success && r.snapshot.general_plugin_records == (empty ? 0U : 2U) && !f.reads.count(0x4000));
        ++cases;
    }
    Refuse([](Fake& f) { Put(f.bytes, 0, 0); }, "observer-invalid-pointer");
    Refuse([](Fake& f) { Put(f.bytes, 0, 0x1201); }, "observer-invalid-pointer");
    Refuse([](Fake& f) { Put(f.bytes, 0x200, 0); }, "observer-invalid-pointer");
    Refuse([](Fake& f) { Put(f.bytes, 0x310, 0); }, "observer-invalid-pointer");
    Refuse([](Fake& f) { Put(f.bytes, 0x400, 0); }, "observer-invalid-pointer");
    Refuse([](Fake& f) { Put(f.bytes, 0x500, 0, 4); }, "observer-list-magic");
    Refuse([](Fake& f) { Put(f.bytes, 0x510, 257, 4); }, "observer-list-count-or-stride");
    Refuse([](Fake& f) { Put(f.bytes, 0x510, UINT32_MAX, 4); }, "observer-list-count-or-stride");
    Refuse([](Fake& f) { Put(f.bytes, 0x518, 8, 4); }, "observer-list-count-or-stride");
    Refuse([](Fake& f) { Put(f.bytes, 0x100, 0x4000); }, "observer-invalid-vector");
    Refuse([](Fake& f) { Put(f.bytes, 0x108, 8); }, "observer-invalid-vector");
    Refuse([](Fake& f) { Put(f.bytes, 0x100, 0x4000); Put(f.bytes, 0x108, 0x4008); }, "observer-invalid-vector");
    Refuse([](Fake& f) { Put(f.bytes, 0x100, 0x4000); Put(f.bytes, 0x108, 0x4000 + 8193 * 0xb0); }, "observer-invalid-vector");
    Refuse([](Fake& f) { Put(f.bytes, 0x548, 0); }, "snapshot-invalid-callback-target");
    Refuse([](Fake& f) { f.on_copy = [](Fake& x, Address at) {
        if (at == 0x1548 && x.reads[at] == 2) Put(x.bytes, 0x550, 99);
    }; }, "observer-bootstrap-changed");
    Refuse([](Fake& f) { f.on_copy = [](Fake& x, Address at) {
        if (at == 0x1548 && x.reads[at] == 3) Put(x.bytes, 0x550, 99);
    }; }, "snapshot-changed-no-retry");
    Refuse([](Fake& f) { f.on_copy = [](Fake& x, Address at) {
        if (at == 0x1000 && x.reads[at] == 2) Put(x.bytes, 0, 0x1210);
    }; }, "observer-global-changed");
    Refuse([](Fake& f) { f.on_query = [](Fake& x, Address) { x.mapping.object_id++; }; }, "mapped-read-region-changed");
    Refuse([](Fake& f) { Put(f.bytes, 0x100, 0x4000); Put(f.bytes, 0x108, 0x40b0);
        f.on_query = [](Fake& x, Address at) { if (at == 0x4000 && x.copies == 20) x.mapping.object_id++; };
    }, "observer-record-mapping-changed");
    Refuse([](Fake& f) { f.on_copy = [](Fake&, Address) { throw std::runtime_error("copy-failed"); }; }, "copy-failed");
    { Fake f; Observer o; Check(o.run({0, 0x1100}, f).failure == "observer-invalid-roots" && f.copies == 0);
      Check(o.run({0x1000, 0x1100}, f).failure == "observer-consumed"); ++cases; }
    { const auto spans = Clip({{0x1000, 8}, {0x1004, 8}, {0x100c, 4}, {0x2000, 8}});
      Check(spans.size() == 2 && spans[0].size == 16 && spans[1].size == 8); ++cases; }
    std::cout << "CLEANUP_OBSERVER_CASES=" << cases << " PASS; callbacks_invoked=0; records_copied=0\n";
}
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
static resident_data_root::Profile Profile(const char* path, Address vm, unsigned size) {
    using namespace resident_data_root;
    const Pin pin{path, {}};
    const auto bytes = [&] { std::ifstream f(path, std::ios::binary); Check(bool(f));
        return Bytes(std::istreambuf_iterator<char>(f), {}); }();
    const Root root{vm, size, "__common"};
    const auto layout = Describe(bytes, "_AEHL_OwnedAnchor", root);
    return {{pin.path, Hash(bytes)}, "_AEHL_OwnedAnchor", root, layout.image.uuid};
}
static void Owned(char** argv) {
    // Test alone loads freshly compiled OWNED providers and initializes own chain.
    const Profiles profiles{Profile(argv[1], std::stoull(argv[2], nullptr, 0), 8),
                            Profile(argv[3], std::stoull(argv[4], nullptr, 0), 16)};
    ResidentObserver absent; Check(!absent.run(profiles).success);
    void* plug = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    void* mee = dlopen(argv[3], RTLD_NOW | RTLD_LOCAL); Check(plug && mee);
    auto* slot = static_cast<Address*>(dlsym(plug, "AEHL_OwnedRoot"));
    auto* vector = static_cast<Address*>(dlsym(mee, "AEHL_OwnedRoot")); Check(slot && vector);
    alignas(8) unsigned char list[0x58]{};
    Bytes raw(sizeof(list)); Put(raw, 0, 0x00d00bee, 4); Put(raw, 0x10, 1, 4); Put(raw, 0x18, 16, 4);
    Put(raw, 0x48, 0x9000); Put(raw, 0x50, 42); std::copy(raw.begin(), raw.end(), list);
    Address list_handle = reinterpret_cast<Address>(list);
    Address sack[3]{0, 0, reinterpret_cast<Address>(&list_handle)};
    Address sack_handle = reinterpret_cast<Address>(sack); *slot = reinterpret_cast<Address>(&sack_handle);
    alignas(8) unsigned char records[0xb0]{};
    vector[0] = reinterpret_cast<Address>(records); vector[1] = vector[0] + sizeof(records);
    const auto images = resident_binding::Snapshot(); ResidentObserver observer;
    const auto r = observer.run(profiles);
    Check(r.success && r.snapshot.callbacks.size() == 1 && r.snapshot.callbacks[0].context == 42 &&
          r.snapshot.general_plugin_records == 1 && r.calls == 20 && images == resident_binding::Snapshot());
    Check(observer.run(profiles).failure == "resident-observer-consumed");
    bool thread_refused = false; std::thread thread([&] { ResidentObserver o; thread_refused = !o.run(profiles).success; });
    thread.join(); Check(thread_refused);
    *slot = 0; ResidentObserver malformed; Check(!malformed.run(profiles).success);
    Check(dlclose(mee) == 0 && dlclose(plug) == 0); // own providers after final use
    std::cout << "OWNED_RESIDENT_OBSERVER PASS; Adobe_calls=0; provider_loads_by_observer=0\n";
}
#endif
int main(int argc, char** argv) {
    try {
        if (argc == 1) Synthetic();
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
        else { Check(argc == 5); Owned(argv); }
#else
        else { (void)argv; Check(false); }
#endif
        return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
