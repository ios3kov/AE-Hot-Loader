// Research-only no-scan FILE operations; NO resolver, AE entrypoint or auto-run.
// All addresses must come from a separately reviewed, image-pinned native binder.
// This table is not a consent mechanism. Never fill it from user/request addresses.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <string>

#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "The observed directory/string ABI requires a little-endian target."
#endif

namespace directory_spec {
// Storage for an object constructed by its PRODUCING runtime, not a fabricated
// std::u16string or FILE_Spec. This observed ABI is specific to the pinned AE image.
constexpr std::size_t kStringBytes = 24, kMaxPath = 4096;
struct Functions {
    using Indirect = void (*)(const void* target, const void* argument, void* result);
    using Reader = bool (*)(const void*, void*, std::size_t) noexcept;
    Indirect indirect = nullptr;
    const void* ascii_to_host = nullptr;
    const void* inquire_path = nullptr;
    void (*destroy_string)(void*) = nullptr;
    void* (*new_spec)(const void*) = nullptr;
    bool (*is_dir)(const void*) = nullptr;
    int (*dispose_spec)(void*) = nullptr;
    Reader read_memory = nullptr;
    bool complete() const noexcept {
        return indirect && ascii_to_host && inquire_path && destroy_string &&
               new_spec && is_dir && dispose_spec && read_memory;
    }
};
struct Result {
    // Only operation/lifetime results. Not a live host, registry, consent or PASS verdict.
    bool completed = false, invoked = false, cleanup_ok = true;
    unsigned strings_created = 0, string_release_attempts = 0;
    unsigned specs_created = 0, spec_release_attempts = 0;
    const char* stage = "validate";
};
inline bool AsciiDirectoryPath(const std::string& path) noexcept {
    if (path.size() < 2 || path.size() > kMaxPath || path.front() != '/' || path.back() == '/')
        return false;
    std::size_t begin = 1;
    for (std::size_t i = 1; i <= path.size(); ++i) {
        if (i != path.size() && path[i] != '/') {
            const auto c = static_cast<unsigned char>(path[i]);
            if (c < 32 || c > 126) return false;
            continue;
        }
        const auto count = i - begin;
        if (!count || (count == 1 && path[begin] == '.') ||
            (count == 2 && path[begin] == '.' && path[begin + 1] == '.')) return false;
        begin = i + 1;
    }
    return true; // lexical only; outer probe must bind a new owned no-link directory
}
inline void Need(bool value) { if (!value) throw std::runtime_error("directory-operation-failed"); }

// Read-only view of the observed 24-byte alternate host UTF-16 layout.
// FILE 0x4a9c..0x4ae4 reads tag+23, long length+8, data pointer+0; 0x4af0
// reads 16-bit units. Never mutate these bytes, infer a target from them, or free
// their data pointer. read_memory must perform a bounded safe SELF-process read.
// A matching path does NOT independently verify the object/destructor ABI.
inline bool MatchesAscii(const void* object, const std::string& expected,
                         Functions::Reader read_memory) noexcept {
    if (!object || !read_memory || !AsciiDirectoryPath(expected)) return false;
    std::array<unsigned char, kStringBytes> bytes{};
    if (!read_memory(object, bytes.data(), bytes.size())) return false;
    const bool is_long = (bytes[23] & 0x80U) != 0;
    std::uint64_t length = bytes[23];
    std::uintptr_t data_address = 0;
    static_assert(sizeof(std::uintptr_t) == 8, "64-bit process required");
    if (is_long) {
        std::memcpy(&length, bytes.data() + 8, sizeof(length));
        std::memcpy(&data_address, bytes.data(), sizeof(data_address));
        if (!data_address || data_address % alignof(std::uint16_t)) return false;
    } else if (length > 10) return false; // inline 11 UTF-16 slots include terminator
    if (length != expected.size()) return false; // bounds before size arithmetic/read
    const std::size_t nbytes = (expected.size() + 1) * sizeof(std::uint16_t);
    std::array<unsigned char, (kMaxPath + 1) * 2> characters{};
    if (is_long) {
        if (data_address > UINTPTR_MAX - nbytes ||
            !read_memory(reinterpret_cast<const void*>(data_address), characters.data(), nbytes))
            return false;
    } else std::memcpy(characters.data(), bytes.data(), nbytes);
    for (std::size_t i = 0; i < expected.size(); ++i) {
        const auto c = static_cast<unsigned char>(expected[i]);
        if (characters[i * 2] != c || characters[i * 2 + 1] != 0) return false;
    }
    return characters[nbytes - 2] == 0 && characters[nbytes - 1] == 0;
}

// Takes one path. No plugin search, resources, module loading, file opening or
// registry operation is expressible through this adapter. The binder must use
// the exact inspected FILE_New constructor, not one acquiring a plugin module.
// Caller MUST surround this with claim/identity/scope/postflight/supervisor gates.
inline Result CreateRoundtripRelease(const Functions& supplied, const std::string& supplied_path) {
    const Functions f = supplied; // freeze callbacks against mutation during calls
    const std::string path = supplied_path;
    Result r;
    if (!f.complete() || !AsciiDirectoryPath(path)) return r;
    alignas(8) std::array<unsigned char, kStringBytes> input{}, output{};
    bool input_live = false, output_live = false;
    void* spec = nullptr;
    auto destroy = [&](bool& live, void* storage) noexcept {
        if (!live) return;
        live = false; // attempted exactly once, even if a destructor throws
        ++r.string_release_attempts;
        try { f.destroy_string(storage); }
        catch (...) { r.cleanup_ok = false; }
    };
    auto dispose = [&]() noexcept {
        if (!spec) return;
        void* owned = spec;
        spec = nullptr; // ownership uncertain on failure; NEVER retry or use again
        ++r.spec_release_attempts;
        try { if (f.dispose_spec(owned) != 0) r.cleanup_ok = false; }
        catch (...) { r.cleanup_ok = false; }
    };
    try {
        r.stage = "input-string";
        r.invoked = true;
        f.indirect(f.ascii_to_host, path.c_str(), input.data());
        input_live = true; // throwing construction has no completed object to destroy
        ++r.strings_created;
        Need(MatchesAscii(input.data(), path, f.read_memory));
        r.stage = "create-spec";
        spec = f.new_spec(input.data());
        Need(spec != nullptr);
        ++r.specs_created;
        r.stage = "release-input";
        destroy(input_live, input.data());
        Need(r.cleanup_ok);
        r.stage = "is-directory";
        Need(f.is_dir(spec));
        r.stage = "path-result";
        f.indirect(f.inquire_path, spec, output.data());
        output_live = true;
        ++r.strings_created;
        r.stage = "path-compare";
        Need(MatchesAscii(output.data(), path, f.read_memory));
        r.stage = "release-output";
        destroy(output_live, output.data());
        Need(r.cleanup_ok);
        r.stage = "release-spec";
        dispose();
        Need(r.cleanup_ok);
        r.completed = true;
        r.stage = "complete";
    } catch (...) {
        // No backend exception text, addresses or user path in the result.
        // Preserve the failed stage and clean independent completed objects once.
    }
    destroy(output_live, output.data());
    destroy(input_live, input.data());
    dispose();
    r.completed = r.completed && r.cleanup_ok;
    return r;
}
} // namespace directory_spec
