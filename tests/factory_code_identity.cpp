#include "../experiments/ordinary_discovery/NativeFactoryCodeIdentity.hpp"
#include "../experiments/ordinary_discovery/AE256FactoryIdentityProfile.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <dlfcn.h>
#include <thread>
#endif
using namespace factory_code_identity;
static Bytes ReadFile(const char* path) {
    std::ifstream f(path, std::ios::binary); Require(bool(f));
    return Bytes(std::istreambuf_iterator<char>(f), {});
}
template<class F> static void Refuse(F f) {
    bool refused = false; try { f(); } catch (const std::exception&) { refused = true; }
    Require(refused);
}
int main(int argc, char** argv) {
    try {
        Require(argc == 6); const auto bytes = ReadFile(argv[1]);
        const std::string anchor = argv[2], mode = argv[5];
        const std::vector<Entry> entries{{"first", std::stoull(argv[3], nullptr, 0), 4},
                                        {"second", std::stoull(argv[4], nullptr, 0), 4}};
        const auto layout = Describe(bytes, anchor, entries);
        Require(layout.spans.size() == 2 && SpanBytes(bytes, layout, "first").size() == 4);
        for (unsigned i = 0; i < 10; ++i) {
            auto bad = entries;
            if (i == 0) bad.clear();
            if (i == 1) bad[0].size = 0;
            if (i == 2) bad[0].size = 4097;
            if (i == 3) ++bad[0].vm;
            if (i == 4) bad[0].vm = UINT64_MAX - 3;
            if (i == 5) bad[1].vm = bad[0].vm;
            if (i == 6) bad[1].tag = bad[0].tag;
            if (i == 7) bad[0].tag = "";
            if (i == 8) bad[0].tag = "untrusted/path";
            if (i == 9) bad.resize(9, bad[0]);
            Refuse([&] { (void)Describe(bytes, anchor, bad); });
        }
        Refuse([&] { (void)SpanBytes(bytes, layout, "unknown"); });
        std::cout << "FACTORY_CODE_LAYOUT PASS; no_receiver_or_ABI_claim\n";
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
        const auto reviewed = ae256_factory_identity::ReviewedProfile();
        Require(reviewed.spans.size() == 3 && reviewed.spans[0].entry.vm == 0x73e4 &&
                reviewed.spans[1].entry.vm == 0x7b1c && reviewed.spans[2].entry.vm == 0x43944);
        if (mode == "--resident") {
            Profile profile{{argv[1], Hash(bytes)}, anchor, layout.image.uuid, {}};
            for (const auto& e : entries) profile.spans.push_back({e, Hash(SpanBytes(bytes, layout, e.tag))});
            const auto absent = Snapshot(); Refuse([&] { (void)Bind(profile); }); Require(absent == Snapshot());
            // Only this TEST loads its fresh owned dylib; binder never loads it.
            void* handle = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); Require(handle);
            const auto before = Snapshot(); const auto bound = Bind(profile);
            const auto a = reinterpret_cast<std::uintptr_t>(dlsym(handle, "AEHL_OwnedFunction"));
            const auto b = reinterpret_cast<std::uintptr_t>(dlsym(handle, "AEHL_OwnedSecond"));
            Require(a && b && bound.spans.at("first").address == a && bound.spans.at("second").address == b);
            Require(bound.spans.at("first").size == 4 && bound.uuid == profile.uuid);
            for (unsigned i = 0; i < 7; ++i) {
                auto bad = profile;
                if (i == 0) bad.pin.sha256[0] ^= 1;
                if (i == 1) bad.uuid[0] ^= 1;
                if (i == 2) bad.spans[0].sha256[0] ^= 1;
                if (i == 3) bad.spans[0].entry.size += 4;
                if (i == 4) bad.spans[0].sha256.fill(0);
                if (i == 5) bad.spans.clear();
                if (i == 6) bad.spans.resize(9, bad.spans[0]);
                Refuse([&] { (void)Bind(bad); }); Require(before == Snapshot());
            }
            bool refused = false;
            std::thread t([&] { try { (void)Bind(profile); } catch (const std::exception&) { refused = true; } });
            t.join(); Require(refused && before == Snapshot());
            Require(dlclose(handle) == 0); // after final use of this owned fixture
            std::cout << "OWNED_FACTORY_CODE_BIND PASS; Adobe_calls=0; binder_loads=0; callable_pointers=0\n";
        } else Require(mode == "--describe");
#else
        Require(mode == "--describe");
#endif
        return 0;
    } catch (const std::exception&) { std::cerr << "REFUSED factory-code identity\n"; return 1; }
}
