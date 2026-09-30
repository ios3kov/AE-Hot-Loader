# Stage C: FILE ownership, indirect results and a no-scan boundary

Date: 2026-09-30. Continues `ad1ec8d2f49fc262260a6986d0566ac763f5c7d7`
on `research/ordinary-plugin-discovery`. AGENTS, the current resource-pass design
and journal record were consulted. Shared DEVELOPMENT_RULES were refreshed,
unchanged blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Scope and acceptance

Independently verify the received FILE implementation; identify creation,
string-return and release behavior; check the relevant branches against raw
instruction words; prepare and test only the missing machine-call primitive.
Require cross-assembly validation and an owned C++ producer on real macOS arm64,
including exception propagation and destruction, before describing that primitive
as tested. Preserve the original inputs and prior AE results.

No Adobe library may be loaded or executed, no process attachment or host
request is made, and no installation, restart, in-host scan, callback change,
cache reset, native unload, main update, merge or release is authorized here.
The assembly primitive is NOT a FILE adapter or a runnable AE probe.

## Received input

Upload `AEHL-FILE-bin.45Wcjk.zip`: 86,146 bytes, SHA-256
`8c13e0fc7866aee6a2ed4ed46d5ee01596ff672ba7642513042ae55bf2ae0fad`.
Its three exact flat regular entries were checked before being copied to a new
private analysis directory. No archive links or paths were followed.

| Entry | Bytes | SHA-256 |
|---|---:|---|
| FILE.dylib | 294816 | `df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864` |
| SHA256-before.txt and SHA256-after.txt, each | 77 | `3125709b76b1004972e82dd906bbd2f570307071055fc7c4ba98f0483a36f915` |

Both statements are byte-identical and match the independently hashed received
binary. This is received-file identity, not identity in a resident or historical
AE process. The arm64 slice begins at file offset 16384; its SHA-256 is
`54077a83553638a6a9cb075e27b5f456f76ded39d1b90e8791992a5894c37637`.
UUID: `E24D6F35-7B34-3663-8509-A2FF76370CFC`.

LLVM 17/apple-m1 decoded all 85,304 bytes of __TEXT,__text beginning at 0x49b4:
21,326 addressed instructions, with no missing addresses, unknown instructions
or stderr. This is decoding coverage, not an exhaustive semantic audit.
The original binary, full dump and symbol table remain private, outside Git.

## FILE creation and path ownership

The exported host-string overload of FILE_New starts at 0x12c48. It requests
0x60 bytes through U_MemTrackedObject allocation at 0x12c6c and calls the
FILE_Spec constructor at 0x12c78, returning the resulting pointer. The exception
landing pad releases that allocation through the matching host deallocator
at 0x12ca4 and resumes unwinding. It is not a char-pointer constructor returning
an error code, and it must not be declared noexcept.

The constructor begins at 0x4d54. It reads the source string's tag at +0x17.
The short branch copies a 24-byte representation to a temporary; the long branch
calls the producing runtime's string copy constructor helper at 0x4dc8.
It normalizes the copied path and constructs owned File/Dir members from it
(0x5368, 0x538c). Its initialized stream slots, resource state at +0x48 and
bundle slot at +0x50 are empty. This supports copying/ownership of the input
rather than retaining the caller's string-object address. It does not justify
manually manufacturing the 96-byte FILE_Spec or recreating a host allocator.

FILE_IsDir delegates to the stored Dir's Exists operation, rather than reading
an immutable type flag. A future probe therefore still needs independent
ownership, no-link and directory checks, not just a truthy constructor result.

The exported FILE_InqUnicodePath at 0x4a70 returns a separate host string. The
output address is retained from x8 at 0x4a80 and forwarded to FullPath. Callers
must manage a returned object, not read a borrowed char pointer from x0.
The inspected callers use 24-byte string storage and the matching host string
destructor/recycler; this does not certify another release's representation.

A tempting char-pointer helper, FILEp_NewSpecFromFullPath at 0xe2a4, is a local
symbol, not an exported alternative. The local FILEp_InqFullPath at 0x18d18
passes a fixed 256-byte capacity to U_CopyString at 0x18d80-0x18d8c. It is not an
appropriate substitute for the gate's possible 4096-byte paths. Neither helper
is bound using a hardcoded offset.

