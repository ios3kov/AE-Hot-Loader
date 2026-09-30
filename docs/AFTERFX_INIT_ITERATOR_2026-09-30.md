# Stage C: AfterFXLib separates plugin initialization from preset scanning

Date: 2026-09-30. Review ID: `afterfx-init-route-20260930-ArhCU8`.
Continues `61b14fafac48339a47a86d3bdc35f48e28368d2c` on
`research/ordinary-plugin-discovery`. Shared DEVELOPMENT_RULES were rechecked
at unchanged blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
AGENTS, the current status and PRODUCTION_PLAN Stage C remain applicable.

## Scope and acceptance

Verify the supplied AfterFXLib binary against both source-hash statements;
resolve its relevant imported-call references and startup sequence; separate
preset scanning from ordinary effect discovery; retain exact addresses and
limitations. Read files only. No Adobe binary was loaded or executed; no AE
request, debugger attachment, scan, installation, restart, lifecycle call,
production source change, main change, merge or release.

The prior PLUG/FLT chain remains conditional static evidence, not a confirmed
late-registration operation. A PLUG_Search import alone did not establish its
purpose. This review resolves the observed direct call's purpose without
reclassifying the historical live results.

## Exact received inputs

Upload `AEHL-AfterFXLib-bin.ArhCU8.zip`: 13,758,601 bytes; SHA-256
`89d5458ed5713e641259eed79eb30936d920bc7b79d201b9b9c2a189cb832520`.
Exactly three expected regular files were copied to a new private analysis
workspace. Unexpected names, symlinks and oversized entries were rejected.
Original uploaded files were not overwritten.

| Input | Bytes | Independently calculated SHA-256 |
|---|---:|---|
| AfterFXLib | 45,998,720 | `ce3aa2f16fe5449a77379a6b622e1a221596e511b86f7708dd3e2f7a3cced01a` |
| SHA256-before.txt, each matching SHA256-after.txt | 77 | `ee5db69560fd9d4b3f280e74511b08bea3b40fb4d70aa534b5f6d2962a57be6c` |

The binary hash equals the value in both byte-identical source statements.
The arm64 slice starts at container offset 0x4000, size 45,982,336, UUID
`EDC800D6-9E4B-3A03-9BBB-8239F3F6EEA5`. These identify received bytes, not
what was resident in the prior failed AE process or the current host.
The earlier supplied PLUG/FLT binaries were also rehashed and still match
[their recorded identities](PLUG_FLT_RESOURCE_REGISTRATION_2026-09-30.md).

## Findings

All addresses below are unslid file-analysis references, not runtime addresses
or a supported private ABI. No function is proposed for immediate invocation.

### 1. The direct PLUG_Search caller is a preset search

Raw branch scanning of AfterFXLib's __TEXT,__text finds one direct B/BL
reference to its PLUG_Search import stub (0x168dbf0): the BL at 0xa42bf4,
inside `CFx::PresetFxSearch`, beginning at 0xa427e0.

Its caller `CFx::DoFxScan` (0xa42d54) creates its own PLUG sack at 0xa42dfc.
It installs a scan callback at 0xa42e50 with one file-type key, constructed
as 0x46614658 (`FaFX`) at 0xa42e28-0xa42e30, then calls PresetFxSearch at
0xa42e6c. Its diagnostics explicitly refer to loading presets; it disposes
this sack on its normal exit path. This differs from the earlier FLT scan
callback registered for the observed eFKT/.AEX keys.

The direct AfterFXLib PLUG_Search import therefore does NOT supply the missing
ordinary-effect startup call. Copying DoFxScan or its arguments into our loader
would conflate preset handling with resource-effect registration.
This result does not invalidate the independently mapped PLUG/FLT effect chain.
Only direct B/BL references to the known stub were enumerated. Indirect calls,
inlining, other images and other dispatch forms are not excluded.

### 2. Plugin initialization advances an external aelib iterator

`MainMain` (0x7b42f4) calls `aelib::Birth` at 0x7b4410 through import stub
0x16951b0. The caller supplies client/options values and a std::function
callback, with return storage at stack+0x270. Their complete semantics and
safe late-session use are not inferred from the argument registers.

The actual undefined symbol's Mach-O library ordinal resolves to:
`@executable_path/../Frameworks/aelib.framework/Versions/A/aelib`.
This is a different binary from AfterFXLib. The same dependency owns the
import `aelib::InitIterator::operator++`, stub 0x169518c.
Debug/STAB records were excluded when classifying actual imports.

`CEggApp::BirthPlugins` (0x766b24) receives this iterator type. Its normal
path advances the iterator through the call at 0x766d84 until the stored
stage reaches at least 0x21. After suite/other initialization, it advances
again at 0x766f5c until the stage reaches at least 0x22. Immediately after that
loop, 0x766f70-0x766f74 selects the diagnostic marking plugin scan completion.
These numeric thresholds are observed caller-side comparisons, not assigned
names for undocumented aelib enum entries.

