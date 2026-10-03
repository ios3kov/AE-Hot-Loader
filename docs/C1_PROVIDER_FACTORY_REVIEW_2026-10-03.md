# C1 PluginImpl and canonical factory retention — bounded file review

Stage C1, Development. Starting clean research HEAD
`c45dca7d3c46908af99122235d454e3cd5946773`; adopted rules **6.2.0**,
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`. AI_ENTRYPOINT, PROCESS
API-SOURCE-001/SAFE-001/regression/evidence, ENGINEERING debugging/compatibility,
TOOLS diagnostics and NATIVE ownership apply. Collector maintenance is Standard;
dependent private host implementation remains Critical and blocked. Product
scope unchanged; no Validation/Release or installable candidate delivery.

Continue [effect dispatch](C1_EFFECT_DISPATCH_REVIEW_2026-10-02.md): its file path
calls canonical registration before PARAMS_SETUP and dispatches a saved procedure,
but actual provider lifetime and transactional rollback remain unproven.

## Acceptance and boundaries

RETAIN-001: pin original PluginSupport/TDB files before/after, collect complete
bounded functions for PluginImpl initialization/load/free/entrypoint/module and
canonical registration/get/unregister. Reject changed input, anchors and coverage.
Separate lock/reference/map/callee observations from safe runtime semantics.
RETAIN-002: implement one bounded file-only mode with explicit unknown runtime
identity/lifetime/thread/rollback claims; preserve existing modes, source identity,
archive inventory/hash checks and owned-tool/refusal behavior.
RETAIN-003: focused refusal tests, all-mode clean-source collection, independent
archive/raw branch verification, full available local regression/static review
and exact-source CI. Update canonical status and compatibility at closeout.

No AE launch/attach/process read/install/private invocation/scan/retain/teardown
or retry. Prior live authority remains consumed. Original checkout/plugins/session
and native helpers/ResourcePassGate remain preserved. Data-only input identity
may be extended for the new TDB file; it does not authorize a live binding/call.

## Input baseline / prepared checkpoint

Exact AE 25.6x101 arm64 research configuration, not broad AE compatibility.
PluginSupport existing profile SHA-256
`4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`,
UUID `64C01AC4-2413-3463-8822-17EE5543052A`.
New TDB SHA-256
`c40f65989078368f63302050edc42315873dbbd71949324ddc79f01753f2d7d5`,
UUID `CEFA11E1-A795-318C-B7C2-B3FE4213618D`.
Both exact paths are in the original app; owner/link/size/path checks and unchanged
hashes before/after symbol inspection PASS. Private baseline locator:
`../private-live/provider-factory-baseline-9ijhbyxj`. This locates functions only;
complete-body findings and clean-source acceptance remain pending.
Backend NOT READY; actual registration/apply/render/release remain open.

## Complete-body file findings

Fourteen complete windows cover **1365 instructions and 146 anchors**. Preliminary
private bodies: `../private-live/provider-factory-bodies-plgejz29`; these were
collected with explicit dirty/preliminary scope and are not clean-source evidence.

- PluginImpl initializes a recursive mutex and zero module/shared-control fields.
  Init reads metadata and retains/replaces an interface reference through virtual
  calls; later metadata reads can fail. Its receiver/interface and virtual targets
  remain private and unobserved in the running host.
- Load locks that mutex, creates a main-app module for the static-plugin branch,
  or calls ASL::Module::Load for the path branch. The object stores its module /
  shared-control pair at `0x128/0x130`; returning the pair increments its control
  count (`0x4c4e4`). Negative load status returns an empty pair and optionally
  writes the error. Load uses the arm64 C++ hidden return destination in x8;
  it must not be cast into a guessed C function signature.
- **PluginImpl::Free is a single RET** in this exact file. It does not itself
  unload/release. The destructor decrements retained control counts, invokes
  virtual release when a count reaches its boundary, releases weak controls and
  its interface reference, then destroys the mutex. Callee/final unload behavior
  is not covered; no safe lifetime duration follows from this file evidence.
- GetModuleHandle returns a retained shared pair or empty pair, with a count
  increment at `0x4d384`; this body has no explicit mutex lock. GetEntryPoint
  invokes receiver slot `0x20`, releases the temporary returned shared pair,
  then uses the stored module. Static plugins search nine name/pointer pairs;
  the normal branch converts the name and calls ASL::Module::GetProcAddress.
  The procedure pointer return does not transfer a module reference to its caller.
  Actual vtable/receiver identity, concurrency and provider bytes are not observed.
- Get_AE_StreamFactory returns a file-relative global word; no identity/null
  or caller-thread proof is added. GetCanonicalInstance first checks the factory
  table and then uses a default-emplacement helper for the canonical table.
  It can therefore reach a table insertion path: it is not a generally safe
  read-only runtime probe simply because its name starts with Get.
- RegisterCanonicalInstance locks the factory mutex. When its name lacks a
  factory function, it marks the candidate canonical and calls a virtual method,
  inserts its raw pointer in the canonical table (`0x1f248`), then allocates and
  inserts a callable binding into the factory-function table (`0x1f25c`/`0x1f294`).
  When the name is already registered, it invokes the candidate's virtual release /
  destruction slot and returns the existing canonical value. It does not promise
  to publish a replacement effect. Later allocation/insertion can fail after the
  first map insertion; the local unwind paths release transient state/candidate
  and unlock, without an explicit canonical-map erase in this complete body.
  Transitive destructor/helper effects remain unknown; transactional rollback
  is NOT PROVEN, not declared impossible or identified as a confirmed AE defect.
- UnregisterFactoryFunc_NullOK finds the canonical entry, erases it and then
  erases the factory-function entry, verifying each erase count. A failed second
  verification occurs after the first mutation and can throw. The successful path
  unlocks before invoking the saved canonical object's virtual destruction slot.
  Missing-entry behavior/logging differs by its boolean argument. Lock cleanup
  does not establish transactional restoration of either map.
- UnregisterCanonicalMatchName first obtains a canonical stream/group, recursively
  unregisters its layout when present, then erases another name table under lock.
  The recursive routine copies a layout vector, unregisters the parent and visits
  nested groups / remaining names using the supplied exclusion set. This reaches
  transitive object destruction and multiple tables; it is not a harmless inverse
  call usable as a blanket rollback after a guessed registration sequence.
- GetCanonicalStream performs a locked tree lookup and returns a raw stored
  pointer after unlocking. Canonical stream maps are distinct from the ordinary
  effect registry. A map entry or retained module is not registration/apply/render
  success, and a local recursive mutex is not proof of safe host-thread/MFR use.

## Implementation checkpoint

One new `provider-factory` file mode, fixed complete bounds and exact opcode/state
anchors. TDB's pin lives in **AE256ProviderFactoryFiles.json**, explicitly scoped
`offline-only-not-native-host-profile`, and is checked against fixed collector
inputs including exact schema/scope/inventory. Existing native profile/helpers /
ResourcePassGate stay unchanged; no new TDB native binding is introduced.
Reports explicitly keep actual identities NOT OBSERVED, native ABI UNKNOWN,
safe lifetime/unregistration/rollback NOT PROVEN and registration/apply/render
NOT RUN. Refusal tests precede implementation; clean-source collection, full
regression, static/independent review and exact-source CI remain pending.

Next file-only discriminator: ASL::Module Load/GetProcAddress/final destruction,
and the exact FCSpec virtual/provider reference path connecting PLUG preparation
to dispatch. This block narrows ownership boundaries, not the production ABI.
No live packet is executable; backend NOT READY and release gates remain open.
