# Agent identity CI correction — 2026-09-28

Source `72dd50a2734235b4db428dfdbd14cfb2bdd48dff` did not pass native gates.
Run 36477934165 (#239) stopped at Rust formatting in `agent/build.rs` and
`agent/src/lib.rs`; no native build or package was produced. Those exact
formatter changes are applied without changing behavior.

Identity run 36477932628 failed workflow validation before jobs started.
The job-level `env` used `runner.temp`, which is not an allowed context there.
The target directory is now the already ignored `target-ae-hot-loader` path.
The step-level artifact path may still use `runner.temp`.
Reference: https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#context-availability

Acceptance is unchanged: generator regression, locked native builds, actual
Agent getter tests and the existing full package/synthetic gates must pass.
The failures remain historical evidence, not a successful checkpoint.
No loader behavior, dependency versions, user installation or release changed.
