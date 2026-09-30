# Stage C: resource PiPL takes a separate retention path

Date: 2026-09-30. Review ID: `mee-resource-route-20260930-tk18ws_t`.
Continues `454806c96d1c2f869d5d00461a03b3182ce52c83` on
`research/ordinary-plugin-discovery`. AGENTS.md, current status and the plan
were consulted. Shared DEVELOPMENT_RULES blob remains
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Scope and predeclared acceptance

Validate the supplied v3 collection, trace the concrete factory's PiPL
predicates, return values and two collection fields, cross-check the virtual
method mapping against the previously supplied PluginSupport data, and record
what remains unobserved. Keep original inputs unchanged. No new scan, attach,
AE script, installation, restart, unload, private host call or native change.
This is static analysis, not a demonstrated corrective registration operation.

## Inputs and verification

Upload `AEHL-MEE.tk18ws_t.zip`: 125458 bytes, SHA-256
`359fbc13c87be184403a05bb43361f70b0b0410f2b821c3f043804a896051dbd`.
It contains 13 flat regular files: record.json and 12 payloads. All 12 payload
hashes match the record. Safe copying used a new private analysis workspace;
no archive paths or links were followed over existing files.

| Input | SHA-256 |
|---|---|
| disassembly.txt | `22fbac8628ea1c789c7c64402dbb94d61402eda97e9db7803a835be1597f4b80` |
| symbols.txt | `a89e7bbe32f74c9cc1a4f3955cc561942b95a44399f97059d3cf627b50995fa6` |
| selection.json | `14519930589a94e173d03a8b32717bc724ab649983e64336f0899b1b6b091faa` |
| inspect.lldb | `1ba7dd46030f412a53cf0ce3b00416c4ee09728fae33e11e2f371aaa83a8aa91` |

The unchanged v3 collector bytes match SHA-256
`1e198f5bf92e125c6577b9d60dd30754eb6ba687b290a9df547f22fb982c2d7e`,
Git blob `57d992404cdb7e1cda82341db1c3e795173efeb9`, code checkpoint
`1fa62a775b0b0197f51c4e93b86caefba95c43d4`. Its selection was independently
recomputed from the supplied symbols, and its actual transcript validator was
run on the saved output: **41 windows, 3529 instructions, PASS**. All requested
addresses and final quit are present; stderr is empty. Total selected span is
14116 bytes; no selected window is capped or omitted. This is complete coverage
of the requested windows, not proof of exhaustive function/factory coverage.

The collector reports capture_status=PASS and matching before/after MEE hash
`18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344`.
Its main-image hash is
`464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6`.
The DLL and main executable themselves were not supplied, so these image
hashes remain collector statements, not independently rehashed binaries here.
The prior failed v2 capture is not retrospectively changed to PASS.

Additional source material: the original complete PluginSupport dump in
`AEHL-offline.MIHU68.zip`, identified in
[the static dispatch record](REGISTRATION_DISPATCH_STATIC_2026-09-30.md).
That image's reported SHA-256 remains
`4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`.
Raw disassembly, binary paths and symbol inventories remain private, not in Git.

## New static finding

The selected factory was previously mapped to
`ML::AELibraryVideoFilterFactory`, GUID
`7a7d3cd3-6b81-48f8-bee0-ec40018a4432`. The new bodies expose a deliberate
separation between a retained IPlugin reference and a created video module.
Addresses below are references into identified offline images, not callable
runtime addresses or a supported private ABI.

### Resource-derived PiPL returns no video module

In MEE `CreateUnknownImpl` (0x7dc8-0x8dfc), the selected descriptor is examined
through two virtual slots. With the concrete ML::PiPL mapping described below,
slot +0x88 is IsNull and slot +0xb0 is IsCreatedFromResource.
The relevant decisions are at 0x80c0-0x810c.

When the resource predicate is true and the normal branch completes:

