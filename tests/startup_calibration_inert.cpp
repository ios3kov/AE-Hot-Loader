#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include <cstdlib>
#include <dlfcn.h>
#include <iostream>
#include <stdexcept>
static int acquired = 0;
SPErr Acquire(const char*, int32, const void**) { ++acquired; return 1; }
int main(int argc, char** argv) {
    try {
        if (argc != 3) throw std::runtime_error("arguments");
        // This is our own just-built library, never an Adobe binary.
        void* library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
        if (!library) throw std::runtime_error("owned library unavailable");
        using Entry = A_Err (*)(SPBasicSuite*, A_long, A_long, AEGP_PluginID, AEGP_GlobalRefcon*);
        auto entry = reinterpret_cast<Entry>(dlsym(library, "EntryPointFunc"));
        if (!entry) throw std::runtime_error("export");
        SPBasicSuite suite{}; suite.AcquireSuite = Acquire;
        unsetenv("AEHL_STARTUP_CALIBRATION_TOKEN");
        if (entry(&suite, 0, 0, 0, nullptr)) throw std::runtime_error("default inert");
        setenv("AEHL_STARTUP_CALIBRATION_TOKEN", "wrong-token", 1);
        if (entry(&suite, 0, 0, 0, nullptr)) throw std::runtime_error("token inert");
        setenv("AEHL_STARTUP_CALIBRATION_TOKEN", argv[2], 1);
        if (entry(&suite, 0, 0, 0, nullptr) || acquired) throw std::runtime_error("host inert");
        if (dlclose(library)) throw std::runtime_error("close");
        std::cout << "PASS: 3 inert cases; acquired_suites=0; Adobe_calls=0\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
