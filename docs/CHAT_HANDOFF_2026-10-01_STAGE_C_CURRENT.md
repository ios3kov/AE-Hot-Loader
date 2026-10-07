# AE Hot Loader — current Stage C handoff, updated 2026-10-04

## Controlled no-region run: null world refused — 2026-10-07

Baseline `acbf9104170f6683a62efcae4ea920dc9b8a3033`; plan commit `2e045c0`.
User «делай» authorized the twelve-step packet and one own normal-startup test.
Rules v8.0.0 / `132b7cd`: public-SDK Debugging, Development/Validation, native
main-thread/lifetime, API sources, task closure and ownership-aware cleanup.
No native/controller code changed in this packet. Candidate code `79e2955`,
nonce `711dd22e925b4211a5f279b816d4a25f`, manifest SHA256
`730cd473c515eecf7c5246cf90ca5a0feaa098e62031f3a7c21db24c02af2c5d`.
Both signatures, all 74 SDK hashes, exact AE binary and non-Markdown source
reverified; unused control/live/install destinations verified before launch.
Prior exact-code offline 509 Python / 62 Node / 22-stage ZIP and baseline
exact-head CI 2/3/44 verified. No applicable code change justified rerunning them.

Own PID 94305, birth `1791364746.239041`, exact executable/build/ready matched.
Ordinary startup effect key 796 applied to the owned fixture; one frame request
sent. Callback READY/error0/uncanceled/matchingID/nonnull receipt/onStartThreadYES.
Region query absent. SDK boundaries 2/3 show GetReceiptWorld returned; diagnostic
records error0 and `stage=world-handle`, so its output world was null and refused.
World type/size/base/pixel-copy stages were not reached. No frame.argb/metadata
accepted, no marker-after/pixel-oracle confirmation. SDK14/15 CheckinFrame and
SDK16/17 options Dispose returned; outer cleanup/destruction/publication finished.
Native result PARTIAL_UNKNOWN, stage listed-applied-frame-not-run, cleanup PASS,
cleanup_safe YES, render NOT_RUN_OR_UNKNOWN. This run advanced beyond the old
region boundary; it does not establish a general crash fix or receipt lifetime.

| Task | Acceptance and observed result | Status |
| --- | --- | --- |
| NF01 | Exact source/rules/branch restored; no unrelated changes | PASS |
| NF02 | Empty AE/aerender before install/launch; exact owned identity afterward | PASS |
| NF03 | Unused signed candidate/source/SDK and mandatory offline receipts verified | PASS |
| NF04 | Two unique owned bundles installed; hashes/signatures match | PASS |
| NF05 | One startup; exact ready/PID/birth/executable/build | PASS |
| NF06 | Owned fixture and startup effect applied; key 796 | PASS; startup only |
| NF07 | One async request and successful matching callback with receipt | PASS; not pixel proof |
| NF08 | Nonnull world/type/size/stride/base/copy | FAIL: world null after error0 |
| NF09 | Real pixels equal independent oracle; marker counter increases | NOT RUN: no valid world |
| NF10 | Fresh native proof before own termination; SDK release PASS; host later absent; exact pair retired outside discovery | DONE with original wait timeout preserved |
| NF11 | Immutable failure/diagnostics and ownership-aware checkpoint/Evidence reconciliation | DONE locally; archive bound separately |
| NF12 | Research-only publication; exact-head CI and other branches tracked separately | Source/CI tracked separately |

Original supervisor result remains FAIL_OR_UNKNOWN, SHA256
`8381b07b78724694c06aa973d19812932f41d2db032dffef441aa1cbf9b6c342`.
Its generic refusal text says “no frame requested/accepted”; actual publication
was SENT ONCE and callback READY. Interpret that text as no accepted frame,
not as evidence that no request was made. Do not alter the original receipt.
Supervisor accepted fresh native owned-project/resource proof before termination,
but waiting for its own process exceeded 10s. Later independent inventory found
no AE/aerender; no repeated termination, window/project read or second launch.
The supervisor's post-run other-plugin comparison did not execute after the wait
exception; no whole-run metadata PASS inferred. Separate retirement verified
both bundle hashes and unchanged other-entry metadata before/after that move.
Exact pair retained in original run live/retired-after-observed-host-exit.
Late observed host exit does not relabel the frame failure as PASS.

C1 PARTIAL; real render/pixels UNKNOWN; capture refused; late ordinary registration
NOT RUN. This nonce/control is used and cannot be replayed. No private call/attach,
preferences/cache/security changes, main merge/release, timeout extension or
replacement of the async route. Historical receipts/checkpoints retained.
Next diagnostic question: why does the target explicit async successful receipt
produce no world on the caller's later idle path? Review exact SDK suite/lifetime
and call context before choosing a separately authorized experiment. Neither
callback ownership nor an alternative route is established by this run. Do not
relax the null-world guard or transfer AsyncManager/PF_Event_DRAW rules onto the
explicit LayerFrame_Async path. New live validation requires a fresh candidate
identity, preflight and current authority. Evidence retained in private workspace.

## Optional receipt-region query removed — 2026-10-07

Baseline: `0d74d020fb71727bea44b8d63198b15afd2cabfa`; code:
`79e2955f3ea07467a71e47b1b5fccc62d6bcbc3b` on the research branch.
Rules v8.0.0 / `132b7cd`, public-SDK Debugging and Development/Validation apply.
Existing obligations and historical receipts remain unchanged.

One authorized own diagnostic run used code `0512f84`, nonce
`b5d43fa0a03e4019b9429df0795e5f7c`, PID 86040. Exact ready PID/birth/build
and callback READY/error0/uncanceled/matching ID/nonnull receipt were observed.
The caller-thread guard returned; Copy entered; SDK boundary 0 before
`AEGP_GetRenderedRegion` exists, boundary 1 after and boundary 2 before
`AEGP_GetReceiptWorld` do not. No final native result/world/pixels were accepted.
The original 120s timeout remains FAIL_OR_UNKNOWN, SHA256
`1a30c9487961e323c2af551dacb4db34c381cc6d63d55727f867bee89647d00a`.
A missing after-record bounds the last confirmed operation, not the faulting
instruction or receipt lifetime. No matching own-plugin crash stack was found
in three recent reports under the scoped macOS/Adobe log directories.

User-supplied screenshot later confirms AE reported a crash while invoking
`AEHLCalibrationb5d43fa0a03e`, matching the original run, not new code `79e2955`.
Screenshot SHA256 `fb06aac14c172c664f8e6cd04974f1cf7074fcc5e63bde78009f78e044c9a847`.
It identifies the invoked plugin, not the failing instruction or root cause.
The original timeout receipt is unchanged; changed-candidate native validation
remains NOT RUN. No dialog action or process shutdown was authorized by the image.

| Task | Acceptance and observed result | Status |
| --- | --- | --- |
| RG01 | Preserve the original live failure and localize the last confirmed boundary without assuming root cause | DONE |
| RG02 | Remove only the optional region query and required slot; keep async route, receipt/world/pixel/marker/cleanup checks | DONE |
| RG03 | Actual-SDK ASan/UBSan: 18 frame cases, zero region calls with both absent and present slots, original null-world rejection; signed pair, 13 backend and 3 inert cases; full 509 Python / 62 Node / 22 stages | PASS, offline only |
| RG04 | No second launch/replay/timeout extension or agent shutdown; user closed AE, fresh empty inventory verified, exact old pair retained outside discovery | DONE |
| RG05 | Source/candidate/Evidence reconciled; research publication only, exact-head CI retained in GitHub checks and private receipt | Local reconciliation DONE; CI tracked separately |

Trace IDs 0/1 are reserved and absent; ID 2 remains the first receipt-world call.
The fixed diagnostic schema reports `region_queried=NO`. No callback gains SDK
or filesystem work; original acquire/release and cleanup ownership are retained.
The static scanner retained one unchanged CLI heuristic
`e2999cfe8b5b3a6bd27f0a62`, manually reviewed as a false positive (not an auth
route). Raw exit1 and scanner limitations are retained; C++ review was separate.
Release readiness remains not assessed.

Fresh offline candidate: nonce `711dd22e925b4211a5f279b816d4a25f`, code `79e2955`,
manifest SHA256 `730cd473c515eecf7c5246cf90ca5a0feaa098e62031f3a7c21db24c02af2c5d`.
Both signatures and all 74 SDK hashes verified; control empty, live directory
absent. Candidate installation/AE loading/changed-code frame validation NOT RUN.
Full-check ZIP SHA256
`cf2f8887e52a7d773758ee3b4ed5bf5309a6afbdb6f81b6e4280e35b35ab5744`;
CRC and every member hash verified. Initial output-directory invocation was
BLOCKED before checks (inside checkout); corrected to a private sibling evidence
directory, where the complete run passed. No incomplete ZIP is claimed.

