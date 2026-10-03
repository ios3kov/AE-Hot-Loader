# AE Hot Loader — current development status

Updated: 2026-10-03. Branch: `research/ordinary-plugin-discovery`.
Stage **C of A–D**; core registration, A/B/D and release gates remain open.
Current continuation handoff: [CHAT_HANDOFF_2026-10-01_STAGE_C_CURRENT.md](CHAT_HANDOFF_2026-10-01_STAGE_C_CURRENT.md).
AGENTS.md and PRODUCTION_PLAN apply. Current canonical rules:
AE-Development-Rules **8.0.0**, tag `v8.0.0`, peeled commit
`132b7cd32873ba7328e3128ffbb33e1929b74d45`, adopted on 2026-10-03, starting with
AI_ENTRYPOINT.md. Older rule/permission/environment statements below belong
to their named checkpoints and do not supersede this continuation.
Previous status is preserved at
[immutable e96a1c8](https://github.com/ios3kov/AE-Hot-Loader/blob/e96a1c8f31b5aad70c11400b17c1f11e9bbe4154/docs/DEVELOPMENT_STATUS.md).
Dated evidence is unchanged; previous instructions do not renew permissions.

## Module admission — list membership and readiness separated

[Admission review](C1_MODULE_ADMISSION_2026-10-03.md): 12 pinned windows /
3446 instructions /232 anchors. Factory Create inserts before Init; CreateUnknown
checks SetupFilter before returning a module; cache/virtual paths remain conditional.
GetModules has no explicit body lock/readiness check; default AddModuleToList is
no-op and SetdownAsync constructs a ready future, not a proved host drain. Outer
LoadPlugins delegates to LoadPluginList; full transitive late ABI/owner/thread/
admission/drain/rollback UNKNOWN. Backend NOT READY. At exact clean research code
59f1e7ae1a8e279adfb7a9891ff5de6494d203cc: 54 focused /430 full Python, no skips,
62 Node/22 stages PASS; clean collection and independent original-byte/archive/
335-source-file review PASS. Sole raw scanner finding reviewed as a local-CLI false
positive; raw exit 1 retained. Research CI 37135099702 and macOS CI 37135099694
both completed/success at exact 59f1e7a. ADMIT-01–04 bounded file findings documented,
required native contracts BLOCKED; 05 research implementation/refusal checks done;
06 checks/review/both CI complete, 07 docs/cleanup reconciled,
08 executable host experiment BLOCKED,
registration/apply/render NOT RUN. No current AE operation; original product and
A/B/C1/C2/D/release obligations retained. Owned private receipts durably retained;
no shared/loaded cleanup. Next: complete LoadPluginList dispatch/ownership/error
transaction and relevant one-time/virtual delegates.

## Routine-to-effect handoff — internal route found, safe late contract open

[Combined handoff review](C1_ROUTINE_HANDOFF_2026-10-03.md): 17 complete pinned
file windows / 4707 instructions / 275 anchors. Startup registers a setter consumed
by MEE SetupFilter, routed through aelib to FLT provider/path setup and publication.
Cache can skip the callback; nonnegative status normalization is not readiness.
Provider AddEffect can precede failing lazy globals; disposal mutates canonical/
GPU/global/descriptor state without proved whole-effect rollback. A per-module
mutex does not establish continuous all-reader/render exclusion. Actual supported
late ABI/receiver/lifetime/thread/drain/transaction UNKNOWN; backend NOT READY.
At exact clean code e0b85908706290771ba50bd9efe3ff0d59be9772: 51 focused /
427 full Python tests, zero skips, 62 Node / 22 stages PASS; clean collection and
independent original-byte/archive/334-source-file verification PASS. One scanner
finding reviewed as a local-CLI false positive, raw exit 1 retained. Research CI
37133192290 and macOS CI 37133192291 both completed/success at exact e0b8590.
HAND-01–08 bounded file findings documented, required native contracts BLOCKED;
HAND-09 research tooling/checks/review/CI/docs complete, HAND-10 executable experiment BLOCKED, HAND-11/12
NOT RUN. Original product/A/B/C1/C2/D/release retained; no current AE operation.
Next: upstream module admission/initialization and its enforceable late-host contract.

## PiPL publication owner — routine roster and effect registry distinguished

[Publication-owner research](C1_PUBLICATION_OWNER_2026-10-03.md) extends the metadata
lifetime result with 12 complete PLUG/PluginSupport windows, 2403 instructions and
248 anchors. Registration overloads retain routine descriptors/providers in the
PLUG roster under its own mutex; ordinary effects are published separately through
FLT. Provider construction precedes roster locking in two variants. Unregister can
return success for a missing roster entry, or enter unprep/dispose/teardown before
erase; it is not a confirmed whole-effect rollback. Actual runtime provider/owner,
thread/admission/drain/completion/rollback remain unproven. Native backend NOT READY.
At clean research code f5150253c8f1ea013ec7edf3d03d587126a7cd10:
48 focused / 424 full Python tests, zero skips, 62 Node / 22 stages PASS;
clean-source collection and independent original-byte/archive/source review PASS.
Research CI 37132060603 and macOS CI 37132060602 both completed/success at that
exact source. One scanner finding reviewed as a local CLI false positive, raw exit
1 retained. OWNER-07 research checks/review/CI/docs complete. OWNER-01–05 file
findings documented; required native contracts remain BLOCKED. OWNER-06 executable
host experiment BLOCKED,
OWNER-08 NOT RUN. Original product/A/B/C1/C2/D/release retained; no current AE
operation or opaque-context replay, no merge/release. Next: establish the supported
late-entry transaction joining the retained owner to FLT publication.

## Host metadata bridge — lifetime boundary identified, runtime still blocked

[Bounded metadata review](C1_PLUGIN_METADATA_BRIDGE_2026-10-03.md) reconciles PICA
with the historical Dynamic/PiPL and resource/shell findings. In the reviewed
uncached GetPiPLs path, the host callback receives a stack-local metadata vector,
which is destroyed on normal and exceptional exit. Retaining/replaying this
context is NO-GO. Callback success and PiPL conversion do not by themselves prove
ordinary-registry publication; actual transitive targets/receiver/host-wide
admission/drain/completion/rollback remain unproven. Six file-only windows cover
744 instructions / 139 anchors at exact clean code source 9e35d1e. Local checks:
421 Python/no skips, 62 Node/22 stages PASS; actual SDK owned callback control PASS.
Independent file/archive/source-byte review PASS; research CI 37126661037 success,
macOS CI 37126661063 completed/success at exact 9e35d1e. BRIDGE-06 complete.
These are offline checks; no current AE invocation.
BRIDGE-01 research complete; usable mechanism in 02 and full contract in 03 remain
BLOCKED. Host experiment 04 and live 07/08 NOT RUN; no new live scope assumed.
Backend NOT READY; original product and A/B/C1/C2/D/release obligations retained.
Next: follow copied PiPL/path to the publication owner and establish its safe
transaction contract. Preserve previous consumed helpers/session/history.

## Public PICA inventory — all eight pass steps complete, registration open

User authorized the exact packet with “запускай”, then confirmed normal AE Quit
with “закрыл”. Closed-host guards passed; only the unique helper was installed
and one controlled AE 25.6x101 arm64 session launched. Code/helper source
**525000b6915423b7d387f10e846f972472570754**, build **inventory-a96d55e17240**,
PID **28761**, start **1791033664.137575**. One exact request **COMPLETE**,
independently verified. Plug-ins rev4 / Adapters rev3 available, both error 0.
Complete public global PICA list: **2** fully resolved records, both the AE.app
file with standard **Sweet Pea 2 Adapter v1**. Known Control Shell/Rust Probe
files **NOT_LISTED**, although both match names are registered in AE. No direct
file bridge demonstrated; possible host/aggregate/proxy meaning UNKNOWN.
Same blank clean idle project revision 1, **786** effect identities and **1410**
loaded images byte-identical, no additions. [Exact result, interpretation and
receipts](PICA_INVENTORY_REVIEW_2026-10-03.md). INV-01–06 preparation complete,
INV-07 scoped live PASS, INV-08 interpretation complete; one-shot authority consumed.

Preparation 418 Python/no skips, 62 Node/22 stages PASS and research CI 37124717978 /
macOS CI 37124718156 success remain exact 525000b receipts, not rerun for this
runtime doc closeout. Actual helper loading/diagnostic separately verified.
Backend NOT READY; registration/apply/render NOT RUN, A/B/C1/C2/D/release retained.
NO-GO for treating public PICA AddPlugin as a confirmed ordinary-effect registry
bridge. Next: identify a host-specific bridge and its ownership/admission/drain/
completion/failure/rollback contracts; no repeat of this inventory or guessed call.
No broad impossibility claim, shell-only product adoption, merge or release.
Cleanup retains installed consumed helper/session/evidence pending safe closed-host
cleanup; no forced quit, loaded-file removal, third-party/project/SDK changes.
Following sections preserve earlier checkpoints; their pending inventory statements
are superseded by this current closeout.

## PICA live diagnostic — all eight pass steps complete, registration open

User replied “продолжай” to the concrete one-shot request. AE was verified closed
before installing only the identified **pica-1840ac76ef3b** helper and launching
one controlled session. Actual code source **f21064a5ea0e9dc41828987d365d18f8687515e2**,
AE 25.6x101 arm64, PID **14298**, start **1791030995.377505**; final binary SHA-256
`e80e5875033d13e2d43922cc852092ddb2bc056733f5dd91215287852f13066b`.
One exact request **COMPLETE**, independently reverified. All four PICA providers
available: Plug-ins rev4/rev6, Access rev3, Adapters rev3, error 0 each.
Complete global adapter list: only **Sweet Pea 2 Adapter v1**, the SDK's standard
PICA adapter. No separately identified ordinary-effect adapter observed in this
list; no broad absence/impossibility claim. Project/registry/identity unchanged:
blank clean idle revision 1, **786** effects; **1409** images byte-identical.
[PICA result, acceptance and exact receipts](PICA_AVAILABILITY_REVIEW_2026-10-03.md).

PICA-01–06 preparation completed; PICA-07 scoped live observation PASS; PICA-08
interpretation complete. Old and this new one-shot authority consumed; no replay.
Preparation regression remains **399 Python/no skips, 62 Node, 22 stages PASS**;
research CI 37122917227 and macOS CI 37122917217 success at exact f21064a. These
are preparation receipts, not checks rerun for the doc-only runtime closeout.
Actual AE/helper loading is separately verified, not full release certification.

Next: bounded public PICA plug-in inventory correlation with known ordinary-effect
files; review exact revision-6 file-spec/CFURL lifetime first. No native packet or
renewed live scope for that different operation. FindPluginProperty may send a
message/modify properties, so it is excluded from assumed passive name lookup.
Backend NOT READY; registration/apply/render NOT RUN. NO-GO for AddPlugin/private
publication until ordinary-effect bridge/ownership/admission/drain/failure are
established. A/B/C1/C2/D/release obligations and original product contract retained.
No private call, ordinary scan, unload, restart, merge or release. Cleanup preserves
identified installed inert/consumed helper and session pending closed-host cleanup,
other plugins/SDK/historical evidence. No forced termination or removal while loaded.

## Current combined hypothesis pass — offline checks complete, runtime open

User requested all three hypotheses together and then their combinations.
Code/test source **65edce84340fd919e738be65100a8ea73d1c2c31**; rules remain
v8.0.0 at 132b7cd32873ba7328e3128ffbb33e1929b74d45. Acceptance mapping is
in [production plan](PRODUCTION_PLAN.md); findings and exact evidence in
[combined review](HYPOTHESES_REVIEW_2026-10-03.md).
PICA revision-4 AddPlugin and revision-6 AddXPlatPlugin contracts compile against
the actual SDK. The latter requires its own structure/file type; AE suite/provider
and ordinary-effect adapter/publication availability UNKNOWN. Five relevant
literals absent in nine exact pinned files: bounded lexical result only.
Single-effect native invocation remains BLOCKED on ownership, admission/drain
and completion/failure contracts. Historical dynamic-fixture registration delta
and scoped apply evidence are preserved separately from incomplete lifecycle,
render NOT RUN and PiPL/RSMB failures; no broad impossibility claim is justified.
New owned-process test executes actual shell logic with isolated log/home/temp
routing. **383 Python/no skips, 62 Node, 22 stages PASS**, including fifteen
labelled shell checks counted as one aggregate Python test. Archive/source/log
verification PASS; 25 ZIP members / 309 tracked files. Static audit completed,
raw exit 1 with sole known local argparse false positive retained.
Research CI [37121857027](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37121857027)
completed/success at exact 65edce8. macOS CI
[37121857015](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37121857015)
also completed/success at that exact source; CI is not live AE proof.

Combinations reviewed: PICA + ordinary-effect adapter/publication is a conditional
same-goal research candidate. A shell cannot remove initial-registration
prerequisites; adopting a preinstalled shell-only product requires a scope
decision. Next: identify exact AE suite provider and ordinary-effect adapter,
then prepare an identified potential-load availability probe before any
registration operation. No guessed opaque-handle conversion or executable combined
adapter. Current AE registration/apply/render NOT RUN, backend NOT READY;
A/B integration, D compatibility/hardening and release obligations remain open.
README baseline/diagnostic authority reconciled. Cleanup preserves historical,
installed and unknown inputs; only disposable owned test workspaces removed.
No AE operation, merge, release or installable handoff. Documentation-only
closeout is distinct from the tested code SHA above.

## Current five-block pass — offline PASS, live adapter NO-GO

Rules v8.0.0 adopted at the supplied 132b7cd commit. All five scoped offline
blocks are complete at code/test source **a293c90e615dd4a67c2d559422ac990756d79908**:
14 fixed FLT windows / 2413 instructions / 150 anchors; original bytes independently
corroborate 342 direct/44 indirect branches, eight state stores, five TSS-global
address paths and two imported boost get/set_tss_data identities. All twelve
clean-source file-mode archives independently verified.

Local regression **382 Python/no skips, 62 Node, 22 stages PASS**. Research CI
[37120969285](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120969285) and
macOS CI [37120969284](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120969284)
completed/success at exact a293c90. Bounded static review completed; raw exit 1
retains the sole reviewed local argparse false positive. [Exact evidence,
findings and decision](C1_REGISTRY_CONSUMERS_BATCH_2026-10-03.md).

We confirmed that project serialization scopes maintain thread-local data and
cannot be used as global exclusion; preference errors have a path after registry
publication, with no proven registration rollback. Individual registry locks,
settings snapshots and idle/loading counters do not establish the required
continuous all-reader/dispatch/MFR exclusion. **NO-GO for a live adapter using
these reviewed mechanisms**; this is not a proof that the product is impossible.

Backend NOT READY; registration/apply/render NOT RUN; historical unchanged scan
FAIL preserved. A/B integrated acceptance, D compatibility/hardening and release
remain open; no acceptance was removed or weakened. Next: identify a specific
prospective admission/drain provider and proof procedure before extending private
ABI research; actual ownership/completion/error contracts are still required.
No executable live packet or renewed host authority. Cleanup assessed; preserve
unique evidence, old/new rule checkouts and installed helpers; no deletion/move.
Documentation-only closeout must not be presented as the code SHA tested above.

## Latest C1 registry transaction batch — offline PASS

Code/test source **880b55fe7c0fb32b3c978349cf618b45e2f40952**. Six-step batch
reviews startup/resource caller sequencing, selected registry readers/writer,
render scopes and completion/partial-mutation paths, then adds a mandatory
continuously held publication lease to the unbound policy and durable journal.
Seventeen fixed windows / 3063 instructions / 484 anchors; independent original
bytes corroborate 578 direct/71 indirect branches, nine field accesses and three
global-counter address paths. Catalog omission reproduced and fixed.

Full local regression **379 Python/no skips, 62 Node, 22 stages PASS**; all eleven
file-mode archives independently PASS. Policy: 129 synthetic gate cases; journal:
38 real-file/process cases with synthetic host. Research CI [37120018578](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120018578) and macOS CI [37120018592](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120018592) both completed/success at exact 880b55f.
Bounded static review complete; raw scanner exit 1 and sole known local argparse
false positive retained. See [findings, protective change and exact evidence](C1_REGISTRY_TRANSACTION_BATCH_2026-10-03.md).

We now know that selected registry operations lock individually, returned owners
outlive those locks, zero render count does not prevent new work, and a completed
loading flag/normal notifier return need not prove every module succeeded.
These are bounded file findings and tested refusal behavior, not hot registration.
Backend NOT READY. No native adapter, AE operation or renewed live scope.
Next: remaining registry consumers/lifetime and transitive preference/canonical
failure paths; establish an enforceable all-reader/dispatch/MFR exclusion route
or record go/no-go before preparing an isolated adapter. Registration/apply/render
NOT RUN; historical scan FAIL preserved; A/B/D/release gates remain open.

## Latest C1 provider/isolation/completion batch — offline PASS

Code/test source **56be72b888652da450dc58c0d83c64187218af95**. One cycle closes
the bounded file ownership chain, reviews per-effect dispatch counters/guards and
post-setup, and binds three mandatory reviewed contracts into the unbound
resource transaction and durable journal. Old broad native approval alone no
longer permits the model operation. Sixteen complete bodies / 884 instructions /
293 anchors; six original table slots resolve owner/destructor and inherited
Load/GetEntryPoint correspondence. Actual AE receiver identity remains unknown.

Full local regression **376 Python/no skips, 62 Node, 22 stages PASS**; all ten
collector archives independently PASS, including new 105 direct / 24 indirect
raw branches, four rebases and two raw import resolutions. Research CI
37118807823 and macOS CI 37118807775 both completed/success at exact 56be72b.
Bounded static review complete; sole known local argparse scanner false positive
retained. See [combined findings, contract requirements and evidence](C1_PROVIDER_ISOLATION_BATCH_2026-10-03.md).

File evidence now distinguishes object ownership and local guards from host-wide
publication safety. Backend NOT READY; no executable live packet justified:
actual provider ownership, exclusive reader/dispatch/MFR window and complete
native publication/failure semantics remain unproven. No new AE operation;
historical diagnostic scope remains consumed and unchanged scan FAIL preserved.
Next offline block: resource-pass caller, effect-registry reader/writer
synchronization and completion/partial-mutation paths; then reassess an isolated
adapter. Registration/apply/render, A/B/D and release gates remain open.

## Latest C1 combined entry/lifetime batch — offline PASS

Code/test source **50e93973309fbff0b65e37b7c6cbb26e4b9422ad**. One cycle covers
library retention, descriptor/saved-entry/FCSpec dispatch correspondence, a failure
and recovery matrix, and a concrete registration → apply → render trial design.
Twenty-three complete bodies/thunks / 1351 instructions / 225 anchors; all nine
archives independently PASS, including 264 raw direct/22 indirect branches and
29 original fixup-chain rebases. Lookup can load code; private unload is not a
proven rollback. File table correspondence does not identify a live receiver.

Full local regression **372 Python/no skips, 62 Node, 22 stages PASS**.
Research CI 37117715670 and macOS CI 37117715623 both completed/success at
exact 50e9397. Bounded source/static review complete; sole known local argparse
scanner false positive retained. See [combined evidence and trial design](C1_ENTRY_LIFETIME_BATCH_2026-10-03.md).
ASLFoundation's new pin is offline only; native profile/helpers/ResourcePassGate
unchanged. No AE operation or executable live packet. Future trial is BLOCKED on
actual provider/receiver ownership, quiescence/publication isolation and a new
identified adapter/operation scope. Next file work: provider/interface construction
and virtual-table correspondence, then the remaining host-quiescence contract.
Backend NOT READY; registration/apply/render/release remain open.

## Latest C1 provider and canonical factory retention — offline PASS

Code/test source **49a85318fcfb884315b9d36d3cb4b74a094a0399**. Fourteen complete
PluginSupport/TDB bodies / 1365 instructions / 146 anchors; all eight archives
independently PASS, with 257 raw direct and 26 raw indirect branches checked.
Library shared references and canonical/factory tables have separate lifetimes;
Free is a no-op, canonical retrieval can mutate a table, and recursive unregister
is not a proven transactional rollback.

Full local regression **368 Python/no skips, 62 Node, 22 stages PASS**.
Research CI 37116821256 and macOS CI 37116821279 completed/success at exact
49a8531. Bounded source/static review complete; sole known local argparse scanner
false positive retained. See [provider/factory evidence](C1_PROVIDER_FACTORY_REVIEW_2026-10-03.md).
TDB's new pin is confined to a file-only manifest; native profile/helpers /
ResourcePassGate unchanged. No live AE operation or executable live packet.
Next: file-only ASLFoundation Module load/procedure/final lifetime and exact FLT
FCSpec GetRoutineDescH/SetRoutineDescH/GetEffectProc provider/virtual reference path.
Backend NOT READY; registration/apply/render/release remain open. This supersedes
the prepared checkpoint; historical late-registration FAIL remains unchanged.

## Latest C1 effect dispatch and parameter failure — offline PASS

Code/test source **8aec890b95e0eea0216582f43bee0109c31700f3**. Eight complete
FLT bodies / 1939 instructions / 86 anchors; all seven archives independently
PASS, with 377 raw direct branches and three raw indirect-call sites checked.
Canonical registration is called before PARAMS_SETUP; local diagnostic/handle
cleanup does not establish canonical rollback or provider lifetime.

Full local regression **364 Python/no skips, 62 Node, 22 stages PASS**.
Research CI 37060170220 and macOS CI 37060170144 completed/success at exact
8aec890. Bounded source/static review complete; sole known local argparse scanner
false positive retained. See [dispatch evidence](C1_EFFECT_DISPATCH_REVIEW_2026-10-02.md).
Native helpers/profiles/ResourcePassGate unchanged; no live AE operation.
Next: file-only PluginSupport PluginImpl preparation/retention and TDB canonical
factory retention/error paths, with new exact file pins before any body review.
Backend NOT READY; registration/apply/render/release remain open. This supersedes
the prepared checkpoint, without changing historical late-registration FAIL.

## Latest C1 readiness and descriptor ownership — offline PASS

Code/test source **986adb36e2b127c44608ec0a5e30ff165cb6f47d**. Nine complete
file windows / 1136 instructions / 79 anchors; all six mode archives and 146 raw
direct B/BL checks independently PASS. Preparation/global setup change retained
state; a zero preparation return alone does not prove a usable plugin entrypoint,
and safe rollback is unproven. Native helpers/profiles/ResourcePassGate unchanged.

Full clean local regression **361 Python/no skips, 62 Node, 22 stages PASS**.
Static review complete; the sole known local argparse scanner false positive is
retained. Research CI 37057799645 and full macOS CI 37057799722 both
completed/success at exact 986adb3. See [readiness evidence](C1_EFFECT_READINESS_REVIEW_2026-10-02.md).
Next: file-only inner host dispatch, parameter/canonical-stream failure paths
and PluginImpl provider lifetime. Preliminary downstream windows are preserved.
No new live packet/AE operation. Backend NOT READY; registration/apply/render/
release gates remain open. This supersedes the earlier prepared checkpoint.

## Latest C1 ordinary-effect publication review — offline PASS

Code/test source **db4799e2d964a68be761d71924bc5c693d13dea3**. File-only
publication collection PASS: 13 complete windows / 5002 instructions / 83 static
anchors; 48 direct raw BL checks and all five mode archives independently PASS.
The Missing Effect route creates a placeholder, not a loaded plugin. Real resource
setup reaches descriptor retention/post-setup/conditional publication/readiness;
safe isolation from existing GeneralPlugin state remains unproven.

Collector exception-comment false positive fixed; full clean local regression
**358 Python/no skips, 62 Node, 22 stages PASS**. Research CI 37055729740 and
full macOS CI 37055729761 both completed/success at exact source db4799e. Source/static review complete; sole known local
argparse scanner false positive retained (raw exit 1, not security certification).
Native profiles/helpers and ResourcePassGate unchanged; no new AE operation.
See [publication evidence and remaining contract](C1_EFFECT_PUBLICATION_REVIEW_2026-10-02.md).
Next file-only review: FCSpec::ReadyFilter / DoLazyGlobalSetup and PiPL/path
routine descriptor construction. Native backend NOT READY; registration/apply/
render/release gates remain open. Earlier prepared status is superseded.

## Latest C1 retained-name diagnostic — live PASS

The user explicitly approved the exact `identity-d5480a2a4090` install/one-launch/
read-only scope. Fresh AE-absence preflight, unique installation, loaded identity,
blank project and one request PASS; that authority is now consumed. Seven raw
names identify driver, Photoshop import/export and keyframe-assistant state.
Bounded current-file callback correspondence and seven static signature checks
PASS; full loaded-provider identity/lifetime/repeat safety remains unproven.

Registry **786** and project revision **1** stayed unchanged in this session.
Images **1407 → 1408 → 1408**: one permitted system framework addition, no
removed/replaced existing image. **8 copies / 2578 bytes**. Private report SHA
`c0cb5db1e2682e2b7d31e98c916c76f4a447889a4d3689e759790d37c11ce1a8`;
independent archive/hash/semantic checks PASS. No registration/private call/retry/
teardown/project edit/AE termination. At operation closeout PID 28774 and the
consumed helper were preserved; do not infer current process state from this log.

See [exact live result and evidence limits](C1_RETAINED_NAMES_LIVE_PASS_2026-10-02.md).
ResourcePassGate unchanged; current baseline remains ineligible. Next authorized
work is file-only ordinary-effect publication/isolation research without replaying
existing general-plugin initialization. C1 registration/C2 apply-render and release
remain blocked. Earlier NOT RUN/permission statements below are checkpoint history.

## Historical C1 retained-name native adapter and supervisor — preparation PASS

Code/test source **0204ab83212d68b19d85b78d0c7239511f301b7b** connects the
separate helper to actual loaded self/MEE measurement, bounded capture, five-file
journal and external one-shot request/independent verification. Safe public SDK
project snapshot precedes initial binding; scope/images are rebound around capture.
The controller derives expected root from fixed MEE layout plus loaded-image
header/base/slide, and checks a separate 15-second operation budget started before
its claim/publication. On failure/unknown outcome, evidence/process/helper stay
preserved; no automatic retry, private call, ordinary-effect registration or provider retention.

Full clean local regression PASS: **353 Python/no skips, 62 Node, 22 stages**.
Focused candidate/supervisor: 16 Python tests; native binding/capture fixture has
41 nested cases. Independent ZIP/member/inventory/source verification PASS.
Local report SHA-256
`dab580b0db0a15bbce5f2a1c6c264f9cdbc06bdbec41a19d83fbd9da9153c645`.
Bounded source/static review completed: 332 supported files/no omissions, all
selected checks complete; raw exit 1 retains only the rechecked known local
argparse false positive, no whole-security certification. Static report SHA-256
`ab6ae2988e749c62a0add0251648d4c53c126e9d3d4a41b07564db2369ef1ad4`.

Exact new candidate **identity-d5480a2a4090**: real SDK 25.6 build, local signing/
strict verification, two exports, compiled identity and three inert entry cases
PASS (SDK suites=0/root reads=0). Actual loaded self binding in an owned child
PASS; wrong signed-file hash refused. Four bundle payloads, 74 SDK inputs and
fixed provider files independently verified. Final binary SHA-256
`5e87b628434775d702da2c04475d8121d7ad0ecdddb0b28d23582fcb7510c530`;
private manifest SHA-256
`b0ed7a0f1e51d3949a279b94f02faa6b508cb1f127fa5af448eea24836b85968`.

Exact-source [research CI 37052270787](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37052270787)
and [full macOS CI 37052270804](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37052270804)
both completed/success at 0204ab83212d68b19d85b78d0c7239511f301b7b.
At the preparation checkpoint this candidate was not installed/launched/requested.
The subsequently authorized [live diagnostic](C1_RETAINED_NAMES_LIVE_PASS_2026-10-02.md)
now identifies the seven names; its one-shot scope is consumed. The verifier
retains host_execution_verified=false and does not prove allocation lifetime.

See [native candidate review](C1_RETAINED_NATIVE_CANDIDATE_REVIEW_2026-10-02.md),
[supervisor review](C1_RETAINED_SUPERVISOR_REVIEW_2026-10-02.md), and
[exact diagnostic scope and execution](C1_RETAINED_LIVE_SCOPE_2026-10-02.md).
Next: file-only ordinary-effect publication/isolation research. Registration/
apply/render and release remain blocked; no further live action is authorized
by this consumed diagnostic scope.

## Historical rules baseline migration — 6.2.0

User explicitly requested v6.2.0. Published annotated tag/source verified;
AI_ENTRYPOINT and applicable changes read. Standard self-test PASS: 136 files,
43 executed cases, two Windows-only skipped; PowerShell NOT RUN locally.
Applicability map and actual routing contexts PASS. Exact-build compatibility,
remote-packet boundaries and pre-release user documentation are adopted.
See [migration](RULES_ADOPTION_6_2_0_2026-10-02.md) and
[bounded C1 compatibility](C1_COMPATIBILITY_2026-10-02.md).
No runtime/helper/profile change or renewal of consumed diagnostic authority.
Migration checkpoint is closed; current native/supervisor preparation and next
operation boundary are recorded above. Actual seven names are now recorded in the live result.

## Historical rules baseline migration — 6.0.0

User-requested migration from accepted b27f454 is recorded in
[RULES_ADOPTION_6_0_0](RULES_ADOPTION_6_0_0_2026-10-02.md). Published tag/commit,
applicability map/router and full available standard self-test PASS (132 files,
43 executed test cases; two Windows-only skipped, PowerShell NOT RUN locally).
Distribution now requires exact artifact integrity, documented installation and
actual host loading; paid accounts/certificates/remote signing services are not
release prerequisites. Relevant phase/IPC/feature-selection guidance is adopted.
Product runtime/candidate bytes unchanged; historical b27f454 reports retain
their original scope. This migration does not close live, registration or release
gates. Final documentation consistency/pinned-source/local-link checks PASS;
documentation/policy migration complete. No runtime behavior changed.

## Historical Stage C1 count diagnostic — authorized read-only PASS

After the user closed the prior AE session and confirmed full exit, the exact
unused observe-d548b007e316 helper was installed, AE launched once, and one
read-only capture completed **PASS**. External supervisor source f4f84aa and
native source 7c983c5 remain independently pinned. Report SHA-256
`54976e137d928861a5cffd8288e4dccc10a3b347f95b766dab89f297554b16f4`;
independent archive/hash/token/native-evidence verification PASS.

Actual state: **two cleanup callbacks, seven retained general-plugin records**;
20 bounded copies / 496 bytes. Blank/unsaved/clean/idle project, PID/start,
registry (785) and resident images remained unchanged. No private Adobe call,
provider retention, registration, retry or AE termination. Diagnostic authority
and request consumed. AE and the consumed helper are preserved.
See [live result and bounded attribution](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md).

MEE callback matches PluginCleanupFunc; file-only PIN attribution matches
PINp_CleanupFunc → PINp_SortModules, a host global sorting path. Loaded PIN UUID/
content and full lifetime/quiescence remain unproven. The actual retained count
violates ResourcePassGate's zero-record requirement; do not weaken the gate or
invoke teardown. Next independent work: reproducible bounded PIN file review,
then retained-state/lifetime contract. Registration/apply/render and release
remain blocked. Earlier environment/authority records are historical.

## C1 retained host journal — exact-source PASS

All three host observations and both copied-byte captures are now saved in a
private one-shot journal and independently checked. Expected run/candidate/host/
provider/root/paths are bound; changed project/registry/images, malformed or
partial files and an independent expired/backwards deadline refuse. Focused
retained family: 27 Python PASS, including 13 new verifier tests and 19 nested
C++ disk-producer cases. No AE operation or native helper/profile/gate change.
Code/test source dfa78e04d8a1e3f7cae64262a9f13a147aa4a5a3. Full clean local
regression PASS: 337 Python/no skips, 62 Node, 22 stages; independent report/hash/
source verification PASS. Bounded static review retains only known local-argparse
false-positive. Exact-source [research CI 37049587798](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37049587798)
and [full macOS CI 37049587807](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37049587807)
both completed/success at dfa78e04d8a1e3f7cae64262a9f13a147aa4a5a3. Measured native binding and
external request supervision remain unconnected; actual seven names NOT RUN.
See [host journal/verification review](C1_RETAINED_HOST_JOURNAL_REVIEW_2026-10-02.md).

## C1 retained identity transaction — exact-source PASS

The transaction core now refuses wrong-run/process/provider/root/project data,
consumes invalid and concurrent attempts without retry, and enforces a monotonic
15-second deadline around the diagnostic boundaries. Focused retained family:
14 Python tests PASS, including 101 nested transaction cases. Actual capture core
is exercised on owned bytes; no Adobe call, install, launch or sensitive host read.
Native/disk adapter and independent host supervisor are still unconnected; this
is not a live-ready candidate. Code/test source 836c29d3ef18b93a563e1b271198faf1a4eb473f:
full clean local regression PASS (324 Python/no skips, 62 Node, 22 stages), report
hash/inventory/source recheck PASS. Bounded static review retains only the known
local-argparse false-positive. Exact-source [research CI 37047951971](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37047951971)
and [full macOS CI 37047951931](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37047951931)
both completed/success at 836c29d3ef18b93a563e1b271198faf1a4eb473f.
See [transaction acceptance and review](C1_RETAINED_TRANSACTION_REVIEW_2026-10-02.md).

## C1 retained identity journal — exact-source PASS

Code/test source **59becab0056fae08b450cbb4471466b427427744**.
A bounded journal now saves completed raw copy frames from both captures. A
separate Python verifier reconstructs names/read order and refuses incomplete,
inconsistent or wrong-run evidence. Focused journal suite PASS: 11 Python tests,
17 nested C++ journal cases. Native helper/profile, copied-byte/read budgets and
ResourcePassGate unchanged; actual AE names still NOT RUN. Full clean local regression PASS:
323 Python/no skips, 62 Node, 22 stages; archive/hash/source verification PASS.
Bounded static review retains only the known local-argparse false-positive.
Exact-source [research CI 37046241769](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37046241769)
and [full macOS CI 37046241807](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37046241807)
both PASS. Next separate host transaction/
supervisor and inert candidate, with actual binding/pre/postflight and authority.
See [journal/verifier review](C1_RETAINED_JOURNAL_REVIEW_2026-10-02.md).

## C1 retained identity capture — exact-source PASS

Code/test source **eb559edac5d9bf5d3861d5673d9df47e9de1f5e8**.
Separate one-shot capture core is implemented under rules 6.2.0. Strict C++17
focused regression PASS: 46 nested synthetic cases plus actual macOS arm64 owned
heap/main-thread-refusal smoke. Two bounded matching captures, atomic consumed
claim, no retarget/retry; maximum 22 copies / 6,976 bytes. No Adobe calls or
callback invocations. Full clean local regression PASS: 312 Python/no skips, 62 Node, 22 stages;
independent report/hash/source verification PASS. Bounded static review retains
only the known local-argparse false-positive. Exact-source research CI
37043790769 and full macOS CI 37043790324 both PASS.
No native helper/profile or ResourcePassGate change; actual seven live names
remain unknown. Next snapshot journal/independent verifier/supervisor and a
separately identified inert candidate before its operation authority request.
See [capture review](C1_RETAINED_CAPTURE_REVIEW_2026-10-02.md).

## C1 retained-record decoder — exact-source PASS

Code/test source **15c528f6d7dabad83e7203970fc8a09bb2b7e710**. Portable owned-buffer
decoder preserves ordered raw fields/names and rejects bounded inventory or
alias/overlap inconsistencies. Strict C++17 focused suite PASS: 38 nested cases,
zero host/record calls. Full clean local regression PASS: 311 Python/no skips,
62 Node, 22 stages; independent archive/hash/source verification PASS. Bounded
static review completed with the sole known local-argparse false-positive.
Exact-source research CI 37042066391 and full macOS CI 37042066540 both PASS.
Actual seven live names remain unknown; no host read, native helper/profile or
ResourcePassGate change. Next prepare the separately identified one-shot
record/name capture adapter, journal/supervisor and verification before its
operation authority request. See [decoder contract](C1_RETAINED_IDENTITY_DECODER_2026-10-02.md).

## C1 MEE ownership evidence — exact-source PASS

File-only collector source 095a219 reproduces five MEE ownership/lifecycle
windows: 960 instructions, 61 structural anchors PASS. Default search compatibility
PASS (472 instructions). Full clean local regression PASS: 310 Python/no skips,
62 Node, 22 stages. Independent private report/hash verification PASS; research CI
37038542355 and full macOS 37038542153 both exact-source PASS. Bounded static audit
retains the sole known local-argparse false-positive, raw exit 1.

Retention, state overwrite/repeated saved entrypoint call, finish callbacks and
separate teardown release are distinguished. Supplemental 315-instruction AEgx
file review identifies a separate modern AEGP queue; do not equate seven retained
GeneralPlugin records with seven particular AEGPs or borrow public AEGP repeat
semantics. Actual seven-record identities and lifetime/repeat safety remain
unproven. No new live operation, native profile/helper or gate change. Next owned-
buffer record identity/layout decoder and a separately scoped diagnostic contract;
PIN comparator/synchronization remains open.
See [MEE ownership review](C1_MEE_OWNERSHIP_REVIEW_2026-10-02.md).

## C1 PIN file collector — exact local PASS

Reproducible exact-file collector/source c01fb89 completed PASS: 58 instructions,
11 structural anchors. Full clean local regression PASS: 307 Python/no skips,
62 Node, 22 stages. Report inventories/hashes independently verified; bounded
static scan retains sole known local-argparse false-positive. Research CI
37036763724 and full macOS 37036763790 both exact-source PASS. No native profile/helper change
or further live operation. Seven-record blocker unchanged. Next retained-state/
lifetime and PIN comparator/synchronization review. See
[bounded PIN review](C1_PIN_CLEANUP_REVIEW_2026-10-02.md).

## Current Stage C1 — supervisor deadline bug fixed offline

Two reproduced deadline defects are fixed in the external diagnostic and
no-scan supervisors: expired preflight cannot publish a request, and verification that
reaches the deadline cannot return PASS. Both consume/preserve the attempt and
evidence without retry or host termination. Final code/test source
**f4f84aa5a41fd86cc76ee2d702fe61e9b61d16e2**. Focused supervisor family
27 tests PASS; full clean local regression **302 Python/no skips, 62 Node,
22 stages PASS**, inventory/report hashes independently verified. Exact-source
research CI **37024297435 PASS** and full macOS CI **37024297373 PASS**, both
completed/success at that full SHA. Bounded code scan
completed (266 supported files/no omissions), raw exit 1 retained for the sole
known local argparse false-positive. Native candidate bytes
are unchanged; no installation/launch/read performed. See
[deadline review](C1_SUPERVISOR_DEADLINE_REVIEW_2026-10-02.md).
The later diagnostic authorization is recorded above; actual complete-state/
lifetime/repeat evidence still blocks dependent registration; ordinary registration/apply/render NOT RUN.

## Historical preparation — diagnostic authority was initially blocked

Latest user direction on 2026-10-02: publish a release ("релиз делай").
Publication is now explicitly requested; do not ask for that permission again
after the mandatory exact-candidate gates pass. This does not close or waive
the release gate, authorize an unverified build as production-ready, or supply
the separate install/AE-launch/sensitive-read scope rejected by automatic review.
Release execution remains BLOCKED on Stage C1/C2, integration and Level 2
evidence. No tag, release, merge or main change was performed.

Independent continuation check on 2026-10-02: clean documentation head
`5a74fd8d78bc28fab633e8abbc43cd8cdea60578`, unchanged code/test head below.
Offline code-profile static scan completed all selected checks: 265 supported
files, no candidate omissions, four workflow files. Raw exit **1** / verdict
`review_required` is retained: the sole finding is `vibe.no_ratelimit_auth` at
`tools/artifact_manifest.py:71`. Reinspection confirms local `argparse` handling,
no authentication/network route; classification remains false-positive.
No new scanner findings; overall security/release readiness is not assessed by
this scan. Binary inspection, dependency advisories, full security review and
live gates remain separate. Evidence scope digest
`25e6c15ba0bde24dd1081b2d2478be62f405cd7fdceb42f7d8bf3be408252931`;
private JSON report SHA-256
`b16f7d24decb13af96a6f20e2804766f5abeab91e9be6770ab78cb7f5b802aa8`.
No behavior/artifact change; existing candidate identity remains unchanged.
The requested explicit live diagnostic scope is still pending; no install,
launch or capture was performed in this continuation.

Code/test head: **`7c983c5b5adfde0300f2370e5772ed757ab6b613`**.
Separate inert AEGP, durable one-shot diagnostic transaction and independent
supervisor are prepared. Exact clean local PASS: 298 Python/no skips, 62 Node,
22 stages; research CI **36931094055 — PASS**; full macOS CI **36931094195 — PASS**.
SDK build/sign/export/identity and three inert cases PASS for
**observe-d548b007e316**. Candidate inventory/all hashes independently verified.
Evidence: [C1_OBSERVER_CANDIDATE_REVIEW_2026-10-01.md](C1_OBSERVER_CANDIDATE_REVIEW_2026-10-01.md).

The proposed unique-helper installation / one test AE launch / one sensitive
read-only capture was rejected **before execution by automatic approval review**
for lack of explicit user authority for those exact live actions. No install,
launch, request, native root read, provider retain or private Adobe call occurred.
No bypass attempted. Process-list checks found no AE at their check time; current
project/resident state remains NOT OBSERVED.

At that checkpoint the next step required exact diagnostic approval. That
approval is now granted; the current environment refusal above controls continuation. Continue
independent authorized work; generic development scope does not bypass the
reviewer's decision. Complete cleanup, allocation/lifetime/quiescence and
repeat behavior remain unproven; no ResourcePassGate integration. Native C1
registration backend NOT READY; registration/apply/render NOT RUN. C0 recorded
PASS; historical registration FAIL preserved. Original checkout/main/release
boundaries remain intact.

## Second live no-scan result — PASS; Stage C0 closed

The second authorized no-scan request ran from source
**`182d058254203236414602acdd9901b8749d89cc`**, build
`noscan-8f9cb9fea71c`, run
`directory-probe-d097765fede949f5b9958b2897687df2`.

Report ZIP SHA-256:
`f767e891359a3e73dc41eefe4124fe63dc0cf4dde123c2d7efa7444cd35bc62a`.

The uploaded report was independently rehashed and every archived payload was
verified against `report-hashes.json`.

Result: **PASS**.

Exact native lifecycle evidence:

- invoked = 1;
- completed = 1;
- cleanup_ok = 1;
- strings created/released = 2/2;
- specs created/released = 1/1;
- retained provider references = 3.

Before/after host evidence is byte-identical: project revision 1, runtime image
count 1402, and complete registry count **785** all remained unchanged. No lazy
system image appeared in this run. `plugin_scan_requested=false`.

This closes the no-scan FILE ownership/binding gate: **Stage C0 = PASS**.

See [NO_SCAN_DIRECTORY_LIVE_PASS_2026-10-01.md](NO_SCAN_DIRECTORY_LIVE_PASS_2026-10-01.md).

Ordinary-effect late registration is still NOT fixed. The historical registration
FAIL remains unchanged. The next development gate is Stage C1: a single-root
resource-registration experiment, first prepared and reviewed offline. Any live
private PLUG/resource-registration call requires fresh authorization; the second
no-scan approval was consumed by this PASS.

## First live no-scan result — FAIL; evidence gap remediated offline

The first real no-scan request ran from source
**`161b180714a734baf71f8c8cb58440e73f8dcd23`**, build
`noscan-f0aa4a3bd54a`, run
`directory-probe-11f0a9c60dc44fcea98579536234fd34`.

Report ZIP SHA-256:
`727a65d7ba64be8371c40025a4fc2196785216cc77299941d0978a71eb0cff5a`.

Result: **FAIL at postflight**. The single request was published; call-started,
postflight and cleanup evidence were present. PID/process-start, project
revision and the full effect registry stayed unchanged at **785** effects.

The only before/after image delta was one new Apple system framework,
`/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/SafariPlatformSupport`.
No image was removed and no Adobe/user/plug-in image was added.

The old gate required byte-identical image lists, so the system lazy load caused
the FAIL. The old journal also did not persist the complete native lifecycle
counts before postflight, so this report cannot prove the FILE
create/roundtrip/single-release acceptance even though cleanup was reported
successful. No retry was performed.

Offline remediation is complete at code head
**`dadd884b4758a351fbc725969ed49d2f9a912781`**:

- `native.txt` is durably written immediately after the private call;
- PASS requires exact string/spec/release/retention counts;
- existing runtime images must remain exact;
- only newly loaded `/System/Library/` images may be tolerated;
- new Adobe/user/plug-in images still fail;
- the external supervisor independently checks the same contract.

Exact-head research CI **`36857286317`** — PASS.  
Exact-head full macOS CI **`36857286194`** — PASS.

See [NO_SCAN_DIRECTORY_LIVE_FAIL_2026-10-01.md](NO_SCAN_DIRECTORY_LIVE_FAIL_2026-10-01.md).

A second live request is **NOT RUN** and needs fresh authorization because the
first one-shot approval was consumed.

## Live-ready one-shot launcher checkpoint

Current live-launcher code/test head is **`3852192406da5af539b9100114393584642e9197`**.

Added `RUN_LIVE_NO_SCAN_GATE.command`, a fail-closed one-shot launcher for the
authorized Mac. It:

- requires the research branch and a clean checkout;
- fast-forwards only, never resets or overwrites local work;
- refuses to touch an already-running After Effects session;
- requires the reviewed AE 25.6 application path;
- locates an already-extracted SDK or accepts `AEHL_SDK`;
- builds the unique inert no-scan AEGP with the reviewed builder;
- installs only that newly named helper into the user MediaCore root, never
  replacing another plug-in;
- verifies installed bytes/signature before AE launch;
- launches After Effects exactly once with the one-shot activation token;
- waits for exact helper-ready evidence;
- invokes the existing supervisor exactly once with the approved private FILE
  and provider-retention flags;
- contains no `PLUG_Search`, old `ML::LoadPlugins` path or ordinary-effect scan.

Dedicated launcher source-policy tests were added. The unified macOS research
runner also syntax-checks all top-level `.command` files.

Exact-head verification for `3852192`:

- research CI **`36855482114`** — PASS;
- full macOS CI **`36855482175`** — PASS.

This makes the one-shot launcher **ready for the authorized Mac gate**, not a
live AE PASS. No private FILE call, provider-reference retention or new helper
installation was executed by CI.

The user's explicit authorization in this chat covers this one no-scan gate:
the unique helper installation / one AE launch if needed, the private FILE call,
and retaining the three already-loaded FILE/U/dvacore references until process
exit. It does not authorize a plug-in scan, ordinary-effect registration,
additional retries or later Stage C1 operations.

## Current Stage C checkpoint — identity + final ZIP evidence hardened; CI green

Current Stage C code/test head is **`c1e20e4ab4d4a4f6654f67df7dbb224f0790b5be`**.
The external no-scan supervisor now reads the process start tuple through macOS
`proc_pidinfo(PROC_PIDTBSDINFO)`, matching the exact `sec.usec` identity written
by the AEGP. Preparation refuses a loaded-helper start identity that differs from
the supervisor's host identity **before request publication**. The later native
journal must still match that same AEGP start identity. A real macOS self-process
regression covers the libproc representation; Linux records that case as an
explicit platform skip.

The no-scan report packager now also verifies the final ZIP inventory and every
archived payload against `report-hashes.json`, then prints the final report
SHA-256. The request/token is still excluded from the report ZIP.

Exact-head research CI **`36854509313`** completed successfully on Linux and
macOS. Exact-head full macOS CI **`36854509275`** also completed successfully,
including the Python/Node/no-scan regressions, existing product build/sign/package
and smoke gates. These are still offline/build evidence only; no private Adobe
function was executed by CI and no live AE registration result changed.

CI coverage was also corrected at **`6009c18552c5d6be0e64b7af7e0f315fac840c0e`**:
changes under `experiments/**` now trigger the full macOS workflow instead of
only the research workflow.

The five previously recorded static-scanner candidates were revisited. Four real
workflow-policy issues in `dual-pipl.yml` were fixed/classified through
`54eb513dc3526f75f1446e3a80223fa3a06eea7c` and
`da5d3a8e5a69b9cb719997ddba835e1a56f5d896`; all current workflow `uses:`
references are SHA-pinned and every checkout disables credential persistence.
The fifth historical candidate remains the previously reviewed local-argparse
false positive. **Known five candidates are resolved/classified; a new full
static-security audit is still NOT RUN.** See
[STATIC_AUDIT_CLOSEOUT_2026-10-01.md](STATIC_AUDIT_CLOSEOUT_2026-10-01.md).

README and the current production plan now describe AE Hot Loader as a **tool**
with internal AEGP helpers and distinguish the no-scan safety helper from the
ordinary effect being researched.

Live AE remains **NOT RUN / NOT OBSERVED** for this checkpoint. The user's
`/Users/os3kov/Documents/AE-Hot-Loader/` checkout, current AE PID/project and
installed/loaded no-scan helper are still not accessible from this environment.
The real folder-object gate therefore remains pending.

Before that live gate, the exact no-scan AEGP still needs a dedicated SDK build,
sign/hash/inert verification and installed/loaded identity on the authorized Mac.
Because the AEGP must be present in AE, any new installation and AE launch/restart
also require fresh authorization if needed. Separately, publishing the one-shot
request requires explicit approval for the private FILE call and retaining the
three already-loaded FILE/U/dvacore references until process exit. The first live
run remains folder create → path roundtrip → single release only, with **no plug-in
scan or ordinary-effect registration**.

## Previous code checkpoint — ready/journal process identity binding; CI green

Current code head is **`a0d08f46c45c56b2695b82d2ff71d7e5da08a6c1`**. The existing
no-scan folder-object gate now writes the native process start identity into
`ready.txt`, and the external supervisor requires the later native journal to
contain that exact same start identity. PID equality alone can no longer satisfy
the cross-process evidence check. A negative owned-fixture test proves that a
mismatched start identity fails the run and still preserves the one ZIP report.

This is a hardening of the already connected no-scan gate, not a new Adobe call,
plug-in scan or registration path. The change adds no private API, no provider
load, no installation and no restart.

Exact-head research CI **`36842766751`** completed successfully. Exact-head full
macOS CI **`36842766786`** also completed successfully for the same code head.
The macOS product pipeline remained synthetic/build-only; its packaged panel
regression reported 51/51 Node tests. Live AE, private FILE execution, retained
Adobe provider references, dedicated user-Mac SDK candidate build and the real
folder lifecycle remain **NOT RUN / NOT OBSERVED** here.

## Previous code checkpoint — timeout contract hardened; CI green; live host still NOT RUN

Previous code head was **`0e63156cbbbd3b1ec1c37ca6d8701af1cd5ed7e9`**. Four commits after `763c6e7` hardened the one-shot supervisor deadline: the native directory call remains bounded at 15000 ms, the external supervisor must allow at least a 5000 ms margin, and shorter timeouts are rejected before request publication. The final test-only adjustment aligns the PASS fixture with that reviewed floor. No plug-in scan or registration call was added.

Exact-head CI is green: research run **`36835180596`** and full macOS run **`36835180654`** both completed successfully. These remain offline/build evidence only; dedicated SDK build on the user's Mac, local checkout identity, current AE/PID/project/module baseline, private FILE call, provider-reference retention and real folder lifecycle are still **NOT RUN / NOT OBSERVED** here. No installation, restart, live Adobe call, merge, release or `main` change was performed.

## Post-checkpoint result — no-scan bridge connected in source; live host still NOT RUN

The separate inert-by-default no-scan AEGP and external one-shot supervisor are now
connected in source. The implementation was introduced at `422abba40644216ae9076ed4f148172ae9fe72c0`;
macOS CI then exposed test-fixture paths traversing the platform `/tmp`/`/var`
symlinks. Production path guards were not weakened. The fixtures were canonicalized
at `bdbb98940f8daab64332ec517ef0052e5793775d`, and the current code was hardened at
**`763c6e7e2fa73ef58fa38353c9ac41b21f26b02c`** so a clean checkout can create the
build parent and `adapter-stopped.txt` is retained in the single failure ZIP.

The AEGP has no plug-in scan/registration call in this probe path. Without the exact
startup token, exact host/module identity and private owned directories it returns
inert. After a separately published exact one-shot request, the native operation is
limited to one newly owned directory object, exact path roundtrip and one release.
The supervisor publishes at most one request, never retries an uncertain native
outcome, and packages one sanitized report ZIP. These are source/offline properties;
they do not prove execution inside After Effects.

Research CI **`36833660016`** passed on Linux and macOS. Full macOS CI
**`36833660022`** passed for exact code `763c6e7`: Python 243 tests, no-scan gate
11 cases, owned directory 28/28, resource gate 63, resource journal 32 and existing
scoped guards 15; product build/sign/package/smoke/archive checks also completed.
The dedicated no-scan AEGP SDK build and any live AE call were **NOT RUN** by these
workflows. Green CI therefore remains offline evidence only.

The user's Mac checkout and current AE/PID/project/resident-module state are still
**NOT OBSERVED** in this chat; the previously reported local `ce5d80d` state has not
been confirmed or updated here. No installation, AE launch/restart, private Adobe
call, provider-reference retention in AE, project/preferences change, third-party
plug-in change, merge, release or `main` change was performed.

Fresh live authorization is still required for the private FILE call and retaining
three already-loaded provider references until process exit. Previous install/restart
permission remains consumed. The first live gate remains folder lifecycle only;
`PLUG_Search` and ordinary-effect registration are explicitly outside that run.

## Historical continuation checkpoint — 2026-10-01

This records the state saved at checkpoint `90c257c`; the post-checkpoint section
above is the current continuation state.

[CHAT_HANDOFF_2026-10-01.md](CHAT_HANDOFF_2026-10-01.md) is the restart point for
the next chat. It preserves the exact code/CI identity, historical AE outcomes,
consumed permissions, existing private-input inventory and remaining integration.
This save changes documentation only. Code remains `9ea7bcf57fffee2382c6890459dca89201345395`;
research CI `36824300893` and macOS CI `36824300983` were rechecked successful.
No new tests or live AE operations were run. The no-scan AEGP and live supervisor
are still not connected; registration remains unproven. Documentation uses [skip ci].
The user's Mac checkout and current AE state were not inspected or updated.

## Latest result — U/dvacore checked; provider retention tested on macOS

The supplied U/dvacore archive was independently hashed. Both binaries agree
with its matching before/after statements. Their actual producer/destructor and
storage bodies match the directory adapter's representation for this exact build.
The converter is ASCII-only, not UTF-8; non-ASCII probe paths remain blocked.
The destructor recycles host-allocated storage and has a terminate path, so not
every native failure is catchable. No Adobe binary was loaded or executed.

Added `AE256DirectoryProfile.hpp` with exact received FILE/U/dvacore digests,
and `ResidentDirectorySession.hpp` with a controlled already-loaded-reference
wrapper. Exact code commit: **`9ea7bcf57fffee2382c6890459dca89201345395`**.
It validates providers, retains up to three RTLD_NOLOAD references, then rebinds
under those references. Missing images are refused, never loaded as a fallback.
There is no dlsym, startup replay, plugin scan or automatic AE entrypoint.

The wrapper intentionally keeps acquired references until process exit, including
partial failure; it never unloads a provider. **This changes loader reference
counts and must be included in future explicit host-test approval.** Its boolean
is only a supervisor assertion, not verified consent or a durable claim. The
existing disk journal and fresh host/project guards still have to be connected.

The macOS test uses three OWNED libraries. After the wrapper retains them, the
test closes all original references and successfully runs the directory lifecycle
through the remaining references. Image-list, missing-image, bad-digest,
permission-assertion, environment-override and repeat-attempt checks passed.
This proves the tested owned-provider behavior, not execution of FILE/U/dvacore.

[Exact input identities, static findings, lifetime tradeoff, checks and limits](U_DVACORE_CONTRACT_2026-10-01.md).
U/dvacore implementation availability is no longer the current blocker.

## Checks for exact code 763c6e7

| Check | Result and scope |
|---|---|
| Research CI 36833660016 | PASS, Linux + macOS; unified offline result explicitly says full AE pipeline BLOCKED |
| Full product macOS CI 36833660022 | PASS; Python 243, no-scan gate 11, owned directory 28/28, resource gate 63, resource journal 32, scoped guards 15 |
| No-scan source integration | PRESENT: inert entry, one-shot journal/supervisor, one ZIP, no plug-in scan in this probe path |
| Dedicated no-scan AEGP SDK build | NOT RUN in the cited workflows |
| Real AE folder-object lifecycle | NOT RUN; private FILE/provider-retention authorization still required |
| Ordinary-effect late registration/apply-render | NOT RUN; historical registration FAIL unchanged |
| User Mac checkout / current AE state | NOT OBSERVED in this chat |
| Full static-security audit | NOT RUN again; five historical findings remain open |

Commit `422abba` initially failed macOS automation only because new security tests
used temporary paths whose parents are symlinks on macOS. The code now canonicalizes
only those owned test fixtures; the production no-symlink checks remain strict.
Commit `763c6e7` additionally fixes clean-build parent creation and preserves the
AEGP stop marker in failure reports. No live Adobe evidence is inferred from CI.

## Preserved checks for exact code 9ea7bcf

| Check | Result and scope |
|---|---|
| Received-file integrity and 24 structural assertions | PASS, six named windows / 529 instructions; not runtime tests |
| Actual export parsing and compiled profile hashes | PASS; file-only, Adobe calls=0 |
| Local unified Linux | PASS: 238 collected, 229 PASS/nine platform skips; Node 62 |
| Research CI 36824300893 | PASS on Linux and macOS |
| Downloaded macOS unified report | All 21 stages PASS; Python 238/238, Node 62 and existing scoped guards 15 |
| Owned provider retention and directory lifecycle | PASS on macOS arm64, including calling after original references are closed |
| Full product macOS CI 36824300983 | PASS, all build/sign/package/smoke/archive-verification steps completed |
| Downloaded research reports and source identity | Both outer hashes, all inner entries and five changed source hashes verified |
| Real AE no-scan AEGP/supervisor | NOT CONNECTED / NOT RUN |
| Actual resource registration/apply-render | NOT RUN; historical registration FAIL unchanged |
| Full static-security audit | NOT RUN again; five historical findings remain open |

The Python count remains 238: the new retention scenario extends an existing
test. Nested native cases are not counted again. Local parser ASan/UBSan passed
with empty diagnostics, not a full audit or AE memory proof. The unified local
runner still does not build the product; that separate workflow was checked.
No product ZIP was installed or handed over. Green CI does not clear unreviewed
warnings. Docs use [skip ci]; CI belongs to the exact code commit above.

## Next concrete integration gate

The source connection is complete; the next gate is the exact SDK build plus
preparation/inert verification on the authorized Mac, followed by exactly one live
folder-object run only after fresh authorization for the private FILE call and
provider-reference retention. The live run must still begin from a fresh blank,
clean, idle AE 25.6 host and produce one report ZIP without any plug-in scan.

This chat cannot inspect or update `/Users/os3kov/Documents/AE-Hot-Loader/` or the
running AE process, so local checkout synchronization, SDK build identity, loaded
artifact identity and live baseline remain blocked on access to that Mac. No new
library collection or repeat of the unchanged ordinary plug-in scan is justified.

Before a live call, verify SDK build, inert entry, exact artifact/loaded identity,
fresh blank/clean/idle host state, one owned ASCII directory, and separately
specified authorization including provider-reference retention. Require exact
path roundtrip, single successful release and unchanged PID/project/registry/
module list. Do not treat the authorization flag or stored observations as consent
or a fresh baseline. No automatic retries after uncertain native outcomes.

The subsequent PLUG pass still needs end-of-pass callback and retained-state
review. Do not invoke global-folder helpers, Birth/InitIterator/RequiredPreSearch,
replace callbacks, bypass the cache predicate, clear caches, force notifications,
change the old bool, unload code or repeat the unchanged scan. Previous installation
and one-restart permissions are consumed. New risky actions need separate approval.

## Preserved actual host results

| Gate | Preserved result |
|---|---|
| Scoped embedded late registration | FAIL: 45de0c9 / scoped-0b8c8f122e80 / fixture88019a1a01a7; 785 unchanged effects |
| RSMB startup-registered apply/render | PASS: earlier identified one-frame smoke |
| RSMB late registration | FAIL, retained separately |
| Dynamic fixture application | PASS, earlier add/remove; render NOT RUN |
| Flat-resource failure | FAIL, earlier crash evidence retained |
| Current AE/project/resident identity | NOT OBSERVED; offline files and CI are not a live baseline |

The SDK review did not establish a public ordinary-effect late-registration
procedure; PICA ordinary-effect publication remains unverified, not disproved.
No product loader, installed Agent/shell/panel, third-party plugin, user project,
preferences or main changed. No merge, release, installation, restart or live
Adobe call. Proprietary inputs and raw dumps remain private, outside Git.
