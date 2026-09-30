# Stage C: PLUG/FLT resource-effect registration, offline

Date: 2026-09-30. Review ID: `plug-flt-route-20260930-WyTSaS`.
Continues `8489d5c51cd08389e1f3c52a0985f53510e361a1` on
`research/ordinary-plugin-discovery`. AGENTS, current status and PRODUCTION_PLAN
were consulted; shared rules remain blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Scope and acceptance

Independently hash the supplied PLUG/FLT binaries, inspect their arm64 code,
locate the resource callback and actual filter-registry publication, and
cross-check the relevant branches with raw instruction bytes and symbols.
Preserve inputs. No execution/loading of either library, process attachment,
AE script, scan, installation, restart, native change, main change or release.
Static findings are not a demonstrated safe corrective operation.

## Exact inputs

Upload `AEHL-PLUG-FLT.WyTSaS.zip`: 585716 bytes, SHA-256
`32f35cbdb7ae1d9e24cb55094c40edb4c4bdfb389631214a2511195eb1077935`.
Four expected regular files were read into a new analysis directory. Archive
paths/links were not followed and no existing files were overwritten.

| File | Bytes | Independently calculated SHA-256 |
|---|---:|---|
| PLUG.dylib | 221280 | `12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22` |
| FLT.dylib | 1915248 | `227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256` |
| SHA256-before.txt and SHA256-after.txt, each | 153 | `263bd00fd7fa57260cf612b386af81ba0dbb0b65305c56059e29bac8a32aee94` |

Both received binaries match both byte-identical hash statements. Unlike the
previous text-only dumps, original binary bytes are available for independent
hashing. This still does not identify a library loaded in the previous failed
AE process or establish today's resident modules.

Both containers have one arm64 slice at file offset 0x4000. PLUG UUID is
`D4DDB055-E565-378F-B8F4-33AC0BB2253D`; FLT UUID is
`C8786A71-E313-3B20-9494-359FB56D705A`. Slice hashes and section boundaries
are recorded in the private review JSON. Raw binaries, disassembly and symbol
inventories remain private and must not be committed or redistributed.

## New static registration chain

All addresses below are unslid image references, not callable runtime offsets.

### FLT registers a resource-scan callback

In `FLT_Birth` (0xd7ac), the call at 0xd9c4 reaches `PLUG_InstallScan`.
The callback argument constructed at 0xd9a8-0xd9ac is
`FLT_PLUGScanFunc`, 0x8cf98. Two registered scan file-type keys are read from
FLT 0xb7e58: `eFKT` and `.AEX`. These are the observed scan keys; they are
not a claim that every installed platform/plugin variant is supported.

`PLUG_InstallScan` (0x87e4) stores the supplied callback/context in the scan
record at 0x887c and inserts records into the scan list. It does not itself
perform a new plugin scan. Do not rerun FLT_Birth or replace its callback.

### PLUG_Search reaches the installed callback, subject to path filtering

`PLUG_Search` (0x8a6c) walks caller-supplied file specifications and reaches
`PLUGp_ScanFolder` at 0x8b88. Its file-enumeration path reaches
`PLUGp_ScanFile` (0xf6c0), which matches scan types and invokes the saved
callback through `blr x8` at 0xf91c with prepared scan data and context.
This supplies a concrete static route to the callback installed by FLT.
It is not proof of the active callback or execution in the failed experiment.

An important prerequisite precedes that callback. `PLUG_Birth` (0x5f1c)
retains a caller-supplied path predicate at global 0x18570. `PLUGp_ScanFile`
reads the same global, obtains the Unicode path, invokes the predicate at
0xf750 and skips the file when its result is true (0xf770 -> 0xf93c).
The predicate's concrete startup implementation and its decision for our
fixture are not identified. Adding an unverified PLUG_Search call is therefore
not yet a justified or safe fix.

### Resource PiPL reaches FLTp_FiltSetup

`FLT_PLUGScanFunc` calls `PLUG_GetRoutineCount` at 0x8cfe0, iterates resource
indices, calls `PLUG_GetPiPL` at 0x8d028, and obtains the file path. Its call
at 0x8d084 reaches `FLTp_FiltSetup` (0x8d250), with a PiPL/path and null
IPlugin reference rather than a newly created MEE video module.

