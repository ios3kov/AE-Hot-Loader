# AE Hot Loader — Code Audit

Date: 2026-09-28  
Branch: `feature/internal-loader-agent`

Related adapter branches:
- `ios3kov/ElasticGridFX / feature/ae-hot-loader-shell`
- `ios3kov/stellar-gradient / feature/ae-hot-loader-shell`

## Scope

This audit covers the production shell architecture before the first live After Effects 25.6 runtime gate.

Reviewed areas:

- shell / implementation ABI;
- MFR and concurrent EffectMain execution;
- implementation swap semantics;
- persistent Rust/global/sequence/GPU state;
- SmartFX pre-render payload compatibility;
- dylib staging and change detection;
- rollback and failed candidate behavior;
- C/C++ ABI boundaries;
- Agent shell discovery;
- ScriptUI request/response bridge;
- duplicate plug-in installation;
- signing / architecture / deployment-target checks;
- ElasticGrid and Stellar Gradient adapters;
- CI coverage.

## Audit conclusion

The earlier private `ML::LoadPlugins` path is not used in production.

The production design is now:

```
After Effects startup
    ↓
stable registered shell .plugin
    ↓
bundled default implementation dylib
    ↓
AE Hot Loader Agent
    ↓
validated candidate implementation
    ↓
generation-safe pointer publication
```

The architecture is ready for a **live AE runtime gate**, but is not yet release-approved until that gate passes.

## Findings and fixes

### 1. CRITICAL — reload could overlap an active MFR/render call

Risk:

A pointer swap while old EffectMain calls are still executing can let two implementation generations touch the same AE/native state.

Fix:

- per-shell active-call counter;
- swap-pending generation gate;
- concurrent MFR calls remain allowed;
- final publication happens only with zero active calls;
- Reload does not block AE waiting for a render;
- when busy, Reload returns a retry error.

CI:

- MFR busy-swap stress smoke;
- candidate is rejected while a simulated render is active;
- same candidate succeeds after the active call finishes.

### 2. HIGH — mtime + file size was not sufficient change detection

Risk:

A rebuild can produce different dylib bytes with unchanged size and timestamp granularity.

Fix:

- fingerprint the exact uniquely staged dylib bytes;
- unchanged detection uses the content fingerprint;
- the same fingerprint is also used as the implementation generation identity.

### 3. CRITICAL — C++ exceptions could cross a C ABI boundary

Risk:

An exception escaping `EffectMain`, `PluginDataEntryFunction2`, shell reload, or native Agent reloader into AE is undefined behavior.

Fix:

- exception barriers around exported shell entry points;
- exception barrier around the Agent native shell enumerator;
- explicit negative error codes returned instead.

### 4. CRITICAL — stale external candidate could become the process baseline

Risk:

A leftover `current.dylib` from another build/toolchain could be loaded before the bundled implementation and silently define the session state/runtime ABI.

Fix:

- first implementation load always comes from the shell bundle;
- external candidate is accepted only through Reload;
- installer clears stale staged candidates;
- removing a candidate rolls back to the bundled implementation.

CI:

- bundled-default → candidate → unchanged;
- candidate removal → bundled rollback → unchanged.

### 5. CRITICAL — Rust runtime ABI drift

Risk:

Rust does not guarantee stable layout/ABI for opaque runtime data across compiler/library versions. AE can retain global/sequence/GPU-facing state across EffectMain calls.

Fix:

Required implementation export:

`AEHotLoader_ImplementationRuntimeABI`

The value includes the exact Rust compiler/toolchain identity, target triple and pinned `after-effects` dependency family/revision.

Rules:

- bundled implementation establishes the session Runtime ABI;
- candidate Runtime ABI must match;
- hot-reload toolchain is pinned to Rust **1.98.1**;
- mismatch is rejected without losing the active implementation.

CI:

- explicit runtime-ABI mismatch negative test.

### 6. CRITICAL — persistent GPU state could belong to an older dylib generation

Risk:

After hot swap, AE may retain Metal/native state created by the old implementation. New code must not blindly reinterpret or destroy that resource.

Fix:

Protocol ABI v2 adds:

`AEHotLoader_SetGeneration(u64)`

The shell assigns a fingerprint-derived generation before publishing the candidate.

ElasticGrid and Stellar Gradient GPU state now retain:

- creating generation;
- old-generation native destroy function pointer.

This allows:

- stale GPU state detection;
- CPU fallback / GPU rejection when generation is stale;
- destruction by code belonging to the generation that created the native resource;
- old implementation dylibs remain loaded until AE exits.

Adapter StateABI is now **4** for both ElasticGrid and Stellar Gradient.

### 7. HIGH — parameter / persistent-state schema drift was manual-only

Risk:

Changing Params, SmartFX pre-render data, GPU state, or serialized/custom parameter state without bumping StateABI can make an otherwise valid reload unsafe.

Fix:

Dedicated state-contract verifiers now freeze:

ElasticGrid:
- parameter list/order;
- GridArb wire version;
- GPU state layout;
- protocol ABI;
- StateABI;
- generation/destroy-function evidence.

Stellar Gradient:
- exact parameter IDs;
- `ParamsC`;
- `RenderStateC` SmartFX pre-render payload;
- `GpuContext`;
- protocol ABI;
- StateABI;
- generation/destroy-function evidence.

Any intentional schema change must update the verifier and StateABI together.

### 8. HIGH — PiPL / shell registration metadata could drift

Risk:

PiPL resources and manual shell registration callback may advertise different name/category/match-name/API metadata.

Fix:

Adapter CI compares build.rs PiPL metadata against shell registration metadata.

This is mandatory for both ElasticGrid and Stellar Gradient.

