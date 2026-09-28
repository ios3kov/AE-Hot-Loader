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

## Shell architecture implementation status — 2026-09-28

Production shell architecture is implemented on `feature/internal-loader-agent`.

### Hardened runtime contract

Current shell protocol:

- Protocol ABI: **2**
- implementation key validation;
- explicit StateABI;
- explicit Runtime ABI;
- `AEHotLoader_SetGeneration` before candidate publication;
- content fingerprint generation;
- bundled implementation is always the process ABI baseline;
- external `current.dylib` cannot become the session baseline by merely existing;
- old implementation images stay loaded until AE exits;
- maximum 64 retained generations per shell/process.

For Rust implementations, Runtime ABI includes:
- exact rustc/toolchain identity;
- target triple;
- pinned `after-effects` dependency family/revision.

Hot-reload builds are pinned to Rust **1.98.1**.

### Concurrency / MFR hardening

The shell tracks active EffectMain calls and a pending swap state.

Rules:

1. concurrent MFR calls remain concurrent;
2. reload never waits indefinitely for a render;
3. if any call is active, reload returns busy/retry;
4. candidate pointer publication happens only with zero active calls;
5. C++ exceptions are contained inside every exported C ABI boundary.

### Persistent state hardening

ElasticGrid and Stellar Gradient adapter StateABI is currently **4**.

Their state-contract gates freeze:
- parameter IDs/order;
- custom/wire-format state where applicable;
- SmartFX pre-render payloads;
- GPU/native state layout;
- generation field;
- old-generation native destroy-function pointer.

The shell assigns a fingerprint-derived generation to every accepted implementation. GPU/native state created by an older generation is not blindly reused by newer code.

### Rollback behavior

Verified behavior:

- invalid key/ABI/runtime ABI candidate is rejected;
- active implementation remains unchanged;
- malformed/unterminated ABI strings are rejected;
- removing an external candidate reloads the bundled default;
- unchanged reload does not consume a generation.

### Agent / installer hardening

The production Agent:
- no longer links or calls private `ML::LoadPlugins`;
- discovers already loaded shells through dyld;
- calls only `AEHotLoader_ShellReload`;
- reports per-shell reloaded / unchanged / failed state.

Installer:
- refuses updates while AE is running;
- scans system/user/app plug-in roots for duplicate Loader copies;
- validates signatures and arm64 architecture;
- backs up managed plug-ins and restores them on install failure;
- clears stale bridge files and staged control candidates.

### CI evidence

AE Hot Loader:
- direct shell reload smoke;
- Agent dyld discovery → shell reload smoke;
- MFR busy-swap stress;
- invalid key/ABI rollback;
- Runtime ABI mismatch rejection;
- malformed ABI-string rejection;
- bundled default → candidate;
- candidate removal → bundled rollback.

Latest known green checkpoint:
**AE Hot Loader run #218 — SUCCESS**.

ElasticGrid adapter:
- dedicated shell CI;
- PiPL ↔ shell metadata parity;
- state-contract verifier;
- pinned Rust toolchain;
- default + candidate binary kit;
- deployment target and dylib dependency checks;
- bundled default → candidate → unchanged → bundled rollback;
- full project GCC / Clang / ASan+UBSan / TSan / static-analysis gates.

Latest stable green checkpoint before the current state-contract extension:
**Hot Loader Shell CI #48 — SUCCESS** and full project CI #126 — SUCCESS.
The newest verifier run must also be green before live AE installation.

Stellar Gradient adapter:
- dedicated shell CI;
- PiPL ↔ shell metadata parity;
- exact parameter-ID freeze;
- `ParamsC`, `RenderStateC`, and GPU context state-contract verifier;
- pinned Rust toolchain;
- default + candidate binary kit;
- deployment target and dylib dependency checks;
- bundled default → candidate → unchanged → bundled rollback.

Latest stable green checkpoint before the current params/PiPL contract extension:
**Hot Loader Shell CI #66 — SUCCESS**.
The newest verifier run must also be green before live AE installation.

### Remaining live gate

No further private-loader/PiPL reverse-engineering is required.

Before merge to `main`, real After Effects 25.6 must prove:

1. Control shell registers through normal AE startup.
2. Bundled default applies and renders.
3. Candidate reload reports success through the Agent/panel path.
4. Existing instance renders after swap.
5. Unchanged reload reports unchanged.
6. Busy render returns retry instead of hanging AE.
7. Removing the candidate rolls back to bundled default.
8. ElasticGrid passes CPU, custom UI, MFR, GPU smoke.
9. Stellar Gradient passes CPU, SmartFX, MFR, GPU smoke.
10. Existing GPU/native state survives/reinitializes safely across generation changes.
11. Repeated A→B→C reloads remain stable.
12. Project save/reopen remains compatible.
13. No duplicate Agent/shell copies are discovered.

See `docs/CODE_AUDIT_2026-09-28.md` for the full audit and rationale.

No merge to `main` before these live gates pass.

