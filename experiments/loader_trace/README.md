# AE Loader Trace Experiment

## Goal

Identify the smallest internal After Effects call path that owns a valid plug-in registration transaction.

Verified on After Effects 25.6.0 ARM64:

- two registrations using the same `PF_PluginDataPtr` inside `PluginDataEntryFunction2` both return 0;
- using the saved callback after `PluginDataEntryFunction2` returns is unsafe/rejected;
- the registration callback lifetime is scoped to AE's loader transaction;
- loader chain:
  `ML::LoadPlugins → LoadPluginList → AddPlugin → PluginImpl::GetPiPLs → GetPFPluginData → GetEntryPoint → dlsym("PluginDataEntryFunction2")`;
- observed `ML::LoadPlugins` ABI:
  `(vector<UTF16String>& out, UTF16String const& root, ModuleOwnership ownership, vector<UTF16String> const& filters, vector<UTF16String> const& extra, bool flag)`;
- ARM64 register mapping at entry: `x0, x1, w2, x3, x4, w5`;
- observed startup values: `w2=1`, `w5=0`, with `x0` and `x4` initially empty vectors.

## Current target

Capture the stable image-relative offset for `ML::LoadPlugins` in AE 25.6.0 ARM64. Runtime addresses are ASLR-dependent and must not be hard-coded.

Use:

`experiments/loader_trace/capture_loadplugins_abi.lldb`

The script captures:
- call stack;
- argument registers;
- raw object/vector layouts;
- symbol/image lookup;
- image-relative address information;
- function disassembly.

## Stop criterion

Produce a stable AE 25.6.0 ARM64 image + offset for `ML::LoadPlugins`, then use that offset in an isolated native prototype that invokes the loader on a dedicated folder containing one new test `.plugin`.
