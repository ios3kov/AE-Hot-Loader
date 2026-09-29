#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include <cassert>
#include <cstdlib>
#include <dlfcn.h>
#include <iostream>

namespace {
int acquired = 0;
SPErr Acquire(const char*, int32, const void**) { ++acquired; return 1; }
}
int main(int argc, char** argv) {
    assert(argc == 3);
    void* library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    assert(library);
    using Entry = A_Err (*)(SPBasicSuite*, A_long, A_long, AEGP_PluginID, AEGP_GlobalRefcon*);
    auto entry = reinterpret_cast<Entry>(dlsym(library, "EntryPointFunc"));
    assert(entry);
    SPBasicSuite suite{};
    suite.AcquireSuite = Acquire;
    assert(entry(nullptr, 0, 0, 0, nullptr) == 0);
    assert(setenv("AEHL_SCOPED_GATE_TOKEN", "incorrect-test-token", 1) == 0);
    assert(entry(&suite, 0, 0, 0, nullptr) == 0);
    assert(setenv("AEHL_SCOPED_GATE_TOKEN", argv[2], 1) == 0);
    // Correct token still cannot activate in this unpinned standalone process.
    assert(entry(&suite, 0, 0, 0, nullptr) == 0);
    assert(acquired == 0);
    assert(dlclose(library) == 0);
    std::cout << "PASS: 3 inert entrypoint cases; no SDK suite acquired\n";
}
