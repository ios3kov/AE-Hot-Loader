# Stage C: resident export binding reaches the directory adapter

Date: 2026-09-30. Continues `1b6f072d38fc66e2b56cf0b98aeea9f5a82c6c8b`
on `research/ordinary-plugin-discovery`. AGENTS and PRODUCTION_PLAN apply.
Shared DEVELOPMENT_RULES were rechecked unchanged at blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Scope and acceptance

Implement bounded, file-hash-pinned lookup of already resident arm64 exports
and connect those addresses to DirectorySpecAdapter. Test the complete chain
on actual macOS with owned libraries, not merely mock symbol maps. Retain the
unified runner, original inputs and previous runtime results. No Adobe code
execution, AE connection, scan, installation, restart, private host call,
native unload, main update, merge or release in this work.

Implemented: resident parser/resolver, NativeDirectoryBinding and an actual
three-provider owned-library integration test. NOT implemented: an approved
Adobe U/dvacore profile, no-scan AEGP entrypoint, live supervisor or resource pass.

## Implementation and the failed intermediate revision

Initial code: `14223926e6a6738d9f6bebe4d2c94c85d9dfa0b3`.
Verified corrected code: **`31868ab019e58600bb0a79f260bcbe2fd69cad00`**,
tree `e20d54d8c6180543e1424f7b5257c087061ec8e8`.

The initial macOS tests failed at compilation: Apple clang rejected five direct
const-void-address to function-pointer conversions. Research run 36776082256
had Linux PASS/macOS FAIL; full macOS run 36776082239 FAILED before product
compilation. The two new native cases did not run in that revision. This
failure is retained, not retrospectively called PASS.

The correction centralizes conversion in Callable<Function>, requires a
function-pointer type and non-null address, and explicitly removes the
inspection pointer's object qualifier before the platform conversion. It changes
no memory or page protection. A callable owned function and null refusal are
now compiled/tested on Linux too. No warning or test was disabled.

### ResidentImageBinding.hpp

The bounded parser accepts thin/FAT32 arm64-all dylib/bundle images with UUID,
read/execute __TEXT, pure regular __text and direct named exports in the trie.
It rejects malformed traversed nodes, cycles, missing/duplicate requested names,
out-of-text results, arm64e, reexports, resolver/TLS/absolute/unknown export
flags. Weak direct definitions remain acceptable inside their pinned image.
Only requested trie paths are inspected, not every possible node. Runtime
addresses come from the observed resident header plus actual export offsets,
not request-supplied addresses or hardcoded function offsets.

The native resolver requires the main thread and an already loaded exact-path
image. It uses descriptor-relative no-follow file reads, expected SHA-256,
bounded sizes and before/after file metadata. It compares resident header/load
commands and the complete __text bytes against the pinned file. Image names and
code use the existing current-process memory reader. It never dlopens, dlsyms,
dlcloses, attaches, runs a resolver or invokes the resolved function.

Repeated dyld snapshots detect observed list changes, but are NOT a loader
lock or lifetime lease. Apple's [dyld manual](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/dyld.3.html)
warns that count-based iteration is not thread-safe under concurrent image
loading/unloading. Transient remove/readd can escape comparisons. Future
integration must establish lifetime/quiescence before calling an address;
main-thread execution alone does not exclude other threads' loading. No
race-free, hostile-process or complete memory-integrity guarantee is made.