Only later, at 0x76708c, this routine calls `CFx::DoFxScan` under a separate
preset-scan diagnostic and UI conditions. The sequence separates the plugin
initialization step from the later preset scan; the PLUG_Search call above
belongs to the latter.

Other inspected BirthPkgGrp functions also advance the external iterator to
stage thresholds. Therefore aelib is a concrete implementation boundary to
inspect, rather than another guessed owner based on a generic function name.
Neither PLUG_Birth nor FLT_Birth appears as an actual undefined import in this
AfterFXLib symbol table. This negative import observation is not proof they
cannot be reached transitively.

### 3. What is still unknown

The body of InitIterator::operator++ and its stage dispatch are in aelib,
which has not been supplied. The normal resource PLUG_Search call, installation
of the PLUG path predicate, its decisions for the fixture, and the actual
setter installation are not established by this AfterFXLib alone.

The next discriminator is the aelib stage implementation and its calls to the
already mapped MEE/PLUG/FLT boundaries. Do not replay Birth or advance a live
startup iterator to test this: a startup lifecycle operation is not a safe
late-registration API. No broad scan, forced notification, guessed flag change,
private teardown or fabricated host-owned structures are authorized.

## Method and validation

LLVM 17 read symbols, load commands and seven selected function windows using
`llvm-objdump --macho --arch=arm64 --disassemble --mcpu=apple-m1
--no-show-raw-insn --dis-symname <exact-symbol> <file>`.
The [LLVM tool reference](https://llvm.org/docs/CommandGuide/llvm-objdump.html)
was consulted; it is not a source for Adobe private semantics.

An independent file parser checked FAT/slice/section bounds, actual nlist
records, library ordinals and the LC_DYSYMTAB indirect-symbol mapping. It scanned
5,903,141 aligned text words for direct B/BL encodings (836,121 matching words).
This is a syntactic reference search, not execution or full semantic review.

Seven windows contain 5,016 decoded instructions. Their addresses are
contiguous and agree with the next defined-text-symbol boundary; no unknown
instruction words occur in those windows. A next-symbol boundary does not
prove exhaustive source-function coverage, particularly for split/cold code.

The private verification helper checks 40 structural assertions: raw import
stub mappings, seven independently decoded BL destinations, direct-reference
counts, two import dependency ordinals, absence of two specific imports,
window coverage/extents, nine instruction anchors and post-analysis input
hash. All pass. They are NOT unit tests, a live trace, or a registration PASS.

Main windows: PresetFxSearch 0xa427e0-0xa42d54; DoFxScan 0xa42d54-0xa42f64;
MainMain 0x7b42f4-0x7b6150; BirthPlugins 0x766b24-0x76792c. Additional iterator
controls: BirthPkgGrpA 0x760250-0x7602f8; C 0x764c68-0x76527c;
D 0x76527c-0x766638. Bounds are start-inclusive/end-exclusive.

Private derived `afterfx-init-review.json` SHA-256:
`3cbba1e0e48884e9c299689b84a8e044b73d8dcf4e2e8d4b1a80e0cfe9eaa442`.
It records input/slice identities, assertion locations and raw-window hashes.
Original proprietary binaries, symbol inventories and instruction text remain
private and are not committed or redistributed.

## Gates and preserved results

| Gate | Result |
|---|---|
| Received-file hash and both source statements | PASS |
| Addressed static checks | PASS, 40 structural assertions, not runtime tests |
| Purpose of the observed direct AfterFXLib PLUG_Search call | Presets, not the missing resource-effect startup call |
| aelib iterator dispatch / concrete path predicate | BLOCKED, aelib implementation bytes unavailable |
| New live registration, apply/render or host baseline | NOT RUN / NOT OBSERVED |
| Scoped embedded late registration | FAIL, source 45de0c9 / scoped-0b8c8f122e80, unchanged |
| RSMB startup-registered apply/render | PASS, retained identified one-frame smoke |
| RSMB late registration | FAIL, retained separately |
| New product/collector code or native artifact | N/A, documentation-only continuation |

Last changed code/test remains 1fa62a7. Its previously verified CI is historical;
no Python/Node/native regression was rerun for these documentation-only changes.
They use [skip ci]. Five historical static-audit findings remain unresolved.
Neither file inspection nor green CI establishes current AE/project identity.

## Next file-only request

Request only `aelib.framework/Versions/A/aelib`, using the exact dependency
path established above, with source-before/source-after and copied-byte hash
agreement. Do not repeat AfterFXLib, MEE, PLUG or FLT collection. No new LLDB
collector is required. The copy command passed bash syntax and an isolated
Linux copy/hash/ZIP fixture test with spaces in the path and original bytes
preserved. Its actual Mac execution is not claimed.

The data request does not load aelib, contact or restart AE, modify settings,
install plugins or change the local Git repository. Stop on missing files or
hash mismatch, preserving partial evidence. Prior installation/one-restart
permission is consumed; future risky host actions require separate consent,
a fresh identified baseline and a specific bounded, falsifiable experiment.
