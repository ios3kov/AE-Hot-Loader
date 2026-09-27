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
```

### Protocol ABI

`AEHotLoader_ImplementationABI() -> u32`

Current value: **1**.

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

1. Locate the candidate implementation.
2. Copy it to a unique runtime path.
3. Fingerprint the staged bytes.
4. `dlopen` the unique copy.
5. Resolve all required exports.
6. Validate protocol ABI, state ABI and implementation key.
7. Only after all validation succeeds, atomically publish the new `EffectMain` pointer.
8. Keep every old dylib handle loaded until AE exits.

If steps 3–6 fail, the previous implementation remains active.

## What may be hot-reloaded

Typical safe changes:

- rendering algorithms;
- math/quality fixes;
- performance changes;
- CPU implementation internals that preserve the persistent AE-facing state contract;
- GPU shader/renderer changes **only when** the existing GPU context remains fully binary/semantic compatible;
- behavior that preserves the persistent AE-facing state contract.

Changes that normally require a shell rebuild + AE restart:

- PiPL metadata;
- match name/category;
- parameter schema/IDs;
- incompatible global/sequence data;
- GPU context, pipeline, cache or opaque native-state changes that make an existing `gpu_data` pointer unsafe for new code;
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
