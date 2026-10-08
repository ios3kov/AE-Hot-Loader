# C1 independent Render Queue control — 2026-10-08

Stage C1 / Development. User approved the ten-step control-frame packet, then
explicitly supplied rules v11.0.0. Baseline source `dcf33db270c92019c297c9c9cf04cc3b496e0463`,
research/ordinary-plugin-discovery. No main, merge, release or product-goal change.

## Adoption and applicability

AI_ENTRYPOINT read first from a separate clean v11.0.0 tag checkout, peeled commit
`e8b763ad2fefd0c5d79f865f7f017ff714cf7c23`, VERSION11.0.0. Git source/tag identity
verified; GitHub Release confirms this same source, published2026-10-08T17:13:39Z,
non-draft/non-prerelease. Release archives were not used or locally verified. Historical v8.0.0
and all earlier Evidence remain frozen. Applied core §1, API §3, automation §4,
identity/regression/Evidence/task closure, native §23, tools §22, diagnostics §16,
code review §14, standard migration §34 and the limited handoff checklist §26.
Risk Critical (host/project/render), delivery Development. Existing product
contract covers this diagnostic; discovery/reference/evaluation package N/A.
9–11 adoption delta: proportional decision routing, native review split/units,
conditional skill admission and compact core/checklist; no relaxation of real-AE
or project safety. No new incompatible repository/IPC schema.

Production-engineering is an existing accepted toolchain. Text-only review for
this packet: SKILL.md SHA256 `655791fc067e891b7ea7a301ef3e74736b61ad1b1e854c792b2bc3ec76da93fb`,
workflow.md SHA256 `553985683990651ff5f3e604134950aa519cf20dc0b1de9038cc7f0cd11befad`.
Instructions reviewed for current scope/trust; no new third-party package/hook/
service installed. Git/compiler/project checks are retained tools, not newly
self-authorized extensions. No proprietary projects/source uploaded.

## Question, acceptance and preserved obligations

Can the already startup-registered ordinary marker generate the independently
expected pixel pattern via documented Render Queue export? This is a separate
control experiment, **not an async fallback, async fix, C2 or hot-add PASS**.

Acceptance: exact identified source/signed pair/host/PID/birth/unique request,
own initially blank unsaved clean project, full installed-key enumeration and
Apply/reverse/build/seed proof; one queue frame at1/24s (duration1/24s,24fps),
64x48 pixels,8bpc,PAR1,full resolution,working-space None,no linearization/OCIO;
queue DONE, render counter increases, one bounded valid PNG, pixel agreement.
RGB8 exports imply opaque alpha; native alpha is NOT independently verified by
RGB. RGBA8 additionally verifies the exported alpha. Decoder performs no color,
gamma, resizing or alpha conversion; PNG decompression/filter reversal only.

Existing async route/callback/receipt guards and original null-world failure
remain unchanged. C1 late ordinary registration PARTIAL/NOT RUN; C2/D/release
open. Unattributed scripting screenshot stays OUT_OF_SCOPE. No worker AEGP,
private call, attach, cache purge, preference/security change or nonce replay.

## API source inventory (checked 2026-10-08)

SDK25.6_61 exact AE_GeneralPlug.h SHA256
`30d12ec3eb5af1a902c7414053b1be1da0204b226e0b1cdc71272be1e137000c`:
UtilitySuite6 revision13 ExecuteScript/IsScriptingAvailable and MemorySuite1
handle pairing reused on main-thread idle. Exact host AE25.6x101/macOS arm64.

Public scripting sources:
- https://ae-scripting.docsforadobe.dev/renderqueue/renderqueue/ — render() is
  blocking until completion; no claim of interrupting a blocked call.
- https://ae-scripting.docsforadobe.dev/renderqueue/renderqueueitem/ — items.add,
  timeSpanStart/Duration (seconds), settings/readback, DONE and outputModule.
- https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/ — local templates,
  applyTemplate/file/postRenderAction/getSettings. Format is readable, not settable.
- Adobe automated-rendering docs establish aerender as an alternative; selected
  control uses Render Queue in one owned AE process, without saving an .aep or
  launching another renderer.

