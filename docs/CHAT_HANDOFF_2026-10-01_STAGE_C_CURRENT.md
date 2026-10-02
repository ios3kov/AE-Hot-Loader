# AE Hot Loader — current Stage C handoff, updated 2026-10-02

Continue the existing work. Do not restart research or repeat the unchanged
ordinary plug-in scan.

Current continuation: [live diagnostic PASS](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md),
[rules adoption](RULES_ADOPTION_6_2_0_2026-10-02.md),
[supervisor deadline review](C1_SUPERVISOR_DEADLINE_REVIEW_2026-10-02.md) and
[prepared native candidate](C1_OBSERVER_CANDIDATE_REVIEW_2026-10-01.md).
The current C1 section and next-gate order below supersede historical no-scan
preparation/permission statements in this handoff. C0 is closed; do not repeat it.
The earlier `CHAT_HANDOFF_2026-10-01.md` is a historical checkpoint.

## Exact starting point

- Repository: `ios3kov/AE-Hot-Loader`.
- Branch: `research/ordinary-plugin-discovery`; never change `main`.
- Latest retained identity capture/code/test head: **eb559edac5d9bf5d3861d5673d9df47e9de1f5e8**.
- Prior retained-record decoder/code/test head: **15c528f6d7dabad83e7203970fc8a09bb2b7e710**.
- Prior MEE ownership collector/code/test head: **095a219253bf86bea82fa06fc00ac6c87e6f0b05**.
- Prior PIN collector/code/test head: **c01fb89d7b1842a145bb7c66681a045fa6b12a82**.
- Reviewed external supervisor code/test head:
  **`f4f84aa5a41fd86cc76ee2d702fe61e9b61d16e2`** (external supervisors).
- Prepared native candidate source:
  **`7c983c5b5adfde0300f2370e5772ed757ab6b613`**; native bytes unchanged.
- Current canonical AE Development Rules source:
  **6.2.0 / `d966078a9e45fee7ec9ad14f211a9da753d64b8a`**; read pinned AI_ENTRYPOINT first.
- Historical Stage C no-scan core head:
  **`c1e20e4ab4d4a4f6654f67df7dbb224f0790b5be`**.
- Historical live-launcher code/test head:
  **`3852192406da5af539b9100114393584642e9197`**.
- Status documentation before this migration:
  `c8c56fa`.
