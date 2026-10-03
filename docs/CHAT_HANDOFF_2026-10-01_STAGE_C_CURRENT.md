# AE Hot Loader — current Stage C handoff, updated 2026-10-03

Continue the existing work. Do not restart research or repeat the unchanged
ordinary plug-in scan.

Current continuation: [scoped admission controls and match-name correction](C1_ADMISSION_CONTRACTS_2026-10-03.md),
[actual factory object owners](C1_FACTORY_OBJECT_OWNERS_2026-10-03.md),
[factory dependency lifetime](C1_FACTORY_DEPENDENCY_LIFETIME_2026-10-03.md),
[native reference call boundary](C1_CLASSREF_CALL_BOUNDARY_2026-10-03.md),
[registry transaction batch](C1_REGISTRY_TRANSACTION_BATCH_2026-10-03.md),
[provider/isolation batch](C1_PROVIDER_ISOLATION_BATCH_2026-10-03.md),
[entry/lifetime batch](C1_ENTRY_LIFETIME_BATCH_2026-10-03.md),
[provider/factory review](C1_PROVIDER_FACTORY_REVIEW_2026-10-03.md),
[dispatch review](C1_EFFECT_DISPATCH_REVIEW_2026-10-02.md),
[publication review](C1_EFFECT_PUBLICATION_REVIEW_2026-10-02.md),
[retained names live PASS](C1_RETAINED_NAMES_LIVE_PASS_2026-10-02.md),
[rules adoption](RULES_ADOPTION_8_0_0_2026-10-03.md),
[supervisor deadline review](C1_SUPERVISOR_DEADLINE_REVIEW_2026-10-02.md) and
[prepared native candidate](C1_OBSERVER_CANDIDATE_REVIEW_2026-10-01.md).
The current C1 section and next-gate order below supersede historical no-scan
preparation/permission statements in this handoff. C0 is closed; do not repeat it.
The earlier `CHAT_HANDOFF_2026-10-01.md` is a historical checkpoint.

## Scoped controls and corrected match-name dependency — current continuation

Exact clean tested/pushed code b693169b3b25bfc660ba0bb27f0859965144833c;
[ADM checkpoint](C1_ADMISSION_CONTRACTS_2026-10-03.md). PluginImpl+e8 is a
match-name ImmutableString, established by typed setter/getter and two complete
string destructors. The earlier separate-provider interpretation below is
historical; string implementation callbacks/full host ownership still unobserved.

Selected SDK25.6_61 queue/idle/request controls and private GUID cancellation /
single Mach thread resume do not establish continuous all-reader admission and
callback/MFR drain. Opaque BEE cancellation completion remains UNKNOWN. Do not
turn idle, queue pause, cancel return, a zero counter or thread suspension into
that proof. Actual acquisition/private thread contract and whole-effect recovery
also remain required. AE adapter/trial BLOCKED, registration/apply/render NOT RUN.

Six new complete bodies/247 instruction anchors with exact SDK excerpts/pin;
76 collector /25 runner focused /472 Python/no skips,62 Node/all22 stages PASS;367 source-byte proof.
Independent original eight-window/677-instruction/20-field review, nine reused
archive/pin checks PASS. Raw scanner1 preserved, local CLI false positive reviewed
without suppression. Original evidence retained; only new owned scan clone removed.
Both exact-source CI37148392586/37148392471 completed/success. Earlier ae5ca5c
Research CI120s timeout FAIL/artifact retained; aggregate worker480s, individual
command120s and owned timeout/failure guards unchanged. Packet PARTIAL:
3 DONE /6 PARTIAL /1 BLOCKED; no executable host packet. Docs-only closure proves
235 non-Markdown files unchanged; final private retention/source/remote record
in admission-closeout-ae5ca5c-bda0_fy8/fixed-candidate. All original gates retained.
Next bounded file research can follow the opaque work-queue cancellation target
and its admission/completion scope; actual wrapper call is not an authorized or
proved replacement for a host-owned token and recovery boundary.

## Previous actual factory object owners — selected chain traced, host trial blocked

[OBJ checkpoint](C1_FACTORY_OBJECT_OWNERS_2026-10-03.md): twelve-task packet PARTIAL,
6 DONE /5 PARTIAL /1 BLOCKED. Exact code2b0dbdd04590dcae6cada595ba368b5726f2d288.
Module stores retained PluginImpl/PiPL owners, destroys PiPL before PluginImpl and
then its mutex/base/weak state. PluginImpl releases image/other controls and a
separate private+e8 virtual owner. Selected file class's last-owner route is bound
through original destructor slots. Cache handback replaces/releases old outputs
and invokes a virtual query; never use it as a read-only live probe.

Fixed8-body/325-instruction/five-rebase collector and four refusal regressions
complete; independent9-archive/38-window/4215-instruction/29-field/8-atomic review
PASS.468 Python/no skips,62 Node/22 stages PASS,366-source proof; both exact-source
CI37146890744/37146890712 completed/success. Scanner raw1/CLI false positive
retained,243 text/123 unsupported/no omissions; no suppression. Private receipts
at build-ae-hot-loader/objects-closeout-2b0dbdd-8dpr93ct, cleanup only fresh clone.

Actual retained initial receiver/ABI/thread, concrete provider/full callbacks,
continuous all-reader/render/MFR admission/drain and whole-effect recovery remain
required. The observed registry mutex/counter/ready future do not supply that
boundary. Native adapter/executable trial BLOCKED; registration/apply/render NOT RUN.
Next identify and prove the actual admission/drain provider plus ownership/recovery
contract. No unchanged scan/private cache call/foreign teardown/gate bypass.


## Factory callback dependencies — owned teardown order demonstrated

[DEP checkpoint](C1_FACTORY_DEPENDENCY_LIFETIME_2026-10-03.md) follows the native reference packet. Complete reused MEE cleanup bodies map selected factory/vector release paths. The bounded owned lease holds listed provider images through result destruction. Two dynamic callbacks ran after harness handles/original owner dropped; order2→30→40→1→3→41→31 confirms reference release, both callbacks, object/factory destruction and reverse provider unload. Same-lease reentrant Diagnostic/Reset/transfer guards pass; wrong-order TDD and initial observer failure remain preserved.

Exact source **a75a5aa15044b4a4606e5fe39a4185f018fbfab4**:464 Python/no skips,62 Node/22 stages,365 tracked source bytes unchanged. Scanner raw1 and the CLI false positive are retained/reviewed without suppression;242 text/123 unsupported/no omissions. Both exact-source CI succeeded. Five focused methods/eight native processes; preliminary count corrected to eight.

Actual AE callback graph/provider-object ownership, ABI/thread and host admission/drain/rollback remain unknown. AE registration/apply/render not run. Next prove real callback/provider lifetime, then host-wide entry exclusion, render drain and rollback. Product remains partial.

## Native reference — calling and complete-result cleanup prototype checked

[Current CALL packet](C1_CLASSREF_CALL_BOUNDARY_2026-10-03.md) supersedes the
previous owned-ABI implementation checkpoint. Complete original caller/cleanup
shows whole24-byte destructor base; raw nlist confirms12 shared-entry aliases.
Actual owned nontrivial C++ return uses new hardwired-false arm64 carrier/CFI and
stable raw heap output; whole-base destruction/moves/exception/no-create/continuous
code lifetime/refusals and ASan/UBSan PASS. AE identity-only profile refused before
original file/resident access; no actual Adobe private call/helper integration.
Exact tested code ddfe06c1733b8e77c3912b0a45495adcb0ab9551:459 Python/no skips,62 Node/
22 stages;360-source/ZIP/original/native-artifact review PASS. Scanner raw1/CLI
false positive retained,240 text/120 unsupported/omissions[], native checked
separately. CI37143658830/37143658832 completed/success. Private evidence/artifacts
and preliminary results retained; only owned clean scanner clone removed.
Eight-block bounded research packet complete; product PARTIAL, actual AE adapter
BLOCKED, acquisition/release/registration/apply/render NOT RUN. Next substantive
actual retained receiver/acquisition/release/thread contract, then late-host
admission/render drain/atomic whole-effect rollback. Original gates retained;
no unchanged scan, foreign lifetime operation, gate bypass, merge or release.

## Existing factory — owned acquisition and code lifetime implemented

[Current lease packet](C1_EXISTING_FACTORY_LEASE_2026-10-03.md): non-creating
MEE branch reviewed without new Adobe capture; it can still initialize guards/atexit.
Repo-owned24-byte opaque ABI acquisition and resident-only exact-pinned code lease
implemented, real native cross-module lifetime/move/absence/expiry/refusal/sanitizer
tests PASS, release before image close/unload observed on fresh owned fixtures.
Exact codea9a7f7211f9d2ee2e12cae05600a4dbcb6045e2b:455 Python/no skips,62 Node/22 stages,
353-source/ZIP/native-artifact/original-byte review PASS; raw scanner1/local-CLI
false positive retained,238 supported text/115 unsupported types/omissions[];
native manual/strict compiler/sanitizer coverage separate. Both exact-source CI
37141951178/37141951225 completed/success. Private evidence/artifacts retained,
owned clean scanner copy removed; historical/shared/app/SDK/session state untouched.
Actual AE adapter and full product remain PARTIAL/BLOCKED; owned ABI is not Adobe
classref ABI. Next real retained acquisition/release/thread contract, then host
admission/drain/whole-effect rollback. No unchanged scan or private call on this basis.

## Transitive factory — creation and ownership paths traced

