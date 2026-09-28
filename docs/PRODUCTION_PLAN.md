# AE Hot Loader — Production Plan

## Ordinary-plugin discovery milestone — 2026-09-28

The original workflow is now proven on After Effects 25.6.0 ARM64:

1. AE remains open in one process.
2. A previously absent ordinary `.plugin` bundle is placed in an isolated
   plug-in root.
3. The Agent-native loader invokes `ML::LoadPlugins`.
4. The newly created `IVideoFilterModule` is passed to
   `FLT_NotifyFilterLoadingDone`, matching AE's startup completion path.
5. The Installed Effects Registry changes from `783` to `784`.
6. The new effect can be added to a layer and rendered to a valid `128×128`
   PNG in the same process.

The production Agent now scans the standard Adobe plug-in roots and reports
the post-load module count for each pass. Effects Registry identity is checked
separately because AE may recreate private module objects on a repeat scan.
The private ABI is currently
gated to AE 25.6 arm64 and must be revalidated for other host versions.

Evidence is retained under the local ordinary-discovery test workspace. The
Rust probe produced `canAdd=true`, applied with one parameter, and exported a
valid `128×128` PNG (`14,323` bytes). The probe is intentionally a one-shot
diagnostic effect; AE disables it after the first render, so later attempts in
the same process are not treated as independent passes.

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

Production supports ordinary native plug-in discovery after AE startup. A
separate stable-shell workflow remains available for implementation reloads.

## Final architecture

```
ScriptUI panel
    ↓ request/response
AEGP Agent
    ↓ scan Adobe plug-in roots
ML::LoadPlugins + FLT notification
    ↓
ordinary effect module in AE registry
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
- scan standard Adobe plug-in roots;
- invoke ordinary discovery and post-load registration;
- collect loaded and post-load module counts;
- return concise status to the panel;
- keep diagnostics/logging.

The Agent must not depend on applying an internal effect to a layer.

## Research path — completed for production

The project investigated:
- saved `PF_PluginDataCB2`;
- direct late registration;
- internal `ML::LoadPlugins`;
- isolated runtime staging;
- registry diagnostics;
- Rust/C++ single- and multi-PiPL controls.

The first loader-only experiment established that binary loading and a
registration callback result of `0` do not by themselves imply insertion into
AE's Installed Effects Registry after startup. The completed path adds the
missing video-filter module notification.

Therefore:

- private `ML::LoadPlugins` is used only together with the version-gated
  post-load filter notification;
- UI refresh hacks are abandoned;
- runtime registration of a brand-new ordinary effect is the primary release
  requirement for the current milestone.

## Implementation phases

### Phase 1 — control shell

1. Convert the existing bridge wrapper into a stable control shell.
2. Register it normally at AE startup.
3. Move behavior behind an implementation dylib.
4. Export `AEHotLoader_ShellReload`.
5. Reload by loading a uniquely staged dylib and atomically swapping the implementation pointer.
6. Keep old dylib handles alive until AE exits.

**Gate:** repeated implementation swaps work without restarting AE.

### Phase 2 — ordinary discovery Agent integration

1. Scan the standard Adobe plug-in roots.
2. Invoke the AE private loader on the idle/main path.
3. Snapshot and diff video-filter modules.
4. Notify AE of newly loaded modules.
5. Return loaded and newly registered counts.

**Gate:** one panel click adds a newly installed ordinary effect without an AE
restart.

### Phase 3 — stable-shell implementation reload

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
- **automatic cache invalidation / fresh evaluation after successful reload**;
- no manual Edit → Purge step in normal use;
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
- links the version-gated ordinary discovery helper;
- scans system/user/app plug-in roots;
- calls `ML::LoadPlugins` followed by `FLT_NotifyFilterLoadingDone`;
- reports loaded and post-load module counts.

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
**AE Hot Loader run #236 — SUCCESS**.

ElasticGrid adapter:
- dedicated shell CI;
- PiPL ↔ shell metadata parity;
- state-contract verifier;
- pinned Rust toolchain;
- default + candidate binary kit;
- deployment target and dylib dependency checks;
- bundled default → candidate → unchanged → bundled rollback;
- full project GCC / Clang / ASan+UBSan / TSan / static-analysis gates.

Latest green checkpoints:
**Hot Loader Shell CI #60 — SUCCESS** and full project CI **#139 — SUCCESS**.

Stellar Gradient adapter:
- dedicated shell CI;
- PiPL ↔ shell metadata parity;
- exact parameter-ID freeze;
- `ParamsC`, `RenderStateC`, and GPU context state-contract verifier;
- pinned Rust toolchain;
- default + candidate binary kit;
- deployment target and dylib dependency checks;
- bundled default → candidate → unchanged → bundled rollback.

Latest fully green shell checkpoint: **Hot Loader Shell CI #70 — SUCCESS**.
A later dependency-lock hardening run (#73) failed because of a malformed committed Cargo checksum and must be repaired before the Stellar live package is used.

### Current live status and remaining gate

No further private-loader/PiPL reverse-engineering is required.

**Control Shell: PASSED in real AE 25.6.** Registration, A→B→C, real rendering, unchanged/no-op, deterministic busy rejection, rollback, and post-rollback render are all proven without restarting AE.

Manual cache Purge was used only to force cache misses during proof. Normal product usage must automatically invalidate stale cached output after a successful reload.

Before merge to `main`, the remaining real-AE work is:

1. ElasticGrid passes CPU, custom UI, Smart Render/MFR, GPU, A→B→C, rollback, save/reopen.
2. Stellar Gradient passes CPU, SmartFX, MFR, GPU, A→B→C, rollback, save/reopen.
3. Existing GPU/native state survives/reinitializes safely across generation changes.
4. Successful reload automatically invalidates stale cached output; no manual Purge is needed.
5. No duplicate Agent/shell copies or duplicate match-name installations remain.

See `docs/CODE_AUDIT_2026-09-28.md` for the full audit and rationale.

No merge to `main` before these live gates pass.
