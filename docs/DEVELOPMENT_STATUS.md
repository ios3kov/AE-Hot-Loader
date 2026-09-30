# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Stage **C of A–D**, with open A/B/D and release gates. No completion percentage.
AGENTS, PRODUCTION_PLAN and shared rules apply; rules were rechecked unchanged
at blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
Previous status is preserved at [immutable checkpoint 56683d8](https://github.com/ios3kov/AE-Hot-Loader/blob/56683d873edbafb1b489e331458c14783422b6d0/docs/DEVELOPMENT_STATUS.md).
Dated evidence is unchanged; old permissions are not renewed.

## Latest implementation — one offline run, one private report

Code/test/workflow commit: **`7411a903fb6cb21ca1f93e258d172e1a268072a2`**.
Added `tools/run_research_checks.py`, `RUN_OFFLINE_CHECKS.command` and 22
orchestration regressions. The research workflow now uses the same runner on
Linux and macOS while retaining its two existing job names. The separate full
macOS product build/sign/package/smoke workflow is unchanged.

The runner executes existing offline checks sequentially, pins actual tracked
bytes to HEAD (including hidden assume-unchanged modifications), checks source
identity between stages, stops after failure and retains one new report ZIP.
It records explicit platform skips and never treats offline PASS as live-AE or
release PASS. Real test-child failure/timeout, bounded logs, source changes,
missing worker evidence, report hashes and non-overwrite behavior were tested.

This consolidates implemented checks, **not** the complete future user pipeline.
Product build/sign/package is NOT RUN by this local runner; its independent CI
result is separate. No native FILE adapter, no-scan host probe, registration,
apply/render or risky-action permission is connected. No user run is requested.
[Scope, exact behavior, failure handling and remaining integration](UNIFIED_OFFLINE_RUNNER_2026-09-30.md).

## Verified results for exact code 7411a90

| Gate | Result and scope |
|---|---|
| Local unified Linux run | PASS: 234 Python collected, 227 PASS/seven explicit macOS skips; Node 51+11 PASS |
| New orchestration regressions | 22 PASS in the complete local/CI suites, including actual owned child processes and temporary Git/file tests |
| Research CI 36767508822 | PASS, both Linux and macOS jobs completed |
| Unified macOS arm64 run | PASS: all 21 planned stages; Python 234/234 without skips, Node 62/62, native scoped mock-loader guards 15/15 |
| Owned ABI/LLDB tests on macOS | Retained and passed; six owned ABI cases at both -O0/-O2; no Adobe code execution |
| Existing resource policy/journal cases | Retained within Python totals, not counted again as additional Python tests |
| Downloaded unified reports | PASS: both outer hashes, inner manifests, exact source commit and all five changed file hashes verified |
| Full product macOS CI 36767508583 | IN PROGRESS at this documentation checkpoint; source/static/regression and default build passed; final build/package result not yet asserted |
| FILE/PLUG binding and live-AE tests | NOT IMPLEMENTED / NOT RUN; full pipeline remains BLOCKED |
| Full static-security audit | NOT RUN again; five historical findings remain unresolved |

The macOS unified report identifies macOS 15.7.9 arm64, Python 3.14.7,
Apple clang 17.0.0 and Node 22.23.2. This is hosted CI, not the user's working AE.
No successful test is represented as a new ordinary-plugin registration result.
The earlier 212-test suite is retained, with 22 orchestration tests added.

Evidence from research run `36767508822` was downloaded and independently hashed:

| Evidence | ID / SHA-256 |
|---|---|
| macOS Actions archive | `11121352036` / `596ec86fe9e6aa3770c9c3412b978b30894db140b459cee544687159d25f40c3` |
| macOS inner report ZIP | `8c1e89de46a659886d52c495095c0d7e758cea53f0e8b3f6659e46cbb1d81651` |
| Linux Actions archive | `11121431993` / `a79c6de719610876a43c72be030d7079d0fa78e1b7a6a80a93f9a945d23daec7` |
| Linux inner report ZIP | `a859d47840084e1da2e479f226bae71c6a3f3f7373d29906a35cfd983e94f026` |

Runner SHA-256: `e9f1968549e2974a5033aa970341d876416e20ff1f3b1d5dbc65f13063705aa3`.
Runner Git blob: `8d03dab4d1bed4724e14709d2fb06d23a6b6215b`.
Tests SHA-256: `380e69951e6b8b8e546fe07496869c7027236feea9c4d71c2096632a9af56e7b`.
No installable AE package is handed over. Green jobs do not clear unreviewed
warnings. Documentation follow-ups use [skip ci]; CI belongs to the code commit.

## Core engineering boundary — unchanged by test consolidation

The [FILE contract](FILE_OBJECT_CONTRACT_2026-09-30.md) and tested arm64
indirect-result primitive remain the baseline. The missing work is verified
host-string construction/destruction, FILE_New/path return/disposal binding,
loaded-symbol provenance, and the separate no-scan create/roundtrip/release
probe. The later PLUG resource pass also needs its end-of-pass callbacks and
retained state reviewed; a single root does not constrain every cleanup callback.
The backend and live external supervisor remain unbound. Existing scoped commands
still invoke the old loader and must not be reused for the proposed resource pass.

Do not replace host callbacks, fabricate host objects, use global folder helpers,
replay Birth/InitIterator/RequiredPreSearch, change the final bool, clear caches,
force notification, unload native modules or repeat the unchanged scan.
Any private host call, installation, restart or attachment needs separately
specified authorization and a fresh host/project/loaded identity. The original
installation and one-restart permissions are consumed.

## Preserved actual host results

Scoped embedded late registration remains **FAIL**, source `45de0c9`, Build ID
`scoped-0b8c8f122e80`, fixture `88019a1a01a7`, 785 unchanged effect identities.
RSMB startup-registered apply/render **PASS** and historical late-registration
**FAIL** remain separate. The earlier flat-resource failure is not declared fixed.
Current AE/project/resident identity is **NOT OBSERVED**; no user-Mac update,
pull, installation or fresh baseline is claimed. The old PID 78417 is historical.

Product loader/Agent/shell/panel, user projects/settings, third-party plugins
and main are unchanged. No merge, installation, restart or release. Proprietary
inputs remain private. Live registration, apply/render, integration, compatibility
and clean-candidate release gates remain open.
