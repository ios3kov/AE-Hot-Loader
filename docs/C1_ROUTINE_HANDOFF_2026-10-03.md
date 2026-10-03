# C1 retained routine/provider to ordinary-effect handoff

Stage C1 Development; accepted rules v8.0.0 / 132b7cd32873ba7328e3128ffbb33e1929b74d45.
Starting clean research source 815f2f9639da9b299ae6c26bdae986067d4f94fd.
[HAND-01–12 acceptance](PRODUCTION_PLAN.md) recorded before new body collection.
Continue [owner findings](C1_PUBLICATION_OWNER_2026-10-03.md), preserving original
arbitrary ordinary-effect/no-restart product and A/B/C1/C2/D/release obligations.
Collector Standard, native integration Critical/gated. Only pinned original-file
research and owned controls; no AE process operation in preparation.

Prepared state: investigation not completed, new source-bound checks NOT RUN.
Native receiver/ABI/thread/admission/drain/completion/rollback UNKNOWN; dependent
HAND-10–12 BLOCKED/NOT RUN until established mechanism and concrete operation scope.


## Fixed file scope and new discriminator

New collector mode `--review routine-handoff`: 17 complete fixed windows,
4707 decoded instructions, 275 selected structural anchors. FLT setup is two
adjacent chunks of one complete function; constructor/release helper are separate
complete symbols (do not mislabel their earlier combined preliminary window).
Existing exact pins for aelib, MEE, PluginSupport, FLT and PLUG are reused from the
collector/profile; no native helper/profile/ResourcePassGate or SDK modifications.
Only original file bytes / offline LLDB with no dependents, launch, attach or
expressions. Full Adobe binaries/disassembly remain private.

| Complete window, end exclusive | Instructions |
|---|---:|
| aelib / handoff-init 0x61134–0x61fe8 | 941 |
| aelib / handoff-aelib 0x63aa0–0x63c04 | 89 |
| MEE / handoff-setter 0x3e320–0x3e400 | 56 |
| MEE / handoff-getter 0x3e400–0x3e454 | 21 |
| MEE / handoff-module 0xbbe0–0xc274 | 421 |
| MEE / handoff-invoker 0xc274–0xc450 | 119 |
| PluginSupport / handoff-load-ae 0x5b3f8–0x5b944 | 339 |
| FLT / handoff-entry 0x8ef8c–0x8f360 | 245 |
| FLT / handoff-setup-a 0x8d250–0x8e250 | 1024 |
| FLT / handoff-setup-b 0x8e250–0x8ef8c | 847 |
| FLT / handoff-store 0x5e26c–0x5e2f0 | 33 |
| FLT / handoff-ctor 0x5cae4–0x5cbec | 66 |
| FLT / handoff-release 0x5cbec–0x5cc60 | 29 |
| FLT / handoff-dtor 0x5cc64–0x5cd3c | 54 |
| FLT / handoff-dispose 0x9a258–0x9a4d8 | 160 |
| PLUG / handoff-provider 0x7228–0x7430 | 130 |
| PLUG / handoff-routine-dispose 0xd6d8–0xd8ec | 133 |

## Handoff, ownership and invocation (HAND-01–04)

1. The original aelib InitIterator startup state installs the SetupAEPlugin
   callback through MEE_SetAELibPluginSetter before LoadAEPlugins and the FLT/MEE
   loading-done notifications. It later enters general-plugin cleanup and module
   lockdown. That startup sequence is not a supported late replay operation.
2. MEE's setter clones/copies then swaps a process-wide boost function and can
   dispose the previous target; its getter copies that global function. Neither
   complete body establishes host-wide admission/drain or even a shared lock
   around that callback slot. Do not replace the global setter as an experiment.
3. AELibraryVideoFilterModule::SetupFilter locks **that module object's** recursive
   mutex at +8, obtains a copied setter, and queries the hardcoded-plugin cache.
   A nonzero cache result bypasses the callback and writes cache outputs (+b0/+b8).
   Otherwise it retains plugin/PiPL references and calls the boost function invoker.
   The invoker transfers those references into its local arguments, uses a stored
   indirect invoker and releases on normal/exceptional exit; empty function throws.
   The original initializer binds the aelib wrapper in file evidence. Actual live
   setter/provider/module/cache identity and a callable late contract UNKNOWN.
4. The aelib wrapper copies/retains IPlugin/IPiPL and calls FLT_SetupAEPlugin.
   FLT validates a PiPL kind, excludes the AE.AEGP route, obtains provider path via
   a virtual method, copies both interfaces and calls FLTp_FiltSetup with cache
   output and an empty existing FCSpec. The negative not-handled route can fall
   back to MEE_SetupAEGPPlugin. This is an actual internal setup consumer rather
   than treating PLUG routine-roster insertion as effect publication.
5. FiltSetup explicitly selects path-only registration when the provider interface
   is absent and the provider overload when present. Both pass their retained
   descriptor through SetRoutineDescH, post-setup and AddEffect; the ordinary
   registry publication remains the separately reviewed FLT publisher's operation.
   SetRoutineDescH retains/swaps the Boost owner pair at FCSpec +c0/+c8, then
   releases the old pair. The FCSpec constructor initializes that pair and creates
   a per-object mutex at +170; its destructor destroys local strings/trees/mutex
   and releases the descriptor pair. Retained ownership is not a global publication
   lease or proof of final executable lifetime/unregistration semantics.
