# Internal Loader Probe

Experimental one-shot probe for **After Effects 25.6.x / macOS Apple Silicon**.

## Goal

Call After Effects' own private loader path while AE is already running:

```
ML::LoadPlugins
→ PluginNameList::AddFolder
→ LoadPluginList
→ AddPlugin
→ PluginDataEntryFunction2
```

This is intentionally isolated from the production Agent.

## Safety

- arm64 only;
- refuses hosts whose bundle version does not start with `25.6`;
- refuses calls off the main thread;
- resolves `ML::LoadPlugins` from the loaded `PluginSupport.framework` Mach-O symbol table;
- scans only the folder explicitly passed to the probe;
- does **not** call a saved `PF_PluginDataCB2`;
- does **not** call `AddPlugin` directly;
- does **not** free ABI shim storage after the private call, to avoid allocator mismatch during this one-shot experiment.

The previous deferred-registration experiment crashed AE. That path has been removed from the diagnostic wrapper in this branch and must not be reintroduced.

## Confirmed ABI for AE 25.6 ARM64

```cpp
ML::LoadPlugins(
    outputVector,          // x0, empty vector
    rootPath,              // x1, UTF-16 string
    1,                     // w2, ModuleOwnership
    {"PlayerMediaCore"},   // x3
    {},                    // x4
    false                  // w5
);
```

Observed layouts:

```cpp
struct RawVector {
    void* begin;
    void* end;
    void* capacity_end;
}; // 24 bytes

struct RawString {
    void* data;
    uint64_t size;
    uint64_t capacity_flags;
}; // 24 bytes
```

## Build

The GitHub Action `internal-loader-probe.yml` builds:

- `libAEHotLoaderInternalProbe.dylib`
- a safe `AEHotLoaderDualPiPL.plugin` test bundle

## Live test

1. Quit AE and make sure `AEHotLoaderDualPiPL.plugin` is **not** installed in any normal AE plug-in directory.
2. Start the debuggable AE 25.6 copy under LLDB and let it finish startup.
3. Put the test plug-in into a dedicated folder, for example:

```text
/tmp/AEHotLoaderProbe/AEHotLoaderDualPiPL.plugin
```

4. In LLDB, pause AE and load the probe dylib:

```lldb
expr (void*)dlopen("/absolute/path/libAEHotLoaderInternalProbe.dylib", 2)
```

5. Resolve and call the exported probe **on the main thread**:

```lldb
expr (int)((int(*)(const char*))dlsym((void*)-2, "AEHotLoader_InternalLoaderProbe"))("/tmp/AEHotLoaderProbe")
```

6. Check:

```bash
cat /tmp/ae-hot-loader-internal-probe.log
cat /tmp/ae-hot-loader-dualpipl.log
```

7. Verify whether the new effects appear in the running AE Effect menu.

## Stop criterion

Success means the new test effect becomes registered and usable **without restarting After Effects**.

If AE crashes, hangs, or the private call returns without registering the test effect, stop. Do not retry with direct or deferred registration callbacks.
