# AE Hot Loader — Code Audit

Date: 2026-09-28  
Scope:
- `ios3kov/AE-Hot-Loader` — `feature/internal-loader-agent`
- `ios3kov/ElasticGridFX` — `feature/ae-hot-loader-shell`
- `ios3kov/stellar-gradient` — `feature/ae-hot-loader-shell`

No merge to `main` is allowed before the real After Effects runtime gates pass.

## Audit result

The previous private-loader registration path is no longer the production architecture.

The production path is now:

```
AE startup registration
→ stable effect shell
→ versioned implementation dylib
→ Agent discovers loaded shells
→ validated nonblocking implementation swap
```

Static/CI review found multiple issues before live AE testing. They were fixed in the feature branches.

## High-risk findings fixed

### 1. Reload during MFR / render calls

Risk:
a candidate could be published while an older `EffectMain` call was still executing, allowing two implementation generations to touch the same AE-owned state concurrently.

Fix:
- reentrant-safe `active_calls + swap_pending` generation gate;
- MFR calls remain concurrent with each other;
- reload never blocks waiting for render completion;
- when an effect is busy, reload returns a retryable busy error;
- CI has a concurrent busy-swap stress test.

### 2. C++ exceptions crossing C ABI

Risk:
exceptions from filesystem/string/allocation code in the shell or native Agent helper could escape into After Effects.

Fix:
- exception barriers around shell exports;
- exception barrier around native Agent shell enumeration.

### 3. Incompatible implementation activation

Risk:
a dylib for another effect, another shell protocol or an incompatible state layout could be activated.

Fix:
every implementation must export and pass:
- `AEHotLoader_ImplementationABI`;
- `AEHotLoader_ImplementationStateABI`;
- `AEHotLoader_ImplementationKey`;
- `AEHotLoader_ImplementationLabel`;
- `EffectMain`.

A failed candidate never updates the active function pointer/fingerprint.

### 4. Unsafe unload inside a live AE process

Risk:
`dlclose` may execute candidate destructors/unload code while AE is running.

Fix:
after a successful `dlopen`, mapped candidate images are retained until process exit, including rejected candidates. A per-session generation cap bounds memory growth.

### 5. Unbounded reload generations

Risk:
intentional retention of implementation dylibs could grow process memory indefinitely during a very long development session.

Fix:
hard cap of 64 mapped implementation generations per shell/session. AE restart is required after the cap.

### 6. Runtime image path collisions

Risk:
duplicate copies of the same shell could stage runtime dylibs under the same PID/ordinal name.

Fix:
runtime filenames include the loaded shell image identity plus generation ordinal.

### 7. Weak change detection

Risk:
mtime/size can miss rebuilt binaries.

Fix:
change detection fingerprints the staged binary contents.

### 8. Unsafe runtime staging location

Risk:
a global temporary directory gives weaker isolation and predictable paths.

Fix:
runtime dylibs are staged under the current user's `TMPDIR`, with a per-process directory.

### 9. Stale / duplicate plug-ins

Risk:
multiple Agents or multiple effect bundles with the same match name can produce duplicate registration/hooks and undefined reload behavior.

Fix:
- central installer scans standard Adobe system/user roots and AE app Plug-Ins for duplicate Loader bundles;
- effect installers scan standard roots for duplicate ElasticGrid/Stellar bundles;
- modifying a plug-in inside the signed Adobe application bundle is refused.

### 10. Backups inside Adobe scan roots

Risk:
renaming an old effect beside the new one could still leave a scan-visible bundle-like directory.

Fix:
effect backups are stored outside Adobe plug-in roots under:
`~/Library/Application Support/AE Hot Loader/backups/`.

### 11. Partial installation / rollback

Risk:
failed copy/signature verification could leave no working effect.

Fix:
effect installers:
- validate the source bundle before mutation;
- backup the old bundle;
- remove partial installs on failure;
- restore the backup when one exists;
- verify the installed bundle before success.

### 12. Architecture/signature mistakes

Risk:
wrong-architecture or damaged binaries could be staged or installed.

Fix:
- installers verify code signatures and arm64 architecture;
- candidate staging verifies source signature/architecture;
- final staged `current.dylib` is verified again.

### 13. Stale bridge requests

Risk:
an incomplete/malformed request file could be reread on every AEGP idle callback forever.

Fix:
- request size is capped;
- malformed/incomplete requests are discarded;
- invalid request IDs are discarded;
- idle polling reduced to 250 ms.

### 14. Missing shells reported as success/no-op

Risk:
Agent can be alive while AE failed to load any shell, but the panel previously displayed this as a harmless noop.

Fix:
`shells=0` is now an explicit error.

## Metadata audit

Current PiPL/build metadata and stable shell registration metadata match for all three effects.

### Control shell
- name: `AE Hot Loader Control Shell`
- category: `AE Hot Loader`
- match name: `OS3KOV.AEHotLoader.ControlShell`
- AE spec: 13.29

### ElasticGrid
- name/category: `ElasticGrid FX`
- match name: `com.elasticgrid.fx.warp`
- AE spec: 13.28
- support URL preserved

### Stellar Gradient
- name: `Stellar Gradient`
- category: `Stellar`
- match name: `StellarLabs.StellarGradient`
- AE spec: 13.29
- support URL preserved

## Automated gates

AE Hot Loader CI covers:
- Rust/C++ static checks;
- Agent build;
- shell build/signature;
- implementation ABI exports;
- direct shell reload;
- Agent dyld shell discovery;
- concurrent MFR busy-swap stress;
- incompatible-candidate rollback;
- unchanged-build detection;
- package creation.

ElasticGrid gates cover:
- portable GCC/Clang;
- ASan/UBSan;
- TSan;
- static analysis;
- native shell build;
- implementation ABI exports;
- shell bundle verification;
- hot-reload smoke;
- packaged default/candidate kit.

Stellar Gradient gates cover:
- shell static checks;
- Rust host build;
- implementation ABI exports;
- shell signing/bundle validation;
- hot-reload smoke;
- packaged default/candidate kit.

## Risks that cannot be closed without a real AE 25.6 process

These are the remaining release blockers.

### AE lifecycle
Verify normal AE calls through the shell:
- registration;
- GlobalSetup;
- ParamsSetup;
- apply effect;
- render;
- GlobalSetdown.

### Existing instance across reload
An effect already applied to a layer must continue working after A → B implementation swap.

### MFR in real AE
CI tests the shell concurrency gate, but the host's real Multi-Frame Rendering scheduling must be exercised.

### GPU / Metal lifecycle
For ElasticGrid and Stellar Gradient verify:
- GPU device setup before reload;
- render after reload;
- GPU device setdown after reload;
- no invalid interpretation of retained GPU state.

The state ABI contract protects intended compatibility, but only AE can exercise the real host-owned GPU lifecycle.

### SmartFX transient data
Verify pre-render/render sequencing around a reload in a real project.

### ScriptUI host permission
The panel's file bridge must be tested under the user's actual AE scripting/file-access preference.

## Release decision

Code/CI audit is not a substitute for the real host gate.

Current rule:

**Do not merge to main and do not call the product finished until the real AE 25.6 control-shell, ElasticGrid and Stellar Gradient runtime gates pass.**
