// Read-only identity of reviewed factory code spans in an already resident image.
// Never loads Adobe code, invokes a function, reads/retains a factory object or
// supplies a callable ABI. Integer diagnostic addresses are point-in-time only.
#pragma once
#include "ResidentImageBinding.hpp"
namespace factory_code_identity {
using namespace resident_binding;
struct Entry { std::string tag; std::uint64_t vm = 0, size = 0; };
struct Span { std::uint64_t relative = 0, size = 0; };
struct Layout { Image image; std::map<std::string, Span> spans; };
inline bool Tag(const std::string& value) {
    if (value.empty() || value.size() > 32) return false;
    for (const unsigned char c : value)
        if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_')) return false;
    return true;
}
inline Layout Describe(const Bytes& bytes, const std::string& anchor,
                       const std::vector<Entry>& entries) {
    Require(!entries.empty() && entries.size() <= 8);
    Layout result{Parse(bytes, {anchor}), {}};
    const auto& image = result.image;
    Require(image.text_size <= UINT64_MAX - image.text_vm);
    const auto end = image.text_vm + image.text_size;
    auto previous_end = image.text_vm;
    for (const auto& e : entries) {
        Require(Tag(e.tag) && e.vm % 4 == 0 && e.size && e.size <= 4096 && e.size % 4 == 0 &&
                e.vm >= previous_end && e.vm >= image.base_vm && e.vm < end && e.size <= end - e.vm);
        const Span span{e.vm - image.base_vm, e.size};
        Require(result.spans.emplace(e.tag, span).second);
        Range(std::size_t(span.relative), std::size_t(span.size), image.slice_size);
        previous_end = e.vm + e.size;
    }
    return result; // containment only; exact pin/span fingerprints checked by Bind
}
inline Bytes SpanBytes(const Bytes& bytes, const Layout& layout, const std::string& tag) {
    const auto it = layout.spans.find(tag); Require(it != layout.spans.end());
    const auto& span = it->second;
    Range(layout.image.slice, layout.image.slice_size, bytes.size());
    Range(std::size_t(span.relative), std::size_t(span.size), layout.image.slice_size);
    const auto start = layout.image.slice + std::size_t(span.relative);
    return Bytes(bytes.begin() + start, bytes.begin() + start + std::size_t(span.size));
}
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
struct ReviewedSpan { Entry entry; Digest sha256{}; };
struct Profile {
    Pin pin;
    std::string anchor; // direct code export used only to recover checked header
    std::array<unsigned char, 16> uuid{};
    std::vector<ReviewedSpan> spans; // immutable reviewed build profile, not request data
};
struct BoundSpan { std::uintptr_t address = 0; std::size_t size = 0; };
struct BoundCode {
    Pin pin;
    std::array<unsigned char, 16> uuid{};
    std::uintptr_t header = 0;
    std::map<std::string, BoundSpan> spans;
};
inline BoundCode Bind(const Profile& supplied) {
    Require(!supplied.spans.empty() && supplied.spans.size() <= 8);
    const Profile p = supplied;
    Require(std::any_of(p.uuid.begin(), p.uuid.end(), [](unsigned char c) { return c; }));
    const auto before = Snapshot(); // existing resolver enforces main-thread identity
    const auto resident = Resolve(p.pin, {p.anchor}); // absence is refusal, never a load
    const auto bytes = ReadPinned(p.pin);
    std::vector<Entry> entries;
    for (const auto& s : p.spans) entries.push_back(s.entry);
    const auto layout = Describe(bytes, p.anchor, entries);
    Require(layout.image.uuid == p.uuid && resident.image.uuid == p.uuid);
    for (const auto& s : p.spans) {
        Require(std::any_of(s.sha256.begin(), s.sha256.end(), [](unsigned char c) { return c; }));
        Require(Hash(SpanBytes(bytes, layout, s.entry.tag)) == s.sha256);
    }
    const auto code = reinterpret_cast<std::uintptr_t>(resident.functions.at(p.anchor));
    const auto relative = resident.image.exports.at(p.anchor);
    Require(code >= relative); const auto header = code - relative; Require(header);
    BoundCode result{p.pin, p.uuid, header, {}};
    for (const auto& item : layout.spans) {
        const auto& span = item.second;
        Require(span.relative <= UINTPTR_MAX - header && span.size <= UINTPTR_MAX - header - span.relative);
        const auto address = header + span.relative;
        EqualMemory(address, bytes, layout.image.slice + std::size_t(span.relative), std::size_t(span.size));
        result.spans.emplace(item.first, BoundSpan{address, std::size_t(span.size)});
    }
    Require(before == Snapshot()); return result;
    // No factory receiver/base adjustment/reference lease was acquired. Recheck
    // identity at use; do not convert this result into ResourcePassGate approval.
}
#endif
} // namespace factory_code_identity
