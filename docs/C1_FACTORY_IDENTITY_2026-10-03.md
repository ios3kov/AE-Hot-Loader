# C1 factory code identity and construction

Stage C1 Development; accepted rules v8.0.0 /
132b7cd32873ba7328e3128ffbb33e1929b74d45. Starting clean source
fcc99577601ead31c6f8a365dd5eb677252b920a. FACTORY-01–08 acceptance recorded
in [production plan](PRODUCTION_PLAN.md) before new body collection. Native
code identity Critical, bounded file collector Standard; source/thread/ownership,
refusal/repro/task-close/cleanup apply. Existing verified SDK25.6_61 API inventory
reused: no new Adobe call, private callable ABI, receiver acquisition or invocation.
Original arbitrary ordinary-effect/no-restart product and A/B/C1/C2/D/release retained.

## Reviewed file boundary

Nine complete arm64 windows /643 instructions /533 structural anchors, all <=4096
bytes, in existing pinned AE25.6x101 PluginSupport and MEE files. Initial six bodies
extended only to actual direct tree insertion, KnownPlugins allocation and factory
allocation delegates; complete bodies end at next exact text symbols. Preliminary
dirty capture is discovery, not clean acceptance. LLDB uses no dependents, process,
expression or call. Original binaries/full inventories/disassembly not committed.
PluginSupport SHA256 4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832,
UUID64C01AC4-2413-3463-8822-17EE5543052A; MEE SHA256
18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344,
UUID74a30dba-a08b-367b-bd99-15d6d77e9d52. No broader compatibility claim.

| Complete window, end exclusive | Instructions |
|---|---:|
| factory-register /PluginSupport 0x52d28–0x52fec | 177 |
| factory-known-holder /PluginSupport 0x5f404–0x5f46c | 26 |
| factory-known-init /PluginSupport 0x65dec–0x65df0 | 1 |
| factory-known-get /PluginSupport 0x65df0–0x65ed4 | 57 |
| factory-map-emplace /PluginSupport 0x550b0–0x5521c | 91 |
| factory-known-new /PluginSupport 0x6319c–0x63208 | 27 |
| factory-ctor /MEE 0x73e4–0x7410 | 11 |
| factory-classref /MEE 0x43944–0x43c0c | 178 |
| factory-allocate /MEE 0x43c38–0x43d64 | 75 |

## Factory registry versus metadata holder (FACTORY-01)

RegisterPluginModuleFactory checks null interface at 0x52d54/0x52e38; a missing
receiver reaches ThrowError rather than legitimizing a guessed pointer. It copies
GUID/interface, atomically retains a shared owner at 0x52e60 and invokes unique
emplacement at 0x52e7c. ADRP/add 0x52e6c/0x52e70 select factory tree 0xb1218.
Emplace compares GUIDs; an existing-key return sets w1=0 (0x55200). Register's
caller does not expose insertion success. New-node branch allocates72 bytes,
stores interface at node+0x30 (0x55144), paired ownership at +0x38 (0x5515c),
consumes input owner fields, publishes node (0x55170), balances tree and increments
count. Local retained references release on normal/unwind exits. There is no
explicit body-wide mutex in these two bodies; outer/transitive synchronization is
UNKNOWN. This is factory registration, not effect registration or replacement.

KnownPluginsHolder is distinct: call_once delegates 0x5f448→0x65dec→0x65df0.
Guarded static Get allocates an0x88-byte holder through0x6319c and stores its
pointer at0xb0f00 (0x65e44), builds a shared-control owner and registers atexit.
Its containers and guard do not make it the factory receiver tree at0xb1218.
Previous FindPluginFactories metadata selection must not be mistaken for actual
receiver/registry ownership. No live object was read or retained here.

## Constructor and shared reference (FACTORY-02)

MEE constructor writes primary vtable0xef640 at object+0, secondary0xef6b0 at
+0x38, and zeroes selected fields. File-only data scope captures11 primary slots
0xef640–0xef698 (end exclusive). Every slot is a plain format6
DYLD_CHAINED_PTR_64_OFFSET rebase verified against dyld_info fixups. Primary
slot+0x28 decodes to CreateUnknown0x7b1c, consistent with prior AddPlugin's virtual
slot+0x28. This is file correspondence, not an observed actual virtual receiver.
Adjustment/header words after these11 slots are excluded and not decoded as pointers.

CreateClassRefInternal holds a singleton mutex (0x43988), locks a weak owner
(0x4399c), reuses an existing strong reference; absent + creation flag false goes
to null output (0x439cc). Creation true allocates through0x43c38, calls ClassWatcher
AddObject and updates weak ownership. Allocation helper uses an0x68-byte recycled
block; object begins at+0x18 and constructor runs at0x43c8c. Output records primary
object and paired reference fields, computing a virtual-base-adjusted interface from
vtable[-0x38] at0x43adc/0x43ae0 and storing it at0x43ae8. Object address and returned
interface address may differ; a hard-coded equivalence is unjustified. Normal/unwind
releases and mutex unlock are present. Singleton locking is not host-wide admission
or render drain; invoking creation can mutate singleton/ClassWatcher state.
Transitive methods and valid private receiver/argument/lifetime contracts UNKNOWN.

