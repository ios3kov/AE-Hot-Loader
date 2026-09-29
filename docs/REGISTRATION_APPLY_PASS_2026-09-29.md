# Dynamic fixture application — PASS (no render)

Stage C of A–D. Rules blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`
rechecked unchanged. Historical failures remain in REGISTRATION_APPLY_FAIL_2026-09-29.md.

## Evidence and correction

Fresh preflight `aehl-preflight-4e397f6752fd45d78166f399c634a9cd` found PID
21778 with original start `Tue Sep 29 12:49:13 2026`. Therefore the previous
assertion that AE exited was unsupported and is withdrawn. The original
postflight failed to identify exactly one host; that is NOT proof of process
termination. Its detection failure remains unexplained. The prior ad-hoc shell
check also used an incorrect path pattern (`After Effects.app` versus actual
`Adobe After Effects 2025.app`). No crash claim is supported.

Enumeration run `pair-apply-7d02419e310f4c36a0cc93a31248ac73`, source `21f5399`,
reported one child: `ADBE Effect Built In Params` / `Compositing Options`.
Cleanup and independent postflight passed in the same host. The assertion still
failed, preserving the original expectation. Its apply.json SHA-256:
`da5d3f86e48f850cdb45b47bcdb3655c1f37d4af6b09fdbd7d1111896d926f99`.

This directly establishes a harness defect: scripting child count includes a
host-owned group and is not the native parameter count. Before the next run,
acceptance was changed to require exactly that built-in group and no additional
children. Unknown/missing children still fail. Native fixture bytes unchanged.

## Passing gate

- Probe source (clean): `b97b4019a1b71e780af24141d7daa208c1e81591`.
- Fixture Build ID: `50650366d8b6`, source `8980c3c96b4e20e0e0955929a2943b0b2f5ff81b`.
- Agent Build ID: `native-36483421984-1`, source `04fea7060c7ef7ebc4a315b5c39364850287e294`.
- AE 25.6x101, PID 21778, same start as the original late-registration run.
- Run: `pair-apply-6ac122ed35a94abc8335d50770930551`.
- Evidence: `build-ae-hot-loader/evidence/<Run ID>/` (preflight, apply,
  postflight, metadata, invocation and result JSON plus executed JSX).
- result.json SHA-256: `63d3a000feefee712a4df29f8669a919b65d7938e709d81b718a4e62bff78ea2`.

| Check | Result |
|---|---|
| Fresh blank/clean/idle baseline and resident Agent identity | PASS |
| Exact `AEHL.Dynamic.50650366d8b6` application on disabled layer | PASS |
| Built-in-only property contract and effect removal | PASS |
| Disposable-project cleanup | PASS |
| Independent postflight, blank clean project, same PID/start | PASS |
| JSX safety regression | PASS: 10/10 |
| RSMB JSX regression | PASS: 6/6 |
| Python regression | PASS: 90/90 |
| Fixture render | NOT RUN |
| New CI | NOT RUN |
| Continuous visual absence of 25::34 | BLOCKED: UI snapshot failed |

No install, reload request, preferences modification or process termination was
performed in these application runs. Selecting AE through the UI tool found
the original host, not a new process. The installed test bundles remain retired.
Render remains unsupported by this fixture. This is scoped application evidence,
not complete modal-error certification, render compatibility or a product release.

Next: isolate missing PiPL-only registration; use a separately designed
render-capable fixture for eventual apply/render acceptance. Historical RSMB
late registration and PiPL-only late registration remain FAIL. Main unchanged.
