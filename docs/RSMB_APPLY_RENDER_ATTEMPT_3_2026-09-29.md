# Controlled RSMB apply/render host attempt 3 — 2026-09-29

## Scope and identity

- Branch state before this record:
  `7d17e5ad378a9bcd13f24ec562e8426d3dfb2dd5`.
- Runner source:
  `b3c30a09b6106c3c9f57e486bd621e4e2959954f`.
- Reference Agent source / Build ID:
  `04fea7060c7ef7ebc4a315b5c39364850287e294` /
  `native-36483421984-1`.
- Preflight Test Run ID:
  `aehl-preflight-87d028dd485a4343b7ca757cf0991bc7`.
- JSX Test Run ID: `aehl-rsmb-1790678082157-790720`.
- Host: After Effects `25.6x101`, macOS Apple Silicon arm64.

## Observed result

Overall launcher gate: **FAIL**.

The preflight and JSX stages ran successfully, but the launcher expected
`DoScriptFile` stdout to be the returned JSX report path. After Effects returns
status `0` for this call. The report and render output existed, while the
launcher rejected `0` as a missing file and exited with code `7`.

| Check | Status | Evidence / scope |
| --- | --- | --- |
| Resident Agent identity | PASS | Exact Build ID, commit, clean state, target and version matched. |
| RSMB registry presence | PASS | All three exact match names were present. |
| Blank/unsaved/clean/idle preflight | PASS | Required fields passed before and after the read-only preflight. |
| Preflight project unchanged | PASS | Recorded counters and render state matched. |
| JSX baseline | PASS | Empty project and `Smart Motion Blur 3.x` registry presence. |
| RSMB add / apply | PASS | Exact match name added with 14 parameters. |
| One-frame render | PASS | Non-empty PNG output, 2,860 bytes. |
| JSX cleanup | PASS | Disposable project closed and a blank project recreated. |
| Launcher report-path capture | FAIL | `DoScriptFile` returned `0`, not the JSX path. |
| Launcher output-hash step | NOT RUN | The launcher stopped before writing `render.sha256`. |
| Launcher same-PID check | NOT RUN | The launcher stopped before this step. |
| Postflight | NOT RUN | The launcher stopped before the final preflight. |

Independent inspection after the stop found the owned regular files:

- report SHA-256:
  `35ec1b304d3b5198cd22088fd09af467b07024e724ab50aa9443729e244db6d0`;
- rendered PNG SHA-256:
  `49961f447cf8ce22e5f8ff8f6622a0fc6d92f220aac1c85e727ea12881d10071`.

These hashes preserve the partial evidence but do not upgrade the overall gate
to PASS because the required same-PID check and postflight were not executed.
Cold-start causality remains NOT RUN, and historical late registration remains
FAIL.

## Root cause and correction

A non-mutating JSX return-value probe reproduced `DoScriptFile` stdout as `0`.
Source `f7cae49f5d50b4ff56e0e759945027715afc39d9` removes that assumption.
The launcher snapshots existing `aehl-rsmb-*` directories, requires exactly one
new user-owned real directory, and accepts only a user-owned regular non-empty
bounded `report.json`. Ambiguous or invalid evidence remains a hard stop.

Corrected launcher SHA-256:
`f3ccfc5d5f0428148102d5efedb3c024c143c7c79260742b72a276b0b1f1a3d9`.

Local verification is PASS: 7/7 focused harness tests, 90/90 Python discovery
tests, 6/6 exact JSX mocks and zsh syntax. A new complete live execution of the
corrected runner is still NOT RUN.
