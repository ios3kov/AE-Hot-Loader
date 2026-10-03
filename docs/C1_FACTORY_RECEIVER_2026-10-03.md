# C1 factory receiver acquisition and retained-reference boundary

Stage C1 Development research; rules8.0.0 /
132b7cd32873ba7328e3128ffbb33e1929b74d45, AI_ENTRYPOINT first. Starting clean
d27449a885713398877bc1a014063b090fb405b1. Seven user-authorized requirements
RECV-01–07 recorded in [production plan](PRODUCTION_PLAN.md) before original
body collection. Native receiver/lifetime component Critical, collector Standard;
API-SOURCE/thread/ownership/refusal/repro/task-close/cleanup apply. Existing
SDK25.6_61 inventory reused; no new Adobe API call. Original arbitrary ordinary
effect/no-restart product and A/B/C1/C2/D/release retained.

## Exact file scope

Mode factory-receiver:14 complete MEE arm64 windows /563 instructions /481 anchors.
Initial five bodies selected by exact symbol inventory; selected direct branch
inventory led to exported register wrapper and owner release/deallocation delegates.
Zero-shared object's primary slot matched previous table's D1, requiring its full
hidden-VTT delegate. Import stub is exactly three instructions, bounded to next
stub. Other bodies end at next distinct original text symbol. Preliminary dirty
capture is discovery only. MEE SHA256
18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344,
UUID74a30dba-a08b-367b-bd99-15d6d77e9d52, selected AE25.6x101 arm64.
Prior exact [factory identity/construction](C1_FACTORY_IDENTITY_2026-10-03.md)
and [insertion/dispatch](C1_LOADER_DISPATCH_2026-10-03.md) evidence reused after
pin verification. No original binaries/full disassembly committed; no AE runtime.

| Window, end exclusive | Instructions |
|---|---:|
| recv-instance0x71b4–0x73e4 |140|
| recv-query0x92b0–0x938c |55|
| recv-unknown-ref0x938c–0x9414 |34|
| recv-global0xb5e8–0xb610 |10|
| recv-create-instance0x3e150–0x3e234 |57|
| recv-register0x3dfb8–0x3e150 |102|
| recv-interface-dtor0x3e9c–0x3efc |24|
| recv-shared-dtor0x5354–0x53b4 |24|
| recv-factory-dtor0x7410–0x7540 |76|
| recv-weak-dtor0x43c0c–0x43c38 |11|
| recv-zero-shared0x43dd8–0x43de4 |3|
| recv-zero-weak0x43de4–0x43e00 |7|
| recv-d1 0x7540–0x7584 |17|
| recv-register-stub0x9fe48–0x9fe54 |3|

Data windows: one raw signed header word each at0xef608 and0xef628, values0 and
0x38. Both have no dyld fixup; format6 chains checked separately. These are
adjustments, not serialized callable pointers. LLDB no dependents/process/expression/
call. No private register/acquire/retain/release/destructor invoked.

## Registration and class acquisition (RECV-01/02)

Exported MEE_RegisterVideoFilterFactory first calls dvacore ClassFactory::RegisterClass
(0x3dff8), supplying callback0x3e150 selected by ADRP/add0x3dff0/0x3dff4. It then
calls CreateClassRefInternal with creation flag true (0x3e040/0x3e044), queries the
returned UnknownBase virtually at slot+0x18 for24-byte identifier
ML::IPluginModuleFactory, transfers retained owner fields (0x3e080–0x3e088),
and calls the MEE import stub for PluginSupport RegisterPluginModuleFactory
(0x3e0a0→0x9fe48). Original indirect-symbol inventory maps stub0x9fe48 /slot0xed738
to that PluginSupport import; body ADRP/ldr/br is linkage, not a supported late ABI.
Previous insertion body retains the interface in the factory registry, not the
ordinary-effect registry. Null/query failure is not ready factory/effect success.
Register's local owners release normally and on unwind. No explicit caller-wide
once/mutex guard in this complete exported body; repeating it late is unproved.

