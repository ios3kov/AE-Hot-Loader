# Registration fixture application gate — FAIL

Stage C of the A–D research plan; not production acceptance. Rules reviewed:
FSTR-Line DEVELOPMENT_RULES blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Identity and acceptance

- Probe source: `ab03290aeba32d02af23ea66394035e20457e36f` (clean at execution).
- Fixture: `50650366d8b6`, source `8980c3c96b4e20e0e0955929a2943b0b2f5ff81b`.
- Resident Agent: `native-36483421984-1`, source `04fea7060c7ef7ebc4a315b5c39364850287e294`.
- Host baseline: AE 25.6x101, PID 21778, start Sep 29 12:49:13 2026.
- Run: `pair-apply-461b275a66d3487a95cd88e84d9fd8a4`.
- Local evidence: `build-ae-hot-loader/evidence/` plus that Run ID.
- Required: fresh identity/blank baseline, exact match application on a disabled
  layer, expected property contract, disposable cleanup, same-process postflight.
- No render, reload, install, preferences change or restart in this gate.

## Observed results

| Gate | Result | Evidence |
|---|---|---|
| JSX mocked safety paths | PASS | `node tests/registration-apply-js.cjs`, 7/7 |
| Fresh baseline and Agent identity | PASS | `preflight/report.json` |
| Complete application assertion | FAIL | `apply.json`: expected 0 children, observed 1 |
| Cleanup reported by JSX | PASS | `apply.json`; independent confirmation unavailable |
| Independent postflight | BLOCKED | no running AE found by collector |
| Whole gate | FAIL | `failure.json` |
| Render | NOT RUN | intentionally unsupported by fixture |
| Original 25::34 symptom resolution | NOT RUN | no conclusive UI evidence |

The exact-match addProperty call returned an effect and reading numProperties
returned 1. This is a scripting child-property count, NOT proof that native
PF_OutData.num_params is wrong. The probe's zero-child assumption may be wrong;
inspect child match names before changing native code or accepting a new count.

DoScriptFile returned exit 0 and `0` stdout, but that is NOT a gate PASS.
The original AE process was absent during postflight and subsequent process
inspection. Cause is unknown: do not label this a confirmed crash or intentional
user quit. No matching crash report was located in the initial DiagnosticReports
check. UI inspection also timed out. Do not automatically replay the probe.

SHA-256:

- `apply.json`: `588c69d568b445780662da1846a8b46949e74edaaaa7377b194e94c6f4aac468`
- `failure.json`: `7bd39c9f54cf4dbd8f62ce5d5f8e0f1f609e69eef13c225a1ecab82ce525fbc7`

## Next

Establish why the host session ended, then run a separately identified fixture
property-enumeration diagnostic with fresh baseline and postflight. Keep this
failure record. Historical RSMB render PASS and PiPL late-registration FAIL are
unchanged. No full-product release, merge, push or main changes were performed.
