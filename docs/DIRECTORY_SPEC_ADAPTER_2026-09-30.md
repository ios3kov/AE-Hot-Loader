# Stage C: concrete no-scan directory operations; pending host binding

Continues upstream `61ea0871cc6e55d9f2669e9d5b4989a0e83f9a15` on
`research/ordinary-plugin-discovery`. AGENTS, PRODUCTION_PLAN, the current status
and FILE_OBJECT_CONTRACT apply. Shared rules were rechecked unchanged at blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Scope and acceptance

Implement the create/roundtrip/release sequence behind an **unbound** function
table, not another registration policy. Exercise it against owned C++ string/
spec producers, including construction exceptions, invalid paths and release
failures. Use the existing unified runner. Do not execute Adobe code, attach,
install, restart, scan, change callbacks, clear caches, unload, change main or
release. Strict builds, -O0/-O2 lifecycle tests, ASan/UBSan, unified Linux checks
and read-only contract review are required. New macOS checks remain NOT RUN
unless verified for this change; an earlier green CI run is not a substitute.

## Implementation

`DirectorySpecAdapter.hpp` implements the concrete sequence:

1. Reject incomplete callbacks or invalid/non-ASCII paths before any call.
2. Construct the input host string via the existing indirect-result mechanism
   and check its value without manufacturing a C++ host string.
3. Call the supplied FILE constructor and retain only its newly returned object.
4. Destroy the input string once; verify directory status; obtain a separately
   constructed path result and compare the exact path.
5. Destroy the output once and dispose the owned directory spec once.

Completed objects are cleaned on errors. A failed constructor is not followed by
attempted destruction of an unconstructed object. A destructor/disposer failure
marks cleanup unsuccessful and is never retried. The result contains operation
completion and lifetime counters, not a live registry/consent/PASS verdict.
Backend exception text, raw paths and addresses are not copied into it.

No search, resource-opening, module-loading or registry callback exists in this
adapter. The 24-byte aligned storage is filled by the producing runtime; it is
not initialized as a fabricated host representation. A bounded read-only view
checks characters without adopting/freeing their data pointer. A matching path
is not proof of producer/destructor identity or private ABI compatibility.

`SelfMemoryRead.hpp` provides a macOS arm64 self-reader using
`mach_vm_read_overwrite(mach_task_self(), ...)`, with an 8194-byte limit and
exact copied-length check. It cannot select/attach to another process. It
prevents unchecked pointer dereference during comparison, not malicious native
callbacks, invalid destructor contracts or every concurrent memory change.

## Boundaries

The function table is populated only by test-owned producers. There is no
host resolver, automatic execution, AEGP entrypoint or runnable user experiment.
This is not a complete FILE binding. Its table is not a security or consent
boundary, and must never be filled from user/request-supplied addresses.
The outer probe still needs authorization, exact loaded-image/function pins,
main-thread and PID/start checks, a fresh owned no-link directory, durable
one-shot claim, deadline, external supervisor and unchanged project/registry/
loaded-module postflight. Nothing is connected to the product or old scoped
loader. The resource-pass policy/journal are not relabelled as an implemented
no-scan supervisor.

ASCII-only input is a restriction of this preliminary **no-scan probe**, not a
change to promised product Unicode support. Non-ASCII is refused before calls;
no unverified UTF-8 conversion is used. The read-only view is little-endian,
64-bit and specific to the inspected 24-byte host representation, not generic
libc++ compatibility. U/dvacore producer/destructor provenance remains unverified.

A failed release leaves ownership uncertain. The test release functions free
their own allocation before reporting an error, covering the double-free hazard;
that is not a claim about Adobe failure behavior. A future supervisor must retain
the failure and one-shot evidence. Neither destructor nor FILE disposal is retried.

## Sources and existing FILE evidence

Rehashed received FILE.dylib, unchanged:
`df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864`.
FILE_InqUnicodePath reads tag+23, long length+8 and data pointer+0 at
0x4a9c..0x4ae4, then 16-bit character units at 0x4af0. These static references
support the read-only view, not runtime targets. Existing creation/disposal and
exception evidence stays in FILE_OBJECT_CONTRACT_2026-09-30.md. Adobe binaries
were read only and stay outside Git and the handover archive.

Public interface references, not Adobe-private-ABI specifications:
- Arm AAPCS64 sections 6.1.1 and 6.9:
  https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst
- Apple XNU self-read interface:
  https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/mach/mach_vm.defs

No external implementation was copied. The test string is owned synthetic code,
not Adobe's allocator or string. On macOS the new test uses the actual arm64
result thunk and self-reader; on Linux it uses typed C++17 construction and an
owned-allocation-bounded reader. Both run 27 lifecycle cases at -O0 and -O2.
The macOS path additionally checks unreadable pointers and read limits.

## Reproducible source and checks

Baseline: full macOS CI source snapshot for
`7411a903fb6cb21ca1f93e258d172e1a268072a2`, artifact `11123010954`, SHA-256
`81d74d02f3bd8b0018e6572016df2deca370d1249578078d66c3b528f77c6be9`.
All 181 source files match the archive. Reconstructed Git tree:
`55283e5239bc68c68507acd13df7fe3013384ca8`, identical to upstream 7411a90.
The following upstream 61ea087 changes only DEVELOPMENT_STATUS.md. This patch
adds files, so it does not overwrite that newer status. The local baseline commit
is explicitly labelled reconstructed, not impersonated as an upstream commit.
This is not the user's Mac checkout.

The earlier full macOS CI `36767508583` was rechecked: all build/sign/package/
smoke steps completed successfully for **7411a90**, closing its prior in-progress
status. It does not test the new adapter. The companion local evidence archive
records new test results, exact local Git commit and file hashes.

The existing unified runner discovers the two new Python tests. Native cases
remain nested in those tests, not extra Python counts. New GitHub/macOS CI is
BLOCKED: the current connector exposes read actions but no create/update/push
actions. A full discovery confirmed this; permission settings were not changed,
and no account/security bypass was attempted. The work is saved in a local Git
commit and patch, not claimed pushed. No installable AE artifact is handed over.

## Next boundary and preserved verdicts

Pin/review the actual U producer and dvacore destructor, implement a trusted
version-specific binder, and connect to a separately authorized no-scan probe
with fresh host/project/loaded-image evidence. Run the new native macOS checks
before authorizing that probe. The later PLUG pass still needs cleanup-callback
review and distinct authorization. No new user-side collection/test is requested.

Historical scoped embedded registration remains FAIL. RSMB startup-registered
apply/render PASS and RSMB late-registration FAIL remain distinct. Current AE
state is NOT OBSERVED. Five known full-audit findings remain open. There is no
new registration/render result, deployment, main change, merge or release.