Global initializer0xb5e8 merely initializes named class GUID storage0x10f080 from
7a7d3cd3-6b81-48f8-bee0-ec40018a4432; it does not register the factory. Instance
uses named GUID storage0x10f080, calls dvacore CreateClassInstanceRef (0x71dc),
queries31-byte identifier ML::AELibraryVideoFilterFactory through slot+0x18
(0x7204), and moves retained owner fields to its output (0x7220–0x7228).
Missing interface has assert/log/cleanup paths, not an acceptable valid receiver.
Class registration's GUID input points to distinct storage0x10fa38; class/name/callback
argument correspondence is observed, but original-file zero-fill/addresses alone
cannot establish equality of its runtime GUID value with0x10f080. No equality or
full transitive ClassFactory behavior is asserted. Indirect/transitive callers and
actual call timing/thread remain UNKNOWN.

CreateInstanceRef0x3e150 calls CreateClassRefInternal(true) and transfers the returned
UnknownBase/owner fields to its output (0x3e184–0x3e190), releasing old/local owners.
Therefore Instance/CreateClassInstanceRef can route to creation; this is not proved
a read-only lookup of an already initialized factory. Callback registration and
creation form a bounded original-file path, not a harmless late acquisition contract.

## Query and pointer adjustment (RECV-02/04)

Complete QueryMap compares exact31-byte factory identifier and24-byte module-factory
identifier, returning its incoming object address on match or null on mismatch.
Independent raw MOVZ/MOVK comparison proves exact31/24-byte string_view content
excludes the trailing ] printed after the pointed-to literal in LLDB comments.
No generic RTTI/string/comment guessing is valid.
Conversion to UnknownBase loads primary vtable[-0x38] (0x93a4), adjusts object,
then calls external dvacore UnknownBase::GetSharedFromThis (0x93b0), transferring
paired reference fields. Prior classref output uses the same header adjustment.
Original header at0xef608 (primary table0xef640 minus0x38) is0. The different
header at0xef628 (primary minus0x18) is0x38 and is used in prior allocation's
shared-from-this base adjustment. Earlier hypothesis that the UnknownBase shift
would itself be0x38 was refuted by original data. Secondary vptr at object+0x38
cannot establish the primary interface adjustment. This is selected final-vtable
file evidence; actual live receiver/construction state was not observed.

Symbols/static argument movement are not supported callable host ABI. Private
Instance/QueryMap/conversion/CreateInstanceRef/classref exports/types must not be
cast to guessed function pointers. Actual receiver lifetime/thread/mutation permission,
dvacore class lookup/query/shared-from-this contract and reentrancy UNKNOWN.

## Lifetime and teardown (RECV-03/04)

InterfaceRef destructor reads control field+0x10; shared_ptr destructor reads+0x8.
Their selected atomic decrement at control+0x8 checks old value zero before virtual
zero-shared slot+0x10 and external release_weak. These offsets/bias are private file
observations, not legal foreign refcount mutation instructions. Weak destructor
calls release_weak separately. Zero-shared delegate adjusts control by+0x18 and
jumps through object's first vtable slot. Prior table identifies D1=0x7540; D1
supplies VTT0xef6c0 to D2, then calls external UnknownBase destructor and releases
a remaining weak field. D2 requires the additional construction-table argument,
rewrites vptr/base fields, releases retained module vectors and frees their storage.
Calling it as a guessed single-argument destructor would violate observed dataflow.
Zero-weak recycles0x68 bytes; surviving control/storage is not surviving object.
Local destruction does not prove render completion or whole-effect rollback.

## Implemented copied-reference component and owned native stand (RECV-05/06)

FactoryReceiverReference.hpp implements exact24-byte little-endian tuple decoding:
primary pointer, UnknownBase owner pointer and control token. Layout requires the
reviewed zero UnknownBase adjustment and object=control+0x18 allocation relation.
All-zero tuple returns Absent. Partial-null, misaligned, inconsistent owner/control,
wrong layout and overflow refuse. Output contains diagnostic integers only; decoder
reads no object, checks no mapped allocation and acquires no reference. Exact image
binding and actual ownership are separate requirements. Plausible dangling tuples
can still decode; never construct a shared_ptr/callable pointer from these integers
or treat them as ResourcePassGate capability. Existing helper/gate stays unconnected.

