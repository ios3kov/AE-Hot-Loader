# C1 scoped cancellation, admission and match-name ownership

2026-10-03 ADM-01–10 packet, Stage C1 Development research. Rules8.0.0,
132b7cd32873ba7328e3128ffbb33e1929b74d45; AI_ENTRYPOINT first. Baseline
2685ca657dba7c2613b1902e9937697f3c78cc36. Acceptance/dependencies and six
new original-file windows were recorded in PRODUCTION_PLAN before capture.
Native admission/lifetime/thread/ABI Critical, file collector Standard;
API-SOURCE/RENDER-001/exact-source/TASK-CLOSE/CLEANUP apply. Original ordinary
third-party effect/no-restart scope and A/B/C1/C2/D/release retained.

## Correction: PluginImpl+e8 is match-name storage

Pinned AE25.6x101 arm64 PluginSupport has GetMatchName4d25c–4d264:
`add x0,x0,#0xe8; ret`. SetMatchName4d264–4d330 has the original typed
nlist name `__ZN2ML10PluginImpl12SetMatchNameERKN7dvacore7utility15ImmutableStringE`.
It computes the same field at4d270, checks self-assignment, retains the incoming
string implementation via adjusted virtual slot0, clears/releases the previous
string through adjusted slot+8, then stores the new implementation. Null input
clears/releases the old implementation; terminate tails also remain captured.

Complete ImmutableString destructors in PluginSupport2714–275c and dvacore
de00–de48 use the same clear, virtual adjustment-30 and slot+8 release sequence.
This matches the previously captured PluginImpl Init4becc and D2 4bbd0 field
operations. **The selected+e8 field is an ImmutableString for the match name;
it is not evidence of a separate plug-in provider object.**

The earlier [OBJ checkpoint](C1_FACTORY_OBJECT_OWNERS_2026-10-03.md) recorded
the field's concrete type as UNKNOWN. That was the evidence limit at that time;
this new typed-method/field/destructor evidence narrows that interpretation.
String storage still has owned virtual implementation callbacks. Actual incoming
virtual target, concrete runtime string implementation, complete callback graph
and supported foreign retain/release/thread contract remain unobserved. This
correction does not make a copied pointer valid ownership or enable private calls.

## Exact selected public API inventory

Source: SDK25.6_61 Examples/Headers/AE_GeneralPlug.h, SHA256
30d12ec3eb5af1a902c7414053b1be1da0204b226e0b1cdc71272be1e137000c.
The collector retains selected original excerpts and validates the whole header
before and after collection. No new Adobe host API call is implemented.

| Selected API | Exact declaration / revision | Contract and limitation |
|---|---|---|
| Idle hook/register | Lines2734–2738/2797–2803; A_Err hook(global refcon, idle refcon, A_long* max_sleep), registration with plugin ID/callback/refcon | Callback scheduling does not declare continuous exclusion of registry readers, callbacks or MFR. |
| Render queue state | Lines3199–3240; RenderQueueSuite1 revision1; A_Err Set(state), Get(state*) | STOPPED/PAUSED/RENDERING refer to the render queue; STOPPED→PAUSED is illegal. No selected declaration supplies a host-wide lifetime/admission lease. |
| Layer async request | Lines5330–5385; RenderSuite5 **revision8**, AEGP_AsyncRequestId=A_u_longlong; async call(options, callback, refcon, request ID*) | Callback(request ID, canceled, error, receipt, refcon) is guaranteed except when AE shuts down. Completion is scoped to that request. |
| Async cancellation/checkin | Same selected RenderSuite5; A_Err CancelAsyncRequest(request ID), CheckinFrame(receipt) | Cancel addresses one request ID; checkin releases receipt memory. Neither selected declaration establishes all-reader/MFR drain or prevents new registry/dispatch entry. |

These are selected header contracts, not proof that no suitable API exists
anywhere in AE, nor runtime compatibility VERIFIED. No queue state was changed,
request submitted/canceled or idle hook installed. Synchronous UI render is not
used as a drain/warmup shortcut; the header restricts that use.

## Selected private candidates

