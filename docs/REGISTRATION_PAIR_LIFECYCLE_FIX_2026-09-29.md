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

Live host error resolution: NOT RUN. The current AE session may retain the old
fixture image despite retirement of its disk installation. New live validation
requires newly identified fixture bytes and a fresh controlled process.
This change provides no render compatibility claim and no RSMB late-registration
fix. Historical registry observations and the reported modal error are retained.
