# AE Hot Loader — current development status

Updated: 2026-09-28. Working branch: `research/ordinary-plugin-discovery`.
The Git branch head is the source of truth for the latest documentation.

## Development versus verified checkpoint

- Panel implementation commit: `721794e2601f134018b04ccceeeb531cb72cb4a8`.
- Latest checked code/CI configuration: `f274961b14c28696b96e151d335924c76162f9c6`.
- Verified run: [36472758795 / attempt 1](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36472758795).
- This status is added by a documentation-only successor. It does not change
  the tested panel, Agent, native loader, tests or CI configuration.
- New installable artifact: none distributed. Release approval: NOT GRANTED.
- `main` was not changed by this iteration.

The previous [dated status](DEVELOPMENT_STATUS_2026-09-28.md) is a preserved
historical snapshot, not the current head status.

## Implemented now

The panel copies `app.effects` match names before a request and after its
matching response. It reports observed additions/removals, unchanged registry
or errors. Loaded module counts no longer substitute for the panel's registry
check. Apply/render is explicitly unverified by that check.

Added protocol validation, duplicate-field rejection, pending-click guard,
file-close cleanup, failed-write protection and UI recovery for the tested
error paths. Timeout means unknown result; it does not cancel a native scan.
The Agent protocol and native loader were not changed. Direct bridge consumers
still must verify registration separately from the Agent's `success` status.

Research pushes now run automated panel regression and macOS syntax checks.
CI action SHAs and test Node are pinned, with read-only repository permissions
and no persisted checkout credentials. The first run's action-deprecation
warnings were investigated and absent from the reviewed replacement run.

README, production plan and audit entry point now distinguish current source
from historical shell/adapter claims. Original documents were retained with
identical Git blobs under `docs/archive/`.

## Verification matrix

| Check | Status | Evidence / limit |
|---|---|---|
| Updated JSX host-mock regression | PASS: 22/22 | Actual JSX under Node; not ExtendScript/AE |
| arm64 C++ syntax, warnings as errors | PASS | macOS job, not native linking/runtime |
| Root command script zsh parsing | PASS | Syntax only; scripts not installed/executed |
| CI source identities and report upload | PASS | Commit/run/hash evidence retained |
| New panel in real AE | BLOCKED | No accessible AE runtime in this development session |
| Full native build/sign/package on current research source | NOT RUN | Existing historical build is not this gate |
| RSMB controlled cold-start/apply/render | NOT RUN | Historical late-registration FAIL unchanged |
| Full adapter-specific reference/fixture cleanup | NOT RUN | Current-scope documentation corrected only |
| Production release / install / merge | NOT RUN | No new candidate approved or distributed |

Historical modern-probe and generic Control Shell results remain as recorded
in the dated status. They are not new tests of the current source.
Detailed identities: [CI_CHECKPOINT_f274961](CI_CHECKPOINT_f274961.md).

## Remaining work

Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md): complete scoped cleanup and full
native checks; establish controlled RSMB startup/apply/render evidence; isolate
legacy late registration; run real panel/Agent, repeat/timeout/ownership and
project-safety gates. Do not call unsafe private teardown/reinit functions or
turn an unavailable AE test into a mock-test PASS.