- The source IPlugin reference is appended to a separate collection beginning
  at factory+0x20; its end/capacity are read at +0x28. The slow-path append at
  0x8324 is explicitly typed as vector<InterfaceRef<IPlugin>>.
- A trace annotation at 0x84bc names this collection
  `mRetainedModulesHandedOverToPLUG`. This identifies a retention purpose;
  it does NOT prove that a PLUG registration call happened.
- The branch joins 0x859c-0x85a4, writes zero to the output status and returns
  a null module reference. It does not reach the module-construction lane.

This is conditional control-flow analysis, not a recorded result of those
predicates in the failed live experiment. It also does not claim that every
resource descriptor, host version or third-party plugin behaves identically.

### Retention is not publication to GetModules

`CreateUnknown` calls the implementation at 0x7bc0. Its check at 0x7be0 skips
video-module publication when the returned reference is null. A non-null
reference instead reaches the typed video-module vector at factory+0x08;
0x7c54 and 0x7c5c expose that field and append operation.

`GetModules` reads this +0x08 vector at 0x8ea4, not the retained-IPlugin vector
at +0x20. Thus retaining a resource plugin does not make it appear in the
video-module list read by MEE_GetVideoFilterModules.

For this concrete factory, `AddModuleToList` at 0x8e80 is only a return
instruction. The generic post-recognition virtual call seen in PluginSupport
is therefore not evidence of a missing useful AddModuleToList operation here.
Forcing this method is not a registration fix.

PluginSupport's status test at 0x103b4 skips the recognized-result handling
when the status is zero. Together, these paths are consistent with the
historical loaded-image/no-new-module observation. They do not demonstrate
which branch was actually taken in that historical process.

### Non-resource lane already contains a host callback

A non-null, non-resource descriptor can proceed through the hardcoded-cache
check and entrypoint resolution, then construct an
AELibraryPluginVideoFilterModule (0x8620), initialize it (0x86d8), and call
SetupFilter (0x8820). SetupFilter obtains MEE_GetAELibPluginSetter at 0xbc30
and invokes its callback at 0xbd24. The sign check at 0xbd74 sends a negative
callback result to the failure path. The current installed callback and its
concrete implementation have not been observed.

This helps distinguish the dynamic-compatible lane from the resource-retention
lane. It does not authorize calling a retained callback, spoofing resource
provenance, constructing a private module or changing the existing final bool.

## Virtual method mapping and its limits

The prior PluginSupport symbols name ML::PiPL's vtable at 0xab100. Constructor
instructions at 0x19484-0x1948c set the primary address point to 0xab138.
Interpreting the serialized entries consistently with Apple's 64-bit chained
rebase layout gives these cross-checked targets:

| Slot | Serialized entry | Matching symbol address | Method |
|---|---|---|---|
| +0x50 | 0xab188 | 0x461ec | GetEntryPointName |
| +0x60 | 0xab198 | 0x46220 | GetReservedInfo |
| +0x88 | 0xab1c0 | 0x46228 | IsNull |
| +0xb0 | 0xab1e8 | 0x46304 | IsCreatedFromResource |

IsNotNull separately calls +0x88 and inverts the result at 0x462f0-0x462f8.
IsCreatedFromResource compares two stored bounds at 0x46304-0x4630c and returns
whether they differ. The neighboring getters and constructor are independent
consistency checks within the supplied static data.

