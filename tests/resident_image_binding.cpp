// Parser and resident-address checks. Never loads or executes an Adobe image.
#include "../experiments/ordinary_discovery/ResidentImageBinding.hpp"
#include "../experiments/ordinary_discovery/NativeDirectoryBinding.hpp"
#include "../experiments/ordinary_discovery/ResidentDirectorySession.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <dlfcn.h>
#include <thread>
#endif
using namespace resident_binding;
int OwnedCallable() { return 73; }
Bytes Read(const char* path) {
    std::ifstream in(path, std::ios::binary); Require(bool(in));
    return Bytes(std::istreambuf_iterator<char>(in), {});
}
void Fail(const Bytes& b, const std::vector<std::string>& n) {
    bool blocked = false; try { (void)Parse(b, n); } catch (const std::exception&) { blocked = true; }
    Require(blocked);
}
int main(int argc, char** argv) {
    try {
        Require(argc >= 3);
        // Compile this conversion on every platform, not only in the Apple branch.
        const void* inspected = reinterpret_cast<const void*>(&OwnedCallable);
        Require(native_directory::Callable<int (*)()>(inspected)() == 73);
        bool null_blocked = false;
        try { (void)native_directory::Callable<int (*)()>(nullptr); }
        catch (const std::exception&) { null_blocked = true; }
        Require(null_blocked);
        const auto bytes = Read(argv[1]); const std::string symbol = argv[2];
        Require(ae256_directory::kFile[0] == 0xdf && ae256_directory::kFile[31] == 0x64 &&
                ae256_directory::kUtility[0] == 0xae && ae256_directory::kUtility[31] == 0xaa &&
                ae256_directory::kCore[0] == 0xcb && ae256_directory::kCore[31] == 0xb0);
        auto image = Parse(bytes, {symbol}); Require(image.exports.size() == 1);
        Fail(Bytes{}, {symbol}); Fail(bytes, {symbol, symbol}); Fail(bytes, {"_AEHL_NOT_PRESENT"});
        auto bad = bytes; bad[image.slice + 4] = 0; Fail(bad, {symbol});
        bad = bytes; bad[image.slice + 8] = 2; Fail(bad, {symbol});
        bad = bytes; bad[image.slice + 20] = 0xff; bad[image.slice + 21] = 0xff; Fail(bad, {symbol});
        std::cout << "PARSE direct export + malformed/missing/duplicate/architecture guards PASS\n";
        if (argc == 4 && std::string(argv[3]) == "--file-contract") {
            const auto file = Parse(bytes, native_directory::FileExports());
            Require(file.exports.at(native_directory::FileExports()[0]) == 0x12c48 &&
                    file.exports.at(native_directory::FileExports()[1]) == 0x1315c &&
                    file.exports.at(native_directory::FileExports()[2]) == 0x4a70 &&
                    file.exports.at(native_directory::FileExports()[3]) == 0x130cc);
            std::cout << "FILE four named exports agree; Adobe calls=0\n"; return 0;
        }
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
        if (argc == 6 && (std::string(argv[3]) == "--profile" ||
                         std::string(argv[3]) == "--retained-profile")) {
            const std::string root = argv[4];
            const std::array<std::string, 3> paths{root + "/FILE.dylib", root + "/U.dylib",
                root + "/dvacore.framework/Versions/A/dvacore"};
            native_directory::Profile profile{root, Hash(Read(paths[0].c_str())),
                Hash(Read(paths[1].c_str())), Hash(Read(paths[2].c_str()))};
            std::array<void*, 3> handles{};
            if (std::string(argv[3]) == "--retained-profile") {
                const auto absent_before = Snapshot();
                bool rejected = false;
                try { (void)native_directory::BindRetainedOnce(profile, true); }
                catch (const std::exception&) { rejected = true; }
                Require(rejected && native_directory::RetainedDirectoryReferences() == 0 &&
                        absent_before == Snapshot());
            }
            for (std::size_t i = 0; i < paths.size(); ++i) {
                handles[i] = dlopen(paths[i].c_str(), RTLD_NOW | RTLD_LOCAL); Require(handles[i]);
            }
            const auto before = Snapshot();
            const bool retain = std::string(argv[3]) == "--retained-profile";
            if (retain) {
                bool rejected = false;
                try { (void)native_directory::BindRetainedOnce(profile); }
                catch (const std::exception&) { rejected = true; }
                Require(rejected && native_directory::RetainedDirectoryReferences() == 0);
                Require(::setenv("DYLD_AEHL_OWNED_TEST", "1", 1) == 0);
                rejected = false;
                try { (void)native_directory::BindRetainedOnce(profile, true); }
                catch (const std::exception&) { rejected = true; }
                Require(::unsetenv("DYLD_AEHL_OWNED_TEST") == 0);
                Require(rejected && native_directory::RetainedDirectoryReferences() == 0);
                auto bad = profile; bad.utility[0] ^= 1;
                rejected = false;
                try { (void)native_directory::BindRetainedOnce(bad, true); }
                catch (const std::exception&) { rejected = true; }
                Require(rejected && native_directory::RetainedDirectoryReferences() == 0);
            }
            const auto table = retain ? native_directory::BindRetainedOnce(profile, true)
                                      : native_directory::Bind(profile);
            if (retain) {
                Require(native_directory::RetainedDirectoryReferences() == 3);
                // Drop the TEST's original references. The new NOLOAD references
                // must keep all three owned producers alive for the call below.
                for (auto& handle : handles) { Require(dlclose(handle) == 0); handle = nullptr; }
                Require(before == Snapshot());
                bool rejected = false;
                try { (void)native_directory::BindRetainedOnce(profile, true); }
                catch (const std::exception&) { rejected = true; }
                Require(rejected && native_directory::RetainedDirectoryReferences() == 3);
            }
            const auto result = directory_spec::CreateRoundtripRelease(table, argv[5]);
            Require(result.completed && result.cleanup_ok && result.strings_created == 2 &&
                result.string_release_attempts == 2 && result.specs_created == 1 && result.spec_release_attempts == 1);
            Require(before == Snapshot());
            for (auto i = handles.rbegin(); i != handles.rend(); ++i)
                if (*i) Require(dlclose(*i) == 0);
            if (retain) std::cout << "NOLOAD lifetime and one-shot/consent/environment/hash guards PASS; retained=3 until process exit\n";
            std::cout << "BOUND DIRECTORY own 3-provider create/roundtrip/release PASS; Adobe calls=0\n";
        }
        if (argc == 4 && std::string(argv[3]) == "--resident") {
            const Pin pin{argv[1], Hash(bytes)};
            bool absent = false;
            try { (void)Resolve(pin, {symbol}); } catch (const std::exception&) { absent = true; }
            Require(absent);
            // The TEST, not the resolver, loads this freshly compiled owned fixture.
            void* handle = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); Require(handle);
            const auto before = Snapshot(); auto bound = Resolve(pin, {symbol});
            const auto value = native_directory::Callable<int (*)()>(bound.functions.at(symbol));
            Require(value() == 73); Require(before == Snapshot());
            auto wrong = pin; wrong.sha256[0] ^= 1;
            bool hash_blocked = false, thread_blocked = false;
            try { (void)Resolve(wrong, {symbol}); } catch (const std::exception&) { hash_blocked = true; }
            std::thread thread([&] { try { (void)Resolve(pin, {symbol}); }
                catch (const std::exception&) { thread_blocked = true; } }); thread.join();
            Require(hash_blocked && thread_blocked);
            bool incomplete = false;
            try { (void)native_directory::Bind({"/owned/Test.app/Contents/Frameworks", {}, {}, {}}); }
            catch (const std::exception&) { incomplete = true; }
            Require(incomplete && before == Snapshot());
            Require(dlclose(handle) == 0); // owned fixture only, after all assertions
            std::cout << "RESIDENT named address, code bytes, hash, absent-image and main-thread guards PASS; Adobe calls=0\n";
        }
#endif
        return 0;
    } catch (const std::exception&) { std::cerr << "FAIL resident binding check\n"; return 1; }
}
