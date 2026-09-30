# Stage C: supplied SDK 25.6 registration audit and adapter recovery

Date: 2026-09-30. Review ID: `sdk25_6-registration-20260930`.
Continues upstream `61ea0871cc6e55d9f2669e9d5b4989a0e83f9a15` and the
previously saved local adapter patch `1c0d7e36e81b22b959b43d212b5e2bdb44df97ca`.
AGENTS.md, PRODUCTION_PLAN and current shared DEVELOPMENT_RULES were consulted;
shared rules remain blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Scope and acceptance

Inspect the actual supplied SDK headers and sample source, not an online guide
or synthetic API inventory. Trace candidate registration/loading APIs to their
stated inputs and purpose; distinguish effect registration, PICA bookkeeping,
module access, effect application and startup lifecycle. Preserve unsupported
or unobserved conclusions as such. Recover the pending adapter without changing
its behavior and exercise its previously unrun macOS checks in the existing
unified CI. No new test framework or speculative host binding is introduced.

No Adobe executable or library, including the supplied extractor, is executed.
No AE attachment, script, scan, installation, restart, native unload, cache reset,
callback replacement, main change, merge or release is performed. This review
and the owned adapter tests are not a live late-registration gate.

## SDK input and coverage

The uploaded files have misleading suffixes but their formats were checked:

| Input | Bytes | SHA-256 |
|---|---:|---|
| ae25.6_61.64bit.AfterEffectsSDK.tar.zstd (actual tar) | 7182336 | `eee39a787ab09226a5a08c27496335faf79cbe52dd96f19cf795e48af09e2df6` |
| ae25.6_61.64bit.AfterEffectsSDK.tar.zstd.zip (actual Zstandard stream) | 1540471 | `e02fa2b488c3cceb238866b648eb9a2526d308a260744367915a2f173663c36c` |

The trusted environment's decompressor produced bytes identical to the supplied
tar. The uploaded zstd executable and extractzstd.sh were not run; no xattr or
security setting was changed. Tar members were checked for unexpected types,
links, absolute paths and traversal before copying regular files into a new
private workspace. AppleDouble and .DS_Store metadata were excluded.

The extracted non-metadata set contains 434 regular files. The source search
covers 160 .h/.hpp headers and 109 additional .c/.cpp/.cc/.cxx/.r files:
269 files, 2362760 bytes. All were byte-searched, with the decision points below
read in context. PDF guide, project/build metadata, media and executable files
were not part of the source search; the PDF was not analyzed. This is not an
exhaustive semantic review of all SDK functions or an SDK compile/load test.
Version 25.6_61 is the supplied distribution label, not independent Adobe
package-signature verification. All source hashes were rechecked unchanged.

Private derived `sdk25_6-registration-review.json` contains the complete source
hash inventory, query locations and 14 checked contextual ranges, including raw
range hashes. SHA-256:
`6871e767650f8634dfab259147519d2a16bc87ee2bc6f79e4815f9d625eac400`.
Range hashes include the original line-ending bytes. These are source checks,
not additional unit tests. No SDK source, header or binary is committed here.
This is not a completed redistribution-license review.

## What the supplied SDK actually establishes

All paths in this section are relative to the supplied SDK root. Line ranges
refer to the original files, not a translated or regenerated guide.

### Effect registration callback is not an arbitrary late-load command

`Examples/Headers/AE_PluginData.h:61-94` defines PF_PluginDataCB2 and
PluginDataEntryFunction2Ptr. The latter receives an opaque PF_PluginDataPtr
and a callback from the host. The callback takes that same pointer with effect
metadata and the entrypoint name.

`Examples/Util/entry.h:40-69` shows that PF_REGISTER_EFFECT and
PF_REGISTER_EFFECT_EXT2 invoke the supplied callback; they do not discover a
folder, obtain a new loader context or provide an independent registry API.
`Examples/Template/Skeleton/Skeleton.cpp:219-240` passes the incoming pointer
and callback directly to the macro inside PluginDataEntryFunction2.

Conclusion limited to these declarations/sample: this is a host-initiated
metadata-registration exchange. The SDK does not establish that an unrelated
running AEGP may save/replay that callback for another binary. Merely exporting
PluginDataEntryFunction2 or calling a locally manufactured callback cannot be
claimed to register an ordinary third-party effect with AE.

