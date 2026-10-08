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
| QC05 | Fresh unique signed source-bound build | PASS offline at c137782; exact signed files and74SDK hashes reverified |
| QC06 | Guard failures, one render, cleanup, applicable regression | PASS offline:26 generated-script model cases;515Python/62Node/22stages;21SDK frame/13backend/3inert ASan/UBSan cases |
| QC07 | No foreign AE/aerender before installation | BLOCKED pending user closure of PID13150; no project read |
| QC08 | One own startup/apply/queue export | NOT RUN |
| QC09 | Exact PNG/counter/provenance/pixel verification | NOT RUN |
| QC10 | Review, safe retention/retirement, checkpoint/source/CI reconciliation | IN PROGRESS |

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

## Preparation result and exact Evidence

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

QC01–06 preparation complete; QC07–09 await the user's explicit AE-closed
confirmation and fresh process/file preflight. QC10 documentation/review/source
publication complete for preparation; exact final CI and live evidence remain
open. User chose to close PID13150 and report; no message confirming closure
has arrived. No inspection, shutdown, install or host launch performed.
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
