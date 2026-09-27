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
2. Fingerprint it.
3. Copy it to a unique runtime path.
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
- GPU/CPU implementation internals;
- behavior that preserves the persistent AE-facing state contract.

Changes that normally require a shell rebuild + AE restart:

- PiPL metadata;
- match name/category;
- parameter schema/IDs;
- incompatible global/sequence data;
- supported command/capability flags that must be advertised during host registration.

## Threading rule

The pointer swap is atomic. Already executing calls may finish in an older implementation while later calls enter the new implementation. This is why old implementation dylibs are never unloaded during the AE process lifetime.
