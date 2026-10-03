# C1 library lifetime, effect entry and failure boundary — combined batch

Stage C1 / Development. Starting clean research source
`b539c6b42e7b826e24d3bd1d405ef72c2ad9711f`; adopted rules 6.2.0,
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`. AI_ENTRYPOINT routes PROCESS
API-SOURCE-001/SAFE-001/regression/evidence, ENGINEERING debugging/compatibility,
NATIVE ownership and TOOLS diagnostics. Collector work is Standard; dependent
private host integration remains Critical / BLOCKED. This batch combines the
four steps requested in chat; no product-scope change or release candidate.

## Acceptance fixed before body review

- ENTRY-001: pin ASLFoundation before/after; review complete bounded module
  load/create/procedure/destruction bodies, including final shared-owner release.
  Separate CFBundle release, executable unload and live lifetime claims.
- ENTRY-002: follow FCSpec descriptor retention/procedure retrieval into the
  existing PLUG preparation and host dispatch evidence. Confirm serialized
  virtual-table correspondence from exact files where possible; never treat
  serialized words as observed runtime receivers or callable ABI.
- ENTRY-003: combine load/lookup/partial publication/parameter failure findings
  into an explicit failure and recovery contract. Do not invent transactional
  rollback or call private teardown to test it.
- ENTRY-004: add a bounded file-only collector mode and refusal checks; collect
  all modes at a clean source, independently verify archives and original bytes,
  run available regression/static review and exact-source CI. Prepare a concrete
  future AE trial sequence with mandatory blockers, separate registration,
  application and render acceptance, and explicit stop/preserve behavior.

No AE launch/attach/process read/install/script/private invocation/scan/retain/
teardown/retry. Prior live authority is consumed. Original checkout, plugins,
session, native helpers/profile and ResourcePassGate are preserved. New ASL file
identity belongs only to the offline pin manifest.

## File baseline / prepared checkpoint

ASLFoundation exact path:
`/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/ASLFoundation.framework/Versions/A/ASLFoundation`.
SHA-256 `f1c3c7256f8a986f39519387511436577a3d65fb9d04a672bbb115c1871a3fe7`;
arm64 UUID `408BB5BB-BD1A-31AC-9FA6-E033644CE8EE`; size 485376 bytes.
Owner/link/absolute non-symlink path/hash and bounded symbol inspection PASS.
Private locator: `../private-live/entry-lifetime-baseline-fs1xz3g1`.
This checkpoint establishes input identity, not body findings or clean-source
acceptance. Exact AE 25.6x101 arm64 scope; no broad compatibility claim.

Backend NOT READY. Actual registration/apply/render/release remain open.

## Complete-body findings and combined chain

Preliminary bodies in `../private-live/entry-lifetime-bodies-w8_q3326` have dirty,
file-only scope. The implemented mode separates the FCSpec descriptor-release
body (`0x5cbec–0x5cc60`) from the following constructor thunk; nm aliases at
`0x87a0` include both a counted-pointer destructor and **UnloadPlugin**. The
correct named callee is recorded, rather than trusting one LLDB alias.

1. PluginImpl Load stores a module/shared-control pair, as established by the
   [provider review](C1_PROVIDER_FACTORY_REVIEW_2026-10-03.md). ASL Load performs
   SecStaticCode creation/validity checks, creates a CFBundle, then calls Module
   Create (`0x23cc8`). Its failure paths return a negative private result or
   unwind; they are not a security-bypass route. Create allocates a Module,
   retains its bundle (`0x24210`), builds a shared control, publishes the pair
   (`0x24234`) and releases the previous control. Allocation/exception paths
   differ from a successful replacement; no general atomic-load claim follows.
2. GetProcAddress locks a global recursive mutex and calls
   CFBundleGetFunctionPointerForName (`0x24674`). Apple documents that this API
   may load executable code while resolving the function:
   [official API contract](https://developer.apple.com/documentation/corefoundation/cfbundlegetfunctionpointerforname%28_%3A_%3A%29),
   consulted 2026-10-03. This public API statement does not prove what happened
   in AE. The private body restores exception state/unlocks on normal completion,
   can return zero on its handled error lane, and has an intentional-crash lane
   (`0x249f8`). A name lookup is not automatically a read-only live diagnostic.
3. PLUGp_LoadPlatRoutine obtains a descriptor entry name and calls
   PLUG_RoutineDescPriv::GetEntryPoint (`0x108e8`), writes the result into the
   descriptor's `+0x8` field (`0x108f0`), then marks flags after a nonzero result.
   GetEntryPoint checks a cached pointer, otherwise requires provider fields
   `+0x48/+0x50`, calls receiver virtual slot `0x68`, and caches its return
   (`0x10bd4`). Actual receiver/vtable identity at this virtual boundary remains
   unobserved. Its conditional `+0x60` path gets temporary module references and
   calls SetUnloadOnDestroy(false), then releases temporary controls. It returns
   a raw procedure pointer, without transferring the module pair to the caller.
4. FCSpec retains its descriptor/control at `+0xc0/+0xc8`. GetRoutineDescH uses
   the C++ hidden destination x8 and increments the Boost count; SetRoutineDescH
   retains the incoming pair before replacing/releasing the old one. Constructor
   initializes that pair and the separate procedure field to zero; destructor
   releases the descriptor control. The already reviewed ReadyFilter prepares
   that descriptor and copies its `+0x8` procedure into FCSpec `+0xd0`
   (`0x5d03c`, alternate `0x5d090`). SetEffectProc atomically exchanges this
   field; GetEffectProc uses an acquire load. These atomics do not establish
   provider ownership or quiescence for concurrent host work.
5. The exact serialized FCSpec table has address point `0xd5c80`; slot `0x10`
   (`0xd5c90`) rebases to GetEffectProc `0x5e2f0`. Its constructor installs this
   table in the file. This connects the slot used in the prior
   [host dispatch review](C1_EFFECT_DISPATCH_REVIEW_2026-10-02.md) to the saved
   procedure for this file class. It is conditional on an actual FCSpec receiver;
   the running host's receiver, descriptor and function image were not read.
6. ASL shared-control slot `0x10` rebases to `__on_zero_shared` `0x27ca8`, which
   calls the Module deleting-destructor slot `0x8`; the Module table maps that to
   `0x2449c`. All complete/base/deleting destructor instructions are bound by
   anchors. In these exact bodies, the unload flag is zeroed and string/object
   storage is reclaimed; there is **no CFRelease(bundle), CFBundleUnloadExecutable
   or dlclose call**. SetUnloadOnDestroy only stores a byte in its complete body.
   These observations prevent assuming that final shared release unloads code.
   They do not establish process-wide permanence, a leak, safe provider unloading,
   or actual runtime virtual targets.

Twenty-three bounded complete bodies/thunks cover **1351 instructions / 225
anchors**; three tables cover **32 serialized words / 29 rebases**. Data validation
rejects changed targets, bind/reserved/high-address words, missing/duplicate/wrong
fixups and another pointer format. Original file pins and clean-source evidence
are required separately. Native helpers/profile and ResourcePassGate unchanged.

## Failure and recovery contract

| Trigger | Observed exact-file behavior | Safe tool response / unresolved gate |
| --- | --- | --- |
| Signature/bundle/module allocation fails | ASL negative result or exception; PluginImpl returns an empty module pair on its error lane | Stop once; record status and input identities. Do not bypass signature checks or assume an unchanged previous module from the status alone. |
| Entry name empty | PLUG adds to the incompatible-plugin registry, clears descriptor procedure, returns failure | This is a mutation. Do not use it as an observational probe or rescan automatically. |
| Name exists but function lookup fails | Lookup can load code; PLUG writes zero, reports a missing entry and translates/catches errors | Image visibility or zero preparation status cannot substitute for a nonzero, identified entry. Preserve loaded state; no speculative unload. |
| Preparation succeeds | Descriptor flags/counts and cached procedure are changed; FCSpec later copies the pointer | Prove exact owner and receiver correspondence before dispatch. Atomic cache operations alone do not prove shared lifetime. |
| Canonical publication or PARAMS_SETUP fails | Prior reviews show map insertion before later allocation/setup; local cleanup is not a proven inverse | Stop after the one attempt; independently compare full registry/project/module state. No recursive unregister, callback replay or automatic retry. |
| PLUG "unload" is called | Conditional UnloadPlugin is RET at `0x87a0`; platform body clears descriptor procedure/flags on its success lane | No full factory/FCSpec/global-state rollback or executable unload is established. This function is not approved recovery. |
| Host lookup/dispatch throws, hangs or crashes | Private handlers have translated-error and intentional-crash lanes | External supervisor records timeout/unknown outcome and disables continuation. Preserve evidence; do not terminate/restart the user's AE or retry. |

The combined evidence narrows recovery to **stop and preserve** until ownership,
quiescence and a reviewed inverse are proven. This is not a claim that AE itself
has a rollback bug; transitive behavior and actual live state remain unknown.

## Concrete future AE trial design — BLOCKED, not an executable packet

This design keeps the existing single-root resource route in
[PRODUCTION_PLAN](PRODUCTION_PLAN.md). It does not select direct private function
casts, canonical Get-as-read probes, replay of general-plugin startup, or provider
unloading. No new live action or installable helper is prepared by this batch.

Mandatory preparation before an executable packet:

- Resolve actual provider/interface/vtable correspondence, descriptor and entry
  ownership, host-thread/idle/MFR quiescence, and resource end-of-pass publication
  isolation. File targets and a mutex are insufficient. If a fresh diagnostic is
  needed, design only bounded copied fields with mapping/identity/rebind checks;
  no GetProcAddress/GetCanonicalInstance/private retain call as a read substitute.
- Implement/review a new one-shot adapter and supervisor, prove inert/refusal
  behavior offline, then bind exact clean source, SDK/header inputs, helper Build
  ID, package/binary hashes and target AE/OS/arm64 identities. Existing installed
  helper's identity and authority are historical and cannot cover this packet.
- Prepare one fresh owned embedded effect using `AEHL.Embedded.<12 hex>` and
  exact verified PiPL/file inventory. The consumed historical fixture is excluded.
  Existing `apply_registration_probe.jsx` accepts `AEHL.Dynamic.*`; it therefore
  needs an explicitly reviewed fixture-compatible adapter before C2. Do not widen
  its check blindly or reuse the hardcoded Rust/startup demonstration as proof.
- Fix exact installation paths/no-overwrite preservation, copy inventory,
  supervisor time budget and one-attempt claim, archive verifier, permitted state
  deltas and operation authority in the final packet. Missing safety prerequisites
  block execution even if the future validation question is already approved.

Proposed sequence once all those prerequisites pass:

1. Fresh preflight identifies one AE process, exact loaded helper/providers and
   a blank, unsaved, clean, idle disposable project. Snapshot complete registry,
   project revision and image identities. Intended embedded match must be absent;
   unrelated projects/processes or identity drift stop before the claim.
2. Consume one new Run ID/claim and perform one bounded resource pass on the
   fixture's verified root, preserving existing GeneralPlugin records. Observe
   provider → descriptor → cached function → FCSpec correspondence using only the
   reviewed adapter. A failed/unknown outcome disables remaining steps.
3. Registration PASS requires exactly one new intended registry identity in the
   same PID/start identity, unchanged project, and no unrelated registry changes
   or removed/replaced existing images. New fixture image identity is recorded;
   image loading alone is insufficient. Independently verify the evidence archive.
4. Only after registration PASS, and under scoped project-edit authority, create
   one owned 64×64, 8-bpc, one-second composition with one known solid. Apply that
   exact installed effect key; record the instance and expected parameter schema.
   Application PASS is separate from registry presence. Fixture algorithm/schema
   must be fixed and independently verified in preparation, not invented after AE
   returns a result.
5. Render a fixed frame into the run's new owned output directory; verify format,
   dimensions, decoded pixels against the fixture's deterministic expected output,
   output hash and observed command completion. A PNG's existence or a preview
   alone is insufficient. Registration/application/render get separate results.
6. Close the attempt by preserving host/project/plugin/evidence state. No private
   unregister/unload, automated retry or forced AE quit. Safe artifact removal or
   host close requires its own reviewed ownership/preconditions and authority.

Failure-injection tests for signature/entry/params/canonical failures first run
on owned offline fixtures. A later host failure trial requires a separate packet;
the positive registration trial cannot silently add intentional-crash cases.
This sequence is a prepared validation design, **NOT RUN** and **BLOCKED** on the
mandatory semantics/safety/identity/authority above. Backend NOT READY.


## Clean-source verification — local and exact-source CI PASS

Code/test source **50e93973309fbff0b65e37b7c6cbb26e4b9422ad**. Focused collector
suite **32 PASS**. Four new tests and the extended offline pin expectation first
failed against the previous implementation as expected. Refusal coverage binds
all 225 changed anchors, duplicate/incomplete/unreviewed windows and altered table
rebases/targets/bind/reserved/format/coverage. Both offline-only input hashes and
retargeted collector inputs are checked; neither enters the native profile.

All **nine** modes collected at this clean source. New archive
`build-ae-hot-loader/resource-entry-lifetime-e3a0a2f8-7icvxdxa.zip`, SHA-256
`16422ccf644f8045b1b4ba30d83e64620ea6d1a73626e390c2feff537abe7588`,
contains 61 members. Original ASLFoundation/FLT/PLUG pins unchanged before/after.
Offline pin manifest SHA-256
`f9dba1e09f96d937f25eb0c4d22b4b872a8c570408b22324e45137a79ad745f1`.

Independent verifier `../private-live/verify_entry_lifetime_20261003.py`, SHA-256
`97378b67f632fbdf9a975231b8e2273c9b3d9c2712f8c99df1878796a0ea24ed`,
checks exact ZIP inventory/CRC/member hashes/source and complete decoded coverage
for all nine archives. For the new mode it independently decodes **all 264 direct
B/BL and 22 indirect BR/BLR** from original arm64 Mach-O bytes, compares all 32
serialized words to original bytes and walks original LC_DYLD_CHAINED_FIXUPS pages
to prove membership/targets of **29 rebases**. This supports file correspondence,
not an actual live receiver or safe lifetime. Result
`entry-independent-50e9397.json`, SHA-256
`318214e378aaa6c25995dfdd0e0c4fae25bd75c8ac6056c2e729282c058b8b35`.

Full local available regression **372 Python/no skips, 62 Node, 22 stages PASS**.
Report `/private/var/folders/bs/39klz7cd52z6xkm817vj0zjm0000gn/T/AEHL-checks-ycl86uds.zip`,
SHA-256 `4c39bf96cb11d7344e06022d6471422eb2f6004a397184e2333af15821a84e4e`.
Independent archive/303 tracked source hashes/unchanged-source verification PASS;
`entry-local-independent-50e9397.json`, SHA-256
`f379658d59e35eeea4df8e5e579cee78b46b9032b9fa791798bc5a0aa1e66cad`.
Live operations false; full AE pipeline BLOCKED and product package NOT RUN.

Bounded source/static review completed at exact source; scanner snapshot covers
658 text files, no inventory omissions, 418 unsupported files and four workflows,
all selected checks completed. Raw exit 1 retains the sole known heuristic
`vibe.no_ratelimit_auth` at `tools/artifact_manifest.py:71`; reinspection confirms
local argparse with no HTTP auth route. No suppression or security certification.
Snapshot `entry-audit-50e9397.json`, SHA-256
`ce669e1fc55e646bf23d03978a7c298a3325ba988bd8985191f526c9a1b2d0ab`.
History, runtime/browser/authorization/performance/rollback/dependency-vulnerability
checks are not assessed by that scanner. Native helper/profile/gates unchanged.

Research CI [37117715670](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37117715670)
and macOS CI [37117715623](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37117715623)
both completed/success at exact 50e9397. Private final receipt
`entry-ci-50e9397-final.json`, SHA-256
`d1a1afdf8c5adc20ec7a2fff6aa499e9a8ad701acd72fb3e4b2168cb922c1e11`.
CI build/sign/package/owned synthetic checks do not prove AE loading, late
registration, application or rendering. No runtime gate is promoted.

ENTRY-001/002 complete in bounded file scope; ENTRY-003 produces the reviewed
failure/stop-and-preserve contract; ENTRY-004 offline verification and trial design
complete. The trial itself remains BLOCKED/NOT RUN, with mandatory prerequisites
explicit above. Backend NOT READY; main/release/installed artifacts unchanged.

Next file-only locator prepared at
`../private-live/entry-next-provider-locator-rricv5va`: PluginSupport complete
constructor `0x4bb34–0x4bbd0`, vtable `0xab500`, VTT `0xab5f0`, next construction
table `0xab648`. Existing exact PluginSupport pin unchanged before/after bounded
symbol/serialized-word inspection. This is preliminary location data only, not
new body/virtual target semantics or clean-source acceptance. Next stage reviews
provider/interface construction and virtual-table correspondence, then remaining
resource publication isolation and host-quiescence contracts before a live packet.
