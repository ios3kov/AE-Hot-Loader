# Stage C: scoped research AEGP build evidence

Plan and acceptance: [scoped discovery plan](SCOPED_DISCOVERY_PLAN_2026-09-29.md).
Rules rechecked: `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Identified artifact

- Clean source: `01aef683128b759d12afebc74aa961d32cc9f410`.
- Build ID: `scoped-0d35394a6f6a`.
- Local directory: `build-ae-hot-loader/scoped-0d35394a6f6a/`.
- Manifest SHA-256: `328077e67d9388808d0c76da9094c38559cab89944104906711ad30c66d31c6a`.
- Signed binary SHA-256: `9ca206e8f2eee72886f39d070dc486495797769ba52a94ef2ac82e117ae88e0c`.
- PiPL resource file SHA-256: `2369ff9ffcb3a50239edece874b796984a86b4e8663dadee5c99738835577ff4`.
- Pinned input fixture: `88019a1a01a7`, manifest SHA-256
  `947cf0c26296c8d78f0c4b2a28492228b96397c6b9525f17bf85616bae76d937`.
- Apple clang 21.0.0, macOS SDK 27.0, arm64, ad-hoc signing; Adobe SDK
  header identity and exact command recorded in the manifest.

Reproduce from a clean checkout using `build_scoped_discovery.py --sdk <SDK
Examples> --fixture <embedded manifest> --fixture-sha256 <verified hash>`.
Each build creates a fresh identity and owned directory, so byte-identical
reproduction is not claimed. No installation or AE launch is performed.

## Behavior and boundaries

The research module compiles the current single-folder native loader with only
its two log destinations redirected to the run's private evidence directory.
The manifest records both native-source hashes. No product source was changed.

The module activates only with its per-build token and the exact executable
path under its owned `host/` directory. A request must name its current PID
and Build ID. No request can select a path. The compiled fixture inventory
and SHA-256 values are rechecked immediately before the call; extra empty
directories, symlinks and hard links also fail. The experiment assumes a stable
test-owned directory, not protection from a hostile same-user filesystem race.

An exclusive durable claim prevents retry after success, failure or crash.
The module records its loaded image path/identity, preflight, call start,
native return, postflight and result. A crash may leave only `call-started.txt`;
that is never PASS. The read-only host snapshot requires AE 25.6x101 build 101
and an empty, unsaved, clean, non-rendering project with an empty queue. PASS
requires exactly the pinned registry addition and unchanged project revision.
Neither application nor rendering is performed.

The target host path does not yet exist. A token and copied application alone
do **not** demonstrate isolated preferences, caches, plug-in roots or IPC.
Establish that environment and a bounded external crash/timeout supervisor
before publishing any request. This build is internal evidence, not a runtime
test package for the user or a release candidate.

## Verification

| Check | Status | Scope |
| --- | --- | --- |
| SDK compile/link, signature, export allowlist | PASS | Exact built arm64 AEGP |
| Build identity getter | PASS | Exact binary loaded outside AE |
| Inert entry point | PASS | 3 native cases: null suites, wrong token, correct token/wrong host; zero suite acquisitions and no evidence writes |
| Native single-root/one-shot guards | PASS | 15 cases with mock loader; changed files, extra entries, links, PID/token/host mismatch, unsafe baseline, delta/revision failures and replay |
| Exact embedded snapshot script | PASS | 11 Node cases; host state unchanged |
| Existing panel regression | PASS | 51/51 Node tests |
| Python regression | PASS | 100/100 tests |
| Static audit | FAIL | Five existing findings: four workflow findings in dual-pipl.yml and one CLI rate-limit heuristic in artifact_manifest.py; no new findings |
| Remote CI for this development head | NOT RUN | Local verification above; remote evidence must be recorded separately |
| Live idle-hook/registry/project-safety gate | BLOCKED | Isolated AE environment and bounded supervisor not established |
| Late-registration repair | BLOCKED | No new live registration evidence |

Native guard and snapshot checks are included in research/full macOS workflows.
SDK AEGP compilation and the exact binary's inert-entry tests were run locally.
Saved local outputs under the build's `offline-checks/`: `node-tests.txt`
SHA-256 `61c46305827589478e19903ecd5ef63e830c0569a2c8e8c7cd6b163c721d1cd3`,
`python-tests.txt` SHA-256
`aeb1f01c10c3bfbdb80fd6b444637bb339c58e48a4f35e84947fa97dd3129612`.
Audit record: current chat `work/scoped-gate-final-audit.json` (source `01aef68`
with only result documentation pending); findings retain their existing scope
and do not become release acceptance. Raw crash dumps remain outside Git. The original broad
scan FAIL and prior valid runtime PASS results remain unchanged.