Two focused native tests PASS, strict C++17; owned lifetime control also runs ASan/
UBSan. Its real C++ Factory/Unknown interface resides in an owned block with24-byte
layout prefix. That block is a test layout token, NOT the standard library's shared
control block or Adobe control ABI. A typed weak_ptr lock and aliasing shared_ptr
independently retain the real owned object: it remains callable after external owner
release, transfer preserves ownership, last strong release destroys exactly once,
weak lock then fails, replacement cannot resurrect the old weak owner. Copied bytes
still decode after destruction, explicitly proving shape is not lifetime. Invalid
pointer shapes refuse without dereference. No Adobe call/load/process operation.
This stand substantiates owned C++ lifetime/decoder behavior only, not AE retention.

TDD first run exactly two missing-header compile failures; implementation run two
PASS. Four new collector refusal tests first fail for missing mode, then65 focused
collector tests PASS. Source/owned-output/hash/window/ZIP guards retained; original
semantic review is separate from synthetic parser tests.

## Current reconciliation and dependent gate

RECV-01/02 bounded register/create/query findings recorded;03 selected lifetime/
destruction boundaries recorded, actual supported AE retention remains UNKNOWN;
04 private ABI/thread/transitive contracts remain UNKNOWN;05 diagnostic component
implemented, actual retained receiver/call adapter BLOCKED;06 owned native lifetime/
ASan/UBSan controls PASS, actual AE lifetime NOT RUN;07 clean collection/separate
original-byte/header/archive/source review/full runner/scanner/exact-source CI/
status/handoff/compatibility/retention/cleanup PENDING pre-commit acceptance.
No claim that all seven product-dependent requirements are complete.

Conditional native registration remains BLOCKED: actual retained receiver/supported
late ABI/continuous host reader/render admission/drain/full-effect rollback missing.
Launch authorization remains received; technical contracts are not implemented by
consent. AE launch/attach/install/read active session/private invoke/retain/release,
registration/apply/render NOT RUN. Original product/A/B/C1/C2/D/release retained.

## Exact clean-source reconciliation

This supersedes PENDING research checks above. Exact clean tested code
4ca1e665ec418b2bc7cde008b48ac67b1832865a. Independent review also corrected preliminary query-name
wording: the closing bracket in LLDB's pointed-to literal comment is excluded from
the actual31/24-byte string_view comparison. Only documentation changes at final
closeout; no code/anchor/decoder change was needed. Later documentation SHA is not
claimed to have run preceding exact-source code checks.

| Task | Exact bounded acceptance / result | Remaining dependent scope |
|---|---|---|
| RECV-01 | Exported registration/class callback/creation/query/factory-map insertion route traced and raw import linkage verified | Actual runtime GUID values/equality and transitive class registry UNKNOWN |
| RECV-02 | Complete Instance/QueryMap/conversion/CreateInstanceRef and raw signed adjustments reviewed | Actual native acquisition/receiver NOT OBSERVED |
| RECV-03 | Complete selected strong/weak/interface/zero-owner/D1/D2 lifetime boundaries reviewed; own real-object lifetime controls PASS | Supported actual AE retention/storage lifetime UNKNOWN |
| RECV-04 | Private/static argument/return/error/hidden-VTT/transitive/thread limitations explicitly established | Supported callable late ABI/thread/admission/drain/full rollback BLOCKED |
| RECV-05 | Copied-reference shape decoder IMPLEMENTED, rejects unsupported layout/partial/misaligned/inconsistent/overflow data | Actual retained receiver/call adapter BLOCKED; no object read/ownership/call capability |
| RECV-06 | Real owned C++ object/alias/move/destruction/weak expiry/replacement/stale copied data, ASan/UBSan PASS | Actual AE lifetime/registration/apply/render NOT RUN |
| RECV-07 | Clean collection, separate original byte/query/header/import/ZIP/source review, all checks/scanner/CI/docs/retention/cleanup COMPLETE | Full product/A/B/C1/C2/D/release remain open |

- Clean collection `resource-factory-receiver-6d31b658-jnlvecb2.zip`, SHA256
  cce2f22dd3d8708e31c792848d9203a10a5468ad638ed7cbd7180731564c9c2e, 37 members. Complete14 fixed windows/563 rows/
  481 anchors, two distinct raw non-fixup header words, exact input pins before/
  after, CRC/hash inventory and byte equality to exclusive owned outputs PASS.
  Zero Adobe calls/load/process activity; no scan/native acquire/release.