### 9. HIGH — duplicate plug-ins could create duplicate Agent hooks / duplicate match names

Risk:

Multiple copies in system/user MediaCore, Adobe Plug-Ins or app plug-in directories can cause duplicate Agent idle hooks or multiple effects with the same match-name.

Fix:

AE Hot Loader installer:
- refuses install while AE is running;
- scans known system/user/app plug-in roots;
- rejects unmanaged duplicate Loader bundles and bundle IDs;
- replaces only the managed user copy;
- verifies signature and arm64 architecture;
- keeps rollback backups.

ElasticGrid/Stellar test-kit installers:
- locate existing named bundle;
- refuse ambiguous multiple copies;
- replace the existing bundle in place;
- create backup and restore on failed install;
- clear stale staged implementation.

### 10. HIGH — installer failure could leave the installation half-replaced

Fix:

- pre-install backup;
- post-copy signature verification;
- automatic restore on failure;
- bridge request/response cleanup;
- stale candidate cleanup.

### 11. MEDIUM — unbounded retained dylib generations

Risk:

Old implementation images are deliberately retained for state/destructor safety.

Fix:

- maximum **64** loaded generations per shell/process;
- unchanged reloads do not consume a generation;
- restart required after the cap is reached.

### 12. MEDIUM — multi-shell Reload is not atomic

Behavior is intentionally documented:

- each shell reload is independently validated;
- an earlier successful shell is not rolled back if a later shell fails;
- Agent reports mixed success/failure.

This is safer than attempting cross-effect rollback with unrelated persistent AE state.

## CI gates

### AE Hot Loader

Current hardened production CI covers:

- Rust/C++ static checks;
- default and candidate implementation builds;
- Agent build;
- shell build/sign/package;
- shell direct reload smoke;
- Agent dyld enumeration → shell reload smoke;
- MFR busy-swap stress;
- incompatible key/ABI rollback;
- Runtime ABI mismatch rejection;
- invalid / unterminated ABI string rejection;
- bundled default → candidate transition;
- candidate removal → bundled rollback.

Latest known green checkpoint:
**AE Hot Loader run #236 — SUCCESS**.

### ElasticGrid

Adapter CI covers:

- PiPL ↔ shell metadata parity;
- hot-reload state-contract verifier;
- Rust toolchain pin;
- default + candidate implementation builds;
- macOS deployment target;
- no private relative dylib dependencies;
- signed shell bundle;
- bundled default → candidate → unchanged → bundled rollback;
- packaged binary test kit.

Full project CI additionally covers:
- GCC;
- Clang;
- ASan/UBSan;
- TSan;
- static analysis.

Latest adapter checkpoints:
- ElasticGrid Hot Loader Shell CI **#60 — SUCCESS**
- ElasticGrid full CI **#139 — SUCCESS**
- Stellar Gradient Hot Loader Shell CI **#70 — SUCCESS** is the latest fully green build; later lock-hardening run #73 exposed a malformed committed checksum and is being repaired before live use.

### Stellar Gradient

Adapter CI covers the same shell/runtime gates plus:

- exact numeric parameter ID freeze;
- SmartFX `RenderStateC` pre-render layout freeze;
- GPU context generation/destructor layout.

## Live runtime status — 2026-09-28

The real AE 25.6 **Control Shell gate is fully passed**:

- startup registration succeeded;
- bundled `default-v1` rendered;
- A→B reload to `candidate-v2` succeeded without AE restart;
- the existing instance rendered through `candidate-v2`;
- unchanged/no-op detection succeeded;
- deterministic busy-render reload was rejected with `-4112` and the expected retry message;
- B→C reload to `candidate-v3` succeeded after the render ended;
- `candidate-v3` rendered;
- rollback to bundled `default-v1` succeeded;
- bundled `default-v1` rendered after rollback.

Manual cache Purge was used only to force AE to execute a fresh render during validation. It is **not** a product workflow requirement. Automatic invalidation/fresh evaluation after a successful reload is now an explicit release requirement.

Still open: real ElasticGrid and Stellar Gradient adapter gates plus automatic cache refresh UX.

## Remaining live-only risks

These cannot be proven by synthetic CI and require After Effects 25.6:

1. AE startup registration of the real shell through native Effects & Presets.
2. Actual AEGP idle-hook scheduling while AE is interactive/rendering.
3. Real MFR behavior under AE's renderer.
4. Real SmartPreRender → SmartRender lifecycle around a reload attempt.
5. AE GPU device setup/setdown behavior after a generation change.
6. Existing effect instances after A→B→C implementation swaps.
7. Project save/reopen compatibility.
8. UI/custom-event behavior for ElasticGrid after reload.
9. Stellar Gradient GPU/CPU fallback behavior after reload.
10. Repeated reload stress in a real AE process.

## Live release gate

Control Shell items 1–7 below are now passed in real AE 25.6:

1. Control shell registers normally after one AE restart. ✅
2. Bundled default renders. ✅
3. Candidate reload reports success. ✅
4. Existing instance renders after swap. ✅
5. Unchanged reload reports unchanged. ✅
6. Busy render produces retry rather than hang/crash. ✅
7. Candidate removal rolls back to bundled default and renders. ✅

Still required before merge to `main`:

8. ElasticGrid passes CPU + UI + Smart Render/MFR + GPU + A→B→C + rollback + save/reopen.
9. Stellar Gradient passes CPU + SmartFX + MFR + GPU + A→B→C + rollback + save/reopen.
10. Successful reload automatically invalidates stale cached output; normal use requires no manual Purge.
11. Logs contain no duplicate shell/Agent discovery.
12. No duplicate match-name copies remain installed.

