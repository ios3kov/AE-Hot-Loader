# Stage C continuation: registration gap, offline only

Date: 2026-09-30. Review ID: `gap-review-20260930-626babcf`.
Continues checkpoint `ce5d80dcff1b2bb1324a42f227a9f79590fa25fd` on
`research/ordinary-plugin-discovery`; this is not a restarted research plan.
AGENTS.md and the shared DEVELOPMENT_RULES were read. Shared rules were
rechecked unchanged at blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Scope and acceptance

Explain what the existing source and recorded failed experiment establish,
add a read-only saved-evidence analyzer, exercise contradictory/malformed
inputs, and record CI independently. Do not change the production loader,
repeat the scan, install, attach a debugger, call private host functions,
restart AE, change main, merge or release.

The one installation/restart authorization described in
[the working-host record](SCOPED_USER_HOST_2026-09-29.md) is consumed.
It is not permission for another runtime experiment.

## Evidence available and unavailable

The branch head initially matched the supplied checkpoint. The runtime report,
tested loader source, earlier static-research reports and GitHub CI were read.
The working environment for this iteration is Linux, not the user's Mac.
The Mac repository, running AE process, exact PluginSupport image and original
private evidence files were not accessible. Library searches did not retrieve
the original logs. Their absence here is not evidence that they were deleted.

Consequently:

- Current AE PID, project state, installed/resident modules: **BLOCKED**.
- Rehashing/reanalyzing the actual retained native log and snapshots: **BLOCKED**.
- New offline disassembly of the exact Adobe image: **BLOCKED**.
- Any new live scan, apply/render, installation or restart: **NOT RUN**.

The historical statement that AE remained open and blank describes the
2026-09-29 postflight, not a fresh observation on 2026-09-30.

## Preserved runtime baseline

The latest registration gate remains **FAIL**:
source `45de0c91112805cfdbc7528bb5747b41b14f13a8`, research Build ID
`scoped-0b8c8f122e80`, embedded fixture `88019a1a01a7`, match name
`AEHL.Embedded.88019a1a01a7`. The record reports loader return 1, the fixture
image present, video modules 339 -> 339 with added_modules=0, all 785 effect
identities unchanged, target absent, project revision 1 unchanged. No crash
was observed. These are attributed to the existing report, not newly captured
or independently rehashed here. The native gate failed at postflight;
`research adapter stopped` is not proof that the AE process stopped.

Original evidence remains under
`build-ae-hot-loader/scoped-0b8c8f122e80/evidence/` on the user's host.
The historical record pins these SHA-256 values:

| Input | Recorded SHA-256 |
|---|---|
| Native loader log | `e9eefd0f8ddd73be00cebe3d7623255d20f2c85f70edcec8abe17887b85188df` |
| before.txt and after.txt, each | `4bac64f5d06aecb2cad76c9497552c234d78f0c85ed9316d09de6034dbf03749` |
| supervisor.json | `b21c4d66c9b8208545e2ee152bf8ce424148b7daa28afafcecef773a9791c5bd` |

[RSMB startup-registered apply/render PASS](RSMB_APPLY_RENDER_PASS_2026-09-29.md)
is retained separately from historical RSMB late-registration **FAIL**.
Neither is replaced by the embedded fixture or by synthetic analyzer tests.

## Source-derived localization, not a proven root cause

`agent/native/InternalLoader.cpp` is the same blob in the tested source and
checkpoint: `df64e125a984199e45cd777eef8c16a556ec393b`.

1. `NotifyNewVideoFilterModules` obtains the global video-module list and
   computes new interface identities. It returns immediately when the added
   vector is empty. Only a nonempty vector reaches
   `FLT_NotifyFilterLoadingDone`.
2. Therefore, conditional on the recorded added_modules=0 and identified
   source, **this wrapper skipped its notifier call**. This is a control-flow
   inference, not a captured trace of every internal AE call. The next
   discriminating boundary is why no new video-filter module was published
   before notification. Forcing notification with an empty list is not a fix.
3. The `ML::LoadPlugins` output vector is passed to the loader and its bounds
   are logged, but this wrapper does not otherwise consume its elements.
   **Hypothesis to investigate:** the normal startup caller may perform an
   additional classification/publication step. This is not established:
   `ML::LoadPlugins` itself could already do that work. Its return value and
   a vector byte span do not prove the element type, ownership or plugin count.
4. A dyld image or exported function address does not prove entrypoint
   invocation, successful PiPL parsing, module publication or registration.
   The line `ordinary registration complete` is emitted even with no new
   module, so it is not an acceptance signal.

Earlier [PiPL fallback](RESEARCH_PIPL_FALLBACK_2026-09-29.md) and
[dispatch](RESEARCH_PIPL_DISPATCH_2026-09-29.md) records establish static paths,
not valid parsed PiPL contents in this embedded live run. No missing-entrypoint,
byte-order, receiver-type or registry-insertion root cause is asserted here.
The historical flat-resource failure is not relabelled as fixed.

