# AE Hot Loader — Production Plan

## Goal

Allow a newly installed native After Effects effect plug-in to become available in an already-running After Effects process on macOS.

## Phase 1 — Proof of concept

1. Capture the host registration callback during normal AE startup.
2. Keep a permanent loader plug-in active.
3. Trigger a second effect registration after AE is fully running.
4. Confirm the late effect appears in the Effect menu.
5. Apply it to a layer and confirm rendering works.

### Stop criterion

AE is running → click **Register Late Effect** → new effect appears → applies → renders → no AE restart.

If the late-registration callback is rejected, stop product work on the public-callback approach and move to internal loader investigation.

## Phase 2 — External plug-in bundle loading

1. Scan standard Adobe/MediaCore plug-in locations.
2. Detect newly added `.plugin` bundles.
3. Load bundle executable with the macOS dynamic loader.
4. Resolve `PluginDataEntryFunction2` and `EffectMain`.
5. Invoke registration using the proven host context.
6. Verify AE menu visibility and application.

## Phase 3 — Compatibility

Test:
- CPU effects
- SmartFX
- Metal/GPU effects
- custom UI
- licensing frameworks
- embedded dylibs/frameworks
- signed/notarized bundles

## Phase 4 — Product UX

- Reload Plugins button
- folder watcher / auto-detect
- success/error list
- per-plugin compatibility status
- logs and blacklist
- never unload an effect that may be in use

## Platform order

1. macOS Apple Silicon
2. macOS Intel only if still useful
3. Windows only after macOS feasibility is proven