[Transitive review](C1_FACTORY_TRANSITIVE_2026-10-03.md):24 complete pinned dvacore/
MEE windows /1369 instructions /780 anchors. Class-map registration and lookup
locks found; shared lookup lock ends before the creation callback. Throwing24-byte
return and status/output-reference variants differ; successful status is not proof
of a valid receiver. Shared-from-this temporarily retains weak storage, obtains
strong ownership through libc++ lock, can return empty/throw, and reads object/
vtable BEFORE that lock. Copied integers cannot establish initial safe reachability.
Both distinct GUID storage cells use same36-byte literal/address/constructor during
initialization; earlier missing-counterpart question resolved statically. Actual
runtime GUID equality NOT OBSERVED. New fixed collector and four TDD/refusal tests
implemented; exact-command4 MiB dvacore symbol budget correction preserves2 MiB
for all other inspections. Actual retained host adapter remains BLOCKED.
At exact clean code2f5fcb962dd4509e5f485b7d2cf6db017c6ae887:69 focused /
450 full Python/no skips,62 Node/22 stages PASS. Clean collection/separate raw branch/
GUID/import/nlist/ZIP/346-source-file review PASS. Initial collector/scanner size
refusals preserved; final scanner scans independently byte-matched clean local Git
clone, raw exit1/local-CLI false positive retained. Research CI37140197009 and macOS
CI37140197001: completed/success. TRANS-01–06 bounded file findings documented;
07 research collector/refusals done, actual supported receiver/call/thread component
BLOCKED;08 local checks/review/both CI/retention/docs/cleanup complete.
Backend NOT READY; registration/apply/render NOT RUN. Product/A/B/C1/C2/D/release
retained. Next: substantiate non-creating existing-factory acquisition, callable ABI/
initial reachability/retained ownership/thread boundary; host-wide admission/drain/
whole-effect rollback still required before a live registration packet.

## Factory receiver — acquisition route traced, actual ownership open

[Receiver review](C1_FACTORY_RECEIVER_2026-10-03.md): exported registration links
class creation callback, typed query, retained-owner transfer and factory-registry
insertion. Instance may create; it is not proved a read-only existing-object lookup.
Original final-vtable UnknownBase shift is0, distinct shared-from-this shift0x38;
exact31/24-byte query names independently reconstructed without the closing bracket
shown after the source literal in LLDB comments. Runtime equality of distinct class
GUID cells/transitive ClassFactory and GetSharedFromThis contracts remain UNKNOWN.
A concrete copied24-byte reference decoder implemented; diagnostic integers only,
no object read/retain/callable pointer or gate capability. Real owned C++ lifetime/
alias transfer/last destruction/weak expiry/replacement/stale-byte controls PASS with
ASan/UBSan. The stand's layout token is not a C++/Adobe shared control block. Copied
plausible pointers survive object destruction; shape cannot prove ownership/liveness.
At exact clean research code 4ca1e665ec418b2bc7cde008b48ac67b1832865a:65 collector +2
native focused,446 full Python/no skips,62 Node/22 stages PASS. Clean14-window/
563-instruction/481-anchor collection and separate original-byte/query/header/import
linkage/ZIP/345-source-file proof PASS. Raw scanner exit1 retained; local-CLI false
positive reviewed. Research CI 37138868803 /macOS CI 37138868787 success at
exact4ca1e66. RECV-01/02 bounded findings recorded;03/04 actual AE ownership/
call/thread contracts unresolved;05 diagnostic component done, retained host adapter
BLOCKED;06 owned native controls PASS/AE NOT RUN;07 checks/docs/retention/cleanup
complete. This is partial implementation of the seven-block packet, not completion
of its actual AE ownership/call dependency. Backend NOT READY; registration/apply/
render NOT RUN, original product/A/B/C1/C2/D/release retained. Next: substantiate
transitive ClassFactory/GetSharedFromThis/acquisition contract and actual retained
receiver before a live packet; host-wide admission/drain/full rollback still required.

## Factory code identity — implemented, actual receiver open

[Factory identity review](C1_FACTORY_IDENTITY_2026-10-03.md): real native code-identity
component implemented and verified against a fresh owned arm64 dylib. Exact code
addresses/hash/UUID/text/thread/bounds refusals PASS. A separate immutable identity-only
MEE profile has three original-file span hashes verified; no callable ABI/receiver/
reference lease or ResourcePassGate capability is provided. Shared parser protection
ceiling defect corrected and full regression passed. Nine complete file windows /
643 instructions /533 anchors distinguish factory tree from KnownPlugins metadata
holder and trace weak/shared construction and virtual-base pointer adjustment.
At exact clean research code e70d13c693977449e27cf50dcb3e5a388e08a87e: 61 collector +3
native focused, 440 full Python/no skips, 62 Node/22 stages PASS. Separate original
byte/11 serialized rebases/three profile spans/ZIP/341-source-file proof PASS.
Scanner raw exit1 retained; sole local-CLI false positive reviewed. Research CI
37137765177 and macOS CI 37137765153 completed/success at exact e70d13c.
FACTORY-01–07 bounded implementation/review/checks/docs/retention/cleanup complete;
08 real retained receiver, supported callable late ABI and continuous host admission/
drain/full effect rollback BLOCKED. Backend NOT READY; AE operation and
registration/apply/render NOT RUN. Original product/A/B/C1/C2/D/release retained.
Next: a supported retained receiver acquisition and real host transaction contract;
integer code identity cannot supply these or authorize a private invocation.

## Loader dispatch — research checks complete, native contract open

[Loader dispatch review](C1_LOADER_DISPATCH_2026-10-03.md): 23 complete fixed
windows /11754 instructions /792 anchors. LoadPluginList routes candidates to
AddPlugin; factory selection retains interfaces and creation is delegated virtually.
Actual receiver/supported late ABI unproven; HeavyInit success is not render drain,
cache cleanup/local unwind not full effect rollback. Startup exception-policy
mutation documented as original-file evidence only. No current AE operation.
At exact clean research code 2a2dabb68d442355e97e0d1053d84bccef60c825: 57 focused /
433 full Python tests, zero skips/errors/failures, 62 Node /22 stages PASS.
Clean collection and separate original-byte/archive/336-source-file review PASS;
raw scanner exit 1 retained, sole local-CLI false positive independently inspected.
Research CI 37136115466 and macOS CI 37136115496 both completed/success
at exact 2a2dabb. DISPATCH-01–06 bounded findings/limits documented;
07 collector/refusals PASS, 08 checks/review/CI complete, 09 docs/retention/cleanup
reconciled, 10 executable native packet/host trial BLOCKED. Registration/apply/render
NOT RUN; backend NOT READY. Original product and A/B/C1/C2/D/release retained.
Next: actual factory receiver/capability binding and supported continuous
admission/drain/rollback transaction, before any new host packet.


## Module admission — list membership and readiness separated

[Admission review](C1_MODULE_ADMISSION_2026-10-03.md): 12 pinned windows /
3446 instructions /232 anchors. Factory Create inserts before Init; CreateUnknown
checks SetupFilter before returning a module; cache/virtual paths remain conditional.
GetModules has no explicit body lock/readiness check; default AddModuleToList is
no-op and SetdownAsync constructs a ready future, not a proved host drain. Outer
LoadPlugins delegates to LoadPluginList; full transitive late ABI/owner/thread/
admission/drain/rollback UNKNOWN. Backend NOT READY. At exact clean research code
59f1e7ae1a8e279adfb7a9891ff5de6494d203cc: 54 focused /430 full Python, no skips,
62 Node/22 stages PASS; clean collection and independent original-byte/archive/
335-source-file review PASS. Sole raw scanner finding reviewed as a local-CLI false
positive; raw exit 1 retained. Research CI 37135099702 and macOS CI 37135099694
both completed/success at exact 59f1e7a. ADMIT-01–04 bounded file findings documented,
required native contracts BLOCKED; 05 research implementation/refusal checks done;
06 checks/review/both CI complete, 07 docs/cleanup reconciled,
08 executable host experiment BLOCKED,
registration/apply/render NOT RUN. No current AE operation; original product and
A/B/C1/C2/D/release obligations retained. Owned private receipts durably retained;
no shared/loaded cleanup. Next: complete LoadPluginList dispatch/ownership/error
transaction and relevant one-time/virtual delegates.

## Routine-to-effect handoff — internal route found, safe late contract open

[Combined handoff review](C1_ROUTINE_HANDOFF_2026-10-03.md): 17 complete pinned
file windows / 4707 instructions / 275 anchors. Startup registers a setter consumed
by MEE SetupFilter, routed through aelib to FLT provider/path setup and publication.
Cache can skip the callback; nonnegative status normalization is not readiness.
Provider AddEffect can precede failing lazy globals; disposal mutates canonical/
GPU/global/descriptor state without proved whole-effect rollback. A per-module
mutex does not establish continuous all-reader/render exclusion. Actual supported
late ABI/receiver/lifetime/thread/drain/transaction UNKNOWN; backend NOT READY.
At exact clean code e0b85908706290771ba50bd9efe3ff0d59be9772: 51 focused /
427 full Python tests, zero skips, 62 Node / 22 stages PASS; clean collection and
independent original-byte/archive/334-source-file verification PASS. One scanner
finding reviewed as a local-CLI false positive, raw exit 1 retained. Research CI
37133192290 and macOS CI 37133192291 both completed/success at exact e0b8590.
HAND-01–08 bounded file findings documented, required native contracts BLOCKED;
HAND-09 research tooling/checks/review/CI/docs complete, HAND-10 executable experiment BLOCKED, HAND-11/12
NOT RUN. Original product/A/B/C1/C2/D/release retained; no current AE operation.
Next: upstream module admission/initialization and its enforceable late-host contract.

