# C1 — suspend contexts, admission and completion scope

2026-10-03. Accepted rules8.0.0 /132b7cd32873ba7328e3128ffbb33e1929b74d45,
AI_ENTRYPOINT first. Start clean45a7aa4d6ab92e87e0db81ee419166b1db094e92;
branch research/ordinary-plugin-discovery. C1 Development research, Critical
native ABI/thread/ownership/admission, Standard bounded original file collector.
API-SOURCE, RENDER-001, TASK-CLOSE/CLEANUP and production-engineering apply.
[Twelve accepted tasks and checks](PRODUCTION_PLAN.md),
[previous executor evidence](C1_CONCRETE_EXECUTOR_2026-10-03.md).
Original ordinary-effect/no-restart product and A/B/C1/C2/D/release retained.

Initial missing contract: U_SuspendContext imports exposed by the EXE lifecycle
review; related U_RenderContext use in BEE item stage scopers. Identify original
defining image and exact symbol ends before
capture; only new selected bodies,<=4096 per capture and unchanged output caps.
No AE install/launch/attach/session read/scan, foreign retain/release/private call,
teardown, thread suspension or application/project/plugin mutation. Unknown
native contracts block dependent implementation/trials; historical evidence
keeps its exact source and does not become current host proof.

Original BEE import ordinal40 and aelib ordinal28 resolve the selected
U_SuspendContext symbols to existing U.dylib. Offline review reuses its existing pin:
1,372,928 bytes, SHA256 aecabb33c5ac5948ad742848c46588398bc690411b70aae7ca3f08a919362daa,
arm64 UUID3053ea7ea176315d900b9f17cc96dbe5;14740 nlist symbols/308320 string
bytes/2497 text symbols. No addition to native/live AE256ResourceProfile.

Selected before capture: twelve complete constructor/destructor/New/context
dispatch/threaded/event-loop templates/ExecuteStatic/resume/terminate/get-render
bodies,1771 instructions. Concrete TLS attach/detach targets and current-context
get/has then selected before transitive capture:1286c–12ca0,13ae8–13e24,
140f0–14418,148e0–14cd8,29104–29538,29538–29874,131d8–13348,
13528–13680,2a5e0–2a77c. All<=4096; original byte/full-transcript hashes fixed
before implementation. Original selection/refusal/captures retained privately.

## Findings and bounded implementation

27 complete original bodies/windows,3788 instructions. Six additional activation
get/clear/last-owner targets selected before capture:14cd8–14eb8,29874–29a54,
146e0–14734,2af4c–2afa0,1a300–1a35c,2bb80–2bbdc. Original chain membership
and plain rebase words a5f68→1a300 /a63b0→2bb80 checked separately, tied to
the activation-owner vptrs constructed at14d64–14d70 /29900–2990c. These are
original-file identity findings, not supported live object acquisition/ABI.

- NewSuspendContext16960–169a8 allocates one96-byte object, constructs it and
  hands it back through a retained boost shared-pointer path. Constructor153c4
  captures current mutable/const/render context and its owner-thread field+38,
  detaches TLS associations and sets selected context owner-thread fields to-1.
  It creates an OpenOnceGate+40 and callback result+50. This is context transfer,
  not a demonstrated caller-held lease on every registry reader.
- Threaded wrapper164e0 branches to full template164e4–16960. Executor virtual
  +38 decides direct-current-executor path; that path reattaches context and
  calls the requested function directly at16578. Otherwise retained context/
  gate/error/result owners are bound into ExecuteStatic and submitted via+10
  at16784; the returned submission value is not checked on that selected path.
  It waits on its one Gate in50ms intervals at167ec, polling the process-wide
  termination flag before each wait. Submission failure/lifetime/private-thread
  preconditions cannot be guessed; no host call or retry was attempted.
- Event-loop wrapper16060/full template16064–164e0 has corresponding direct/
  dispatch/context/result paths. Neither reviewed template joins every general,
  analysis, housekeeper or effect-registry consumer queue established by EXE.
- ExecuteStatic16a80–16e4c clones the selected error state, attaches the supplied
  contexts through U_ResumeContext, invokes one function at16b10 or16b38, stores
  its result, destroys the resume scoper and opens that callback Gate at16d18.
  Exception translation and unwind also preserve Gate opening at16e3c. Gate
  opening establishes this callback path only, not all downstream observers/
  housekeeper removals or MFR work completion.
- Resume scoper16e6c–16fe4 attaches mutable/const/render context TLS and updates
  owner-thread fields to U_GetCurrentThreadID. Its destructor16fe4–171f0 detaches
  these associations and releases retained owners. Suspend destructor15c24
  restores the saved owner-thread field/TLS, then releases result/Gate/context
  owners. These private lifecycle/thread requirements remain UNKNOWN.
- Six complete TLS attach/detach helpers and three current-context get/has
  functions use thread-specific data. Activation getters14cd8/29874 create or
  reuse one context's token and return a retained std owner pair. The token
  stores a boost weak context pair; selected last-owner paths release its weak
  count and allocation. Clear146e0/2af4c removes/releases that context's pair.
  This ownership is not proven all-reader exclusion or whole-effect rollback.
- TerminateAndFailAllSuspendedContexts16e54–16e6c consists of a byte CAS0→1
  on the process-wide flag read by dispatch/wait paths. It does not contain a
  worker join. Excluded as registration safety/control or reversible recovery;
  it was never invoked. Destructive lifecycle names remain outside live scope.

