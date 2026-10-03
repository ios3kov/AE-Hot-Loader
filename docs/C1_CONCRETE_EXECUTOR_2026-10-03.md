# C1 — concrete BEE executor, callback completion and admission limits

2026-10-03. Rules8.0.0 /132b7cd32873ba7328e3128ffbb33e1929b74d45;
AI_ENTRYPOINT first, C1 Development research. Baseline clean
5f2230fcf31bc0b6fe933e12130b02ae2c5b2ef8 on research/ordinary-plugin-discovery.
User accepted9 main /3 conditional blocks. Critical native ABI/thread/lifetime/
admission; Standard bounded offline collector. API-SOURCE, RENDER-001,
TASK-CLOSE/CLEANUP, exact-source verification and production-engineering apply.
[Task mapping](PRODUCTION_PLAN.md), [status](DEVELOPMENT_STATUS.md),
[previous QUE evidence](C1_WORKQUEUE_CONTROLS_2026-10-03.md).
Original arbitrary ordinary-effect/no-restart product and A/B/C1/C2/D/release retained.

## Source and scope

Original BEE31,373,056 bytes, SHA256
817b9de9c6d57b5d6988b634842090e1528fe817a5685c8d1ff358553c6660ca,
arm64 UUID161300f373f83ebca751959df40a073b. Original dvacore SHA256
cb6faaf5b745903b80b44105b658ab68186d5065ae47c8a57c9b23e26aa8ecb0,
arm64 UUID4427999d3db3396482f718df4fa24d76. Both existing file pins unchanged;
BEE remains offline-only, no extension of AE256ResourceProfile live scope.

23 complete next-defined-text bodies /24 capture windows /5901 instructions.
ScheduleWork79438c–7953f0 is4196 bytes: fixed contiguous windows79438c–79538c
and79538c–7953f0, each <=4096. Explicit complete-group checking refuses gaps,
overlap, reordering, partial coverage, oversize windows or changed symbol boundary.
The original unpartitioned4096-byte guard remains. Output caps2MiB /dvacore nm4MiB
remain unchanged; both images use selected nlist records in this review.
Original nlist metadata: BEE271537 symbols/7871712 strings/58390 text symbols;
dvacore70803/2366720/12012. Fixed complete raw-byte and full-transcript digests.
Names/bounds/hashes selected before implementation; no scan or Adobe execution.

15-word dvacore table39ded0–39df48: zero offset/header and14 plain
DYLD_CHAINED_PTR_64_OFFSET rebases. Initial22-word proposal crossed separate
RTTI/binds and was refused, corrected before acceptance; never treated as a valid
executor table. Rebase membership independently checked from original chain.
Large malformed test fixture first used wrong struct offsets; parser refused it,
fixture corrected against Apple layouts. Preliminary logs/corrections retained.

## Concrete findings and limits

- Birth7901b4–790918 creates three AsyncThreadedExecutor instances via import
  d41d5c: general render at7902e8, housekeeper790450 and analysis7905c0. Returned
  std shared-owner pairs move into global+720/+730/+740 at790300/790468/7905d8.
  RegisterThread/DeregisterThread callbacks are supplied; this is a private
  lifecycle path with allocation/preferences/global mutation, never invoked.
- Original dvacore factory139cc–14564 installs ThreadedWorkQueue vptr39dee0
  at13a38. Its original table identifies +10 CallAsynchronously14da0,
  +20 Terminate15004, +48 Flush15450, +50 Pause15b64, +58 Resume15c70 and
  +60 BlockWhilePaused15d7c. This closes the opaque concrete-type/slot question
  for these file paths, not supported callable ABI/thread/live receiver proof.
- CallAsynchronously14da0–14ff4 acquires only the executor's queue resource;
  missing/closing queue returns false, otherwise moves/clones a function and
  passes it to Push17bb0–17dd4. It releases the resource before returning.
  Scheduler ScheduleWork locks its list at794440, inserts/retains a WorkListNode,
  unlocks at794ed0, then submits PerformWork via+10 at794f30. No continuous
  caller-held registry-reader exclusion emerges from this submit path.
