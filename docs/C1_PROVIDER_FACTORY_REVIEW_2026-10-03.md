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

## Clean-source local and exact-source CI verification — PASS

Implementation source **49a85318fcfb884315b9d36d3cb4b74a094a0399**.
Focused collector suite **28 PASS**. Four new tests were first run against the
prior implementation and failed as expected; the completed mode rejects every
changed anchor and duplicate/incomplete/unreviewed coverage. File-only pin tests
reject scope/schema/hash/inventory changes and a retargeted collector input.
During implementation the first import check caught a misplaced report block;
it was corrected before the clean commit, and no host action was involved.

All eight modes collected successfully at the same clean source. New archive
`build-ae-hot-loader/resource-provider-factory-e289a072-0hvk_ie_.zip`, SHA-256
`840565d3276b899608cb30f8a1226414029dbad494e125da6a3fcba27f9d1b12`,
contains 32 members; **14 complete bodies / 1365 instructions / 146 anchors**.
Original PluginSupport/TDB pins match before/after. TDB's separate file-only pin
manifest SHA-256 `95efd474139c90f322dbfadfed8aeef9570637adf7628bc459646f3cfc080171`;
the native profile remains unchanged.

Independent verifier `../private-live/verify_provider_factory_20261003.py`,
SHA-256 `ace588c499bb8dc863ed47ccaffff1074c11919f8c1034cd2835d32023f712cb`,
verified archive SHA/CRC/exact manifest inventory/member hashes/source, complete
coverage, original input pins and **all 257 direct B/BL and 26 indirect BR/BLR**
in the new mode from original arm64 Mach-O bytes. This confirms instructions,
not actual recipients. All eight archives PASS; result
`retention-independent-49a8531.json`, SHA-256
`a9a1d0e450824a90c92571dd95a7744552c87c5d2c5267bcadc54d2c7cfe38d1`.

Full local regression **368 Python/no skips, 62 Node, 22 stages PASS**.
Report `/private/var/folders/bs/39klz7cd52z6xkm817vj0zjm0000gn/T/AEHL-checks-k5l7kfs_.zip`,
SHA-256 `e9f0b32e8783972837aa5cef7542d333950130dd428688fc985ca48df3f6be94`.
Independent ZIP inventory/CRC/member hashes / 302 tracked source hashes / unchanged
source PASS; receipt `retention-local-independent-49a8531.json`, SHA-256
`f53814efb0792f7285ffa4ae0e367c0f6f45aa8dfe81512268e8cdb97bd8a841`.
Live/product/release gates remain BLOCKED/NOT RUN, not promoted by this runner.

Bounded source/static review complete. Scanner `retention-audit-49a8531.json`,
SHA-256 `8d5cfefe139fb4bb4d822b98cd7d5dca1f0abfa9d4a80961a9209d620bb82cc8`,
records 657 text files / no inventory omissions / 4 workflow files inspected.
Scope includes ignored text evidence and omits unsupported files/history/runtime/
dependency-vulnerability checks. Raw exit 1 retained: the sole known
`vibe.no_ratelimit_auth` at `tools/artifact_manifest.py:71` is a local argparse
entrypoint. Manual source review confirms this false positive; no suppression.
The bounded scanner is not security or release certification.

Both GitHub workflows completed/success on exact implementation source:
[research CI 37116821256](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37116821256)
and [macOS CI 37116821279](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37116821279).
Private final receipt `retention-ci-49a8531-final.json`, SHA-256
`b598e36c4e6aecbcf74524dd0810e8f075f142e92cc17f170c23319494b21719`.
CI build/sign/package/synthetic checks are not actual AE loading/rendering.
RETAIN-001/002/003 PASS in their bounded offline scope.
No native/live binding or AE action. Backend NOT READY; ordinary-effect late
registration/apply/render remain NOT RUN, historical registration FAIL unchanged.

## Next-scope locator

Private locator `../private-live/retention-next-locator-crwq107i` rechecked the
existing FLT file pin and located GetRoutineDescH (`0x5d0dc`), SetRoutineDescH
(`0x5e26c`) and GetEffectProc (`0x5e2f0`). No bodies/vtable correspondence were
collected in this locator; actual runtime identity remains unobserved. The next
review must separately pin ASLFoundation before examining the Module callees,
and establish the exact FCSpec reference path before calling a saved procedure.
Do not infer a safe lifetime contract from the slot names or shared-pointer words.