## PiPL publication owner — routine roster and effect registry distinguished

[Publication-owner research](C1_PUBLICATION_OWNER_2026-10-03.md) extends the metadata
lifetime result with 12 complete PLUG/PluginSupport windows, 2403 instructions and
248 anchors. Registration overloads retain routine descriptors/providers in the
PLUG roster under its own mutex; ordinary effects are published separately through
FLT. Provider construction precedes roster locking in two variants. Unregister can
return success for a missing roster entry, or enter unprep/dispose/teardown before
erase; it is not a confirmed whole-effect rollback. Actual runtime provider/owner,
thread/admission/drain/completion/rollback remain unproven. Native backend NOT READY.
At clean research code f5150253c8f1ea013ec7edf3d03d587126a7cd10:
48 focused / 424 full Python tests, zero skips, 62 Node / 22 stages PASS;
clean-source collection and independent original-byte/archive/source review PASS.
Research CI 37132060603 and macOS CI 37132060602 both completed/success at that
exact source. One scanner finding reviewed as a local CLI false positive, raw exit
1 retained. OWNER-07 research checks/review/CI/docs complete. OWNER-01–05 file
findings documented; required native contracts remain BLOCKED. OWNER-06 executable
host experiment BLOCKED,
OWNER-08 NOT RUN. Original product/A/B/C1/C2/D/release retained; no current AE
operation or opaque-context replay, no merge/release. Next: establish the supported
late-entry transaction joining the retained owner to FLT publication.

## Host metadata bridge — lifetime boundary identified, runtime still blocked

[Bounded metadata review](C1_PLUGIN_METADATA_BRIDGE_2026-10-03.md) reconciles PICA
with the historical Dynamic/PiPL and resource/shell findings. In the reviewed
uncached GetPiPLs path, the host callback receives a stack-local metadata vector,
which is destroyed on normal and exceptional exit. Retaining/replaying this
context is NO-GO. Callback success and PiPL conversion do not by themselves prove
ordinary-registry publication; actual transitive targets/receiver/host-wide
admission/drain/completion/rollback remain unproven. Six file-only windows cover
744 instructions / 139 anchors at exact clean code source 9e35d1e. Local checks:
421 Python/no skips, 62 Node/22 stages PASS; actual SDK owned callback control PASS.
Independent file/archive/source-byte review PASS; research CI 37126661037 success,
macOS CI 37126661063 completed/success at exact 9e35d1e. BRIDGE-06 complete.
These are offline checks; no current AE invocation.
BRIDGE-01 research complete; usable mechanism in 02 and full contract in 03 remain
BLOCKED. Host experiment 04 and live 07/08 NOT RUN; no new live scope assumed.
Backend NOT READY; original product and A/B/C1/C2/D/release obligations retained.
Next: follow copied PiPL/path to the publication owner and establish its safe
transaction contract. Preserve previous consumed helpers/session/history.

## Public PICA inventory — all eight pass steps complete, registration open

User authorized the exact packet with “запускай”, then confirmed normal AE Quit
with “закрыл”. Closed-host guards passed; only the unique helper was installed
and one controlled AE 25.6x101 arm64 session launched. Code/helper source
**525000b6915423b7d387f10e846f972472570754**, build **inventory-a96d55e17240**,
PID **28761**, start **1791033664.137575**. One exact request **COMPLETE**,
independently verified. Plug-ins rev4 / Adapters rev3 available, both error 0.
Complete public global PICA list: **2** fully resolved records, both the AE.app
file with standard **Sweet Pea 2 Adapter v1**. Known Control Shell/Rust Probe
files **NOT_LISTED**, although both match names are registered in AE. No direct
file bridge demonstrated; possible host/aggregate/proxy meaning UNKNOWN.
Same blank clean idle project revision 1, **786** effect identities and **1410**
loaded images byte-identical, no additions. [Exact result, interpretation and
receipts](PICA_INVENTORY_REVIEW_2026-10-03.md). INV-01–06 preparation complete,
INV-07 scoped live PASS, INV-08 interpretation complete; one-shot authority consumed.

Preparation 418 Python/no skips, 62 Node/22 stages PASS and research CI 37124717978 /
macOS CI 37124718156 success remain exact 525000b receipts, not rerun for this
runtime doc closeout. Actual helper loading/diagnostic separately verified.
Backend NOT READY; registration/apply/render NOT RUN, A/B/C1/C2/D/release retained.
NO-GO for treating public PICA AddPlugin as a confirmed ordinary-effect registry
bridge. Next: identify a host-specific bridge and its ownership/admission/drain/
completion/failure/rollback contracts; no repeat of this inventory or guessed call.
No broad impossibility claim, shell-only product adoption, merge or release.
Cleanup retains installed consumed helper/session/evidence pending safe closed-host
cleanup; no forced quit, loaded-file removal, third-party/project/SDK changes.
Following sections preserve earlier checkpoints; their pending inventory statements
are superseded by this current closeout.

## PICA live diagnostic — all eight pass steps complete, registration open

User replied “продолжай” to the concrete one-shot request. AE was verified closed
before installing only the identified **pica-1840ac76ef3b** helper and launching
one controlled session. Actual code source **f21064a5ea0e9dc41828987d365d18f8687515e2**,
AE 25.6x101 arm64, PID **14298**, start **1791030995.377505**; final binary SHA-256
`e80e5875033d13e2d43922cc852092ddb2bc056733f5dd91215287852f13066b`.
One exact request **COMPLETE**, independently reverified. All four PICA providers
available: Plug-ins rev4/rev6, Access rev3, Adapters rev3, error 0 each.
Complete global adapter list: only **Sweet Pea 2 Adapter v1**, the SDK's standard
PICA adapter. No separately identified ordinary-effect adapter observed in this
list; no broad absence/impossibility claim. Project/registry/identity unchanged:
blank clean idle revision 1, **786** effects; **1409** images byte-identical.
[PICA result, acceptance and exact receipts](PICA_AVAILABILITY_REVIEW_2026-10-03.md).

PICA-01–06 preparation completed; PICA-07 scoped live observation PASS; PICA-08
interpretation complete. Old and this new one-shot authority consumed; no replay.
Preparation regression remains **399 Python/no skips, 62 Node, 22 stages PASS**;
research CI 37122917227 and macOS CI 37122917217 success at exact f21064a. These
are preparation receipts, not checks rerun for the doc-only runtime closeout.
Actual AE/helper loading is separately verified, not full release certification.

Next: bounded public PICA plug-in inventory correlation with known ordinary-effect
files; review exact revision-6 file-spec/CFURL lifetime first. No native packet or
renewed live scope for that different operation. FindPluginProperty may send a
message/modify properties, so it is excluded from assumed passive name lookup.
Backend NOT READY; registration/apply/render NOT RUN. NO-GO for AddPlugin/private
publication until ordinary-effect bridge/ownership/admission/drain/failure are
established. A/B/C1/C2/D/release obligations and original product contract retained.
No private call, ordinary scan, unload, restart, merge or release. Cleanup preserves
identified installed inert/consumed helper and session pending closed-host cleanup,
other plugins/SDK/historical evidence. No forced termination or removal while loaded.

## Current combined hypothesis pass — offline checks complete, runtime open

User requested all three hypotheses together and then their combinations.
Code/test source **65edce84340fd919e738be65100a8ea73d1c2c31**; rules remain
v8.0.0 at 132b7cd32873ba7328e3128ffbb33e1929b74d45. Acceptance mapping is
in [production plan](PRODUCTION_PLAN.md); findings and exact evidence in
[combined review](HYPOTHESES_REVIEW_2026-10-03.md).
PICA revision-4 AddPlugin and revision-6 AddXPlatPlugin contracts compile against
the actual SDK. The latter requires its own structure/file type; AE suite/provider
and ordinary-effect adapter/publication availability UNKNOWN. Five relevant
literals absent in nine exact pinned files: bounded lexical result only.
Single-effect native invocation remains BLOCKED on ownership, admission/drain
and completion/failure contracts. Historical dynamic-fixture registration delta
and scoped apply evidence are preserved separately from incomplete lifecycle,
render NOT RUN and PiPL/RSMB failures; no broad impossibility claim is justified.
New owned-process test executes actual shell logic with isolated log/home/temp
routing. **383 Python/no skips, 62 Node, 22 stages PASS**, including fifteen
labelled shell checks counted as one aggregate Python test. Archive/source/log
verification PASS; 25 ZIP members / 309 tracked files. Static audit completed,
raw exit 1 with sole known local argparse false positive retained.
Research CI [37121857027](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37121857027)
completed/success at exact 65edce8. macOS CI
[37121857015](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37121857015)
also completed/success at that exact source; CI is not live AE proof.

Combinations reviewed: PICA + ordinary-effect adapter/publication is a conditional
same-goal research candidate. A shell cannot remove initial-registration
prerequisites; adopting a preinstalled shell-only product requires a scope
decision. Next: identify exact AE suite provider and ordinary-effect adapter,
then prepare an identified potential-load availability probe before any
registration operation. No guessed opaque-handle conversion or executable combined
adapter. Current AE registration/apply/render NOT RUN, backend NOT READY;
A/B integration, D compatibility/hardening and release obligations remain open.
README baseline/diagnostic authority reconciled. Cleanup preserves historical,
installed and unknown inputs; only disposable owned test workspaces removed.
No AE operation, merge, release or installable handoff. Documentation-only
closeout is distinct from the tested code SHA above.

## Current five-block pass — offline PASS, live adapter NO-GO

