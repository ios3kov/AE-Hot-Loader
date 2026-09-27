# AE Hot Loader

Dockable After Effects tool for experimentally loading/registering newly installed native effects without restarting After Effects.

## User-facing UX

The visible product is a ScriptUI panel:

`Window → AE Hot Loader`

Main action:

**Reload Plugins**

The native components are internal implementation details.

## macOS PoC architecture

`ScriptUI Panel → AEGP Agent → Effect Bridge → AE registration callback`

### AEHotLoaderAgent.plugin
- genuine AEGP/general plug-in;
- starts automatically with After Effects;
- registers an idle hook;
- listens for requests from the ScriptUI panel;
- calls the effect bridge inside the AE process;
- writes a response back to the panel.

### AEHotLoaderBridge.plugin
- temporary internal effect plug-in used only to capture AE's `PF_PluginDataCB2` registration callback during startup;
- exports `AEHotLoader_RegisterLateEffect`;
- is not part of the intended user workflow.

### ScriptUI panel
- contains the **Reload Plugins** button;
- never needs an effect applied to a layer;
- communicates with the agent through the bridge request/response files.

## Current research result

The saved `PF_PluginDataCB2` route is considered blocked: a late call was rejected and a deferred call after `PluginDataEntryFunction2` returned crashed AE.

LLDB tracing on After Effects 25.6 ARM64 identified the native loader transaction:

`LoadAllPlugins → ML::LoadPlugins → LoadPluginList → AddPlugin → PluginDataEntryFunction2`

The current experiment branch contains an isolated `internal_loader_probe` that resolves `ML::LoadPlugins` from the loaded `PluginSupport.framework` symbol table and calls it only for a dedicated `/tmp/AEHotLoaderProbe` folder on the AE main thread. Production Agent behavior is unchanged.

## Stop criterion

AE already running → click **Reload Plugins** → late test effect appears and can be applied/rendered → no AE restart.

The next stop criterion is narrower: while AE is already running, the internal-loader probe scans only the dedicated test folder and the newly copied native effect becomes registered and usable without restarting AE.

## Platform

Current target: macOS Apple Silicon only.