Added fixed suspend-contexts collector/helper with original nlist metadata,
complete-body byte hashes and all-instruction transcript digests, reusing the
existing bounded parser. No output cap change, new native adapter, live profile
or file-only profile change. Initial focused refusal exposed a mistaken assumption
that U was absent from the native data profile; it was already pinned. Restored
the unchanged three-entry file-only profile and reused U's existing native data
pin in the collector. Initial failures/correction preserved; no safety guard
weakened.4 helper/79 collector focused PASS. Subsequent original label review
also corrects the initial linkage: BEE scopers call U_RenderContext::GetCurrent /
GetState (d4001c/d40058); they are not direct U_SuspendContext acquisitions.
Death imports its termination method (d40208). Other New/CallOnThreaded imports
and actual U definitions are separately verified; no complete BEE call-site or
universal reader coverage inferred from that import inventory.

## Verification of the clean candidate

Exact tested/pushed code **b01ae48ea8ee56a1994940933f8e327dd6902e94**.
494 Python/no skips,62 Node/all22 steps PASS. Owned macOS native smoke PASS,
actual AE pipeline BLOCKED, product package acceptance NOT RUN. All376 tracked
files match Git/working/scanner/final runner. Live native data profile, file-only
pin profile, actual native backend and unrelated source bytes unchanged.

Independent original review imports no current collector:27 complete bodies /
3788 instruction words/full-transcript digests,571 direct/322 conditional/86
indirect branches/25 returns,47 scalar fields,5 ADRP+ADD pointer decodes,
2 original chained activation-owner slots and4 BEE/aelib import ordinals PASS.
The three decoded termination flag references resolve to b0000. Twelve historical
archive/manifest/pin checks PASS, exact SDK25.6_61/Apple layouts unchanged.

Raw scanner exit1/review_required,253 text/123 unsupported/no omissions,all9
checks completed; release readiness not_assessed. Sole local argparse mode
false positive at tools/artifact_manifest.py:71 manually reviewed with exact
context/diff; raw finding retained without suppression or scanner PASS claim.
Only the fresh owned scanner checkout removed after376 byte/clean/no-ignored/
no-untracked/UID/no-symlink proof and raw retention. Original captures,
preliminary refusals/corrections and historical/unknown materials retained.
Private receipts: build-ae-hot-loader/suspend-closeout-b01ae48-xmz2dk8k;
original captures: build-ae-hot-loader/suspend-original-e_7wmioy.

| Evidence | SHA256 |
|---|---|
| resource-suspend-contexts-b6f974cf-33y3yai5.zip |1765728aaa6f8d40463093953bb4ef14262831250673b2730b48e33be2bfae7b |
| Full runner AEHL-checks-jb0kwqur.zip, retained in closeout |fa95cdd6c27493777128303da8b8fb0afa1d09d94b30d6dcd56367d98946bd8d |
| aehl-suspend-original-review.json, retained in closeout |34a320a6286f5691ec26e5d543efe75d6c97e51e458b76a11a3e2b960f619acc |

Both exact-source CI completed/success at b01ae48:
[research37153356616](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37153356616)
and [macOS37153356615](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37153356615).
Required jobs/steps, logs and artifact metadata retained. Artifacts not downloaded
or installed. Synthetic checks do not establish actual AE loading/registration/
apply/render, MAC-001 acceptance or release approval. Final closure changes only
five Markdown records; all241 non-Markdown files remain byte-identical to tested
b01ae48, local links/diff checked. Final source/remote/retention receipt retained
in the private closeout folder; no unrelated native/source/profile change.

## Task reconciliation and remaining work

Packet **PARTIAL:4 DONE /5 PARTIAL /3 BLOCKED**. Implementation/tests/research
evidence complete for the bounded collector; native host safety and acceptance
remain incomplete. This count describes these twelve tasks, not product readiness.

| ID | State | Observable result / remaining condition |
|---|---|---|
| SUS-01 | DONE, bounded file research | Actual U definitions/import image and per-context transfer/activation mechanism identified; live private acquisition/ABI still UNKNOWN |
| SUS-02 | PARTIAL | Current TLS detach/attach and per-context activation owners traced; continuous all-registry-reader admission lease unproved |
| SUS-03 | PARTIAL | One callback Gate and termination flag traced; all general/analysis/housekeeper/MFR/observer owners not joined |
| SUS-04 | PARTIAL | Twelve historical archives/original pins rechecked; complete effect-registry consumer coverage missing |
| SUS-05 | PARTIAL | Prior safe-acquisition evidence retained; initial receiver/read-before-retain/private ABI/thread/full owner graph unresolved |
| SUS-06 | PARTIAL | Publication-before-failure/recovery evidence retained; full registry/canonical/preferences inverse missing |
| SUS-07 | DONE, research only | Fixed collector/helper/real original-byte and transcript refusal controls; focused/full checks PASS, native backend unbound |
| SUS-08 | DONE | Local22 steps/494 Python/no skips/62 Node, independent original/manual and both exact-source CI complete |
| SUS-09 | DONE | Five docs, source-byte verification, evidence, commit/push/remote reconciliation and owned-only cleanup/retention |
| SUS-10 | BLOCKED | Actual AE adapter requires supported01–06 acquisition/admission/thread/owner/recovery contracts |
| SUS-11 | BLOCKED / NOT RUN | Registration→apply→render requires10 and safe current exact-candidate environment |
| SUS-12 | BLOCKED / NOT RUN | Repeat/error recovery trial requires11 and complete recovery contract |

These findings narrow the selected hypothesis to per-context transfer and one
callback completion; they do not provide a safe ordinary-effect registration
transaction. Next requires a different supported host-owned admission/drain
boundary covering all registry consumers, safe retained factory acquisition and
full recovery. The unknown scope must not be bypassed with Pause/Flush/Terminate,
thread suspension, an unchanged scan or another owned mock. Actual host
registration/apply/render NOT RUN; original product/A/B/C1/C2/D/release retained.
