// Research-only export binding. Reads files/current-process memory; never dlopen,
// dlsym, attach, evaluate code, or call a resolved function. Not an ABI/consent gate.
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

namespace resident_binding {
using Bytes = std::vector<unsigned char>;
inline void Require(bool ok) { if (!ok) throw std::runtime_error("resident-binding-refused"); }
inline void Range(std::size_t start, std::size_t size, std::size_t limit) {
    Require(start <= limit && size <= limit - start);
}
inline std::uint64_t U(const Bytes& b, std::size_t p, unsigned n, bool big = false) {
    Require(n == 2 || n == 4 || n == 8); Range(p, n, b.size());
    std::uint64_t v = 0;
    for (unsigned i = 0; i < n; ++i) v |= std::uint64_t(b[p + i]) << (8 * (big ? n - i - 1 : i));
    return v;
}
inline std::string CString(const Bytes& b, std::size_t& p, std::size_t end) {
    Range(p, 0, end); Require(end <= b.size()); std::string s;
    while (p < end && b[p]) { Require(s.size() < 1024); s += char(b[p++]); }
    Require(p < end); ++p; return s;
}
inline bool Name16(const Bytes& b, std::size_t p, const char* wanted) {
    Range(p, 16, b.size()); std::size_t n = std::strlen(wanted); Require(n < 16);
    return std::memcmp(b.data() + p, wanted, n) == 0 && b[p + n] == 0;
}
struct Image {
    std::size_t slice = 0, slice_size = 0, header_size = 0, text_offset = 0, text_size = 0;
    std::uint64_t base_vm = 0, text_vm = 0;
    std::array<unsigned char, 16> uuid{};
    // Values are image-relative offsets derived from the export trie, not request addresses.
    std::map<std::string, std::uint64_t> exports;
};
inline std::uint64_t Leb(const Bytes& b, std::size_t& p, std::size_t end) {
    std::uint64_t value = 0;
    for (unsigned shift = 0; shift < 64; shift += 7) {
        Require(p < end); const unsigned c = b[p++];
        Require(shift != 63 || (c & 0xfeU) == 0);
        value |= std::uint64_t(c & 127U) << shift;
        if (!(c & 128U)) return value;
    }
    throw std::runtime_error("resident-binding-refused");
}
inline std::uint64_t Export(const Bytes& b, std::size_t begin, std::size_t size,
                            const std::string& name) {
    const std::size_t end = begin + size; Range(begin, size, b.size());
    std::set<std::size_t> visited; std::size_t node = 0, matched = 0;
    for (unsigned depth = 0; depth <= 1024; ++depth) {
        Require(node < size && visited.insert(node).second);
        std::size_t p = begin + node; auto terminal = Leb(b, p, end);
        Range(p, terminal, end); const std::size_t children = p + terminal;
        if (matched == name.size()) {
            Require(terminal != 0); const auto flags = Leb(b, p, children);
            // Accept only regular direct exports (optionally weak). No absolute,
            // reexport, resolver, thread-local or unknown export flags.
            Require((flags & ~std::uint64_t(4)) == 0);
            auto address = Leb(b, p, children); Require(p == children); return address;
        }
        p = children; Require(p < end); const unsigned count = b[p++];
        bool found = false; std::size_t next = 0, consumed = 0;
        for (unsigned i = 0; i < count; ++i) {
            const auto edge = CString(b, p, end); auto child = Leb(b, p, end);
            Require(!edge.empty() && child < size);
            if (name.compare(matched, edge.size(), edge) == 0) {
                Require(!found); found = true; next = std::size_t(child); consumed = edge.size();
            }
        }
        Require(found); node = next; matched += consumed;
    }
    throw std::runtime_error("resident-binding-refused");
}
inline Image Parse(const Bytes& b, const std::vector<std::string>& names) {
    Require(!names.empty() && names.size() <= 16 && b.size() <= 256U * 1024U * 1024U);
    std::set<std::string> unique;
    for (const auto& n : names) Require(!n.empty() && n.size() <= 1024 &&
        n.find('\0') == std::string::npos && unique.insert(n).second);
    Image im; im.slice_size = b.size();
    if (U(b, 0, 4, true) == 0xcafebabeU) {
        auto count = U(b, 4, 4, true); Require(count && count <= 16); Range(8, count * 20, b.size());
        bool found = false;
        for (std::size_t i = 0; i < count; ++i) {
            auto p = 8 + i * 20; auto off = U(b, p + 8, 4, true), size = U(b, p + 12, 4, true);
            Range(off, size, b.size()); Require(off >= 8 + count * 20);
            if (U(b, p, 4, true) == 0x100000cU) {
                Require(!found && U(b, p + 4, 4, true) == 0); found = true;
                im.slice = off; im.slice_size = size;
            }
        }
        Require(found);
    }
    const auto o = im.slice, limit = o + im.slice_size;
    Range(o, 32, limit); Require(U(b, o, 4) == 0xfeedfacfU && U(b, o + 4, 4) == 0x100000cU);
    Require(U(b, o + 8, 4) == 0 && (U(b, o + 12, 4) == 6 || U(b, o + 12, 4) == 8));
    const auto ncmds = U(b, o + 16, 4), commands = U(b, o + 20, 4);
    Require(ncmds && ncmds <= 4096 && commands <= 2U * 1024U * 1024U);
    Range(o + 32, commands, limit); im.header_size = 32 + commands;
    bool uuid = false, text_segment = false, text_section = false, trie = false;
    std::size_t exp_offset = 0, exp_size = 0, p = o + 32;
    for (std::size_t i = 0; i < ncmds; ++i) {
        Range(p, 8, o + im.header_size); auto cmd = U(b, p, 4), len = U(b, p + 4, 4);
        Require(len >= 8 && len % 8 == 0); Range(p, len, o + im.header_size);
        if (cmd == 0x1b) {
            Require(!uuid && len == 24); uuid = true;
            std::copy_n(b.data() + p + 8, 16, im.uuid.begin());
        } else if (cmd == 0x19) {
            Require(len >= 72); auto sections = U(b, p + 64, 4);
            Require(sections <= 255 && len == 72 + sections * 80);
            if (Name16(b, p + 8, "__TEXT")) {
                Require(!text_segment); text_segment = true;
                im.base_vm = U(b, p + 24, 8); auto vmsize = U(b, p + 32, 8), filesize = U(b, p + 48, 8);
                Require(U(b, p + 40, 8) == 0 && filesize >= im.header_size && filesize <= im.slice_size);
                Require(U(b, p + 60, 4) == 5); // mapped read/execute, never writable text
                for (std::size_t j = 0; j < sections; ++j) {
                    auto s = p + 72 + j * 80;
                    if (!Name16(b, s, "__text")) continue;
                    Require(!text_section && Name16(b, s + 16, "__TEXT")); text_section = true;
                    im.text_vm = U(b, s + 32, 8); im.text_size = U(b, s + 40, 8);
                    im.text_offset = U(b, s + 48, 4);
                    Require(im.text_size && im.text_size <= 64U * 1024U * 1024U && im.text_size % 4 == 0);
                    Require(im.text_vm >= im.base_vm && im.text_vm - im.base_vm == im.text_offset);
                    Range(im.text_offset, im.text_size, filesize); Range(im.text_offset, im.text_size, vmsize);
                    Require((U(b, s + 64, 4) & 0x800000ffU) == 0x80000000U);
                }
            }
        } else if (cmd == 0x80000033U || cmd == 0x80000022U || cmd == 0x22U) {
            const auto q = cmd == 0x80000033U ? 8U : 40U;
            Require(len == q + 8); const auto size = U(b, p + q + 4, 4);
            if (size) {
                Require(!trie); trie = true; exp_offset = U(b, p + q, 4); exp_size = size;
                Range(exp_offset, exp_size, im.slice_size); Require(exp_size <= 16U * 1024U * 1024U);
            }
        }
        p += len;
    }
    Require(p == o + im.header_size && uuid && text_segment && text_section && trie);
    Require(std::any_of(im.uuid.begin(), im.uuid.end(), [](unsigned char c) { return c != 0; }));
    for (const auto& n : names) {
        auto relative = Export(b, o + exp_offset, exp_size, n);
        Require(relative % 4 == 0 && relative >= im.text_offset &&
                relative - im.text_offset <= im.text_size - 4);
        im.exports.emplace(n, relative);
    }
    return im;
}
} // namespace resident_binding

