# AE Hot Loader Shell ABI

This document defines the stable contract between an After Effects shell plug-in and a hot-swappable implementation dylib.

## Shell responsibility

The shell owns all host-visible registration data:

- PiPL;
- effect name;
- category;
- match name;
- native `EffectMain` export;
- `PluginDataEntryFunction2`;
- the expected implementation identity and state ABI.

The shell remains loaded for the complete AE session.

## Required implementation exports

Every reloadable implementation dylib must export:

```text
EffectMain
AEHotLoader_ImplementationABI
AEHotLoader_ImplementationStateABI
AEHotLoader_ImplementationKey
AEHotLoader_ImplementationLabel
AEHotLoader_ImplementationRuntimeABI
AEHotLoader_SetGeneration
```

### Protocol ABI

`AEHotLoader_ImplementationABI() -> u32`

Current value: **2**.

Change this only when the shell/implementation calling convention changes.

### State ABI

`AEHotLoader_ImplementationStateABI() -> u64`

The value identifies the in-process state/schema contract used by `EffectMain`.

A candidate whose state ABI differs from the shell is rejected before the active function pointer is changed.

For an AE effect, increment the state ABI whenever an in-session reload could reinterpret incompatible data, including changes to:

- parameter identity/order expected by the host implementation;
- global-data layout;
- sequence-data layout or serialization contract;
- GPU-device/global state representation;
- other persistent memory passed back through AE between commands.

A state-ABI change requires rebuilding/installing the shell and restarting AE once.

### Runtime ABI

`AEHotLoader_ImplementationRuntimeABI(char* output, size_t capacity) -> int`

This identifies the Rust/compiler runtime contract of the implementation. The current implementation embeds at least:

- exact `rustc` version;
- target triple;
- the pinned `after-effects` crate/revision family.

The shell always establishes the process Runtime ABI from the **bundled implementation shipped inside the shell**. An external `current.dylib` is never allowed to define the session baseline, even when Reload is clicked before the effect has rendered. Later candidates whose Runtime ABI differs are rejected.

This matters because the Rust host keeps opaque `global_data` / sequence / GPU-facing state across EffectMain calls. Rust does not promise a stable layout for such internal types across compiler/library versions.

A candidate built with another Rust toolchain must therefore not be hot-swapped into an already-running session. Rebuild it with the pinned toolchain, or restart AE with a shell/default implementation built for the same runtime ABI.

### Shell-assigned generation

`AEHotLoader_SetGeneration(u64 generation)`

The shell computes a content fingerprint from the exact staged dylib bytes and assigns that value to the implementation **before** publishing its `EffectMain` pointer.

The generation is not derived from a human label. Rebuilding different code with the same label must still create a different generation.

Persistent GPU/native state should record the generation that created it. New implementation code must reject or bypass stale GPU/render state from a previous generation. If an old native resource needs destruction after a reload, the persistent state must retain a destructor/function pointer belonging to the implementation generation that created that resource; old implementation images stay loaded for this reason.

### Implementation key

`AEHotLoader_ImplementationKey(char* output, size_t capacity) -> int`

The key prevents loading a valid implementation for the wrong effect.

Examples:

- `control`
- `elasticgrid`
- `stellar-gradient`

### Label

`AEHotLoader_ImplementationLabel(char* output, size_t capacity) -> int`

Human-readable build identifier used for diagnostics, for example `candidate-v2`.

## Reload transaction

1. Ensure the bundled implementation has established the session baseline.
2. Locate the candidate implementation.
3. Copy it to a unique runtime path.
4. Fingerprint the staged bytes.
5. `dlopen` the unique copy.
6. Resolve all required exports.
7. Validate protocol ABI, state ABI, implementation key and Runtime ABI.
8. Assign the staged-byte fingerprint through `AEHotLoader_SetGeneration`.
9. Only after all validation succeeds, publish the new `EffectMain` pointer.
10. Keep every old dylib handle loaded until AE exits.

If steps 3–6 fail, the previous implementation remains active.

## What may be hot-reloaded

Typical safe changes:

- rendering algorithms;
- math/quality fixes;
- performance changes;
- CPU implementation internals that preserve the persistent AE-facing state contract;
- GPU shader/renderer changes when stale per-device state is generation-detected and safely bypassed/reinitialized;
- behavior that preserves the persistent AE-facing state contract.

Changes that normally require a shell rebuild + AE restart:

- PiPL metadata;
- match name/category;
- parameter schema/IDs;
- incompatible global/sequence data;
- GPU/state schema changes that are not covered by an intentional StateABI bump and compatibility migration;
- supported command/capability flags that must be advertised during host registration.

## Threading rule

Effect calls may run concurrently under MFR, but old and new implementation code must not overlap on the same shell generation.

The shell uses a reentrant-safe generation gate built from atomics:
- concurrent and nested/reentrant EffectMain calls remain allowed;
- every active call increments an in-flight counter;
- Reload marks a swap as pending only for the final pointer publication;
- if any EffectMain call is still in flight, Reload returns a **busy / retry** error instead of blocking AE's main thread;
- while the tiny publication window is active, new calls wait briefly and then enter the published generation;
- the pointer is published only when the in-flight count is zero.

Old implementation dylibs are still never unloaded during the AE process lifetime.

## Multi-shell transaction rule

`Reload Plugins` is intentionally per-shell, not all-or-nothing across every loaded effect. If one shell reloads and a later shell fails validation, the earlier shell remains updated. The Agent reports the mixed result; it does not roll back already successful shells.


## Session generation limit

Old implementation images are intentionally retained because AE can keep persistent state whose destructor or opaque native state still belongs to an older implementation generation.

To keep this safety rule from becoming unbounded memory growth, each shell allows at most **64 loaded generations per AE process**. Unchanged reloads do not consume a generation. When the limit is reached, Reload returns an error asking for one AE restart.
