// Read-only point-in-time data-root binding; no Adobe invocation/attach/load.
// Static profile semantics must be reviewed separately. NOT lifetime/consent/
// allocation/completeness proof and never converted to ResourcePassGate approval.
#pragma once
#include "ResidentImageBinding.hpp"

namespace resident_data_root {
using namespace resident_binding;
struct Root {
    std::uint64_t vm = 0, size = 0;
    std::string section;
};
struct Layout {
    Image image;
    std::uint64_t relative = 0, size = 0;
};
inline std::uint64_t Add(std::uint64_t a, std::uint64_t b) {
    Require(a <= UINT64_MAX - b); return a + b;
}
inline Layout Describe(const Bytes& bytes, const std::string& anchor, const Root& root) {
    Require(root.vm && root.vm % 8 == 0 && root.size && root.size <= 4096 && root.size % 8 == 0 &&
            (root.section == "__bss" || root.section == "__common"));
    auto image = Parse(bytes, {anchor});
    const auto root_end = Add(root.vm, root.size);
    Require(root.vm >= image.base_vm);
    const auto start = image.slice, command_end = start + image.header_size;
    std::size_t p = start + 32;
    unsigned data_segments = 0, matching_sections = 0;
    std::vector<std::pair<std::uint64_t, std::uint64_t>> segments;
    for (std::size_t i = 0; i < U(bytes, start + 16, 4); ++i) {
        Range(p, 8, command_end); const auto command = U(bytes, p, 4), length = U(bytes, p + 4, 4);
        Range(p, length, command_end);
        if (command == 0x19) {
            Require(length >= 72);
            const auto vm = U(bytes, p + 24, 8), size = U(bytes, p + 32, 8);
            Require(size); segments.emplace_back(vm, Add(vm, size));
        }
        if (command == 0x19 && Name16(bytes, p + 8, "__DATA")) {
            Require(++data_segments == 1 && length >= 72);
            const auto vm = U(bytes, p + 24, 8), size = U(bytes, p + 32, 8);
            const auto end = Add(vm, size), fileoff = U(bytes, p + 40, 8), filesize = U(bytes, p + 48, 8);
            Require(size && filesize <= size && U(bytes, p + 56, 4) == 3 &&
                    U(bytes, p + 60, 4) == 3 && U(bytes, p + 68, 4) == 0);
            Range(fileoff, filesize, image.slice_size);
            const auto count = U(bytes, p + 64, 4);
            Require(count && count <= 255 && length == 72 + count * 80);
            for (std::size_t j = 0; j < count; ++j) {
                const auto s = p + 72 + j * 80;
                if (!Name16(bytes, s, root.section.c_str())) continue;
                Require(++matching_sections == 1 && Name16(bytes, s + 16, "__DATA"));
                const auto begin = U(bytes, s + 32, 8), extent = U(bytes, s + 40, 8);
                const auto section_end = Add(begin, extent), alignment = U(bytes, s + 52, 4);
                Require(extent && alignment <= 31 && begin % (std::uint64_t(1) << alignment) == 0 &&
                        begin >= vm && section_end <= end && root.vm >= begin && root_end <= section_end);
                Require(U(bytes, s + 48, 4) == 0 && U(bytes, s + 64, 4) == 1 &&
                        U(bytes, s + 60, 4) == 0); // S_ZEROFILL, no relocations
            }
        }
        p += length;
    }
    Require(p == command_end && data_segments == 1 && matching_sections == 1);
    std::sort(segments.begin(), segments.end());
    for (std::size_t i = 1; i < segments.size(); ++i) Require(segments[i - 1].second <= segments[i].first);
    return {std::move(image), root.vm - image.base_vm, root.size};
}
} // namespace resident_data_root

#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
namespace resident_data_root {
struct Profile {
    Pin pin;
    std::string anchor;
    Root root;
    std::array<unsigned char, 16> uuid{};
};
struct BoundRoot {
    Pin pin;
    std::array<unsigned char, 16> uuid{};
    std::uintptr_t header = 0, address = 0;
    std::size_t size = 0;
};
inline BoundRoot Bind(const Profile& supplied) {
    const Profile profile = supplied;
    Require(std::any_of(profile.uuid.begin(), profile.uuid.end(), [](unsigned char c) { return c; }));
    const auto before = Snapshot();
    // Resolve validates an already loaded image, exact file/header/text and thread.
    // The anchor is never invoked; its bound offset only recovers the checked header.
    const auto bound = Resolve(profile.pin, {profile.anchor});
    const auto bytes = ReadPinned(profile.pin);
    const auto layout = Describe(bytes, profile.anchor, profile.root);
    Require(layout.image.uuid == profile.uuid && bound.image.uuid == profile.uuid);
    const auto anchor = reinterpret_cast<std::uintptr_t>(bound.functions.at(profile.anchor));
    const auto relative = bound.image.exports.at(profile.anchor);
    Require(anchor >= relative);
    const auto header = anchor - relative;
    Require(header && header <= UINTPTR_MAX - layout.relative &&
            header + layout.relative <= UINTPTR_MAX - layout.size);
    EqualMemory(header, bytes, layout.image.slice, layout.image.header_size);
    Require(header <= UINTPTR_MAX - layout.image.text_offset);
    EqualMemory(header + layout.image.text_offset, bytes,
                layout.image.slice + layout.image.text_offset, layout.image.text_size);
    Require(before == Snapshot());
    return {profile.pin, profile.uuid, header, header + layout.relative, std::size_t(layout.size)};
    // No root data was read and no provider reference/lifetime lease acquired.
    // Recheck identity at use; an independent bounded reader still needs range/
    // process/state/lifetime review and separately scoped live authorization.
}
} // namespace resident_data_root
#endif
