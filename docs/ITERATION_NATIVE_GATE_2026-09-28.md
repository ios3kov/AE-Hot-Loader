# Native research build gate — 2026-09-28

Baseline: `732b8edefcdd50842b3de28379c9bb2ce6383a8e` on
`research/ordinary-plugin-discovery`. Shared rules reviewed at blob
`a1760fde8763f789b50b91c20407938b4fcaea4a` (FSTR-Line DEVELOPMENT_RULES).

## Scope and acceptance declared before the native run

Enable the existing complete macOS build pipeline for the research branch,
without removing any native smoke/negative test. No host registration code,
private ABI, installed bundles, user projects or main-branch changes.

Mandatory checks for this stage:

1. Existing Rust/C++ static and shell-contract checks.
2. Build default, candidate-v2, candidate-v3, Agent and Control Shell.
3. Assemble/sign bundles and validate signatures, exports and deployment target.
4. Retain direct reload/rollback, shell discovery, duplicate-key rejection,
   busy-swap and incompatible-key/runtime-ABI/unterminated-string tests.
5. Run the new 14 manifest unit tests and the existing 22 panel host-mock tests.
6. Record clean source identity and compiler/SDK information before compilation.
7. Hash final signed package files; verify the complete inventory before and
   after archive extraction; hash the final ZIP without modifying it afterward.
8. Preserve run-specific source/evidence and internal-build artifacts. Do not
   publish a Release or offer a package for installation as a result of CI alone.

## Evidence available at authoring

The manifest helper passed 14/14 tests locally under Python on Linux. Tests
cover roundtrip/determinism, changed/added/missing files, identity mismatch,
symlinks, traversal-like manifest keys and accidental runtime-approval claims.
The native workflow for the resulting commit is NOT RUN at authoring. Its
actual result must be recorded from its own run, not inferred from old CI.

Historical build artifact 10962083434 from run 36405500792 was retrieved and
its outer ZIP hash verified:
`9bcd445489883f6e9fac60ca7e46b8836cc4fdc9caff832fcabdc21b8a456ddb`.
Its generated lockfiles are historical inputs, not proof of a current build.

## Identity and limitations

The manifest records package Build ID, Git commit, all payload hashes and an
explicit `runtime_identity_verified=false`. It intentionally does not pretend
that a file hash proves which code AE loaded. The legacy Agent still has a
static runtime label; generated runtime identity across components remains a
release blocker. Current Cargo lockfiles are generated and retained as build
evidence, not yet committed: dependency selection is not fully frozen between
runs. No bit-for-bit reproducibility claim is made.

Native smoke tests run outside AE, in owned runner workspaces and fake HOME
directories. Busy-swap smoke is not evidence of AE MFR integration. No renderer,
GPU, user process, restart, cache purge or RSMB cold-start test is run here.
Real AE integration, controlled RSMB startup/apply/render and full candidate
handoff gates remain BLOCKED/NOT RUN until separately exercised.

Sources: GitHub Actions workflow syntax and Cargo build documentation
(`--locked` requires an existing unchanged lockfile). This stage preserves the
existing native test logic rather than replacing it with syntax-only checks.
