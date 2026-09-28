# Shell Hot Reload — Live Gate

Target: After Effects 25.6 / macOS Apple Silicon.

## Live status — 2026-09-28

The Control Shell gate is **FULLY PASSED** in real AE 25.6:

- shell startup registration returned `0`;
- bundled `default-v1` rendered;
- `candidate-v2` reloaded through the panel without restarting AE;
- the existing effect instance rendered through `candidate-v2`;
- repeated Reload reported `unchanged=1`, `failed=0`;
- deterministic in-flight render self-test returned `-4112` with the expected busy/retry message;
- `candidate-v3` loaded after the busy render ended and rendered successfully;
- removing the staged candidate rolled back to bundled `default-v1`;
- bundled `default-v1` rendered successfully after rollback;
- the entire A→B→C→bundled sequence ran in one AE process.

The Control Shell architecture is therefore proven. Adapter-specific ElasticGrid/Stellar Gradient live gates remain open.

## Clean-install prerequisite

Use the current package's `INSTALL.command` with After Effects fully closed.

The installer validates the new package first, backs up the managed user copy, then moves known old Loader diagnostics/legacy copies out of Adobe plug-in roots. It may ask for the macOS administrator password only when old system-wide copies exist. It also clears stale `current.dylib`, bridge requests, runtime copies, and Loader logs.

After the installer prints **CLEAN INSTALL COMPLETE**, start AE and continue with the test below.

## What this validates

This test no longer attempts to register a brand-new effect while AE is running.

It validates the production architecture:

`stable registered shell → hot-swappable implementation dylib`

## Test

1. Quit After Effects.
2. Run `INSTALL.command`.
3. Start After Effects once.
4. Open `Window → AE Hot Loader`.
5. Confirm **AE Hot Loader Control Shell** exists in native Effects & Presets.
6. Apply it to a layer and render/preview once.
7. Keep AE open.
8. Run `STAGE_IMPLEMENTATION.command`.
9. Click **Reload Plugins** once.
10. The panel must report:
   - `shell-reload-v1`;
   - `shells=1`;
   - `reloaded=1`;
   - implementation label `candidate-v2`.
11. Render/preview again.
12. Inspect:
   - `/tmp/ae-hot-loader-shell.log`
   - `/tmp/ae-hot-loader-shell-reloader.log`
   - `/tmp/ae-hot-loader-implementation.log`
   - `/tmp/ae-hot-loader-agent.log`

Expected implementation log after the reload contains `candidate-v2: Render`.

## Repeat gate

Run `STAGE_IMPLEMENTATION.command` again without changing the candidate file.

Expected result:
- shell is discovered;
- implementation is reported unchanged;
- AE remains stable.

## Failure safety gate

A bad candidate must not replace the current implementation.

The shell only publishes the new `EffectMain` pointer after:
1. runtime copy and content fingerprint succeed;
2. `dlopen` succeeds;
3. required Protocol ABI v2 exports resolve;
4. StateABI matches;
5. Rust Runtime ABI matches the bundled baseline;
6. implementation key/label are valid;
7. generation is assigned;
8. no EffectMain call is active.

Old implementation handles remain loaded until AE exits.

## Busy-render safety

A reload attempted while an EffectMain call is active must return a retry/busy error. It must not block AE waiting for render completion and must not publish the new generation.

Deterministic live procedure:

1. From the newest test kit, run `STAGE_IMPLEMENTATION.command`, click Reload, and confirm `candidate-v2` is active.
2. Run `STAGE_BUSY_TEST.command`.
3. Purge cache if needed and start a fresh Preview/render of the Control Shell.
4. Do **not** click Reload during the one-shot ~8 second held render. A test-only helper thread calls the shell reload entry point automatically while the current `EffectMain` call is still active.
5. After render completes, inspect `/tmp/ae-hot-loader-implementation.log`.
6. Expected: `BusySelfTest result=-4112` with the busy/in-flight retry message; AE remains stable.
7. Click **Reload Plugins** once after the render ends.
8. Expected: `candidate-v3` becomes active and renders.

The slow-render hook is test-only and activates only when `/tmp/ae-hot-loader-slow-render-once` exists. The first render consumes that sentinel. The callback wiring is optional and is not part of the production shell protocol contract.

## Bundled rollback live gate

1. With `candidate-v2` or `candidate-v3` active, run `ROLLBACK_TO_BUNDLED.command`.
2. Keep AE open and click **Reload Plugins**.
3. Expected: `reloaded=1` and `default-v1` becomes active.
4. Force a fresh render/preview and confirm the implementation log contains a new `default-v1: Render`.
5. Click **Reload Plugins** once more; expected: `unchanged=1`.

## Cache note

Manual cache Purge was used only as a validation aid to force AE to execute the active implementation instead of reusing a cached frame. It is not required by the shell architecture itself and must not become part of the user workflow.

Production requirement: after a successful reload, AE Hot Loader must invalidate stale cached output for affected instances and request/trigger fresh evaluation automatically.

## Pass criterion

The Control Shell criterion is now **passed**:
- initial effect works after one normal AE startup;
- A→B→C swaps work without restarting AE;
- real renders execute in each accepted generation;
- busy reload is rejected with retry instead of hanging/crashing;
- rollback to bundled implementation works and renders;
- repeated reload/noop is stable.

The next gate is the same workflow on real ElasticGrid and Stellar Gradient adapters.
