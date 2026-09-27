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

On After Effects 25.6.0 the effect bridge loads correctly and captures the registration callback.

A previous direct late-registration call reached AE but returned code `1`, so the public callback may reject registration after startup. The two-module AEGP build is intended to confirm this cleanly from the panel.

## Stop criterion

AE already running → click **Reload Plugins** → late test effect appears and can be applied/rendered → no AE restart.

If AE again returns code `1`, the public callback route is considered blocked and the next research phase is the internal AE loader/registry.

## Platform

Current target: macOS Apple Silicon only.
