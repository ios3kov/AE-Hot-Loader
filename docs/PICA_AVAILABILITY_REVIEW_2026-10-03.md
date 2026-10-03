# PICA availability diagnostic — preparation and live result

Date: 2026-10-03. Stage C1 research; Development preparation for a scoped
Validation diagnostic. Rules v8.0.0 / `132b7cd32873ba7328e3128ffbb33e1929b74d45`.
Starting source `9dbc361affe186cb04d30e49bd1f373799909078`.
User approved the eight-step proposal; [acceptance mapping](PRODUCTION_PLAN.md)
was written before implementation. The first six steps prepare/check the packet;
steps seven/eight require a separately authorized real AE diagnostic/result.
No change to the original arbitrary ordinary-effect registration goal.

## Current result — PICA-07/08 completed on the exact candidate

After the concrete packet/permission request, the user's direct reply
“продолжай” authorized this stated install/one-launch/public snapshot/PICA
availability/adapter-enumeration operation. AI_ENTRYPOINT §4.1 applies the reply
within that exact proposed scope; the permission did not originate from a manifest
or old checkpoint. Main AE process was verified absent before installation and
again before launch. Other matching background brokers/crash reporters were
preserved. No active-user-process termination or existing project reset.

Candidate source **f21064a5ea0e9dc41828987d365d18f8687515e2**; documentation baseline
`6094f9a2cd7b7d807c573849889f92f92b5da4a2`. The difference is documentation only;
source/build/manifest/final binary identities above/below are unchanged.
Actual Build **pica-1840ac76ef3b**, final binary
`e80e5875033d13e2d43922cc852092ddb2bc056733f5dd91215287852f13066b`.
One controlled AE 25.6x101 arm64 launch, PID **14298**, start **1791030995.377505**;
run `pica-availability-d320f17bf29f496893a345a19c1cee13`.
Installed file inventory/sign verification PASS; preexisting MediaCore entry
identities/modes preserved. Startup readiness matched exact loaded helper/source,
module, process and run. One request published; no replay/restart.

| Requested observation | Actual result |
|---|---|
| SP Plug-ins Suite rev4 | AcquireSuite error 0; provider present |
| SP Plug-ins Suite rev6 | AcquireSuite error 0; provider present |
| SP Access Suite rev3 | AcquireSuite error 0; provider present |
| SP Adapters Suite rev3 | AcquireSuite error 0; provider present |
| Complete global adapter enumeration | One entry: **Sweet Pea 2 Adapter**, version **1**; documented NULL end observed, owned iterator deleted once |
| Project/registry/host baseline | Same exact PID/start/module/source, blank unsaved clean idle project revision **1**, **786** effect identities before/after |
| Loaded images | **1409** before/after, byte-identical image inventories; additions **0** |
| Native terminal + independent observer | **COMPLETE**, independently reverified exact request/claim, every required stage, terminal/result and original evidence hashes |
| Ordinary-effect registration / apply / render | **NOT RUN**; no mutation APIs were invoked |

PICA-07 **PASS for the scoped availability diagnostic**, actual AE loading of this
identified local helper observed. This is not full product/release MAC-001 pass.
PICA-08 **complete**: the actual provider is available, but an ordinary-effect
publication bridge remains unverified. Runtime authority is now consumed.
Prep builder manifest intentionally remains immutable (its installation/launch
fields describe build time); actual setup/runtime are separate identified receipts.

Primary SDK interpretation: `Headers/SP/SPInterf.h:62-65` defines
`kSPSweetPea2Adapter` and version 1 for PICA version 2.
`SPAdapts.h:267-276` distinguishes that adapter from application legacy adapters;
`SPInterf.h:97-100` limits generic PICA messages to PICA plug-ins, with a separate
adapter interface needed for non-PICA targets. Therefore the one enumerated entry
is the standard PICA adapter. **No separately identified ordinary-AE-effect adapter
was observed in this complete global list for this exact host/session.** This
neither proves all possible bridges absent nor justifies treating PF_Cmd-style
ordinary effects as PICA-message plug-ins or guessing adapterInfo/opaque casts.

Combination decision: **NO-GO for AddPlugin/AddXPlatPlugin/AcquirePlugin or direct
ordinary-effect publication now**. Suite availability alone does not establish
owned AE registration receivers, lifecycle conversion, continuous admission/drain,
completion/error/rollback contracts. PICA + private publication remains conditional
on those contracts; PICA + preinstalled shell still requires initial registration;
three-way combination has no accepted safe native design. Original product goal,
A/B integration, C1 publication, C2 apply/render, D compatibility/hardening and
release obligations remain open. No universal loader or impossibility claim.

