# Registration fixture parameter-setup correction

Stage C; shared rules blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
Baseline: `9a0d988`, Dynamic fixture error 25::34, overall acceptance FAIL.

The old EffectMain returned success for every command without setting
PF_OutData.num_params. The new implementation uses the locally supplied Adobe
25.6 SDK headers and sets one parameter (the host input layer) during
PF_Cmd_PARAMS_SETUP. Global version/flags match the PiPL. Rendering remains
unsupported and now returns PF_Err_INVALID_CALLBACK rather than false success.
No SDK headers or sample implementation are redistributed.

The pair builder now requires `--sdk /path/to/SDK/Examples` and records the
AE_Effect.h hash. Both variants still share one effect implementation.

Standalone regression: PASS, compiled with Apple clang and actual SDK headers,
`-std=c++17 -Wall -Wextra -Werror`. Test source:
`tests/registration_pair_lifecycle.cpp`. It verifies the input parameter count,
global version/flags, missing output-data error, render rejection and teardown.
Compile with `-I<SDK>/Examples/Headers -I<SDK>/Examples/Headers/SP` and execute
the resulting test binary. This check does not require After Effects.

Live host error resolution: NOT RUN. The prior AE session could retain the old
fixture image despite retirement of its disk installation. New live validation
requires newly identified fixture bytes and a fresh controlled process.
This change provides no render compatibility claim and no RSMB late-registration
fix. Historical registry observations and the reported modal error are retained.

## Clean build and subsequent live registration checks

Source: `8980c3c96b4e20e0e0955929a2943b0b2f5ff81b`, clean.
Build ID: `50650366d8b6`. Build/signature/export verification: PASS.
Python regression: 90/90 PASS. Standalone SDK lifecycle regression: PASS.
Manifest SHA-256:
`9fb2e82e3cef0586318a21b60bd0647bd846b9d7037d6d92847da1da64138bc6`.
AE_Effect.h SHA-256:
`5432df9bb447cefce2f96c1477d6beccd4686b7236d460c803beab76dae1d537`.

Fresh AE 25.6x101 processes were started with and without the exact pair.
Agent identity remained `native-36483421984-1` / `04fea706` / clean arm64.
Both names were absent before the single late scan in PID 21778; PID and
blank project counters were unchanged across it.

| Gate | PiPL-only | Dynamic |
| --- | --- | --- |
| Controlled startup registry | PASS | PASS |
| Same-process late registry | FAIL | PASS |
| Live application/parameter setup | NOT RUN | NOT RUN |
| Render compatibility | NOT RUN | NOT RUN |

Local evidence under `build-ae-hot-loader/registration-pair-50650366d8b6/`:

- `startup-14ad0f26b3364dd4a448e8974f32f3f6/result.json`, SHA-256
  `fd732a16296ab78e6a18066adddb1df3f57b4aef650b79b9fb1bd7a3e819d23b`;
- `late-1a1b1939ee3d472f81ef7ead9efcb128/result.json`, SHA-256
  `cab58ec70e94cc99bed12e13a13cab749903120cd93081575358208f05ade055`.

Cleanup PASS: both hash-verified test installations moved into the late-run
evidence directory. No test bundle remains on disk in its MediaCore test root.
The new Dynamic image may remain resident until normal AE exit. The old
50a85fce3046 process was closed during the controlled startup sequence.

The registry difference persists after correcting parameter-count setup.
This is not evidence that the original modal error cannot recur in an untested
application scenario. No production loader fix or safe missing registration
API has been established. CI for this local change is NOT RUN.
