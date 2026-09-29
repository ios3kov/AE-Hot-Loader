# Controlled RSMB apply/render live PASS — 2026-09-29

## Identity and environment

- Branch state before this documentation record:
  `e5e15097c3b32a65fb60578b6a8ae02733f25ae6`.
- Corrected runner source:
  `f7cae49f5d50b4ff56e0e759945027715afc39d9`.
- Reference Agent source:
  `04fea7060c7ef7ebc4a315b5c39364850287e294`.
- Resident Agent Build ID: `native-36483421984-1`.
- Resident Agent target/version: `aarch64-apple-darwin` / `0.1.0`.
- Resident Agent source state: clean.
- Host: After Effects `25.6x101`, build 101, macOS Apple Silicon arm64.
- Host PID: `6305`, unchanged for the complete gate.
- Initial preflight Test Run ID:
  `aehl-preflight-91a40f41191340eebc29c64215364b7f`.
- RSMB JSX Test Run ID: `aehl-rsmb-1790678283279-625615`.
- Postflight Test Run ID:
  `aehl-preflight-6b8f42d871ef4c4d9e27c7cf178e577f`.

Exact runner inputs:

- launcher SHA-256:
  `f3ccfc5d5f0428148102d5efedb3c024c143c7c79260742b72a276b0b1f1a3d9`;
- JSX SHA-256:
  `d691874c217c650d7ae994256dcd2d2e25b292904193e99a2269bb6058d52935`;
- preflight collector SHA-256:
  `cfb7175f7f394b7bc17f838f8fb5337c9bee5e6fde46125570762c6d6b157865`.

The isolated runtime copy was byte-identical to the clean committed sources.

## Result

Overall controlled RSMB apply/render gate: **PASS**.

| Check | Status | Evidence / scope |
| --- | --- | --- |
| Initial Agent identity | PASS | Exact Build ID, commit, clean state, target and version matched. |
| Initial RSMB registry | PASS | All three exact RSMB match names were present. |
| Initial blank/unsaved/clean/idle state | PASS | Zero project items and queue items; no active render. |
| Initial project unchanged | PASS | Recorded project counters and state matched before/after preflight. |
| JSX baseline | PASS | Exact `Smart Motion Blur 3.x` identity present. |
| RSMB add / apply | PASS | Exact match name added; 14 parameters observed. |
| One-frame render | PASS | 64x64 single-frame PNG output, 2,860 bytes. |
| Disposable-project cleanup | PASS | Test project closed without saving; blank project recreated. |
| Output SHA-256 step | PASS | `render.sha256` was written and independently matched. |
| Same AE PID | PASS | PID remained `6305` through the complete launcher. |
| Postflight Agent identity | PASS | Same exact resident Agent identity matched. |
| Postflight RSMB registry | PASS | All three exact match names remained present. |
| Postflight blank/unsaved/clean/idle state | PASS | Zero items/queue, not rendering, revision 1. |
| Postflight project unchanged | PASS | Recorded counters and state matched within postflight. |

Evidence directory:
`~/Downloads/aehl-rsmb-1790678283279-625615`.

Evidence hashes:

- JSX report SHA-256:
  `75ca5722050c79de75deb3ec2fb46f96d49109511e6fda3305f5a3738f86c565`;
- rendered PNG SHA-256:
  `49961f447cf8ce22e5f8ff8f6622a0fc6d92f220aac1c85e727ea12881d10071`.

The launcher exited `0` and printed
`PASS: controlled RSMB apply/render gate`.

## Scope limits

This is a live compatibility smoke for an RSMB effect that was already present
in the registry at the start of the controlled run. It proves the observed
exact-match apply, one-frame render and cleanup path in AE 25.6x101 on this
host.

It does not prove controlled cold-start causality, late registration, temporal
quality, MFR, 8/16/32-bpc behavior, color-management correctness, performance,
license behavior or general compatibility with other effects and hosts.
Historical late registration therefore remains FAIL; controlled cold-start
causality remains NOT RUN.

The corrected runner has local verification PASS: 7/7 focused harness tests,
90/90 Python discovery tests, 6/6 exact JSX mocks and zsh syntax. CI for local
runner-fix commits `b3c30a0` and `f7cae49` is NOT RUN until those commits are
pushed.