No invented saveFrameToPng or new private symbol. PNG Sequence must exist in the
actual target templates; no assumed template creation/global template save.
Strings Quality/Resolution/Effects and PNG settings must read back correctly or
this experiment refuses. Mocks establish behavior of our guards, not those
values or host-object identity on AE. One actual target run is still required.

## Task → check → Evidence

| ID | Ten-step packet | Result before live run |
|---|---|---|
| QC01 | Review exact supported export contract and v11 adoption | DONE; sources above |
| QC02 | Separate queue command; never dispatch async for this request | IMPLEMENTED; request/branch checks |
| QC03 | Reuse owned native fixture/key/Apply/build/seed gates | IMPLEMENTED; retained actual-SDK tests |
| QC04 | Independent pattern and bounded PNG decoder | 6 Python cases PASS, including all five PNG filters, RGB/RGBA, corruption/bombs |
| QC05 | Fresh unique signed source-bound build | PASS offline at547bd6d; exact signed files and74SDK hashes reverified |
| QC06 | Guard failures, one render, cleanup, applicable regression | PASS offline:27 generated-script model cases;515Python/62Node/22stages;21SDK frame/13backend/3inert ASan/UBSan cases |
| QC07 | No foreign AE/aerender before installation | PASS; user closed AE, fresh no-AE/aerender preflight |
| QC08 | One own startup/apply/queue export | PARTIAL: startup/key/apply PASS; queue refused at template selection before render |
| QC09 | Exact PNG/counter/provenance/pixel verification | NOT RUN: no output; refusal identity verified |
| QC10 | Review, safe retention/retirement, checkpoint/source/CI reconciliation | DONE for this bounded attempt; user closed host, exact bundles retained outside discovery; both exact-code CI runs PASS |

The one-shot supervisor reuses120s operation and180s startup budgets; it never
resets deadlines/retries. Render Queue blocking cannot be forcibly interrupted
by this contract. On failure it preserves partial project/queue/output and marks
UNKNOWN, with no assumed rollback. Completed owned queue item stays as evidence.
Shutdown needs a fresh exact owned-project proof (including the exact completed
queue item/output path) and released SDK handles. No unknown session is stopped.
Retirement only after no AE process and exact unique bundle hashes; never delete
unknown installed material. Original plugin metadata comparison remains mandatory.

## Spec and quality review scope

Spec: separate startup control, explicit request, same owned process; original
late-add and async acceptance retained. No release or implicit engine restart.
Native reviewed: QueueControl::Quote/Script and Backend::QueueControl,
OwnedSnapshot/CleanupSafe queue branch, FinishCalibration/Idle dispatch. String
allocations bounded by fixed configuration/4096-byte responses; resource pairing
uses existing Script/Backend RAII. uint64 deadlines are seconds; frame1 at24fps
is1/24s; duration1/24s means one frame. No pixel pointer crosses callbacks, no
worker SDK, idle_active and consume-before-parse guard reentry. Main-thread
queue_control only. No marker/AsyncFrameCapture changes. Real queue/render thread
behavior and remaining async lifetime are BLOCKED/UNKNOWN until target evidence.
Python decoder bounds file1MiB, fixed64x48x3/4 strides,128chunks,CRC/decompression
EOF/size and filter types; no external decoder dependency. Supervisor enforces
source/artifact/process exclusivity, distinct result schemas and matching export
channels. Cleanup failure cannot turn render completion into whole-run PASS.

Review correction: run.py previously required18 frame cases while current builder
produces21. Updated mandatory preflight to21 for the fresh current-source build;
old bytes cannot pass current-source validation. This does not alter async capture.

## Initial preparation result and exact Evidence (historical c137782)

Code candidate `c137782086a971907df0a28da4f73a59f32f3d15`, research branch pushed.
Fresh nonce `93b34ac9a7df4975ad98691f389c26ad`; manifest SHA256
`e3c7cb382abf9be9c82c02c914828d927dbf25d19c6b3fb07a0c6897f7af1241`.
Both signed bundle file maps and74SDK hashes independently reverified. Private
control EMPTY/live ABSENT: installation, host loading and queue render NOT RUN.
ASan/UBSan21 frame cases,13 backend/3 inert and own signed marker pixel comparison
PASS. This is offline code evidence; no new TSan run or real AE claim.

