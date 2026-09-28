# AE Hot Loader — Quick Start

Target: After Effects 25.6 on Apple Silicon Mac.

## 1. Clean install

1. Fully quit After Effects.
2. Double-click `INSTALL.command`.
3. If macOS asks for your password, enter it. This happens only when old system-wide AE Hot Loader test copies must be moved out of Adobe plug-in folders.
4. Wait for:

   `CLEAN INSTALL COMPLETE`

The installer validates the new package first, backs up the currently managed user copy, moves old diagnostic/legacy Loader copies out of Adobe plug-in folders, installs the fresh Agent + Control Shell, and clears stale staged implementations/logs/runtime copies.

Old diagnostic builds covered include LiveTest, ProbeTest, DualPiPL, RustProbe, RustProbePermissive, SinglePiPLCpp, old Loader/Bridge copies, and other bundles with the AE Hot Loader bundle-ID prefix.

## 2. First launch

1. Start After Effects.
2. Open `Window → AE Hot Loader`.
3. Search Effects & Presets for `AE Hot Loader Control Shell`.
4. Apply it to a layer and run Preview once.

## 3. Normal hot-reload check

1. Keep AE open.
2. Double-click `STAGE_IMPLEMENTATION.command`.
3. Click **Reload Plugins** in the AE Hot Loader panel.
4. Expected: `reloaded=1`, `failed=0`, `candidate-v2`.
5. Force a fresh Preview/render.
6. Optional Terminal check:

   `cat /tmp/ae-hot-loader-implementation.log`

   Expected new line: `candidate-v2: Render`.

7. Click **Reload Plugins** again without changing anything.
8. Expected: `unchanged=1`, `failed=0`.

## 4. Busy-render safety test

1. Confirm `candidate-v2` is already active from step 3.
2. Double-click `STAGE_BUSY_TEST.command`. It stages `candidate-v3` and arms a one-shot real-render self-test.
3. In AE, purge cache if needed and start a fresh Preview/render of the Control Shell.
4. Do **not** click Reload during the ~8 second held render. The active implementation now calls the shell reload gate itself from a helper thread while its own `EffectMain` is still in flight.
5. After the render finishes, run:

   `cat /tmp/ae-hot-loader-implementation.log`

   Expected lines include:
   `SlowRenderTest begin`
   and
   `BusySelfTest result=-4112 message=Effect is busy with an in-flight call; retry Reload Plugins.`

6. AE must remain stable.
7. Now click **Reload Plugins** once.
8. Expected: `candidate-v3` reloads successfully.

## 5. Rollback test

1. Double-click `ROLLBACK_TO_BUNDLED.command`.
2. Keep AE open and click **Reload Plugins**.
3. Expected: `reloaded=1` and `default-v1` becomes active.
4. Force a fresh Preview/render.
5. Click Reload once more; expected: `unchanged=1`.

## Logs

Double-click `COLLECT_LOGS.command` or use:

`cat /tmp/ae-hot-loader-implementation.log`

If anything differs from the expected result, send the AE Hot Loader panel result or the collected logs.
