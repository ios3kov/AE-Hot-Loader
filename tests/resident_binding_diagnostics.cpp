// Exact binding diagnostics on owned files/memory only. Never touches Adobe.
#include "../experiments/ordinary_discovery/ResidentImageBinding.hpp"
#include <iostream>
#include <fstream>
#include <iterator>
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <dlfcn.h>
#include <thread>
#endif
using namespace resident_binding;
template<class F> void Refused(const char* stage, F action) {
    bool refused = false;
    try { action(); }
    catch (const Failure& error) {
        Require(std::strcmp(error.stage(), stage) == 0);
        Require(std::strcmp(error.what(), "resident-binding-refused") == 0); refused = true;
    }
    Require(refused);
}
int main(int argc, char** argv) {
    try {
        Require(argc >= 2 && argv != nullptr);
        Refused("resident-image-parse", [] {
            AtStage("resident-image-parse", [] { return Parse({}, {"_owned"}); });
        });
        Refused("resident-text-mismatch", [] {
            AtStage("resident-text-range", [] { Require(false, "resident-text-mismatch"); });
        });
        Require(AtStage("resident-image-parse", [] { return 7; }) == 7);
        bool allocation = false;
        try { AtStage("resident-image-parse", [] { throw std::bad_alloc(); }); }
        catch (const std::bad_alloc&) { allocation = true; }
        Require(allocation); // Do not mislabel unrelated allocation failure as malformed image.
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
        if (argc == 3) {
            const std::string path = argv[1], mode = argv[2];
            std::ifstream in(path, std::ios::binary); Require(bool(in));
            const Bytes bytes(std::istreambuf_iterator<char>(in), {});
            Pin pin{path, Hash(bytes)};
            if (mode == "files-memory") {
                Refused("resident-pin-contract", [&] { ReadPinned({"relative", pin.sha256}); });
                Refused("resident-pin-contract", [&] { ReadPinned({path, {}}); });
                Refused("resident-file-open", [&] { ReadPinned({path + "-missing", pin.sha256}); });
                auto wrong = pin; wrong.sha256[0] ^= 1;
                Refused("resident-file-hash", [&] { ReadPinned(wrong); });
                Refused("resident-file-stat", [&] { ReadPinned({path.substr(0, path.rfind('/')), pin.sha256}); });
                Require(ReadPinned(pin) == bytes);
                const Bytes actual{1,2,3,4}, different{1,2,9,4};
                const auto address = reinterpret_cast<std::uintptr_t>(actual.data());
                EqualMemory(address, actual, 0, actual.size(), "resident-header-read", "resident-header-mismatch");
                Refused("resident-header-mismatch", [&] {
                    EqualMemory(address, different, 0, different.size(), "resident-header-read", "resident-header-mismatch");
                });
                Refused("resident-text-mismatch", [&] {
                    EqualMemory(address, different, 0, different.size(), "resident-text-read", "resident-text-mismatch");
                });
                Refused("resident-text-read", [&] {
                    EqualMemory(1, actual, 0, actual.size(), "resident-text-read", "resident-text-mismatch");
                });
                Difference difference;
                Refused("resident-text-mismatch", [&] {
                    EqualMemory(address, different, 0, different.size(), "resident-text-read", "resident-text-mismatch", &difference);
                });
                Require(difference.known && difference.relative_offset == 2 && difference.file_offset == 2 &&
                        difference.expected_word == 0x04090201U && difference.actual_word == 0x04030201U);
                EqualMemory(address, actual, 0, actual.size(), "resident-text-read", "resident-text-mismatch", &difference);
                Require(!difference.known);
                Refused("resident-text-read", [&] {
                    EqualMemory(1, actual, 0, actual.size(), "resident-text-read", "resident-text-mismatch", &difference);
                }); Require(!difference.known);
                Bytes large(8200, 0), expected(8212, 0);
                large[8197] = 19; expected[12 + 8197] = 23;
                const auto large_address = reinterpret_cast<std::uintptr_t>(large.data());
                Refused("resident-text-mismatch", [&] {
                    EqualMemory(large_address, expected, 12, large.size(), "resident-text-read", "resident-text-mismatch", &difference);
                });
                Require(difference.known && difference.relative_offset == 8197 && difference.file_offset == 8209 &&
                        difference.expected_word == (23U << 8) && difference.actual_word == (19U << 8));
            } else if (mode == "resident") {
                Refused("resident-image-missing", [&] { Resolve(pin, {"_AEHL_OwnUnused"}); });
                void* handle = dlopen(path.c_str(), RTLD_NOW | RTLD_LOCAL); Require(handle);
                const auto before = Snapshot();
                const auto bound = Resolve(pin, {"_AEHL_OwnUnused"}); Require(bound.functions.size() == 1);
                Refused("resident-image-parse", [&] { Resolve(pin, {"_AEHL_NotExported"}); });
                auto wrong = pin; wrong.sha256[0] ^= 1;
                Refused("resident-file-hash", [&] { Resolve(wrong, {"_AEHL_OwnUnused"}); });
                bool worker = false;
                std::thread thread([&] {
                    try { Resolve(pin, {"_AEHL_OwnUnused"}); }
                    catch (const Failure& error) { worker = std::strcmp(error.stage(), "resident-snapshot-first") == 0; }
                }); thread.join(); Require(worker && before == Snapshot());
                Require(dlclose(handle) == 0);
            } else Require(false);
        }
#endif
        std::cout << "PASS binding predicate diagnostics; Adobe_calls=0\n"; return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
