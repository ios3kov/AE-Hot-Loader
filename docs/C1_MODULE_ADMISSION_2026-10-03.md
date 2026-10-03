# C1 module admission and initialization

Stage C1 Development research; accepted rules v8.0.0 /
132b7cd32873ba7328e3128ffbb33e1929b74d45. Starting clean research source
b03f249c74b5ce15ab17ed9af2a1db6aa26291c3. [ADMIT-01–08](PRODUCTION_PLAN.md)
acceptance recorded before new body collection. Continue the
[routine handoff](C1_ROUTINE_HANDOFF_2026-10-03.md); original arbitrary ordinary
effect/no-restart product and A/B/C1/C2/D/release obligations retained.
Collector Standard; dependent native invocation Critical/gated. No current AE
operation or native helper/profile/ResourcePassGate/SDK modification.

Preparation checkpoint: 54 focused collector tests PASS, including three new
refusal/scope controls and the actual owned arm64 file-disassembly control.
TDD first run had exactly three expected missing-mode errors; second run 54/54,
zero skips/failures/errors. Full checks/clean collection/independent review/CI
NOT RUN at this preparation checkpoint; final source-bound receipts below will
supersede it. Native supported ABI/owner/thread/drain/rollback still UNKNOWN.

## Fixed original-file scope

Mode `--review module-admission`: 12 fixed windows / 3446 instructions /
232 structural anchors. Complete ML LoadPlugins and CreateUnknownImpl each split
into adjacent windows of at most 4096 bytes. Init ends at the actual next symbol
0x45ac; CreateUnknownImpl ends at 0x8dfc. Preliminary larger windows included
stream helpers; those helpers are excluded from this final scope. Fixed MEE and
PluginSupport pins unchanged. No original Adobe binary/full disassembly committed.
Offline LLDB uses no dependents, process operations or expressions; clean-source,
input hash, exclusive owned output, decoded coverage and archive guards retained.

| Complete window, end exclusive | Instructions |
|---|---:|
| PluginSupport / admit-load-a 0x60a8–0x70a8 | 1024 |
| PluginSupport / admit-load-b 0x70a8–0x7788 | 440 |
| MEE / admit-create 0x7660–0x7a48 | 250 |
| MEE / admit-unknown 0x7b1c–0x7dc8 | 171 |
| MEE / admit-impl-a 0x7dc8–0x8dc8 | 1024 |
| MEE / admit-impl-b 0x8dc8–0x8dfc | 13 |
| MEE / admit-add 0x8e80–0x8e84 | 1 |
| MEE / admit-get 0x8e84–0x90b0 | 139 |
| MEE / admit-cache 0x90b0–0x9108 | 22 |
| MEE / admit-init 0x408c–0x45ac | 328 |
| MEE / admit-base-init 0xbbcc–0xbbd4 | 2 |
| MEE / admit-setdown 0x9110–0x9190 | 32 |

## Admission and initialization findings (ADMIT-01/02)

- PluginSupport ML::LoadPlugins at 0x60a8–0x7788 contains one-time initialization
  delegated through std::call_once (0x6114), then constructs a plugin-name list,
  selects extensions based on application type, adds the root folder (0x68a0),
  orders/removes entries by file-part comparisons and configured lists. It calls
  ML::LoadPluginList at 0x7ee8 from 0x72fc, then a virtual delegate and releases
  local lists/interfaces. Return 0x7390/0x7394 is a 32-byte file-entry-vector count,
  not observed ready effects. LoadPluginList, the one-time body and virtual targets
  remain transitive UNKNOWN; this outer body does not prove direct factory dispatch
  or establish a usable supported late call.
- MEE AELibraryVideoFilterFactory::Create allocates a module at 0x768c, queries its
  interface and inserts the reference into factory vector +8/+10/+18 (0x7708/
  0x771c/0x77b8) BEFORE module Init at 0x78a8. Its complete local unwind releases
  temporaries but shows no explicit inverse vector erase. A present module in this
  factory list is not a ready ordinary-registry effect. Actual exception behavior
  and transitive destruction/rollback remain unknown; no runtime failure asserted.
- Module Init at 0x408c–0x45ac first calls base Init (0x40b8); the complete base body
  stores its integer field +bc then returns. Derived Init queries/copies retained
  PluginImpl state at +d8/+e0/+e8, then retains PiPL at +f0/+f8/+100, releasing
  previous owners. Its named direct calls do not include SetupFilter; unresolved
  QueryMap/virtual and transitive behavior must not be asserted absent. A copied
  provider/metadata triple is not a confirmed executable lifetime or host lease.