6. LoadAEPlugins loads static plugins and selects plugin/required-plugin roots,
   then delegates to LoadPlugins with ownership/scan arguments. Its file-flush
   delay scoper and temporary-vector cleanup are not a render drain. Full transitive
   loader/factory/initialization behavior remains UNKNOWN; no root scan is invoked.

Primary SDK cross-check: actual SDK 25.6_61 Headers/AE_GeneralPlug.h SHA-256
`30d12ec3eb5af1a902c7414053b1be1da0204b226e0b1cdc71272be1e137000c`.
FLT_SetupAEPlugin, MEE_Set/GetAELibPluginSetter and AELibraryVideoFilterModule
literals absent in that one header. This lexical boundary is not global API
absence; existing public installed-effect keys cannot be cast to private
InterfaceRef/Boost owners. No new host API call/signature/SDK fixture change;
prior SDK owned macro results keep their original 9e35d1e identity.

## Thread/exclusion/completion/rollback (HAND-05–08)

- The per-module recursive lock is held across cache/callback invocation and local
  teardown. Different modules, escaped readers/render/MFR and global setter
  replacement are not shown to share it. Recursion also permits same-thread reentry.
  It does not bridge the distinct PLUG roster/FLT registry/per-FCSpec mutexes into
  a continuous all-reader admission/drain lease. Actual permitted thread UNKNOWN;
  prior idle/render-zero snapshots are not that contract.
- **Success is not effect readiness.** A cache shortcut can skip the callback;
  SetupFilter accepts a nonnegative callback result. The aelib wrapper returns
  zero for any nonnegative FLT status, including a possible positive translated
  error. FLT's caught exception paths translate/read error values and return them;
  those outputs are not independently observed registry/apply/render success.
  The full caught type/status contract remains private/UNKNOWN.
- Provider setup can AddEffect before its optional ReadyFilter/lazy-global path.
  A subsequent lazy-global error is thrown after publication. Local references
  unwind, but the complete setup/outer wrapper bodies do not directly compensate
  by removing the published registry entry. Transitive cleanup is not claimed
  absent; its transaction/rollback contract remains unproven.
- **DisposeFCSpec is destructive teardown, not a tested inverse transaction.** It
  unregisters canonical match names (preserving a selected built-in group), then
  performs GPU-device and global setdown and combines returned errors. Selected
  caught canonical errors still continue into later teardown. Neither success nor
  failure is atomic restoration; no direct registry erase/unregister-routine call
  occurs in this body. Transitive behavior, prepared counts, escaped owner/reader
  safety and final executable unloading remain UNKNOWN.
- PLUGp_DisposeRoutineDesc takes the roster mutex, can reject a descriptor carrying flag bit 2,
  or call platform unload. On the returned unload-error lane it can still clear
  the caller's descriptor pair; on success it also decrements the global count.
  This extends the prior unregister failure/no-op finding: no guessed cleanup,
  callback replacement, destructor or unload is authorized as recovery.

## Prepared research verification and dependent gate

Three new scope/catalog/refusal controls first failed with expected missing mode
errors; implementation then passes all 51 collector tests, including real owned
arm64 LLDB controls. Wrong cache/status/owner-transfer/cleanup operands, changed
bounds, incomplete/duplicate/undecoded data refuse collection. Synthetic parser
controls are not AE execution proof. New records explicitly label startup-only
file correspondence, cache/status normalization, per-module lock, unknown ABI/
actual identities/global lease/rollback and registration/apply/render NOT RUN.

Separate review: complete function boundaries, cache versus callback branch,
retains/transfers/normal and exceptional release, status normalization, AddEffect
before optional lazy setup and non-atomic teardown assessed independently of the
selected-anchor tests. Preliminary original-file/xref/SDK material at
build-ae-hot-loader/handoff-preliminary-8o37whzq is dirty/preliminary; not final
clean-source acceptance. Source-bound full collection/raw-byte/archive verification,
full regression/scanner/exact-source CI pending at this prepared checkpoint.

HAND-01/02 bounded file handoff identified; HAND-03/04 structural invocation and
ownership findings documented, actual supported ABI/receiver/lifetime still
UNKNOWN. HAND-05–08 research complete for the selected boundaries, required
thread/all-reader exclusion/completion/whole-effect rollback BLOCKED. HAND-09
implementation/focused controls complete, final checks pending. HAND-10 native
experiment BLOCKED on those contracts; HAND-11/12 live registration/apply/render
and actual result interpretation NOT RUN. No concrete safe native packet exists.

Original product/A/B/C1/C2/D/release preserved; backend NOT READY. Current owned
research receipts retained for reproducibility; existing sessions/consumed helpers,
SDK, projects, third-party plugins and historical evidence left in place. Next
research discriminator: the upstream module-admission/initialization contract
that supplies SetupFilter's actual provider, and whether it supplies an enforceable
late-host drain/transaction. Do not replay InitIterator, swap the setter, or call
SetupFilter/FLT/disposal through guessed objects. No main merge/release.
