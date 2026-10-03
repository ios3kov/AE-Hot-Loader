# AE Hot Loader — current development and release plan

Updated: 2026-10-03. Branch: `research/ordinary-plugin-discovery`.

Source of current verified state: [DEVELOPMENT_STATUS](DEVELOPMENT_STATUS.md).
Accepted standard: **6.2.0**, `v6.2.0` peeled to
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`, adopted on 2026-10-02.
Canonical [AI_ENTRYPOINT](https://github.com/ios3kov/AE-Development-Rules/blob/d966078a9e45fee7ec9ad14f211a9da753d64b8a/AI_ENTRYPOINT.md)
and its selected AE Development Rules modules, plus `AGENTS.md`, apply.
Historical plans/evidence remain preserved and must not
be treated as current approval.
Migration scope/evidence: [rules adoption](RULES_ADOPTION_6_2_0_2026-10-02.md).
Current bounded [compatibility inventory](C1_COMPATIBILITY_2026-10-02.md) records exact AE/candidate scope.

## Product scope

AE Hot Loader is a **tool/panel**, not an ordinary effect plug-in. Native AEGP
modules are internal helpers when code must execute inside After Effects.

Primary Stage C goal:

> make an ordinary effect that is absent from the running AE registry become
> registered in that same identified process, then prove apply and render
> separately without restarting AE.

Loaded binaries, registry publication, application and rendering are separate
claims.

## Latest C1 combined entry/lifetime batch — prepared, acceptance pending

Stage C1 / Development, rules 6.2.0. This combined cycle covers library retention,
FCSpec/PLUG saved-entry correspondence, failure/recovery constraints and a concrete
future AE trial design. Twenty-three complete bodies/thunks / 1351 instructions /
225 anchors plus three serialized tables / 29 rebases; new focused suite 32 PASS.
ASLFoundation pin is offline only; native profile/helpers/ResourcePassGate unchanged.
Clean-source collection, independent original-byte verification, full regression/
static review and exact-source CI remain pending. No live packet or AE operation.
See [combined evidence and trial design](C1_ENTRY_LIFETIME_BATCH_2026-10-03.md).
Backend NOT READY; actual registration/apply/render/release remain open.

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

## Preserved baseline

- Scoped embedded late registration: **FAIL**
  (`45de0c9` / `scoped-0b8c8f122e80`; 785 effect identities unchanged).
- RSMB startup-registered apply/render: **PASS**, startup baseline only.
- RSMB late registration: **FAIL**.
- Supported public SDK late-registration procedure: **NOT ESTABLISHED**.
- Original user checkout remains preserved; latest owned test AE runtime
  identity/project/registry were verified by the C1 read-only diagnostic.
  This is not live registration/apply/render evidence.

Do not repeat the unchanged historical scan merely to reproduce this baseline.

## Stage C0 — no-scan FILE ownership gate — PASS

Live PASS evidence: [NO_SCAN_DIRECTORY_LIVE_PASS_2026-10-01.md](NO_SCAN_DIRECTORY_LIVE_PASS_2026-10-01.md).

Source `182d058254203236414602acdd9901b8749d89cc`, build
`noscan-8f9cb9fea71c`, report SHA-256
`f767e891359a3e73dc41eefe4124fe63dc0cf4dde123c2d7efa7444cd35bc62a`.

The exact directory lifecycle completed with 2/2 host-string releases, 1/1
spec create/release, three retained provider references, unchanged project,
unchanged 785-effect registry and unchanged runtime image set. No plug-in scan
was requested.

### Implemented in source/offline tests

A separate research-only inert AEGP and external one-shot supervisor are
connected. They are not the ordinary effect being loaded.

The live operation is deliberately limited to:

1. fresh exact AE/process/project/module baseline;
2. one new owned ASCII directory;
3. create one host directory specification;
4. exact path roundtrip;
5. release it once;
6. postflight proof of unchanged PID/start/project/registry/image list;
7. one report ZIP.

The path contains **no `PLUG_Search`, ordinary-effect registration or broad
plug-in scan**.

The supervisor publishes at most one request and never automatically retries an
uncertain native outcome.

### Gate before live execution

Before publishing the request:

- exact clean source commit and Build ID;
- exact SDK build of the no-scan AEGP on the authorized Mac;
- signed artifact plus final hashes/manifest;
- inert-entry verification;
- exact installed/loaded module identity;
- AE 25.6x101 arm64, fresh blank/clean/idle project;
- exact reviewed FILE/U/dvacore provider identities;
- one fresh owned/private probe directory;
- separate explicit authorization for:
  - the private FILE call;
  - retaining three already-loaded provider references until process exit.

A failure or timeout preserves evidence and stops. No retry, AE kill, provider
unload or cleanup of uncertain native state.

### Acceptance

PASS means only:

- exactly one specification was created;
- the returned path equals the approved path;
- owned host strings/specification have the reviewed release counts;
- exactly three approved provider references were retained;
- cleanup completed;
- all pre-existing host/project/registry/runtime-image evidence remains exact;
- only newly loaded immutable `/System/Library/` images are tolerated by the
  remediated policy; the successful run added none.

It does **not** mean ordinary-effect late registration works.

## Stage C1 — resource-registration experiment

Independent external-supervisor deadline remediation on 2026-10-02:
[C1_SUPERVISOR_DEADLINE_REVIEW](C1_SUPERVISOR_DEADLINE_REVIEW_2026-10-02.md).
Reproduced premature request publication and late PASS acceptance are fixed
in both diagnostic and no-scan supervisors. Final source f4f84aa local regression
PASS (302 Python/no skips, 62 Node, 22 stages), bounded code scan completed with
sole known false-positive. Exact-source research CI 37024297435 and full macOS
CI 37024297373 PASS. This offline remediation is complete. Native candidate
unchanged. The later authorized diagnostic installed/launched/captured once and
passed; complete-state gates remain open. See
[C1 live diagnostic](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md).

Current offline checkpoint: [C1_OBSERVER_CANDIDATE_REVIEW_2026-10-01.md](C1_OBSERVER_CANDIDATE_REVIEW_2026-10-01.md).
The isolated sampler captures ordered callback pairs and retained record count
within caller-supplied regions, comparing two bounded captures without calls or
retries. It does not create a complete observation or connect the C1 backend.
Matching reads are not atomicity, allocation or provider identity proof.

Static root provenance is verified in exact pinned PLUG/MEE zero-fill sections;
PLUG requires slot → handle → sack, not direct slot → sack. Resident root binding
is now verified on owned data and is only a point-in-time identity/address check.
Current-process mapped-range reads now pass owned-page/boundary/mutation checks
and exact clean-source CI. One-shot diagnostic observer composition now passes synthetic and actual owned
provider/heap-chain checks and exact CI. The separate inert diagnostic AEGP/supervisor candidate is now built/signed/hashed
and verified at clean 7c983c5, exact CI PASS. Live installation/launch/sensitive
read approval was initially rejected before execution by automatic review.
The user has now explicitly approved the concrete observe-d548b007e316 scope.
Preflight initially preserved the existing AE session. After the user closed
it, the one authorized diagnostic completed PASS and consumed its authority.
Actual baseline has two callbacks and seven retained general-plugin records; heap ownership and host lifetime/quiescence remain unresolved. Repeat preparation can still invoke saved entrypoints;
the ResourcePassGate must continue requiring complete reviewed cleanup state
and zero retained general-plugin records. These are necessary restrictions,
not proof that a real baseline is eligible. Actual state/other callback effects
remain UNKNOWN; dependent native integration is blocked. Do not replay setup,
setdown/unprep, relax the restriction or replace callbacks. No native C1
backend/live request is ready. Prior records are preserved.

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

Only after C0 PASS:

1. review PLUG end-of-pass callbacks and retained state;
2. freeze the exact single-root resource-pass contract;
3. prepare one fresh embedded ordinary-effect fixture;
4. use a new Run ID, Build ID and one-shot evidence directory;
5. execute at most one bounded registration attempt.

Forbidden shortcuts remain:

- global plug-in root enumeration;
- Birth/InitIterator/RequiredPreSearch replay;
- callback replacement;
- cache-predicate bypass;
- cache purge/forced notification as a registration mechanism;
- another `ML::LoadPlugins` pass alongside the resource pass;
- unloading provider code;
- reuse of consumed fixture/claim evidence.

### Registration acceptance

Registration PASS requires an exact new intended match name in the complete
effect registry of the **same AE process**, with unchanged project state and
without unrelated registry/module changes.

Loaded-image evidence alone is insufficient.

## Stage C2 — apply and render

After exact registration PASS:

- apply the newly registered installed-effect key to an owned fixture;
- prove effect instance creation separately;
- render an identified output separately;
- preserve source/artifact/runtime identities and output evidence.

Registration success must not be promoted to apply/render success.

## Stage D — integration and hardening

After C succeeds:

- real ScriptUI/tool → Agent/helper roundtrip;
- repeat/no-op/error/timeout ownership;
- multiple panel instances/reopen;
- project safety;
- cache invalidation/fresh evaluation UX where applicable;
- clean install/update/rollback behavior;
- compatibility matrix for the actually supported AE/macOS/architecture scope;
- full static/security review;
- Regression Level 2.

Offline code-profile scan at clean `5a74fd8` on 2026-10-02 is complete for its
bounded text scope: 265 supported files, no omissions, sole reviewed local CLI
false-positive (raw exit 1 retained). It does not close the full static/security
review or dependency/runtime checks above. Exact report identity is recorded in
DEVELOPMENT_STATUS; historical closeout evidence remains unchanged.

## CI and artifact requirements

Every behavior/artifact change must keep:

- unified offline checks green;
- macOS product regression green where applicable;
- `experiments/**` changes covered by macOS CI;
- pinned workflow actions/toolchains and locked dependencies;
- clean Git/source identity;
- Build ID + final SHA-256/manifest for testable artifacts.

The public CI environment does not contain the proprietary AE SDK/provider
runtime. Therefore CI cannot substitute for the dedicated SDK build and real AE
C0 gate on the authorized Mac.

## Release gate

The user explicitly requested release publication on 2026-10-02. Publication
permission is recorded; the mandatory readiness conditions below remain open.
No release/tag is created while those conditions are unverified. The separately
requested concrete diagnostic completed PASS under explicit authority; that
one-shot scope is consumed. Seven retained general-plugin records prevent the
current resource-pass gate. Publication authority does not waive any release requirement.

No merge to `main` or final release until all applicable
mandatory checks pass for the exact candidate:

- clean identified source;
- reproducible build/package;
- final artifact hashes;
- actual loaded runtime identity;
- late registration in the same process;
- separate apply and render PASS;
- repeat/error/timeout/project-safety scenarios;
- Level 2 regression;
- no unresolved critical findings;
- documentation/evidence matching the exact candidate.

Historical Control Shell success remains useful research but is not evidence of
arbitrary ordinary-effect late registration.

## Validation handoff and platform distribution under 6.0.0

A diagnostic Validation Build has its own stated question and pre-handoff
prerequisites (candidate identity/integrity, bounded inert/refusal behavior,
reviewed safe scope, instructions/limitations and required live authority).
The intended user-validation answer can be pending after these prerequisites
pass; this does not waive a missing internal safety prerequisite. Full product
registration/apply/render acceptance remains mandatory for final Release.
This phase clarification is not approval to install/launch/read in the user's AE.

For the macOS distributable, MAC-001 requires identified final bytes, structure/
architecture/dependencies, the selected delivery channel, documented installation,
actual loaded Build ID and applicable smoke/update/uninstall/data-preservation
checks. Unsigned or locally ad-hoc-signed artifacts may qualify after those
checks. Paid accounts, distribution certificates and remote signing/notarization
services are not prerequisites. Local signing stays in the current reviewed
build profile; its result does not prove host loading. Do not promise warning-free
installation or alter general system security/quarantine automatically.

WIN-001 is outside the current Mac-only native research scope. A future Windows
scope must separately establish package/architecture/dependency/install/AE-load
evidence; successful macOS CI creates no Windows compatibility claim.
