# In-process plugin-core reinitialization research

## Status

**BLOCKED for implementation** on After Effects 25.6.0 ARM64. No supported or
validated private lifecycle was found that can tear down and reinitialize the
effect/plugin core while preserving an open project and its live UI state.

## Baseline

- Git commit: `67c747e`
- Host: After Effects 25.6.0 ARM64
- Live process remained open during the audit.
- Existing ordinary-discovery path can load compatible effects through
  `ML::LoadPlugins` followed by `FLT_NotifyFilterLoadingDone`.
- RSMB live test loaded three bundles but left the Effects Registry unchanged
  (`count=782` before and after). This is the motivating failure.

## Audited private lifecycle symbols

### SweetPea

`ae_sweetpea.dylib` exposes `SPStartupPlugins`, `SPShutdownPlugins`, `SPInit`,
and `SPTerm`. Disassembly shows shutdown transitions SweetPea into a shutdown
state and invokes adapter shutdown. `SPTerm` releases suites, plugin lists,
adapter lists, and file lists. This is a subsystem termination path, not a
validated After Effects effect-registry refresh operation.

### MEE / general plugins

`MEE.dylib` exposes `MEE_Plugins_Init` and `MEE_Plugins_Terminate`, together
with `SetdownGeneralPlugins`, `CleanupGeneralPluginScan`, and
`MEE_HardcodedPluginsCache::Terminate`. The inspected code clears plugin maps,
calls plugin cleanup callbacks, unprepares routines, and destroys hardcoded
plugin cache state. No matching public/private reinitialization sequence that
restores project-held effect references was found.

### Filter host and registry

`FLT.dylib` contains `VideoFilterHost::Initialize/Shutdown`, the
`FLT_FilterRegistry` singleton, `FLT_SetupAEPlugin`, and
`FLT_NotifyFilterLoadingDone`. The registry destructor disposes registered
filter specs and effect state. Calling this teardown while an open project
can hold effect instances would invalidate live references unless the complete
host-owned lifecycle is also restored; that contract is not available.

## Decision

Do not call `SPShutdownPlugins`, `SPTerm`, `MEE_Plugins_Terminate`,
`MEE_HardcodedPluginsCache::Terminate`, `SetdownGeneralPlugins`,
`CleanupGeneralPluginScan`, `VideoFilterHost::Shutdown`, or the filter-registry
destructor from the Agent. Such a call would be an unvalidated destructive
operation in the user's live AE process and would violate the requirement to
preserve the open project and working interface.

The current ordinary-discovery implementation remains the least destructive
validated path. RSMB is **not** classified as fixed or compatible: its late
load remains a live FAIL and requires a separate compatibility/registration
investigation, or an Adobe-supported host refresh API if one becomes
available.

## Evidence and limitations

The result is based on AE 25.6 ARM64 symbol inspection, disassembly of the
relevant lifecycle functions, and the recorded RSMB live test. It is not a
claim about other AE versions, architectures, or future host builds. No
teardown function was invoked in the live process.
