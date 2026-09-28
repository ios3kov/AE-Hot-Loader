# AE Hot Loader — current development status

Updated: 2026-09-28. Branch: `research/ordinary-plugin-discovery`.
The branch head identifies development; tested artifacts have their own exact
source, Build ID, hashes and evidence.

## Current diagnostic work

Added a minimal existing-host collector to unblock real AE evidence without
installing another candidate. `tools/collect_ae_host.py` reads host/project
counters, checks the three exact RSMB registry identities and requests only
`get_build_identity`. It never applies effects, renders, reloads plug-ins or
issues quit/restart commands. Existing bridge state is preserved.

Local checks: 61 Python tests (23 new preflight tests, including nine emitted
JSX host-mock scenarios) and 51 panel tests passed. The collector itself ran
on Linux and correctly returned BLOCKED rather than claiming an AE result.
Fresh CI for the resulting commit is not yet reviewed at authoring.

This is a minimal environment-data request under DEVELOPMENT_RULES, not an
AE Hot Loader product candidate. Real Apple Events/AE behavior is unverified;
cold-start, apply/render and late registration remain NOT RUN for this tool.
[Scope, safety and evidence](ITERATION_AE_HOST_PREFLIGHT_2026-09-28.md).

## Last verified product package

Source: `04fea7060c7ef7ebc4a315b5c39364850287e294`.
Build ID: `native-36483421984-1`.
Full macOS build #243 (run 36483421984) and research #9 (run 36483422020) passed.
[Complete evidence and hashes](CI_CHECKPOINT_04fea70.md).

The collector compares against this immutable reference package, not an
unspecified latest branch build. It does not replace any installed component.
No installable candidate has been handed over or approved for release.
No user installation or change to `main` occurred.

## Product behavior

The panel has a **Diagnostics** button. Each **Reload Plugins** first requests
`get_build_identity`, then compares the resident Agent's Build ID, full commit,
clean state, platform and version against generated panel metadata. Missing
identity, an older/different build or failed diagnostics blocks scan dispatch.
Diagnostics alone does not scan plug-ins or read/change the project or registry.
The matching scan reply is rechecked before reporting registry changes.

The panel is generated during packaging from clean Git source with the same
Build ID as the Agent. The unstamped repository JSX intentionally cannot scan.
Pending bridge requests are preserved, temporary files are request-specific,
response parsing is bounded and timer callbacks are tied to a request ID.
These guards do not establish cross-process IPC ownership or cancel native work.

All four full-package Cargo builds use `--locked`. The CI tests the exact
generated panel and reads both getters from the exact Agent extracted from the
final ZIP. Their metadata and hashes match the package manifest. This preflight
iteration does not change the panel, Agent, loader, private ABI or render code.

## Reference package verification matrix

| Check | Result | Scope |
|---|---|---|
| Panel regression | PASS: 51/51 | Host/file mocks; also exact generated ZIP payload |
| Python regression | PASS: 38/38 | Reference package generator/identity/manifest tests |
| Full build / signing / packaging | PASS | macOS arm64, ad-hoc signing, not release approval |
| Existing native shell gates | PASS: 7/7 | Standalone synthetic scenarios, not AE/MFR rendering |
| Exact packaged Agent identity/path getters | PASS | Standalone macOS process, not in AE |
| Independent downloaded package verification | PASS | All 24 payload files and ZIP/manifest hashes |
| Real ScriptUI / resident Agent roundtrip | BLOCKED | No accessible isolated AE runtime in this session |
| RSMB controlled cold-start / apply / render | NOT RUN | Historical late-registration FAIL unchanged |
| Complete adapter-specific cleanup | NOT RUN | Historical research and generic shell remain |

The reference CI log contains a reviewed redundant Rust-action-input warning;
the pinned compiler version is correct. No warning-free or full production
readiness claim is made.

## Next gates

Collect the read-only preflight from the actual Mac. Then validate Diagnostics
and Reload in an owned AE 25.6.0 arm64 test environment, including an
intentionally mismatched Agent and project-safety checks. Establish the
controlled RSMB startup/apply/render baseline, then isolate the missing legacy
late-registration step. Complete remaining component identities, IPC
ownership/reopen/timeout checks, scope and CI cleanup before product handoff.

Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md). Historical AE results remain
historical; do not call unverified private teardown/reinitialization functions
or turn mock tests into live-AE evidence.
