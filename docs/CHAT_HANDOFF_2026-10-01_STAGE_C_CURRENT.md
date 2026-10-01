# AE Hot Loader — current Stage C handoff, 2026-10-01

Continue the existing work. Do not restart research or repeat the unchanged
ordinary plug-in scan.

The earlier `CHAT_HANDOFF_2026-10-01.md` is now a historical checkpoint. This
record supersedes its "no-scan bridge not connected" statement.

## Exact starting point

- Repository: `ios3kov/AE-Hot-Loader`.
- Branch: `research/ordinary-plugin-discovery`; never change `main`.
- Current Stage C no-scan core head:
  **`c1e20e4ab4d4a4f6654f67df7dbb224f0790b5be`**.
- Current live-launcher code/test head:
  **`3852192406da5af539b9100114393584642e9197`**.
- Current status documentation before this save:
  `e3f577ef5781731a2055365f4bef94074d3584b7`.
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
| Current live no-scan folder lifecycle | **NOT RUN** |
| Current AE/PID/project/loaded helper | **NOT OBSERVED** |

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

## Next gate — exact order

1. Reconcile the user's local checkout
   `/Users/os3kov/Documents/AE-Hot-Loader/` with the research branch **without
   discarding local changes**. The last user-reported local state was older and
   has not been re-observed here.
2. Re-observe the current AE process/project/runtime state.
3. On the authorized Mac, build the exact no-scan AEGP against the supplied
   AE 25.6 SDK; record Build ID, hashes and clean source identity.
4. Verify signing, exports and inert entry for that exact artifact.
5. Verify the intended install path is unused and the exact loaded helper
   identity can be proven.
6. Only with fresh authorization, perform any needed helper installation and
   AE launch/restart.
7. Separately require explicit approval for:
   - the private FILE call;
   - retaining three already-loaded FILE/U/dvacore references until process exit.
8. Publish exactly one request and produce exactly one ZIP report.

The live acceptance is only folder create → path roundtrip → one release.
`PLUG_Search`, ordinary-effect registration and apply/render are outside this
first run.

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

This environment cannot inspect
`/Users/os3kov/Documents/AE-Hot-Loader/` or the user's running AE process.
Therefore local checkout identity, current AE baseline, exact SDK build,
installed/loaded helper identity and the real folder-object lifecycle remain
NOT OBSERVED / NOT RUN here.
