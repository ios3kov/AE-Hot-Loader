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
Exact clean tested/pushed code **9921ab0df7ee20d601854821431cf1aedc45d66b**.
Full runner: **489 Python/no skips,62 Node and all22 steps PASS**. Owned macOS
native smoke PASS; actual AE pipeline BLOCKED, product package acceptance NOT RUN.
All373 tracked files matched Git, working tree, fresh scanner checkout and runner
source digest. Production native profile/backend and all unrelated source unchanged.

Independent review does not import the current collector: original Mach-O/nlist,
complete body ends/bytes, all24 transcript hashes and5901 instruction words,
909 direct/508 conditional/157 indirect branches/25 returns,32 scalar/add fields
and14 original chain rebases checked. Eleven unchanged historical archive/manifest/
pin checks and exact SDK25.6_61/Apple layout headers PASS. Preliminary decoder
refused a MOV at14eec where a scalar load was expected; selected actual LDR14ee8
instead, preserving the initial script/log. No collector guard or evidence weakened.

Raw scanner: **exit1/review_required**,250 text/123 unsupported/no omissions;
all9 checks completed, release readiness not_assessed. Its sole heuristic finding
at tools/artifact_manifest.py:71 is local argparse create/verify mode selection,
not an HTTP authentication route. Exact context/diff manually reviewed and raw
finding retained; no suppression and no scanner PASS claim.

Both exact-source CI completed/success at9921ab0:
[research37152252624](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37152252624)
and [macOS37152252660](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37152252660).
Required jobs/steps and artifact metadata preserved. CI builds, ad-hoc signing,
synthetic reload/busy/rollback and archive roundtrip are not AE runtime proof or
an installable/release handoff. No CI artifact downloaded or installed.

Private evidence (not a public shipping artifact):

| Evidence | Identity / result |
|---|---|
| Clean collector ZIP | build-ae-hot-loader/resource-workqueue-executor-e1fb1d2c-ov4np3kr.zip; SHA256 c3b3bb95889136d2793c8253aeec7e2effe0bd3263b4dc2e696751ec7dc9d729 |
| Full runner ZIP | executor-closeout-9921ab0-of5lojlu/AEHL-checks-r2w97j3n.zip; SHA256 f7610b256ead55d6c202c5f8bdbf756010beafd68d5d4f3700f03e5d55944f82 |
| Independent original receipt | executor-closeout-9921ab0-of5lojlu/aehl-executor-original-review.json; SHA256 2996f21d98942dabc1b0cf9c80d7ad99434a0330c149607fd3f678a554bc137d |
| Before-implementation original manifest | executor-original-9sb3o200/fixed-manifest.json; SHA256 3e8479c1fe8a32ff562052ecad0143fd97180c9a047585288e232b25c2d32ab8 |
| Source/manual/CI/cleanup | build-ae-hot-loader/executor-closeout-9921ab0-of5lojlu; original captures, initial refusals and historical archives retained |

Only the fresh owned scanner checkout was removed after all373 byte checks,
clean/no-untracked/no-ignored/UID/no-symlink proof and raw receipt retention.
Application/SDK/project/plugin state and historical/unknown materials untouched.
Final documentation closure changes only five Markdown records; all239
non-Markdown tracked files remain byte-identical to tested9921ab0. Local links
and documentation diff checked; final source/remote/retention proof preserved
in the private closeout folder.

## Task state and remaining gates

Packet **PARTIAL:3 DONE /6 PARTIAL /3 BLOCKED**. Checks above close the bounded
research component; no native registration implementation or host acceptance.

| ID | Final task status | Observable result / evidence and remaining condition |
|---|---|---|
| EXE-01 | DONE, bounded file identification | Birth/factory/vtable and retained executor fields checked in originals; safe live acquisition/private ABI still unknown |
| EXE-02 | PARTIAL | ScheduleWork unlocks before submit; resource lease/Worker Gate lacks continuous all-registry-reader exclusion |
| EXE-03 | PARTIAL | Worker and full Flush branches traced; single executor completion lacks universal MFR/consumer coverage |
| EXE-04 | PARTIAL | Retained item/notify/completion/housekeeper removal traced; observer reentry and downstream owners remain unknown |
| EXE-05 | PARTIAL | Historical registry/render archives and exact pins rechecked; all-reader coverage still unproved |
| EXE-06 | PARTIAL | Existing-only factory/initial receiver/owner evidence rechecked; retained initial receiver/private ABI/thread/full owner graph missing |
| EXE-07 | PARTIAL | Publication-before-failure evidence retained; complete registry/canonical/preferences inverse missing |
| EXE-08 | DONE, research only | Fixed collector/helper, complete-body partition/refusal controls;10/5/78 focused and full checks PASS, native backend unbound |
| EXE-09 | DONE | Exact source/full/original/manual/CI evidence, five documentation records, commit/push and owned-only cleanup; final byte/remote receipt |
| EXE-10 | BLOCKED | Actual AE adapter depends on unresolved02–07 and safe01 acquisition; native implementation NOT RUN |
| EXE-11 | BLOCKED / NOT RUN | Actual registration→apply→render depends on10 and current safe exact-candidate environment |
| EXE-12 | BLOCKED / NOT RUN | Repeat/error trial depends on11 and demonstrated full recovery |

Unchanged factory/registry/render/SDK evidence rechecked against original archive
identities and pins. Safe initial factory receiver/private declaration/
thread/full owner graph, all registry consumer/MFR admission/drain and complete
registry/canonical/preferences inverse remain required. Scope of reviewed
executor controls is insufficient; native ResourcePassGate backend stays unbound.
No AE install/launch/attach/session read/scan, host private call/foreign retain/
release/teardown, thread suspension, user-state mutation, main/merge/release.
Owned evidence and preliminary corrections retained; fresh owned scanner checkout
removed after proof. Unknown/history material preserved. Next work must establish
an actual continuous admission/drain owner and complete recovery contract, plus
safe retained factory acquisition. Another Pause/Flush/cancel call or unchanged
ordinary plug-in scan cannot establish those prerequisites.