User reported closure, but fresh inventory still found own PID 86040 (state UEs)
and no other AE/aerender. User then explicitly authorized only that window's
inspection. Exact official app-path inspection timed out; window/project content
was not read. No agent shutdown performed. User subsequently confirmed full closure;
AE/aerender inventories were empty before and after exact old-pair retirement.
Both old bundle hashes verified; other plugin-entry metadata unchanged. Old pair
retained under the original run live/retired-after-user-confirmed-closure; original
timeout SHA unchanged. New candidate remains uninstalled. A new live run requires
fresh artifact/preflight checks and current authority.
No private attach/calls, preferences/cache/security changes, main merge or release.

C1 PARTIAL; native frame UNKNOWN; late ordinary registration NOT RUN. Removing
the diagnostic call is a controlled experiment, not a validated crash repair.
Next check: one separately authorized own run of the new candidate, observing
receipt-world/type/size/base/pixels and native cleanup, with the same acceptance.
Own receipts are retained under ignored workspace build evidence and a private
sibling checks directory; older temporary receipts unavailable after restart are
not represented as recovered. Unknown material and historical evidence retained.

## Crash boundary preparation verified; cause remains unknown —2026-10-04

Code0512f84b43b3e6b1e96cbfc163b0ee0d77a4b771; fresh offline candidate
runb5d43fa0a03e4019b9429df0795e5f7c; manifest SHA25644efda14f582555f3250ae88771d3f96e02fa1be42c08791fac11bbb86cb9c8b.
CR01 matching native crash stack NOT FOUND in scoped macOS/Adobe directories.
User screenshot names own AEHLCalibrationbbb7009a147d; no faulting instruction
established. Original runbbb7009a147d47f0a3b16e358336b28b evidence preserved.
CR02 code/header review DONE; no proved crash repair. CR03 bounded diagnostic
coverage DONE. Inner frame-sdk pairs0/1 region,2/3 receipt world,4/5 type,6/7 size,
8/9 rowbytes,10/11 base address,12/13 pixel copy,14/15 checkin,16/17 options dispose.
Outer frame-boundary pairs0/1 first Allowed,2/3 Copy,4/5 marker counter,6/7 owned
snapshot,8/9 second Allowed,10/11 Release,12/13 CleanupSafe,14/15 destruction,
16/17 final publication. Optional noexcept trace only on calling path, never
Ready callback. Same SDK call count/order and original guard short-circuit;
no receipt lifetime assumption, acceptance change or timeout/route replacement.
A before-only mark would bound last observed operation, not prove its root cause.
CR04 PASS: actualSDK18 async ASan/UBSan tests assert caller-thread trace and
real SDK call boundaries/order/refusals,13 backend/3 inert; exact74SDK hashes,
fresh signed bundles. Full509Python/62Node/all22stages PASS; ZIP SHA256
3d9c06eb71ea895a73a25f60720ec09dd4e84f37d83b0c1937d414c0a4561ad7; CRC/all member hashes verified.
Scanner preserves same manually reviewed CLI heuristic e2999cfe8b5b3a6bd27f0a62;
release readiness not assessed. No candidate installed or new AE launch.
Prior own PID73811 now absent, AE/aerender inventories empty before/after exact
old pair retirement. Agent did not view/quit project. Own two bundles retained
at build-ae-hot-loader/startup-calibration-bbb7009a147d47f0a3b16e358336b28b/live/retired-after-crash-and-observed-closure;
hashes match before/after; other plugin entries unchanged; original supervisor
result9c85fa618f445586daa8a83a07432610e2cf539babba470a295b1655cbc30ad7 unchanged.
CR05 cause/fix/live validation remains BLOCKED on fault localization. This
candidate improves diagnosis, not a verified repair. C1 PARTIAL/frame UNKNOWN/
late-add NOT RUN. CR06 status/source/evidence reconciled; research push and exact
SHA CI tracked separately. No private attach, cache/preferences/security changes.


## Crash investigation and boundary preparation —2026-10-04

Baseline f78b94b39136785b04c361034188640ddc246c44, clean research branch,
Rules8.0.0/132b7cd unchanged; existing public SDK Debugging/Development/Validation.
User screenshot reports crash while invoking AEHLCalibrationbbb7009a147d,
matching own runbbb7009a147d47f0a3b16e358336b28b/code563fe30. Screenshot does
not identify faulting instruction/stack or prove receipt lifetime. Original
supervisor timeout, callback READY and missing final/world/pixels remain valid.
CR01 locate report matching exact session; searched macOS DiagnosticReports,
Adobe AE25.6/CrashReporter and scoped Adobe crash/temp locations: no matching
stack found. Other app logs/projects not evidence; no arbitrary crash dump read.
CR02 inspect exact SDK25.6_61 and code; no established crash root cause. Public
web RenderSuite4 guide lacks target async contract; local RenderSuite5/version8
header remains authority. No SDK calls moved into callback or private attach.
CR03 fix diagnostic coverage only: optional noexcept fixed numeric tracing before/
after each existing Copy/Release SDK operation, pixel copy, and Done-path outer
boundaries. No new Adobe API, callback IO, acceptance/lifetime/order/timeout change.
CR04 existing18 async realSDK fake-host ASan/UBSan tests verify trace stays on
caller thread, not callback, and real host-call before/after order/refusal behavior.
Full offline checks and fresh signed inert candidate; no install/new AE launch.
CR05 cause/fix/live validation BLOCKED until exact crash boundary/stack and safe
own-session cleanup established. User's prior PID73811 view/closure request
still pending; preserve session and plugins if running. No report generated by
attachment, forced termination, unknown-project reading or replay.
CR06 reconcile evidence/status/research publication/exactSHA CI; C1 PARTIAL,
frame UNKNOWN/late-add NOT RUN. Diagnostic improvement is not crash repair.


## Startup stages observed; callback confirmed, frame unresolved —2026-10-04

Code563fe302c2bc0996db4fb5cdf39e9dfcfd7ca8f6/runbbb7009a147d47f0a3b16e358336b28b,
own PID73811/birth1791113628742893. Rules8.0.0/132b7cd unchanged.
ST01–04 DONE: eight fixed startup stages, realSDK exclusive/schema/refusal
checks,13 backend/18 async/3 inert ASan/UBSan PASS, signed two-bundle admission.
Full509Python/62Node/all22 stages PASS; ZIP SHA2562b40474ea20df2e5cdb1055dd5b198b9b5b106013a24d69f7dd58c02f88457f4,
CRC/all member hashes verified. Raw scanner retained same reviewed local CLI
heuristic e2999cfe8b5b3a6bd27f0a62; release readiness not assessed.
ST05 startup PASS: ready about11.808seconds after attempt, all stages present,
entry through ready-after2ms monotonic. Previous222s delay not reproduced;
this does not establish root cause or prove the new diagnostic fixed startup.
ST06 one request SENT, own fixture/effect/identity/async submission observed.
First poll confirms READY/uncanceled/error0/same request ID/receipt present,
callback_on_start_thread=YES. Native final result/world/pixel oracle absent.
Original operation120s timeout FAIL_OR_UNKNOWN retained immutable, SHA256
9c85fa618f445586daa8a83a07432610e2cf539babba470a295b1655cbc30ad7.
ST07 observation PARTIAL: render-poll-allowed is written only for Pending branch;
its absence with READY does not identify Allowed as blocker. Done path includes
Allowed, Copy, MarkerCounter, OwnedSnapshot, Release and final publication;
no further persisted boundary separates them. Receipt lifetime/root cause UNKNOWN.
No pixel capture accepted; C1 PARTIAL; late-add/private calls NOT RUN.
Own host preserved, no fresh native cleanup proof; exact PID73811 window/own
project closure request pending. Other plugin entries unchanged. No replay,
timeout increase, shared-cache/preferences/security or foreign project changes.
ST08 source/status/Evidence reconciled; cleanup and exact research publication/CI
tracked separately. Next useful diagnostic is bounded Done-path stage separation,
without moving SDK calls into callback or replacing the agreed async route.


## Startup-stage diagnostic pass — accepted2026-10-04