The resource operations are visible in PLUG itself:

- `PLUG_GetRoutineCount` opens a resource file and calls Count1Resources for PiPL.
- `PLUG_GetPiPL` reaches `PLUGp_GetPiPL` (0x10074); the uncached route opens
  the resource file and calls Get1IndResource at 0x10150, using index+1.
- The obtained resource bytes reach `ML::PiPL::Create(vector<char>&)` through
  the call at 0x10294.

This is a resource-read/parse route, not proof of its actual bytes, endian
conversion, success or receiver in the historical failing process.

### Setup and PLUG routine registration are distinct from effect publication

`FLTp_FiltSetup` checks the effect kind `eFKT`, entrypoint and other metadata.
It has rejection and incompatible-plugin paths; reaching this function alone
is not a registration PASS.

Its normal path-only/resource lane calls the path overload of
`PLUG_RegisterRoutine` at 0x8e288, records the routine descriptor, performs
post-setup and calls `FLTp_AddEffect` at 0x8e404. The IPlugin lane instead
calls the IPlugin overload at 0x8e4e0 and can reach the same AddEffect at
0x8e68c. PLUG_RegisterRoutine owns a separate routine-descriptor collection;
it must not be equated with insertion into FLT's effect registry.

`FLTp_AddEffect` (0x8b2d4) handles disabled and duplicate cases as well as
new entries. Its new-filter path calls
`FLT_FilterRegistry::RegisterNewFilter` (0x5014) at 0x8bd8c. The latter
appends to the filter vector, inserts into the string-key map (0x5254), assigns
the index and updates preferences-derived filter state. This establishes a
concrete conditional effect-publication path, not merely image discovery.
A broad PLUG scan could also touch duplicates or replacement paths; it must
not be used as an uncontrolled experiment.

### Dynamic setter and module notification do not replace resource discovery

`FLT_SetupAEPlugin` (0x8ef8c) checks kind, excludes `AE.AEGP`, and reaches
FLTp_FiltSetup at 0x8f1ac with the IPlugin/cache route. Its signature is a
candidate for the setter used by MEE, but installation of the actual setter
callback remains unobserved. Its zero return after setup is not independent
proof that a new match was inserted; setup contains early exits.

`FLT_NotifyFilterLoadingDone` (0x8f360) can call FLTp_FiltSetup for supplied
video modules at 0x8f7ec. An empty input skips that loop at 0x8f398. The tail
calls `FLT_FilterRegistry::NotifyFilterLoadingDone` (0x606c); that routine
sets the completed flag at registry+0x48. It does not enumerate missing resource
plugins. Forcing notification with an empty list is not the missing resource
scan, and the larger notifier is not claimed to be a harmless no-op.

## Comparison with our loader and remaining hypothesis

The full current InternalLoader.cpp was compared with the source snapshot in
the previously downloaded successful CI evidence. Its Git blob remains
`df64e125a984199e45cd777eef8c16a556ec393b`. It explicitly calls ML::LoadPlugins,
checks loaded images, computes the new video-module delta and notifies for a
nonempty delta. It contains no explicit PLUG_Search or FLT_SetupAEPlugin call.

The [previous MEE analysis](MEE_RESOURCE_ROUTE_2026-09-30.md) found a conditional
resource-PiPL retention branch that returns no video module. These observations
support a precise hypothesis: the wrapper's AELibrary discovery does not by
itself reproduce the separate ordinary resource-effect PLUG/FLT pass.
The failed run's predicate, receiver and exact dispatch remain unobserved;
this is not a proven runtime root cause or permission to invoke a private API.

Next identify the normal caller's sequence, arguments, path predicate and
ownership/lifetime rules before designing any bounded late-registration test.
Names, raw addresses and inferred structs are not a safe ABI contract.

## Method and checks

