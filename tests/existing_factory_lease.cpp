#include "../experiments/ordinary_discovery/NativeExistingFactoryLease.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <thread>
#include <vector>
using namespace resident_binding;
using owned_factory_lease::Lease;
static std::vector<int> events;
static void Event(int e) noexcept { events.push_back(e); }
template<class F> static void Refuse(F f) {
    bool refused = false; try { f(); } catch (const std::exception&) { refused = true; }
    Require(refused);
}
template<class T> static T Symbol(void* handle, const char* name) {
    auto p = dlsym(handle, name); Require(p); return reinterpret_cast<T>(p);
}
int main(int argc, char** argv) {
    try {
        Require(argc == 3); events.reserve(32);
        std::ifstream f(argv[1], std::ios::binary); Require(bool(f));
        const Bytes bytes(std::istreambuf_iterator<char>(f), {});
        const Pin pin{argv[1], Hash(bytes)};
        const auto uuid = Parse(bytes, {"_AEHL_OwnedFactoryVersion"}).uuid;
        const auto absent = Snapshot(); Refuse([&] { (void)Lease::Acquire(pin, uuid); });
        Require(absent == Snapshot()); // consumer didn't load even a valid owned file
        void* handle = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); Require(handle);
        const auto count = Symbol<std::uint64_t (*)(unsigned) noexcept>(handle, "AEHL_TestCount");
        const auto seed = Symbol<void (*)()>(handle, "AEHL_TestSeed");
        const auto drop = Symbol<void (*)() noexcept>(handle, "AEHL_TestDropOriginal");
        const auto mode = Symbol<void (*)(int) noexcept>(handle, "AEHL_TestMalformed");
        Symbol<void (*)(void (*)(int) noexcept) noexcept>(handle, "AEHL_TestEvent")(Event);
        const std::string runmode = argv[2];
        if (runmode == "--wrong-reset" || runmode == "--wrong-move") {
            seed(); auto owned = Lease::Acquire(pin, uuid);
            std::set_terminate([] { std::_Exit(events.empty() ? 86 : 87); });
            std::thread invalid([&] {
                if (runmode == "--wrong-reset") owned.Reset();
                else { auto moved = std::move(owned); (void)moved; }
            });
            invalid.join(); return 88;
        }
        if (runmode == "--bad") {
            seed(); Refuse([&] { (void)Lease::Acquire(pin, uuid); });
            Require(count(0) == 1 && count(2) == 0 && count(3) == 0);
            drop(); Require(count(1) == 1); Require(dlclose(handle) == 0);
            std::cout << "OWNED_FACTORY_ABI_REFUSAL PASS; acquire_calls=0\n"; return 0;
        }
        Require(runmode == "--good");
        { auto empty = Lease::Acquire(pin, uuid); Require(!empty && count(0) == 0 && count(2) == 0); }
        seed(); Require(count(0) == 1);
        for (unsigned i = 0; i < 3; ++i) {
            auto badpin = pin; auto baduuid = uuid;
            if (i == 0) badpin.sha256[0] ^= 1;
            if (i == 1) baduuid[0] ^= 1;
            if (i == 2) baduuid.fill(0);
            Refuse([&] { (void)Lease::Acquire(badpin, baduuid); });
        }
        bool refused = false;
        std::thread t([&] { try { (void)Lease::Acquire(pin, uuid); }
                           catch (const std::exception&) { refused = true; } });
        t.join(); Require(refused && count(2) == 0);
        for (int m : {1, 2}) {
            mode(m); Refuse([&] { (void)Lease::Acquire(pin, uuid); });
            Require(count(2) == std::uint64_t(m) && count(3) == std::uint64_t(m));
        }
        mode(0);
        // Atomic owned-file replacement leaves mapped original code alone.
        // A fresh callable lookup and subsequent use must refuse changed bytes.
        {
            auto image = ImageLease::Retain(pin, uuid, {"_AEHL_OwnedFactoryVersion"});
            auto retained = Lease::Acquire(pin, uuid);
            const std::string changed = std::string(argv[1]) + ".changed";
            const std::string backup = std::string(argv[1]) + ".backup";
            std::ofstream replacement(changed, std::ios::binary);
            replacement.write(reinterpret_cast<const char*>(bytes.data()), bytes.size()); replacement.put('x'); replacement.close();
            Require(std::rename(argv[1], backup.c_str()) == 0 && std::rename(changed.c_str(), argv[1]) == 0);
            Refuse([&] { (void)image.Function("_AEHL_OwnedFactoryVersion"); });
            Refuse([&] { (void)retained.Value(); });
            // Still balance the originally trusted module's reference on error.
            retained.Reset(); Require(count(3) == 3);
            Require(std::remove(argv[1]) == 0 && std::rename(backup.c_str(), argv[1]) == 0);
        }
        auto first = Lease::Acquire(pin, uuid); Require(first && first.Value() == 73);
        const auto generation = first.Generation();
        auto second = Lease::Acquire(pin, uuid); Require(second && second.Generation() == generation);
        drop(); Require(count(1) == 0 && first.Value() == 73);
        second = std::move(first); Require(!first && second.Value() == 73 && count(3) == 4);
        auto final = std::move(second); Require(!second && final.Value() == 73);
        bool use_refused = false;
        std::thread worker([&] { try { (void)final.Value(); }
                                catch (const std::exception&) { use_refused = true; } });
        worker.join(); Require(use_refused);
        final.Reset(); Require(count(1) == 1 && count(3) == 5);
        Refuse([&] { (void)final.Value(); });
        { auto expired = Lease::Acquire(pin, uuid); Require(!expired && count(0) == 1); }
        seed(); auto last = Lease::Acquire(pin, uuid); Require(last.Generation() != generation);
        drop(); Require(count(1) == 1);
        // Drop harness image owner. Lease must keep actual code + object alive.
        Require(dlclose(handle) == 0); handle = nullptr;
        Require(last.Value() == 73); const auto before = events.size();
        last.Reset(); Require(events.size() >= before + 2 && events[before] == 2 && events[before+1] == 1);
        // dyld may retain C++ images: unload absence is not a promised capability.
        const bool unload = events.size() > before + 2 && events[before+2] == 3;
        std::cout << "OWNED_FACTORY_LEASE PASS; no_create_absent_expired; moved_owner_alive; "
                     "release_before_image_close; Adobe_calls=0; unload_observed=" << unload << '\n';
        return 0;
    } catch (const std::exception&) { std::cerr << "REFUSED owned factory lease\n"; return 1; }
}