Baseline d1c47069b3c17f0986e330b99dc3418a7eea1524, clean research branch;
Rules8.0.0/132b7cd, public SDK Development/Validation, Debugging Protocol,
API-SOURCE/TASK-CLOSE/CLEANUP and native main-thread/lifetime/diagnostics.
User authorized proposed8-step packet with «делай». Hypothesis: delayed ready
can be localized between authorized entry, suite acquisition, idle registration,
suite release and ready publication; no root cause claimed from prior222s.
ST01 fixed bounded stage facts with PID/birth/build and wall/monotonic millis;
only after same original activation/executable/module/main-thread/replay guards.
ST02 stage diagnostics best-effort; failures cannot bypass acceptance or change
SDK calls, cleanup, request route, callback lifetime,180s startup/120s operation.
ST03 actualSDK adapter/refusal/inert and full offline regression; exact source.
ST04 fresh signed own two-bundle candidate and manifest/hash/admission.
ST05 fresh no-AE inventory then one own normal startup, no foreign session read.
ST06 only timely exact ready allows existing apply/frame acceptance; otherwise
request NOT SENT. No nonce replay or timeout extension. Real frame requires
marker execution plus valid world and independent pixel oracle, not CI.
ST07 classify observed startup/poll/callback stage with unknowns; exact own
cleanup only with valid native proof or authorized confirmed own blank session.
ST08 preserve original results, reconcile source/acceptance/Evidence, research
push/exact SHA CI; no main merge/release/private calls/cache/preferences changes.
All new checks NOT RUN until evidence recorded. C1 PARTIAL; late-add NOT RUN.


## Authorized window check and closure —2026-10-04

User authorized viewing exact PID67497. Fresh executable/birth identity matched
our sole owned session. Narrow UI observation showed Untitled Project without
modification marker, empty Project panel/no composition and no visible error dialog.
The native ready journal matched codecb0ab99/runab77d3b7d3aa4198a16647387b017eb0
but appeared222.332seconds after attempt, beyond the unchanged180second deadline.
Cause UNKNOWN; late readiness is not a successful startup within the budget.
Original supervisor FAIL_OR_UNKNOWN/startup timeout remains immutable, SHA256
 af02539f5df1b12b5105c2d56b46f9fbea133fe33f283376543d86c1e056e41c.
Operation NOT SENT; no fixture/apply/frame request, no nonce replay or new launch.
After verifying own empty unmodified project, normal Quit completed. AE/aerender
inventory empty before/after exact two-bundle retirement; file hashes match,
other plugin entries unchanged. Own directory retained outside discovery at
build-ae-hot-loader/startup-calibration-ab77d3b7d3aa4198a16647387b017eb0/live/retired-after-authorized-window-check.
No raw screenshot/host log archived; fixed own facts only. No cache/preferences,
security, private calls or foreign project/plugin changes. AC06 cleanup DONE;
source/evidence reconciliation and research-only publication tracked separately.
AC01–04 prepared/offline PASS; AC05 completion/poll/receipt live NOT RUN. C1 PARTIAL,
late-add NOT RUN. Next: establish a bounded startup cause/control before a fresh
identified lifecycle run; no arbitrary timeout extension or unchanged retry.


## Completion diagnostic prepared; new startup gate not reached

Codecb0ab99d4bc5454aaab77764a6a1e9d7f7435e6d; own runab77d3b7d3aa4198a16647387b017eb0.
509Python/62Node/all22 stages and18 SDK async ASan/UBSan,13 backend/3 inert PASS.
Checks ZIP SHA2566c8ec63d577d0e228cf39ae7e6d6ca9042e0231dacd9ae3c0ffa33f4ac2d3cec,
CRC/member hashes PASS. Original prior2a6bc53 exact CI now PASS2workflows/3jobs/44steps.
New signed two-bundle admission/hash/no-AE prerequisites PASS. Controller started
PID67497, but ready journal never appeared within180seconds. Operation NOT SENT:
no apply/frame request or fixture mutation by this controller. Project/window
state unknown; no assumption about startup UI or auto-restored contents.
Supervisor result FAIL_OR_UNKNOWN/startup timeout retained unchanged; process
preserved because no fresh native owned-project/resource-release proof exists.
Specific PID67497 window-view authorization/manual closure requested; earlier
PID-specific approvals do not cover this session. No foreign data read or stop.
AC01–04 diagnostic implementation/offline checks DONE. AC05 callback/poll/receipt
live diagnostic NOT RUN, blocked by startup readiness; AC06 cleanup pending,
evidence/status/research publication proceeds independently. C1 PARTIAL;
late-add NOT RUN. This startup failure is not evidence about callback lifetime.
No startup retry with same nonce, timeout extension, cache/preferences/security
change, or speculative synchronous switch. Investigate owned startup gate first
with authorized narrow UI evidence; only then resume identified lifecycle test.


## Async completion observation — accepted continuation

Baseline2a6bc53e73836f6cfa387439604cfb5d18386107, clean research branch.
Rules8.0.0/132b7cd; existing public SDK C1 Development/Validation and Debugging,
API sources/main-thread/lifetime/diagnostics/TASK-CLOSE/CLEANUP. Own prior pair
retired, original timeout evidence retained. Actual frame/late-add still unproved.
AC01: distinguish callback absence from missing idle poll/blocked project guard.
AC02: plain callback fact whether completion ran on Start thread; no SDK/IO
on worker, read only after Done acquire; context/options/receipt pin unchanged.
AC03: first poll journal before original Allowed check, and original Allowed
outcome after return. Journals written once on main thread, diagnostic failure
never substitutes for acceptance. No extra guard calls, idle wakeup, route swap,
timeout extension, project change or new Adobe API. Header IdleHook2734–2737,
RenderSuite5 async callback5339–5380 remain exact SDK25.6_61 authority.
AC04: existing18 async ASan/UBSan cases verify inline/worker/delayed thread facts
and pending omission. Full source-bound checks, signed fresh artifact admission.
AC05: fresh no-AE then one own startup/apply/frame diagnostic. Success requires
same exact identity/new marker execution/nonnull world/independent ARGB8 oracle.
If first poll missing: no claim that callback was absent; polling not observed.
If poll Pending and Allowed returns: callback/host completion still unresolved.
If callback Ready on main thread: this establishes thread identity only, not
receipt validity beyond callback. No SDK access moved into callback on this basis.
AC06: exact owned cleanup, evidence/status and research push/final SHA CI.
All new tests/live checks NOT RUN until recorded. No main/release/private calls.


## Confirmed closure and exact retirement —2026-10-04

User confirmed closure of own PID64849. Fresh AE/aerender inventory empty before
and after retirement. Exact run6cb7c8f7fc31442f8844b88fa96d06bd two-bundle directory
retained in build-ae-hot-loader/startup-calibration-6cb7c8f7fc31442f8844b88fa96d06bd/live/retired-after-user-closure;
manifest file hashes match before/after; other plugin entries unchanged.
No project/window reading, process termination, deletion, cache/preferences or
security changes. Original supervisor timeout result unchanged (SHA256
6e41e93d6c279e6eb328bb1365d62ba304cace84cd89dab7410523059858c89a).
Closure is not callback/resource-release/frame proof. C1 remains PARTIAL.
EW11 closure/retirement DONE. EW12 previous b0ecd7e exact CI PASS2workflows/
3jobs/44steps; closure record publication/CI tracked separately. Code untouched;
509Python/62Node/22stages evidence remains bound to3d3108d, not rerun for prose.
Private prior archive ce63f67072fbdd7e6e780e0d8e37655db4080ec29beef3619e79082c157a9018
retained unchanged; new closure receipt is separate. Rules8.0.0/132b7cd,
AI-STATE/TASK-CLOSE/CLEANUP for continuation and owned reversible retirement.
Next technical block: supported async completion/receipt-lifetime investigation;
fix/frame still NOT RUN without causal evidence; no old-nonce replay/late-add.


## Empty-world diagnostic packet — verified options, missing completion

Code3d3108da3f42a2e85266d364d4fbca443e8d5509; own run6cb7c8f7fc31442f8844b88fa96d06bd,
PID64849/birth1791108039777097. Fresh signed isolated startup/public SDK only.
509Python/62Node/all22 stages PASS,18 SDK async ASan/UBSan cases including
success-null-world and getter/region failure;13 backend/3 inert PASS.
Checks ZIP SHA25694cdfc5b9726396c47c09e922446dafb0bdfe9b6d7c390810c7f0d11bbe168ae;
CRC/member hashes PASS. Raw audit preserved; unchanged CLI auth heuristic reviewed.
Exact target SDK getter signatures/suites verified; no private or invented API.
Actual fixture/apply/BuildID/reverse key again passed. Readback API errors all0:
time1/24,step1/24,worldtype8(enum1),downsample1/1,matteSTRAIGHT(enum0).
Thus wrong requested time/type/downsample/matte is not supported by this run.
Async request submitted, no callback/native result before controller deadline;
rendered region/world/counter/pixels remain UNKNOWN, not zero measurements.
Timeout is new observed outcome, not proof of its cause or a fixed null world.
No speculative fix selected. No changed synchronous path or relaxed acceptance.
Supervisor preserved own host: no fresh cleanup-safe/resource release proof.
Asked user to close only this disposable test project without saving; until
fresh no-AE verification, exact own pair remains installed and must be retained.
No UI/project inspection, foreign session termination or plugin deletion.
EW01–06 DONE preparation/diagnostic;EW07 partial cause UNKNOWN;EW08–10 fix/final
frame NOT RUN (causal evidence missing);EW11 pending own closure/retirement;
EW12 source/status/evidence/research publication/CI in progress. C1 PARTIAL,
ordinary late-add NOT RUN. Prior failures/evidence unchanged.
Next after closure: account for pending async callback/receipt lifetime and
completion scheduling using exact supported contract/controlled diagnostics;
do not replay this nonce or treat non-completion as proof of invalid options.


