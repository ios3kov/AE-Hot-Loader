#include "../experiments/ordinary_discovery/AE256CleanupProfile.hpp"
#include <iostream>
int main() {
    for (const auto& p : {ae256_cleanup::kPlug, ae256_cleanup::kMee})
        std::cout << p.path << '\n' << p.sha256 << '\n' << p.uuid << '\n' << p.anchor << '\n'
                  << p.section << '\n' << p.vm << '\n' << p.size << '\n';
}
