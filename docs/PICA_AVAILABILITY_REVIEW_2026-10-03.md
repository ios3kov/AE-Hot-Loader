# PICA availability diagnostic — bounded preparation

Date: 2026-10-03. Stage C1 research; Development preparation for a scoped
Validation diagnostic. Rules v8.0.0 / `132b7cd32873ba7328e3128ffbb33e1929b74d45`.
Starting source `9dbc361affe186cb04d30e49bd1f373799909078`.
User approved the eight-step proposal; [acceptance mapping](PRODUCTION_PLAN.md)
was written before implementation. The first six steps prepare/check the packet;
steps seven/eight require a separately authorized real AE diagnostic/result.
No change to the original arbitrary ordinary-effect registration goal.

## Primary API inventory and ownership

Authority: local supplied SDK 25.6_61, unmodified Examples/Headers and Resources.
No Adobe SDK or target binary enters Git. The builder pins AE_GeneralPlug.h,
SPBasic.h, SPPlugs.h, SPAccess.h, SPAdapts.h and SPFiles.h and inventories every
header/resource input. Compile-time assertions use actual SDK types and versions.
AE target is macOS arm64, AE 25.6x101, executable SHA-256
`464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6`.

| API/source | Exact contract used | Boundary |
|---|---|---|
| AEGP sample Grabba.cpp:156-190 / AE_GeneralPlug.h | Host supplies SPBasicSuite at AEGP entry; registers an AEGP_IdleHook through RegisterSuite5, whose SDK version constant is 6 | Host callback provider; no invented private provider or numeric revision substitution |
| SPBasic.h:82-101 | AcquireSuite(name, int32 revision, const void**) may load and retain suite modules | This diagnostic is potentially loading, not passive observation |
| SPPlugs.h:45-54 / SPAccess.h:48-50 / SPAdapts.h:45-48 | SP Plug-ins Suite rev4/rev6, SP Access Suite rev3, SP Adapters Suite rev3 | Acquire four tables once; raw error/presence recorded. Nonzero error is not proof of global absence |
| SPAdapts.h:320-348 | NewAdapterListIterator(NULL global list), NextAdapter until documented NULL end, DeleteAdapterListIterator once | Own iterator only; no list/adaptor creation, mutation or guessed private handle |
| SPAdapts.h:354-364 | GetAdapterName/GetAdapterVersion | Copy borrowed name at most 256 bytes with mapping-safe self reads; maximum 64 entries. Names do not prove ordinary-effect registration support |
| AEGP UtilitySuite6 / MemorySuite1 | Read-only ExecuteScript and owned result/error handles | Exact empty unsaved clean nonrendering project, revision and sorted effect matchNames before/after. No project creation/reset or effect application |

PICA acquisitions deliberately retain at most four successful suite leases until
this controlled AE session exits: ReleaseSuite can unload modules, so no PICA
ReleaseSuite/ReleasePlugin or private inverse/teardown is attempted. AEGP public
snapshot/registration suites and result handles use their existing checked public
ownership paths. The iterator is deleted once after successful creation; ambiguous
creation/error or failed durable cleanup record preserves uncertainty until host
exit. No cleanup retry or rollback claim. Image additions are retained in evidence;
preexisting image loss/change fails external verification.

## Protocol and failure semantics

A separate uniquely named AEGP helper is inert without its exact host/module path
and activation token. Its single request binds source/build/run, PID/start,
self binary SHA and explicit potential-load/enumeration scope. The helper consumes
before parsing/calling; durable private no-follow/exclusive records precede each
stage. Loaded self image, export address, exact target bytes and main thread are
checked. Before and after snapshots must match host/project/registry; this checks
an observed interval and is not a global admission/drain barrier for registration.

Owned control directory is 0700, single-link regular evidence 0600, exclusive
publication; duplicates, tampering, stale controls and foreign PID/start fail
closed. Terminal/result/claim and every required stage are independently checked
by the external observer, which hashes the complete evidence set. Adapter names
remain hex encoded in evidence to avoid assuming encoding. COMPLETE means only
the requested availability/enumeration observation finished consistently.

Native monotonic deadline is checked before/after every stage/API (10 seconds).
It cannot preempt a synchronous SDK call that never returns. External observer
stops waiting at 30 seconds, records TIMEOUT and preserves the live process and
partial evidence; never kills a host, retries a request, or replays lifecycle.
STOPPED/partial/error is not upgraded to COMPLETE. No AddPlugin/AddXPlatPlugin,
AcquirePlugin, AddAdapter, messaging, ordinary scan, registration, unload,
private reinitialization, attach/debugger or preference/security changes.

## Preparation evidence and remaining gates

PICA-01/02: reviewed public provider/iterator contracts implemented; actual host
suite availability remains UNKNOWN. PICA-03: isolated one-shot helper and observer
implemented. PICA-04: focused policy/evidence checks PASS on owned/synthetic inputs:
23 labelled C++ scenarios (one aggregate Python case), plus 15 real-file Python
cases. Synthetic providers/processes are explicitly labelled; Linux publication
transport is synthetic, macOS test uses its real exclusive filesystem primitive.
AE NOT RUN. No current installation, launch or host read performed.

PICA-05 build/sign/hash/inert checks and PICA-06 full regression/CI/review are
pending until the identified clean-source candidate is built and checked.
PICA-07/08 are NOT RUN, pending exact packet prerequisites and live authority.
The accepted conditional proposal and AI_ENTRYPOINT §4.1 do not renew consumed
historical one-shot scopes. Actual authorization must include potentially loading
PICA acquisition and adapter enumeration in a new owned empty-project AE session.

A positive adapter list opens investigation of the actual AE publication bridge;
it does not prove registration/apply/render. A nonzero acquisition error preserves
the raw code and does not establish product impossibility. Private direct-effect
publication remains blocked on ownership, admission/drain and failure contracts.
Preinstalled shell remains a distinct compatible-ABI alternative, not an approved
replacement for the ordinary-effect goal. All A/B/C1/C2/D/release gates retained.

Cleanup review: retain existing installed helpers, SDK, user sessions and historical
or unknown evidence. New build/evidence stays in ignored owned private workspace;
no third-party/root cleanup. No merge, release or installable handoff.
