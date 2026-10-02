#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "../experiments/ordinary_discovery/ResidentImageBinding.hpp"
#include <filesystem>
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
        Check(argc == 4); void* library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); Check(library);
        using Entry = A_Err (*)(SPBasicSuite*, A_long, A_long, AEGP_PluginID, AEGP_GlobalRefcon*);
        auto entry = reinterpret_cast<Entry>(dlsym(library, "EntryPointFunc")); Check(entry);
        SPBasicSuite suite{}; suite.AcquireSuite = Acquire;
        Check(entry(nullptr, 0, 0, 0, nullptr) == 0);
        Check(setenv("AEHL_RETAINED_IDENTITY_TOKEN", "incorrect-test-token", 1) == 0);
        Check(entry(&suite, 0, 0, 0, nullptr) == 0);
        Check(setenv("AEHL_RETAINED_IDENTITY_TOKEN", argv[2], 1) == 0);
        Check(entry(&suite, 0, 0, 0, nullptr) == 0 && acquired == 0);
        resident_binding::Digest digest{};
        const std::string hex=argv[3], digits="0123456789abcdef"; Check(hex.size()==64);
        for(std::size_t i=0;i<32;++i){const auto a=digits.find(hex[i*2]),b=digits.find(hex[i*2+1]);
            Check(a!=digits.npos && b!=digits.npos);digest[i]=static_cast<unsigned char>(a*16+b);}
        const auto bound=resident_binding::Resolve({std::filesystem::canonical(argv[1]).string(),digest},
                                                   {"_AEHL_RetainedBuildIdentity"});
        Check(bound.functions.at("_AEHL_RetainedBuildIdentity")==dlsym(library,"AEHL_RetainedBuildIdentity"));
        bool refused=false;digest[0]^=1;
        try{(void)resident_binding::Resolve({std::filesystem::canonical(argv[1]).string(),digest},
              {"_AEHL_RetainedBuildIdentity"});}catch(...){refused=true;}Check(refused);
        Check(dlclose(library) == 0);
        std::cout << "PASS: 3 retained identity inert entrypoint cases; SDK suites=0; root_reads=0; self_binding=PASS; wrong_hash=REFUSED\n";
        return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
