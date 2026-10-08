# C1 independent Render Queue control — 2026-10-08

Stage C1 / Development. User approved the ten-step control-frame packet, then
explicitly supplied rules v11.0.0. Baseline source `dcf33db270c92019c297c9c9cf04cc3b496e0463`,
research/ordinary-plugin-discovery. No main, merge, release or product-goal change.

## Adoption and applicability

AI_ENTRYPOINT read first from a separate clean v11.0.0 tag checkout, peeled commit
`e8b763ad2fefd0c5d79f865f7f017ff714cf7c23`, VERSION11.0.0. Git source/tag identity
verified; release archives were not used or locally verified. Historical v8.0.0
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
| QC05 | Fresh unique signed source-bound build | NOT RUN until clean code commit |
| QC06 | Guard failures, one render, cleanup, applicable regression | 26 actual generated-script model cases and 9 retained live-controller cases PASS; native/full pending |
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