aelib capsule CancelRender2dd68–2dfb0 is selected by its original Guid const&
signature. The complete body takes a recursive mutex twice, walks a request
tree and compares the input's two64-bit GUID words (2de50/2de60). A match selects
one queue handle and calls BEE_WorkQueue_Cancel at2deec. Inner lock releases
before the cancellation call; outer lock releases before return. No-match skips
cancellation; exceptional cleanup and terminate/unwind tails remain included.
The opaque BEE callee is not reviewed here: cancellation completion semantics
are UNKNOWN, rather than assumed asynchronous or assumed drained. The selected
wrapper supplies no caller-held token covering subsequent factory/publication
work or all future registry/dispatch entry. Its internal request mutex cannot
be promoted to that contract without evidence of all consumers and its lifetime.

dvacore ScopedThreadSuspend D1 2d1fc4–2d1ff4 reads a single Mach thread port;
nonzero calls thread_resume, then returns, with a terminate tail. This selected
destructor restores one system thread; it does not establish a host-owned
all-reader admission boundary. The constructor/stack-trace context and general
suspension behavior are not claimed. No thread was suspended/resumed.

Existing registry+50 recursive mutex, effect-render counter/scopers, ready
SetdownAsync future and publication-before-preference/lazy-global failures remain
as previously reviewed. A zero-count snapshot, queue pause, cancel return, idle
callback or thread suspension is insufficient to infer continuous admission
plus complete callback/MFR drain. Existing-only factory acquisition still needs
safe initial live reachability/private declaration/thread; its guard/lock/retain
side effects remain. Selected cleanup is not a whole-effect registry/preferences
inverse. Actual AE adapter and registration/apply/render experiment remain NO-GO.

## Implementation and verification state before exact closeout

Added only fixed file-only admission-contracts collector scope: six complete
bodies /247 instructions, every instruction checked, exact original binary pins
and SDK header pin/excerpts. Outputs distinguish scoped cancellation, string
metadata and one-thread resume from actual host admission/drain. Native helper,
live profile, bridge and ResourcePassGate backend are unchanged.

Three new meaningful refusal controls failed against the previous implementation
(scope/functions absent). They mutate every instruction, fields, branches,
cancel/resume/release/unwind operations, duplicate/missing/undecodable rows,
window identity and SDK drift. First implementation exposed a duplicate constant
name interfering with the older module-admission scope; this was corrected
without weakening either scope. Focused76 methods PASS. Both failure logs are
retained; synthetic transcripts verify refusal, not host behavior.

Preliminary private inventory/capture is dirty-plan exploration only, under
build-ae-hot-loader/admission-inventory-00whrzh8. Full runner, original-byte
review, raw scanner and exact-source CI are NOT RUN for the new clean candidate
at this checkpoint. Dependent actual adapter/trial BLOCKED; host registration/
apply/render NOT RUN. Complete task reconciliation follows exact-source checks.

## Exact local checks and retained evidence

Clean tested/pushed code **ae5ca5cd30bf3e2aa1538dc3659e4ebe939a8f25**.
Final six-body/247-instruction collector archive
resource-admission-contracts-35adff80-ymb85vdi.zip SHA256
4977fab1f5aff03ab99d28e709cc71a5b797b558000b6eb0a77302aa526a1014.
Full offline runner AEHL-checks-rd3x4zs_.zip SHA256
1d5a4714ed5d61133b2152a3ffe4f7730747a6356fa88b71fae60a042e2a9c56:
471 Python/no skips,62 Node,all22 stages PASS;367 tracked source bytes
unchanged. Existing owned native execution is included; AE runtime is not.

Independent review imports no collector: exact original Mach-O/nlist/branch/
field words and ZIP manifests, typed setter/getter and complete string destructor
correspondence, selected exact SDK header/excerpts/revision. Two new/reused
archives /eight windows /677 instructions,129 direct53 conditional20 indirect
branches,nine returns,20 field decodes; nine earlier archive identities/CRC/
manifests and current original pins revalidated without recapture. Receipt SHA256
7652dbd6215e55059406b6dffc61d831a6e76803df620b5b4bd7dfab7c4c4344.
Preliminary verifier refused its incorrect x31 address-base decoding; corrected
to sp, with observed refusal retained. No original file or expected instruction
was changed to make it pass.

Raw scanner exit1/verdict review_required/release_readiness not_assessed retained:
244 text123 unsupported/no omissions, all configured checks completed. One
local argparse create/verify CLI false positive at tools/artifact_manifest.py:71
reviewed without suppression; file has no HTTP route/listener/auth endpoint.
Manual review SHA2565548057a7f12525dbdeb1b5c23dec85887e90ff77f5b2e194f617e15ae430d9d.
Scanner scope is not host or release certification.

