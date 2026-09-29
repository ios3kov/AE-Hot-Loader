# Registration pair 50a85fce3046: registry observations and fixture failure

Rules blob: `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
Fixture source: `f393fbd7d7a98fead93bdb6f2982250db3d7b5e3`.
Build ID: `50a85fce3046`; hashes and toolchain are in
`REGISTRATION_PAIR_NEXT_GATE_2026-09-29.md`.
Resident Agent: `native-36483421984-1`, source
`04fea7060c7ef7ebc4a315b5c39364850287e294`, clean, arm64, version 0.1.0.

## Observations

| Check | Status | Evidence |
| --- | --- | --- |
| Controlled startup registry, PiPL-only | PASS | Exact match present in AE PID 20726 |
| Controlled startup registry, Dynamic | PASS | Exact match present in AE PID 20726 |
| Subsequent startup without pair | PASS | Both exact matches absent in PID 21168 |
| One late discovery, Dynamic registry | PASS | Exact match became present in same PID 21168 |
| One late discovery, PiPL-only registry | FAIL | Exact match remained absent in same PID 21168 |
| Agent identity and project counters | PASS | Pre/postflight identity matches; blank project counters unchanged |
| Fixture initialization safety | FAIL | User screenshot: parameter count mismatch in AEHL Dynamic 50a85fce3046, AE error 25::34 |
| Overall pair acceptance | FAIL | Host error invalidates an error-free fixture claim |
| Fixture apply/render validation | NOT RUN | Registration-only probes are not valid render fixtures |
| Owned installation retirement | PASS | Exact hash-verified test directory moved out of MediaCore into evidence |

The screenshot arrived after the registry procedure. Its triggering host
command was not captured; do not assume the user applied the effect or that
the scan alone triggered the dialog. The runner did not apply or render it.

## Evidence

Local root: `build-ae-hot-loader/registration-pair-50a85fce3046/`.
Startup run: `startup-ecd7a6d4a5604584b8214cb84daade06`.
Late run: `late-cc72c8abdfa54626bfa2e5f1fd06196c`.
Startup result SHA-256:
`0ba47000c24e68c49731b7bf8143f10395c893b22a3f8957add6306769b1cf42`.
Late result SHA-256:
`493f0bc3cd2535614658fa40beb96f94a2837d6ba71dc9ec1f5dc87a83531587`.
One correlated reload request: `pair-a8ac1fce9a35466295f97b3142357066`.
Its success reply included the expected Agent identity. Registry observations
above are independent of the reply's loaded-module counts.

The retired bundles remain recoverable in `retired-startup` and `retired-late`
inside the late-run folder. No unrelated plug-in or preference was removed.
Retiring files does not unload images already resident in AE.

## Defect and next gate

`RegistrationPair.cpp` returns zero for every EffectMain command and never
initializes parameter count or other required effect lifecycle data. The
observed parameter-count error is consistent with this incomplete fixture;
the exact callback sequence still needs instrumentation.

Do not repeat this fixture in live AE. Replace the stub with a minimal valid
effect using verified SDK definitions, cover lifecycle/parameter setup, and
repeat startup acceptance before any late-loading conclusion is broadened.
Do not write PF_OutData via guessed offsets. The safe missing PiPL registration
step remains unidentified; no production loader change is justified.

The earlier RSMB one-frame apply/render PASS remains a separate historical
result. This pair test does not fix RSMB late registration or certify RSMB
controlled startup/apply/render.
