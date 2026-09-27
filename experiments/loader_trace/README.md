# AE Loader Trace Experiment

## Goal

Identify the smallest internal After Effects call path that owns a valid plug-in registration transaction.

We already proved:

- two registrations using the same `PF_PluginDataPtr` inside `PluginDataEntryFunction2` both return 0;
- using the saved callback after `PluginDataEntryFunction2` returns is unsafe and can crash AE;
- therefore the callback lifetime is scoped to AE's loader transaction.

## Method

Observation only. No patching and no modification of AE memory.

1. Use a development/debuggable copy of After Effects.
2. Launch it under LLDB.
3. Break on the diagnostic bundle's `PluginDataEntryFunction2`.
4. Capture the complete stack before the callback is invoked.
5. Break on `dlopen` and `CFBundleLoadExecutableAndReturnError` only when useful.
6. Symbolicate addresses belonging to the After Effects executable/frameworks.
7. Compare the loader stack with the later AEGP idle-hook stack.

## What we need

The first AE-owned frame above `PluginDataEntryFunction2` that:
- exists only during plugin discovery/loading;
- creates/owns the registration transaction;
- can potentially be invoked with a newly discovered plugin path.

## Stop criterion

Produce a stable AE 25.6.0 ARM64 address/signature and call stack for the loader transaction owner. Do not call it yet.