- Pause15b64–15c70 calls Gate::Close243c24–243c38. Close is a release store
  to Gate state+70; no worker join or active-callback wait. WorkerMain147d8–14c30
  pops first at149e8, passes the Gate at14a20 and then invokes callback wrapper
  at14a64. A worker already past that Gate is not joined by Pause. Resume opens
  this Gate; no universal effect-registry transaction scope is established.
- Flush15450–15b64 can return immediately when called on its executor thread
  (1548c/15490→15864). Single-thread path posts a marker+10 at15540 and waits
  on OpenOnceGate155c8; marker18644–1864c opens that Gate. Other paths enqueue
  SyncPoint work and wait at159b4, or join this executor's NamedThreadInstance
  objects at1583c after its queue is gone. These distinct branches do not supply
  an all-reader/MFR admission lease held across factory/registry publication.
- Terminate15004–15240 swaps out the owned queue at150c4, calls
  CancelAndDeleteDelayedFunctions150e8, pushes worker termination sentinels
  at15154 and opens the Gate15178. Death790f2c–791170 invokes Terminate/Flush
  on all three, releases global owners and destroys the item map and related
  queues. **Excluded as a transaction gate: destructive lifecycle, no live call.**
- ItemStage scoper78f8b0–78fb6c retains the item and attempts stage1 at78f8f8.
  Destructor78fc28–78fe90 skips terminal transition when SchedulerPaused is
  true; otherwise sets stage2 at78fdc0 and runs selected client/notify paths.
  This is per-item work, with additional private client/thread dependencies.
- ExecuteRoutine7acde4–7ad27c establishes project context/scoper, calls work
  callback7ace94, destroys the stage scoper7acf10, runs item virtual+b8 at7acf20,
  then submits a retained RemoveItem bound function to housekeeper+730/+10 at
  7acf88. PostCompletionRoutine7abcc4–7ac64c creates another queue item and
  uses Table_Add7ac190/ScheduleWork7ac1a4; it is a producer, not a host drain.
  Its worker7ac64c–7ac8a4 invokes the completion callback7ac6dc, retains the item
  in a removal bind7ac708, then submits housekeeper work7ac750. Exception logging/
  cleanup is preserved; callback return still does not join every retained owner.
- ItemNotify7e431c–7e48cc retains each item before observer call7e43c4 under
  shared observer lock7e4374, released7e444c. Selected progress handlers may
  request item cancellation. Observer callback behavior/reentry/downstream
  owners remain unknown; synchronous observer invocation does not prove global
  callback/MFR drain or provide a retained caller transaction token.

## Implementation and checks

Added fixed workqueue-executor collector/helper and guarded complete-body
partition support. No native AE adapter or owned stand-in for host safety added.
`--review workqueue-executor` records table/owner/submit/pause/flush/death scope
and explicitly retains UNKNOWN native ownership/thread, NOT PROVEN all-reader
exclusion/full rollback, BLOCKED experiment and NOT RUN registration/apply/render.

Focused10 parser /5 executor /78 collector methods PASS. Two partition tests and
new executor module test first failed against missing implementation; malformed
fixture refusal fixed without loosening parser. Original23 bodies/24 windows/
5901 instructions and14 rebases pass preliminary implementation comparison.
Full clean-candidate runner, independent archive/original review, raw scanner/manual
review and both exact-source CI: NOT RUN yet, pending identified candidate.

## Task state and remaining gates

EXE-01 DONE for bounded original-file concrete executor/owner identification;
EXE-02–07 PARTIAL. EXE-08 implemented research scope, verification pending;
EXE-09 IN PROGRESS. EXE-10–12 BLOCKED / NOT RUN. Final task reconciliation
will bind actual source/artifacts/check results after verification.

Unchanged factory/registry/render/SDK evidence must be rechecked with original
archive identities and pins. Safe initial factory receiver/private declaration/
thread/full owner graph, all registry consumer/MFR admission/drain and complete
registry/canonical/preferences inverse remain required. Scope of reviewed
executor controls is insufficient; native ResourcePassGate backend stays unbound.
No AE install/launch/attach/session read/scan, host private call/foreign retain/
release/teardown, thread suspension, user-state mutation, main/merge/release.
Owned evidence and preliminary corrections retained; only proven fresh owned
scanner checkout eligible for later cleanup. Unknown/history material preserved.
