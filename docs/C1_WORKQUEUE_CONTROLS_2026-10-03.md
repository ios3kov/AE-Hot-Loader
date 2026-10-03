# C1 BEE work-queue cancellation and admission boundaries

2026-10-03 QUE-01–11 continuation; baseline a9500852c00a95f9e4d5760b34b30558d160bbf0.
Stage C1 Development research, accepted rules8.0.0 /132b7cd32873ba7328e3128ffbb33e1929b74d45.
AI_ENTRYPOINT first; native ABI/thread/admission/lifetime Critical, bounded file
collector Standard. API-SOURCE, RENDER-001, exact-source, meaningful checks,
TASK-CLOSE/CLEANUP and production-engineering apply. Original ordinary third-party
registration/apply/render without restart and A/B/C1/C2/D/release retained.
The eleven-block acceptance/dependency map and every new window were recorded in
[PRODUCTION_PLAN](PRODUCTION_PLAN.md) before disassembly. No native API call added.

## Original source and fixed implementation

Original BEE.dylib in the installed AE2025 application:31,373,056 bytes,
SHA256817b9de9c6d57b5d6988b634842090e1528fe817a5685c8d1ff358553c6660ca,
arm64 UUID161300f373f83ebca751959df40a073b. The already-pinned aelib dependency
inventory names BEE.dylib. Original nlist contains271,537 entries,7,871,712 string
bytes and58,390 defined text symbols. Fourteen next-defined-text windows /2,546
instructions include complete normal/error/unwind tails, not selected fragments.

Added only workqueue-control offline collector and BEE file-only pin; live
AE256ResourceProfile, helper, bridge and ResourcePassGate backend unchanged.
Full nm inventory exceeded preliminary2MiB and8MiB limits; those refusals are
preserved and global tool caps remain2MiB/dvacore4MiB. A bounded selected nlist
reader validates FAT32 single arm64 MH_DYLIB, load-command/section/table ranges,
UUID, symbol names and exact next-defined-text end, original body-byte hashes,
and every normalized disassembly instruction through a fixed whole-body digest.
It retains selected names and bounds rather than the full inventory. Raw binary
and transcript hashes are distinct; neither is a host ABI declaration.

Primary file-layout source: local Apple SDK mach-o/fat.h:62, nlist.h:92/103,
loader.h:473/913/1217. Initial implementation incorrectly required string-table
byte0 to be null. Original file rejected that assumption; nlist.h explicitly
defines index0 as the empty name. Corrected that interpretation and added the
non-null-byte0 refusal regression without altering the original file or pin.
An initial owned test fixture had a wrong final-name index/length; corrected it
and recorded the observed correction. Synthetic tests prove parser refusal, never AE behavior.

## Concrete cancellation and scheduler findings

| Complete selected body | Original bounds | Observed scope / remaining contract |
|---|---|---|
| BEE_WorkQueue_Cancel / Pause / Resume |78e840–78ea80 /78ec34–78f100 /78f2b4–78f7b4 | Look up one unsigned64-bit ID under map mutex, retain selected boost owner, unlock before per-item operation, release owner before return. No caller-held continuous token. |
| WorkQueue_Item::SetCancel / Canceled |7e2250–7e2374 /7e1fcc–7e1fe0 | CAS flag+0xd0 from0→1; Canceled reads that flag. SetCancel separately checks stage+220; eager completion only stage0 or stage1 with SchedulerPaused true. Other stages still have cancel flag set but return false. |
| SchedulerPause / SchedulerPaused / SchedulerStarted |7e1fe0–7e2048 /7e2048–7e2100 /7e2100–7e21d4 | Pause sets byte+d4 and status+224=517 under per-item recursive mutex+138. Paused also consults virtual slot+78. Started clears those fields and copies erased callback+118/120 into result. Concrete virtual targets/thread contract remain UNKNOWN. |
| SetStage |7e18b4–7e19e0 | Updates stage+220 and timestamps; stage2 can remove ID from an attached ID list. No worker join established by this selected state transition. |
| GetCancelHandlerCopy |7e16e4–7e17b0 | Copies erased callback+f8/100 under item mutex, using manager operation0 or inline storage. Copy is ownership work, not a read-only host probe. |
| BEEp_WorkQueue_Table_Cancel_Item |7b8d34–7b9b38 | SetCancel false skips eager completion path. True removes selected work ID from normal/low work lists under map mutex, unlocks, conditionally copies cancel handler for runmode1, wraps callback/ID and selected RemoveItem/shared owner through executor virtual+10, not a direct barrier. Completion virtual+b8 and notify remain indirect/opaque contracts. |
| BEE_WorkQueue_RemoveItem |7b4e48–7b5028 | Removes one map item while retaining a temporary owner; unlocks before item notification and last-owner releases. Erasure does not prove all callback/code owners have completed. |
| BEEp_WorkQueue_Table_Add |7975b4–797778 | Inserts/retains one item by ID under same map mutex, unlocks before log/notify. No visible admission lease spanning a later registry transaction. |
| BEE_WorkQueue_Execute |7ac8f4–7acde4 | Allocates item, captures callback/client/ID-list owners, calls Table_Add, then ScheduleWork79438c, returns item ID. The selected wrapper does not close admission for concurrent/future producers. Scheduler callee remains UNKNOWN. |

