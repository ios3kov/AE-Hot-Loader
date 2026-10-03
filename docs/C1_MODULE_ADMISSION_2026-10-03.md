# C1 module admission and initialization

Stage C1 Development research; accepted rules v8.0.0 /
132b7cd32873ba7328e3128ffbb33e1929b74d45. Starting clean research source
b03f249c74b5ce15ab17ed9af2a1db6aa26291c3. [ADMIT-01–08](PRODUCTION_PLAN.md)
acceptance recorded before new body collection. Continue the
[routine handoff](C1_ROUTINE_HANDOFF_2026-10-03.md); original arbitrary ordinary
effect/no-restart product and A/B/C1/C2/D/release obligations retained.
Collector Standard; dependent native invocation Critical/gated. No current AE
operation or native helper/profile/ResourcePassGate/SDK modification.

Historical preparation checkpoint, superseded by the exact closeout below:
54 focused collector tests PASS, including three new
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

## Preparation reconciliation (historical; superseded below)

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


## Exact clean research closeout

Checked code: **59f1e7ae1a8e279adfb7a9891ff5de6494d203cc**, clean branch
research/ordinary-plugin-discovery, pushed without merge/release. All bodies above
collected again at this clean source; preliminary dirty collection is not acceptance.

- Focused collector: 54 PASS, zero skips/failures/errors, including actual owned
  arm64 LLDB control. Full runner: **430 Python**, zero skips/failures/errors,
  **62 Node** (51 panel +11 snapshot), all **22 stages PASS**. Original logs reviewed;
  Python 59.141 seconds, existing timeout 120 unchanged. Nested native guards count
  as one Python test, not an inflated total. Offline/macOS-native PASS; full AE
  pipeline BLOCKED, product package NOT RUN, live operations requested false.
- Clean collection: `resource-module-admission-1f84f6a9-26oic50m.zip`, SHA-256
  `eba646b5a22d3f0bd476c589106e77779d045b7cd6b64f8398d19cde610f9358`.
  28 unique members / CRC / exact manifest hashes and corresponding folder bytes
  independently verified. Twelve windows /3446 instructions /232 anchors. Private
  archive remains in the owned ignored build directory; not an installable handoff.
- Independent original arm64 byte review: **634 direct**, **347 conditional**,
  **61 indirect** branches and **14 returns** agree with transcripts. Three retained
  interface pair writes and three null/cache/setup decisions independently decoded
  from original words/registers/offsets/bits/targets. No collector verifier imported
  and no Adobe execution. `independent-review.json` SHA-256
  `0c0fb752c71e0bc269cf7e1a391568f557c69eb521623c1891a0aaacec11e20b`;
  independent script SHA-256
  `80b6b9d89b6de11c362631e3fa5c91edb68b4e1f648a22b385ce424f42f4570e`.
- Full runner `/private/tmp/AEHL-checks-111oe9uf.zip`, SHA-256
  `e51d9244ba68308e644a17e65e03283dd6b25d777d7f415a7ff84ed4dc32d0f2`.
  All 25 unique ZIP members /CRC/exact manifest hashes and **335 tracked source
  hashes** independently matched the clean candidate; source unchanged after run.
  Source inventory SHA-256
  `d5e111b8f5ec580f7d7eedc520caa0510f61dc45d0f71decba6afc215042ca73`.
  Independent source-proof SHA-256
  `a0c27d50dc43171c80f60620a9969e6d081b236e376526042a7b0592edeca358`.
- Manual source/structural and safety-output review separately recorded in private
  `manual-review.json`, SHA-256
  `a4a7c2d6f9914bddbc66baf07aa79979de09d340412a30d4de44bc253dbdd2b8`.
  Scanner exact clean 59f1e7a: raw exit **1**, `review_required`, readiness
  `not_assessed`; SHA-256
  `c220f83e474fc86854a304a0be133b66f6ef1ddd7d8aaf39b721d2c5e71f2dc4`.
  Sole `vibe.no_ratelimit_auth` at tools/artifact_manifest.py:71 manually reviewed:
  local argparse CLI, no auth/network route, false positive. Raw finding/exit
  retained without suppression; do not report scanner PASS or release clearance.
- Both exact-source workflows **completed/success** at clean 59f1e7a:
  [research CI 37135099702](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37135099702)
  and [macOS CI 37135099694](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37135099694).
  macOS build/sign/package/owned smoke/archive checks are not AE runtime proof.
- Durable byte-identical private copies of collection/full runner/scanner/independent
  verifier/independent review/manual review/source proof retained at owned ignored
  `build-ae-hot-loader/admission-closeout-59f1e7a-mhal2a7u`.
  RETENTION.json SHA-256
  `5771eb743602b45492620216783bbaf890276c727294f88554e88ef11b79e5b7`.
  Originals preserved; no cleanup of shared or loaded state.

| Requirement / task | Actual acceptance / check / Evidence | Remaining readiness impact |
|---|---|---|
| AI-STATE/API-SOURCE; ADMIT-01 | Baseline/rules/actual SDK pin verified; complete outer loader and factory→Init→SetupFilter file route identified | Full LoadPluginList/one-time/virtual dispatch and supported late ABI UNKNOWN |
| Native ownership; ADMIT-02 | Retained fields, vector writes before/after setup, normal/unwind release independently reviewed | Actual owner/lifetime and full rollback BLOCKED |
| SAFE/native thread; ADMIT-03 | Complete selected list/read bodies and default ready-future reviewed | Continuous all-reader/render/MFR admission/drain/thread BLOCKED |
| Completion/rollback; ADMIT-04 | Null/status/cache gates and partial retained state documented; no guessed private teardown | Full transaction/semantic completion/whole-effect inverse BLOCKED |
| TEST-CONTROL/bounded tools; ADMIT-05 | Fixed mode implemented, three new expected TDD failures then 54 focused PASS; tampered/incomplete outputs rejected | Research parser evidence only, not host certification |
| REPRO/regression/review; ADMIT-06 | Clean collection, original bytes/archive/335 source hashes, 430 Python/62 Node/22 stages PASS, scanner finding manually dispositioned | Both exact-source research/macOS CI completed/success; AE runtime BLOCKED/NOT RUN |
| TASK-CLOSE/CLEANUP; ADMIT-07 | All eight blocks reconciled; canonical status/plan/handoff updated and owned durable receipts retained | Final docs-only publication leaves checked research code unchanged; original product/A/B/C1/C2/D/release retained |
| Native experiment; ADMIT-08 | No safe supported executable packet yet; current live scope absent | BLOCKED; registration/apply/render NOT RUN |

Bounded research progress is verified. No product completion percentage or claim
that eight live-host steps passed; required runtime gates remain open. Next:
complete LoadPluginList admission/dispatch/ownership/error contract, rather than
retrying unchanged scans or interpreting a factory list/default future as safety.

Docs-only closeout is published separately with `[skip ci]`; all non-document
tracked bytes must still match clean 59f1e7a. This does not transfer runtime/release
acceptance to a newer artifact. ADMIT-01–07 bounded research/review/checks/docs
accounted for; required native contracts within 01–04 remain BLOCKED. ADMIT-08
executable host experiment BLOCKED, registration/apply/render NOT RUN. All eight
blocks reconciled; no requested product obligation silently removed.
