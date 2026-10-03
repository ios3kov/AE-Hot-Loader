# C1 transitive class factory and ownership boundary

2026-10-03, Stage C1 Development research. Rules8.0.0 /
132b7cd32873ba7328e3128ffbb33e1929b74d45, AI_ENTRYPOINT first. Clean baseline
f7ba6caa9cb713a3728532cb33e56c4bfad7521d. User “давай снова целый пак шагов
в одном прогоне” continues same arbitrary ordinary-effect/no-restart product.
TRANS-01–08 recorded before body capture in [production plan](PRODUCTION_PLAN.md).
Offline collector Standard; dependent host receiver/call component Critical.
API-SOURCE/thread/ownership/refusal/repro/task-close/cleanup apply. Prior exact SDK
25.6_61 inventory reused; no new Adobe call. Product/A/B/C1/C2/D/release retained.

## Exact bounded scope

Mode factory-transitive:24 complete windows /1369 instructions /780 structural
anchors. Selected dvacore arm64 SHA256
cb6faaf5b745903b80b44105b658ab68186d5065ae47c8a57c9b23e26aa8ecb0,
UUID4427999D-3DB3-3964-82F7-18DF4FA24D76; MEE previous SHA256
18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344,
UUID74A30DBA-A08B-367B-BD99-15D6D77E9D52. AE25.6x101 arm64 only.
Existing dvacore profile pin reused for offline collection, no native ABI extension.
Symbol inventories select exact next distinct text boundaries; import stubs12 bytes.
Preliminary map-init grouped three complete bodies; final collection splits exact
initializer/destructor/recursive-destroy boundaries. Grouping correction recorded; final separate bodies and discovery inventories retained.
Named MEE initializer is recaptured solely for new counterpart comparison, not an
unchanged plug-in scan. No original binaries/unbounded disassembly committed.

| Window, end exclusive | Instructions |
|---|---:|
| trans-create0xaba2c–0xabb18 | 59 |
| trans-instance0xabb18–0xabb70 | 22 |
| trans-register0xabbfc–0xabd84 | 98 |
| trans-mutex0xabd84–0xabe58 | 53 |
| trans-token0xabe8c–0xac024 | 102 |
| trans-shared0xb14d8–0xb14ec | 5 |
| trans-shared-const0xb14ec–0xb1500 | 5 |
| trans-weak0xb1500–0xb15ec | 59 |
| trans-shared-as0xb15f0–0xb1708 | 70 |
| trans-unknown-dtor0xb1410–0xb144c | 15 |
| trans-map-insert0xb1078–0xb1188 | 68 |
| trans-guid-less0xb1188–0xb13f4 | 155 |
| trans-bad-weak0x805b0–0x805e4 | 13 |
| trans-unique-unlock0xabe58–0xabe8c | 13 |
| trans-shared-unlock0xac024–0xac058 | 13 |
| trans-map-init0xb0f94–0xb1008 | 29 |
| trans-mutex-init0xb0edc–0xb0f64 | 34 |
| trans-weak-lock-stub0x2fef34–0x2fef40 | 3 |
| trans-weak-release-stub0x2fef28–0x2fef34 | 3 |
| trans-mee-guid-init0x45214–0x45a08 | 509 |
| trans-map-dtor0xb1008–0xb1030 | 10 |
| trans-map-destroy0xb1030–0xb1078 | 18 |
| trans-named-guid-init0xb5e8–0xb610 | 10 |
| trans-guid-ctor-stub0xa0448–0xa0454 | 3 |

## Creation and class registration (TRANS-01/02/06)