Inner cancellation uses original indirect executor from merged global+730.
At7b9770 a shared owner is retained into a bound RemoveItem callback, delivered
through virtual+10 at7b97b8; cleanup later destroys local bound storage. An
executor may queue or synchronously handle that work; its actual target and
notification/reentry/thread semantics are not established. Do not label this
route as guaranteed asynchronous completion or a guaranteed synchronous drain.
The flag-only branch reaches notification and return without the eager removal
path. No selected result guarantees all MFR workers/callbacks have drained.

Cancellation is scoped to selected work and allows callback/lifetime side
effects. Per-item pause does not retain the global map mutex. New Table_Add and
Execute activity are distinct from old-item cancellation. These functions do
not establish the continuous all-reader/dispatch exclusion required by the
ordinary effect registry transaction. This is a bounded conclusion from the
selected bodies, not a claim that no suitable mechanism exists anywhere in AE.

## Reconciliation with retained factory/registry evidence

The earlier [ADM checkpoint](C1_ADMISSION_CONTRACTS_2026-10-03.md) correctly left
opaque BEE completion UNKNOWN. This pass fills the wrapper/flag/stage/eager
cancel/producer path, while actual indirect executor and notify/worker graph
remain UNKNOWN. Original public SDK25.6_61 selected queue/idle/request contracts
are unchanged; none supplies the missing continuous host lease.

Earlier registry mutex+50/local project scopes do not cover all later retained
registry consumers or effect dispatch/render callbacks. The existing factory
false path still has guard/lock/retain/atexit side effects; GetSharedFromThis
reads the initial object before retaining. Supported safe initial receiver,
private ABI/thread and the full owner graph remain unestablished. Publication
before preference/lazy-global errors and limited cleanup remain; queue cancellation
supplies no full registry/canonical/preferences inverse. All original archive
identities/pins are rechecked at closeout; unchanged bodies are not recaptured.

Actual host adapter QUE-09 BLOCKED by QUE-02–06; trial QUE-10/11 BLOCKED / NOT RUN.
No AE install/launch/attach/session inspection/scan/private call, thread suspension,
foreign retain/release/teardown, project/preferences/plugin mutation or release.

## Verification checkpoint before exact candidate closeout

8 bounded parser/refusal tests and77 collector regressions PASS. Red missing-module
log and preliminary fixture/file-layout corrections retained. Controls cover
architecture/command/section/table bounds, UUID/name/section/duplicate/intruding
symbol/boundary drift, raw-byte/inventory changes, complete instruction changes,
missing/duplicate/undecodable rows and offline-only pins/tool caps. Complete new
collector execution, full runner, raw scanner/manual original review and both
exact-source CI are pending at this checkpoint. Final identities and task states
will follow; no product or release PASS is claimed.

## Exact closeout and evidence

Clean tested/pushed code **a24d8a2f5d0b06234d839005f36cc44749f0478f**.
Final actual offline collector: resource-workqueue-control-e845d062-6jzszadj.zip,
SHA2562a41b7bbd0847f1d6553a4b9d18d53c49849e2f7ab278d0dcc32ca215764a079;
14 complete windows /2546 instructions; exact BEE before/after pin, selected nlist,
raw body hashes and all normalized instruction digests PASS. Adobe calls0.

Full runner AEHL-checks-um95ya9y.zip, SHA256
2a26ec22cbe1c6501cf3306e0c190eaa7b4b818de013c3e75a71d6a2db79190c:
481 Python/no skips,62 Node/all22 steps PASS; aggregate Python480s /individual
120s limits retained.370 tracked Git/working/runner bytes matched; source unchanged
through run. Owned native cases executed on macOS; they do not establish AE behavior.