Full source-bound local regression:515Python,zero skips/errors/failures;
62Node tests and22stages PASS. ZIP
`private-evidence-2026-10-08/AEHL-checks-zkv03ms0.zip`, SHA256
`3b15064f9d6e8228cd7f182012e2b003033cfedcc746aaf8e5b7a77d49c87008`;
CRC and24member digests PASS. Initial invocation before creating the private
output-parent returned BLOCKED before checks; preserved here, corrected to a
fresh owned directory, then the complete source-bound run above passed.

Scanner first included ignored historical build Evidence and exited2/incomplete
on an oversized old symbols file. Raw result retained; no clean PASS claimed.
Corrected scope is a hash-bound copy of all411 tracked candidate files:272
supported text files,139unsupported types,zero omissions; raw exit1 retained.
Only finding `e2999cfe8b5b3a6bd27f0a62` is the unchanged argparse local artifact CLI
at tools/artifact_manifest.py71, not an auth/network route. Manually reviewed
false positive; C++ unsupported by this scanner, reviewed separately as above.

Private receipts and source inventory under ignored
`build-ae-hot-loader/queue-control-2026-10-08-93b34ac9a7df`, pointer
`build-ae-hot-loader/current-queue-control-evidence.json`.
Research CI37824044004 PASS at exact c137782. Full macOS CI37824044060 still
in progress at the preparation checkpoint; not promoted to PASS.

At the initial c137782 checkpoint QC01–06 preparation was complete; QC07–09 awaited the user's explicit AE-closed
confirmation and fresh process/file preflight. QC10 documentation/review/source
publication complete for preparation; exact final CI and live evidence remain
open. User chose to close PID13150 and report; no message confirming closure
has arrived. No inspection, shutdown, install or host launch had been performed at that checkpoint.
C1 PARTIAL; queue pixels/async receipt lifetime UNKNOWN; late-add/C2 NOT RUN;
D/release remain open. Evidence/candidates/old checkpoints retained, no deletion.

## Review correction before any host run

The completed queue fixture alone did not prove that the user had not changed
it after export. Current queue script returns the post-render project revision;
Backend requires the exact same owned snapshot after the marker counter check
and again for CleanupSafe. A changed revision revokes shutdown proof. Added
model case for an edit during render, and verifier refusal for mismatched
revision. 27 generated-script cases PASS. This affects queue control only.
The earlier c137782 candidate/515-test receipt remain historical; current native
artifact and regression must be rebuilt/rechecked before use. No host action.

## Current candidate and one controlled target attempt

Code `547bd6d3465b2c1eb76d27f8245aa83b119180dd`, pushed on the research
branch. Fresh nonce `0fd1bbe7343d4d56af95cac33dc285c1`; manifest SHA256
`c2bfbead79a1effd77d15a65bd92f2d7c1528471e7dc28f3e8d37273c94be963`.
Both signed bundle file maps,411 tracked-source hashes and74SDK hashes PASS.
Rebuilt exact-SDK ASan/UBSan21 frame/13backend/3inert and own marker oracle PASS;
27 generated-script guard cases PASS. Full fresh515Python/62Node/22stages PASS,
zero skips/errors/failures. ZIP `private-evidence-2026-10-08/AEHL-checks-_vkd630a.zip`
SHA256 `5c10f135c8bc7f4f4740767b4ee169fcd9f720d1364ee249fce79cf089eb2694`;
CRC and24member digests independently verified. Current tracked-source scanner
272supported/139unsupported/zero omissions, raw exit1: same unchanged CLI
false positive reviewed; no clean scanner PASS. Native review separately retained.
An initial independent verifier used relative SDK paths without the SDK root,
failed before verification, then corrected and independently checked all74 files;
no candidate/host change or weaker check. Receipts are private under
`build-ae-hot-loader/queue-control-2026-10-08-0fd1bbe7343d`.
Exact research CI37824869756 and macOS CI37824869741 both PASS at547bd6d.
These establish candidate CI only, not target pixels, hot-add, final docs HEAD
or release acceptance. Terminal CI receipt retained separately in private Evidence.