Rules v8.0.0 adopted at the supplied 132b7cd commit. All five scoped offline
blocks are complete at code/test source **a293c90e615dd4a67c2d559422ac990756d79908**:
14 fixed FLT windows / 2413 instructions / 150 anchors; original bytes independently
corroborate 342 direct/44 indirect branches, eight state stores, five TSS-global
address paths and two imported boost get/set_tss_data identities. All twelve
clean-source file-mode archives independently verified.

Local regression **382 Python/no skips, 62 Node, 22 stages PASS**. Research CI
[37120969285](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120969285) and
macOS CI [37120969284](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120969284)
completed/success at exact a293c90. Bounded static review completed; raw exit 1
retains the sole reviewed local argparse false positive. [Exact evidence,
findings and decision](C1_REGISTRY_CONSUMERS_BATCH_2026-10-03.md).

We confirmed that project serialization scopes maintain thread-local data and
cannot be used as global exclusion; preference errors have a path after registry
publication, with no proven registration rollback. Individual registry locks,
settings snapshots and idle/loading counters do not establish the required
continuous all-reader/dispatch/MFR exclusion. **NO-GO for a live adapter using
these reviewed mechanisms**; this is not a proof that the product is impossible.

Backend NOT READY; registration/apply/render NOT RUN; historical unchanged scan
FAIL preserved. A/B integrated acceptance, D compatibility/hardening and release
remain open; no acceptance was removed or weakened. Next: identify a specific
prospective admission/drain provider and proof procedure before extending private
ABI research; actual ownership/completion/error contracts are still required.
No executable live packet or renewed host authority. Cleanup assessed; preserve
unique evidence, old/new rule checkouts and installed helpers; no deletion/move.
Documentation-only closeout must not be presented as the code SHA tested above.

## Latest C1 registry transaction batch — offline PASS

Code/test source **880b55fe7c0fb32b3c978349cf618b45e2f40952**. Six-step batch
reviews startup/resource caller sequencing, selected registry readers/writer,
render scopes and completion/partial-mutation paths, then adds a mandatory
continuously held publication lease to the unbound policy and durable journal.
Seventeen fixed windows / 3063 instructions / 484 anchors; independent original
bytes corroborate 578 direct/71 indirect branches, nine field accesses and three
global-counter address paths. Catalog omission reproduced and fixed.

Full local regression **379 Python/no skips, 62 Node, 22 stages PASS**; all eleven
file-mode archives independently PASS. Policy: 129 synthetic gate cases; journal:
38 real-file/process cases with synthetic host. Research CI [37120018578](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120018578) and macOS CI [37120018592](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120018592) both completed/success at exact 880b55f.
Bounded static review complete; raw scanner exit 1 and sole known local argparse
false positive retained. See [findings, protective change and exact evidence](C1_REGISTRY_TRANSACTION_BATCH_2026-10-03.md).

We now know that selected registry operations lock individually, returned owners
outlive those locks, zero render count does not prevent new work, and a completed
loading flag/normal notifier return need not prove every module succeeded.
These are bounded file findings and tested refusal behavior, not hot registration.
Backend NOT READY. No native adapter, AE operation or renewed live scope.
Next: remaining registry consumers/lifetime and transitive preference/canonical
failure paths; establish an enforceable all-reader/dispatch/MFR exclusion route
or record go/no-go before preparing an isolated adapter. Registration/apply/render
NOT RUN; historical scan FAIL preserved; A/B/D/release gates remain open.

## Latest C1 provider/isolation/completion batch — offline PASS

Code/test source **56be72b888652da450dc58c0d83c64187218af95**. One cycle closes
the bounded file ownership chain, reviews per-effect dispatch counters/guards and
post-setup, and binds three mandatory reviewed contracts into the unbound
resource transaction and durable journal. Old broad native approval alone no
longer permits the model operation. Sixteen complete bodies / 884 instructions /
293 anchors; six original table slots resolve owner/destructor and inherited
Load/GetEntryPoint correspondence. Actual AE receiver identity remains unknown.

Full local regression **376 Python/no skips, 62 Node, 22 stages PASS**; all ten
collector archives independently PASS, including new 105 direct / 24 indirect
raw branches, four rebases and two raw import resolutions. Research CI
37118807823 and macOS CI 37118807775 both completed/success at exact 56be72b.
Bounded static review complete; sole known local argparse scanner false positive
retained. See [combined findings, contract requirements and evidence](C1_PROVIDER_ISOLATION_BATCH_2026-10-03.md).

File evidence now distinguishes object ownership and local guards from host-wide
publication safety. Backend NOT READY; no executable live packet justified:
actual provider ownership, exclusive reader/dispatch/MFR window and complete
native publication/failure semantics remain unproven. No new AE operation;
historical diagnostic scope remains consumed and unchanged scan FAIL preserved.
Next offline block: resource-pass caller, effect-registry reader/writer
synchronization and completion/partial-mutation paths; then reassess an isolated
adapter. Registration/apply/render, A/B/D and release gates remain open.

## Latest C1 combined entry/lifetime batch — offline PASS

Code/test source **50e93973309fbff0b65e37b7c6cbb26e4b9422ad**. One cycle covers
library retention, descriptor/saved-entry/FCSpec dispatch correspondence, a failure
and recovery matrix, and a concrete registration → apply → render trial design.
Twenty-three complete bodies/thunks / 1351 instructions / 225 anchors; all nine
archives independently PASS, including 264 raw direct/22 indirect branches and
29 original fixup-chain rebases. Lookup can load code; private unload is not a
proven rollback. File table correspondence does not identify a live receiver.

Full local regression **372 Python/no skips, 62 Node, 22 stages PASS**.
Research CI 37117715670 and macOS CI 37117715623 both completed/success at
exact 50e9397. Bounded source/static review complete; sole known local argparse
scanner false positive retained. See [combined evidence and trial design](C1_ENTRY_LIFETIME_BATCH_2026-10-03.md).
ASLFoundation's new pin is offline only; native profile/helpers/ResourcePassGate
unchanged. No AE operation or executable live packet. Future trial is BLOCKED on
actual provider/receiver ownership, quiescence/publication isolation and a new
identified adapter/operation scope. Next file work: provider/interface construction
and virtual-table correspondence, then the remaining host-quiescence contract.
Backend NOT READY; registration/apply/render/release remain open.

## Latest C1 provider and canonical factory retention — offline PASS

Code/test source **49a85318fcfb884315b9d36d3cb4b74a094a0399**. Fourteen complete
PluginSupport/TDB bodies / 1365 instructions / 146 anchors; all eight archives
independently PASS, with 257 raw direct and 26 raw indirect branches checked.
Library shared references and canonical/factory tables have separate lifetimes;
Free is a no-op, canonical retrieval can mutate a table, and recursive unregister
is not a proven transactional rollback.

Full local regression **368 Python/no skips, 62 Node, 22 stages PASS**.
Research CI 37116821256 and macOS CI 37116821279 completed/success at exact
49a8531. Bounded source/static review complete; sole known local argparse scanner
false positive retained. See [provider/factory evidence](C1_PROVIDER_FACTORY_REVIEW_2026-10-03.md).
TDB's new pin is confined to a file-only manifest; native profile/helpers /
ResourcePassGate unchanged. No live AE operation or executable live packet.
Next: file-only ASLFoundation Module load/procedure/final lifetime and exact FLT
FCSpec GetRoutineDescH/SetRoutineDescH/GetEffectProc provider/virtual reference path.
Backend NOT READY; registration/apply/render/release remain open. This supersedes
the prepared checkpoint; historical late-registration FAIL remains unchanged.

## Latest C1 effect dispatch and parameter failure — offline PASS

Code/test source **8aec890b95e0eea0216582f43bee0109c31700f3**. Eight complete
FLT bodies / 1939 instructions / 86 anchors; all seven archives independently
PASS, with 377 raw direct branches and three raw indirect-call sites checked.
Canonical registration is called before PARAMS_SETUP; local diagnostic/handle
cleanup does not establish canonical rollback or provider lifetime.

Full local regression **364 Python/no skips, 62 Node, 22 stages PASS**.
Research CI 37060170220 and macOS CI 37060170144 completed/success at exact
8aec890. Bounded source/static review complete; sole known local argparse scanner
false positive retained. See [dispatch evidence](C1_EFFECT_DISPATCH_REVIEW_2026-10-02.md).
Native helpers/profiles/ResourcePassGate unchanged; no live AE operation.
Next: file-only PluginSupport PluginImpl preparation/retention and TDB canonical
factory retention/error paths, with new exact file pins before any body review.
Backend NOT READY; registration/apply/render/release remain open. This supersedes
the prepared checkpoint, without changing historical late-registration FAIL.

## Latest C1 readiness and descriptor ownership — offline PASS

Code/test source **986adb36e2b127c44608ec0a5e30ff165cb6f47d**. Nine complete
file windows / 1136 instructions / 79 anchors; all six mode archives and 146 raw
direct B/BL checks independently PASS. Preparation/global setup change retained
state; a zero preparation return alone does not prove a usable plugin entrypoint,
and safe rollback is unproven. Native helpers/profiles/ResourcePassGate unchanged.

Full clean local regression **361 Python/no skips, 62 Node, 22 stages PASS**.
Static review complete; the sole known local argparse scanner false positive is
retained. Research CI 37057799645 and full macOS CI 37057799722 both
completed/success at exact 986adb3. See [readiness evidence](C1_EFFECT_READINESS_REVIEW_2026-10-02.md).
Next: file-only inner host dispatch, parameter/canonical-stream failure paths
and PluginImpl provider lifetime. Preliminary downstream windows are preserved.
No new live packet/AE operation. Backend NOT READY; registration/apply/render/
release gates remain open. This supersedes the earlier prepared checkpoint.