#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include "SelfMemoryRead.hpp"
#include <CommonCrypto/CommonDigest.h>
#include <fcntl.h>
#include <mach-o/dyld.h>
#include <pthread.h>
#include <sys/stat.h>
#include <unistd.h>
namespace resident_binding {
using Digest = std::array<unsigned char, 32>;
struct Pin { std::string path; Digest sha256{}; };
inline Digest Hash(const Bytes& bytes) {
    Require(bytes.size() <= std::numeric_limits<CC_LONG>::max()); Digest d{};
    Require(CC_SHA256(bytes.data(), CC_LONG(bytes.size()), d.data()) != nullptr); return d;
}
struct FD {
    int n = -1; explicit FD(int value) : n(value) { Require(n >= 0); }
    FD(const FD&) = delete; FD& operator=(const FD&) = delete;
    ~FD() { if (n >= 0) ::close(n); }
};
inline bool Path(const std::string& path) {
    if (path.empty() || path.size() > 4096 || path.front() != '/' || path.back() == '/') return false;
    std::size_t begin = 1;
    for (std::size_t i = 1; i <= path.size(); ++i) {
        if (i != path.size() && path[i] != '/') { if (static_cast<unsigned char>(path[i]) < 32) return false; continue; }
        const auto part = path.substr(begin, i - begin);
        if (part.empty() || part == "." || part == "..") return false;
        begin = i + 1;
    }
    return true;
}
inline Bytes ReadPinned(const Pin& pin) {
    Require(Path(pin.path) && std::any_of(pin.sha256.begin(), pin.sha256.end(), [](unsigned char c) { return c; }));
    FD dir(::open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC)); std::size_t begin = 1;
    while (true) {
        auto end = pin.path.find('/', begin); const bool last = end == std::string::npos;
        auto part = pin.path.substr(begin, last ? std::string::npos : end - begin);
        FD next(::openat(dir.n, part.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK |
                        (last ? 0 : O_DIRECTORY)));
        if (last) {
            struct stat a{}, b{}; Require(::fstat(next.n, &a) == 0 && S_ISREG(a.st_mode) &&
                a.st_nlink == 1 && a.st_size > 0 && a.st_size <= 256 * 1024 * 1024);
            Bytes bytes(std::size_t(a.st_size)); std::size_t got = 0;
            while (got < bytes.size()) {
                auto n = ::read(next.n, bytes.data() + got, bytes.size() - got);
                Require(n > 0); got += std::size_t(n);
            }
            Require(::fstat(next.n, &b) == 0 && a.st_dev == b.st_dev && a.st_ino == b.st_ino &&
                a.st_size == b.st_size && a.st_nlink == b.st_nlink && a.st_mode == b.st_mode &&
                a.st_mtimespec.tv_sec == b.st_mtimespec.tv_sec && a.st_mtimespec.tv_nsec == b.st_mtimespec.tv_nsec &&
                a.st_ctimespec.tv_sec == b.st_ctimespec.tv_sec && a.st_ctimespec.tv_nsec == b.st_ctimespec.tv_nsec);
            Require(Hash(bytes) == pin.sha256); return bytes;
        }
        std::swap(dir.n, next.n); begin = end + 1;
    }
}
struct Loaded {
    std::uintptr_t header = 0; std::intptr_t slide = 0; std::string path;
    bool operator==(const Loaded& b) const { return header == b.header && slide == b.slide && path == b.path; }
};
inline std::vector<Loaded> Snapshot() {
    Require(pthread_main_np() == 1); const auto count = _dyld_image_count(); Require(count && count <= 8192);
    std::vector<Loaded> images; images.reserve(count);
    for (std::uint32_t i = 0; i < count; ++i) {
        Loaded im; im.header = reinterpret_cast<std::uintptr_t>(_dyld_get_image_header(i));
        im.slide = _dyld_get_image_vmaddr_slide(i); const char* name = _dyld_get_image_name(i);
        Require(im.header && name); const auto address = reinterpret_cast<std::uintptr_t>(name);
        for (std::size_t j = 0; ; ) {
            Require(j < 4096 && address <= UINTPTR_MAX - j);
            std::array<char, 128> chunk{};
            const auto n = std::min({chunk.size(), std::size_t(4096 - j),
                                    std::size_t(4096 - ((address + j) % 4096))});
            Require(directory_spec::ReadSelfMemory(reinterpret_cast<const void*>(address + j), chunk.data(), n));
            const auto stop = std::find(chunk.begin(), chunk.begin() + n, '\0');
            im.path.append(chunk.data(), std::size_t(stop - chunk.begin()));
            if (stop != chunk.begin() + n) break;
            j += n;
        }
        images.push_back(std::move(im));
    }
    Require(_dyld_image_count() == count); return images;
}
inline void EqualMemory(std::uintptr_t address, const Bytes& bytes, std::size_t offset, std::size_t count) {
    Range(offset, count, bytes.size()); Require(address && address <= UINTPTR_MAX - count);
    std::array<unsigned char, 8192> copy{};
    for (std::size_t i = 0; i < count;) {
        const auto n = std::min(copy.size(), count - i);
        Require(directory_spec::ReadSelfMemory(reinterpret_cast<const void*>(address + i), copy.data(), n));
        Require(std::memcmp(copy.data(), bytes.data() + offset + i, n) == 0); i += n;
    }
}
struct BoundImage { Pin pin; Image image; std::map<std::string, const void*> functions; };
inline BoundImage Resolve(const Pin& pin, const std::vector<std::string>& names) {
    const auto before = Snapshot(); Require(before == Snapshot());
    const Loaded* found = nullptr;
    for (const auto& im : before) if (im.path == pin.path) { Require(!found); found = &im; }
    Require(found); // do not read/load a missing image to make this pass
    const auto bytes = ReadPinned(pin); auto image = Parse(bytes, names);
    // Derive the runtime base from the resident header, not a user-supplied slide/address.
    if (found->slide >= 0) {
        Require(image.base_vm <= UINTPTR_MAX - std::uint64_t(found->slide));
        Require(image.base_vm + std::uint64_t(found->slide) == found->header);
    } else {
        const auto distance = std::uint64_t(-(found->slide + 1)) + 1;
        Require(image.base_vm >= distance && image.base_vm - distance == found->header);
    }
    EqualMemory(found->header, bytes, image.slice, image.header_size);
    Require(found->header <= UINTPTR_MAX - image.text_offset);
    EqualMemory(found->header + image.text_offset, bytes, image.slice + image.text_offset, image.text_size);
    BoundImage result{pin, image, {}};
    for (const auto& e : image.exports) {
        Require(found->header <= UINTPTR_MAX - e.second);
        result.functions.emplace(e.first, reinterpret_cast<const void*>(found->header + e.second));
    }
    Require(before == Snapshot()); return result;
    // This is a point-in-time check, not a dyld lock or lifetime lease. The future
    // authorized main-thread caller must recheck pins/state and cannot permit unload.
}
} // namespace resident_binding
#endif
