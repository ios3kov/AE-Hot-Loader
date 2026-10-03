# C1 loader dispatch, ownership and failure

Stage C1 Development research; accepted rules v8.0.0 /
132b7cd32873ba7328e3128ffbb33e1929b74d45. Starting clean research source
39b169d16ffbdfb9f1e42894b962e582fda38533. DISPATCH-01–10 acceptance in
[production plan](PRODUCTION_PLAN.md) recorded before new original body collection.
Continue [module admission](C1_MODULE_ADMISSION_2026-10-03.md) and
[routine handoff](C1_ROUTINE_HANDOFF_2026-10-03.md). Original arbitrary ordinary
effect/no-restart product and A/B/C1/C2/D/release obligations retained.
Collector Standard; dependent native invocation Critical/gated. No AE operation,
helper/profile/ResourcePassGate/SDK change or supported private ABI introduced.

## Fixed file scope

Mode `--review loader-dispatch`: 23 fixed PluginSupport arm64 windows /
11754 decoded instructions / 792 structural anchors. Complete LoadPluginList and
AddPlugin split into adjacent windows of at most 4096 bytes; all remaining windows
end at the actual next text symbol in the same pinned original inventory.
PluginSupport SHA-256 4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832,
UUID 64C01AC4-2413-3463-8822-17EE5543052A, selected AE 25.6x101 research host.
No original binaries or full Adobe disassembly committed. File-only LLDB uses no
dependents, launch, attach, expression or invocation. Clean source, exact pins,
exclusive owned outputs, complete decoded coverage and ZIP guards retained.

Initial four windows were selected in the plan. Adaptive downstream capture was
based on actual LoadPluginList calls to AddPlugin and MetaPluginLoader and on
call_once HeavyInit continuations; AddPlugin d15c/e70c and d200 selected
CreatePlugin and FindPluginFactoriesForModule, whose original direct calls selected
five complete GetFactoryList helpers. Preliminary dirty collection is discovery
only, not clean acceptance. Logging-string AddPlugin lambdas were not promoted to
callable registration candidates. Captured complete bodies do not prove every
transitive target or side effect; conclusions below concern selected dataflow.

| Complete fixed window, end exclusive | Instructions |
|---|---:|
| dispatch-list-a 0x7ee8–0x8ee8 | 1024 |
| dispatch-list-b 0x8ee8–0x9ee8 | 1024 |
| dispatch-list-c 0x9ee8–0xa6d0 | 506 |
| dispatch-once 0x35e2c–0x36148 | 199 |
| dispatch-add-1 0xc8a4–0xd8a4 | 1024 |
| dispatch-add-2 0xd8a4–0xe8a4 | 1024 |
| dispatch-add-3 0xe8a4–0xf8a4 | 1024 |
| dispatch-add-4 0xf8a4–0x108a4 | 1024 |
| dispatch-add-5 0x108a4–0x118a4 | 1024 |
| dispatch-add-6 0x118a4–0x128a4 | 1024 |
| dispatch-add-7 0x128a4–0x12cf8 | 277 |
| dispatch-static 0x5890–0x60a8 | 518 |
| dispatch-init-task 0x3642c–0x365fc | 116 |
| dispatch-init-inner 0x366b8–0x36720 | 26 |
| dispatch-init-types 0x367dc–0x36a14 | 142 |
| dispatch-find-factories 0x61768–0x61d4c | 377 |
| dispatch-meta-load 0x3aa10–0x3ac18 | 130 |
| dispatch-create-plugin 0x156f0–0x15a54 | 217 |
| dispatch-factory-many-a 0x61d4c–0x620a8 | 215 |
| dispatch-factory-many-b 0x620a8–0x62410 | 218 |
| dispatch-factory-one-a 0x62410–0x6274c | 207 |
| dispatch-factory-one-b 0x6274c–0x62a88 | 207 |
| dispatch-factory-one-c 0x62a88–0x62dc4 | 207 |

## Dispatch and one-time initialization (DISPATCH-01/02)

LoadPluginList copies/sorts the candidate file vector locally, then processes
entries. At 0x88a8 it checks MetaPluginModule::IsMetaPlugin; meta branch calls
MetaPluginLoader::LoadPlugin (0x88b8). Ordinary branch initializes an output bool
at stack +d0, passes candidate, remaining-entry count, ModuleOwnership and optional
entry info to AddPlugin (0x8900). Its separate returned status is saved at 0x8904.
The bool controls adding filenames to the caller's output vector (0x8934,
0x89bc–0x8a0c); a negative status is checked separately (0x8a10). Neither a filename
nor a loop count proves ordinary-effect registration/readiness.