- Historical shared DEVELOPMENT_RULES blob:
  `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
- Stage: **C of A–D**. Ordinary-effect late registration is still NOT fixed.

AE Hot Loader is a **tool/panel**. The research-only AEGP is an internal helper
used because code must execute inside After Effects; it is not the ordinary
effect being loaded.

## Preserved live results

| Gate | Result |
|---|---|
| Scoped embedded late registration | **FAIL**: source `45de0c9`, Build ID `scoped-0b8c8f122e80`; 785 unchanged effect identities |
| RSMB startup-registered apply/render | **PASS**, separate startup baseline |
| RSMB late registration | **FAIL**, separate historical result |
| First live no-scan folder lifecycle | **FAIL** at strict postflight image equality; preserved separately |
| Second live no-scan folder lifecycle | **PASS**: source `182d058`, build `noscan-8f9cb9fea71c` |
| Ordinary-effect late registration | **NOT RUN again**; historical FAIL unchanged |

Do not merge these results or relabel startup success as late-registration
success.

## What is now connected

The separate inert-by-default no-scan AEGP and external one-shot supervisor are
connected in source.

The first live operation contains **no plug-in scan and no registration**. It is
limited to:

1. exact fresh AE/process/project/module baseline;
2. one fresh owned/private ASCII directory;
3. create one FILE directory specification;
4. exact path roundtrip;
5. release it exactly once;
6. prove unchanged PID/start/project/registry/image set;
7. preserve one report ZIP.

The AEGP is inert unless its exact build/run/token/paths match. The supervisor
publishes at most one request and never automatically retries an uncertain
native outcome.

## Latest hardening

The process identity is now genuinely cross-bound between the external
supervisor and the AEGP:

- supervisor uses macOS `proc_pidinfo(PROC_PIDTBSDINFO)`;
- AEGP uses the same native `pbi_start_tvsec.pbi_start_tvusec` tuple;
- mismatch is refused before request publication;
- the native journal must retain that same start identity.

The final report ZIP is now self-checked against its archived hash manifest and
the supervisor prints the final ZIP SHA-256.

Exact-head CI for `c1e20e4`:

- research CI **`36854509313`** — PASS, Linux + macOS;
- full macOS CI **`36854509275`** — PASS.

The macOS workflow now watches `experiments/**`, so future Stage C experiment
changes trigger the full macOS regression.

These are offline/build results, not live Adobe evidence.

## Static-audit candidate closeout

The five previously recorded scanner candidates were revisited:

- unpinned checkout — fixed;
- floating Rust toolchain — fixed;
- unpinned upload-artifact — fixed;
- checkout credential persistence — fixed;
- `artifact_manifest.py` rate-limit candidate — retained as the previously
  confirmed local-argparse false positive.

All current workflow `uses:` entries are SHA-pinned and all checkout steps use
`persist-credentials: false`.

Known candidates are resolved/classified. A **new full static-security audit is
still NOT RUN**. See `STATIC_AUDIT_CLOSEOUT_2026-10-01.md`.

## Current documentation

- `README.md` now describes the product correctly as a tool with internal AEGP
  helpers.
- `PRODUCTION_PLAN.md` now reflects the actual Stage C sequence.
- `DEVELOPMENT_STATUS.md` is the source of current verified state.
- Historical dated documents remain evidence for their own commits and must not
  be rewritten as current results.


## One-shot Mac launcher

`RUN_LIVE_NO_SCAN_GATE.command` is now the only intended entrypoint for the
first live gate. Exact-head research CI `36855482114` and full macOS CI
`36855482175` are PASS for launcher head `3852192`.

The launcher refuses an already-running AE session, preserves dirty/local Git
work, installs only its unique helper, launches AE once with the one-shot token
and publishes exactly one authorized no-scan request. It does not invoke the old
scan path.

The user explicitly authorized this one gate in the current chat: helper
installation / one AE launch if required, private FILE call and provider-reference
retention. That approval is scoped only to the folder create → path roundtrip →
single release gate and does not extend to later plug-in registration.

## First live no-scan attempt

The first authorized live request is now consumed.

Preserved result:

- source `161b180714a734baf71f8c8cb58440e73f8dcd23`;
- build `noscan-f0aa4a3bd54a`;
- report SHA-256
  `727a65d7ba64be8371c40025a4fc2196785216cc77299941d0978a71eb0cff5a`;
- final status **FAIL**, stage `postflight`;
- effect registry stayed 785;
- PID/start/project revision stayed unchanged;
- only new runtime image was Apple
  `SafariPlatformSupport.framework` under `/System/Library/`.

The old format lacked durable native lifecycle counters before postflight, so
the FILE roundtrip itself is not promoted to PASS.

Remediation code head:
**`dadd884b4758a351fbc725969ed49d2f9a912781`**.

Exact-head CI:

- research `36857286317` — PASS;
- full macOS `36857286194` — PASS.

The new gate persists `native.txt` before postflight and tolerates only new
`/System/Library/` images while requiring all pre-existing images to remain
exact. New Adobe/user/plug-in images still fail.

A second live no-scan request requires fresh authorization. General
"continue" instructions do not authorize that retry.


## Second live no-scan attempt — PASS

The second authorized no-scan request closed Stage C0.

- source: `182d058254203236414602acdd9901b8749d89cc`;
- build: `noscan-8f9cb9fea71c`;
- run: `directory-probe-d097765fede949f5b9958b2897687df2`;
- report SHA-256:
  `f767e891359a3e73dc41eefe4124fe63dc0cf4dde123c2d7efa7444cd35bc62a`;
- final status: **PASS**;
- native counts: strings 2/2, spec 1/1, retained refs 3;
- registry: 785 before/after;
- runtime images: 1402 before/after;
- project revision: 1 before/after;
- plug-in scan requested: false.

The uploaded ZIP and all inner hashes were independently verified.

**Stage C0 = PASS.** Do not repeat the no-scan run.

Next work is Stage C1 offline review/preparation of the single-root
resource-registration experiment. Any live resource-registration/private PLUG
operation needs fresh authorization; the second no-scan approval is consumed.


## Previous Stage C1 ABI checkpoint

The collector's incompatible LLDB `--force` option is fixed and regression-tested
on an owned arm64 bundle. Complete bounded ABI windows and a supplemental
cleanup window were collected from the hash-pinned actual files without Adobe
execution. Clean-head local regression passed: 264 Python, 62 Node, 22 stages.
Exact-head research CI `36920890724` and full macOS CI `36920890645` are PASS
for `5b88779`. These are offline/build results, not live C1 execution.

PLUG_Search invokes the selected sack's installed cleanup list even for one
root and even with null progress callback. Review the actual cleanup registrations
and retained-state effects before creating a native resource-call backend.
An address/signature match does not prove late-call safety.

## Previous Stage C1 cleanup checkpoint

Code bf8a2cc adds a separate `--review cleanup` collection: eight complete
windows / 1390 decoded instructions, matching PLUG/FLT/MEE before/after hashes,
no Adobe execution. Default search mode also passed again (472 instructions).
Local clean-source regression: PASS, 266 Python tests without skips, 62 Node
tests, 22 stages. Exact-code research CI 36922542782 and full macOS CI
36922542905 are PASS; the latter includes build/sign/package/synthetic smoke,
not live AE execution.

FLT registers no cleanup in its normal birth call. MEE registers
PluginCleanupFunc; its body traverses shared GeneralPlugin state and can prepare
procedures, invoke saved entrypoints and mutate records beyond the search root.
Installed cleanup loops stop on nonzero returns. The running sack/vector and
repeated preparation behavior remain unobserved. No native C1 candidate is ready.

Continue with PLUG_PrepRoutine's repeated-preparation/error contract and the
general-plugin lifecycle, then establish a read-only baseline design for actual
callback/state eligibility. Do not replay SetupGeneralPluginScan, invoke
SetdownGeneralPlugins, replace cleanup or forge a sack. C0 remains the recorded
live PASS; C1 registration/apply/render are NOT RUN.

## Previous Stage C1 lifecycle/cleanup-state checkpoint

Code 3e67046 adds bounded lifecycle code/data collection (891 instructions,
96-byte vtable, confirmed fixup format) and a conservative cleanup-state gate.
Current code/test head 52f4f80 additionally fixes a reproduced macOS runner
signal/exit race. Clean current-source local tests: PASS, 270 Python without
skips, 62 Node, 22 stages. Exact research CI 36925153427 is PASS; full macOS CI
36925153460 is PASS (build/sign/package and synthetic smoke, no AE). The old 3e67046 macOS research run remains FAIL.

KeepLoaded + already-prepared can return zero and let MEE call the saved
operation-3 entrypoint again. Repeat safety remains UNKNOWN. The policy requires
complete observed cleanup state with an exactly approved inventory digest and
zero retained general-plugin records, checked again before and after the call;
the journal retains those fields. Synthetic 82 gate / 32 journal cases are
included within the Python count. There is no real state reader or C1 backend.

LIST.dylib's two bounded getter bodies were inspected without calling them.
Its new static hash is not a live-profile/resident identity. Continue only
independent read-only observer preparation, with provider and memory-consistency
bounds. Actual callback/vector state and third-party repeat behavior block
native integration. Do not attach/call without a concrete reviewed scoped
authorization, or replay setup/setdown/unprep to change the baseline.
C0 remains its recorded PASS; C1 registration/apply/render remain NOT RUN.

## Previous Stage C1 bounded snapshot checkpoint

Code 6a758a8 adds an isolated CleanupSnapshot sampler, 44 nested cases and an
owned macOS self-read. It compares two complete chains inside supplied bounds,
refuses invalid/changed/truncated state without retries, preserves callback
order/duplicates and retained count. It never calls callbacks/getters or supplies
complete/observed/digest fields to the resource policy. Provider identity,
allocation provenance, quiescence and actual state remain unknown.

Clean-source local regression: PASS, 271 Python (no skips), 62 Node, 22 stages.
Owned address/undefined-behavior sanitizer run: PASS. Exact research CI
36926349585 is PASS; full macOS CI 36926349591 is PASS. All are offline/build
evidence. C0 remains recorded PASS; C1 registration/apply/render remain NOT RUN.
Continue independent file-only provider/root/range preparation. A matching
snapshot cannot authorize native integration or prove a complete eligible state.

## Previous Stage C1 root provenance checkpoint

Code efe05f2 independently verifies static Mach-O symbol/UUID/zero-fill roots:
PLUG global slot 0x18490 points to a handle; only that separately validated handle
is CleanupSnapshot's sack_slot. MEE vector pair is 0x10fd70. Neither serialized
zero-fill bytes nor static VM values are runtime observations. Complete allocation/
lifetime/quiescence and all callback effects remain unknown. No scope/backend
conversion or host read/call is bound.

Clean local regression: PASS, 284 Python (no skips), 62 Node, 22 stages. Exact
research CI 36927550112 PASS; macOS product CI 36927550048 PASS. Collection
and regression ZIPs independently rehashed; see current report. C1 registration/
apply/render NOT RUN; C0 remains recorded PASS. Continue owned-fixture resident
module/header/text identity and data-root containment checks, then prepare a
concrete diagnostic candidate. The user's newest instruction requests autonomous
continuation through all development stages; report each stage and continue,
preserving the established live/private-call/release boundaries.

## Current Stage C1 resident root checkpoint

Code 0c4cd4c prepares exact resident header/text/path/hash binding and zero-fill
root extent checks. Owned-library tests prove the actual address/data read and
absence/hash/UUID/section/range/thread refusals. Binder never loads a provider or
calls an anchor. This is point-in-time address identity, not lifetime/completeness.

Clean local regression PASS: 287 Python (no skips), 62 Node, 22 stages. Exact
research CI 36928329962 and macOS product CI 36928330044 PASS. No AE roots/
callbacks/vector read. C1 registration/apply/render NOT RUN, C0 recorded PASS.
Continue current-process mapped-range reads with verified Mach API and owned
allocation/guard-page tests, then prepare a concrete diagnostic observer. Do not
promote mapping metadata or matching captures to allocation/complete eligibility.
Continue autonomously as explicitly requested; preserve live authority boundaries.

## Current Stage C1 mapped reader checkpoint

Code 6c666ca: exact self-process copies with mapping/protection/range checks
before/after, fixed budgets and refusal after failure. 29 nested synthetic cases,
owned-page/guard/boundary/thread checks and ASan/UBSan PASS. Full clean local
288 Python (no skips), 62 Node, 22 stages; research CI 36929256787 and full macOS
CI 36929256802 PASS. ZIP/inventory reverified in current report.
Next bounded diagnostic observer composition on owned chains, then an exact
inert candidate with external supervision before scoped live authorization.
No AE roots read, provider retained or native resource pass invoked. Mapping
identity/byte equality is not complete cleanup, allocator ownership or eligibility.
Continue autonomously with stage statuses; C1 registration/apply/render NOT RUN.

## Current Stage C1 observer checkpoint

Code 1a4201c composes a consumed-on-attempt diagnostic bootstrap/capture with
exact resident identities and clipped mapped reads. Bootstrap/capture/global/
record mapping changes refuse; nonzero records remain diagnostics, never gate
eligibility. Synthetic 27 cases and actual owned two-provider chain + sanitizers
PASS. Full clean local 290 Python/no skips, 62 Node, 22 stages and both exact
CI 36929802910/36929802970 PASS. Private ZIP manifest/inventory verified.
Next separate inert diagnostic AEGP, one-shot journal/supervisor and exact SDK
build/sign/hash/inert checks before scoped live operation. No real AE root read,
callback invocation, retained provider or native registration backend. Preserve
NOT OBSERVED/NOT RUN for current live registration/apply/render; C0 remains PASS.
Continue independent work without milestone stops as explicitly requested.

## Current accepted rules — 6.0.0 migration

On 2026-10-02 the user explicitly accepted the proposed rules migration.
Current baseline: 6.0.0 / published v6.0.0, peeled commit
bb8b769404ddd5b97462812a4e6b430e8bfefe13. Tag/version/source, applicability map
and routing contexts verified; full available standard self-test PASS, 132 files,
43 executed test cases, two Windows-only skipped; PowerShell NOT RUN locally.
AGENTS/plan/status/README now identify the pinned source and v6 MAC-001 integrity/
install/host-load policy, without paid-account/certificate/service prerequisites.
Validation phases and applicable IPC/diagnostics/testing overlays are explicit.
No vendored legacy wrapper callers; no runtime/tooling byte change required.
See RULES_ADOPTION_6_0_0_2026-10-02.md; final documentation consistency, pinned
source and 25 local-link checks PASS. Documentation/policy migration complete.

Older b27f454 records remain historical. No new artifact, AE action, permission,
registration evidence, main change or product release is produced by adoption.
Next C1 step retains the concrete diagnostic authority and runtime-safety gates.
Preserve the user's existing final-publication authorization when release gates
eventually pass; the baseline record itself grants no live permission.

## Stage C1 supervisor deadline checkpoint

Code/test source f4f84aa5a41fd86cc76ee2d702fe61e9b61d16e2, accepted rules b27f454.
Four synthetic reproductions proved the same two expiry bugs in the diagnostic
and no-scan supervisors. Both now check the absolute monotonic deadline just
before publication and before PASS acceptance. Expiry preserves the consumed
attempt/journal/report, without retry or host stop. Historical C0 is not rerun.
27 focused supervisor tests and clean full local 302 Python/no skips, 62 Node,
22 stages PASS. ZIP dd7e0777ea95999857bce874050fb9cc02725fb7fe80dbd617fc20d265e264ca
and complete archived inventory/payloads verified; exact-source research CI
37024297435 and full macOS CI 37024297373 both completed/success (PASS) at
the exact full source SHA above. Bounded scanner completed
(266 supported/no omissions), sole known local argparse false-positive/raw exit 1.
See C1_SUPERVISOR_DEADLINE_REVIEW_2026-10-02.md for identities and limitations.

No native source or candidate-byte change. Earlier native artifact source 7c983c5
does not identify the updated external supervisor; pin both identities before a
future authorized combined live run. No installation, launch, request or AE root
read occurred. Concrete diagnostic scope remains pending; the previous automatic
review rejection is not bypassed. Dependent registration/backend/apply/render
remain NOT READY/NOT RUN; exact complete-state/lifetime/repeat questions remain
open. Preserve publication authorization after release gates pass. This offline
block is closed. Next is the separately approved one-shot diagnostic with fresh
safe runtime and exact independent supervisor/native-candidate identities.

## Prepared Stage C1 diagnostic candidate checkpoint

Latest direction 2026-10-02: user explicitly requests release publication
("релиз делай"). Preserve this authorization for the finished verified release;
do not repeat the publication-permission question. Mandatory project release
gates are still open; no release/tag/merge/main change. The concrete diagnostic
install/one AE launch/sensitive-read approval remains pending and is not inferred
from publication scope to bypass the earlier automatic-review rejection.

Continuation 2026-10-02: clean head 5a74fd8, unchanged candidate/code source
7c983c5. Offline code-profile scan v2.0.0 completed at
2026-10-02T08:54:03.224551+00:00: 265 supported files/no omissions, four workflows;
raw exit 1/review_required, sole known local argparse false-positive at
tools/artifact_manifest.py:71 re-reviewed. Private report SHA-256
b16f7d24decb13af96a6f20e2804766f5abeab91e9be6770ab78cb7f5b802aa8.
This is bounded source scanning, not full security/AE/release evidence. No new
behavior, candidate or live operation. Explicit exact diagnostic approval was
requested again with the concrete install/one launch/read-only scope; pending.
The latest generic continuation is not used to bypass the prior automatic-review
rejection. Next dependent step remains that one diagnostic after actual approval
and fresh runtime verification. Do not repeat C0 or an unchanged registration scan.

Code 7c983c5: separate inert AEGP, one-shot durable journal and independent
supervisor. Clean local 298 Python/no skips, 62 Node, 22 stages and both exact
CI 36931094055/36931094195 PASS. Real SDK build/sign/hash/inert candidate
observe-d548b007e316 PASS; binary SHA cfbfa87038d2640a558ca0e30ca5c5d8b171aef8d8be4934f5c25f281950be56,
private manifest SHA 9f305a648b43a6569ccb70165169c2ed021d7977ddfbd9b84f3725d0bbdff100.
Inventory/payloads rehashed. Token stays private. See exact candidate report.

Live install/one test launch/sensitive read was rejected BEFORE execution by
automatic approval review: no explicit authority for those concrete actions.
No install/launch/request/read/private call/retention occurred; no workaround.
Next obtain explicit approval for only this unique helper and one read-only
capture on a fresh blank clean idle test host; preserve existing sessions and
all state on uncertainty. Fresh authorization must come from the user, not this
checkpoint. Generic autonomous-development request was not accepted by review.
Independent work is complete for this diagnostic preparation; dependent native
registration remains blocked by critical complete-state/lifetime/repeat unknowns.
No diagnostic → ResourcePassGate eligibility conversion; C1 registration/apply/
render NOT RUN, C0 recorded PASS. Do not repeat consumed C0 or old registration scan.

## Latest C1 diagnostic authorization and environment refusal

The user explicitly replied «разрешаю» to the exact observe-d548b007e316
install / one launch only without an existing AE session / one read-only capture
scope. This supersedes the earlier missing-authority statements for that scope.
Tool review permitted execution. The orchestrator passed exact clean source,
candidate/signature/provider and unused evidence checks, then refused an
existing AE session (PID 84352) before any live side effect. No installation,
launch, request, sensitive read or retry; destination absent, control/journal
empty, native request unconsumed. Existing project/session preserved, not inspected.

Current result **BLOCKED on safe environment**. Wait for the user to save and
close AE normally and explicitly resume; do not terminate AE or retry
on a timer. Recheck the exact unused candidate and safe baseline on resumption.
Diagnostic permission is already granted; do not ask for it again. Private calls,
provider retention and registration are outside this permission. See
[full scoped evidence](C1_DIAGNOSTIC_PREFLIGHT_BLOCKED_2026-10-02.md).
Registration/apply/render and release gates remain open; C0 is not repeated.

## Latest C1 live diagnostic — PASS, resource baseline ineligible

User closed AE and confirmed full exit. Exact candidate observe-d548b007e316
(native source 7c983c5) installed/launched once under explicit authority, using
reviewed supervisor f4f84aa, clean execution HEAD b3a8536. One read-only request
PASS; authority consumed. ZIP SHA
54976e137d928861a5cffd8288e4dccc10a3b347f95b766dab89f297554b16f4;
independent archive/native-evidence verification PASS. Two callbacks, seven
retained general-plugin records, unchanged blank/clean/idle project, PID/start,
785 effects and resident images. No private call/retention/retry/shutdown.
AE/consumed helper preserved. Earlier environment blocker is superseded.

Current ResourcePassGate cannot accept this baseline (requires zero records plus
complete reviewed cleanup). File-only callback attribution: MEE PluginCleanupFunc;
PINp_CleanupFunc tail-branches into PINp_SortModules (host global sorting).
Runtime PIN UUID/content and full lifetime/quiescence remain unresolved.
Next bounded file-only PIN review and retained-state contract; no gate weakening,
setdown/startup replay, callback replacement or additional live capture under
consumed authority. See [full evidence](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md).
Registration/apply/render/release still open; C0 unchanged PASS.

## C1 PIN file collector — exact local PASS

Reproducible exact-file collector/source c01fb89 completed PASS: 58 instructions,
11 structural anchors. Full clean local regression PASS: 307 Python/no skips,
62 Node, 22 stages. Report inventories/hashes independently verified; bounded
static scan retains sole known local-argparse false-positive. Research CI
37036763724 and full macOS 37036763790 both exact-source PASS. No native profile/helper change
or further live operation. Seven-record blocker unchanged. Next retained-state/
lifetime and PIN comparator/synchronization review. See
[bounded PIN review](C1_PIN_CLEANUP_REVIEW_2026-10-02.md).

## C1 retained identity journal — focused owned-evidence PASS

A bounded journal now saves completed raw copy frames from both captures. A
separate Python verifier reconstructs names/read order and refuses incomplete,
inconsistent or wrong-run evidence. Focused journal suite PASS: 11 Python tests,
17 nested C++ journal cases. Native helper/profile, copied-byte/read budgets and
ResourcePassGate unchanged; actual AE names still NOT RUN. Full clean regression,
static review and exact-source CI pending. Next separate host transaction/
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

## Next gate — exact order

1. Review root/provider identity, memory-range provenance and host lifetime/
   quiescence; prove complete callback/state observation without host getters.
2. Review end-of-pass effects and borrowed/retained state; freeze the complete
   single-root native contract without replacing callbacks or replaying startup.
3. Connect the research-only inert C1 backend/AEGP and independent one-shot
   supervisor; verify refusal/replay/timeout/journal paths offline.
4. Build/sign/hash/inert-test one exact clean candidate and fresh owned fixture.
5. Obtain separately scoped authorization for that candidate's installation,
   any AE launch, provider retention and the one private resource pass.
6. Establish a fresh exact running host/project/resident-module baseline, then
   publish at most one request. Stop and preserve evidence on uncertainty.
7. Require exact registry insertion in the same process; prove apply/render
   separately only after registration PASS.

C0 is already PASS and must not be repeated as a substitute for this work.

## After no-scan PASS

Only then:

1. review PLUG end-of-pass callbacks and retained state;
2. prepare one fresh embedded ordinary-effect fixture;
3. run one bounded resource-registration experiment;
4. require an exact new match name in the same AE process;
5. prove apply and render separately.

Do not replay startup lifecycle functions, enumerate global roots, bypass cache
predicates, replace callbacks, clear caches, force notification, unload provider
code or repeat the old unchanged ML scan.

## Permissions and stop conditions

The earlier installation/one-restart permission is consumed.

General instructions to continue do **not** authorize:

- a new install or AE launch/restart;
- a private FILE/PLUG host call;
- provider-reference retention;
- debugger attachment;
- process termination;
- project/preferences/third-party plug-in mutation.

No `main` change, merge or release. Never delete preferences, projects or
third-party plug-ins.

A timeout or uncertain native outcome preserves evidence and stops; it is not
permission to retry.

## Current limitation

The original `/Users/os3kov/Documents/AE-Hot-Loader/` checkout was read clean at
`182d058`; it was preserved. Development uses a separate working clone, initially
synchronized to remote `9c142ed` and advanced to the C1 code head above.
The current AE process list could not be read in the sandbox; running project
and resident-module baseline remain NOT OBSERVED. No live C1 operation, helper
installation, launch or project mutation was performed. The earlier C0 live
PASS remains identified historical evidence, not today's host observation.