## Accepted12-step empty-world diagnostic packet

User authorized12-step causal pass. Baseline d8ffb3e8d389b4da0c6735b18b86f3b47d1543cd,
clean research branch; rules8.0.0/132b7cd. Existing C1 Development/Validation,
public SDK/main-thread/resource/color/IPC diagnostics and TASK-CLOSE/CLEANUP.
EW01–03: restore state, exact SDK signatures, own layer/request facts.
EW04–06: reproduce success-null-world in fake SDK regression; bounded public
option readback and receipt rendered-region diagnostics; signed fresh build,
full source-bound checks, no-AE admission, separate own startup diagnostic.
EW07–10: causal decision; minimal fix and fresh validation only if evidence
supports it. No speculative route switch, world fabrication or weakened pixels.
EW11–12: safe own cleanup, retained evidence/status, research push/exact CI.
Acceptance: own64x48 fixture/exact installed key/BuildID; new marker execution,
nonnull SDK world and independent bit-exact ARGB8 oracle; actual target AE.
New read-only SDK25.6_61 APIs: LayerRenderOptionsSuite2/version2 GetTime,
GetTimeStep/GetWorldType/GetDownsampleFactor/GetMatteMode; RenderSuite5/version8
GetRenderedRegion(receipt,A_LRect*). Only main-thread, valid owned option/receipt.
Getter outcomes are diagnostics, never substituted for existing acceptance.
ROI/effects getter absent from this suite: no API invented. Own layer nominal
bounds/fixture and documented NewFromLayer(all effects) remain separate facts.
A2024 author report describes async receipt memory issues, without target build
or causal proof for our null world; no synchronous switch justified by it:
https://community.adobe.com/questions-529/help-with-aegp-renderandcheckoutlayerframe-async-55775
No private calls/attach/late-add/main merge/release/foreign project operations.
Tests/live status NOT RUN until new exact source evidence. Prior evidence retained.


## Latest completed packet — precise empty-world boundary

Source6e0f9a82fea16682edbaf4b2238370b3e4d73466; own run47acf998a1614934a26d5d622217b32b,
PID62306/birth1791107003431261. Exact signed two-bundle/public SDK startup only.
Fresh509 Python/no skips,62Node/22stages PASS; checks ZIP SHA256
ed1f6030406def92d358d8ead6aa7a8f774bcb3d31ff694aaca7f7b55c4d8b6e,
CRC/member hashes PASS.13 SDK backend/16 async diagnostic/3 inert cases PASS.
Actual nonOCIO/color/fixture/apply/identity/reverse key796 passed again.
Callback READY, uncanceled, error0, matching request ID, nonnull receipt.
AEGP_GetReceiptWorld returned error0 but null world: diagnostic stage world-handle,
observer phase copy. Type/width/height/rowbytes remain unobserved (zero defaults),
not measured dimensions of an empty world. No pixel bytes accepted; no render
counter increase established. Cause below this boundary remains UNKNOWN.
Native PARTIAL_UNKNOWN/listed-applied-frame-not-run; resource cleanup PASS/safeYES.
Supervisor OWNED HOST STOPPED, no-AE independently verified. Exact own pair retained
outside discovery, hashes match; other plugin entries unchanged. No user closure
needed for this run. Earlier native/supervisor failures remain immutable.

Progress: corrected color gate and actual own Apply are proven; the frame failure
now has a precise API/output boundary. RUN12 remains OPEN, C1 PARTIAL, ordinary
late-add NOT RUN. No percentage, runtime safety or release acceptance inferred.
Next causal packet: inspect the actual layer options/time/effects selection and
rendered-region contract using exact SDK and bounded own diagnostics; add the
observed success-with-null-world refusal to regression; isolate the minimal
supported correction only after evidence. Do not replace async with synchronous
render, fabricate a world, weaken counter/pixel acceptance, or replay old nonce.
Source/status/evidence reconciled; research-only push and exact final-SHA CI
must be recorded separately. No main merge/release/private calls/late-add.


## Frame boundary follow-up within the accepted packet

Corrected5756bb4:674c5faf816044c782fb21a01032a607 on own PID59873 passed public
nonOCIO/color checks, created the exact64x48 fixture, applied exact key796 and
confirmed complete own BuildID/seed through generic effect call and reverse key.
Fresh source509 Python/62Node/22stages and13 SDK backend/16 async/3 inert PASS;
checks ZIP SHA256 d61da8e8dd4153f16b2b04108a6fab24980a169ab97d7b1165563074175c6c64.
Native result PARTIAL_UNKNOWN/listed-applied-frame-not-run, cleanup PASS/safeYES.
Render-started/render-suite journals exist; no accepted frame. The exact failing
callback/world/counter/snapshot check is UNKNOWN; no render fix justified yet.
Owned shutdown timed out10seconds; user confirmed closure. Fresh no-AE and exact
two-bundle retirement with before/after hashes/other entries unchanged PASS.
Original native/supervisor partial and cleanup-timeout results remain immutable.

Add bounded main-thread diagnostics only to the existing async capture: fixed
validation stage, public API numeric error and own callback outcome; own world
size/type/stride only. Callback still only writes plain data and release-publishes
completion; no SDK/filesystem/project work added to worker. Callback fields read
only after acquire/completion. Receipt/options retention/release, rejected world,
exact counter increase/owned snapshot and pixel acceptance unchanged. No raw
exception, pointer, profile name, foreign project or host output journal.
SDK25.6_61 AE_GeneralPlug.h5339–5391: callback ID/cancel/error/receipt contract and
CheckinFrame world ownership;5247–5257 NewFromLayer includes all effects.
Existing public suite versions/options/time/route remain; no synchronous switch.
16 existing SDK async cases must also assert diagnostic stage/callback/size facts
and omission of callback fields while pending, with sanitizers. Build/check fresh
identified bytes before a separate targeted frame diagnostic; no replay.
RUN10–11 Apply/identity DONE; RUN12 real frame OPEN; RUN13 own closures/retirements
DONE. Final source/status/Evidence/research-only publication still required.


## Resumed14-step color packet — observed None token, guarded normalization

User accepted14-step continuation. Baseline fb011ca3d162b6f37e2b625326906e2d88e47f03;
rules8.0.0/132b7cd, C1 Development/Validation. API-SOURCE, Debugging, NATIVE
color/main-thread/resource ownership, TOOLS diagnostic/IPC, TASK-CLOSE/CLEANUP.
Prior PID55115 independently absent; exact old pair retained with before/after
hashes and unchanged other plugin entries. Original failure journals unchanged.
Executed prepared be38af2:96f709a54f8a4ad09c6e2dc547c73330 once; new owned PID57799.
Exact key796 again. Fixed facts: final working-space-mismatch/value=none-token.
The getter is exactly None after setting empty string. No fixture/Apply/frame.
UI Color tab could not be operated; no color-engine observation inferred from UI.
Own empty8bpc project visually confirmed, normal Quit requested; save dialog
awaits Don't Save after computer-use lost access. User asked to close exact test.