The LoadPlugins call_once proxy at 0x35e2c calls internal LoadStaticPlugins with
bool true (0x35e74), then schedules HeavyInit-success continuations (0x35eb0,
0x35f60). The first continuation schedules a nested continuation (0x364a4); its
body invokes LoadStaticPlugins (0x366e8). Another continuation invokes type-group
LoadStaticPlugins with true then false (0x36834/0x3686c), obtains MF registered type
7 entries and delegates to MetaPluginLoader::LoadStaticPlugin (0x36884/0x368b0).
Selected static-type constants have no asserted SDK meaning. Scheduler/thread and
actual execution timing remain UNKNOWN. Task success is not render drain.
Internal LoadStaticPlugins obtains/clears MF registrations (0x598c) and calls
AddPlugin (0x5d00); this startup mutation is not an idempotent safe late rescan.

## Factory selection and retained ownership (DISPATCH-02/03)

CreatePlugin chooses AEPlugin::CreateClassRef for an exact `.aex` suffix
(0x15738–0x15798; call 0x157a4), otherwise Plugin::CreateClassRef (0x157f4), queries
an interface virtually, moves retained owner fields to the output triple
(0x15834–0x1583c or 0x159a8–0x159ac), sets full path/title, and releases local
references on normal/unwind exit. A PluginImpl reference is not an observed
executable-module lifetime or whole-effect rollback contract.

AddPlugin calls CreatePlugin (0xd15c/e70c), optionally MakeStaticPlugin, then
FindPluginFactoriesForModule (0xd200). The selection routine initializes its
manager through call_once, performs path-map lookups and conditional fallback
by list emptiness/application type, returning a local vector of PluginFactoryInfo.
Five complete helpers construct PiPL/interface references, retain queried factory
owners and append 40-byte factory-info records; their null/query branches and
local normal/unwind release paths are separate from ordinary effect readiness.
For example 0x61f14/0x61f34 retain the fields and 0x61f64 advances the vector.
No actual receiver or transitive factory-registration result is observed.

AddPlugin's first factory-info loop uses a virtual predicate (0xd4a8). A later
factory-map route takes a retained factory receiver from entry +30 (0x10230),
queries a retained PluginImpl interface, loads vtable slot +28 (0x10328), and calls
it at 0x10344 with plugin interface, PiPL vector, index, flags and status-out field
at stack +104. Status is checked at 0x103b0/0x103b4. This argument shape is
consistent with the previously reviewed MEE CreateUnknown route; that is a file
inference, not a proven actual MEE virtual receiver or safe callable ABI.
Local reference-count atomics and cleanup preserve selected owners, not host-wide
admission/exclusion. Query/virtual targets and collection growth remain transitive
UNKNOWN. Do not translate stack references into saved late-call contexts.

The separate MetaPluginLoader::LoadPlugin calls module Load, EnumeratePlugins,
CachePiPLs (0x3aa3c/0x3aa54/0x3aa60), then invokes a per-type handler indirectly
(0x3aadc). It releases local/shared references on normal/unwind paths. This meta
handler route must not be equated with arbitrary ordinary-effect registration.

## Thread, error, completion and rollback (DISPATCH-04/05/06)

LoadPluginList constructs a file-flush-delay scoper and changes the global machine
exception policy to false (0x7f3c), saving the previous value (0x7f40). Normal exit
restores that policy at 0x9e78 and destroys the scoper at 0x9e80; unwind destroys
ScopedForceEnableMachineExceptionHandling and the scoper (0xa6bc/0xa6c4). These
selected restoration paths do not restore every plugin side effect. This code was
read as file bytes; no host exception policy was changed by the research pass.
Replaying the startup path would require a separately verified global-state contract.

Negative AddPlugin status takes conditional application/headless/debug branches
leading to plugin-cache RegistryKey::DeleteSubKey (0x8dec). A selected catch path
captures/logs/releases the exception and continues (0x8d14–0x8d68). File-cache
cleanup and exception logging are not FLT ordinary-registry removal. Local AddPlugin
unwind releases interfaces, vectors, strings, registry keys and message temporaries;
it does not establish an all-or-nothing inverse for publication in unresolved
virtual callees. No whole-effect inverse is demonstrated by this scope. Earlier
FLT publication-before-lazy-failure evidence remains relevant and unchanged.

