// Diagnostic decoder of already copied AE25.6x101 arm64 factory reference bytes.
// Does not read/retain an object, validate a mapped allocation or supply a
// callable pointer/host lease. Plausible stale bytes can still match this shape.
#pragma once
#include <array>
#include <cstdint>
#include <stdexcept>
namespace factory_receiver_reference {
using Bytes = std::array<unsigned char,24>;
enum class Presence { Absent, Present };
struct Layout {
    std::uint64_t unknown_base_adjustment=0, object_from_control=0x18;
};
struct Decoded {
    Presence presence=Presence::Absent;
    std::uint64_t primary=0, unknown_base=0, control=0;
};
inline void Require(bool condition) {
    if(!condition) throw std::runtime_error("receiver-reference-shape-refused");
}
inline Layout ReviewedAE256Layout() { return {}; }
inline std::uint64_t Word(const Bytes& b,std::size_t index) {
    Require(index<3);std::uint64_t value=0;
    for(unsigned j=0;j<8;++j) value|=std::uint64_t(b[index*8+j])<<(j*8);
    return value;
}
inline Decoded Decode(const Bytes& b,const Layout& layout) {
    // Exact reviewed file layout only; source image identity is a separate gate.
    Require(layout.unknown_base_adjustment==0 && layout.object_from_control==0x18);
    const auto primary=Word(b,0), unknown=Word(b,1), control=Word(b,2);
    if(!(primary|unknown|control)) return {};
    Require(primary && unknown && control && primary%8==0 && unknown%8==0 && control%8==0);
    Require(control<=UINT64_MAX-layout.object_from_control &&
            primary==control+layout.object_from_control && unknown==primary);
    return {Presence::Present,primary,unknown,control};
    // No refcount value can create ownership. Never construct shared_ptr from
    // these integers, call through them or promote this result to gate approval.
}
} // namespace factory_receiver_reference
