# AE Hot Loader — Production Plan

## Product definition

AE Hot Loader is a **tool panel**, not an Effect plug-in.

User-facing surface:
- dockable ScriptUI panel;
- opened from `Window → AE Hot Loader`;
- main control: **Reload Plugins**;
- optional Auto Watch later.

A native component may exist internally, but only as a hidden technical bridge required to access After Effects' plug-in loader.

## Architecture

`ScriptUI Panel → request file / bridge → native helper inside AE → loader/registry → newly installed .plugin`

### ScriptUI panel

Responsibilities:
- provide the visible button;
- show status: scanning / loaded / failed;
- write reload requests to the bridge;
- read the native helper response;
- never require adding an effect to a layer.

### Native helper

Responsibilities:
- stay loaded inside the AE process;
- detect reload requests;
- scan Adobe/MediaCore plug-in folders;
- load candidate bundles;
- invoke host registration;
- return structured success/error results.

The current effect-based helper is a **temporary feasibility PoC**, not the production UX.

## Phase 1 — UX + bridge shell

1. Build dockable ScriptUI panel.
2. Define request/response protocol.
3. Panel writes a reload request.
4. Native helper detects request and writes a response.
5. Validate that the UI works without applying any effect.

## Phase 2 — late-registration proof

1. Capture the host effect-registration callback during startup.
2. Keep the helper resident.
3. Trigger a second registration only through the ScriptUI request.
4. Confirm the new effect appears without AE restart.
5. Remove the need to press a parameter button on an Effect instance.

### Stop criterion A

AE is running → click **Reload Plugins** in ScriptUI → test effect appears → applies → renders → no AE restart.

If this fails, stop the public-callback approach and investigate the internal loader.

## Phase 3 — external plug-in loading

1. Scan standard Adobe/MediaCore plug-in locations.
2. Detect newly added `.plugin` bundles.
3. Load bundle executable with the macOS dynamic loader.
4. Resolve `PluginDataEntryFunction2` / entry point.
5. Register using the proven host context.
6. Verify menu visibility and application.

## Phase 4 — production hidden helper

The final native bridge must not appear as a normal user Effect.

Candidate implementations:
- background AEGP/general plug-in bridge;
- minimal resident loader module;
- internal AE loader hook if the public registration callback cannot support the hidden-helper design.

The implementation chosen must satisfy:
- no effect needs to be applied to a layer;
- no visible "AE Hot Loader" effect in normal use;
- panel works immediately after AE startup.

## Phase 5 — compatibility

Test:
- CPU effects;
- SmartFX;
- Metal/GPU effects;
- custom UI;
- licensing frameworks;
- embedded dylibs/frameworks;
- signed/notarized bundles.

## Phase 6 — product UX

- Reload Plugins button;
- Auto Watch;
- loaded/failed plug-in list;
- compatibility status;
- logs;
- blacklist;
- recovery after failed load.

## Platform order

1. macOS Apple Silicon
2. macOS Intel only if still useful
3. Windows only after macOS feasibility is proven


## Verified build status — 2026-09-27

The ScriptUI + idle-hook architecture compiles successfully on the macOS ARM64 CI runner.

Verified:
- Rust effect core build;
- RegisterNonAegp idle hook compilation;
- native wrapper build;
- plug-in bundle assembly;
- ad-hoc code signing;
- ScriptUI panel validation;
- test-kit packaging.

Next validation is inside a real running After Effects process:
1. install the package;
2. restart AE once for the initial helper installation;
3. open `Window → AE Hot Loader`;
4. click **Reload Plugins**;
5. confirm the late test effect appears without another AE restart.


## Architecture revision — AEGP Agent + Effect Bridge

Live testing showed that registering an AEGP idle hook from the effect plug-in startup context fails with internal result `-1102`.

The PoC is therefore split into two native modules:

1. `AEHotLoaderAgent.plugin` — genuine AEGP loaded by AE at application startup. It owns the idle hook and handles ScriptUI requests.
2. `AEHotLoaderBridge.plugin` — internal effect bridge that captures `PF_PluginDataCB2` and exposes the experimental late-registration call.

Flow:

`ScriptUI → request.txt → AEGP Agent idle hook → dlopen Effect Bridge → AEHotLoader_RegisterLateEffect → response.txt → ScriptUI`

Observed on AE 25.6.0:
- primary effect registration: `0` (success);
- effect bridge/core load: success;
- direct late registration callback: `1` (rejected/non-success);
- AEGP-from-effect startup attempt: `-1102` (unsupported context).

The standalone AEGP Agent + Effect Bridge build passes macOS ARM64 CI, static checks, code signing, bundle validation, and ScriptUI packaging.


## Live test finding — bridge path lookup

