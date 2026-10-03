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
ML::IPluginModuleFactory], transfers retained owner fields (0x3e080–0x3e088),
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
queries31-byte identifier ML::AELibraryVideoFilterFactory] through slot+0x18
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
The literal constants include trailing ]; no generic RTTI/string guessing is valid.
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
