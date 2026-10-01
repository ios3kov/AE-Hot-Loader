// AE 25.6x101 arm64 Stage C1 input identity.
// Data only: no resolver, dlopen, dlsym, function address or host invocation.
// Hash pins identify reviewed/recorded file bytes; a future live supervisor must
// rehash the actual files and prove resident-image identity before any private call.
#pragma once
#include <array>
#include <string_view>

namespace ae256_resource {
struct ImagePin {
    std::string_view key;
    std::string_view path;
    std::string_view sha256;
};

inline constexpr std::string_view kApp =
    "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app";

inline constexpr std::array<ImagePin, 9> kImages{{
    {"AfterEffects",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/MacOS/After Effects",
     "464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6"},
    {"FILE",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/FILE.dylib",
     "df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864"},
    {"U",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/U.dylib",
     "aecabb33c5ac5948ad742848c46588398bc690411b70aae7ca3f08a919362daa"},
    {"dvacore",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/dvacore.framework/Versions/A/dvacore",
     "cb6faaf5b745903b80b44105b658ab68186d5065ae47c8a57c9b23e26aa8ecb0"},
    {"FLT",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/FLT.dylib",
     "227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256"},
    {"MEE",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/MEE.dylib",
     "18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344"},
    {"PLUG",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/PLUG.dylib",
     "12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22"},
    {"PluginSupport",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/PluginSupport.framework/Versions/A/PluginSupport",
     "4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832"},
    {"aelib",
     "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/aelib.framework/Versions/A/aelib",
     "f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f"},
}};

inline constexpr std::string_view kReview =
    "Stage-C1 profile: C0 FILE/U/dvacore live PASS + PLUG/FLT/aelib/MEE/PluginSupport static evidence";
} // namespace ae256_resource
