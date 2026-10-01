#include "../experiments/ordinary_discovery/ResidentDataRootBinding.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <dlfcn.h>
#include <thread>
#endif
using namespace resident_data_root;
static Bytes ReadFile(const char* path) {
    std::ifstream stream(path, std::ios::binary); Require(bool(stream));
    return Bytes(std::istreambuf_iterator<char>(stream), {});
}
static void Refuse(const Bytes& bytes, const std::string& anchor, const Root& root) {
    bool refused = false;
    try { (void)Describe(bytes, anchor, root); } catch (const std::exception&) { refused = true; }
    Require(refused);
}
int main(int argc, char** argv) {
    try {
        Require(argc == 6);
        const auto bytes = ReadFile(argv[1]); const std::string anchor = argv[2];
        const Root root{std::stoull(argv[3], nullptr, 0), std::string(argv[5]) == "--describe-slot" ? 8U : 16U, argv[4]};
        const auto layout = Describe(bytes, anchor, root);
        Require(layout.relative == root.vm - layout.image.base_vm && layout.size == root.size);
        Refuse(bytes, anchor, {root.vm + 1, 16, root.section});
        Refuse(bytes, anchor, {root.vm, 0, root.section});
        Refuse(bytes, anchor, {root.vm, 4097, root.section});
        Refuse(bytes, anchor, {UINT64_MAX - 7, 16, root.section});
        Refuse(bytes, anchor, {root.vm, 16, "__text"});
        Refuse(bytes, anchor, {root.vm + 0x1000000, 16, root.section});
        std::cout << "DATA_ROOT_LAYOUT PASS; mutable_bytes_not_compared_to_file\n";
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
        if (std::string(argv[5]) == "--resident") {
            const Profile profile{{argv[1], Hash(bytes)}, anchor, root, layout.image.uuid};
            const auto absent = Snapshot(); bool refused = false;
            try { (void)Bind(profile); } catch (const std::exception&) { refused = true; }
            Require(refused && absent == Snapshot());
            // This TEST alone loads and locates its freshly compiled owned data.
            void* handle = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); Require(handle);
            void* storage = dlsym(handle, "AEHL_TestRoot"); Require(storage);
            auto* words = static_cast<std::uint64_t*>(storage); words[1] = 0x123456789abcdef0ULL;
            const auto before = Snapshot();
            const auto bound = Bind(profile);
            Require(bound.address == reinterpret_cast<std::uintptr_t>(storage) + 8 && bound.size == 16);
            std::uint64_t read[2]{};
            Require(directory_spec::ReadSelfMemory(reinterpret_cast<const void*>(bound.address), read, sizeof(read)) &&
                    read[0] == words[1] && read[0] == 0x123456789abcdef0ULL && read[1] == 0);
            for (unsigned i = 0; i < 5; ++i) {
                auto bad = profile;
                if (i == 0) bad.pin.sha256[0] ^= 1;
                if (i == 1) bad.uuid[0] ^= 1;
                if (i == 2) bad.root.section = "__text";
                if (i == 3) bad.root.vm += 1;
                if (i == 4) bad.root.vm += 0x1000000;
                refused = false;
                try { (void)Bind(bad); } catch (const std::exception&) { refused = true; }
                Require(refused && before == Snapshot());
            }
            bool thread_refused = false;
            std::thread thread([&] {
                try { (void)Bind(profile); } catch (const std::exception&) { thread_refused = true; }
            }); thread.join(); Require(thread_refused && before == Snapshot());
            Require(dlclose(handle) == 0); // own fixture after its final use only
            std::cout << "OWNED_RESIDENT_DATA_ROOT PASS; Adobe_calls=0; provider_loads_by_binder=0\n";
        }
#else
        Require(std::string(argv[5]) == "--describe" || std::string(argv[5]) == "--describe-slot");
#endif
        return 0;
    } catch (const std::exception&) {
        std::cerr << "REFUSED data-root binding\n"; return 1;
    }
}
