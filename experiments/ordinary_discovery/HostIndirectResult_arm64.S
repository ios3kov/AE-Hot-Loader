// Research-only ABI primitive. NO resolver, Adobe address, entrypoint or auto-run.
// Intended only for a separately verified one-pointer-argument callee returning
// an object indirectly in x8. The caller owns correctly sized/aligned storage
// and must use the producing runtime's destructor after successful construction.
// This does not validate a callee, establish its ABI, grant consent or bind FILE.
#if !defined(__APPLE__) || !defined(__aarch64__) || defined(__arm64e__)
#error "This research primitive supports macOS arm64 only, not arm64e."
#endif
.text
.p2align 2
.globl _AEHL_Arm64_IndirectResult
.private_extern _AEHL_Arm64_IndirectResult
_AEHL_Arm64_IndirectResult:
.cfi_startproc
    // C wrapper inputs: x0=callee, x1=argument, x2=result storage.
    // Tail transfer preserves the caller's stack, frame and return address.
    mov x16, x0
    mov x0, x1
    mov x8, x2
    br x16
.cfi_endproc