Actual FILE import ordinals resolve U_AsciiToUTF16String to U.dylib (ordinal 4)
and the matching host UTF-16 string destructor to dvacore.framework (ordinal 2).
Their implementations and resident identities were not inspected by this upload.
A future producer/destructor pair must come from verified compatible host
modules; using this process's unrelated std::string/std::u16string is forbidden.
This record does not request another per-library collection.

## Release is not just free, and not unconditionally successful

FILE_Dispose at 0x130cc first calls FILE_IsOpen; there is no leading null guard.
It can close streams, close resource state, inspect the bundle at +0x50 and call
OS_UnloadModule at 0x13130 for a non-main-application bundle. That dependency
resolves to dvacore. If a close operation fails, the function can return a
nonzero status before destruction; it also has paths into throwing helpers.
On the normal successful path it invokes the FILE_Spec destructor at 0x13140
and the matching tracked deallocator at 0x13144.

Consequences: never pass null, never substitute delete/free, never discard the
status, and never interpret a nonzero/throwing release as permission to retry.
Any uncertain ownership must be recorded as a failed, nonreplayable transaction.
The no-scan probe must be limited to its own newly created ordinary directory
specification; it must neither open its resources nor acquire module ownership.
It must not dispose a FILE_Spec borrowed from an installed plugin. The root
path alone is not proof of those ownership properties.

## Recheck of the later PLUG scope

The previously received PLUG binary was rehashed unchanged:
`12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22`.
Its ordinary file-enumeration branch creates separate child specifications,
calls ScanFile at 0xf028 and disposes the child at 0xf044. The root passed to
ScanFolder is used to obtain its Dir, not as that per-file resource object.
These are useful ownership observations, not a guarantee over every alias or
exception path.

Additionally, PLUG_Search calls PLUGp_DoCleanups at 0x8ef4 after its root loop.
DoCleanups iterates the cleanup list at sack+0x10 and invokes its stored callbacks
(0xeba8 or 0xebe8). This iteration is not filtered by the one requested root.
With the default sack, passing just one folder does not by itself constrain
all end-of-pass behavior. The active callback list and each callback's effects
remain unobserved. Do not silently remove, replace or bypass these callbacks;
review them before connecting a later resource-search backend. This narrows the
previous single-root design; it does not prove that a particular callback is
harmful or that the historical failure was caused by cleanup.

## Implemented ABI primitive, deliberately not a host adapter

Code/test commit: `847b7ded4be07995b42facfba38bac0f9d52f060`.

`HostIndirectResult_arm64.S` transfers a separately verified callee address,
one pointer argument and result storage to x16, x0 and x8 respectively, then
performs a tail transfer. It does not allocate, create a host object, resolve
symbols, validate pointers, load a library or invoke anything automatically.
There are no Adobe offsets or API addresses in it. It rejects non-Apple,
non-arm64 and arm64e builds. It is linked only into the new owned test, not into
the Agent, existing scoped module or product package.

This solves only a machine-call marshalling boundary: a host producer can fill
proper result storage without a false C++ declaration claiming a borrowed
pointer return or a fabricated host std::string type. Callee identity, storage
size/alignment, object lifetime, decoder and matching destructor remain the
responsibility of a separately reviewed binding. The primitive is unsafe for
arbitrary targets and must never accept targets from requests or users.