## Latest C1 ordinary-effect publication review — offline PASS

Code/test source **db4799e2d964a68be761d71924bc5c693d13dea3**. File-only
publication collection PASS: 13 complete windows / 5002 instructions / 83 static
anchors; 48 direct raw BL checks and all five mode archives independently PASS.
The Missing Effect route creates a placeholder, not a loaded plugin. Real resource
setup reaches descriptor retention/post-setup/conditional publication/readiness;
safe isolation from existing GeneralPlugin state remains unproven.

Collector exception-comment false positive fixed; full clean local regression
**358 Python/no skips, 62 Node, 22 stages PASS**. Research CI 37055729740 and
full macOS CI 37055729761 both completed/success at exact source db4799e. Source/static review complete; sole known local
argparse scanner false positive retained (raw exit 1, not security certification).
Native profiles/helpers and ResourcePassGate unchanged; no new AE operation.
See [publication evidence and remaining contract](C1_EFFECT_PUBLICATION_REVIEW_2026-10-02.md).
Next file-only review: FCSpec::ReadyFilter / DoLazyGlobalSetup and PiPL/path
routine descriptor construction. Native backend NOT READY; registration/apply/
render/release gates remain open. Earlier prepared status is superseded.

## Latest C1 retained-name diagnostic — live PASS

The user explicitly approved the exact `identity-d5480a2a4090` install/one-launch/
read-only scope. Fresh AE-absence preflight, unique installation, loaded identity,
blank project and one request PASS; that authority is now consumed. Seven raw
names identify driver, Photoshop import/export and keyframe-assistant state.
Bounded current-file callback correspondence and seven static signature checks
PASS; full loaded-provider identity/lifetime/repeat safety remains unproven.

Registry **786** and project revision **1** stayed unchanged in this session.
Images **1407 → 1408 → 1408**: one permitted system framework addition, no
removed/replaced existing image. **8 copies / 2578 bytes**. Private report SHA
`c0cb5db1e2682e2b7d31e98c916c76f4a447889a4d3689e759790d37c11ce1a8`;
independent archive/hash/semantic checks PASS. No registration/private call/retry/
teardown/project edit/AE termination. At operation closeout PID 28774 and the
consumed helper were preserved; do not infer current process state from this log.

See [exact live result and evidence limits](C1_RETAINED_NAMES_LIVE_PASS_2026-10-02.md).
ResourcePassGate unchanged; current baseline remains ineligible. Next authorized
work is file-only ordinary-effect publication/isolation research without replaying
existing general-plugin initialization. C1 registration/C2 apply-render and release
remain blocked. Earlier NOT RUN/permission statements below are checkpoint history.

## Historical C1 retained-name native adapter and supervisor — preparation PASS

Code/test source **0204ab83212d68b19d85b78d0c7239511f301b7b** connects the
separate helper to actual loaded self/MEE measurement, bounded capture, five-file
journal and external one-shot request/independent verification. Safe public SDK
project snapshot precedes initial binding; scope/images are rebound around capture.
The controller derives expected root from fixed MEE layout plus loaded-image
header/base/slide, and checks a separate 15-second operation budget started before
its claim/publication. On failure/unknown outcome, evidence/process/helper stay
preserved; no automatic retry, private call, ordinary-effect registration or provider retention.

Full clean local regression PASS: **353 Python/no skips, 62 Node, 22 stages**.
Focused candidate/supervisor: 16 Python tests; native binding/capture fixture has
41 nested cases. Independent ZIP/member/inventory/source verification PASS.
Local report SHA-256
`dab580b0db0a15bbce5f2a1c6c264f9cdbc06bdbec41a19d83fbd9da9153c645`.
Bounded source/static review completed: 332 supported files/no omissions, all
selected checks complete; raw exit 1 retains only the rechecked known local
argparse false positive, no whole-security certification. Static report SHA-256
`ab6ae2988e749c62a0add0251648d4c53c126e9d3d4a41b07564db2369ef1ad4`.

Exact new candidate **identity-d5480a2a4090**: real SDK 25.6 build, local signing/
strict verification, two exports, compiled identity and three inert entry cases
PASS (SDK suites=0/root reads=0). Actual loaded self binding in an owned child
PASS; wrong signed-file hash refused. Four bundle payloads, 74 SDK inputs and
fixed provider files independently verified. Final binary SHA-256
`5e87b628434775d702da2c04475d8121d7ad0ecdddb0b28d23582fcb7510c530`;
private manifest SHA-256
`b0ed7a0f1e51d3949a279b94f02faa6b508cb1f127fa5af448eea24836b85968`.

Exact-source [research CI 37052270787](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37052270787)
and [full macOS CI 37052270804](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37052270804)
both completed/success at 0204ab83212d68b19d85b78d0c7239511f301b7b.
At the preparation checkpoint this candidate was not installed/launched/requested.
The subsequently authorized [live diagnostic](C1_RETAINED_NAMES_LIVE_PASS_2026-10-02.md)
now identifies the seven names; its one-shot scope is consumed. The verifier
retains host_execution_verified=false and does not prove allocation lifetime.

See [native candidate review](C1_RETAINED_NATIVE_CANDIDATE_REVIEW_2026-10-02.md),
[supervisor review](C1_RETAINED_SUPERVISOR_REVIEW_2026-10-02.md), and
[exact diagnostic scope and execution](C1_RETAINED_LIVE_SCOPE_2026-10-02.md).
Next: file-only ordinary-effect publication/isolation research. Registration/
apply/render and release remain blocked; no further live action is authorized
by this consumed diagnostic scope.

## Exact starting point

- Latest offline collector/policy/code/test source: **880b55fe7c0fb32b3c978349cf618b45e2f40952**.
- Prior publication source: **db4799e2d964a68be761d71924bc5c693d13dea3**.
- Diagnostic scope consumed; next work is remaining registry consumers/lifetime, transitive publication failures and an enforceable exclusion route, as above.

- Latest retained native adapter/supervisor source: **0204ab83212d68b19d85b78d0c7239511f301b7b**.
- Name candidate: **identity-d5480a2a4090**, installed/one-shot diagnostic PASS; authority consumed. Preserve the helper/session; next work is file-only.
- Repository: `ios3kov/AE-Hot-Loader`.
- Branch: `research/ordinary-plugin-discovery`; never change `main`.
- Prior retained host journal/verifier/code/test head: **dfa78e04d8a1e3f7cae64262a9f13a147aa4a5a3**.
- Prior retained identity transaction/code/test head: **836c29d3ef18b93a563e1b271198faf1a4eb473f**.
- Prior retained identity journal/verifier/code/test head: **59becab0056fae08b450cbb4471466b427427744**.
- Prior retained identity capture/code/test head: **eb559edac5d9bf5d3861d5673d9df47e9de1f5e8**.
- Prior retained-record decoder/code/test head: **15c528f6d7dabad83e7203970fc8a09bb2b7e710**.
- Prior MEE ownership collector/code/test head: **095a219253bf86bea82fa06fc00ac6c87e6f0b05**.
- Prior PIN collector/code/test head: **c01fb89d7b1842a145bb7c66681a045fa6b12a82**.
- Reviewed external supervisor code/test head:
  **`f4f84aa5a41fd86cc76ee2d702fe61e9b61d16e2`** (external supervisors).
- Historical count-observer native candidate source:
  **`7c983c5b5adfde0300f2370e5772ed757ab6b613`**; native bytes unchanged.
- Current canonical AE Development Rules source:
  **8.0.0 / `132b7cd32873ba7328e3128ffbb33e1929b74d45`**; read pinned AI_ENTRYPOINT first.
- Historical Stage C no-scan core head:
  **`c1e20e4ab4d4a4f6654f67df7dbb224f0790b5be`**.
- Historical live-launcher code/test head:
  **`3852192406da5af539b9100114393584642e9197`**.
- Status documentation before this migration:
  `c8c56fa`.