CreateClassInstanceRef0xaba2c initializes a24-byte output via indirect-result register
x8 (0xaba44–0xaba4c). GetClassTokenFromClassID0xaba50 returns a ClassMapEntry
pointer; callback field+0x20 loaded0xaba58 and invoked with output pointer x0 at
0xaba64. Missing token constructs/throws exClassNotFound (0xaba7c–0xababc), with
local output/exception cleanup on unwind. Null callback leaves empty initialized
output. It does not query an existing object before invoking the callback.
CreateInstanceRef0xabb18 differs: caller-provided output x1, error0xa00a0002 for
missing class,0xa00a0005 for missing callback, zero after callback0xabb44 returns.
It does not prove that callback returned a nonempty/ready object, and its status
protocol must not be substituted for the throwing wrapper's24-byte return.
Previous MEE registered callback0x3e150 calls CreateClassRefInternal(true).
Therefore neither wrapper is established as harmless late read-only acquisition.

RegisterClass0xabbfc takes GUID/name/type-name/callback, obtains selected shared
mutex, locks exclusively0xabc50, constructs a class-map entry and inserts uniquely
0xabcb8. GUID copy and name/type/callback storage at0xabc98–0xabca4; selected
node allocation0xb1100 stores callback at node+0x50 (0xb1114). Token points to
node+0x30, so token+0x20 matches callback. Duplicate insertion w1=0 at0xb1180
leads to0xa00f0008; successful unique insertion w1=1 gives zero0xabcd0–0xabcdc.
Duplicate does not replace callback in the selected body. Prior MEE wrapper does
not inspect this RegisterClass return before proceeding to factory creation/query/
PluginSupport insertion. This is file dataflow, not a late-call/idempotency contract.

GetClassTokenFromClassID0xabe8c locks shared0xabec0, searches using16-byte GUID
lexicographic comparator0xb1188, returns null or ClassMapEntry at node+0x30.
It unlocks0xabf80 before return0xabf98. Creation's indirect callback happens after
that helper returns: the class-map mutex is not held continuously over construction,
MEE/PluginSupport registration or ordinary-effect publication/rendering. Selected
once/guard initialization and unlock/unwind delegates are reviewed; no whole-host
all-reader/MFR admission, callback reentrancy/thread legality or rollback proof.
Map destructor recursively recycles0x58 nodes; returned token stability over full
host teardown/unregistration remains unproved. Do not assert token is a live lease.

## Shared and weak ownership (TRANS-03/04/06)

UnknownBase GetSharedFromThis0xb14d8 and const alias0xb14ec read virtual-base
adjustment at vptr[-0x18], then tailcall SharedAsVirtualBase::shared_as0xb15f0.
Existing factory final table's0x38 shared-base adjustment is distinct from zero
UnknownBase interface adjustment. shared_as first dereferences the incoming object/
vtable, verifies the adjusted base, obtains control at shared base+0x10 and temporarily
increments weak count (0xb1638–0xb1648). It checks shared count against-1, then
calls external libc++ __shared_weak_count::lock at0xb166c. On success it returns
paired object/control fields (0xb1678), balances temporary strong/weak references,
and has zero-shared cleanup when needed. Missing object/base/control or already
expired shared count returns empty (0xb1620/0xb16a8); lock failure after preliminary
check calls __throw_bad_weak_ptr0x805b0 (0xb16ec), with weak cleanup/unwind.
Consequently it is not a pointer-copy getter and can throw despite prior count check.

The first object/vtable reads occur BEFORE the weak lock: this routine cannot safely
resurrect arbitrary copied/stale integer addresses. Caller must already establish
object/control reachability and callable/thread/ABI validity. GetWeakFromThis0xb1500
also temporarily retains weak storage, routes through shared_as and balances acquired
strong reference; it is not proved a harmless raw read. UnknownBase D2 uses hidden
construction-table x1 and removes the watcher; it is not a guessed one-arg destructor.
Release/lock stubs bind external libc++, not their complete installed runtime body.
No SetSharedFromThis symbol in selected inventory; this does not prove absence of
an indirect setter or constructor path. Foreign refcounts/std::shared_ptr not mutated
or reconstructed. Existing owned native stand remains component evidence, not Adobe
ownership certification. Actual retained factory receiver NOT OBSERVED.

