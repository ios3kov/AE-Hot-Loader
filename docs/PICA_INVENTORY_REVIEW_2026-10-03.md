# Public PICA plug-in inventory — 2026-10-03

Stage C1, Development preparation for a bounded Validation diagnostic.
Rules: AE-Development-Rules v8.0.0 at
`132b7cd32873ba7328e3128ffbb33e1929b74d45`; AI_ENTRYPOINT first, then
AI-STATE/API-SOURCE/SAFE/REPRO/TEST-CONTROL/TASK-CLOSE/CLEANUP and native/thread/
ownership/tools diagnostics/IPC overlays. Acceptance INV-01–08 is recorded
before implementation in [PRODUCTION_PLAN](PRODUCTION_PLAN.md). Original
ordinary-effect workflow, A/B/C1/C2/D and release obligations remain open.

## Decision and primary contracts (INV-01/02)

Actual SDK: AE SDK 25.6_61, Examples/Headers, not redistributed. Exact inputs
are hashed by the clean-source builder. SPPlugs.h: rev4 at lines 157–191,
rev6 at 379–413; SPFiles.h: Mac value FSRef at 174–185; SPAdapts.h public
adapter getters. Native static assertions bind the actual declarations.
SPFiles.h conversion-specific caller-owned CFURL comments at 288–291 do not
establish ownership for the separate GetPluginXplatFileSpec getter. Rev6 getter
is signature-checked only, never invoked. Use rev4 GetPluginFileSpecification:
caller-provided SPPlatformFileSpecification value containing FSRef, converted
with Apple's public FSRefMakePath into an owned 4096-byte UTF-8 buffer.
No CFURL retain/release, guessed lifetime, opaque handle conversion or private ABI.

Primary OS authority is the Files.h selected by `xcrun --show-sdk-path` under
CoreServices/CarbonCore, FSRefMakePath declaration/contract near 4060–4086.
The builder explicitly selects that SDK with -isysroot and records path/hash
before/after. FSRefMakePath is deprecated since macOS 10.8 but present in the
actual selected SDK. Only the two owned/native conversion calls locally suppress
the deprecation warning; other warnings remain errors. A real owned-file
FSPathMakeRef/FSRefMakePath roundtrip is required in the inert prerequisite.
This is an exact Mac research contract, not a future cross-platform guarantee.

SPPlugs.h 492–499 property acquisition may send a plug-in message and change its
property list. No GetPluginProperty/FindPluginProperty, plug-in acquisition,
AddPlugin/AddXPlatPlugin/AddAdapter, startup/shutdown, scan or unload is used.
AcquireSuite itself may load modules; that possibility is explicit in the live
scope. No global list/object is freed: only this diagnostic's iterator is deleted
once; two bounded suite leases remain until controlled host exit.

Known anchors are the existing owned Control Shell and Rust Probe ordinary-effect
bundles in user MediaCore, match names OS3KOV.AEHotLoader.ControlShell and
OS3KOV.AEHotLoader.RustProbe. Builder pins binary/resource/Info.plist bytes,
CFBundleExecutable, source declaration SHA and presence of each ASCII match literal
in its resource. The native observer pins binary/resource before and after and
requires both match names in the same public AE effect baseline. This establishes
bounded metadata/file association, not a runtime source-origin or publication proof.
Neither known binary was loaded in the previous recorded dyld inventory despite
both registered matches; no lazy effect load is required or triggered here.

Exact returned bundle OR main-binary path is a positive LISTED correlation.
No basename/prefix/child guess or implicit normalization. Repeated entries are
retained. NOT_LISTED requires complete enumeration and every path resolved;
otherwise a missing hit is UNKNOWN. File/path/adapter errors retain raw codes.
Even LISTED does not establish that AddPlugin can publish ordinary effects.

## Implementation and bounded failure handling (INV-03/04)

Separate PicaInventory helper, builder and independent file observer reuse only
reviewed public snapshot, resident-image binding and private durable I/O primitives.
New build/run/token and unique prospective bundle; no shared mutable-state reset.
Exact source/host/module/binary/PID/start/token byte scope, consume-before-call,
main-thread idle execution, exclusive durable per-stage files and no replay.
Limits: 2048 entries, 1 MiB serialized entry payload, 4095 path bytes and 256 adapter
name bytes; incremental per-entry journal avoids quadratic disk output.
Native 10-second cooperative deadline checks surround SDK calls and writes;
a blocked host API cannot be preempted. The external 30-second deadline writes
one TIMEOUT and preserves process/partial evidence, without retry or termination.
A failed getter is unresolved evidence; failed stage, changed baseline, missing
durability or exceeded bound is STOPPED. No negative claim from partial output.

Before/after same owned blank clean idle project, registry identities and runtime
binding required. Existing loaded images cannot disappear; potential suite-load
additions are recorded separately. Known-file hashes and registered matches must
stay stable. Independent verifier binds entry deltas/terminal, NULL-end stage,
claim, known-file evidence and every journal to the exact request identity.

Focused owned tests: 19 Python cases, including one aggregate C++ test containing
27 labelled owned/synthetic policy scenarios; all PASS, no skips. File tests use
real private durable files with synthetic host/providers. The C++ policy tests
cover failure injection, deadlines, one-shot refusal, empty/partial/error results,
2048-entry and aggregate-payload bounds. They do not execute AE.

## Prerequisites and remaining steps (INV-05–08)

Clean-source actual SDK build/sign/export/getter/inert prerequisites, available
full regression, bounded code review and exact-source research/macOS CI are
pending for this implementation checkpoint. Live AE inventory is NOT RUN;
installation/launch/runtime inspection have not occurred in this pass.

The accepted eight-step proposal authorizes six preparation steps; live step is
conditional on the concrete reviewed packet and actual operation authority.
Previous PICA availability permission was one-shot and is consumed. Do not inspect
or mutate the current AE session during preparation. A fresh exact packet must
identify the new helper, potential suite load, global plug-in iterator and public
file/adapter getters, with one owned blank clean idle session and closed-host
installation guards. No forced quit, project reset or removal of loaded helpers.

INV-07/08 remain NOT RUN pending that gate. Registration/apply/render NOT RUN,
backend NOT READY. Cleanup retains previous installed inert helper/session,
proprietary SDK, known/third-party plug-ins and historical/private evidence.
Only owned temporary test workspaces are disposable. No main merge or release.
