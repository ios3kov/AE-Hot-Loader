// Isolated arm64 research carrier. Only the owned binder uses these routines.
// No Adobe symbol/import/host integration or runtime creation flag.
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
.text
.p2align 2
.globl _AEHL_CallExistingClassRef
.private_extern _AEHL_CallExistingClassRef
_AEHL_CallExistingClassRef:
    .cfi_startproc
    stp x29, x30, [sp, #-16]!
    .cfi_def_cfa_offset 16
    .cfi_offset x29, -16
    .cfi_offset x30, -8
    mov x29, sp
    .cfi_def_cfa x29, 16
    mov x16, x0
    mov x8, x1
    mov w0, #0
    blr x16
    ldp x29, x30, [sp], #16
    .cfi_def_cfa sp, 0
    .cfi_restore x29
    .cfi_restore x30
    ret
    .cfi_endproc
.p2align 2
.globl _AEHL_DestroyClassRef
.private_extern _AEHL_DestroyClassRef
_AEHL_DestroyClassRef:
    .cfi_startproc
    stp x29, x30, [sp, #-16]!
    .cfi_def_cfa_offset 16
    .cfi_offset x29, -16
    .cfi_offset x30, -8
    mov x29, sp
    .cfi_def_cfa x29, 16
    mov x16, x0
    mov x0, x1
    blr x16
    ldp x29, x30, [sp], #16
    .cfi_def_cfa sp, 0
    .cfi_restore x29
    .cfi_restore x30
    ret
    .cfi_endproc
#endif
