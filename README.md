# AE Hot Loader

A dockable After Effects tool for discovering and loading newly installed native effect plug-ins without restarting After Effects.

## Product UX

The user-facing product is **not an Effect plug-in**.

It is a dockable ScriptUI panel:

`Window → AE Hot Loader`

with one main action:

**Reload Plugins**

The native code exists only as a background technical bridge. It must not be part of the normal Effect workflow.

## Current target

- macOS
- Apple Silicon (arm64)
- After Effects native effect plug-ins
- no Windows work until macOS feasibility is proven

## Current status

The repository contains:
- a working macOS ARM64 build pipeline;
- a temporary native PoC proving access to AE's effect-registration callback;
- a ScriptUI product shell;
- a command bridge protocol between ScriptUI and the native helper.

The current native Effect implementation is **temporary PoC code only**. The production architecture must hide the native bridge from normal users.

## Final architecture

`ScriptUI panel → command bridge → hidden native helper → AE loader/registry → new .plugin`

The panel handles UX. The native helper handles host-level registration and dynamic loading.

## Stop criterion

1. After Effects is already running.
2. User installs a new native `.plugin`.
3. User clicks **Reload Plugins** in the docked AE Hot Loader panel.
4. The new effect appears in AE without restarting.
5. It can be applied and rendered correctly.

## Safety

The loader will not unload active plug-ins. Unsupported plug-ins must fail safely and report a clear status instead of crashing AE.
