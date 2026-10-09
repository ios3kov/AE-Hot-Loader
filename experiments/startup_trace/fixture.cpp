#include <cstdint>
#define POINT(name) extern "C" __attribute__((noinline, used)) void name( \
 std::uint64_t a, std::uint64_t b=0, std::uint64_t c=0, std::uint64_t d=0, std::uint64_t e=0) { \
 asm volatile("" : : "r"(a), "r"(b), "r"(c), "r"(d), "r"(e) : "memory"); }
POINT(marker) POINT(convert) POINT(pipl) POINT(spec) POINT(writer)
POINT(index) POINT(writer_return) POINT(reader) POINT(match) POINT(lookup)
POINT(callback)
int main() {
 const auto cb=reinterpret_cast<std::uintptr_t>(&callback);
 const auto mf=reinterpret_cast<std::uintptr_t>(&match);
 marker(1,0x1000,cb,0,1); marker(2,0x1000,cb,0,1);
 convert(0x9999); convert(0x1000); pipl(0x2000);
 spec(0x9999,0x3000); spec(0x2000,0x3000);
 writer(0x9999,0x4000); writer(0x3000,0x4000);
 index(0x3000,6,0x4000); writer_return(0x4000);
 reader(1,77,mf,0,1); match(77); lookup(0x3000,0x5000,0x4000,7);
 reader(2,77,mf,0,1);
 return 0;
}
