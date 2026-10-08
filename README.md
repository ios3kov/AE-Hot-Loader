# AE Hot Loader

Research-stage **tool** for discovering/registering ordinary After Effects effects
without restarting AE. The user-facing product direction is a panel/tool; native
AEGP modules are internal helpers where code must run inside After Effects.

This is **not yet a universal third-party plug-in loader or a release-approved
product**.

Current verified state: [DEVELOPMENT_STATUS](docs/DEVELOPMENT_STATUS.md).  
Current gates: [PRODUCTION_PLAN](docs/PRODUCTION_PLAN.md).  
Development requirements: [AGENTS](AGENTS.md).
Accepted rules baseline: **AE Development Rules 11.0.0**, pinned source
`e8b763ad2fefd0c5d79f865f7f017ff714cf7c23`; see
[current adoption and control-render checkpoint](docs/C1_QUEUE_CONTROL_2026-10-08.md).
Earlier rules and Evidence remain historical.

## Current Stage C

The core unresolved problem is ordinary-effect late registration.

Preserved live evidence:

- scoped embedded late registration: **FAIL** — source `45de0c9`,
  Build ID `scoped-0b8c8f122e80`, 785 effect identities unchanged;
- RSMB startup-registered apply/render: **PASS**, separate startup baseline;
- RSMB late registration: **FAIL**.

A loaded image or successful native loader return is not registration evidence.
Registry presence, effect application and rendering are separate claims.

### No-scan safety gate

Before another registration experiment, the repository now contains a separate
research-only, inert-by-default AEGP plus an external one-shot supervisor.

That gate performs **no plug-in scan and no ordinary-effect registration**. Its
only intended live operation is:

1. create one newly owned directory specification;
2. roundtrip the exact path;
3. release it exactly once;
4. prove the same AE process/project/registry/image set remained unchanged;
5. preserve one report ZIP.

The no-scan Stage C0 folder-object lifecycle is **PASS** at its identified
historical source; see [live evidence](docs/NO_SCAN_DIRECTORY_LIVE_PASS_2026-10-01.md).
That consumed one-shot gate must not be repeated. Subsequent identified C1
read-only diagnostics are also historical and their one-shot scopes are consumed.
Current C1 research compares PICA, single-effect publication and a stable shell,
including possible combinations; see [hypothesis review](docs/HYPOTHESES_REVIEW_2026-10-03.md).
The identified PICA availability diagnostic completed in AE 25.6:
all four requested suite revisions are available; the complete global adapter list
contains only the standard **Sweet Pea 2 Adapter v1**. Project/effect registry and
loaded image inventories stayed unchanged. [Actual result and exact evidence](docs/PICA_AVAILABILITY_REVIEW_2026-10-03.md).
This confirms PICA access, not ordinary-effect registration. Its one-shot scope is
consumed. A separate bounded public plug-in inventory helper is now built and
locally validated at source 525000b, with 418 Python/no skips, 62 Node and 22 stages
PASS. Its live question is whether exact known ordinary-effect files occur in
PICA's global list. [Contracts, preparation receipts and conditional live scope](docs/PICA_INVENTORY_REVIEW_2026-10-03.md).
That identified inventory completed in AE: two fully resolved PICA records point
to AE.app with the standard adapter; neither known ordinary-effect file is listed,
although both matches exist in AE's registry. Project/registry/images unchanged.
This supplies no direct ordinary-effect publication bridge; the scoped one-shot
permission is consumed. [Actual inventory result](docs/PICA_INVENTORY_REVIEW_2026-10-03.md).
A safe ordinary-effect registration adapter remains BLOCKED on provider ownership,
continuous host-wide exclusion and complete publication/failure semantics.
Current-candidate late registration/apply/render are NOT RUN. Historical scope
and evidence do not authorize a different host operation.

The helper being an AEGP `.plugin` does **not** make AE Hot Loader an effect
plug-in product. It is an internal host-side component of the tool.

## Current workflow vs historical workflow

The existing ScriptUI panel/Agent ordinary-discovery path and Control Shell work
remain in the repository as research/product history. Existing install/staging
commands do **not** represent the current no-scan Stage C gate and must not be
used as substitutes for it.

The generic Control Shell historically demonstrated implementation A→B→C reload,
busy-render rejection and rollback without AE restart. That prepared-shell result
does not prove arbitrary ordinary plug-in registration.

## Development evidence

The research branch uses:

- unified Linux/macOS offline checks;
- full macOS build/sign/package regression for the existing product path;
- owned native directory/binding/journal tests;
- one-shot supervisor tests and source/runtime identity checks.

Green CI is build/offline evidence only. It does not prove a private Adobe call
or late registration inside AE.

The exact current code/CI identities and remaining gates are recorded in
[DEVELOPMENT_STATUS](docs/DEVELOPMENT_STATUS.md).

## Safety boundaries

Do not infer authorization from source flags or old test permissions.

Without a separately approved live gate, do not:

- install/restart or terminate AE;
- delete preferences, projects or third-party plug-ins;
- replay startup lifecycle functions;
- run the unchanged broad plug-in scan;
- unload Adobe providers;
- clear caches or force notifications;
- execute private FILE/PLUG calls.

`main` remains unchanged during Stage C research.

## Historical documentation

Historical reports are preserved under `docs/` and `docs/archive/`. They
describe the source and evidence at their recorded commits and must not be
relabelled as verification of the current candidate.