User confirmed AE closed; fresh no-AE/aerender preflight PASS. Exactly two unique
owned signed bundles installed, no replacement. One exact owned AE25.6x101 arm64
process PID29208/birth1791484459.707439 reached READY; one queue request sent.
Normal startup enumeration/key796, apply/reverse/build/seed gates completed.
Native result `PARTIAL_UNKNOWN`, stage `queue-control`; script result:
`REFUSED`, stage `settings`, reason `png-template-unavailable`.
The exact name `PNG Sequence` was not available exactly once in local templates.
This does **not** prove that PNG format or a differently named PNG template is
absent. No template names/settings were recorded by this candidate. No new
private call, async capture, render retry, timeout extension or fallback.
Render entry count initially0; render() was not reached; output folder EMPTY.
Pixels/queue export NOT RUN, not a render crash or an async-lifetime result.

Native SDK resource release PASS; fresh owned-project shutdown proof absent
because queue operation was incomplete. Host preserved; user closed PID29208
without saving the owned fixture. Fresh no-AE/aerender check PASS, only exact
unique signed installed pair moved to private `live/retired-installation`;
foreign plugin entries unchanged during the run and retirement. Original
`live/result.json` remains immutable (automatic cleanup BLOCKED); supplemental
`live/manual-close-retirement.json` records user closure and retained bundles.
No user project read/window operation, forced stop, preferences or cache change.

Ten-step packet reconciled: QC01–07 preparation/preflight PASS; QC08 partially
completed; QC09 pixels NOT RUN for the specific template guard; QC10 review and
safe retention complete. This is a bounded diagnostic result, not overall task
or release success. C1 PARTIAL; late-add/C2 NOT RUN; async receipt lifetime
UNKNOWN; D/release open. Next packet: observe local output-module template names
and actual Format via documented API in a fresh owned queue fixture, select only
a verified existing PNG format, preserve all guards, then one separate new nonce
control frame and independent pixels. No inference that English template names
or mocked template settings exist in the target host.

Private assembled source/artifact/control/check Evidence:
`private-evidence-2026-10-08/AEHL-queue-control-547bd6d-0fd1bbe7343d.zip`,
SHA256 `1b010dd97fbf96fc8c8a563351195f52874d20e9dfa5d816e7e9ea929154445f`;
460members, CRC and all member hashes PASS, mode0600. Includes all411 exact
candidate source files, both signed own artifacts and bounded control/result/
retirement/check receipts. Proprietary SDK/Adobe binaries, project/window files
and host stdout/stderr excluded; raw own logs retained locally. This is private
research Evidence, not an installable release. Terminal CI receipt was obtained
after assembly and is retained separately without rewriting the archive.

## Follow-up fourteen-step template packet — in progress

User approved the proposed fourteen-step packet. Baseline d31d8d0, clean research
branch; rules v11.0.0/e8b763ad retained. C1/Development, Critical host/render/data
scope. Smart Entry/core§1, API§3, automation§4, task closure§11, diagnostics§16,
native§23, review§14 and limited handoff§26 apply. Existing accepted
production-engineering toolchain reused, no new package/service/skill admission.
Contract remains startup control; no late-add, async fallback or global template
creation. No foreign session/project/preferences/cache/security edits. One new
owned startup/request/render at most, same120s operation/180s startup budgets.

| Step | Planned task | Check/acceptance |
|---|---|---|
| QT01 | Recover baseline/rules/scope | clean d31d8d0; retained obligations |
| QT02 | Verify template API | OutputModule docs: existing templates/apply/read Format; never set Format/save template |
| QT03 | Record actual names/formats/channels | bounded percent-encoded receipt on success/refusal |
| QT04 | Select existing observed PNG | first eligible actual Format=PNG Sequence, RGB/RGBA; template name independent |
| QT05 | Read back frame/output/color/settings | original64x48/24fps/1/24s/8bpc/None guards retained |
| QT06 | Resource/project/shutdown review | OM reacquired after apply; one output; unchanged post-render revision required |
| QT07 | Failure and parser regression | localization/format spoof/absence/invalidated wrapper/bounds/incomplete inventory |
| QT08 | Full offline regression | exact candidate checks |
| QT09 | Unique signed candidate | fresh source/build/nonce/SDK/file maps |
| QT10 | Spec/quality review and CI | native five-risk domains; exact-source CI |
| QT11 | Fresh no-AE preflight and owned start | no foreign process; own PID/birth/build |
| QT12 | Actual templates and one render | known eligible format or explicit refusal with receipt |
| QT13 | Pixels/resources/retirement | oracle + current own-project proof; preserve host if absent |
| QT14 | Evidence/source/status reconciliation | archive/hash/checkpoint; no release claim |

