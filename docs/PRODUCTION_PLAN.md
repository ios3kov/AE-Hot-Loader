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

## Shell architecture implementation status — 2026-09-27

Production shell architecture is implemented on `feature/internal-loader-agent`.

Implemented and CI-verified:

- stable control effect shell registered by AE at normal startup;
- resident AEGP Agent servicing `Window → AE Hot Loader → Reload Plugins`;
- dyld enumeration of loaded hot-reload shells;
- unique runtime copies for every implementation load;
- atomic `EffectMain` pointer swap;
- old implementation dylibs retained until AE exit;
- bundled-implementation fallback when a staged candidate is invalid or incompatible;
- explicit implementation protocol ABI;
- explicit implementation state/schema ABI;
- per-effect implementation key validation;
- human-readable implementation build label;
- stale staged control candidate cleared by installer;
- packaged runtime log collector.

The control shell CI performs a real macOS `dlopen` reload smoke outside AE:
candidate implementation loads successfully and an unchanged second reload is detected.

Latest verified AE Hot Loader CI at this checkpoint: **run #142 — SUCCESS**.

### ElasticGrid adapter

Repository: `ios3kov/ElasticGridFX`  
Branch: `feature/ae-hot-loader-shell`

Implemented:

- existing `ElasticGrid FX` PiPL identity retained;
- match name remains `com.elasticgrid.fx.warp`;
- stable C++ shell owns AE registration;
- existing Rust host is packaged as `libelasticgrid_impl.dylib`;
- implementation key: `elasticgrid`;
- hot-reload staging script added;
- shell ABI validation and bundled fallback enabled.

Verified:

- dedicated macOS Hot Loader Shell CI: **SUCCESS**;
- real shell-reload smoke: **SUCCESS**;
- full portable CI: GCC, Clang, ASan/UBSan, TSan and static analysis: **SUCCESS**.

### Stellar Gradient adapter

Repository: `ios3kov/stellar-gradient`  
Branch: `feature/ae-hot-loader-shell`

Implemented:

- existing `Stellar Gradient` PiPL identity retained;
- category remains `Stellar`;
- match name remains `StellarLabs.StellarGradient`;
- stable C++ shell owns AE registration;
- existing Rust host is packaged as `libstellar_gradient_impl.dylib`;
- implementation key: `stellar-gradient`;
- hot-reload staging script added;
- shell ABI validation and bundled fallback enabled;
- original support URL metadata retained.

Verified:

- dedicated macOS Hot Loader Shell CI: **SUCCESS**;
- implementation build: **SUCCESS**;
- shell bundle/signing: **SUCCESS**;
- real shell-reload smoke: **SUCCESS**.

### Remaining live gate

No further private-loader/PiPL research is required.

The next required evidence must come from a real After Effects 25.6 process:

1. install the current AE Hot Loader control shell + Agent package;
2. restart AE once;
3. confirm the control shell appears through normal native registration;
4. stage `candidate-v2` while AE remains open;
5. click **Reload Plugins**;
6. confirm the Agent finds one loaded shell and reports `reloaded=1`;
7. render/use the existing effect instance after the swap;
8. repeat Reload without a new candidate and confirm `unchanged=1`.

After that passes, run the equivalent live gate for ElasticGrid and Stellar Gradient. No merge to `main` before these runtime gates pass.