HeavyInit success, output bool, signed status, factory-info membership, copied
owners and cache deletion are separate observations. No supported late-entry ABI,
actual live receiver/provider, thread restriction, continuous all-reader/MFR lease,
render completion/drain or whole-effect rollback is proven. Absence of a named
operation in these selected bodies is not proof of absence in transitive callees.
Native packet/execution DISPATCH-10 BLOCKED; registration/apply/render NOT RUN;
backend NOT READY. No merge/release approval derived from file-only findings.

## Preparation checks and task reconciliation

57 focused collector tests PASS, zero skips/failures/errors, including the actual
owned arm64 file-disassembly control. Three new scope/catalog/refusal controls were
first run before implementation: exactly three expected missing-mode errors; then
57/57 PASS. Refusals cover changed opcode/operands at each selected anchor, missing,
duplicate/undecoded instructions and wrong scope/bounds. These synthetic controls
validate collector refusals, not Adobe runtime or semantic completeness.

DISPATCH-01–06 bounded file findings documented; required native contracts remain
BLOCKED. DISPATCH-07 collector/refusal implementation complete at preparation.
DISPATCH-08 clean collection/independent original-byte/archive/source review/full
checks/scanner/current exact-source CI NOT RUN at this preparation checkpoint.
DISPATCH-09 docs/cleanup reconciliation started; exact receipts below supersede
this preparation state. DISPATCH-10 executable native experiment BLOCKED.

Only exclusive new owned private outputs are created. Preliminary disassembly,
older receipts, loaded/shared/unknown material and historical evidence remain
preserved. No shared cache purge, plugin uninstall, unload or AE session cleanup.
The next engineering dependency is the actual factory receiver/capability binding
and a supported continuous admission/drain/rollback transaction; another unchanged
scan cannot supply it. Product acceptance still requires new registration, applying
that same effect and rendering successfully without restarting AE.

## Exact clean-source closeout

Preparation above is historical; this section supersedes its NOT RUN research
checks. Exact clean tested code 2a2dabb68d442355e97e0d1053d84bccef60c825, published to the
existing research branch. Local/source proof, clean collection and source unchanged
through checks verified. Subsequent closeout modifies documentation only; no claim
that the later documentation SHA itself ran these code checks.

| Gate / task | Procedure / exact scope | Result / Evidence |
|---|---|---|
| DISPATCH-01 | Complete LoadPluginList with actual ordinary/meta routing, bool/signed-status separation | Bounded original-file finding documented; callable late orchestration UNKNOWN |
| DISPATCH-02 | Complete call_once/HeavyInit/static dispatch, CreatePlugin/FindFactory/five selection helpers | File order and fallback/owner fields documented; actual virtual receiver/thread UNKNOWN |
| DISPATCH-03 | Selected normal/unwind retained-owner transfers and collection writes, prior MEE/FLT findings reconciled | File finding complete; actual executable owner and host lifetime UNKNOWN |
| DISPATCH-04 | Selected task/atomic/local scope versus continuous all-reader/render exclusion | File limits documented; supported host admission/drain BLOCKED |
| DISPATCH-05 | Output bool, signed status, virtual status-out, caught exceptions/cache cleanup | Distinctions documented; actual registration/apply/render NOT RUN |
| DISPATCH-06 | Local policy/scoper restoration/releases versus whole-effect inverse | File limits documented; full effect rollback BLOCKED |
| DISPATCH-07 | New fixed offline mode + missing/duplicate/undecoded/tampered/scope refusal tests and owned actual arm64 LLDB | 57 focused tests PASS; TDD first run exactly three expected missing-mode errors |
| DISPATCH-08 | Clean capture, independent original-byte/archive/source proof, full runner/scanner, both exact-source workflows | PASS research verification, detailed identities below; no AE-runtime claim |
| DISPATCH-09 | Existing status/plan/handoff/compatibility, retained receipts and ownership-aware cleanup | Complete; no historical/shared/loaded cleanup |
| DISPATCH-10 | Supported executable host packet + live result | BLOCKED ABI/receiver/thread/admission/drain/rollback; concrete current live scope absent; registration/apply/render NOT RUN |

