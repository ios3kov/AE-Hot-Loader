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
AE private loader + post-load filter registration
```

### Ordinary plugin discovery

The primary workflow accepts an ordinary After Effects `.plugin` bundle without
requiring a wrapper or shell conversion. The Agent scans the standard Adobe
plug-in roots, invokes the host's loader, collects newly created video-filter
modules, and completes the same filter-loading notification used during AE
startup.

The current compatibility target is After Effects 25.6 on arm64. This path
uses private host ABI and is version-gated.

### Stable shell

Each hot-reloadable effect has a small native shell plug-in.

The shell:
- owns the PiPL and stable After Effects registration;
- appears normally in native **Effects & Presets**;
- exports the normal `EffectMain`;
- forwards effect commands to the currently active implementation dylib;
- can switch to a newly built implementation while AE stays open.

A stable shell remains available for the separate implementation hot-reload
workflow.

### Implementation dylib

Effect logic lives in a separate dylib.

Reloading uses a new uniquely staged dylib image, validates Protocol ABI / State ABI / Runtime ABI / implementation key, assigns a content-derived generation, and only then publishes the new `EffectMain`.

MFR/render calls are tracked. A reload never blocks AE waiting for an active render; when the effect is busy, Reload returns a retry status. Old dylib images stay loaded until AE exits so persistent state and generation-specific destructors remain valid.

### AEGP Agent

`AEHotLoaderAgent.plugin` is loaded at AE startup and services requests from the ScriptUI panel.

Production responsibility:
- receive `Reload Plugins`;
- scan the standard Adobe plug-in roots;
- late-register ordinary native effects through AE's loader and filter
  notification path;
- report loaded and newly registered module counts.

## Important research conclusion

The earlier loader-only experiment was insufficient: it loaded a bundle but did
not complete AE's post-load video-filter notification.

Live diagnostics showed cases where:
- the bundle executable was loaded;
- `PluginDataEntryFunction2` was called;
- the registration callback existed;
- the callback returned `0`;
- the Installed Effects Registry still did not gain the effect.

The completed path performs both operations and is validated against the
ordinary-plugin workflow in AE 25.6 arm64.

## Target workflow

For a newly installed ordinary effect:

```
AE remains open
→ install ordinary .plugin
→ click Reload Plugins
→ ordinary effect is registered
→ apply and render without restarting AE
```

For an already registered shell, the separate implementation hot-reload
workflow remains available.

## Current target

- After Effects 25.6
- macOS Apple Silicon
- shell protocol ABI: **2**
- adapter StateABI: **4** for ElasticGrid and Stellar Gradient
- pinned hot-reload Rust toolchain: **1.98.1**
- first production adapters: ElasticGrid and StellarGradient

The detailed pre-AE code audit is in `docs/CODE_AUDIT_2026-09-28.md`.

### Live validation status — 2026-09-28

The **Control Shell live gate is fully passed** in real After Effects 25.6:

- stable Control Shell registration;
- bundled `default-v1` render;
- `candidate-v2` hot reload without AE restart;
- real post-swap render through the existing instance;
- unchanged/no-op reload detection;
- deterministic busy-render rejection with `-4112`;
- `candidate-v2 → candidate-v3` reload and real `candidate-v3` render;
- rollback to bundled `default-v1`;
- real render after rollback;
- all of the above in one AE process.

### Cache / refresh UX requirement

Manual **Edit → Purge → All Memory & Disk Cache** was used only during validation to force AE to call the newly loaded `EffectMain` instead of showing an already cached frame.

Manual Purge is **not** acceptable as normal product UX. After a successful implementation reload, AE Hot Loader must automatically invalidate the affected effect/render cache and trigger or request a fresh evaluation so the updated result becomes visible without user cleanup.

This is now a release requirement, not part of the shell ABI proof.

Next live stage: real ElasticGrid, then Stellar Gradient.

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
9. repeated A→B→C reloads do not require AE restart;
10. successful reload invalidates stale cached output automatically — no manual Purge required in normal use.
