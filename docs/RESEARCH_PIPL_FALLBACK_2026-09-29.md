# Offline PiPL fallback inspection

Stage C of A–D. Rules blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`
rechecked unchanged. Baseline: Dynamic late registration and application PASS;
PiPL-only late registration FAIL. Objective: locate the non-dynamic resource
path without executing private host functions. Acceptance: reproducible static
observations tied to an exact binary; no claim of runtime repair.

## Identity and evidence

- Collector source: `ea1a12c3d32d0a8bd377f4cd085e8c171ad1b47b`, clean.
- Native product/fixture builds unchanged: `native-36483421984-1` / `50650366d8b6`.
- Inspected file: installed AE 2025 `PluginSupport.framework/Versions/A/PluginSupport`.
- ARM64 image UUID: `64C01AC4-2413-3463-8822-17EE5543052A`.
- Image SHA-256: `4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`.
- Run: `pipl-static-1e44e6053d5542dfa54772e0979b12e2`.
- Local evidence: `build-ae-hot-loader/evidence/<Run ID>/record.json` and
  `disassembly.txt`. Full proprietary disassembly is not committed/distributed.
- Disassembly SHA-256: `f8b2db2197b0ec723ea1ac34b5ebae4174f25aafcb5e4e9d111c85040fa963ce`.

Collector uses offline LLDB target creation, disabled init files, fixed
disassembly commands and a 30-second timeout. No attach, process launch,
expression evaluation, host mutation or private function invocation.

## Static observations (not runtime execution evidence)

Offsets below identify only this image, never callable production addresses.

1. `GetPFPluginData` at 0x4b5d8 tries `PluginDataEntryFunction2`, then
   `PluginDataEntryFunction`; neither present returns value 3 at 0x4b70c.
   This agrees with the two callback declarations in local AE SDK 25.6
   `Examples/Headers/AE_PluginData.h`; no SDK implementation was copied.
2. `PluginImpl::GetPiPLs` at 0x4c72c first accepts cached PiPL data, otherwise
   calls GetPFPluginData and converts successful dynamic data. If the result
   vector is empty it dispatches a virtual call through slot 0x88 at 0x4c7e0.
   The concrete runtime receiver/vtable has NOT been established here.
3. Separately, `AEPlugin::LoadPiPLs` at 0x210c calls InternalLoadPiPLs for a
   module and falls back to PluginImpl::LoadPiPLs if the vector remains empty.
   PluginImpl::LoadPiPLs also calls InternalLoadPiPLs.
4. `InternalLoadPiPLs` at 0x4ca10 enumerates bundle resource URLs of type PiPL
   and calls the URL-based reader. If no PiPL entries result, its 0x4ce0c call
   invokes the module-reference overload.
5. That overload at 0x41da8 requests resource type PiPL, ID 16000; non-null
   bytes are copied and passed to SetPiPLValues. The separate overload taking
   a short resource ID at 0x41eac consists only of a return in this image.
   Its name/export is therefore not a usable registration recipe.

## Decision and next discriminating checks

Do not claim that dynamic entrypoint absence alone proves the cause, that
PiPL-only is unsupported, or that a `mainB` adapter is required. Static fallback
paths exist; whether this late scan reaches them and receives valid data remains
unknown. No production/native loader change is justified yet.

Next inspect the ASL module resource-reader implementation and compare the
owned fixture's resource representation outside AE. Separate hypotheses:
runtime receiver/dispatch, resource acquisition, PiPL interpretation, subsequent
registry insertion. Do not call private constructors/loaders or saved registration
callbacks to test these hypotheses. Any new live trace needs separately declared
bounded instrumentation and project/host identity safeguards.

| Check | Result |
|---|---|
| Offline collector, exact-image stability, all requested disassemblies | PASS |
| Python syntax check | PASS |
| New AE runtime experiment | NOT RUN |
| PiPL-only late registration | FAIL (historical live gate, unchanged) |
| Safe corrective registration operation | BLOCKED (not established) |
| New artifact build/install | N/A (read-only research) |

Existing product and application evidence remains unchanged; no main change,
push, release, plugin installation, restart or reload was performed.