Research CI37147989601 and macOS CI37147989620 are running at exact ae5ca5c;
their completion is still pending. Private retention/cleanup record is under
build-ae-hot-loader/admission-closeout-ae5ca5c-*; all preliminary/raw/refusal/
runner/original evidence remains. Only the fresh byte-matched owned scanner
clone was removed; application/SDK/projects/plugins/preferences untouched.

## ADM-01–10 reconciliation

| Task | Implementation/task state | Check/evidence and remaining acceptance |
|---|---|---|
| ADM-01 | PARTIAL | Exact selected SDK and bounded private controls reviewed. Continuous registry/dispatch admission provider not established; no caller-held host token. |
| ADM-02 | PARTIAL | Queue versus request versus one-thread scopes distinguished. Opaque cancel completion/all callbacks/MFR and continuous drain still UNKNOWN. |
| ADM-03 | PARTIAL | Historical exact-source existing-only factory/owner evidence reused and pins/archives verified. Safe initial live receiver/private declaration/actual thread contract still unproved. |
| ADM-04 | PARTIAL | Selected+e8 type resolved as match-name ImmutableString; old provider interpretation corrected. Actual inner implementation/indirect targets/full callback graph remain unobserved. |
| ADM-05 | PARTIAL | Existing publication-before-failure/local cleanup evidence retained and verified. Complete registry/canonical/preferences inverse still unproved. |
| ADM-06 | PARTIAL | Fixed collector/SDK evidence component implemented and tested. Actual adapter remains conditional on01–05 and backend unbound; no installable host candidate. |
| ADM-07 | DONE within changed collector scope | Three new meaningful refusal tests, all247 instruction mutations, bounds/rows/symbols/SDK drift; old-scope regression caught/fixed;76 focused methods PASS. Actual AE reentry/lifetime remains NOT RUN. |
| ADM-08 | PENDING CI | Exact local471 Python/no skips62 Node/22 stages/source/scanner/manual/original proof PASS or explicitly reviewed. Both exact-source CI completion pending. |
| ADM-09 | BLOCKED | Prerequisites01–05 unresolved. No executable AE trial; no install/launch/attach/read/scan/private invoke. Registration/apply/render NOT RUN independently. |
| ADM-10 | PENDING final CI reconciliation | Plan/checkpoint/status/handoff/compatibility updated; evidence/refusals retained, owned scanner clone removed. Final exact-CI/docs-source/remote/retention closeout pending. |

Full ten-task packet PARTIAL. No task criterion removed or replaced with an
owned/mock PASS. Original ordinary-third-party/no-restart product, A/B/C1/C2/D
and release gates remain open. The newly identified field removes one specific
mistaken hypothesis; this is a bounded research advance, not a working hot-load
demonstration or completion percentage.

Next authorized file-only research should first locate the opaque BEE work-queue
cancellation target and determine its request/completion scope before designing
any host boundary. Record exact missing bodies/pins before capture. Cancellation
alone would still need a demonstrated continuous all-reader admission token,
safe initial factory/thread/ownership contract and complete failure recovery.
Do not repeat the unchanged scan, suspend user threads or invoke a wrapper merely
because its name or local mutex matches part of the desired behavior.

## CI failure and bounded aggregate-runner repair

The pending-state checkpoints above belong to ae5ca5c and are preserved as
history. Research CI37147989601 native job111275777106 failed; panel job passed.
Downloaded original artifact11283247492, ZIP SHA256
86a1635ccad9952765d48a4f71be4457b16150215a6506a42b7111476576234a,
confirms Python stage FAIL after120.058s with reason `Test time limit exceeded;
no retry`, absent worker summary and subsequent stages NOT RUN. The log ends
during an existing native transaction test; no assertion failure is reported.
Local completed suite took114.341s. This is an aggregate deadline failure, not
an AE result or a passed CI. The failed archive/job log/report remain retained.

ADM-08 scope/acceptance updated before repair. Only the aggregate Python suite
gets a bounded480s budget; individual commands keep120s and native per-test
limits/output limits/failfast/owned child cleanup remain. Runner records the
actual selected stage budget. A new real subprocess/worker-evidence test failed
before implementation, then25 focused runner methods PASS, including actual
timeout/failure/owned-process cleanup controls. Final new-source full checks/CI
are pending. Collector bytes are unchanged, so its ae5ca5c archive keeps its
historical identity and can be reused with byte-invariance proof.