## GUID counterpart resolved statically (TRANS-05)

Prior named GUID0x10f080 and RegisterClass GUID0x10fa38 are distinct storage.
Selected MEE global initializer0x45214 sets x19=0x10fa08 at0x45230/0x45234;
0x45870 passes x19+0x30=0x10fa38. It passes36-byte literal at0xb4607,
7a7d3cd3-6b81-48f8-bee0-ec40018a4432, to constructor stub0xa0448 (0x45880).
Named initializer0xb5e8 passes0x10f080 and the SAME literal address/length to SAME
stub0xa0448 (0xb604). This resolves the earlier missing-initializer question and
establishes same initialization input/intent; actual runtime equality/initialization
order/later mutation NOT OBSERVED. The previously documented UNKNOWN remains
historical runtime evidence, not a contradiction or a demonstrated lookup bug.

## API sources, implementation and bounded acceptance (TRANS-07)

SDK25.6_61 Headers lexical search for dvacore/RegisterClass/CreateClassInstanceRef/
GetSharedFromThis returns no matches. Existing API inventory reused, no new call.
[Adobe official SDK entry](https://developer.adobe.com/after-effects/) reviewed for
source routing; no supported private acquisition contract supplied.
[LLVM libc++ memory implementation](https://github.com/llvm/llvm-project/blob/main/libcxx/src/memory.cpp)
and [shared pointer header](https://github.com/llvm/llvm-project/blob/main/libcxx/include/__memory/shared_ptr.h)
are conceptual primary references only; current upstream main is NOT the exact
installed Apple runtime nor Adobe ownership ABI. They do not close native gate.

Collector adds fixed mode, existing dvacore exact profile pin,24 bounded windows,
780 reviewed anchors and explicit UNKNOWN/BLOCKED/NOT RUN claims. Three new TDD
controls first fail for absent mode/catalog, then all68 focused tests PASS. They
reject changed creation/lock/ownership/GUID anchors, wrong bounds/coverage/undecoded
rows and preserve distinct symbol/pin scope. Synthetic transcripts verify parser
refusal only; separate original-byte and semantic review required. No new host
adapter component: original dataflow is insufficient for a supported safe retained
receiver/call ABI. Existing diagnostic decoder/helpers/gate remain unconnected.

## Reconciliation before exact-source checks

TRANS-01/02 selected class-map creation/lookup/callback/throw versus status paths
recorded;03/04 selected shared/weak/expiration/destruction dataflow recorded, actual
supported AE retention remains UNKNOWN;05 same-input GUID initialization established
statically, runtime NOT OBSERVED;06 class lock ends before creation, whole-host
admission/drain/rollback NOT PROVEN;07 collector/refusals implemented and focused
checks PASS, actual host adapter BLOCKED;08 exact-source collection/review/full
runner/scanner/CI/docs/retention/cleanup PENDING clean-source verification.

No claim of full actual receiver/call acceptance, hot loading or release. Conditional
native trial BLOCKED on actual retained receiver/supported late ABI/continuous host
admission/drain/whole-effect rollback. Actual registration/apply/render NOT RUN.
Original product/A/B/C1/C2/D/release retained. No AE launch/attach/install/session
read/private invoke/retain/release/destructor/unload/scan or merge/release.

## First clean collection refusal and scoped correction

At36b3c9360c13ebab448f36e0558bb4e3a4b26aa8 collection stopped with exit2:
complete dvacore nm inventory3,543,605 bytes exceeds existing2 MiB inspection
budget. Partial exclusive collection directory retained. Full runner at that SHA
PASS, but it does not run original Adobe collector and cannot clear this refusal.
Correction allows4 MiB only for the exact pinned dvacore nm command; all other
commands remain2 MiB, invalid/excessive/boolean budgets refuse. One additional
TDD test first fails for absent output_limit, then scoped refusal/pass controls.
Final new source must repeat collector/full runner/scanner and exact-source CI.

First scanner raw exit2/incomplete retained: the3.54 MB generated private nm file
exceeds scanner2 MiB per-file limit. No source omission or completed scan claimed.
Final scanner uses a fresh owned local Git clone at exact corrected SHA with every
tracked Git/source byte independently compared and no generated evidence outputs.
This preserves original generated evidence and scopes scanner to actual tracked
source. Raw findings and final scanner exit remain review inputs, no suppression.

## Exact clean-source reconciliation

This supersedes PENDING verification above. Corrected tested code
2f5fcb962dd4509e5f485b7d2cf6db017c6ae887. Subsequent documentation-only SHA is not claimed to have run these
code checks. First36b3c93 source/runner/raw scanner/refusal remain historical.

| Task | Bounded acceptance/result | Remaining dependent scope |
|---|---|---|
| TRANS-01 | Registration/unique insertion/token lookup and exact original boundaries reviewed | Actual live class-map/token lifetime NOT OBSERVED |
| TRANS-02 | Creation callback,24-byte indirect result, distinct status/out-reference and throw/error paths reviewed | Supported callable private ABI/actual receiver UNKNOWN |
| TRANS-03 | Shared-from-this virtual adjustment/weak hold/strong lock/paired output traced | Initial object reachability and supported actual ownership UNKNOWN |
| TRANS-04 | Empty/expired/lock-failure throw/temporary release/control-storage/destructor boundaries reviewed | Installed external libc++ and actual AE lifetime not certified |
| TRANS-05 | Both distinct GUID cells initialize with same original literal/address/length/constructor | Runtime equality/order/later mutation NOT OBSERVED |
| TRANS-06 | Selected class registry locks/initialization/normal-unwind unlock established; unlock before callback | Whole-host reader/render exclusion/drain/full rollback NOT PROVEN |
| TRANS-07 | Fixed collector/refusals and scoped size fix IMPLEMENTED,69 focused PASS | Actual retained host adapter BLOCKED, existing gate unconnected |
| TRANS-08 | Clean capture/separate raw-byte/archive/source review/full runner/raw scanner/both exact-source CI/retention/docs/cleanup COMPLETE | Original full product/A/B/C1/C2/D/release open |

- Clean collection `resource-factory-transitive-dce50875-7twu1fq1.zip`, SHA256 7699f92179db3621c0ac7209280ec51d789082df599f1dcdbf2725bbfd0eeedc,
  52 members. Exact input pins before/after,24 complete windows/
  1369 rows/780 anchors, CRC/manifest hashes and equality to exclusive owned outputs
  PASS. Zero Adobe calls. Actual registry/apply/render NOT RUN.
- Separate verifier `aehl-transitive-independent.py`, SHA256
  3241de59e9abf85789b2b6aeade51dffd43af0c59d527599ec2f3893c8deb07f; no collector import. Original arm64
  Mach-O mapping/raw1369 instructions,146 direct/79 conditional/7 indirect branches/
  50 returns, GUID roots/literal/36-byte input/status constants/virtual adjustment/
  paired result fields PASS. Original nlist confirms21 complete next-symbol bodies
  plus3 exact12-byte stubs; indirect-symbol/nlist/library ordinal confirms GUID
  constructor→dvacore, weak lock/release→libc++. Stub GOT file VMs0xedb90/
  0x39cc00/0x39cbf8, no live pointers. Review receipt SHA256
  fb6fec69211188bee331609fbcb571d68c9514b5091c1d2c6733949bed6be839. Raw branch checks do not certify all transitive
  side effects or installed runtime ABI.
- Full runner `AEHL-checks-_ih8pwrq.zip`, SHA256 47402dae45435753bc2d31ad9744c93fd745627b2f10d0b284a2cb6ebbdc6881,
  25 members:450 Python, zero skips/errors/failures/expected failures/
  unexpected successes,62 Node, all22 stages PASS. Python74.131 seconds; actual
  owned native controls include prior ASan/UBSan stand, no AE ABI claim.
  TDD logs retain3 absent-mode errors and1 absent-budget argument error, then
  focused68/69 PASS; original collection size refusal was discovered separately,
  not hidden by the full runner (which does not run original Adobe collector).
- Independent runner CRC/manifest/payload review and all346 working/Git/source-copy
  bytes PASS; clean source/source_unchanged_after=true. Source inventory SHA256
  36455a8317b19c600e452c5e4a93566aec1e2d2e784a87893c954769ccbbef5c; source-proof SHA256 bcf7bcf3e32bbb7460205dee7bcfbae65466dcdf74aca738b1ba965d920e4955.
- First raw scanner36b3c93 exit2/incomplete retained for generated oversized file.
  Final raw scanner2f5fcb9 SHA256 ec4998065d88f1930ece9620a72d7c80ca959af957c4b5fa30f88788e3ffd3a5,
  exit1/review_required/release_readiness=not_assessed, omissions=[]: independently
  byte-matched clean local Git clone at exact source;346 tracked files (236 supported
  UTF-8 text files and110 unsupported types), generated evidence excluded by source
  snapshot. Source-copy proof SHA256 4b59cbcd1295403e8ec65890dc04f9996039c6d14555d67b640bf0c52fbce5b9.
  Sole vibe.no_ratelimit_auth tools/artifact_manifest.py:71 is a local argparse
  manifest CLI, no HTTP/auth route/listener. Separate review disposes as false
  positive; raw finding/exit retained without suppression. Manual review SHA256
  fbfa5062d58e6df9ad5796eff60798e993e50bd2f79d811e8298837b01613172.
- Research CI [37140197009](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37140197009)
  and macOS CI [37140197001](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37140197001)
  completed/success at exact2f5fcb962dd4509e5f485b7d2cf6db017c6ae887. Internal/offline checks, no AE runtime gate.

## Retention, cleanup and next dependency

Durable private owned receipts: `build-ae-hot-loader/transitive-closeout-2f5fcb9-k2u3cbg7`.
Byte-identical clean collection/full runner, separate verifier/review/source proof,
first and final raw scanners/manual review, initial refusal and earlier runner,
TDD/focused logs and compressed preliminary symbol/body/xref inventories retained.
RETENTION.json SHA256 89eaea97d2470ddfe5f365297acfb58551a29a3c2aa55329e6ba0481ce25b668. Final CI.json and CLOSEOUT.json
bind exact source results and later docs-only commit/full receipt inventory.
Source scan clone remains private preserved evidence, no shared/loaded/unknown or
historical materials removed. Owned native temporary binaries cleaned by test
lifecycle. No SDK/app/plugin/project/AE session mutation, prefs/cache purge, scan,
launch/attach/install/read active session/private invoke/refcount/destructor/unload,
main update, merge or release. Cleanup review closes assessment, not blanket deletion.

Next concrete dependency: substantiate non-creating existing-factory acquisition
(e.g. the previously reviewed CreateClassRefInternal(false) path only after its
actual callable/owner/thread/reachability contract is established), then obtain and
retain an actual receiver. File-level creation/ownership findings are now traced;
supported late ABI/initial reachability/retained host ownership/thread boundaries
remain UNKNOWN. Continuous host-wide admission/drain/whole-effect rollback remain
required before registration/apply/render trial. No copied-integer ownership or
wrapper replay; full product/receiver/call acceptance is not declared complete.

Final exact-source CI receipt CI.json SHA256 7c366af6537eb4760adafcd25bb1e35baaada3085dad50520eff219f9802c72c. Both workflows completed/success at corrected tested code; later docs-only commit retains unchanged non-document source bytes.
