# Controlled RSMB apply/render host attempt 2 — 2026-09-29

## Scope and identity

- Branch state before this documentation record:
  `1011cd0b434787e7c0d0cbdc3baf1e09695a7af6` on
  `research/ordinary-plugin-discovery`.
- Harness source: `d19edca897bf2fec051ca6bc74d931416307759e`.
- Reference Agent source / Build ID:
  `04fea7060c7ef7ebc4a315b5c39364850287e294` /
  `native-36483421984-1`.
- Target host: After Effects `25.6x101`, macOS Apple Silicon arm64.
- Private preflight Test Run ID:
  `aehl-preflight-01da77cf22d746c6b10a6cbae0c0d874`.
- Launcher exit code: `1`.
- Exact collector SHA-256:
  `cfb7175f7f394b7bc17f838f8fb5337c9bee5e6fde46125570762c6d6b157865`.

The launcher, JSX and collector were rechecked as byte-identical to the
verified harness before execution. Their hashes and the planned assertion are
recorded in [attempt 1](RSMB_APPLY_RENDER_ATTEMPT_2026-09-29.md).

## Result

Overall controlled gate: **BLOCKED**.

The fresh preflight completed and proved the exact resident Agent identity,
all three RSMB registry match names and unchanged project counters. The
launcher then stopped with `STOP: before project is not blank/clean`: AE had a
saved, non-blank project open. The strict owned blank-project precondition was
not satisfied, so the launcher did not invoke the JSX.

| Check | Status | Evidence / scope |
| --- | --- | --- |
| Resident Agent identity | PASS | Exact Build ID, commit, clean state, target and version matched. |
| RSMB registry presence | PASS | All three exact match names were present before and after preflight. |
| Preflight project unchanged | PASS | Counters and saved/dirty/render state matched before and after. |
| Blank/unsaved/clean/idle baseline | FAIL | The observed project was saved and non-blank. |
| Overall controlled gate | BLOCKED | Unsafe baseline prevented entry into the owned test scenario. |
| RSMB add / apply | NOT RUN | JSX was not invoked. |
| One-frame render | NOT RUN | No owned render was started. |
| Cleanup | NOT RUN | No disposable project was created. |
| Output SHA-256 | NOT RUN | No owned render output exists. |
| Same-PID render postflight | NOT RUN | The render phase did not start. |

This attempt does not establish RSMB apply/render compatibility. Controlled
cold-start causality remains NOT RUN, and the historical late-registration
FAIL is unchanged.

## Safety and next step

The harness did not close, save or replace the open project. It did not request
a plug-in reload, installation, restart, preference change, private teardown
or process termination. Private host evidence and project details remain
outside the repository.

The exact same launcher can be retried only after the user intentionally leaves
AE with exactly one running process and a blank, unsaved, clean, idle project.
That future run requires fresh pre/postflight and its own evidence record.