## Implemented code identity (FACTORY-03/04)

NativeFactoryCodeIdentity.hpp adds bounded Describe/SpanBytes and main-thread-only
Bind. Describe accepts1–8 unique ordered nonoverlapping code spans (aligned,1–4096
bytes) inside the arm64 executable text of a direct-code-export-identified image.
Bind never loads an image: existing resident resolver verifies exact path/file SHA,
UUID, mapped header and whole text; each immutable reviewed span additionally needs
its nonzero exact SHA256 and matching mapped bytes. Stable before/after image
snapshot and overflow checks precede return of integer diagnostic addresses/sizes.
No factory object dereference, callable pointer, ABI, reference lease or gate approval
is returned. Lifetime is point-in-time; continuous safety at later use is unproved.

AE256FactoryIdentityProfile.hpp is a separate immutable identity-only MEE profile,
not automatically connected to a host helper/gate. Its anchor is the direct exported
MEE_GetAELibPluginSetter, used for identity only, never called. Full code spans:

| Tag | Extent | SHA256 |
|---|---|---|
| ctor |0x73e4–0x7410|bc53c9b096b11f55b7793a695b1bedc0ae71c3711c685b8a157dedd0b9de5142|
| create_unknown |0x7b1c–0x7dc8|31107d3f0a91bd1e70ac2b43aa470bcf0d9df51545232d1d09d3786c2bac37f4|
| classref |0x43944–0x43c0c|d83f18648d10cd58e84460929e30e0a209b6a659ea03a67a57b73ed183a054a3|

CreateUnknown's complete body was reviewed in the previous admission checkpoint;
its identity hash is not new ABI proof. File-only compiled profile check on original
MEE PASS: three span hashes/UUID/export/text match, zero Adobe loads/calls, no
resident MEE binding. Original bytes/pins preserved.

Three focused tests PASS, including real fresh owned arm64 dylib: binder refuses
absent image, then exact address correspondence matches the test's dlsym results;
file hash/UUID/span hash/zero hash/bounds/count/thread mutations refuse. Only the
test loads/unloads its owned library; no Adobe invocation. First TDD run failed for
missing implementation; first implemented run exposed contradictory protection
ceiling acceptance. Shared ResidentImageBinding parser now requires maxprot=5 as
well as initprot=5. Reviewed original MEE and fresh native fixture have5/5; fixed
focused run PASS. This is a real parser correction, not relaxed acceptance.
Four new collector tests exercise coverage/anchors/table rebase refusals/catalog;
61 focused collector tests PASS. Owned synthetic controls do not prove AE runtime.

## Required next gate and reconciliation

FACTORY-01/02 bounded original findings documented;03 component implemented;
04 focused owned native/file-profile checks PASS;05 collector/refusal implementation
PASS. FACTORY-06 clean capture, separate original byte/archive/source review,
full checks/scanner/exact-source CI PENDING at this pre-commit checkpoint.
FACTORY-07 durable retention/status/handoff/cleanup PENDING final closeout.
FACTORY-08 BLOCKED: actual retained factory receiver, supported callable late ABI,
continuous host reader/render admission, completion/drain and full effect rollback
are still missing. Generic launch authorization is received; these are technical
gaps. AE launch/attach/install/private invocation, registration/apply/render NOT RUN.
Code identity progress is not completion of the real ResourcePassGate backend.

## Exact clean-source closeout

This supersedes the pre-commit PENDING research checks above. Exact clean tested
code e70d13c693977449e27cf50dcb3e5a388e08a87e. Subsequent closeout changes documentation only;
its later SHA does not receive the preceding code checks by implication.

| Task | Acceptance / procedure | Actual result |
|---|---|---|
| FACTORY-01 | Complete factory insertion/ownership versus metadata holder | Bounded file findings documented, raw root/node fields verified; actual receiver UNKNOWN |
| FACTORY-02 | Complete ctor/classref/allocation/metadata initialization, normal and unwind exits | Bounded file findings documented; mutex/creation flag/weak/shared owner/base adjustment separated from host transaction |
| FACTORY-03 | Concrete bounded resident code identity and immutable exact MEE profile | IMPLEMENTED; no callable ABI/receiver/lease/gate capability returned |
| FACTORY-04 | Actual owned dylib address correspondence, absent/hash/UUID/code/count/bounds/thread refusals; exact original-file profile | PASS; zero Adobe load/call, original profile resident binding NOT RUN |
| FACTORY-05 | Narrow fixed collector, complete coverage/symbol/table/anchor refusal controls | PASS; 61 collector +3 native focused tests; actual owned LLDB and dylib controls separately identified |
| FACTORY-06 | Exact clean source collection, separate raw-byte/fixup/archive/source review, all checks/scanner/CI | PASS research verification; raw scanner review-required exit1 retained, no runtime/release certification |
| FACTORY-07 | Status/plan/handoff/compatibility, immutable private receipts, ownership-aware cleanup | COMPLETE this bounded block; original product and open acceptance retained |
| FACTORY-08 | Actual retained receiver + callable late ABI + continuous host admission/drain/rollback + native trial | BLOCKED missing technical contracts; AE/registration/apply/render NOT RUN |

