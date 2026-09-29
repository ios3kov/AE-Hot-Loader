# Stage C: standalone public Resource Manager control

Rules rechecked: blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`, unchanged.
Production-engineering workflow applied to a single diagnostic hypothesis.
Acceptance: in separate processes read one owned embedded PiPL with and
without an application-local header callback; observe callback invocation,
native count, no executable loading and unchanged complete bundle hashes.
No AE launch/attach, private calls, installation or new full-root scan.

## Identity and evidence

- Source: `c89a75e04cf3400080e966b30f88f1b00afdd9b3`, clean.
- Run/Build ID: `endian-control-242310b0514b4b60ae09ff9a76f14f21`.
- Local evidence: `build-ae-hot-loader/evidence/<Run ID>/record.json` and `probe`.
- Probe SHA-256: `9599bcd6d65aac430d4c8e06ee519882316e1ca79bc6460860a00b4467af4265`.
- Record SHA-256: `85f97838a640391f743dc67dc60cb5e69c29d9b2e9613210d537adac1b45b8df`.
- Compiler: Apple clang 21.0.0, arm64; macOS SDK 27.0.
- Input fixture: Build `79a6ce4be9f7`, owned AEHLPairRsrc bundle; complete file
  hashes retained in record. No input executable loaded.
- Input resource SHA-256: `1876f03aceb143f255f38f2e4e961d259889c9151fb89b2bc9c15e464cdf1f21`.
- Native product Agent remains `native-36483421984-1`; no new product build.

Reproduce: `python3 experiments/ordinary_discovery/run_resource_endian_control.py
--bundle build-ae-hot-loader/resource-pair-79a6ce4be9f7/AEHLPairRsrc79a6ce4be9f7.plugin`
(one command). Subprocess timeout is 30 seconds. Output directories are unique.

## Results

| Check | Result | Observation |
|---|---|---|
| Native compile with warnings as errors | PASS | Deprecation warnings explicitly excluded for this deprecated-API experiment |
| Baseline process, no callback | PASS | Native count 201326592, callback count 0 |
| Separate callback process | PASS | Native count 12, from-disk callback count 1 |
| Third fresh baseline process | PASS | Native count 201326592, callback count 0 |
| Bundle executable not loaded | PASS | false before/after in all three processes |
| Complete input bundle unchanged | PASS | Identical file/hash map before and after |
| Python regression | PASS | 92/92 after source commit |
| Whitespace check | PASS | git diff --check |
| Repository static audit | FAIL | Same existing workflow hardening debt; CLI auth warning remains false positive |
| Live AE registration repair | NOT RUN | This is not an AE experiment |

The callback is original, header-only test code. It accepts only resource
type PiPL, ID 16000, bounded size, and property count 12. It converts the two
header words, NOT the property list, and MUST NOT be used as a real PiPL
converter or installed into AE. No Adobe implementation is called/copied.
The program reads only the count; it never interprets the partly converted
payload as a plugin. Callback registration dies with the standalone process.

Apple's local Endian.h documents application-local flipper registration and
the disk-big-endian/native direction flag. The Resource Manager actually
invoked our callback during this test; this is stronger than an offline
guess about the existence of such a mechanism.

## Conclusion and next step

Resource bytes observed by a standalone process depend on its registered
conversion callback. Therefore the earlier raw standalone resource hash does
not establish what bytes an AE process sees. SDK disk-byte equality remains
valid, but cannot certify in-memory parser compatibility.

This supports the byte-order boundary hypothesis, not the cause of the prior
AE exit, the identity of AE's active flipper, or a fix for RSMB/legacy discovery.
The flat-file path was not executed here; do not generalize this embedded
resource test to it. The failed raw flat scan must not be repeated.

Next inspect when PluginSupport installs its PiPL flipper and which actual
module reader the late path uses. Establish exact runtime state only in a
bounded isolated host experiment before proposing any native-path change.
No main modification, push, release or installable artifact handoff.