- Separate verifier `aehl-receiver-independent.py`, SHA256
  b9c3528115648595aaa5de5a0acfc3f7213abb06f4e2d70da0de1f4fc694f5c3; no collector import.
  Original arm64 fat Mach-O mapping and instruction decoding:563 instructions,
  61 direct/47 conditional/14
  indirect branches/18 returns PASS. Raw callback/data GUID roots,
  MOVZ/MOVK exact query identifiers, zero UnknownBase versus0x38 shared adjustment,
  MEE stub/GOT0xed738/nlist/import ordinal→PluginSupport PASS. Source GUID storage
  distinct; actual runtime equality UNKNOWN. Receipt SHA256
  2c6516e5bf8dfe2251030838ace69a6b5a82095f51f30e992bb8016694c21b39. This is selected original
  file dataflow, not every transitive semantic effect or supported host ABI.
- Full runner `AEHL-checks-q0r6rla0.zip`, SHA256 83712e3493b6143f330367d5ab5ad01c6331693ae379fbd6062eff5cd0b94085,
  25 members;446 Python, zero skips/failures/errors/expected failures/
  unexpected successes,62 Node, all22 stages PASS; Python63.932 seconds. Owned
  native stand compiled/executed with ASan/UBSan, no sanitizer report. C++ owner
  contract only; no AE native ABI/lifetime certification. TDD logs preserve two
  missing-header compile failures and four missing-mode collector errors, followed
  by focused65+2 PASS; no lowered acceptance.
- Independent runner ZIP CRC/manifest/payload hashes and all345 tracked working
  bytes/exact-code Git blob hashes PASS. Inventory SHA256
  4848de3885313cebe7967adb257686ab42f86af9032a0493521baef2d03b18fc; clean source/source_unchanged_after=true.
  Source-proof SHA256 5dac7978a15e2ddb7f2d058e8a5e94c35226350e9d94dcc33eeaacafe071186c.
- Scanner `aehl-receiver-4ca1e66-audit.json`, SHA256
  13a2e7ff8e01129accd41f035c8c79855a25dfac96057d1cbdd49b4a8f65d249; raw exit1/review_required,
  release_readiness=not_assessed. Sole vibe.no_ratelimit_auth at
  tools/artifact_manifest.py:71 reviewed: local argparse manifest CLI, no HTTP/
  auth route/listener. False positive; raw finding/exit retained without suppression.
  Separate source/scanner review (including corrected query-name interpretation)
  SHA256 6aeaa35f72c4a31c50280aa60d10536571f29ba788ea0f86a9cf00d3944d8f40.
- Research CI [37138868803](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37138868803) and macOS CI
  [37138868787](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37138868787) completed/success at exact4ca1e665ec418b2bc7cde008b48ac67b1832865a.
  Internal build/offline controls only; no AE registration/render claim.

## Retention, cleanup and next dependency

Durable private owned receipts under
`build-ae-hot-loader/receiver-closeout-4ca1e66-l8bxu5bm`. Byte-identical collection/runner archives,
independent verifier/review/source proof, raw scanner/manual review, TDD/focused
logs and preliminary direct-branch/GUID/adjustment-hypothesis inventories preserved.
RETENTION.json SHA256 ef9befeb3c7d17bb8490a6684542a2b07bd6b2a9a3daecc685a51306d967ea5b; CI.json SHA256
aeb6dfc8353a76f22e2abd0e4af6106bbff1302c4f9a301cffa2dd03942b316f; final CLOSEOUT.json binds subsequent docs commit
and full retained receipt inventory. Temporary test executable removed by owned
lifecycle; preliminary/historical/shared/loaded/unknown evidence untouched.
SDK/app/plugins/projects/AE session unchanged; no preferences/cache purge, scan,
AE launch/attach/install/read session/private invocation/refcount/destructor/unload,
merge or release. Rule/product/remaining acceptance preserved.

Next: substantiate transitive dvacore ClassFactory/GetSharedFromThis/acquisition
contracts and actual retained factory receiver. Separate supported late-call ABI/
thread/continuous host-wide reader/render admission/drain/full effect rollback
remain mandatory. Do not call the creation/registration wrappers as harmless getters,
reconstruct foreign shared_ptr ownership from tuple bytes, use saved integers after
release, or mistake destructor/control-storage retention for render completion.