## Implementation and identity

Added `experiments/ordinary_discovery/analyze_registration_gap.py` in
`cdea7311a62cbe440190b25ca10c0f3c3aae7dc5`, then its synthetic regression suite
in `626babcf1c4bf6df25a0c2df9d0eb74c4e77a691`.
No native Build ID is assigned to this Python-only change.

| File | SHA-256 |
|---|---|
| analyze_registration_gap.py | `3cee23a69df8e79eede8f1c0d05b15d39eb5deffc8e8b3fb76d550832001d2c9` |
| tests/test_registration_gap.py | `f14c9a3a970ea08559ccf712ae48beafede0bbdcb3b25b82fbeadd27ba2a6d6f` |

Local tested bytes match remote Git blobs
`3bf2d78e3b6575fb9c02475ae9076efa8a8e9628` and
`7fe0ccb33e0657921f2a8d57f747e08fbf423793`, respectively.

The analyzer reads explicitly selected log/before/after files, each with an
expected SHA-256. It rejects links, nonregular/oversized/changed files,
replayed or ambiguous transactions, inconsistent notification records and
malformed snapshots. Registry comparisons preserve identity multiplicity.
It has no process/network/AE interface and writes only JSON to stdout.
Its report omits raw paths, addresses, tokens and registry names.

Exit 0 and analysis_status=PASS mean that supplied evidence was parsed, not
that registration passed. An exact registry-addition check is separate from
the live gate, which remains NOT RUN because acquisition provenance and
PID/start correlation are not established by these three inputs. Supplied
hashes identify bytes; they do not prove runtime provenance or source identity.
The source blob in the report identifies the interpretation model only.

CLI requires `--loader-log`, `--before`, `--after` and a matching
`--<input>-sha256` for each, plus `--scan-root`, `--fixture-image` and
`--fixture-match`. Use exact recorded paths from the retained experiment,
not guessed paths or a fresh scan. The command was not run on the original
private inputs in this iteration.

## Verification and CI

| Check | Result and scope |
|---|---|
| Focused analyzer tests | PASS, 43/43, synthetic Linux fixtures; all pass with Python warnings treated as errors |
| Python compilation | PASS for the two added files |
| Local tested bytes vs remote blobs | PASS |
| Research CI for 626babcf | PASS, run 36735169447; panel-contract and native-syntax jobs |
| Linux CI Python discovery | 151 collected: 147 passed, 4 macOS-only cases skipped; not 151 passes |
| Node CI | PASS, 51 panel + 11 snapshot tests, no AE |
| Full macOS CI for 626babcf | PASS, run 36735169446, completed 2026-09-30 15:17:23 UTC; not a live AE test |
| Earlier checkpoint ce5d80d CI | PASS: macOS #250 / 36567226143 and research #16 / 36567226034 |
| Full static-security audit | NOT RUN again; historical FAIL with five known findings remains recorded |
| Actual retained-log analysis / current AE | BLOCKED, original files and Mac host unavailable here |
| Corrective registration operation | BLOCKED, not demonstrated |

The four Linux skips concern macOS exclusive request publication, completion,
process-exit and timeout supervisor tests. They are not newly failing cases,
but are not PASS on Linux. The previous 15 native guards and three inert-entry
results remain historical unless tied to a newly inspected run.

CI evidence: [research run](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36735169447),
[macOS run](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36735169446).
The research job log was read. Its uploaded evidence artifact is
`11106497847`, SHA-256 reported by Actions:
`34ae98ac8c37a400acf7202ad5649ddf05a3a29b1613a556d715940770c02724`.
This is an upload-log hash, not an independently downloaded archive hash.
CI reports annotations (1 per research job, 2 for build); the connector rejected
the annotations endpoint. Annotation-level review is BLOCKED, not silently
cleared by green jobs. No warning-free or release-readiness claim is made.

Documentation-only follow-up commits use [skip ci]. The exact verified code
commit remains 626babcf; a documentation head is not a newly tested native
artifact. Nothing from the CI package is installed or handed over here.

## Next safe gate and stop condition

First regain read-only access to the original evidence and exact host image.
Fresh current-AE observation must precede any future host interaction; the old
blank-project report cannot authorize it. Do not run another scan to regenerate
missing evidence.

Then analyze the hash-pinned saved transaction and inspect offline the normal
startup consumer of `ML::LoadPlugins` output and the PiPL-to-video-module
creation/publication path. Establish whether output consumption, PiPL parsing,
classification or publication is actually absent; distinguish unobserved from
failed steps. Exact-image addresses are research references, never callable
production offsets.

Stop before any proposed corrective runtime operation until there is a specific
falsifiable hypothesis, bounded instrumentation, host/project identity guards
and separately authorized risky actions. Do not force notifier dispatch,
replay callbacks, construct private objects, guess flags or invoke teardown.
A future registration PASS still requires an exact new match in the same PID
with unchanged project state; apply/render is a separate gate. Stages A/B/D
and the release requirements in PRODUCTION_PLAN remain open.
