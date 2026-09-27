# AE Hot Loader — macOS PoC

Experimental proof-of-concept for loading/registering a new native After Effects effect while AE is already running.

## Current target

- macOS
- Apple Silicon (arm64)
- After Effects native effect plug-ins
- no Windows work until the macOS stop criterion passes

## Stop criterion

1. Start After Effects with `AEHotLoader.plugin` installed.
2. Apply **AE Hot Loader** to a layer.
3. Click **Register Late Effect**.
4. Without restarting AE, **AE Hot Loader Late Effect** appears in the Effect menu.
5. Apply the late effect and confirm it renders correctly.

If this fails, the public registration callback is not sufficient for live registration and the next phase is internal-loader investigation.

## Architecture

- `wrapper/AEHotLoader.cpp`
  - actual bundle executable loaded by AE
  - captures `PF_PluginDataPtr` + `PF_PluginDataCB2`
  - registers the normal effect at startup
  - exposes a late-registration bridge
  - forwards `EffectMain` / `LateEffectMain` to the Rust core
- `core/`
  - SDK-less effect implementation using the Rust `after-effects` stack
  - contains a **Register Late Effect** button
  - passes frames through unchanged
- `.github/workflows/mac-ci.yml`
  - builds ARM64 bundle
  - checks exports and plist
  - ad-hoc signs the bundle
  - produces a ready-to-test ZIP artifact

## Safety

The late-registration path is experimental. It does not unload effects and allows only one late-registration attempt per AE process.