The layout reference is Apple's
[fixup-chains.h](https://github.com/apple-oss-distributions/dyld/blob/main/include/mach-o/fixup-chains.h),
reviewed blob `d5e1b3bdf8e4e2dcec2359313a8f3146efbd64b0`:
36-bit target, 8-bit high part, reserved bits, next-link field and bind bit.
The original chained-fixup format header and a live receiver pointer were not
supplied. No raw serialized word is treated as a resident function pointer;
this mapping does not establish the failed run's concrete receiver.

## Checks and evidence record

A private file-only review script verifies **33 addressed structural assertions**
and the four mapped table entries. All pass. These are assertions about supplied
text and symbols, not 33 unit tests, executed Adobe branches or runtime tests.
The independent review JSON records addresses, instruction/range hashes,
source identity and limitations. SHA-256:
`24ec752e54dd10730c214a7419e0babf8a6da9800e4f03945768c5a0628a995e`.
Private chat workspace filename: `factory-route-review.json`.
The original archive and payload hashes were checked again after analysis.

No product/collector source changed. Full Python/Node/native regression and
static-security audit were not rerun for this documentation-only continuation.
Previous CI belongs to code 1fa62a7, not a new native candidate. Documentation
commits use [skip ci]; five historical audit findings remain unresolved.

| Gate | Status |
|---|---|
| Supplied archive integrity and requested transcript completeness | PASS, file-only scope |
| Resource-retention/module-vector branch review | PASS, conditional static interpretation |
| Actual resource predicate and receiver in failed live run | NOT OBSERVED |
| A safe corrective registration operation | BLOCKED, not demonstrated |
| Scoped embedded late registration | FAIL, original source 45de0c9 / Build ID scoped-0b8c8f122e80 |
| RSMB startup-registered apply/render | PASS, retained historical one-frame smoke |
| RSMB late registration | FAIL, retained separately |
| New live registration/apply/render test | NOT RUN |
| Current AE/project/loaded identities | NOT OBSERVED |

## Next safe discriminator

Inspect PLUG and FLT offline to locate the resource-effect registration path,
its normal caller and relation to the setter callback. MEE's dependency list
names both DLLs; its symbol table attributes PLUG_RegisterRoutine imports to
PLUG. These names are search anchors, not proof that an AEGP scan routine is the
ordinary effect path or that any private call is safe during a running session.
The retention branch itself contains no demonstrated PLUG registration call.

Do not repeat the unchanged MEE collection or in-host scan. Request original
PLUG.dylib and FLT.dylib bytes together in a private archive, plus matching
before/after source hashes and verification of the copied bytes. This avoids
another incomplete heuristic disassembly request and enables independent
binary hashing and offline cross-reference analysis here. The two DLL hashes
will be new observations, not retroactive proof of the prior run's loaded images.
Do not commit or redistribute the proprietary binary payloads.

Available local LLVM 17 successfully read an owned synthetic arm64 Mach-O object
compiled with clang; the object was never executed. This checks local offline
reader availability, not complete support for every command or the unavailable
Adobe DLLs. The collection command below passed bash syntax checking and a
Linux isolated-fixture copy/hash/archive check with spaces in paths and original
source bytes preserved. Its actual Mac execution has not happened here.

```sh
(
set -e
umask 077
DIR="/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks"
OUT="$(/usr/bin/mktemp -d "$HOME/Desktop/AEHL-PLUG-FLT.XXXXXX")"
(cd "$DIR" && /usr/bin/shasum -a 256 PLUG.dylib FLT.dylib) > "$OUT/SHA256-before.txt"
/bin/cp "$DIR/PLUG.dylib" "$DIR/FLT.dylib" "$OUT/"
(cd "$DIR" && /usr/bin/shasum -a 256 PLUG.dylib FLT.dylib) > "$OUT/SHA256-after.txt"
/usr/bin/cmp "$OUT/SHA256-before.txt" "$OUT/SHA256-after.txt"
(cd "$OUT" && /usr/bin/shasum -a 256 -c SHA256-before.txt && /usr/bin/zip -q "${OUT}.zip" PLUG.dylib FLT.dylib SHA256-before.txt SHA256-after.txt)
echo "Пришлите: ${OUT}.zip"
)
```

The command only copies two explicitly named files and writes a new private
Desktop archive. It never executes either DLL, starts or contacts AE, installs
plugins, changes permissions/security settings, removes files or updates Git.
Stop on missing files, changed hashes or tool error; preserve partial evidence.
A future risky runtime experiment still requires separate authorization, a
specific falsifiable hypothesis and fresh host/project/runtime identities.
The prior installation and one-restart permissions remain consumed.