### AEGP identity, application and extension hooks remain separate

`Examples/Headers/AE_GeneralPlug.h:2960-2963` documents the output of
AEGP_RegisterWithAEGP as the ID used by subsequent AEGP calls. It is not a
folder scanner or an installed-effect-key producer.

At `2173-2197`, AEGP_ApplyEffect takes an AEGP_InstalledEffectKey; the same suite
enumerates installed keys and retrieves match names. This is useful for the
independent registry/apply acceptance check, not evidence of discovering a
previously absent binary. Its returned effect reference has its own disposal
requirement, distinct from unloading the native plugin.

AEGP_RegisterSuite5 at `2742-2832` registers hooks and specific extension
interfaces, including AEIO, Artisan and tracker entrypoints. These declarations
must not be relabelled as a generic ordinary eFKT effect loader.

### PICA contains real candidates, but the AE effect connection is unverified

`Examples/Headers/SP/SPPlugs.h:103-150` really does expose AddPlugin. It creates
an SPPluginRef in a PICA plugin list and accepts a file specification, PiPL,
adapter name and adapter-specific information. It is not correct to say that
the SDK contains no plugin-list insertion API.

`Examples/Headers/SP/SPAccess.h:240-257` exposes AcquirePlugin, which can load
a plugin and create/increment an accessor. ReleasePlugin can make unloading
possible. `SP/SPInterf.h:87-104` limits its messaging interface to PICA plugins
and directs non-PICA plugins through their adapter's interface.

These are genuine alternative investigation anchors, not a confirmed shortcut.
The supplied declarations/sample source do not establish that AE 25.6 exposes
these suites to our AEGP, identify the appropriate ordinary-effect adapter or
show that a PICA insertion/access publishes an installed effect in FLT. Their
runtime availability and that connection remain NOT VERIFIED, not disproved.

`SP/SPBasic.h:82-101` says acquiring a suite may load it and releasing it may
unload it. Consequently a future availability probe is not automatically a
passive operation satisfying the no-new-module invariant. It needs its own
scope and before/after evidence; none was sent to AE in this iteration.

### PICA startup is not permission to restart a subsystem

`Examples/Headers/SP/SPHost.h:91-130` places SPInit, SPStartupPlugins,
SPShutdownPlugins and SPTerm in the host lifecycle. The startup routine scans
the application-file list and starts its plugins. This is not a documented
single-owned-folder late-registration procedure for an already running AE.
`SP/SPRuntme.h:158-173` also lets the host override plugin-list construction
and startup. Calling the generic startup functions would not prove that AE's
own startup sequence or state may safely be replayed.

No SPInit/SPStartupPlugins/Shutdown/Term calls are added to our loader.

### FILE_Spec is mentioned, but its private contract is not supplied

The source search found exactly one FILE_Spec occurrence:
`Examples/Headers/AE_Hook.h:108`, a forward declaration used by AE_FileSpecH.
The hook entrypoint at `143-147` receives file/resource handles. This does not
provide object layout, construction, ownership transfer or a disposer.

No occurrence of FILE_New, FILE_Dispose, FILE_InqUnicodePath, PLUG_Search,
FLT_SetupAEPlugin, MEE_GetVideoFilterModules or dvacore was found in the defined
269-file source corpus. This is a bounded lexical result, not proof about
unpublished SDKs or every internal API. SPPlatformFileSpecification and
XPlatFileSpec in SP/SPFiles.h are separate declared types; no conversion to
our private FILE_Spec contract is established by those declarations.

Thus the received SDK does not resolve the U/dvacore producer/destructor or
private FILE ownership/binding requirement. Do not reinterpret a public handle
or manufacture a host string to fill that gap.

## Decision and next boundary

A supported public ordinary-effect late-registration operation is NOT
ESTABLISHED by this audit. This is not a claim that one is impossible or that
all PICA alternatives have been disproved. The useful result is a precise
separation of APIs and the removal of several misleading name-based shortcuts.

The previously mapped resource-pass hypothesis remains conditional. Continue
with the reviewed native no-scan binding/ownership boundary and end-of-pass
callback analysis. Any PICA alternative must first establish suite/provider
availability and its ordinary-effect adapter/publication contract; do not
replace the known resource route based solely on AddPlugin's name. SDK-based
installed-effect enumeration can serve the independent acceptance checks.
No new user-side extraction or test is requested by this record.

