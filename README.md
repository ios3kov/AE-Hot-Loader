# AE Hot Loader

Hot-reload workflow for native Adobe After Effects effects on macOS Apple Silicon.

## Clean installer

`INSTALL.command` now performs a clean migration before installing the current build.

It validates the new package first, backs up the currently managed user Agent/Control Shell, then moves known old diagnostic/legacy AE Hot Loader copies out of Adobe plug-in folders. This includes LiveTest, ProbeTest, DualPiPL, RustProbe, RustProbePermissive, SinglePiPLCpp, old Loader/Bridge copies, and other bundles using the `com.os3kov.AEHotLoader.*` bundle-ID prefix.

The installer asks for the macOS administrator password only when old system-wide copies actually need to be moved. Stale staged implementations, bridge files, runtime copies and Loader logs are also cleared from the active paths. See `QUICK_START.md`.

## Product UX

User-facing surface:

`Window → AE Hot Loader`

Main action:

**Reload Plugins**

The panel does not apply effects automatically and does not replace the native **Effects & Presets** workflow.

## Production architecture

```
After Effects startup
    ↓
stable effect shell .plugin
    ↓
hot-swappable implementation .dylib

Window → AE Hot Loader
    ↓
AEGP Agent
    ↓
loaded shell(s) → atomic implementation swap
```

### Stable shell

Each hot-reloadable effect has a small native shell plug-in.

The shell:
- owns the PiPL and stable After Effects registration;
- appears normally in native **Effects & Presets**;
- exports the normal `EffectMain`;
- forwards effect commands to the currently active implementation dylib;
- can switch to a newly built implementation while AE stays open.

A **new effect shell requires one AE restart the first time it is installed**. After that, implementation updates are hot-reloadable.

### Implementation dylib

Effect logic lives in a separate dylib.

Reloading uses a new uniquely staged dylib image, validates Protocol ABI / State ABI / Runtime ABI / implementation key, assigns a content-derived generation, and only then publishes the new `EffectMain`.

MFR/render calls are tracked. A reload never blocks AE waiting for an active render; when the effect is busy, Reload returns a retry status. Old dylib images stay loaded until AE exits so persistent state and generation-specific destructors remain valid.

### AEGP Agent

`AEHotLoaderAgent.plugin` is loaded at AE startup and services requests from the ScriptUI panel.

Production responsibility:
- receive `Reload Plugins`;
- discover loaded hot-reload shells;
- ask each shell to load its latest implementation;
- report success / unchanged / failure.

## Important research conclusion

The earlier private `ML::LoadPlugins` research proved that AE can late-load some bundles, but it is not a reliable production mechanism for registering arbitrary new native effects into AE's Installed Effects Registry after startup.

Live diagnostics showed cases where:
- the bundle executable was loaded;
- `PluginDataEntryFunction2` was called;
- the registration callback existed;
- the callback returned `0`;
- the Installed Effects Registry still did not gain the effect.

Therefore production development no longer depends on runtime registration of a completely new effect.

The private loader code remains research-only and is not the product architecture.

## Target workflow

For an already installed shell:

```
edit effect code
→ build implementation dylib
→ click Reload Plugins
→ shell loads new implementation
→ continue working without restarting AE
```

## Current target

- After Effects 25.6
- macOS Apple Silicon
- shell protocol ABI: **2**
- adapter StateABI: **4** for ElasticGrid and Stellar Gradient
- pinned hot-reload Rust toolchain: **1.98.1**
- first production adapters: ElasticGrid and StellarGradient

The detailed pre-AE code audit is in `docs/CODE_AUDIT_2026-09-28.md`.

### Live validation status — 2026-09-28

Passed in real After Effects 25.6:

- stable Control Shell registration;
- bundled `default-v1` render;
- `candidate-v2` hot reload without AE restart;
- post-swap render through the existing effect instance;
- unchanged/no-op reload detection.

Next live gates: busy-render rejection, bundled rollback, then ElasticGrid and Stellar Gradient.

## Release gate

The shell architecture is considered ready when:

1. shell is visible in native Effects & Presets after normal AE startup;
2. bundled default applies and renders;
3. **Reload Plugins** switches to a validated candidate;
4. existing instances remain stable after the swap;
5. busy MFR/render produces retry instead of hang/crash;
6. candidate removal rolls back to bundled default;
7. ElasticGrid passes CPU/UI/MFR/GPU smoke;
8. Stellar Gradient passes CPU/SmartFX/MFR/GPU smoke;
9. repeated A→B→C reloads do not require AE restart.