Panel result `Native bridge failed with code -2002` confirmed that:
- the ScriptUI panel worked;
- the AEGP Agent was alive and processing requests;
- failure was only the Agent's hard-coded filesystem lookup for `AEHotLoaderBridge.plugin`.

The Agent was updated to:
1. resolve `AEHotLoader_RegisterLateEffect` from the current AE process;
2. if not found globally, inspect loaded dyld images;
3. locate the actual loaded `AEHotLoaderBridge` image regardless of install path;
4. open that already-loaded image and call the exported registration bridge.

This removes dependence on a fixed MediaCore path.


## Internal loader ABI finding — 2026-09-27

LLDB on After Effects 25.6.0 ARM64 confirmed the host-owned registration transaction:

`ML::LoadPlugins → LoadPluginList → AddPlugin → PluginImpl::GetPiPLs → GetPFPluginData → GetEntryPoint → dlsym("PluginDataEntryFunction2")`.

Observed `ML::LoadPlugins` ABI:

`ML::LoadPlugins(vector<UTF16String>&, UTF16String const&, ModuleOwnership, vector<UTF16String> const&, vector<UTF16String> const&, bool)`

ARM64 entry registers:
- `x0` output vector;
- `x1` root UTF16String;
- `w2 = 1`;
- `x3` filter vector;
- `x4` additional vector;
- `w5 = 0`.

The next gate is a stable image-relative offset for `ML::LoadPlugins` on AE 25.6.0 ARM64. Only after that is captured do we build the isolated internal-loader shim. Runtime ASLR addresses must not be embedded in production code.


## Live-test kit status — 2026-09-27

The isolated `experiment/internal-loader-probe` branch has passed CI with a packaged one-command live-test setup.

Current gate:
- keep production Agent unchanged;
- run `PREPARE_LIVE_TEST.command`;
- invoke `AEHotLoader_InternalLoaderProbe("/tmp/AEHotLoaderProbe")` on the AE main thread;
- confirm the new test effect appears, can be applied, and renders without restarting AE.

Only after this succeeds should the private loader path be integrated into the production Agent.


## Live internal-loader proof — 2026-09-27

A live test on After Effects 25.6.0 ARM64 successfully invoked AE's own `ML::LoadPlugins` after startup against a dedicated test folder.

Verified:

- `ML::LoadPlugins` resolved from `PluginSupport.framework`;
- return value: `1`;
- test bundle loaded from `/private/tmp/AEHotLoaderProbe`;
- effect A registration result: `0`;
- effect B registration result: `0`.

This is the first successful proof that a new native effect bundle can enter AE's real loader/registration transaction while AE is already running.

Remaining gate before integration into the production Agent:
- effect menu visibility;
- apply to layer;
- GLOBAL_SETUP / PARAMS_SETUP;
- render;
- stability after resume.

Production integration remains blocked until those checks pass.


## Live menu/apply verification — 2026-09-27

The live internal-loader test progressed beyond registration:

- both late-loaded effects appeared in the running AE Effects & Presets panel;
- both effects were successfully applied to a layer;
- AE was not restarted.

The remaining stop-criterion checks are render-path verification and stability.


## Stop Criterion A — PASSED — 2026-09-27

Live verification on After Effects 25.6.0 ARM64 is complete.

Without restarting AE:

- a new native effect bundle was loaded through `ML::LoadPlugins`;
- both test effects registered;
- both appeared in Effects & Presets;
- both applied successfully;
- RAM Preview succeeded;
- normal render succeeded;
- AE remained stable.

The diagnostic effects are pass-through and intentionally produce no visible image change.

### Production direction

Proceed with integration of the proven private loader path into `AEHotLoaderAgent.plugin`.

Target flow:

`ScriptUI Reload Plugins → AEGP Agent → detect new bundles → ML::LoadPlugins → AE registry/menu`

The temporary saved-callback Effect Bridge path is no longer the preferred production route.


## Production Agent integration — 2026-09-27

The proven private loader path is now integrated into `AEHotLoaderAgent.plugin` on branch `feature/internal-loader-agent`.

Implemented:
- native `ML::LoadPlugins` shim linked directly into the AEGP Agent;
- startup snapshot of existing `.plugin` bundles;
- recursive scan of standard Adobe / MediaCore locations;
- detection of newly added or changed `.plugin` bundles;
- grouped folder reload through AE's own internal loader;
- ScriptUI `Reload Plugins` request routed directly to the Agent;
- 30-second UI timeout for real folder rescans;
- Effect Bridge removed from the production install/package path.

CI run #46 passed fully on macOS ARM64.

### Next live gate

1. install the Agent-only package;
2. restart AE once to load the updated Agent;
3. copy a new test `.plugin` into a scanned plug-in folder while AE stays open;
4. click `Reload Plugins`;
5. verify the new effect appears and renders without another restart.

Do not merge to `main` until this live button-driven flow passes.