- Clean file-only collection: `resource-loader-dispatch-df242246-0bv0ep2z.zip`,
  SHA-256 82d221364af8b270a5107107086650e28bee6e6936c966a2336adfa12bcb09d7, 49 ZIP members;
  exact bounds, decoded rows, structural anchors, before/after pin and CRC/hash
  manifest PASS. Adobe/native host calls zero; no scan/AE invocation.
- Separate verifier `/private/tmp/aehl-dispatch-independent.py`, SHA-256
  6c58acbab1fc3e027cdae5891e97162d7a08d774be30af4ec34eacf16cd76b24;
  no collector import. Original arm64 Mach-O mapping and branch decoding:
  11754 instructions, 2157 direct,
  1295 conditional, 209 indirect branches,
  16 returns PASS. Three retained-owner pair writes,
  two vtable-slot loads and two signed-status gates independently decoded.
  Receipt SHA-256 5c07477c7b33927beea4a3938c158a4de63a3a90e21692cfd859144314e36190.
  This corroborates selected file structure, not every transitive semantic effect.
- Full runner `/private/tmp/AEHL-checks-8agpl138.zip`, SHA-256
  e91bff07edf48e0a14da6aba4b718aec59db9574de66b988370505e1438abe39, 25 members; 433 Python, zero skips,
  failures/errors/unexpected successes; 62 Node; all 22 stages PASS. Python
  duration 55.5 seconds. Native syntax/owned controls are offline; actual complete
  AE pipeline BLOCKED. Package/host identity is not release approval.
- Independent runner ZIP CRC/exact inventory/payload hashes and all 336 tracked
  working-file/exact-commit Git blob SHA-256 values PASS. Source inventory
  e1260f5ac6b900c43394ff85bbe255fc735f9011c520acfc8e030916207343f2 recomputed separately;
  clean source and `source_unchanged_after=true`. Source-proof SHA-256
  7d61fdf05911a11af04a884f49a7b90de43ead1ee6ea4d4658e47328151338a0.
- Scanner `/private/tmp/aehl-dispatch-2a2dabb-audit.json`, SHA-256
  aeabbbe12037a796e77f22d25636f2e831c70ca0fba64a32114af1e79c1dbda2, exact clean
  2a2dabb source; raw exit 1 /`review_required`, release readiness `not_assessed`.
  Sole `vibe.no_ratelimit_auth` at tools/artifact_manifest.py:71 inspected: local
  argparse package-manifest CLI, no HTTP/auth route or listener. False positive;
  original scanner output retained, no suppression or weakened test. Separate
  manual code/scanner review SHA-256
  9107f6c33e2a50f5694a2bcffbdbb88de7b35247cc0e398395352701e9ba5e29.
- Research CI [37136115466](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37136115466) and macOS CI
  [37136115496](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37136115496) both completed/success at exact
  2a2dabb68d442355e97e0d1053d84bccef60c825. Current exact result, not prior green CI;
  workflow jobs are offline research/internal build, no AE runtime certification.

## Retention, cleanup and next dependency

Durable private owned receipts:
`build-ae-hot-loader/dispatch-closeout-2a2dabb-_c_bnmmn`. Byte-identical copies of the
collection/runner ZIPs, independent verifier/review, raw scanner/manual review,
TDD logs and source proof retained. RETENTION.json SHA-256
3b83f47c735824460ade297dfbea32e6663cec95c08edeb952628dcb0132fa47; CI.json SHA-256
3a448d0721373e2a0e936e3f2eb860bfbedd836229281b4fb512503e4be2ec9a binds final workflow results.
Fresh exclusive owned outputs, temporary test binaries already removed by owned
test lifecycle, historical/preliminary/shared/loaded/unknown evidence preserved.
No files removed from SDK/app/plugins/projects or an AE session. No cache purge,
unload, reinstall, merge or release. Original product and A/B/C1/C2/D/release still
open; only this bounded research pass is reconciled.

Next dependency: establish actual factory receiver/capability binding and a
supported late transaction that continuously excludes reader/render/MFR work,
provides completion and reverses all effect publication on failure. Only after
those are proven may an identified inert native packet be prepared for a new
concrete live scope. Prior startup/metadata contexts and exception-policy changes
must not be replayed by guesswork. An unchanged ordinary scan is not a discriminator.