- Historical shared DEVELOPMENT_RULES blob:
  `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
- Stage: **C of A–D**. Ordinary-effect late registration is still NOT fixed.

AE Hot Loader is a **tool/panel**. The research-only AEGP is an internal helper
used because code must execute inside After Effects; it is not the ordinary
effect being loaded.

## Preserved live results

| Gate | Result |
|---|---|
| Scoped embedded late registration | **FAIL**: source `45de0c9`, Build ID `scoped-0b8c8f122e80`; 785 unchanged effect identities |
| RSMB startup-registered apply/render | **PASS**, separate startup baseline |
| RSMB late registration | **FAIL**, separate historical result |
| First live no-scan folder lifecycle | **FAIL** at strict postflight image equality; preserved separately |
| Second live no-scan folder lifecycle | **PASS**: source `182d058`, build `noscan-8f9cb9fea71c` |
| Ordinary-effect late registration | **NOT RUN again**; historical FAIL unchanged |

Do not merge these results or relabel startup success as late-registration
success.

## What is now connected

The separate inert-by-default no-scan AEGP and external one-shot supervisor are
connected in source.

The first live operation contains **no plug-in scan and no registration**. It is
limited to:

1. exact fresh AE/process/project/module baseline;
2. one fresh owned/private ASCII directory;
3. create one FILE directory specification;
4. exact path roundtrip;
5. release it exactly once;
6. prove unchanged PID/start/project/registry/image set;
7. preserve one report ZIP.

The AEGP is inert unless its exact build/run/token/paths match. The supervisor
publishes at most one request and never automatically retries an uncertain
native outcome.

## Latest hardening

The process identity is now genuinely cross-bound between the external
supervisor and the AEGP:

- supervisor uses macOS `proc_pidinfo(PROC_PIDTBSDINFO)`;
- AEGP uses the same native `pbi_start_tvsec.pbi_start_tvusec` tuple;
- mismatch is refused before request publication;
- the native journal must retain that same start identity.

The final report ZIP is now self-checked against its archived hash manifest and
the supervisor prints the final ZIP SHA-256.

Exact-head CI for `c1e20e4`:

- research CI **`36854509313`** — PASS, Linux + macOS;
- full macOS CI **`36854509275`** — PASS.

The macOS workflow now watches `experiments/**`, so future Stage C experiment
changes trigger the full macOS regression.

These are offline/build results, not live Adobe evidence.

## Static-audit candidate closeout

The five previously recorded scanner candidates were revisited:

- unpinned checkout — fixed;
- floating Rust toolchain — fixed;
- unpinned upload-artifact — fixed;
- checkout credential persistence — fixed;
- `artifact_manifest.py` rate-limit candidate — retained as the previously
  confirmed local-argparse false positive.

All current workflow `uses:` entries are SHA-pinned and all checkout steps use
`persist-credentials: false`.

Known candidates are resolved/classified. A **new full static-security audit is
still NOT RUN**. See `STATIC_AUDIT_CLOSEOUT_2026-10-01.md`.

## Current documentation

- `README.md` now describes the product correctly as a tool with internal AEGP
  helpers.
- `PRODUCTION_PLAN.md` now reflects the actual Stage C sequence.
- `DEVELOPMENT_STATUS.md` is the source of current verified state.
- Historical dated documents remain evidence for their own commits and must not
  be rewritten as current results.


## One-shot Mac launcher

`RUN_LIVE_NO_SCAN_GATE.command` is now the only intended entrypoint for the
first live gate. Exact-head research CI `36855482114` and full macOS CI
`36855482175` are PASS for launcher head `3852192`.

The launcher refuses an already-running AE session, preserves dirty/local Git
work, installs only its unique helper, launches AE once with the one-shot token
and publishes exactly one authorized no-scan request. It does not invoke the old
scan path.

The user explicitly authorized this one gate in the current chat: helper
installation / one AE launch if required, private FILE call and provider-reference
retention. That approval is scoped only to the folder create → path roundtrip →
single release gate and does not extend to later plug-in registration.

## First live no-scan attempt

The first authorized live request is now consumed.

Preserved result:

- source `161b180714a734baf71f8c8cb58440e73f8dcd23`;
- build `noscan-f0aa4a3bd54a`;
- report SHA-256
  `727a65d7ba64be8371c40025a4fc2196785216cc77299941d0978a71eb0cff5a`;
- final status **FAIL**, stage `postflight`;
- effect registry stayed 785;
- PID/start/project revision stayed unchanged;
- only new runtime image was Apple
  `SafariPlatformSupport.framework` under `/System/Library/`.

The old format lacked durable native lifecycle counters before postflight, so
the FILE roundtrip itself is not promoted to PASS.

Remediation code head:
**`dadd884b4758a351fbc725969ed49d2f9a912781`**.

Exact-head CI:

- research `36857286317` — PASS;
- full macOS `36857286194` — PASS.

The new gate persists `native.txt` before postflight and tolerates only new
`/System/Library/` images while requiring all pre-existing images to remain
exact. New Adobe/user/plug-in images still fail.

A second live no-scan request requires fresh authorization. General
"continue" instructions do not authorize that retry.


## Second live no-scan attempt — PASS

The second authorized no-scan request closed Stage C0.

- source: `182d058254203236414602acdd9901b8749d89cc`;
- build: `noscan-8f9cb9fea71c`;
- run: `directory-probe-d097765fede949f5b9958b2897687df2`;
- report SHA-256:
  `f767e891359a3e73dc41eefe4124fe63dc0cf4dde123c2d7efa7444cd35bc62a`;
- final status: **PASS**;
- native counts: strings 2/2, spec 1/1, retained refs 3;
- registry: 785 before/after;
- runtime images: 1402 before/after;
- project revision: 1 before/after;
- plug-in scan requested: false.

The uploaded ZIP and all inner hashes were independently verified.

**Stage C0 = PASS.** Do not repeat the no-scan run.

Next work is Stage C1 offline review/preparation of the single-root
resource-registration experiment. Any live resource-registration/private PLUG
operation needs fresh authorization; the second no-scan approval is consumed.


## Previous Stage C1 ABI checkpoint

The collector's incompatible LLDB `--force` option is fixed and regression-tested
on an owned arm64 bundle. Complete bounded ABI windows and a supplemental
cleanup window were collected from the hash-pinned actual files without Adobe
execution. Clean-head local regression passed: 264 Python, 62 Node, 22 stages.
Exact-head research CI `36920890724` and full macOS CI `36920890645` are PASS
for `5b88779`. These are offline/build results, not live C1 execution.

PLUG_Search invokes the selected sack's installed cleanup list even for one
root and even with null progress callback. Review the actual cleanup registrations
and retained-state effects before creating a native resource-call backend.
An address/signature match does not prove late-call safety.

## Previous Stage C1 cleanup checkpoint

Code bf8a2cc adds a separate `--review cleanup` collection: eight complete
windows / 1390 decoded instructions, matching PLUG/FLT/MEE before/after hashes,
no Adobe execution. Default search mode also passed again (472 instructions).
Local clean-source regression: PASS, 266 Python tests without skips, 62 Node
tests, 22 stages. Exact-code research CI 36922542782 and full macOS CI
36922542905 are PASS; the latter includes build/sign/package/synthetic smoke,
not live AE execution.

FLT registers no cleanup in its normal birth call. MEE registers
PluginCleanupFunc; its body traverses shared GeneralPlugin state and can prepare
procedures, invoke saved entrypoints and mutate records beyond the search root.
Installed cleanup loops stop on nonzero returns. The running sack/vector and
repeated preparation behavior remain unobserved. No native C1 candidate is ready.

Continue with PLUG_PrepRoutine's repeated-preparation/error contract and the
general-plugin lifecycle, then establish a read-only baseline design for actual
callback/state eligibility. Do not replay SetupGeneralPluginScan, invoke
SetdownGeneralPlugins, replace cleanup or forge a sack. C0 remains the recorded
live PASS; C1 registration/apply/render are NOT RUN.

## Previous Stage C1 lifecycle/cleanup-state checkpoint

Code 3e67046 adds bounded lifecycle code/data collection (891 instructions,
96-byte vtable, confirmed fixup format) and a conservative cleanup-state gate.
Current code/test head 52f4f80 additionally fixes a reproduced macOS runner
signal/exit race. Clean current-source local tests: PASS, 270 Python without
skips, 62 Node, 22 stages. Exact research CI 36925153427 is PASS; full macOS CI
36925153460 is PASS (build/sign/package and synthetic smoke, no AE). The old 3e67046 macOS research run remains FAIL.

KeepLoaded + already-prepared can return zero and let MEE call the saved
operation-3 entrypoint again. Repeat safety remains UNKNOWN. The policy requires
complete observed cleanup state with an exactly approved inventory digest and
zero retained general-plugin records, checked again before and after the call;
the journal retains those fields. Synthetic 82 gate / 32 journal cases are
included within the Python count. There is no real state reader or C1 backend.

LIST.dylib's two bounded getter bodies were inspected without calling them.
Its new static hash is not a live-profile/resident identity. Continue only
independent read-only observer preparation, with provider and memory-consistency
bounds. Actual callback/vector state and third-party repeat behavior block
native integration. Do not attach/call without a concrete reviewed scoped
authorization, or replay setup/setdown/unprep to change the baseline.
C0 remains its recorded PASS; C1 registration/apply/render remain NOT RUN.

## Previous Stage C1 bounded snapshot checkpoint

Code 6a758a8 adds an isolated CleanupSnapshot sampler, 44 nested cases and an
owned macOS self-read. It compares two complete chains inside supplied bounds,
refuses invalid/changed/truncated state without retries, preserves callback
order/duplicates and retained count. It never calls callbacks/getters or supplies
complete/observed/digest fields to the resource policy. Provider identity,
allocation provenance, quiescence and actual state remain unknown.

Clean-source local regression: PASS, 271 Python (no skips), 62 Node, 22 stages.
Owned address/undefined-behavior sanitizer run: PASS. Exact research CI
36926349585 is PASS; full macOS CI 36926349591 is PASS. All are offline/build
evidence. C0 remains recorded PASS; C1 registration/apply/render remain NOT RUN.
Continue independent file-only provider/root/range preparation. A matching
snapshot cannot authorize native integration or prove a complete eligible state.

## Previous Stage C1 root provenance checkpoint

Code efe05f2 independently verifies static Mach-O symbol/UUID/zero-fill roots:
PLUG global slot 0x18490 points to a handle; only that separately validated handle
is CleanupSnapshot's sack_slot. MEE vector pair is 0x10fd70. Neither serialized
zero-fill bytes nor static VM values are runtime observations. Complete allocation/
lifetime/quiescence and all callback effects remain unknown. No scope/backend
conversion or host read/call is bound.

Clean local regression: PASS, 284 Python (no skips), 62 Node, 22 stages. Exact
research CI 36927550112 PASS; macOS product CI 36927550048 PASS. Collection
and regression ZIPs independently rehashed; see current report. C1 registration/
apply/render NOT RUN; C0 remains recorded PASS. Continue owned-fixture resident
module/header/text identity and data-root containment checks, then prepare a
concrete diagnostic candidate. The user's newest instruction requests autonomous
continuation through all development stages; report each stage and continue,
preserving the established live/private-call/release boundaries.

## Current Stage C1 resident root checkpoint

Code 0c4cd4c prepares exact resident header/text/path/hash binding and zero-fill
root extent checks. Owned-library tests prove the actual address/data read and
absence/hash/UUID/section/range/thread refusals. Binder never loads a provider or
calls an anchor. This is point-in-time address identity, not lifetime/completeness.

Clean local regression PASS: 287 Python (no skips), 62 Node, 22 stages. Exact
research CI 36928329962 and macOS product CI 36928330044 PASS. No AE roots/
callbacks/vector read. C1 registration/apply/render NOT RUN, C0 recorded PASS.
Continue current-process mapped-range reads with verified Mach API and owned
allocation/guard-page tests, then prepare a concrete diagnostic observer. Do not
promote mapping metadata or matching captures to allocation/complete eligibility.
Continue autonomously as explicitly requested; preserve live authority boundaries.

## Current Stage C1 mapped reader checkpoint

Code 6c666ca: exact self-process copies with mapping/protection/range checks
before/after, fixed budgets and refusal after failure. 29 nested synthetic cases,
owned-page/guard/boundary/thread checks and ASan/UBSan PASS. Full clean local
288 Python (no skips), 62 Node, 22 stages; research CI 36929256787 and full macOS
CI 36929256802 PASS. ZIP/inventory reverified in current report.
Next bounded diagnostic observer composition on owned chains, then an exact
inert candidate with external supervision before scoped live authorization.
No AE roots read, provider retained or native resource pass invoked. Mapping
identity/byte equality is not complete cleanup, allocator ownership or eligibility.
Continue autonomously with stage statuses; C1 registration/apply/render NOT RUN.

## Current Stage C1 observer checkpoint

Code 1a4201c composes a consumed-on-attempt diagnostic bootstrap/capture with
exact resident identities and clipped mapped reads. Bootstrap/capture/global/
record mapping changes refuse; nonzero records remain diagnostics, never gate
eligibility. Synthetic 27 cases and actual owned two-provider chain + sanitizers
PASS. Full clean local 290 Python/no skips, 62 Node, 22 stages and both exact
CI 36929802910/36929802970 PASS. Private ZIP manifest/inventory verified.
Next separate inert diagnostic AEGP, one-shot journal/supervisor and exact SDK
build/sign/hash/inert checks before scoped live operation. No real AE root read,
callback invocation, retained provider or native registration backend. Preserve
NOT OBSERVED/NOT RUN for current live registration/apply/render; C0 remains PASS.
Continue independent work without milestone stops as explicitly requested.

## Current accepted rules — 6.0.0 migration

On 2026-10-02 the user explicitly accepted the proposed rules migration.
Current baseline: 6.0.0 / published v6.0.0, peeled commit
bb8b769404ddd5b97462812a4e6b430e8bfefe13. Tag/version/source, applicability map
and routing contexts verified; full available standard self-test PASS, 132 files,
43 executed test cases, two Windows-only skipped; PowerShell NOT RUN locally.
AGENTS/plan/status/README now identify the pinned source and v6 MAC-001 integrity/
install/host-load policy, without paid-account/certificate/service prerequisites.
Validation phases and applicable IPC/diagnostics/testing overlays are explicit.
No vendored legacy wrapper callers; no runtime/tooling byte change required.
See RULES_ADOPTION_6_0_0_2026-10-02.md; final documentation consistency, pinned
source and 25 local-link checks PASS. Documentation/policy migration complete.

Older b27f454 records remain historical. No new artifact, AE action, permission,
registration evidence, main change or product release is produced by adoption.
Next C1 step retains the concrete diagnostic authority and runtime-safety gates.
Preserve the user's existing final-publication authorization when release gates
eventually pass; the baseline record itself grants no live permission.

## Stage C1 supervisor deadline checkpoint

Code/test source f4f84aa5a41fd86cc76ee2d702fe61e9b61d16e2, accepted rules b27f454.
Four synthetic reproductions proved the same two expiry bugs in the diagnostic
and no-scan supervisors. Both now check the absolute monotonic deadline just
before publication and before PASS acceptance. Expiry preserves the consumed
attempt/journal/report, without retry or host stop. Historical C0 is not rerun.
27 focused supervisor tests and clean full local 302 Python/no skips, 62 Node,
22 stages PASS. ZIP dd7e0777ea95999857bce874050fb9cc02725fb7fe80dbd617fc20d265e264ca
and complete archived inventory/payloads verified; exact-source research CI
37024297435 and full macOS CI 37024297373 both completed/success (PASS) at
the exact full source SHA above. Bounded scanner completed
(266 supported/no omissions), sole known local argparse false-positive/raw exit 1.
See C1_SUPERVISOR_DEADLINE_REVIEW_2026-10-02.md for identities and limitations.

No native source or candidate-byte change. Earlier native artifact source 7c983c5
does not identify the updated external supervisor; pin both identities before a
future authorized combined live run. No installation, launch, request or AE root
read occurred. Concrete diagnostic scope remains pending; the previous automatic
review rejection is not bypassed. Dependent registration/backend/apply/render
remain NOT READY/NOT RUN; exact complete-state/lifetime/repeat questions remain
open. Preserve publication authorization after release gates pass. This offline
block is closed. Next is the separately approved one-shot diagnostic with fresh
safe runtime and exact independent supervisor/native-candidate identities.

## Prepared Stage C1 diagnostic candidate checkpoint

Latest direction 2026-10-02: user explicitly requests release publication
("релиз делай"). Preserve this authorization for the finished verified release;
do not repeat the publication-permission question. Mandatory project release
gates are still open; no release/tag/merge/main change. The concrete diagnostic
install/one AE launch/sensitive-read approval remains pending and is not inferred
from publication scope to bypass the earlier automatic-review rejection.

Continuation 2026-10-02: clean head 5a74fd8, unchanged candidate/code source
7c983c5. Offline code-profile scan v2.0.0 completed at
2026-10-02T08:54:03.224551+00:00: 265 supported files/no omissions, four workflows;
raw exit 1/review_required, sole known local argparse false-positive at
tools/artifact_manifest.py:71 re-reviewed. Private report SHA-256
b16f7d24decb13af96a6f20e2804766f5abeab91e9be6770ab78cb7f5b802aa8.
This is bounded source scanning, not full security/AE/release evidence. No new
behavior, candidate or live operation. Explicit exact diagnostic approval was
requested again with the concrete install/one launch/read-only scope; pending.
The latest generic continuation is not used to bypass the prior automatic-review
rejection. Next dependent step remains that one diagnostic after actual approval
and fresh runtime verification. Do not repeat C0 or an unchanged registration scan.

Code 7c983c5: separate inert AEGP, one-shot durable journal and independent
supervisor. Clean local 298 Python/no skips, 62 Node, 22 stages and both exact
CI 36931094055/36931094195 PASS. Real SDK build/sign/hash/inert candidate
observe-d548b007e316 PASS; binary SHA cfbfa87038d2640a558ca0e30ca5c5d8b171aef8d8be4934f5c25f281950be56,
private manifest SHA 9f305a648b43a6569ccb70165169c2ed021d7977ddfbd9b84f3725d0bbdff100.
Inventory/payloads rehashed. Token stays private. See exact candidate report.

Live install/one test launch/sensitive read was rejected BEFORE execution by
automatic approval review: no explicit authority for those concrete actions.
No install/launch/request/read/private call/retention occurred; no workaround.
Next obtain explicit approval for only this unique helper and one read-only
capture on a fresh blank clean idle test host; preserve existing sessions and
all state on uncertainty. Fresh authorization must come from the user, not this
checkpoint. Generic autonomous-development request was not accepted by review.
Independent work is complete for this diagnostic preparation; dependent native
registration remains blocked by critical complete-state/lifetime/repeat unknowns.
No diagnostic → ResourcePassGate eligibility conversion; C1 registration/apply/
render NOT RUN, C0 recorded PASS. Do not repeat consumed C0 or old registration scan.

## Latest C1 diagnostic authorization and environment refusal

The user explicitly replied «разрешаю» to the exact observe-d548b007e316
install / one launch only without an existing AE session / one read-only capture
scope. This supersedes the earlier missing-authority statements for that scope.
Tool review permitted execution. The orchestrator passed exact clean source,
candidate/signature/provider and unused evidence checks, then refused an
existing AE session (PID 84352) before any live side effect. No installation,
launch, request, sensitive read or retry; destination absent, control/journal
empty, native request unconsumed. Existing project/session preserved, not inspected.

Current result **BLOCKED on safe environment**. Wait for the user to save and
close AE normally and explicitly resume; do not terminate AE or retry
on a timer. Recheck the exact unused candidate and safe baseline on resumption.
Diagnostic permission is already granted; do not ask for it again. Private calls,
provider retention and registration are outside this permission. See
[full scoped evidence](C1_DIAGNOSTIC_PREFLIGHT_BLOCKED_2026-10-02.md).
Registration/apply/render and release gates remain open; C0 is not repeated.

## Latest C1 live diagnostic — PASS, resource baseline ineligible

User closed AE and confirmed full exit. Exact candidate observe-d548b007e316
(native source 7c983c5) installed/launched once under explicit authority, using
reviewed supervisor f4f84aa, clean execution HEAD b3a8536. One read-only request
PASS; authority consumed. ZIP SHA
54976e137d928861a5cffd8288e4dccc10a3b347f95b766dab89f297554b16f4;
independent archive/native-evidence verification PASS. Two callbacks, seven
retained general-plugin records, unchanged blank/clean/idle project, PID/start,
785 effects and resident images. No private call/retention/retry/shutdown.
AE/consumed helper preserved. Earlier environment blocker is superseded.

Current ResourcePassGate cannot accept this baseline (requires zero records plus
complete reviewed cleanup). File-only callback attribution: MEE PluginCleanupFunc;
PINp_CleanupFunc tail-branches into PINp_SortModules (host global sorting).
Runtime PIN UUID/content and full lifetime/quiescence remain unresolved.
Next bounded file-only PIN review and retained-state contract; no gate weakening,
setdown/startup replay, callback replacement or additional live capture under
consumed authority. See [full evidence](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md).
Registration/apply/render/release still open; C0 unchanged PASS.

## C1 PIN file collector — exact local PASS

Reproducible exact-file collector/source c01fb89 completed PASS: 58 instructions,
11 structural anchors. Full clean local regression PASS: 307 Python/no skips,
62 Node, 22 stages. Report inventories/hashes independently verified; bounded
static scan retains sole known local-argparse false-positive. Research CI
37036763724 and full macOS 37036763790 both exact-source PASS. No native profile/helper change
or further live operation. Seven-record blocker unchanged. Next retained-state/
lifetime and PIN comparator/synchronization review. See
[bounded PIN review](C1_PIN_CLEANUP_REVIEW_2026-10-02.md).

## C1 retained host journal — exact-source PASS

All three host observations and both copied-byte captures are now saved in a
private one-shot journal and independently checked. Expected run/candidate/host/
provider/root/paths are bound; changed project/registry/images, malformed or
partial files and an independent expired/backwards deadline refuse. Focused
retained family: 27 Python PASS, including 13 new verifier tests and 19 nested
C++ disk-producer cases. No AE operation or native helper/profile/gate change.
Code/test source dfa78e04d8a1e3f7cae64262a9f13a147aa4a5a3. Full clean local
regression PASS: 337 Python/no skips, 62 Node, 22 stages; independent report/hash/
source verification PASS. Bounded static review retains only known local-argparse
false-positive. Exact-source [research CI 37049587798](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37049587798)
and [full macOS CI 37049587807](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37049587807)
both completed/success at dfa78e04d8a1e3f7cae64262a9f13a147aa4a5a3. Measured native binding and
external request supervision remain unconnected; actual seven names NOT RUN.
See [host journal/verification review](C1_RETAINED_HOST_JOURNAL_REVIEW_2026-10-02.md).

## C1 retained identity transaction — exact-source PASS

The transaction core now refuses wrong-run/process/provider/root/project data,
consumes invalid and concurrent attempts without retry, and enforces a monotonic
15-second deadline around the diagnostic boundaries. Focused retained family:
14 Python tests PASS, including 101 nested transaction cases. Actual capture core
is exercised on owned bytes; no Adobe call, install, launch or sensitive host read.
Native/disk adapter and independent host supervisor are still unconnected; this
is not a live-ready candidate. Code/test source 836c29d3ef18b93a563e1b271198faf1a4eb473f:
full clean local regression PASS (324 Python/no skips, 62 Node, 22 stages), report
hash/inventory/source recheck PASS. Bounded static review retains only the known
local-argparse false-positive. Exact-source [research CI 37047951971](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37047951971)
and [full macOS CI 37047951931](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37047951931)
both completed/success at 836c29d3ef18b93a563e1b271198faf1a4eb473f.
See [transaction acceptance and review](C1_RETAINED_TRANSACTION_REVIEW_2026-10-02.md).

## C1 retained identity journal — exact-source PASS

Code/test source **59becab0056fae08b450cbb4471466b427427744**.
A bounded journal now saves completed raw copy frames from both captures. A
separate Python verifier reconstructs names/read order and refuses incomplete,
inconsistent or wrong-run evidence. Focused journal suite PASS: 11 Python tests,
17 nested C++ journal cases. Native helper/profile, copied-byte/read budgets and
ResourcePassGate unchanged; actual AE names still NOT RUN. Full clean local regression PASS:
323 Python/no skips, 62 Node, 22 stages; archive/hash/source verification PASS.
Bounded static review retains only the known local-argparse false-positive.
Exact-source [research CI 37046241769](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37046241769)
and [full macOS CI 37046241807](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37046241807)
both PASS. Next separate host transaction/
supervisor and inert candidate, with actual binding/pre/postflight and authority.
See [journal/verifier review](C1_RETAINED_JOURNAL_REVIEW_2026-10-02.md).

## C1 retained identity capture — exact-source PASS

Code/test source **eb559edac5d9bf5d3861d5673d9df47e9de1f5e8**.
Separate one-shot capture core is implemented under rules 6.2.0. Strict C++17
focused regression PASS: 46 nested synthetic cases plus actual macOS arm64 owned
heap/main-thread-refusal smoke. Two bounded matching captures, atomic consumed
claim, no retarget/retry; maximum 22 copies / 6,976 bytes. No Adobe calls or
callback invocations. Full clean local regression PASS: 312 Python/no skips, 62 Node, 22 stages;
independent report/hash/source verification PASS. Bounded static review retains
only the known local-argparse false-positive. Exact-source research CI
37043790769 and full macOS CI 37043790324 both PASS.
No native helper/profile or ResourcePassGate change; actual seven live names
remain unknown. Next snapshot journal/independent verifier/supervisor and a
separately identified inert candidate before its operation authority request.
See [capture review](C1_RETAINED_CAPTURE_REVIEW_2026-10-02.md).

## C1 retained-record decoder — exact-source PASS

Code/test source **15c528f6d7dabad83e7203970fc8a09bb2b7e710**. Portable owned-buffer
decoder preserves ordered raw fields/names and rejects bounded inventory or
alias/overlap inconsistencies. Strict C++17 focused suite PASS: 38 nested cases,
zero host/record calls. Full clean local regression PASS: 311 Python/no skips,
62 Node, 22 stages; independent archive/hash/source verification PASS. Bounded
static review completed with the sole known local-argparse false-positive.
Exact-source research CI 37042066391 and full macOS CI 37042066540 both PASS.
Actual seven live names remain unknown; no host read, native helper/profile or
ResourcePassGate change. Next prepare the separately identified one-shot
record/name capture adapter, journal/supervisor and verification before its
operation authority request. See [decoder contract](C1_RETAINED_IDENTITY_DECODER_2026-10-02.md).

## C1 MEE ownership evidence — exact-source PASS

File-only collector source 095a219 reproduces five MEE ownership/lifecycle
windows: 960 instructions, 61 structural anchors PASS. Default search compatibility
PASS (472 instructions). Full clean local regression PASS: 310 Python/no skips,
62 Node, 22 stages. Independent private report/hash verification PASS; research CI
37038542355 and full macOS 37038542153 both exact-source PASS. Bounded static audit
retains the sole known local-argparse false-positive, raw exit 1.

Retention, state overwrite/repeated saved entrypoint call, finish callbacks and
separate teardown release are distinguished. Supplemental 315-instruction AEgx
file review identifies a separate modern AEGP queue; do not equate seven retained
GeneralPlugin records with seven particular AEGPs or borrow public AEGP repeat
semantics. Actual seven-record identities and lifetime/repeat safety remain
unproven. No new live operation, native profile/helper or gate change. Next owned-
buffer record identity/layout decoder and a separately scoped diagnostic contract;
PIN comparator/synchronization remains open.
See [MEE ownership review](C1_MEE_OWNERSHIP_REVIEW_2026-10-02.md).

## Next gate — exact order

1. Review root/provider identity, memory-range provenance and host lifetime/
   quiescence; prove complete callback/state observation without host getters.
2. Review end-of-pass effects and borrowed/retained state; freeze the complete
   single-root native contract without replacing callbacks or replaying startup.
3. Connect the research-only inert C1 backend/AEGP and independent one-shot
   supervisor; verify refusal/replay/timeout/journal paths offline.
4. Build/sign/hash/inert-test one exact clean candidate and fresh owned fixture.
5. Obtain separately scoped authorization for that candidate's installation,
   any AE launch, provider retention and the one private resource pass.
6. Establish a fresh exact running host/project/resident-module baseline, then
   publish at most one request. Stop and preserve evidence on uncertainty.
7. Require exact registry insertion in the same process; prove apply/render
   separately only after registration PASS.

C0 is already PASS and must not be repeated as a substitute for this work.

## After no-scan PASS

Only then:

1. review PLUG end-of-pass callbacks and retained state;
2. prepare one fresh embedded ordinary-effect fixture;
3. run one bounded resource-registration experiment;
4. require an exact new match name in the same AE process;
5. prove apply and render separately.

Do not replay startup lifecycle functions, enumerate global roots, bypass cache
predicates, replace callbacks, clear caches, force notification, unload provider
code or repeat the old unchanged ML scan.

## Permissions and stop conditions

The earlier installation/one-restart permission is consumed.

General instructions to continue do **not** authorize:

- a new install or AE launch/restart;
- a private FILE/PLUG host call;
- provider-reference retention;
- debugger attachment;
- process termination;
- project/preferences/third-party plug-in mutation.

No `main` change, merge or release. Never delete preferences, projects or
third-party plug-ins.

A timeout or uncertain native outcome preserves evidence and stops; it is not
permission to retry.

## Current limitation

The original `/Users/os3kov/Documents/AE-Hot-Loader/` checkout was read clean at
`182d058`; it was preserved. Development uses a separate working clone, initially
synchronized to remote `9c142ed` and advanced to the C1 code head above.
The current AE process list could not be read in the sandbox; running project
and resident-module baseline remain NOT OBSERVED. No live C1 operation, helper
installation, launch or project mutation was performed. The earlier C0 live
PASS remains identified historical evidence, not today's host observation.
