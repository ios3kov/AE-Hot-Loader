# AE Hot Loader — current development status

Updated: 2026-09-28. Branch: `research/ordinary-plugin-discovery`.
The branch head identifies development; tested artifacts have their own exact
source, Build ID, hashes and evidence.

## Latest verified implementation

Source: `04fea7060c7ef7ebc4a315b5c39364850287e294`.
Build ID: `native-36483421984-1`.
Full macOS build #243 (run 36483421984) and research #9 (run 36483422020) passed.
[Complete evidence and hashes](CI_CHECKPOINT_04fea70.md).

This status is a Markdown-only successor. The retained package belongs to
`04fea70`, not this document's commit. No installable candidate has been handed
over or approved for release. No user installation or change to `main` occurred.

## Implemented now

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

All four full-package Cargo builds now use `--locked`. The CI tests the exact
generated panel and reads both getters from the exact Agent extracted from the
final ZIP. Their metadata and hashes match the package manifest. Agent/native
loader code, private ABI, Control Shell and rendering code are unchanged.

## Verification matrix

| Check | Result | Scope |
|---|---|---|
| Panel regression | PASS: 51/51 | Host/file mocks; also run against exact generated ZIP payload |
| Python regression | PASS: 38/38 | Generator, identity and manifest tests |
| Full build / signing / packaging | PASS | macOS arm64, ad-hoc signing, not release approval |
| Existing native shell gates | PASS: 7/7 | Standalone synthetic scenarios, not AE/MFR rendering |
| Exact packaged Agent identity/path getters | PASS | 16 calls in standalone macOS process, not in AE |
| Independent downloaded package verification | PASS | All 24 payload files, outer/inner ZIP and manifest hashes |
| Real ScriptUI / resident Agent roundtrip | BLOCKED | No accessible isolated AE runtime in this session |
| RSMB controlled cold-start / apply / render | NOT RUN | Historical late-registration FAIL unchanged |
| Complete adapter-specific cleanup | NOT RUN | Historical research and generic shell remain |

The CI log contains a reviewed redundant Rust-action-input warning; the pinned
compiler version is correct. Details and remaining cleanup are in the checkpoint.
No warning-free or full production-readiness claim is made.

## Next gates

Validate Diagnostics and Reload in an owned AE 25.6.0 arm64 test environment,
including an intentionally mismatched Agent and project-safety checks. Establish
the controlled RSMB startup/apply/render baseline, then isolate the missing
legacy late-registration step. Complete remaining component identities, IPC
ownership/reopen/timeout checks, scope and CI cleanup before handoff.

Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md). Historical AE results remain
historical; do not call unverified private teardown/reinitialization functions
or turn mock tests into live-AE evidence.