Independent original review imports no current collector:14 windows/2546
instructions,421 direct195 conditional57 indirect branches14 returns,25 scalar/
add field decodes and cancel atomic register encoding; original nlist/body bytes/
ZIP/transcript identities PASS.10 earlier archive CRC/manifests and currently
installed original pins plus exact SDK header revalidated without recapture.
Receipt SHA256138991767fb5a975655191b9da8a540c4410f87c0aed55e8b55b8c4beed60547.

Raw scanner exit1/verdict review_required/release_readiness not_assessed:
247 text123 unsupported/no omissions, all configured checks completed. Sole
local argparse create/verify false positive at tools/artifact_manifest.py:71
manually reviewed without suppression. Raw scanner is not host/release certification.
Manual receipt SHA25661cd05be5dfe28e98cef30f2aebe19da0cb69596b73caa3625f21bb3d6a75462.
[Research CI37149834498](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37149834498)
and [macOS CI37149834507](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37149834507)
completed/success at exact a24d8a2; all three jobs success, no failed step. macOS
build/sign/package/integrity and synthetic regressions PASS; actual AE and release
approval NOT RUN. CI package is not an installable handoff in this packet.

Private evidence: build-ae-hot-loader/queue-closeout-a24d8a2-lgfwcf2f, including
source/scanner/manual/original/CI/runner/preliminary correction records. Preserve
historical artifacts and the two earlier ambiguous empty inventory directories.
Only this pass's new clean byte-matched scanner clone was removed after proof;
raw evidence retained. App/SDK/plugins/projects/preferences untouched. Docs-only
closure checks all non-Markdown bytes against a24d8a2 and local links; final
retention/source/remote receipts remain in that private evidence folder.

## QUE-01–11 final task reconciliation

| Task | Task/implementation state | Acceptance, actual checks and remaining work |
|---|---|---|
| QUE-01 | DONE | Actual original BEE cancel implementation located; pin/UUID/nlist/dependencies/14 selected complete bounds and original-byte review PASS. |
| QUE-02 | PARTIAL | Concrete new-work Add/Execute and per-ID Pause/Cancel scope traced. No supported caller-held continuous host admission lease or all-producer exclusion established. |
| QUE-03 | PARTIAL | Flag versus stage, eager versus flag-only cancel, retained callbacks/indirect executor/removal traced. Actual executor/notify/workers/thread/reentry and all MFR drain UNKNOWN; cancel return is insufficient. |
| QUE-04 | PARTIAL | Reused original registry/dispatch/render evidence revalidated and reconciled with per-item queue scope. Coverage of every registry/effect reader and callback remains NOT PROVEN. |
| QUE-05 | PARTIAL | Existing-only factory and initial pre-retain object-read constraints revalidated. Supported actual receiver/retention/private ABI/thread contract still UNKNOWN. |
| QUE-06 | PARTIAL | Publication-before-error and limited cleanup/full inverse gaps revalidated. Full registry/canonical/preferences recovery remains NOT PROVEN. |
| QUE-07 | DONE (research only) | Implemented only fixed original-file reader/collector/refusal controls.8 parser/77 collector focused plus481 full Python/62 Node PASS; host backend stays unbound. No new owned mock stand offered as host proof. |
| QUE-08 | DONE | Exact-source collector/full runner/raw scanner/manual original review/both CI/source bytes/docs/task reconciliation/commit/push and owned-only cleanup completed; raw and historical evidence retained. |
| QUE-09 | BLOCKED | Actual AE adapter depends on unresolved02–06 contracts; no private host call implemented. |
| QUE-10 | BLOCKED / NOT RUN | Actual registration→apply→render depends on09 and current safe disposable environment; no executable host packet exists. |
| QUE-11 | BLOCKED / NOT RUN | Repeat/recovery trial depends on10 and demonstrated inverse; no automatic retry or state change. |

Packet **PARTIAL:3 DONE /5 PARTIAL /3 BLOCKED**. Original feature, compatibility,
A/B/C1/C2/D and release obligations are retained. This advances the cancellation
hypothesis from an opaque call to a concrete scoped state/callback path. It does
not demonstrate hot registration, rendering or release readiness. Further bounded
research must identify an actual admission/ownership/recovery contract; tracing
more per-item cancellation alone cannot satisfy the all-reader transaction gate.
