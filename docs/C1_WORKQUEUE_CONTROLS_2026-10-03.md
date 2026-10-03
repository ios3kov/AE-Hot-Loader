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
and retained the failure. Synthetic tests prove parser refusal, never AE behavior.

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