Export encoding/flags were cross-checked with Apple's
[mach-o/loader.h](https://github.com/apple-oss-distributions/xnu/blob/main/EXTERNAL_HEADERS/mach-o/loader.h).
This is file-format documentation, not an Adobe ABI or safe late-call contract.
No dyld implementation was copied.

### NativeDirectoryBinding.hpp

The table connects four FILE operations, U's ASCII-to-host-string producer and
dvacore's host-string destructor, using exact names/owners from inspected
imports/exports. It requires three nonzero binary hash pins and exact expected
paths. A profile must be reviewed immutable build data, not IPC/user input,
permission or invented U/dvacore hashes. Bind performs no directory operation.

It wires the existing arm64 indirect-result primitive and self-memory reader.
Actual U/dvacore string behavior and cross-module compatibility still require
implementation review and a separately authorized host probe. A hash identifies
bytes, not a compatible ABI. Tables must not be cached across host requests or
used across unload. The existing ASCII-only path restriction remains unchanged.

## Checks: real owned libraries, zero Adobe calls

The native test compiles three distinct providers under a temporary Owned.app:
our spec provider, string producer and destructor. Matching export spellings
exercise the concrete binding; their deliberately owned string/allocator is
NOT Adobe's implementation. The test explicitly loads its own built libraries;
the resolver does not load missing images. It then resolves the table, creates
an owned directory specification, verifies its exact path, destroys two strings
and disposes the spec once. Completion/cleanup counters and unchanged resident
image lists pass. Tests also check absent-image, wrong-hash, off-main-thread and
incomplete-profile refusal. Only owned test libraries are unloaded afterward.

The received FILE.dylib was separately parsed strictly as bytes. Named exports
agree with previous disassembly: New 0x12c48, IsDir 0x1315c, InqUnicodePath
0x4a70, Dispose 0x130cc. These are offline assertions, not runtime binding
constants. Its SHA-256 remains
`df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864`.

| Check for corrected code 31868ab | Result and scope |
|---|---|
| Local unified Linux | 238 collected: 229 PASS, nine explicit macOS skips; Node 62 PASS |
| Supplied FILE export parsing | PASS, four named exports; Adobe calls=0 |
| Local parser ASan/UBSan/leak detection | PASS, not Adobe memory/runtime certification |
| Bounded parser mutation exercise | 2500 deterministic inputs completed without sanitizer diagnostics; not 2500 additional unit tests |
| Focused portable clang analysis | No diagnostics; not the full product/security audit |
| Research CI 36776672299 | PASS, both Linux and macOS jobs |
| Downloaded macOS unified report | 21 stages PASS; 238/238 Python, no skips; 62 Node and 15 existing scoped guards PASS |
| Native three-provider directory lifecycle | PASS on actual macOS arm64; Adobe calls=0 |
| Full macOS CI 36776672316 | PASS, all build/sign/package/smoke/archive-verification steps complete |
| Actual U/dvacore implementations and Adobe profile | BLOCKED: implementation bytes/pins unavailable among inspected inputs |
| Live no-scan AE probe / resource registration | NOT RUN; no approved entrypoint or supervisor connected |
| Full static-security audit | NOT RUN again; five historical findings remain open |

Two Python cases were added. Internal checks and previous 27/63/32 native cases
are not counted again as additional Python tests. Full product packaging is
still a separate CI workflow, not part of the local offline runner.

## Evidence identity

Local work reconstructed the verified ab5c1cb source evidence archive
11124432691, SHA-256
`eb4ff1997aa7d14c3acb1fda567f41654235528a53a4da3a6d10bff2256b055a`.
The synthetic local Git history is not remote history or the user's checkout.
Git writes were based on the actual upstream 1b6f072 tree, preserving all newer
documents. All five new source hashes agree with corrected CI's tracked inventory.

Both corrected unified Actions archives were downloaded; every inner manifest
entry and the exact source commit were verified. macOS report identifies macOS
15.7.9 arm64 and Python 3.14.7. Full product CI completion was checked through
job/step records; its product ZIP was not independently downloaded or installed.
The initial failure log was read. Its known redundant Rust action input warning
is not silently cleared by green corrected jobs. Documentation uses [skip ci];
verified code identity remains 31868ab.

| Evidence | ID / SHA-256 |
|---|---|
| macOS unified Actions archive | 11125223951 / `e26c205b1012698d81fcb7bb1e2a4a0618065decd712808efb69666abc3d6181` |
| macOS inner report | `deb9ac152bc5461b3786a920cc50852d419680c7200f5f43a122ba8b29bd63ce` |
| Linux unified Actions archive | 11125893839 / `d1961b64f17d1cb59fc3cd00bc4bd1b90572eb84ddafacf1bd74ba2e921cda59` |
| Linux inner report | `54e729bb6fd8332c555a19894e9fc1b1c63013376f60cd2a6ad6458755d20540` |

| New source | SHA-256 |
|---|---|
| ResidentImageBinding.hpp | `89011529414b4ed8dd13946077c0b160a4b4d343164ea18b4d6d4b4af9857d96` |
| NativeDirectoryBinding.hpp | `ee6d8d5d9db9056850ea7d50f6b76d328880c6df0eb99e00fa22d4673b36eb94` |
| resident_image_binding.cpp | `141babee06aa9b8d8867f02277bd83c06f413f3e057528e013cb69f0148fe0d1` |
| directory_binding_fixture.cpp | `617acf9568914d5f196b3e6aa8073e7c1f34ff486e8e215d5c394aab4bb5e273` |
| test_resident_image_binding.py | `f33aa5aa4e58e88baf95aa00e5f56e487f77e8ac9e36d0b5abfcf64715ad3b71` |

## Next safe boundary and one file-only request

Review the actual U/dvacore producer/destructor before freezing an Adobe
profile. Import ownership is known, but implementation behavior and expected
hashes may not be invented. Request these two files together, not another SDK,
FILE/PLUG/FLT collection or blanket disassembly. This command passed bash syntax
and a complete owned dummy-file copy/hash/archive test, including spaces and
unchanged source bytes. Actual Mac collection is NOT RUN here.

```sh
(
set -e
umask 077
DIR="/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks"
REL="dvacore.framework/Versions/A/dvacore"
test -f "$DIR/U.dylib" && test -f "$DIR/$REL"
OUT="$(/usr/bin/mktemp -d "$HOME/Desktop/AEHL-U-dvacore.XXXXXX")"
/bin/mkdir -p "$OUT/dvacore.framework/Versions/A"
(cd "$DIR" && /usr/bin/shasum -a 256 U.dylib "$REL") > "$OUT/SHA256-before.txt"
/bin/cp "$DIR/U.dylib" "$OUT/"
/bin/cp "$DIR/$REL" "$OUT/$REL"
(cd "$DIR" && /usr/bin/shasum -a 256 U.dylib "$REL") > "$OUT/SHA256-after.txt"
/usr/bin/cmp "$OUT/SHA256-before.txt" "$OUT/SHA256-after.txt"
(cd "$OUT" && /usr/bin/shasum -a 256 -c SHA256-before.txt && /usr/bin/zip -q "${OUT}.zip" U.dylib "$REL" SHA256-before.txt SHA256-after.txt)
echo "Пришлите: ${OUT}.zip"
)
```

This reads two named files and writes one new private archive. It never executes
them or contacts AE. Stop on error, preserve partial data and keep binaries out
of Git. No security settings, permissions on originals or existing files change.

After provider review, resolve the lifetime guard and wire a separately identified
one-shot no-scan AEGP and external supervisor. Fresh host/project/loaded identities
and separate explicit permission remain mandatory. The no-scan probe must not
open plugin resources or acquire module ownership. PLUG additionally needs its
cleanup callbacks/retained state reviewed. Existing scoped commands still use
the historical loader; do not run them expecting this binding to be connected.

No callback/predicate replacement, Birth/InitIterator/RequiredPreSearch replay,
global roots, forced notifier, cache reset, bool change, native unload or unchanged
scan. Original installation/restart permission remains consumed.

Scoped registration remains FAIL (45de0c9, scoped-0b8c8f122e80, fixture88019a1a01a7).
RSMB startup-registered apply/render PASS and late-registration FAIL remain
separate. Current AE state is NOT OBSERVED. Product loader, installed components,
projects/preferences, third-party effects, main and release state are unchanged.
A/B/D, live registration, separate apply/render and release gates remain open.