- CreateUnknown at 0x7b1c–0x7dc8 calls CreateUnknownImpl (0x7bc0) and inserts into
  the factory module vector only if its returned reference is non-null (0x7be0).
  It queries/returns another interface afterwards; factory membership and returned
  interface readiness are separate.
- CreateUnknownImpl at 0x7dc8–0x8dfc validates/selects a PiPL entry and follows
  virtual flag/entry predicates. A bit-3 path obtains the PluginImpl module handle
  and passes false to ASL::Module::SetUnloadOnDestroy (0x7ff8/0x7ffc). This is an
  observed retention policy change, not permission to unload or safe rollback.
  Another branch retains the plugin in a separate factory vector +20/+28 before
  returning null/status zero (0x8328, 0x859c–0x85a4). Predicate meanings and actual
  runtime branch selection remain unknown.
- The viable module path checks hardcoded outflags cache (0x8194/0x8198), otherwise
  resolves a virtual entry point. It allocates a module (0x8620), calls derived Init
  (0x86d8), then SetupFilter (0x8820). Setup result bit 0 controls the returned
  module: false clears status/output (0x896c–0x8974); true returns a queried module
  interface and writes status 1 or 2 based on remaining PiPL entries (0x88a4/
  0x88bc). This connects the factory to the previously reviewed callback/FLT path.
  Cache success can bypass entry resolution; prior SetupFilter cache can bypass
  the callback. Status 1/2 is not an observed registration/apply/render result.

## Thread, completion and rollback limits (ADMIT-03/04)

GetModules at 0x8e84–0x90b0 snapshots factory vector begin/end (0x8ea4), queries
and copies interface references into the caller's vector. No explicit mutex or
readiness predicate appears in that complete body. Create/CreateUnknown similarly
show no explicit list lock. This does not prove absence of an outer lock; actual
caller thread/lease and transitive synchronization UNKNOWN. Shared-owner atomics
preserve selected reference counts, not host-wide reader/render/MFR exclusion.

AddModuleToList at 0x8e80 is a single return. Calling a function by this promising
name would not establish admission. IPluginModuleFactory::SetdownAsync at
0x9110–0x9190 constructs an empty executor shared_ptr and calls
Future<void>::CreateReadyFuture at 0x9128, then releases that local owner. No drain
or plugin teardown is directly visible; actual overrides and transitive behavior
UNKNOWN. A ready future/default method is not render quiescence or whole-effect
rollback. GetPiPLFromHardcodedCache delegates or returns an empty reference; its
name/status does not prove current effect publication.

Previously reviewed SetupFilter holds only its per-module recursive lock; FLT
can publish before lazy initialization fails. New factory status/null/reference
checks and local releases do not undo all canonical/parameter/global/provider/
registry/executable state. No supported late transaction, continuous all-reader
lease or complete rollback demonstrated. Native backend remains NOT READY.

Actual SDK 25.6_61 AE_GeneralPlug.h SHA-256
`30d12ec3eb5af1a902c7414053b1be1da0204b226e0b1cdc71272be1e137000c` reverified.
AELibraryVideoFilterFactory, AELibraryPluginVideoFilterModule, ModuleOwnership and
LoadPluginList literals absent in that one header; not global API absence. No new
SDK call/signature or callback control introduced; earlier SDK results keep their
original source identity. Private InterfaceRef/ownership/virtual contracts UNKNOWN.

## Current task reconciliation

ADMIT-01 bounded outer-loader and factory→Init→SetupFilter route documented;
full loader dispatch/ABI remains UNKNOWN. ADMIT-02 normal/unwind retention and
insertion order reviewed; actual runtime identity/lifetime/full rollback BLOCKED.
ADMIT-03/04 explicit lock/default future/cache/status/failure boundaries reviewed;
required continuous host admission/drain/thread/completion/rollback BLOCKED.
ADMIT-05 research mode/refusal controls implemented; 54 focused PASS at working
source, clean acceptance pending. ADMIT-06 full clean verification/CI NOT RUN yet;
ADMIT-07 final docs/cleanup pending. ADMIT-08 executable host packet BLOCKED;
registration/apply/render NOT RUN. No current live scope assumed or requested.

Next discriminator: complete LoadPluginList and its actual module/factory
ownership/dispatch/error transaction, including the one-time/virtual delegates
where relevant. Do not repeat PICA or unchanged file scan, construct a private
provider, replay startup or call default SetdownAsync as a drain.

Cleanup: only fresh owned research folders/test temporaries created; preserve all
original SDK/app/session/plugins/projects, consumed helpers and historical evidence.
Private reproducibility receipts will be retained locally; no shared-state purge,
no installable artifact handoff, merge or release.
