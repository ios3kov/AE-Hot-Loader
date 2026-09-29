# AE Hot Loader — current development status

Updated: 2026-09-28. Branch: `research/ordinary-plugin-discovery`.
The branch head identifies development; tested artifacts have their own exact
source, Build ID, hashes and evidence.

## RSMB apply/render gate prepared — 2026-09-29

Source d19edca adds a controlled one-frame RSMB apply/render harness. Research
run 36546959381 (#13) passed with 51/51 panel tests and 87/87 Python tests;
the macOS native-syntax job also passed. Full macOS run 36546959423 (#247)
passed all existing build/sign/package/native smoke gates.

The user's latest private preflight showed the resident Agent identity PASS,
the blank clean project baseline PASS, and RSMB registry presence PASS.
Real RSMB apply/render is still NOT RUN until the checked harness is executed
on that host. See CI_CHECKPOINT_d19edca.md and
ITERATION_RSMB_APPLY_RENDER_2026-09-29.md.
## Current diagnostic work

The requested user preflight report has been received. Its two read-only
snapshots report AE 25.6x101 and all three exact RSMB identities present.
The observed project counters are unchanged; the project was already dirty
before the probe. Resident Agent identity is BLOCKED: the collector preserved
an existing request/response and did not send a diagnostic query. Apply/render,
controlled startup and product ScriptUI roundtrip were NOT RUN.
[Evidence and exact limits](AE_HOST_PREFLIGHT_RESULT_2026-09-28.md).

Added `tools/inspect_ae_bridge.py` in `0964462a75ce2c232813567dd40779193040ede8`.
This separate passive tool identifies existing request/response records without
contacting AE, publishing requests or deleting files. Messages and raw IDs are
omitted. Stored build metadata is not proof of the resident Agent or safe
cleanup. The original collector, product code and native loader are unchanged.

Verification: 22/22 new local tests, 83/83 Python and 51/51 panel mock tests in
research CI #12 passed; macOS static/Python/panel steps also passed. The exact
handed-over standalone Python copy passed a synthetic Linux CLI test with
bridge bytes retained and no request created. User bridge execution remains
NOT RUN. [Run identities, scope and file hash](CI_CHECKPOINT_0964462.md).
The full native job #246 was still running when that diagnostic checkpoint
was authored; its package is not being handed over by this iteration.

Only the passive inspector is requested next. Do not rerun the unchanged
active preflight or clear IPC state blindly. Do not close/restart a dirty
working project. This is a minimal environment-data request, not a product
release or a substitute for real AE integration tests.

## Reference product package

Source: `04fea7060c7ef7ebc4a315b5c39364850287e294`.
Build ID: `native-36483421984-1`.
Full macOS build #243 (run 36483421984) and research #9 (run 36483422020) passed.
[Complete evidence and hashes](CI_CHECKPOINT_04fea70.md).

Both diagnostic tools compare against this immutable reference package, not
an unspecified latest branch build. They do not replace installed components.
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
final ZIP. Their metadata and hashes match the package manifest. This passive
inspection iteration changes no panel, Agent, private ABI or render code.

## Reference package verification matrix

| Check | Result | Scope |
|---|---|---|
| Panel regression | PASS: 51/51 | Host/file mocks; also exact generated ZIP payload |
| Python regression | PASS: 38/38 | Reference package generator/identity/manifest tests |
| Full build / signing / packaging | PASS | macOS arm64, ad-hoc signing, not release approval |
| Existing native shell gates | PASS: 7/7 | Standalone synthetic scenarios, not AE/MFR rendering |
| Exact packaged Agent identity/path getters | PASS | Standalone macOS process, not in AE |
| Independent downloaded package verification | PASS | All 24 payload files and ZIP/manifest hashes |
| Real ScriptUI / resident Agent roundtrip | BLOCKED | User preflight did not send the query; no isolated AE runtime in this session |
| RSMB controlled cold-start / apply / render | NOT RUN | Uploaded presence-only evidence does not change historical late-registration FAIL |
| Complete adapter-specific cleanup | NOT RUN | Historical research and generic shell remain |

The reference CI log contains a reviewed redundant Rust-action-input warning;
the pinned compiler version is correct. No warning-free or full production
readiness claim is made.

## Next gates

Inspect the preserved bridge records using the passive tool, then establish a
fresh verified resident Agent identity without risking unsaved work. Validate
Diagnostics and Reload in an owned AE 25.6.0 arm64 environment, including an
intentionally mismatched Agent and project-safety checks. Establish controlled
RSMB startup/apply/render evidence, then isolate missing legacy registration.
Complete remaining component identities, IPC ownership/reopen/timeout checks,
scope and CI cleanup before product handoff.

Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md). Historical AE results remain
historical; do not call unverified private teardown/reinitialization functions
or turn mock tests into live-AE evidence.
