# AE Hot Loader — current Stage C handoff, 2026-10-01

Continue the existing work. Do not restart research or repeat the unchanged
ordinary plug-in scan.

Current continuation: [C1_CLEANUP_REGISTRATION_REVIEW_2026-10-01.md](C1_CLEANUP_REGISTRATION_REVIEW_2026-10-01.md).
The current C1 section and next-gate order below supersede historical no-scan
preparation/permission statements in this handoff. C0 is closed; do not repeat it.
The earlier `CHAT_HANDOFF_2026-10-01.md` is a historical checkpoint.

## Exact starting point

- Repository: `ios3kov/AE-Hot-Loader`.
- Branch: `research/ordinary-plugin-discovery`; never change `main`.
- Current C1 code/test head:
  **`bf8a2cca9345df62e50bb69c144f9a2bbc93f34a`**.
- Current canonical AE Development Rules source:
  **`f17c056b292631a0832b894050e204a3ca7bc2dd`**; read AI_ENTRYPOINT first.
- Current Stage C no-scan core head:
  **`c1e20e4ab4d4a4f6654f67df7dbb224f0790b5be`**.
- Current live-launcher code/test head:
  **`3852192406da5af539b9100114393584642e9197`**.
- Current status documentation before this save:
  `0e455db981f2c9d32c6ed0a1bcec081f5a8d2efb`.
- Shared DEVELOPMENT_RULES blob:
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

## Current Stage C1 cleanup checkpoint

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

## Next gate — exact order

1. Identify the existing default-sack cleanup registrations and their targets.
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