The original four-instruction implementation uses the standard indirect-result
register described in [AAPCS64](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst),
sections 6.1.1 and 6.9. Apple-specific ABI behavior must also follow
[Apple's arm64 guidance](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms).
These specifications describe calling conventions, not the private FILE ABI.
No external implementation was copied and no LLVM host-string definition was
substituted for Adobe's type.

The owned C++ test producer returns a nontrivial 24-byte object with its own
allocation and destructor. It checks the pointer argument, result contents,
adjacent canaries, explicit destruction, repeated ownership, propagation of a
C++ exception through the tail transfer and caller cleanup. There are six named
cases, run at -O0 and -O2. The test object is NOT Adobe's string or allocator.
No inference that FILE_New ran is permitted from these results.

## Verification and evidence

The private review validates FAT/load-command/section bounds and symbol kinds.
Sixteen BL instructions were independently decoded from raw machine words and
nine additional instruction anchors checked: 25 structural assertions PASS.
Additional export checks distinguish globals from local/debug symbols.

| Derived file | SHA-256 |
|---|---|
| FILE disassembly | `c05a36623ca778312d33ca021b98e0df302ae1be19d2042e7f071f1508769581` |
| Private review helper | `ce0ee66382db49f3b516f663237dbf6403d4535d9fe73e1a8a297b285bc52c60` |
| file-contract-review.json | `b54992d465920bf00c84313a067ef4a2e36bf1b31919caab8fca149248ff1339` |

| New source | SHA-256 |
|---|---|
| HostIndirectResult_arm64.S | `01cb3a04dbaf662a55374f14cee95ab8eafd12a22d9795f1509503d027618e19` |
| host_indirect_result.cpp | `f3b55e64b69e6615f3c524222398f4a28b86dcddce3d3aabd9cd85fb08aad493` |
| test_host_indirect_result.py | `89838f317aab2b8c310c1b4016bb5cb91876a804596d51e4e181e0f45f5aecd3` |

Local work reconstructed the verified 5beb51c CI source archive; the intervening
ad1ec8d change was documentation only. Git writes use ad1ec8d's tree as their
base, not a reconstructed tree missing current documents. This is not the Mac
checkout. Local strict C++ syntax, exact cross-assembled instruction bytes,
Python regression (212 collected, 205 PASS/seven macOS-only skips), and 62 Node
mock tests passed. The existing 63 policy and 32 journal cases remain nested in
their original Python tests; counts are not inflated by adding them again.

Both workflows completed successfully for exact code 847b7de:
research `36763733179`, full macOS `36763733162`. The downloaded research
artifact `11119299627` has independently verified SHA-256
`2795055e6cf474bd25e17bc3799cba251da055be59ba779e3432a93c12d83b6f`.
Its source record names the exact commit; Python reports 212 collected,
205 PASS/seven platform skips, and Node TAP confirms 51 + 11 passes.

The downloaded macOS evidence artifact `11119443582` has independently verified
SHA-256 `33c2857cc30696d5685afab9868f7573c0764ff30e38746f17e47a542a0373a9`.
Its source snapshot matches all three new local code/test files byte-for-byte.
The build record identifies clean source, arm64, Xcode 16.4 and Apple clang
17.0.0. Its Python log confirms 212/212 PASS, no skips, and all six owned ABI
cases at both -O0 and -O2, including exception propagation and destruction.
The 63 policy cases and 32 journal cases remain nested in their original tests.
The existing 15 scoped guards and both Node suites passed. Every required
build/sign/package/smoke step in that workflow completed successfully.

This is execution of the new bridge against an owned producer on macOS, not
against FILE.dylib. No Adobe call, full AE integration or new FILE runtime result
is claimed. The native product package was not installed or handed over.
Green CI does not clear prior/unreviewed warnings or the five historical audit
findings. Documentation follow-ups use [skip ci]; CI applies to the exact code
commit, not a later documentation head.

## Next gate and unchanged limits

Native FILE symbol binding, owned host-string construction/destruction,
path comparison and a no-scan create/roundtrip/release probe are NOT connected.
No approved or installable research probe is handed over. Complete these
bindings and verify loaded-function provenance before proposing the separately
authorized no-scan host test. Its acceptance must include no new module load or
unload, unchanged registry/project/PID, exact path roundtrip and successful
single release. A subsequent PLUG experiment additionally requires review of
end-of-pass callbacks and retained state, not merely the FILE constructor.

No new command or user data collection is requested by this record. Current
AE/project/resident identities remain NOT OBSERVED. New live FILE/registration/
apply/render tests are NOT RUN. The latest scoped embedded registration remains
FAIL; RSMB startup-registered apply/render PASS and historical late-registration
FAIL remain separate. No product loader, native request path or authorization
flag was changed. Five full-audit findings remain open; the full static-security
audit was not rerun. Private inputs remain unchanged and outside Git. No main
update, merge, install, restart or release occurred.
