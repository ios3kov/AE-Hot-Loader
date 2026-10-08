#pragma once
#include <cstdint>
#include <cstring>
#include <string>

namespace startup_image {
struct Facts { const char* path = nullptr; std::uintptr_t base = 0; };
struct Description {
    bool known = false;
    std::uintptr_t address = 0, base = 0, offset = 0;
    std::string path_hex;
};
// Describe an already supplied pointer through loader metadata only. Never
// invoke it, read image bytes, resolve a new symbol, or acquire a module owner.
template<class Resolver>
Description Inspect(std::uintptr_t address, Resolver resolve) {
    Description out; out.address = address;
    Facts facts;
    if (!address || !resolve(address, facts) || !facts.path || !facts.base || address < facts.base)
        return out;
    const auto length = strnlen(facts.path, 1024);
    if (!length || length == 1024 || facts.path[0] != '/') return out;
    static constexpr char digits[] = "0123456789abcdef";
    out.path_hex.reserve(length * 2);
    for (std::size_t i = 0; i < length; ++i) {
        const auto byte = static_cast<unsigned char>(facts.path[i]);
        out.path_hex += digits[byte >> 4]; out.path_hex += digits[byte & 15];
    }
    out.base = facts.base; out.offset = address - facts.base; out.known = true;
    return out;
}
} // namespace startup_image
