#include "../experiments/ordinary_discovery/AE256ResourceProfile.hpp"
#include <algorithm>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>

static void Check(bool value) { if (!value) throw std::runtime_error("resource-profile"); }
static bool Hex64(std::string_view value) {
    return value.size() == 64 &&
           std::all_of(value.begin(), value.end(), [](char c) {
               return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
           });
}
int main() {
    using namespace ae256_resource;
    Check(kImages.size() == 9);
    const std::set<std::string> expected{
        "AfterEffects","FILE","U","dvacore","FLT","MEE","PLUG","PluginSupport","aelib"};
    std::set<std::string> actual;
    for (const auto& image : kImages) {
        Check(!image.key.empty() && !image.path.empty() && image.path.front() == '/');
        Check(image.path.find(kApp) == 0);
        Check(Hex64(image.sha256));
        Check(actual.insert(std::string(image.key)).second);
    }
    Check(actual == expected);
    std::cout << "RESOURCE_PROFILE_TESTS=9 PASS; calls=0\n";
}