Implementation:64-template ceiling,128 UTF-16-unit name/Format/Channels ceiling,
2600 ASCII inventory chars,3300 inventory+selected chars, within native4096-byte
script-result envelope. URI percent encoding protects separators/newlines and
records Unicode names without executing them. At every apply, only owned queue
item changes; guard before/after; reacquire output module and force post-action
NONE. Completed inventory required before selecting/rendering; partial refusal
preserved. Final Format/Channels must match eligibility/readback. Native async,
marker, SDK handle ownership and PNG decoder remain unchanged. Selection still
requires observed canonical PNG Format; an unrecognized/localized Format value
will be recorded and refused, not guessed from name or numeric ID.

Spec/quality review before build: Quote/Script, queue_templates and verify_queue
reviewed for memory/response bounds, numeric/unit bounds, ownership/error cleanup,
thread affinity/reentry and diagnostic safety. Headers/API ownership and observer
resource pairing unchanged; pure generated JS exercises fresh OM wrappers.
Non-image templates without Channels record UNAVAILABLE and cannot be selected.
Review tightened inventory+selected bound to3300, rejected extra output modules,
and requires selected Channels to read back unchanged. No other code scope.
40 generated-script cases and7 queue Python/9 retained startup cases PASS.
Model checks establish our decisions/refusals, not Adobe execution or PNG presence.
Fresh exact-code build/regression/CI and actual target run still NOT RUN here.

An added audio-template model initially referenced the template name outside
its callback; test failed, binding corrected inside applyTemplate, then all40
script cases/7 Python methods passed. Whitespace check corrected a trailing
blank line. No AE action or weakened acceptance during these corrections.

## Fourteen-step target result and completion-reader correction

Tested code65c9eed72a46e3db82caa740413f86d838153e76, nonce
4a464c29bb9d4325bbee56f97008d27c, manifest SHA256
1b434d04b6604acea7a6fea63684e325815b16a1a2ea1afeb2c2bb333a15264e.
Native signed file maps,411source files,74SDK hashes PASS. Rebuilt actual-SDK
21frame/13backend/3inert ASan/UBSan and own marker oracle PASS. Fresh full
516Python/62Node/22stages PASS, zero skips/errors/failures. Check ZIP
AEHL-checks-1a2tljo9.zip SHA256
d77c9319ab056cf2a5f934ba30f8e99532025fa749a4a88d6a948be64f2a2445,
CRC/24member digests verified. Exact research CI37826641856 and macOS
CI37826641919 PASS. Scanner raw exit1 retained:272supported/139unsupported,
zero omissions; same unchanged local CLI false positive; native separately
reviewed. These receipts cover65c9eed only, not the later fix bytes.

Fresh preflight no AE/aerender; user authorized this packet. One own AE25.6x101
arm64 process PID32884/birth1791485229.881104, key796 normal startup/apply,
build/seed4867660 verified, one queue request/render. Complete20-template actual
inventory recorded; existing template `png` read back Format `PNG Sequence`,
Channels RGB, selected by format. Queue script reported DONE at revision34.
No global template creation/settings changes. Output `control00001.png`,914bytes,
64x48 RGB8. Independent bounded decoder/oracle:0differing channels, PASS,
packed/expected SHA256
7a9109355c6d9aff5e6a0dadf648d6b0a643b411f027a47035ceaac560ed15de.
RGB alpha implicit255; native alpha NOT independently verified. No color/gamma/
resizing conversion. Real queue DONE and pixel comparison are distinct evidence
from whole native completion; C1 hot-add/C2 and async lifetime remain unchanged.

