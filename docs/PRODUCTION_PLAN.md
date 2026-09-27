# AE Hot Loader — Production Plan

## Product definition

AE Hot Loader is a dockable ScriptUI tool that reloads the implementation of already-registered native After Effects effects without restarting AE.

User-facing surface:
- `Window → AE Hot Loader`;
- **Reload Plugins**;
- status / errors;
- Auto Watch later.

It does **not** auto-apply an effect to the active layer.

## Production constraint

After Effects performs effect registration during normal plug-in discovery/startup.

Production therefore assumes:

**one stable shell registration → many implementation reloads**

A brand-new effect shell requires one normal AE restart after installation. Subsequent implementation changes must not require a restart.

## Final architecture

```
ScriptUI panel
    ↓ request/response
AEGP Agent
    ↓ enumerate loaded shells
stable effect shell .plugin
    ↓ atomic function-pointer swap
versioned implementation .dylib
```

### Stable effect shell

Responsibilities:
- own PiPL / match name / category / entry point;
- remain loaded for the AE session;
- expose the effect through native Effects & Presets;
- forward `EffectMain` calls to the active implementation;
- expose a private shell reload export for AE Hot Loader;
- never unload an implementation image during the session.

### Implementation dylib

Responsibilities:
- contain the effect behavior;
- export an EffectMain-compatible entry point;
- be independently rebuildable;
- be loaded from a unique runtime path on every accepted reload.

Safety rule:

**do not `dlclose` old implementations while AE is running.**

This trades a small amount of temporary process memory for much safer reload behavior with render threads and existing effect instances.

### AEGP Agent

Responsibilities:
- receive ScriptUI commands on AE's main-thread/idle path;
- enumerate already loaded shell plug-ins;
- invoke their reload exports;
- collect per-shell results;
- return concise status to the panel;
- keep diagnostics/logging.

The Agent must not depend on applying an internal effect to a layer.

## Research path — closed for production

The project investigated:
- saved `PF_PluginDataCB2`;
- direct late registration;
- internal `ML::LoadPlugins`;
- isolated runtime staging;
- registry diagnostics;
- Rust/C++ single- and multi-PiPL controls.

The research established that successful binary loading and even a registration callback result of `0` do not reliably imply insertion into AE's Installed Effects Registry after startup.

Therefore:

- private `ML::LoadPlugins` is **not** the production architecture;
- UI refresh hacks are abandoned;
- runtime registration of an arbitrary brand-new effect is not a release requirement;
- research code stays isolated until it is removed or archived.

## Implementation phases

### Phase 1 — control shell

1. Convert the existing bridge wrapper into a stable control shell.
2. Register it normally at AE startup.
3. Move behavior behind an implementation dylib.
4. Export `AEHotLoader_ShellReload`.
5. Reload by loading a uniquely staged dylib and atomically swapping the implementation pointer.
6. Keep old dylib handles alive until AE exits.

**Gate:** repeated implementation swaps work without restarting AE.

### Phase 2 — Agent integration

1. Replace production `Reload Plugins` behavior with shell enumeration.
2. Find shell exports in loaded dyld images.
3. Invoke every shell reload.
4. Return per-shell success / unchanged / error.
5. Keep the ScriptUI protocol stable.

**Gate:** one panel click reloads the control shell implementation.

### Phase 3 — ElasticGrid adapter

1. Preserve ElasticGrid's public PiPL identity in a shell.
2. Move effect logic into its implementation dylib.
3. Build/update implementation independently.
4. Verify existing instances, render and repeated reloads.

### Phase 4 — StellarGradient adapter

Same architecture and validation as ElasticGrid.

### Phase 5 — production hardening

- unique runtime staging paths;
- implementation version/fingerprint;
- malformed dylib rejection;
- missing export rejection;
- rollback: retain previous active implementation when a new load fails;
- logs and diagnostics;
- repeated reload stress test;
- Multi-Frame Rendering / render-thread stress;
- crash/recovery documentation;
- signing/notarization strategy.

### Phase 6 — UX

- clear per-effect reload status;
- Auto Watch;
- compatibility indicators;
- compact log view;
- optional implementation build integrations.

## Stop criteria

Development stops and the architecture is considered viable only when all are true:

1. shell effect appears through native AE startup registration;
2. effect applies and renders;
3. implementation A is active;
4. implementation B is built while AE remains running;
5. **Reload Plugins** switches A → B;
6. B → C → D repeated reloads work;
7. existing instances do not crash;
8. failed implementation load leaves the previous implementation active;
9. ElasticGrid and StellarGradient both pass the same workflow.

## Platform order

1. macOS Apple Silicon / AE 25.6
2. newer AE versions after the shell ABI is stable
3. Windows only after the macOS product workflow is complete
