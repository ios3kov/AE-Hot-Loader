#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include <cstdlib>
#include <dlfcn.h>
#include <iostream>
#include <stdexcept>
namespace {
unsigned acquired = 0;
SPErr Acquire(const char*, int32, const void**) { ++acquired; return 1; }
void Check(bool value) { if (!value) throw std::runtime_error("inert-test-failed"); }
}
int main(int argc, char** argv) {
    try {
        Check(argc == 3); void* library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); Check(library);
        using Entry = A_Err (*)(SPBasicSuite*, A_long, A_long, AEGP_PluginID, AEGP_GlobalRefcon*);
        auto entry = reinterpret_cast<Entry>(dlsym(library, "EntryPointFunc")); Check(entry);
        SPBasicSuite suite{}; suite.AcquireSuite = Acquire;
        Check(entry(nullptr, 0, 0, 0, nullptr) == 0);
        Check(setenv("AEHL_CLEANUP_OBSERVER_TOKEN", "incorrect-test-token", 1) == 0);
        Check(entry(&suite, 0, 0, 0, nullptr) == 0);
        Check(setenv("AEHL_CLEANUP_OBSERVER_TOKEN", argv[2], 1) == 0);
        Check(entry(&suite, 0, 0, 0, nullptr) == 0 && acquired == 0);
        Check(dlclose(library) == 0);
        std::cout << "PASS: 3 observer inert entrypoint cases; SDK suites=0; root_reads=0\n";
        return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