Native completion was PARTIAL_UNKNOWN: old QueueControl reader took everything
after `revision=` as digits. New inventory lines after revision caused refusal
before counter-after and post-render owned-snapshot/cleanup-safe publication.
Whole supervisor result FAIL_OR_UNKNOWN, preserved; queue-metadata absent.
Cannot reconstruct missing counter/lifetime/shutdown proof from matching pixels
or retrospectively relabel this run PASS. Native SDK resource cleanup PASS;
automatic host stop not attempted. User closed PID32884; fresh no-AE/aerender
check, exact signed own pair retained in live/retired-installation; other plugin
entries unchanged during run/retirement. Raw original report unchanged;
manual-close-retirement.json supplemental. No window/foreign project read.

Implemented correction: native RevisionLine consumes exactly one terminated
positive canonical safe-integer revision field, rejects duplicate/missing/
overlarge/nondecimal/unterminated values and bounds4095bytes. Additional
capability fields are accepted. QueueControl then still requires new marker
counter, exact post-render snapshot and unchanged cleanup revision. Review scope
RevisionLine and its QueueControl consumer: bounded allocations, positive
integer/Number safe range, no ownership changes, same main-thread affinity,
fail-closed exceptions; existing SDK RAII preserved. Added production-reader
regression with extended suffix and malformed receipts. Actual retained DONE
receipt parses as34 offline; this is no Adobe call and no runtime-fix proof.
An initial standalone pixel verifier imported a nonexistent oracle module,
failed before verification; corrected to the actual oracle.py and compared all
pixels. No acceptance bypass or host retry.

QT01–12 preparation/inventory and one render completed; QT13 RGB pixel comparison
PASS but native counter/completion/shutdown proof incomplete, user retirement
PASS. QT14 reconciliation preserves all evidence; fix rebuild/regression/CI
results are recorded below. Only one own launch/request/render in this packet. No second host run,
replay or extended budget after correction. Next validation needs new exact
fixed build and one fresh owned run to establish the complete native receipt.
C1 PARTIAL; late-add/C2 NOT RUN; async receipt lifetime UNKNOWN; D/release open.

## Reader-fix preparation and packet reconciliation

Fixed code `92155daa0ee4753afb6874f8c9e317efed831095`, research branch pushed.
Fresh inert nonce `d09fad1ea0b243c5bc31054d7312d4c2`, manifest SHA256
`1cd20b3f28a969eab378f5352d146d2ab2292c3715055b6b41347a668ad3279e`.
Both signatures/file maps,411source files and74SDK hashes independently PASS.
Observer binding UNCONFIGURED_INERT; control EMPTY/live ABSENT, install/load/
render NOT RUN. Exact-SDK21frame/13backend/3inert ASan/UBSan and marker oracle
PASS. Dedicated bounded native RevisionLine ASan/UBSan12cases PASS, including
actual retained DONE receipt; Adobe_calls0. Eight queue Python methods/40
JS model cases PASS; revised full517Python/62Node/22stages PASS, zero skips/
errors/failures. ZIP AEHL-checks-ha6plzzc.zip SHA256
0c3bb3aa6b06fcb767521aff8bb75547c257bc230e7a1f77b27783ed894f6f64,
CRC/24member digests verified. Scanner raw exit1 preserved:272supported/
139unsupported/zero omissions, same unchanged CLI false positive reviewed.
Native five-domain/spec/quality review retained separately. No fresh TSan
required for the pure parser with unchanged thread/SDK path; no lifetime claim.
Research CI37827710861 and macOS CI37827710776 both PASS at92155da.
Terminal receipt retained separately after archive assembly. Neither prior65c9eed CI nor local parser tests establish the fixed
candidate in AE. No second host launch/request/render in this packet.

Final reconciliation: QT01–10 implementation/build/review/local checks done,
exact fixed CI both PASS; QT11 own start PASS, QT12 actual inventory/
one queue render PASS at65c9eed; QT13 independent RGB pixels PASS, native
counter-after/snapshot/completion proof INCOMPLETE, user closure/retirement PASS;
QT14 scoped source/check/Evidence reconciliation done. Ten-step historical
results and all old receipts retained. Fixed-runtime completion is the next
open check; current whole live result remains FAIL_OR_UNKNOWN. C1 PARTIAL,
late-add/C2 NOT RUN, async receipt lifetime UNKNOWN, D/release open.

