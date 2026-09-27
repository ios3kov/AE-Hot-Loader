# Shell Hot Reload — Live Gate

Target: After Effects 25.6 / macOS Apple Silicon.

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
1. runtime copy succeeds;
2. `dlopen` succeeds;
3. `EffectMain` resolves.

Old implementation handles remain loaded until AE exits.

## Pass criterion

The control shell is considered proven when:
- initial effect works after one normal AE startup;
- candidate-v2 becomes active after one panel click;
- no AE restart occurs between staging and reload;
- render continues to work;
- repeated reload/noop is stable.
