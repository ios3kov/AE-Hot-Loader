# C1 — suspend contexts, admission and completion scope

2026-10-03. Accepted rules8.0.0 /132b7cd32873ba7328e3128ffbb33e1929b74d45,
AI_ENTRYPOINT first. Start clean45a7aa4d6ab92e87e0db81ee419166b1db094e92;
branch research/ordinary-plugin-discovery. C1 Development research, Critical
native ABI/thread/ownership/admission, Standard bounded original file collector.
API-SOURCE, RENDER-001, TASK-CLOSE/CLEANUP and production-engineering apply.
[Twelve accepted tasks and checks](PRODUCTION_PLAN.md),
[previous executor evidence](C1_CONCRETE_EXECUTOR_2026-10-03.md).
Original ordinary-effect/no-restart product and A/B/C1/C2/D/release retained.

Initial missing contract: U_SuspendContext mechanism referenced by BEE item
stage scopers. Identify original defining image and exact symbol ends before
capture; only new selected bodies,<=4096 per capture and unchanged output caps.
No AE install/launch/attach/session read/scan, foreign retain/release/private call,
teardown, thread suspension or application/project/plugin mutation. Unknown
native contracts block dependent implementation/trials; historical evidence
keeps its exact source and does not become current host proof.

Original BEE import ordinal40 and aelib ordinal28 resolve the selected
U_SuspendContext symbols to existing U.dylib. Its offline-only pin:
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
weakened.4 helper/79 collector focused PASS. Full clean-candidate/original/manual/
scanner/CI checks pending; historical results do not cover the new bytes.

SUS-01 DONE for bounded mechanism identification,02–06 PARTIAL;07 implemented
research/checks pending,08–09 IN PROGRESS. SUS-10–12 BLOCKED/NOT RUN: depend on
supported continuous all-consumer/MFR
admission/drain, safe existing factory acquisition/private ABI/thread/full owners,
whole-effect recovery and current safe exact-candidate environment. Native backend
unbound; actual registration/apply/render NOT RUN. Checks NOT RUN on new bytes.