- Clean file-only collection `resource-factory-identity-6311418b-umyhgeul.zip`,
  SHA256 b10b56a1b6b3edae3246a7de7b6192a139901f27590f9cc72d5102fd6ecbf472, 26 members;
  exact fixed bounds/533 anchors/decoded coverage/pins before-after, CRC/payload
  hashes and equality to exclusive owned output PASS. Adobe calls zero.
- Separate verifier `aehl-factory-independent.py`, SHA256
  2eeca65c7a3de640b172224d6301b360350011a4e89ec3f4800f3f6b70e90330; no collector import.
  Independently maps original fat arm64 Mach-O bytes: 643
  instructions, 88 direct/55 conditional/
  8 indirect branches/9 returns verified.
  Raw registry0xb1218 versus metadata0xb0f00, ctor primary/secondary tables,
  interface output/base adjustment, eleven serialized words/rebase fixups and
  three literal profile fingerprints PASS. Receipt SHA256
  cf7ae440539443f4805143f37ead4907d234a73dd15654345496fc4d8312f0b6. This corroborates selected
  original fields, not every transitive semantic side effect.
- Full runner `AEHL-checks-tkgzfqbo.zip`, SHA256 cef9fbfb86a960ce79a8aacc4304fe96e84a81454135e6dd2fd2efc20a4a12bc,
  25 members; 440 Python tests, zero skips/failures/errors/expected
  failures/unexpected successes, 62 Node, all22 stages PASS. Python73.417 seconds.
  Original parser regression included. Independent ZIP CRC/manifest/payload
  hashes/all341 tracked working bytes and exact-source Git blob checks PASS.
  Inventory SHA256 fb7dbba616d931674d1a1be28f9c321326abd7356d570ac6d26ee6713952318f;
  clean source and source_unchanged_after=true. Source-proof SHA256
  a74af52793827ad46b753d579195b0610dfe36a6d744b4c137eddea7653d3ccc.
- Clean-source strict C++17 original-file profile check PASS, three span hashes/
  UUID/direct export/text; zero Adobe loads/calls, resident binding NOT RUN.
  Receipt SHA256 24785d29ee7184805b9af555bd8382d79cf51d2f5883cdc50361dbea52ec28dd;
  owned executable removed by lifecycle. TDD preserves initial missing-header
  failures, real protection-ceiling failure, corrected/final focused logs and
  initial four expected missing-mode collector errors. No test acceptance relaxed.
- Scanner `aehl-factory-e70d13c-audit.json`, SHA256
  861bf06f08fa1b6970cce587a9b99f5e230683d5498a04368ab35743d6cc8f97; raw exit1,
  review_required, release_readiness=not_assessed. Sole vibe.no_ratelimit_auth
  at tools/artifact_manifest.py:71 inspected in exact source: local argparse
  manifest CLI, no HTTP/auth route/listener. False positive, original raw output
  retained without suppression. Separate code/scanner review SHA256
  80b9dcabddedfe981e9e060866541df9c4f47097790fa0d83c40576c4519829e.
- Research CI [37137765177](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37137765177) and macOS CI
  [37137765153](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37137765153) both completed/success at exact e70d13c693977449e27cf50dcb3e5a388e08a87e.
  Research/native internal build checks do not establish AE registration/render.

## Retention, cleanup and next dependency

Private owned receipts retained under
`build-ae-hot-loader/factory-closeout-e70d13c-s7hx1tq2`: byte-identical collection/runner archives,
separate verifier/receipt/source proof, raw scanner/code review, TDD/native/focused
logs, original profile fingerprint inventory and clean-source compiled profile
check. Original RETENTION.json SHA256 e9c85645f8391539eb90b1c955692efba960dd81fa10db33edb578c1a511771a;
CI.json SHA256 e92cf1ac59418f1352810eb0935cc486320d6190deb4d672fdfcc64ae7ea5bc4. Final complete receipt hash
inventory recorded separately in CLOSEOUT.json after documentation reconciliation.
Only temporary binaries created by these tests were removed; old/shared/loaded/
unknown/preliminary evidence preserved. SDK/app/plugin/project/session untouched.
No rescan, AE launch/attach/install/private call, teardown/unload, preferences/cache
cleanup, merge or release. Rules/product/remaining stage obligations retained.

Next dependency remains actual supported retained receiver acquisition plus a
continuous late host transaction providing all-reader/render exclusion, completion
and whole-effect rollback. File classref signatures/pointer offsets/private symbols
are discovery evidence only. Identity fingerprints and diagnostic integer addresses
cannot establish call consent/ABI/ownership or satisfy ResourcePassGate on their own.
