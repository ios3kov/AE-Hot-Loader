# Stage C: candidate count and factory dispatch, offline

Date: 2026-09-30. Review ID: `dispatch-static-20260930-MIHU68`.
Continues `56dd0099630dd30a6afc44de75762946d6fa54f4` on
`research/ordinary-plugin-discovery`. Shared DEVELOPMENT_RULES rechecked:
blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`, unchanged.
AGENTS and PRODUCTION_PLAN remain applicable. No native source changed.

## Scope, acceptance and baseline

Read the supplied offline PluginSupport dump, verify its archive/file hashes
and matching before/after image statements, trace the loader return value and
PiPL-to-factory dispatch, and record independently checkable instruction ranges.
Do not load/execute the image, attach to AE, scan, install, restart, unload,
change flags, invoke private functions, change main, merge or release.

The latest real scoped gate remains FAIL: source `45de0c9`, Build ID
`scoped-0b8c8f122e80`, fixture `88019a1a01a7`; video modules 339 -> 339,
added=0, 785 effect identities unchanged, target absent. The original native
logs were verified in [the preceding record](REGISTRATION_GAP_SAVED_LOGS_2026-09-30.md).
RSMB startup-registered apply/render PASS and historical RSMB late-registration
FAIL remain separate. None of the following static observations repairs them.

## Supplied evidence and identity limits

Upload: `AEHL-offline.MIHU68.zip`, 1,000,074 bytes, SHA-256
`d832134e71c7ad35e9b713e08d47beab67c321903bbd1b59d9d4ac373af62594`.
Exactly five regular files were read into a new private analysis directory;
links, unexpected names and path traversal were excluded. Original inputs
were retained and their hashes checked again after analysis.

| Input | Bytes | SHA-256 |
|---|---:|---|
| disassembly.txt | 6153846 | `2889cfa7ab15df6f614892bdf5348928badf1eae8693cf6a687747a18610c995` |
| symbols.txt | 512601 | `dadb76e01599bc8bcb28b1cfbe02b49192a7186386e70ffdc1fa66cf0fb9ad4d` |
| vtables.txt | 71659 | `f5285bdf9d2341d4bbb8cb6a9d10a985793ddcb836066911404d2bd61ebc7796` |
| image-before.txt | 203 | `f19aced8dd95a2c7b2fb4d6bcbac53a58d3a6df7f07fe17ac308c874289905ac` |
| image-after.txt | 203 | `f19aced8dd95a2c7b2fb4d6bcbac53a58d3a6df7f07fe17ac308c874289905ac` |

The two image statements are byte-identical and contain the expected
PluginSupport image hash
`4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`.
The executable itself was not supplied, so it was NOT independently rehashed
here. Binding the dump to the installed image relies on the user's recorded
collection and matching hash statements, not an independent binary attestation.
Full disassembly, symbols, paths and raw vtable data stay private, not in Git.

## New findings

Addresses below are static image references, never runtime callable addresses.

### 1. Return 1 counts candidates, not registered effects

`ML::LoadPlugins` starts at 0x60a8. It calls `LoadPluginList` at 0x72fc with
the PluginNameList at stack offset 0x40. At 0x731c it saves that list's begin
and end pointers; after cleanup, 0x7390 subtracts them and 0x7394 divides the
byte span by 32 for the return value. The result of `LoadPluginList` is not
used as the returned count.

Therefore the recorded return 1 is consistent with one candidate entry. It
is NOT a count of successfully recognized, created, published or registered
effects. This resolves the previous uncertainty about that return on the
inspected ordinary return path. It does not explain why the fixture failed.

### 2. The final bool selects a restricted factory lane

The product call supplies a final `true`. Static register/stack tracing follows
this value from `LoadPlugins` (0x60c8, 0x72f4), through `LoadPluginList`
(0x7f0c, 0x7f90, restored at 0x83b4), to `AddPlugin` (0x88f8, 0x8900).
The explicit factory override passed at 0x88f0 is null in this path.

`AddPlugin` retains this flag at stack offset 0x4c. Its factory loop uses the
registry at 0xb1218. At 0xfe38-0xfe88, true selects only the factory GUID stored
at 0xb06a0; false follows a different path that excludes that GUID and the one
at 0xb06b0. The initializer at 0x378f8 maps these stored GUIDs respectively to:

- `7a7d3cd3-6b81-48f8-bee0-ec40018a4432`;
- `106f2a5b-3d8d-445a-b520-778e780075f3`.

The same flag also selects a branch containing the `AELibraryPlugins` cache
namespace (0xcff4-0xd054). This is a code/string observation, not an established
public meaning of the bool or proof that true is wrong. The concrete factory
implementation, the ordinary AE startup argument and the last run's actual
receiver are still unobserved. Historical Dynamic late-registration PASS is
not invalidated. Do not flip the flag as an experiment without further evidence.

### 3. Recognition and subsequent handoff already occur inside the scan

`ML::LoadPlugins -> LoadPluginList -> AddPlugin` already contains this path:

- PiPL acquisition through the plugin interface; the observed GetPiPLs dispatch
  at 0xf238 supplies the vector later held at stack offset 0x4f0.
- Factory dispatch at 0x10344 through virtual slot +0x28, supplied with the
  plugin reference, that PiPL vector, an output/status flag and return storage.
- A status check at 0x103b4. The accepted branch contains the recognized-loader
  diagnostic and examines the returned reference.
- For a non-null returned reference, another call to the same factory at
  0x10820 through slot +0x30, passing the reference copied to stack offset 0xd0.

Interpretation: the first dispatch is recognition/construction and the second
is candidate/module handoff. This interpretation is narrower than claiming
that the second slot definitely inserts a video filter into AE's global list.
Its concrete implementation and runtime effects are not present in the traced
indirect call; no guessed private method declaration is added to production.

The registry's registration function is visible at 0x52d28, with unique map
insertion at 0x52e7c. Its presence does not authorize registering a replacement
factory or constructing private objects.

These observations weaken the blanket hypothesis that a separate generic
post-scan dispatch call was omitted. The useful next discriminator is the
selected concrete factory: what PiPL it accepts, what it returns, and how its
handoff reaches the video-module collection. The last failing run could still
have failed before this dispatch or inside it; the static dump cannot decide.

## Reproducibility and checks

The supplied nm symbols, demangled labels and addressed instructions were
cross-checked. A scratch text-review program checked 32 addressed structural
assertions. All 32 passed. These are text assertions, NOT 32 unit/runtime tests.
The following raw-disassembly line ranges identify the main review windows:

| Window | Lines | Key static addresses |
|---|---|---|
| Final flag forwarding | 4588-4600; 6527-6572; 7163-7173 | 0x60c8; 0x7f90; 0x88f8 |
| Candidate-list return | 5757-5807 | 0x731c; 0x7390; 0x7394 |
| Factory GUID filtering | 14713-14742 | 0xfe38-0xfe88 |
| Recognition/status | 14974-15073 | 0x10344; 0x103b4 |
| Returned-reference handoff | 15352-15365 | 0x10814; 0x10820 |
| GUID initialization | 55717-55745 | 0x37958; 0x37970 |
| Factory registry insertion | 84017-84032 | 0x52e7c |

Private derived `dispatch-review.json` records input hashes, assertion locations
and hashes of the selected instruction ranges. Its SHA-256 is
`746f7d059f74cc26eb5e39889a68fd023ba282b292d77a5889675031a5251481`.
Range hashes use the addressed raw instruction lines joined with LF, including
one final LF. Symbol labels are excluded. The record is a derived review aid,
not independently acquired runtime evidence.

No literal runtime vtable pointer was inferred from raw chained-fixup words.
The earlier resource/flipper research remains valid within its own scope;
there is no new proof of parsed PiPL contents or conversion in the failed run.

| Gate | Status |
|---|---|
| Archive/file integrity, matching image statements, input preservation | PASS, supplied-file scope |
| Addressed structural review | PASS, 32 text assertions |
| Current AE/project/loaded identity | BLOCKED, no live access or fresh snapshot |
| Concrete selected factory and runtime rejection reason | BLOCKED, not established |
| New live registration / apply / render | NOT RUN |
| Historical scoped registration | FAIL, unchanged |
| Full Python/Node/native regression | NOT RUN again, documentation-only change |
| Full static-security audit | NOT RUN again; five historical findings remain open |
| New build/package/installable artifact | N/A, no native changes or handoff |

CI remains tied to code `626babcf`: research `36735169447` and macOS
`36735169446` previously PASS. This documentation-only continuation uses
`[skip ci]`; it does not create a new tested native artifact or release approval.

## Next bounded data request and stop condition

First locate the concrete factory implementation using the main AE executable's
symbols and dependency names. The main image is a search target, not yet a
proven owner of the factory. This next collection reads files only; it does not
start AE, execute an image, attach, send scripts or scan plugins. It creates a
new private Desktop directory, checks the image hash before/after and archives
only the four diagnostic text files. No whole-main-image disassembly is needed
at this step. The shell command passed bash syntax checking here; its macOS
execution is NOT RUN here.

```sh
(
set -e
umask 077
BIN="/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/MacOS/After Effects"
test -f "$BIN" || { echo "Файл AE не найден"; exit 1; }
OUT="$(/usr/bin/mktemp -d "$HOME/Desktop/AEHL-factory.XXXXXX")"
/usr/bin/shasum -a 256 "$BIN" > "$OUT/image-before.txt"
/usr/bin/nm -arch arm64 -n -m "$BIN" > "$OUT/symbols.txt"
/usr/bin/otool -L "$BIN" > "$OUT/libraries.txt"
/usr/bin/shasum -a 256 "$BIN" > "$OUT/image-after.txt"
/usr/bin/cmp "$OUT/image-before.txt" "$OUT/image-after.txt"
(cd "$OUT" && /usr/bin/zip -q "${OUT}.zip" ./*.txt)
echo "Пришлите: ${OUT}.zip"
)
```

Stop on missing files, inspection failure or changed image hashes. Do not infer
current AE state from this collection. The earlier PID 78417 observation is
not a fresh project baseline. Installation/restart permission remains consumed.
Before any future risky runtime operation, require a specific falsifiable
hypothesis, bounded evidence plan, fresh host/project identity and separate
authorization. Do not repeat the unchanged scan, change the bool speculatively,
force empty-list notification or invoke private lifecycle operations.
