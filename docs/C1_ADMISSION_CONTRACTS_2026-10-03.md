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