Next discriminator: review and prepare bounded **public PICA plug-in inventory
correlation** with known startup-registered ordinary-effect files. The SDK declares
NewPluginListIterator(NULL)/NextPlugin/DeletePluginListIterator and GetPluginAdapter;
rev6 GetPluginXplatFileSpec requires its exact XPlatFileSpec/CFURL ownership review.
Actual list contents/correlation are NOT RUN. Avoid FindPluginProperty: its documented
fallback can send a message and modify a property list (SPPlugs.h:492-499), so it is
not an assumed passive name getter. No AddPlugin/AddAdapter, AcquirePlugin, global
list free, messaging, private access or registration without a newly reviewed,
identified packet and its actual applicable authority. This is the next research
question, not an approved executable design or renewed live scope.

Evidence retained in ignored private `build-ae-hot-loader/pica-1840ac76ef3b/`:

- `control/external-result.json`: SHA-256
  `0e4933a74a6739e2a41c9dbdfbfee7cf926f237201c323724b8c4b7c52df997c`.
- `live-verification.json`: SHA-256
  `dbdf5b24289da284e7d43b8284b3d8def3bdec9905068519c1748c978a1cbeb0`.
- `pica-live-private.zip`: 30 members, CRC checked, SHA-256
  `eb04fb9f70627c1221cbe0437cd643ee7849395dfa7900a8d9e63833bab9b841`.
  Private original transport includes its consumed token; not uploaded or committed.
- Before/after project/registry payloads equal; images-0/images-1 SHA-256 both
  `786e3510f8bd35638d9e4448f593b1b4b3875d08d27a0318e7aca55e118e598f`.
  Terminal SHA-256
  `e4e66a2db563dfe32f73fb17825676fa9d18bece0aee9f07e5840bf93b9e5d39`.

No code/build input changed. Prior exact-source 399 Python/no skips, 62 Node,
22 local stages and both CI success remain the preparation receipts; they are
not reported as tests rerun for this documentation closeout. Actual runtime is
separate evidence above. Repository links/whitespace and final branch state are
checked at closeout. No merge/release, private call, scan, unload, preference or
security change. Cleanup: do not remove the loaded helper or terminate a session
that may become user-owned; keep the identified installed helper inert/consumed
and preserve all receipts/SDK/other plugins. Normal session exit and guarded
removal of only the exact owned helper remain pending closed-host cleanup.

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

PICA-05 build/sign/hash/inert and local PICA-06 regression/review are complete
at the identified clean-source candidate below. CI is reconciled in closeout.
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

## Identified packet — historical pre-run scope at 6094f9a

Code/test source **f21064a5ea0e9dc41828987d365d18f8687515e2**, clean when built
and tested. Build **pica-1840ac76ef3b**; run
`pica-availability-d320f17bf29f496893a345a19c1cee13`.
Final binary SHA-256
`e80e5875033d13e2d43922cc852092ddb2bc056733f5dd91215287852f13066b`.
Private manifest SHA-256
`a473c0218e00259056e7f9c75071daaf58c1573f4fd299ba63a8d01cfe915340`.
Candidate and private manifest/control are under ignored
`build-ae-hot-loader/pica-1840ac76ef3b/`; 4 bundle files / 74 SDK inputs independently
rechecked. Exact real-SDK compile, local ad-hoc sign/verify, export set, identity
getter, inert null/token/wrong-host and resident self/export/changed-hash checks
**PASS**. Control remains empty; prospective destination absent. No installation.

Proposed sole new installation path:
`/Users/os3kov/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore/AEHLPica1840ac76ef3b.plugin`.
It must be absent; copy only this identified bundle with AE fully closed. Preserve
all installed helpers and third-party files. One newly controlled AE 25.6 session,
no user project ownership assumption, no active-session termination. Its initial
project must actually be blank/unsaved/clean/nonrendering; restored or nonowned
project blocks the request, with no reset/discard automation. Exact loaded helper,
AE executable/PID/start and private readiness must match before publishing once.

Intended operation: public project/effect snapshot; acquire the four exact PICA
suite revisions (may load modules); enumerate adapter name/version via the public
iterator if available; snapshot after and preserve image additions, raw error,
terminal and evidence hashes. No effect registration/application/rendering, scan,
private call, attach/debugger, preference/security changes, restart/retry or unload.
Native 10-second cooperative deadline / external 30-second wait; on a hung SDK call
preserve the process and partial evidence. This preparation does not authorize
force termination. After completion, session exit/removal of only this owned helper
requires a closed host and ownership/inventory checks; no existing plugin cleanup.