Local LLVM 17 read the binaries as files, never as executable code. Final
command for each DLL was `llvm-objdump --macho --arch=arm64 --disassemble
--mcpu=apple-m1 --no-show-raw-insn <DLL>`. Symbols and load commands were read
separately; defined text symbols were distinguished from undefined/debug entries.
The [LLVM command reference](https://llvm.org/docs/CommandGuide/llvm-objdump.html)
is the tool reference, not a source for AE's private semantics.

The default CPU initially left unsupported instruction words undecoded. The
final apple-m1 decoding contains no such unknown words. A separate parser
validated FAT/slice boundaries, UUIDs and exact __TEXT,__text coverage:
14572 PLUG instructions and 165100 FLT instructions. This is decoding coverage,
not exhaustive semantic review or execution of those instructions.

Sixteen direct BL targets were independently decoded from their raw 32-bit
instruction words; eight additional addressed instruction anchors were checked.
All **24 structural assertions** pass. They are not unit or runtime tests.

| Derived output | SHA-256 |
|---|---|
| PLUG disassembly | `a417468bc2003b1da9623fe63768b21d331eeb8d484247db226e205d9f621de6` |
| FLT disassembly | `988a6490a2b3c893923090183b66c17b72804e3b24e32d0f95cfb26e49d225db` |
| static-route-review.json | `3f7b834c8cb91766bdfb51aa0aa481a08774776c8ed29f4dd9fe6d7ab90957db` |
| Private review helper | `b3cb7ea6e9e8cd6bc1eef1acea848c9b5b2618b88d5451e62d192e6f3cf83a21` |

Original input hashes were checked again after review. No product/collector
source changed. Full regression and static-security audit were not rerun for
this documentation-only stage. Prior automated results remain tied to code
1fa62a7; these commits use [skip ci]. Five historical audit findings remain open.

| Gate | Result |
|---|---|
| Received binary and before/after hash agreement | PASS, independent received-file hashing |
| Structural resource-dispatch/registry path review | PASS, static and conditional only |
| Normal startup caller and concrete path predicate | BLOCKED, implementation not identified |
| Corrective late-registration operation | BLOCKED, not demonstrated |
| Scoped embedded late registration | FAIL, historical source45de0c9 / scoped-0b8c8f122e80 unchanged |
| RSMB startup-registered apply/render | PASS, retained one-frame smoke |
| RSMB late registration | FAIL, retained separately |
| New live registration/apply/render | NOT RUN |
| Current AE/project/resident identity | NOT OBSERVED |

## Next file-only request

The already supplied AfterFXLib symbol table imports PLUG_Search from PLUG
(symbols.txt line773, SHA-256
`b95e127cd163e179df6a17aedf0661373457c76323941afe6aae3a84d06302be`).
That earlier collection failed before instruction bodies; it cannot reveal
this call's inputs. AfterFXLib is a concrete caller-search target, not proof of
the path-predicate owner or actual live invocation.

Request only its original binary, not another MEE/PLUG/FLT collection or a new
LLDB sweep. Before/after and copied-byte hashes allow independent analysis here.
The following command passed bash syntax and an isolated Linux dummy-file
copy/hash/archive check with spaces in paths. Its actual Mac run is NOT RUN.

```sh
(
set -e
umask 077
DIR="/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/AfterFXLib.framework/Versions/A"
test -f "$DIR/AfterFXLib" || { echo "AfterFXLib не найден"; exit 1; }
OUT="$(/usr/bin/mktemp -d "$HOME/Desktop/AEHL-AfterFXLib-bin.XXXXXX")"
(cd "$DIR" && /usr/bin/shasum -a 256 AfterFXLib) > "$OUT/SHA256-before.txt"
/bin/cp "$DIR/AfterFXLib" "$OUT/"
(cd "$DIR" && /usr/bin/shasum -a 256 AfterFXLib) > "$OUT/SHA256-after.txt"
/usr/bin/cmp "$OUT/SHA256-before.txt" "$OUT/SHA256-after.txt"
(cd "$OUT" && /usr/bin/shasum -a 256 -c SHA256-before.txt && /usr/bin/zip -q "${OUT}.zip" AfterFXLib SHA256-before.txt SHA256-after.txt)
echo "Пришлите: ${OUT}.zip"
)
```

This copies one file into a fresh private directory. It does not execute the
binary, contact AE, install plugins, alter originals, reset preferences or
restart anything. Stop on a missing file, hash mismatch or error; preserve
partial evidence. Keep the proprietary copy private. Installation/restart
permission remains consumed. Any future risky host test requires separate
authorization, a fresh identified baseline and a specific bounded hypothesis.