Assembled private evidence archive (before terminal fixed macOS CI receipt):
`private-evidence-2026-10-08/AEHL-template-frame-65c9eed-reader-fix-92155da.zip`,
SHA256 `02b48af6e2404b2455b005f05c1f7706a3af2b95ac813b1646a321b3ecb44e46`;
893members, CRC/all member digests PASS, mode0600. Both complete411-file source
inventories, own signed tested/fixed artifacts, own PNG/control/results/retirement
and check/review receipts included; SDK/Adobe binaries, project/window files
and host stdout/stderr excluded, raw own logs retained separately. Tested and
fixed-inert namespaces prevent transferring runtime claims between candidates.
Terminal CI/final documentation follow-up are retained separately without
rewriting this archive. This is research Evidence, not a release/handoff package.

Final review/current-source identity: only four Markdown checkpoint/status
pointers changed after exact92155da tests; all non-Markdown source still matches
the signed inert candidate. Docs-only follow-up does not inherit full CI for
its own HEAD; code/runtime identities remain65c9eed and92155da as above. No
merge/main/release/security/preferences/foreign-plugin change. Next bounded
validation: fresh prospectively bound fixed build, one owned startup/control,
new counter-after and post-render/cleanup-safe receipt, independent pixels,
then scoped reconciliation. Actual hot-add/writer safety work remains open.

## Authorized twelve-step fixed-reader validation — in progress

User explicitly approved «делай твои 12 содержательных шагов в один проход».
Baseline1c658794bd834fd31392e05ee161556b90aad805, clean research branch;
rulesv11.0.0/e8b763ad retained. C1/Development, Critical host/project/render
scope. Existing production-engineering workflow; no new tool or dependency.
All non-Markdown bytes match fixed92155da; historical65c9eed pixel success and
incomplete native completion remain distinct. No product-goal/late-add/async
change, main/merge/release, foreign-project/window, preferences/cache/security
operation. Authorization covers one freshly bound owned startup/request/render,
normal owned exit only with current native proof and exact-bundle retirement.
No retry, reused nonce, unverified private call or increased deadlines.

| ID | Task | Acceptance / evidence |
|---|---|---|
| QR01 | Recover rules/baseline/retained obligations | clean identity and current checkpoint; C1 PARTIAL |
| QR02 | Compare fixed native reader and consumer | canonical bounded revision; marker-after/snapshot gates unchanged |
| QR03 | Fresh prospective bound build | unique nonce; exact source/SDK/host/module paths; no installation yet |
| QR04 | Verify signatures/hashes and applicable checks | actual-SDK sanitizers/oracle; focused queue/reader refusals; bound regression evidence |
| QR05 | Fresh no-AE/aerender preflight | no foreign process; exclusive owned destination |
| QR06 | One owned normal startup | PID/birth/executable/build/loaded identity and READY |
| QR07 | Startup registry/apply proof | acquired suite key, reverse key, unique marker build/seed |
| QR08 | Actual PNG output settings | complete local template inventory; observed Format/Channels/readback |
| QR09 | One uncached control frame | standard queue DONE, exactly one private PNG |
| QR10 | Full receipt and independent pixel/counter proof | positive counter delta, same revision, exact64x48 RGB8 pattern |
| QR11 | SDK resources and safe owned exit/retirement | cleanup PASS/current own-project proof; preserve if missing; foreign entries unchanged |
| QR12 | Evidence/status/source reconciliation | immutable private archive/digests; honest scoped result and next gate |

Initial no-AE/aerender inventory PASS. Recheck immediately before dependent live
action; absence now does not prove later absence. Offline fixed build evidence
covers92155da; newly bound bytes receive fresh actual-SDK checks. Full prior
517Python/62Node/22stage evidence may be reused only after non-Markdown equality
and archive integrity verification, never relabeled as a new whole-suite run.
The parser/queue focused regressions run again for this control acceptance.
Whole control success does not establish new ordinary-effect late registration,
startup writer→reader ownership or async receipt lifetime; C2/D/release stay open.