PICA-05 completed. Local PICA-06 regression **399 Python/no skips, 62 Node,
22 stages PASS** at exact f21064a; report
`/private/tmp/AEHL-checks-utsfsheg.zip`, SHA-256
`18ad13ae6c98e711ee21388d58db798acdb9d489185d9dcabada853977ad1119`.
ZIP CRC, all 25 member hashes and 320 tracked-source hashes independently verified.
Bounded static review completed at the same source; raw exit **1**, sole reviewed
local argparse false positive at tools/artifact_manifest.py:71, no suppression.
Private scanner SHA-256
`43a085eb6e8648ff25a3f0524d73180b021fee190bf2b78c2af6488cfb82e675`.
CI reconciliation follows below; PICA-07/08 remain NOT RUN until live prerequisites
and actual operation permission. Prepared packet is not a release or ordinary
registration proof. Doc-only closeout is distinct from the tested code identity.

## Preparation reconciliation at 6094f9a — before live authorization

[Research CI 37122917227](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37122917227)
completed/success, panel-contract and native-syntax jobs success.
[macOS CI 37122917217](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37122917217)
completed/success, build/sign/ABI smoke/package roundtrip success. Both are at
exact **f21064a5ea0e9dc41828987d365d18f8687515e2**. Research CI runs the portable
policy/evidence tests; the supplied SDK/helper build is local, not claimed as a
CI SDK build. Neither CI runs AE or validates hot effect registration.
Private `ci-review.json` SHA-256: `864495c1a61111c61d63d92f152078ef8c792552a2c9feb8dd53ac7f1bd7b468`.
`preparation-review.json` SHA-256:
`10e1ee2ee5a3d6975742606f34b21a6a7fa08dd7bc7d8f8be7828c283db187fd`.

| Requirement/task | Acceptance result | Evidence / retained limit |
|---|---|---|
| PICA-01 | PASS for exact public access contract | Local SDK pins and successful provider/callback signature assertions; AE availability UNKNOWN |
| PICA-02 | PASS for bounded enumeration contract | Exact SDK iterator/getter assertions, owned iterator and bounded names/count; actual adapters UNKNOWN |
| PICA-03 | PASS for implemented separate one-shot diagnostic | Public helper/build manifest, request/source/runtime/self binding, durable stages; AE NOT RUN |
| PICA-04 | PASS for owned/synthetic refusal/failure/deadline checks | 23 labelled native cases plus 15 real-file Python cases; not counted twice in 399 total |
| PICA-05 | PASS for identified candidate prerequisite checks | Clean f21064a, real SDK arm64/sign/exports/getter/inert, final SHA and 4-file inventory; no installation or actual AE load |
| PICA-06 | PASS for available regression/review/CI/packet/docs | 399 Python/no skips, 62 Node, 22 stages; independently checked ZIP/source/SDK, raw static-review finding retained, both exact-source CI success |
| PICA-07 | NOT RUN | Fresh live authorization and current fully closed host required before installing this sole new helper/session; baseline checked without resetting a project |
| PICA-08 | NOT RUN | Depends on actual PICA-07 evidence; no fabricated availability/publication conclusion |

All six preparation tasks are complete. Prepared Validation packet prerequisites
are distinct from actual host loading and final product acceptance. Public suite
calls may load modules, so the consumed passive/no-new-image and old diagnostic
permissions do not cover this new operation. The proposed one-shot scope above
needs an actual human reply; command-line flags or this checkpoint are not consent.
[AI_ENTRYPOINT §4.1](https://github.com/ios3kov/AE-Development-Rules/blob/132b7cd32873ba7328e3128ffbb33e1929b74d45/AI_ENTRYPOINT.md#41-продолжение-работы-и-границы-разрешений):
“Повторно не запрашивать ранее выданное действительное разрешение в том же scope.”
Here prior one-shot scopes are consumed, and the new request expressly permits
potential module loading rather than assuming unchanged images.

Final checkpoint: Stage C1, original ordinary-effect goal retained; backend NOT
READY, registration/apply/render NOT RUN, A/B/C2/D/release obligations open.
No merge/release/installation/host operation or executable registration adapter.
Cleanup retains the uniquely identified build and private receipts for the next
step, all installed/SDK/historical/unknown materials; owned disposable test fixtures
self-clean only. Documentation-only closeout changes no code/build inputs and
must not be presented as the code/source identity tested above.