Correction scope: recognize only empty or exact None under the already exact
AE25.6x101 host gate; retain false linear flags, depth8 and all project guards.
Add public SDK AEGP_ColorSettingsSuite6 / kAEGPColorSettingsSuiteVersion6=7
(frozen AE25.1), AEGP_IsOCIOColorManagementUsed(plugin_id,A_Boolean*).
Acquire/release through existing RAII on main thread; refuse before depth/color
mutation on SDK error or OCIO=true; recheck for owned snapshot/cleanup. No profile
names/paths, private AEGPD functions, engine switch or preference mutation.
[Adobe color-management documentation](https://helpx.adobe.com/in/after-effects/desktop/adjust-colors/color-management/color-management.html)
states Working Color Space=None disables project color management. SDK25.6_61
AE_GeneralPlug.h lines3097–3100/3152–3154 is the exact new API authority.
The read-only SDK engine guard plus strict token/flags will be checked in the next
fresh candidate; ordinary startup/frame acceptance remains separate from hot-add.

| Tasks | Acceptance/current state |
|---|---|
| RUN01–03 | Baseline/source/closure/own pair retirement/fresh signed admission DONE |
| RUN04–05 | Own launch and fixed getter fact DONE; None observed, original result retained |
| RUN06–09 | Minimal representation fix plus public nonOCIO guard, refusal regression, exact fresh build/full checks IN PROGRESS |
| RUN10–12 | Corrected own launch/fixture/Apply/reverse/actual frame CONDITIONAL NOT RUN |
| RUN13 | Empty session Quit requested; Don't Save pending user; own install retained |
| RUN14 | All source/Evidence/status/publication/exact CI require final reconciliation |

All A/B/C1/C2/D, writer/reader/lifetime/reentry/partial-failure/reload/release
obligations retained; no private call/late-add/third-party changes/main merge/release.
Private evidence: aehl-color-facts-9xahsxfo. No repeated consumed request.


## Color packet handoff — preparation complete, second host run pending

Final diagnostic code source be38af2aad3fb32cab1b9d5f1aa3027712e0805c.
Fresh nonce96f709a54f8a4ad09c6e2dc547c73330; manifest SHA256
20b15caa089705d3268cef5b83a4e2c4ddd193e2b980b2f5f497bbe26d58719b.
Signed arm64 marker/observer, exact exports, SDK74 unchanged, prospective
supervisor admission PASS; own control empty, not installed or consumed.
Full exact-source509 Python/no failures/errors/skips,62 Node and all22 stages
PASS. AEHL-checks-p7bt1y19.zip SHA256
21edd90ea60e6543dfd194bdad3cd3d763d068e8705c69114b57e2572f0667f7;
CRC PASS. Actual script36 model cases and actual SDK fake backend11/async16/
inert3 PASS; none establishes an AE frame. Raw static audit retained: one
unchanged argparse CLI heuristic fingerprint e2999cfe8b5b3a6bd27f0a62 manually
reviewed; unsupported C++ manually reviewed; runtime/release not certified.
395 baseline files and256 non-Markdown files outside scoped edits unchanged;
no deletions, foreign plugin modifications, private calls or release actions.

| Tasks | Current outcome |
|---|---|
| COLOR01–05 | DONE: source/rules/contracts, staged fixed diagnosis, negative tests and exact signed build/full checks |
| COLOR06 | DONE: one own normal startup/key796; final working-space postcondition failed; original partial result retained |
| COLOR07 | OPEN: actual getter/category unknown; no causal fix justified |
| COLOR08–09 | PARTIAL: next bounded diagnostic built/tested; causal-fix build conditional |
| COLOR10–12 | NOT RUN: fixture/Apply/reverse/real frame depend on color acceptance |
| COLOR13 | PENDING: PID55115 closure requested after unreliable modal notification UI; exact retained installation unchanged |
| COLOR14 | Source/docs/selected private evidence reconciled; research push and exact final-SHA CI require separate receipt |

Next action after user closure: independently verify no AE/aerender; retain the
exact old two-bundle installation with hash/other-entry checks; verify exact new
manifest/source/own-project authority; run the prepared nonce once. Inspect only
fixed color facts and existing own journals. No unchanged retry or relaxed
profile acceptance. Original failed result is immutable; a later cleanup receipt
must remain separate. C1 stays PARTIAL; hot-add, render and release unproven.


## Color diagnostic observation and next bounded probe

Executed source38672db3c0228e796c7d75c30394926420646adb, nonce
0db57ae5c24c4c1fbd8bc8e2b540d35c, manifest SHA256
142fe5fe1beed4def8742a0b66999659656cf81df5cdb223d7bbe1605d465a94.
Own normal startup returned key796. Native result PARTIAL_UNKNOWN/create-fixture;
color diagnostic final/working-space-mismatch. All three setters returned and
post-setter blank/unsaved/depth8/queue guards passed. The actual workingSpace
value and cause remain UNKNOWN; this does not justify accepting another profile.
Apply/reverse/frame NOT RUN. Full exact-source regression509 Python/no failures/
errors/skips,62 Node/22 stages PASS;11 SDK backend/16 async/3 inert PASS.
AEHL-checks-wuf2vmq0.zip SHA256
9184409f3fa3b10e3685582e23a03a1d45b7d0503ce70abb4a28f553db73bb73.
The first offline prototype d537f30 was never installed: prepare refused an
outdated7-case admission prefix;38672db corrected it to the actual11-case gate.
Both candidates and all original results retained.

Test PID55115 is preserved pending safe closure. A settings-dialog inspection
produced the AE modal-script notification and did not establish the color engine
or workingSpace value. UI input was unreliable; user asked to close this exact
empty diagnostic project without saving. No forced stop, foreign session access,
or automatic cleanup success is claimed. Original supervisor failure remains.

Next diagnostic only classifies the failed getter into fixed categories: null,
undefined, empty, exact None token, other-string, other. No arbitrary profile name,
raw error, host paths or settings are retained. Empty-string acceptance and all
mutation guards remain unchanged; facts are not a fix or frame acceptance.
36 actual-script model cases and native normalization rejection tests cover this
bounded observation; model checks are not host behavior. Fresh source-bound
build/checks required; a second owned startup requires confirmed closure and
fresh no-AE preflight. COLOR07 causal fix, COLOR10–12 Apply/frame and COLOR13
cleanup remain open. COLOR14 final publication/CI is not yet complete.
Private evidence retained under aehl-color-cause-1le8564d; no merge/release or
late-add claim. Earlier A/B/C1/C2/D/reentry/lifetime/recovery gates unchanged.


## Active14-step packet — isolate color preparation before fixture/render

Baseline ee4b51bb2795733563a09af08f9783dfc8f80d1c; clean research branch.
Rules8.0.0/132b7cd, AI_ENTRYPOINT first; C1 Development/Validation. Debugging,
API-SOURCE, NATIVE main-thread/render ownership, TOOLS bounded diagnostic/IPC,
TASK-CLOSE and CLEANUP apply. Existing contract unchanged; no Stage0 restart.
User accepted14-step packet with “Делай”. Prior exact startup key PASS remains
historical, Apply/frame NOT RUN. Prior sessions closed and bundles retained.

| Tasks | Acceptance/check | Planned dependency |
|---|---|---|
| COLOR01–02 | Restore exact rules/source/evidence; selected SDK UtilitySuite6 and scripting property contracts | Required before code |
| COLOR03–05 | Fixed diagnostic subcauses per color stage; no raw errors/foreign project data; negative/no-later-mutation tests; fresh signed identified pair and full checks | No relaxed color/ownership/Apply guards |
| COLOR06 | One fresh owned startup, exact key, own color diagnostic | Only no foreign AE/aerender; consume once |
| COLOR07–09 | Minimal fix only after observed cause; regression/source audit and second fresh signed pair | Conditional on causal evidence |
| COLOR10–12 | Color/fixture → key/Apply/BuildID/reverse → actual64x48 ARGB8/new render/full pixel oracle | Each existing safety guard must pass |
| COLOR13 | Exact own session/resource cleanup, retain pair outside discovery; foreign data untouched | Fresh proof/authority; no forced unknown stop |
| COLOR14 | Reconcile all tasks/source/docs/private evidence, publish research only and exact CI | No merge/release/hot-add claim |

API inventory: local SDK25.6_61 AE_GeneralPlug.h UtilitySuite6/ExecuteScript uses
UTF-8 when platform_encodingB=FALSE; optional result/error handles retain existing
bounded locked/copied/freed ownership. [Scripting Project documentation](https://ae-scripting.docsforadobe.dev/general/project/)
reports workingSpace string/None as empty and two linear properties Boolean read/
write. This is maintained community documentation, not a live AE25.6 contract;
the isolated authorized test distinguishes exact host behavior. No new host APIs.
No cache/preferences/quarantine/third-party changes, worker AEGP, private writer,
unverified unload/reentry, or unchanged consumed retry. All A/B/C1/C2/D, append/
reload/recovery/compatibility/release obligations and previous evidence retained.

## Current result — own startup key confirmed; color fixture gate open

Baseline d5967fe; correction code831c6cea7e2fef08252a709dd74bbdcbad09ac9a.
Two different owned startup attempts completed within the accepted packet:

| Gate | Exact result |
|---|---|
| Prior44-byte own match | Three full787-entry snapshots returned its31-byte prefix/key796; strict guard refused before mutation |
| Fresh31-byte compact match | PASS: three complete snapshots0/1001/3080ms; exact1/key796; matches builder/callback/PiPL/config |
| Candidate |831c6ce:a8d8013686e84eef8e247ce48c579a5b; signed own marker+observer; SDK74 unchanged |
| Manifest SHA256 |6fe4f9200e0879a92eb819d7866d2a917d1089926ebbefa5762d91d2a1fe34c8 |
| Fresh offline regression |508 Python/no failures/errors/skips;51 panel+11 snapshot Node;22 stages PASS, AEHL-checks-byuuy9mf.zip |
| Native guards |17 name-observation+36 core ASan/UBSan;16 async/7 backend/3 inert; own registration adapter/independent pixels PASS |
| Actual blank-project preparation | begin and SDK depth8 confirmed; color-started exists, color-adjusted absent |
| Native result |PARTIAL_UNKNOWN/create-fixture/key796; exact color subcause not yet journaled |
| Apply/reverse/actual AE frame |NOT RUN; no successful color preparation/fixture, no frame acceptance |
| Private entry/late-add/ownership |NOT RUN/UNKNOWN; ordinary startup key is not these proofs |
| Cleanup |Previous PID46466 empty inspection/normal Quit/exact retirement PASS; current PID50612 closed by user; independent no-AE/aerender/exact retirement PASS |

The correction passes the old enumeration gate without weakening byte equality.
Full nonce/source BuildID remains; compact match carries96 identity bits. A
prefix/display observation still never authorizes Apply. The31-byte constraint
is observed in this target AE25.6x101/macOS arm64, not asserted for every SDK/host.

Current session changed only the authorized empty diagnostic project's depth/
color preparation; no comp/solid/Apply/frame success. Automatic review denied
normal Quit because the title is dirty and empty-panel evidence was insufficient.
User chose “Закрою AE самостоятельно”, then confirmed “закрыл”. Independent
no-AE/aerender PASS; exact own pair retained outside discovery with unchanged
before/after maps and other plugin entries. No indirect stop. Original supervisor
failure remains unchanged; separate compact-closure-retirement.json records closure.

Private evidence root: aehl-name-projection-live-zz_eap2e; cause/closure of first
attempt, new source checks/raw audit/manual review, signed manifest, regression
archive and compact-live-reconciliation.json. Raw audit267 text/136 unsupported/
no omissions: unchanged local argparse CLI heuristic fingerprint
 e2999cfe8b5b3a6bd27f0a62 retained with manual disposition.403 tracked paths remain;
392 baseline paths and253 non-Markdown paths outside intentional changes intact.
Final docs-only reconciliation does not alter tested/built non-Markdown bytes.
Exact final research remote/CI and private archive receipts follow publication.

Next: after safe own-session closure, isolate the color-script failure with bounded
own diagnostic subcauses/property checks; do not guess a color-route fix or replay
a consumed run. Then fresh guarded fixture/Apply/reverse/real AE frame. Only after
that startup baseline can the writer/reader/ownership/partial-failure gates advance.
All previous A/B/C1/C2/D, append/reload/recovery and release obligations retained.

## Current correction — observed own match-name projection

One owned startup attempt of e0451d1/9e09478c2faf completed. Three full main-thread
Effect Suite snapshots (787 entries;1/1034/3079ms) found our display-identifiable
marker at opaque key796, but returned31 bytes of the44-byte registration match.
Registration callback completed once/result0; exact own resident-image binding
and registration arguments matched config. Strict exact-match guard refused
before begin/fixture/Apply/frame. This establishes an own startup projection
mismatch, not late-add, descriptor ownership, or a general SDK length contract.
The location of truncation inside the host remains UNKNOWN.

Owned PID46466 was inspected as empty Untitled Project, normally Quit, and
independently absent together with aerender. Exact two own bundles retained
outside discovery; other plugin entries and original failed result unchanged.
Private receipts: aehl-name-projection-live-zz_eap2e, name-projection-cause.json
and closure-retirement.json. Earlier prepared archives remain immutable.

Next authorized correction: fresh marker match `AEHL.M.` plus24 hex nonce digits
(31 ASCII bytes/96-bit identity), while retaining the full nonce/BuildID and exact
byte equality/unique-key guard. Apply never accepts display/prefix/truncated names.
Builder and supervisor must share encoding; diagnostic retention covers both own
prefixes. Required before one new owned run: name-bound/refusal regressions,
full identified checks, source/manual audit, fresh signed pair/SDK74/sanitizers,
independent pixels and prepare. Conditional real key/Apply/reverse/AE-frame and
cleanup follow only their existing guards. No consumed candidate replay.
All private publication/render lifetime/reentry/partial-failure gates, A/B/C1/C2/D,
append/reload/recovery and release obligations remain open. Research only.

## Current packet — Own name/key projection and timing

Baseline79f07b2; user accepted12-step packet. C1 Development/Validation under
rules8.0.0, normal-startup/public-SDK diagnostics only. Own ABI v2 exposes the
same immutable name/match arrays passed to the host registration callback.
Three complete read-only snapshots at monotonic0/1/3second offsets run through
main-thread idle; no sleep/worker AEGP/registration retry. Only own identifiable
name/match/key observations are journaled; display-only/prefix observations never
authorize Apply. Original exact unique key/build/reverse/frame guards retained.
Fresh codee0451d1/nonce9e09478c2faf: SDK74 stable, signed exact exports, ABI/state/
callback metadata/refusals/independent pixels/async16/backend7/inert3 PASS.
506 Python/no failures/errors/skips,62 Node/all22 offline stages PASS;15 new
projection and36 prior core sanitizer cases PASS; raw/manual audit reviewed.
Live stages BLOCKED: unrelated AE PID40212 exists; user asked to save/close and
confirm. That session is untouched. No install/AE launch/request/project read or
mutation; candidate control empty and unconsumed, exact supervisor prepare PASS.
[NAME-01–12 mapping](C1_OWNED_STARTUP_FRAME_2026-10-04.md). Next: after explicit
closure and fresh no-AE preflight, consume this identified candidate once.
ProductC1 PARTIAL; key/apply/frame and private/late-add/lifetime/reentry/partial-
failure/release gates remain open. No merge/release or unchanged consumed retry.

Current continuation: [marker startup/load observation](C1_OWNED_STARTUP_FRAME_2026-10-04.md).
Baseline166c727; corrected793efe4b67ae was consumed once after confirmed no AE.
Marker still absent before mutation; callback correction not sufficient. Exact
PiPL348 bytes match SDK/Rez. PID30555 inspected under exact user permission,
empty32bpc Untitled Project confirmed, normal Quit/no-AE/aerender PASS. Exact own
installations retained outside discovery; original failures/other plugins unchanged.
New versioned atomic own-marker counters and exact own resident-image/SHA observer
read implemented; no load/manual registration/extra SDK selector. Optional binding
failure UNKNOWN; refusal/cleanup unchanged. Fresh13945c4/c8bda7ee9b77 signed/
SDK74/state/oracle/async16/backend7/inert3/505 Python/no skips/62 Node/22 stages
PASS; raw/manual audit reviewed. One actual owned PID33086 startup bound exact
resident marker; registration started/completed1, callback0, setup counters0.
Effect Suite still has no exact target match; key/Apply/frame NOT RUN. Callback0
is not installed-key proof. User-authorized exact PID33086 inspection confirmed
empty Untitled Project/32bpc; normal Quit and independent no-AE/aerender PASS.
Exact own installation retained with unchanged bundle maps and other-plugin entries.
Next: own match-name/key projection and startup publication timing; no blind
packaging/flag change or repeated consumed request.
No unchanged retry; private/late-add/lifetime/reentry/rollback/release remain open.

Previous continuation: [resumed startup registration diagnostic](C1_OWNED_STARTUP_FRAME_2026-10-04.md).
Baseline bb05448; user explicitly resumed owned AE validation. Prepared e6cbac34a5bc
was consumed once, with native REFUSED at enumeration-marker-absent before mutation.
No key/Apply/frame; own PID23266 was preserved because safe closure proof failed.
Later process inventory found23266 absent and another PID27219 running; no window
inspection/closure performed. Preserve27219; await user-confirmed closure and a
fresh no-AE preflight. Marker now supplies the SDK-typed PluginDataEntryFunction2 startup
callback, exact PiPL metadata and error propagation. Focused sanitizer/registration
tests PASS; host-absence causality UNKNOWN. Fresh4218dbe signed793efe4b67ae/
SDK74/async16/backend7/inert3/independent pixels/supervisor prepare PASS;
505 Python/no skips,62 Node/all22 stages PASS; raw audit reviewed. New owned
startup still NOT RUN, dependent on no running AE. Own installed bundles retained.
No private calls,
late-add, attach, merge or release. Prior evidence/obligations remain unchanged.

Previous continuation: [12-step packet preparation](C1_OWNED_STARTUP_FRAME_2026-10-04.md).
User explicitly restricted this pass to preparation without AE launch. Fresh
signed paire6cbac34a5bc at cleanb0140e6 passed SDK74/async16/backend7/inert3/
independent pixels/supervisor prepare; no install/launch/request/project mutation.
Existing AE18624 untouched. Steps1–3 DONE, dependent live stages NOT RUN;
enumeration subcause/key/Apply/real frame remain UNKNOWN/NOT RUN. Exact private
source/diagnostic/publication evidence is retained separately. Runtime resumes
only on renewed user direction and a fresh no-existing-AE preflight.

Previous continuation: [owned startup/frame calibration](C1_OWNED_STARTUP_FRAME_2026-10-04.md).
Executed21c315e passed exact owned startup/live suite/blank-project guards and
refused at enumeration before mutation. Key/apply/frame NOT RUN; subcause
UNKNOWN.505 Python/62 Node/22 stages and16 async/7 SDK-backend/3 inert cases
PASS for that code. Explicit PID15349 inspection/empty-session closure permission
resolved the screenshot rejection; empty32-bpc project quit normally. No AE/
aerender remains; exact own bundles retained outside discovery. Finer enumeration
refusal diagnostics are prepared offline with every safety gate retained.
Final offline repair7134746:505 Python/no skips,62 Node/all22 stages,
36 core/16 async/7 SDK-backend/3 inert cases and exact signed/74 SDK/independent
pixels PASS. Prepared inert build was not installed or run in AE. Final docs-only
commit retains tested code; exact remote/CI and private closeout receipts are
recorded separately at the checkpoint evidence root.
Next gate: fresh reviewed public observer determines exact enumeration subcause,
then one normal-startup key/Apply/marker/frame control. Private late-add/lifetime/
reentry/compensation gates remain UNKNOWN/BLOCKED; no merge/release.


Continue the existing work. Do not restart research or repeat the unchanged
ordinary plug-in scan.

Current continuation: [implemented startup calibration/override checkpoint](C1_STARTUP_CALIBRATION_2026-10-04.md),
[publication/factory contract](C1_PUBLICATION_CONTRACT_2026-10-04.md),
[sequence/render dependencies](C1_SEQUENCE_RENDER_DEPENDENCIES_2026-10-04.md),
[host-operation boundaries](C1_COMPLETE_HOST_OPERATION_2026-10-04.md),
[static Effect Suite reader bridge](C1_EFFECT_SUITE_READER_BRIDGE_2026-10-04.md),
[online research reconciliation](C1_WEB_RESEARCH_RECONCILIATION_2026-10-03.md),
[suspend contexts](C1_SUSPEND_CONTEXTS_2026-10-03.md),
[concrete executor](C1_CONCRETE_EXECUTOR_2026-10-03.md),
[BEE queue controls](C1_WORKQUEUE_CONTROLS_2026-10-03.md),
[scoped admission controls and match-name correction](C1_ADMISSION_CONTRACTS_2026-10-03.md),
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

## Startup calibration — current offline continuation

Baseline6dd5efb; [CAL-01–16 mapping](C1_STARTUP_CALIBRATION_2026-10-04.md).
New code lives only in experiments/startup_calibration and isolated tests.
Marker/core/oracle/public observer implemented; clean codeea6d92a and exact
signed artifact/SDK/independent pixels/inert/refusal/sanitizer checks PASS.
Full local498 Python/no skips,62 Node/all22 stages PASS; original source/SDK and
history retained; raw audit reviewed. Complete private lifecycle/reader/reentry/
recovery and legal late entry remain PARTIAL/UNKNOWN. Documentation-only closure
preserves code; publication state is authoritative only in the exact-SHA
postcommit publication-final.json receipt at the checkpoint's evidence root.
The current packet excludes install/AE launch/attach/process observation/private
calls/fault injection/merge/release. Future owned normal-startup calibration must
prove acquired-suite/startup/key/Apply/uncached frame identity; it is not hot-load.
Do not activate the default inert artifact or borrow an existing user session.
All original stage/product/release obligations and prior evidence stay retained.

## Publication contract — previous offline continuation

2026-10-04, clean baseline `0ee3317555f4e2f37837724699b9f8f0c70ccd1c`;
[publication/factory findings and prepared calibration](C1_PUBLICATION_CONTRACT_2026-10-04.md).
PUB-01/02/06/09/10 DONE for bounded static selection/callback/procedure/closure;
PUB-03/04/05/07/08 PARTIAL.51 complete bodies/51 windows/4525 instructions checked;
17 overlapping historical bodies excluded,34 nonoverlapping bodies/2093
instructions within the stated prior corpus.1133 direct branch checks,nine scalar
fields,two getter bodies,20 encoded rebases/one import bind and seven SDK pins
PASS. Concrete ordinary factory→canonical clone and three sequence-data lanes
are now connected; the selected registration match-name getter cannot reenter.
Reused registry/preferences/notify bodies sharpen post-mutation error and
visibility boundaries without demonstrating whole-operation compensation.

Complete nested lifetime, all-reader/reentry coverage, legal late host entry and
partial-failure compensation remain UNKNOWN. Prepared known-good startup
calibration needs reviewed marker/suite instrumentation and concrete operation
authority; it is not an executed diagnostic. Research/product PARTIAL, adapter/
private implementation/trials BLOCKED; registration/apply/render NOT RUN.
Source/docs/audit/exact publication receipts retained at
`/private/tmp/aehl-publication-contract-yd3r3doa`. No executable/profile/refusal/
product change or AE launch/attach/install/private call. All original
A/B/C1/C2/D/append/reload/recovery/release obligations and evidence retained.
Full local executable regression NOT RUN for Markdown-only edits; no deletion.
Next: override/cache/sequence lifetime and enclosing compensation, then reviewed
startup marker/suite instrumentation. Do not repeat solved static bridges/scans.

## Sequence/render dependencies — previous offline continuation

2026-10-04, clean baseline `983a28b16d005b6854e696626877cd8c6052096d`;
[sequence/render findings and exact next dependency](C1_SEQUENCE_RENDER_DEPENDENCIES_2026-10-04.md).
SEQ-01/02/05/08 DONE for bounded source/table/render-path/closure;
SEQ-03/04/06/07 PARTIAL.33 complete bodies/35 windows/6558 instructions checked,
including26 new bodies/6085 instructions; seven repeated bodies excluded from
novelty.1673 direct branch checks,7 fields,3 original table rebases and exact
SDK selectors/pins PASS. Command16 selects the actual apply task; a SmartRender
path reads the same FLT registry through the sequence index, then retains FCSpec
under the registry mutex before dispatch. This establishes a mixed lookup/owner
path for these files, not complete reader coverage or live frame execution.

Complete factory/derived sequence ownership, code/callback lifetime, publication
reentry/atomicity and full partial-error compensation remain UNKNOWN.
Research/product PARTIAL; adapter unbound, implementation/trials BLOCKED;
registration/apply/render NOT RUN. Current bounded source/docs/audit/commit/remote/
CI receipts retained at `/private/tmp/aehl-sequence-render-3vrnri_6`.
No executable/profile/refusal/product scope change, AE launch/attach/install or
private call. All original A/B/C1/C2/D/append/reload/recovery/release obligations
and evidence remain. Full local executable regression NOT RUN for Markdown-only
changes; no cleanup deletion. Next: concrete factory/sequence-data ownership,
writer callback/reentry and remaining reader/failure boundaries.

## Host-operation boundaries — previous offline continuation

2026-10-04 baseline12ef175; rules8.0.0 unchanged. The maximum connected CTX
packet completed22 original bodies/2267 instructions and629 raw branch checks,
7 scalar/2 owner-field checks, seven SDK pins and four historical archives/
48 windows/11212 instructions. FCSpec retains its routine owner; resource and
provider setup have different preparation timing; readiness can fail after add.
Queued project-clone apply carries an index and can later look up FCSpec.
[Exact evidence, V/C distinction and limits](C1_COMPLETE_HOST_OPERATION_2026-10-04.md).

3 bounded tasks DONE /3 PARTIAL; packet/product PARTIAL. No fresh legal late
entry, complete failure compensation or all-reader/lifetime contract established.
Next: command16 selection→apply task→FLT sequence/FCSpec owner transfer→actual
frame dispatch/callback read set, and per-module phase/error completion. Preserve
the established static reader bridge; do not repeat unchanged scans/context work.
Known-good startup calibration remains conditional on a reviewed instrumentation
contract and current authority; no late mutation/fault injection is authorized.
Adapter/trials BLOCKED, registration/apply/render NOT RUN. No native/executable
or product/refusal/release scope change. Source/docs/raw-audit/exact publication
receipts and original archive retained at
`/private/tmp/aehl-complete-operation-7gyvoc6k`; no deletion.

## Reader bridge — previous offline continuation

2026-10-04 baseline f22671b; rules8.0.0 pinned source unchanged. The user's
continuation resumes original-file research. Effect Suite5's original23-member
table and decoded rebases identify the selected readers; key conversion and
imports lead to the same FLT singleton/vector as the startup registration writer.
12 complete new bodies/1787 instructions,417 raw branch checks,23 original table
words/rebases and historical source checks PASS. [Scope, ownership boundaries
and exact evidence](C1_EFFECT_SUITE_READER_BRIDGE_2026-10-04.md).

Progress: reader/writer storage bridge established statically; live suite mapping,
known-good effect identity, full render/UI/callback dependencies, fresh late
context and partial-failure recovery remain UNKNOWN. Local owner retention does
not close mutation safety. Native adapter/trials BLOCKED; registration/apply/render
NOT RUN. No AE launch/attach/install/private call or executable policy change.
Next: complete per-module host operation and changed read set, then conditional
known-good startup calibration with valid instrumentation/current authority.
Keep late writer calls blocked until the full prerequisites are demonstrated.
Scoped source/SDK/documentation checks, raw audit and exact publication/CI state
are retained under `/private/tmp/aehl-effect-suite-readers-gxz1e__3`.
Full executable regression NOT RUN locally for these Markdown changes. Preserve
all product/A/B/C1/C2/D/release obligations and historical/shared evidence.
No cleanup deletion needed. This section supersedes the previous text-only scope.

## Checkpoint correction — previous scope

That pass requested only checkpoint text correction, no new search.
Baseline0d29d70; [revised hypotheses](C1_WEB_RESEARCH_RECONCILIATION_2026-10-03.md).
Use actual changed-state/read-set safety, distinguish partial failure from
successful-record unregister, and main-thread AEGP reentry from unsupported
worker calls. Historical crash stacks corroborate scan/ML symbols only; Effect
Manager restart is a product signal. Product/native gate policies are retained.
Preliminary MEE reader symbol locations gathered before the scope change are
private leads; no body tracing or live suite mapping occurred. Further READ
research is deferred by the user's text-only scope. DOCFIX-01–03 documentation
DONE:167 local links/table shapes/diff PASS,241 non-Markdown and373 other source
files unchanged. Local full executable regression NOT RUN; prior CI/scanner remain
historical. Exact publication/CI state and checks in
`/private/tmp/aehl-reader-route-d6u09f1y`; owned evidence retained, no deletion.
Adapter unbound,
implementation/trials BLOCKED, registry/apply/render NOT RUN. C1 remains research.

## External research — previous packet

Research/documentation from clean ecc6c28; exact SDK25.6_61, pinned guide and
original-author sources reconcile14 claims from independent reports. Public late
publication is unsupported in reviewed sources; universal impossibility is not
proved. Add plugin-owned threads/deferred callbacks to coverage; AEXCompat's
Windows substitute-host evidence is not native AE2025 arm64 acceptance.
[Full audit and dependency order](C1_WEB_RESEARCH_RECONCILIATION_2026-10-03.md).
Next bounded original-file work: startup callback context/receiver owners, outer
dispatch/admission callers and full per-record error/unwind inverse. Preserve
existing captures rather than repeat unchanged Pause/Flush/SUS/PICA research.
Calibration requires safe instrumentation/current authority; late and fault trials
require the technical safety prerequisites first. External suggested operations
are not authority to execute them. NET-01–05 documentation research DONE;164 local
links/diff PASS,241 non-Markdown/seven SDK sources unchanged; raw scanner1 reviewed
as the unchanged CLI false positive, no suppression. Exact publication/CI results
and source checks retained in `/private/tmp/aehl-web-research-9wj5i8wr`.
Local full executable regression NOT RUN for these Markdown changes; old CI is
historical. Owned snapshot/receipts retained, no cleanup removal needed.
Product PARTIAL, adapter unbound, trials BLOCKED, registry/apply/render NOT RUN.

## Suspend contexts — previous packet

[SUS checkpoint](C1_SUSPEND_CONTEXTS_2026-10-03.md),12 accepted steps from
clean45a7aa4.27 complete original U bodies/3788 instructions: current-context TLS
transfer and callback-local Gate, per-context weak activation owners, termination
flag without worker join. Fixed collector/refusals,4 helper/79 collector focused
PASS;494 Python/no skips,62 Node/all22 steps PASS at exact tested/pushed
b01ae48ea8ee56a1994940933f8e327dd6902e94,376 source-byte proof. Independent47
scalar/5 pointer/2 owner-slot/4 import-ordinal and12 historical archive/pin checks
PASS; SDK/Apple layouts unchanged. BEE stage scopers actually use U_RenderContext
GetCurrent/GetState; initial direct suspend-context linkage corrected. Raw
scanner1/review_required,253 text/123 unsupported/no omissions,9 checks completed;
local CLI false positive reviewed without suppression. Owned scanner clone
removed after proof; captures/corrections/history retained in
suspend-closeout-b01ae48-xmz2dk8k and original folder. Both exact-source
CI37153356616/37153356615 completed/success; synthetic checks are not AE proof or
release approval. Five Markdown closure records with241 non-Markdown files
unchanged; final source/remote/retention receipt. Packet **PARTIAL:
4 DONE /5 PARTIAL /3 BLOCKED**,01/07/08/09 DONE,02–06 PARTIAL,10–12 BLOCKED.
Native safety contracts
remain UNKNOWN: continuous all-registry-consumer/MFR admission/drain, safe retained
factory acquisition/private ABI/thread and whole-effect inverse. Adapter/trials
BLOCKED, registration/apply/render NOT RUN; no speculative private invocation.
Original product/all gates retained; preserve all original evidence/corrections.

## Concrete executor — previous packet

[EXE checkpoint](C1_CONCRETE_EXECUTOR_2026-10-03.md),12-block packet closed as
**PARTIAL:3 DONE /6 PARTIAL /3 BLOCKED**,01/08/09 DONE,02–07 PARTIAL,
10–12 BLOCKED / NOT RUN. Exact clean tested/pushed code
9921ab0df7ee20d601854821431cf1aedc45d66b.
23 complete original bodies /24 windows /5901 instructions /14 rebases.
Concrete ThreadedWorkQueue identified; Pause is a Gate close, Flush has distinct
same-executor/marker/sync/join paths, Death destroys subsystem state. Notification
and completion retain callbacks/items and transfer removal to housekeeper.
All-reader/MFR admission, safe initial factory/thread/private ABI and full inverse
remain required; actual adapter/trials BLOCKED, registration/apply/render NOT RUN.
10 parser/5 executor/78 collector focused,489 full Python/no skips,62 Node/all22
steps PASS;373 Git/working/scanner/runner source-byte proof. Independent original
5901-instruction/32-field/14-rebase review and11 historical archive/pin checks
PASS; SDK/Apple layouts unchanged. Raw scanner1/review_required,250 text/123
unsupported/no omissions,9 completed checks; one local CLI false positive manually
reviewed without suppression. Both exact-source CI37152252624/37152252660
completed/success; synthetic checks are not AE proof or release acceptance.
Private receipts executor-closeout-9921ab0-of5lojlu, original captures/corrections
and history retained; only proven fresh owned scanner checkout removed.
Five Markdown closure records with239 non-Markdown files unchanged from tested
source; final remote/source/retention receipt. Keep backend unbound and original
product/all gates; next requires safe factory receiver/private ABI/thread,
continuous all-consumer/MFR admission/drain and whole-effect recovery contract.
No destructive lifecycle call or unchanged scan can establish those contracts.

## BEE queue controls — previous continuation

Exact clean tested/pushed code a24d8a2f5d0b06234d839005f36cc44749f0478f;
[QUE checkpoint and reconciliation](C1_WORKQUEUE_CONTROLS_2026-10-03.md).
BEE exact offline pin/UUID/nlist,14 complete bodies /2546 instructions.
Cancel/Pause/Resume act on one ID; flag and terminal stage differ. Eager completion
transfers retained callbacks/RemoveItem through an indirect executor. Add/Execute
remain separate new-work paths. Actual executor/notify/worker/thread graph UNKNOWN;
no caller-held all-registry-reader/MFR admission/drain barrier. Safe initial factory
acquisition/private ABI/thread and whole-effect inverse remain required. Backend
unbound, actual adapter/trials BLOCKED, registration/apply/render NOT RUN.

8 parser/77 collector focused,481 full Python/no skips,62 Node/all22 steps PASS;
370 tracked source-byte proof. Independent14-window/2546-instruction/25-field review
and10 historical archive/pin rechecks PASS. Raw scanner1/review_required preserved:
247 text123 unsupported/no omissions, one CLI false positive reviewed without
suppression. Research CI37149834498 /macOS CI37149834507 completed/success at exact
a24d8a2; build/synthetic package checks are not AE proof. Packet PARTIAL:
3 DONE /5 PARTIAL /3 BLOCKED. Private evidence queue-closeout-a24d8a2-lgfwcf2f;
only fresh owned scanner clone removed. Docs-only closeout proves all non-Markdown
source unchanged. Original product/A/B/C1/C2/D/release and historical evidence retained.

Further work needs an actual admission/owner/recovery contract. Do not promote
cancel return, item pause/stage/map erasure, idle, zero-counter, loader visibility
or owned mocks to universal host safety. No unchanged scan or speculative foreign
call/teardown. QUE-09–11 require the unresolved actual prerequisites, then current
safe disposable environment; prior user authority does not prove those contracts.

## Scoped controls and corrected match-name dependency — previous continuation

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
