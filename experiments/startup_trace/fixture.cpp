#include <cstdint>
#define POINT(name) extern "C" __attribute__((noinline, used)) void name( \
 std::uint64_t a, std::uint64_t b=0, std::uint64_t c=0, std::uint64_t d=0, std::uint64_t e=0) { \
 asm volatile("" : : "r"(a), "r"(b), "r"(c), "r"(d), "r"(e) : "memory"); }
POINT(marker) POINT(convert) POINT(pipl) POINT(spec) POINT(writer)
POINT(index) POINT(writer_return) POINT(reader) POINT(match)
POINT(callback)
// Preserve the callee-saved registers; expose a real SIMD pair at one exact NOP.
extern "C" __attribute__((naked, noinline, used)) void lookup(
 std::uint64_t, std::uint64_t, std::uint64_t, std::uint64_t) {
 asm volatile("stp x21, x22, [sp, #-16]!\n"
              "mov x21, x2\nmov x22, x3\nfmov d0, x0\nmov v0.d[1], x1\n"
              ".globl _lookup_probe\n_lookup_probe:\nnop\n"
              "ldp x21, x22, [sp], #16\nret\n");
}
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