Before any private host call, require a separately authorized no-scan probe,
fresh host/project/loaded-image identity, one-shot journal, exact path roundtrip,
successful single release and unchanged registry/modules/project. A later
resource scan additionally requires reviewed cleanup behavior and distinct
approval. Existing scan commands still run the historical loader. No old
installation/restart permission is reused.

## Pending adapter recovered without changing its bytes

The earlier archive `AEHL-directory-adapter-1c0d7e3.zip` was verified:
SHA-256 `d908c29c28c8fef1a820874998cd5d65b3e5de5db5b5b600434171d4b45b44a3`.
Every SHA256SUMS entry matched. The 181-file baseline was reconstructed from the
verified 7411a90 CI archive; its tree equals
`55283e5239bc68c68507acd13df7fe3013384ca8`. The pending patch was applied without
changing its four source/test files or its dated document.

Connector writes are available in this iteration. The five restored files were
committed on top of actual upstream 61ea087, preserving its newer status and all
other files. Final tree `83b16579aab213e42b74de870286590d25128cc2` was independently
recomputed before advancing only the research ref without force.
Verified code commit: **`ab5c1cb341e8432a226d8f58d2210c4fe1bbda83`**.
The original local commit ID is not presented as a pushed commit. The restored
dated document's write-unavailable/NOT RUN wording remains historical; this
record and current DEVELOPMENT_STATUS supersede it.

The adapter remains unbound to Adobe. No real producer/destructor resolver,
FILE call or PLUG operation has been enabled by this synchronization.

## Verification for restored code ab5c1cb

| Check | Result and scope |
|---|---|
| Local focused adapter regression | 27/27 owned cases at -O0 and -O2; native macOS case skipped on Linux |
| Local ASan/UBSan | PASS for owned adapter cases, leak detection enabled; not Adobe memory proof |
| Local unified Linux run | PASS; 236 collected, 228 passed/eight platform skips; 62 Node passed |
| Research CI 36772108084 | PASS, unified Linux and macOS jobs |
| Downloaded macOS report | 236/236 Python PASS, no skips; 62 Node and 15 existing scoped guards PASS |
| Actual macOS adapter transport test | 27 owned cases at -O0/-O2 with arm64 thunk and self-memory reader; invalid-pointer/bounds checks PASS |
| Downloaded Linux report | 236 collected, 228 passed/eight explicit platform skips; 62 Node PASS |
| Source/report integrity | Both outer hashes, every inner manifest entry and all five restored source hashes verified |
| Full product macOS CI 36772107919 | Separate workflow; completion must be checked in current status, not inferred from research CI |
| SDK header compilation or SDK sample build in this review | NOT RUN; source-contract audit only |
| Native Adobe binding / new live FILE or registration gate | NOT IMPLEMENTED / NOT RUN |
| Current AE/project/resident state | NOT OBSERVED |
| Full static-security audit | NOT RUN again; five historical findings remain open |

The 27 native cases are nested inside Python tests, not added to the Python
count. The SDK audit did not add new tests to inflate this total. The two new
Python cases were already in the pending patch and are now tested in macOS CI.
The unified runner still does not perform the separate product package build.

Downloaded research artifacts:

| Platform | Artifact ID | Outer SHA-256 | Inner report SHA-256 |
|---|---|---|---|
| macOS | 11124506773 | `65dc8435d42258bb592d259bc7c5564152b3132cbb83b16794a037c384c9589e` | `0065dfbf984e3148eb76a4e9a85505669b4e6c45255783a324b15bfc4704d7c7` |
| Linux | 11124102488 | `24b2b62acce2b6b66a1cd80e297f0e2a9c0eb864f2648e4c6296e501e4710fd8` | `854dd0110dcaa995538371b42bceb49d4a08250065e77f49f288367f4134d303` |

Historical scoped registration stays FAIL. RSMB startup-registered apply/render
PASS and historical RSMB late-registration FAIL stay separate. No SDK/PICA
source declaration or owned test changes those verdicts. CI applies to ab5c1cb;
documentation follow-ups use [skip ci]. No installable artifact is handed over,
and SDK/proprietary binary contents remain outside Git.
