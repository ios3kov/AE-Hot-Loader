# AE Hot Loader — current development and release plan

Updated: 2026-10-02. Branch: `research/ordinary-plugin-discovery`.

Source of current verified state: [DEVELOPMENT_STATUS](DEVELOPMENT_STATUS.md).
Accepted standard: **6.0.0**, `v6.0.0` peeled to
`bb8b769404ddd5b97462812a4e6b430e8bfefe13`, adopted on 2026-10-02.
Canonical [AI_ENTRYPOINT](https://github.com/ios3kov/AE-Development-Rules/blob/bb8b769404ddd5b97462812a4e6b430e8bfefe13/AI_ENTRYPOINT.md)
and its selected AE Development Rules modules, plus `AGENTS.md`, apply.
Historical plans/evidence remain preserved and must not
be treated as current approval.
Migration scope/evidence: [rules adoption](RULES_ADOPTION_6_0_0_2026-10-02.md).

## Product scope

AE Hot Loader is a **tool/panel**, not an ordinary effect plug-in. Native AEGP
modules are internal helpers when code must execute inside After Effects.

Primary Stage C goal:

> make an ordinary effect that is absent from the running AE registry become
> registered in that same identified process, then prove apply and render
> separately without restarting AE.

Loaded binaries, registry publication, application and rendering are separate
claims.

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
