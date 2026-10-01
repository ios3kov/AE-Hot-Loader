#include "../experiments/ordinary_discovery/CleanupSnapshot.hpp"
#include <functional>
#include <iostream>
#include <string>
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include "../experiments/ordinary_discovery/SelfMemoryRead.hpp"
#endif
using namespace cleanup_snapshot;
static unsigned cases = 0;
static void Check(bool good) { if (!good) throw std::runtime_error("test-assertion"); }
static void Put(Bytes& b, std::size_t p, Address value, unsigned n = 8) {
    for (unsigned i = 0; i < n; ++i) b.at(p + i) = static_cast<unsigned char>(value >> (i * 8));
}
struct Fixture : Reader {
    Bytes memory = Bytes(0x10000, 0);
    Scope scope{0x1000, 0x1100, {{0x1000, 0x10000}}};
    std::size_t calls = 0;
    std::function<void(Fixture&, Address, Bytes&)> hook;
    Fixture() {
        Put(memory, 0, 0x2000); // sack root
        Put(memory, 0x1010, 0x3000); // sack list handle
        Put(memory, 0x2000, 0x4000); // list storage
        Put(memory, 0x3000, 0x00d00bee, 4);
        Put(memory, 0x3010, 2, 4); Put(memory, 0x3018, 16, 4);
        Put(memory, 0x3048, 0x8000); Put(memory, 0x3050, 0xdeadbeef);
        Put(memory, 0x3058, 0x8000); Put(memory, 0x3060, 0xdeadbeef);
    }
    Bytes read(Address address, std::size_t size) override {
        Check(address >= 0x1000 && address - 0x1000 + size <= memory.size());
        ++calls;
        Bytes b(memory.begin() + (address - 0x1000), memory.begin() + (address - 0x1000 + size));
        if (hook) hook(*this, address, b);
        return b;
    }
};
static void Pass(const std::function<void(Fixture&)>& setup,
                 const std::function<void(const Snapshot&)>& verify) {
    Fixture f; setup(f); const auto s = Capture(f.scope, f); verify(s); ++cases;
}
static void Refuse(const std::function<void(Fixture&)>& setup, const char* reason,
                   std::size_t max_calls = 12) {
    Fixture f; setup(f);
    try { (void)Capture(f.scope, f); throw std::logic_error("unexpected-success"); }
    catch (const std::runtime_error& e) { Check(e.what() == std::string(reason)); }
    Check(f.calls <= max_calls); ++cases;
}
int main() {
    Pass([](Fixture&) {}, [](const Snapshot& s) {
        Check(s.callbacks.size() == 2 && s.callbacks[0].target == 0x8000 &&
              s.callbacks[0].context == 0xdeadbeef && s.callbacks[1].target == 0x8000);
        Check(s.general_plugin_records == 0 && s.frames.size() == 6 &&
              s.read_calls == 12 && s.bytes_read == 320);
    });
    Pass([](Fixture& f) { Put(f.memory, 0x3010, 0, 4); }, [](const Snapshot& s) {
        Check(s.callbacks.empty() && s.read_calls == 10 && s.bytes_read == 256);
    });
    Pass([](Fixture& f) { Put(f.memory, 0x100, 0x6000); Put(f.memory, 0x108, 0x6160); },
         [](const Snapshot& s) { Check(s.general_plugin_records == 2); });
    Pass([](Fixture& f) { Put(f.memory, 0x100, 0x6000); Put(f.memory, 0x108, 0x6000); },
         [](const Snapshot& s) { Check(s.general_plugin_records == 0); });
    Pass([](Fixture& f) {
        Put(f.memory, 0x3010, 256, 4);
        for (unsigned i = 0; i < 256; ++i) Put(f.memory, 0x3048 + i * 16, 0x8000);
    }, [](const Snapshot& s) {
        Check(s.callbacks.size() == 256 && s.bytes_read == 8448 && s.read_calls == 12);
    });
    Refuse([](Fixture& f) { f.scope.readable.clear(); }, "snapshot-region-count", 0);
    Refuse([](Fixture& f) { f.scope.readable.assign(17, {0x1000, 8}); }, "snapshot-region-count", 0);
    Refuse([](Fixture& f) { f.scope.readable = {{UINT64_MAX - 7, 16}}; }, "snapshot-address-overflow", 0);
    Refuse([](Fixture& f) { f.scope.readable.push_back({0x2000, 16}); }, "snapshot-overlapping-regions", 0);
    Refuse([](Fixture& f) { f.scope.readable[0].size = 2 * 1024 * 1024 + 1; }, "snapshot-region-budget", 0);
    Refuse([](Fixture& f) {
        f.scope.readable.clear();
        for (unsigned i = 1; i <= 5; ++i) f.scope.readable.push_back({Address(i) * 0x400000, 0x200000});
    }, "snapshot-region-budget", 0);
    Refuse([](Fixture& f) { f.scope.sack_slot = 0x1001; }, "snapshot-root-outside-scope", 0);
    Refuse([](Fixture& f) { f.scope.vector_slot = 0x11000; }, "snapshot-root-outside-scope", 0);
    Refuse([](Fixture& f) { Put(f.memory, 0, 0); }, "snapshot-unavailable-sack", 1);
    Refuse([](Fixture& f) { Put(f.memory, 0, 0x2001); }, "snapshot-unavailable-sack", 1);
    Refuse([](Fixture& f) { Put(f.memory, 0, 0x12000); }, "snapshot-read-outside-scope", 1);
    Refuse([](Fixture& f) { Put(f.memory, 0x1010, 0); }, "snapshot-unavailable-list", 2);
    Refuse([](Fixture& f) { Put(f.memory, 0x2000, 0); }, "snapshot-unavailable-list-header", 3);
    Refuse([](Fixture& f) { Put(f.memory, 0x2000, UINT64_MAX - 7); }, "snapshot-address-overflow", 3);
    Refuse([](Fixture& f) { Put(f.memory, 0x3000, 0, 4); }, "snapshot-list-magic", 4);
    Refuse([](Fixture& f) { Put(f.memory, 0x3010, 0xffffffff, 4); }, "snapshot-list-count-or-stride", 4);
    Refuse([](Fixture& f) { Put(f.memory, 0x3010, 257, 4); }, "snapshot-list-count-or-stride", 4);
    Refuse([](Fixture& f) { Put(f.memory, 0x3018, 8, 4); }, "snapshot-list-count-or-stride", 4);
    Refuse([](Fixture& f) { f.scope.readable = {{0x1000, 0x3048 - 0x1000}}; },
           "snapshot-read-outside-scope", 4);
    Refuse([](Fixture& f) { Put(f.memory, 0x3048, 0); }, "snapshot-invalid-callback-target", 5);
    Refuse([](Fixture& f) { Put(f.memory, 0x3048, 0x8001); }, "snapshot-invalid-callback-target", 5);
    Refuse([](Fixture& f) { Put(f.memory, 0x100, 0x6000); Put(f.memory, 0x108, 0x5ff8); },
           "snapshot-invalid-vector", 6);
    Refuse([](Fixture& f) { Put(f.memory, 0x100, 0x6001); Put(f.memory, 0x108, 0x6001); },
           "snapshot-invalid-vector", 6);
    Refuse([](Fixture& f) { Put(f.memory, 0x100, 0x6000); Put(f.memory, 0x108, 0x6008); },
           "snapshot-invalid-vector", 6);
    Refuse([](Fixture& f) { Put(f.memory, 0x108, 0x10000); }, "snapshot-invalid-vector", 6);
    Refuse([](Fixture& f) { Put(f.memory, 0x100, 0x1000); Put(f.memory, 0x108, 0x1000 + 8193 * 0xb0); },
           "snapshot-invalid-vector", 6);
    Refuse([](Fixture& f) { Put(f.memory, 0x100, 0x12000); Put(f.memory, 0x108, 0x12000); },
           "snapshot-vector-outside-scope", 6);
    Refuse([](Fixture& f) { Put(f.memory, 0x100, 0x10000); Put(f.memory, 0x108, 0x10000 + 32 * 0xb0); },
           "snapshot-vector-outside-scope", 6);
    for (const bool extra : {false, true}) Refuse([extra](Fixture& f) {
        f.hook = [extra](Fixture&, Address, Bytes& b) { if (extra) b.push_back(0); else b.pop_back(); };
    }, "snapshot-short-or-extra-read", 1);
    Refuse([](Fixture& f) {
        f.hook = [](Fixture&, Address, Bytes&) { throw std::runtime_error("owned-reader-failed"); };
    }, "owned-reader-failed", 1);
    // Mutate every captured level on the second pass, without allowing a retry.
    Refuse([](Fixture& f) { f.hook = [](Fixture& x, Address, Bytes& b) {
        if (x.calls == 7) Put(b, 0, 0);
    }; }, "snapshot-unavailable-sack", 7);
    Refuse([](Fixture& f) { f.hook = [](Fixture& x, Address, Bytes& b) {
        if (x.calls == 8) b[0] ^= 1;
    }; }, "snapshot-changed-no-retry");
    Refuse([](Fixture& f) { f.hook = [](Fixture& x, Address, Bytes& b) {
        if (x.calls == 9) Put(b, 0, 0);
    }; }, "snapshot-unavailable-list-header", 9);
    Refuse([](Fixture& f) { f.hook = [](Fixture& x, Address, Bytes& b) {
        if (x.calls == 10) b[1] ^= 1;
    }; }, "snapshot-list-magic", 10);
    Refuse([](Fixture& f) { f.hook = [](Fixture& x, Address, Bytes& b) {
        if (x.calls == 10) b[8] ^= 1;
    }; }, "snapshot-changed-no-retry");
    Refuse([](Fixture& f) { f.hook = [](Fixture& x, Address, Bytes& b) {
        if (x.calls == 11) b[8] ^= 1;
    }; }, "snapshot-changed-no-retry");
    Refuse([](Fixture& f) { f.hook = [](Fixture& x, Address, Bytes& b) {
        if (x.calls == 12) { Put(b, 0, 0x6000); Put(b, 8, 0x60b0); }
    }; }, "snapshot-changed-no-retry");
    Pass([](Fixture& f) { f.hook = [](Fixture& x, Address, Bytes&) {
        x.scope.sack_slot = 0; x.scope.vector_slot = 0; x.scope.readable.clear();
    }; }, [](const Snapshot& s) { Check(s.callbacks.size() == 2 && s.read_calls == 12); });
    std::cout << "CLEANUP_SNAPSHOT_CASES=" << cases << " PASS; host_calls=0\n";
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
    // Test only our own allocated buffer via the previously reviewed self reader.
    Bytes memory(4096);
    const Address base = reinterpret_cast<std::uintptr_t>(memory.data());
    Put(memory, 0, base + 64); Put(memory, 80, base + 128); Put(memory, 128, base + 192);
    Put(memory, 192, 0x00d00bee, 4); Put(memory, 208, 1, 4); Put(memory, 216, 16, 4);
    Put(memory, 264, 0x8000); Put(memory, 272, 0xdeadbeef);
    struct Self : Reader {
        Bytes read(Address address, std::size_t size) override {
            Bytes b(size);
            Need(directory_spec::ReadSelfMemory(reinterpret_cast<const void*>(address), b.data(), size),
                 "owned-self-read-failed");
            return b;
        }
    } self;
    const auto real = Capture({base, base + 32, {{base, memory.size()}}}, self);
    Check(real.callbacks.size() == 1 && real.callbacks[0].context == 0xdeadbeef &&
          real.general_plugin_records == 0);
    Bytes invalid(8);
    Check(!directory_spec::ReadSelfMemory(reinterpret_cast<const void*>(1), invalid.data(), 8));
    std::cout << "OWNED_SELF_SNAPSHOT PASS; foreign_processes=0; Adobe_calls=0\n";
#endif
}
