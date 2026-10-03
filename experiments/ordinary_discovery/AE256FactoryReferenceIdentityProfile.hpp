// Exact reviewed MEE acquisition/destruction CODE IDENTITY only. Never a callable
// ABI/receiver/capability. The owned classref call lease explicitly refuses it.
#pragma once
#include "AE256FactoryIdentityProfile.hpp"
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
namespace ae256_factory_reference_identity {
inline factory_code_identity::Profile ReviewedProfile() {
    auto p = ae256_factory_identity::ReviewedProfile();
    const auto classref = p.spans.at(2);
    p.spans = {
        {{"interface_dtor", 0x3e9c, 96}, {0xbf,0x3f,0x1c,0xe5,0x59,0x90,0xc5,0xa4,
            0x27,0xb6,0xd0,0xd8,0x71,0x21,0xfe,0xce,0x1e,0xc3,0x96,0x64,0xff,0x6c,0x8f,0x00,
            0x4c,0x7d,0xfb,0xb5,0xf5,0x78,0x16,0x2c}},
        classref,
    };
    return p;
}
} // namespace ae256_factory_reference_identity
#endif
