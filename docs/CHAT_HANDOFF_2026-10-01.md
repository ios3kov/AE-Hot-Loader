# AE Hot Loader — chat handoff, 2026-10-01

Continue the existing work. Do not restart research or repeat the failed scan.
This is a documentation checkpoint, not a new native artifact or release.

## Exact starting point

- Repository: `ios3kov/AE-Hot-Loader`.
- Branch: `research/ordinary-plugin-discovery`; never change `main`.
- Pre-handoff branch head: `8abcbadc53dde2aa964ea6720459d7a090b0b006`.
- Last changed and CI-verified code: `9ea7bcf57fffee2382c6890459dca89201345395`.
- Stage: **C of A–D**. Registration, open A/B/D requirements and release gates remain incomplete.
- Goal: register an absent ordinary effect in a running AE process, then independently prove apply and render without restarting that process. This is not merely replacing a shell implementation.

Read [AGENTS](../AGENTS.md), the current [shared rules](https://github.com/ios3kov/FSTR-Line/blob/main/DEVELOPMENT_RULES.md), [DEVELOPMENT_STATUS](DEVELOPMENT_STATUS.md) and [PRODUCTION_PLAN](PRODUCTION_PLAN.md). The rules were rechecked at blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`. Read current remote versions before each significant stage; state the stage, scope and next check briefly.

## What exists in code

All paths below are under `experiments/ordinary_discovery/` unless specified:

- `ResourcePassGate.hpp`: bounded single-root transaction policy; its AE backend remains unbound.
- `ResourcePassJournal.hpp`: actual disk-backed one-shot claim, observations, call marker and final evidence. Real file/process tests exist.
- `DirectorySpecAdapter.hpp`, `SelfMemoryRead.hpp`, `HostIndirectResult_arm64.S`: create a directory specification, validate path roundtrip, release returned strings and dispose the owned specification once.
- `ResidentImageBinding.hpp`, `NativeDirectoryBinding.hpp`: exact resident-image/export verification and wiring; no arbitrary IPC-provided call address.
- `AE256DirectoryProfile.hpp`: pins for the received FILE/U/dvacore binaries.
- `ResidentDirectorySession.hpp`: retains up to three already-loaded provider references with RTLD_NOLOAD, then rebinds. Missing providers are not loaded as fallback.
- `tools/run_research_checks.py` and `RUN_OFFLINE_CHECKS.command`: one sequential offline run and one private ZIP; fail-closed with explicit platform skips. They do not run the full future live pipeline or product packaging.

The binding, retention and directory lifecycle have run on **three owned test libraries on macOS arm64**, not on Adobe providers. The adapter is no longer merely local: the previously delivered `1c0d7e3` patch was incorporated upstream as `ab5c1cb`; subsequent binding/retention changes are in the code checkpoint above. Do not reapply the old patch.

**Not connected:** separate inert-by-default no-scan AEGP, its real host observations, durable-journal wiring and external live supervisor. No approved runnable no-scan artifact exists. Existing scoped-discovery commands still call the old loader and must not be used as if the new path were connected.

At handoff, the accessible container contained uploaded archives, including the CI source snapshot, but no working Git checkout or newer no-scan implementation was found. This is not an inspection of the user's Mac. The preceding continuation recovered source; it did not establish a completed no-scan bridge.

## Research conclusions to preserve

The SDK 25.6 header/sample review did not establish a supported public ordinary-effect late-registration procedure. PF_REGISTER_EFFECT uses a host-supplied callback/context; AEGP_ApplyEffect needs an installed-effect key. PICA AddPlugin/AcquirePlugin availability and ordinary-effect publication remain unverified, not disproved. Do not redo this audit without new evidence.

Static analysis separates AELibrary loading from the earlier PLUG/FLT resource pass. The missing-resource-pass hypothesis is concrete but not runtime-proven. A library image in memory and loader return 1 are not registration success. Prior vector-element speculation was superseded; do not revive it without new evidence.

FILE/U/dvacore implementations are available and were analyzed; lack of those binaries is no longer the blocker. The identified string converter is ASCII-only; non-ASCII probe paths remain refused. FILE_Dispose can close/unload associated resources and must only receive our own newly created ordinary-directory specification in the no-scan probe. Never dispose a borrowed plugin object, pass null or retry uncertain release. The string destructor has a terminate path: exception handling cannot guarantee recovery from every native failure.

Provider references are intentionally retained until process exit, including partial acquisition failure. This changes loader reference counts and must be explicitly covered by future host-test approval. It is not a passive read or verified consent just because a Boolean is set.

PLUG_Search calls sack cleanup callbacks after enumeration. **One root does not constrain every cleanup side effect.** Review the installed callbacks and retained state before connecting the later resource pass; do not bypass them.

## Exact verified checks

The following results belong to code `9ea7bcf`, not to this documentation commit:

| Check | Result and scope |
|---|---|
| Unified macOS arm64 | 21 stages PASS; Python 238/238, Node 62/62, existing scoped guards 15 PASS |
| Unified Linux | 238 Python collected: 229 PASS and nine explicit platform skips; Node 62 PASS |
| Owned provider retention and directory lifecycle | PASS on macOS, including calls after original test references were closed; Adobe calls=0 |
| Research CI | Run `36824300893`, both jobs completed successfully |
| Full product macOS CI | Run `36824300983`, build/sign/package/smoke/archive checks completed successfully; not installed in AE |
| Full static-security audit | Not rerun; five earlier findings remain open |
| New live no-scan / registration / apply-render | NOT RUN |

Both CI job results were read again while saving this handoff. No tests were rerun for the documentation-only save; `[skip ci]` is intentional. Never relabel a code/file check as live AE evidence or add nested C++ cases again to the Python total.

[Research CI](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36824300893) · [macOS product CI](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36824300983).

## Last actual AE results — separate gates

| Gate | Retained result |
|---|---|
| Embedded late registration, AE 25.6x101 arm64 | **FAIL**: source `45de0c9`, Build ID `scoped-0b8c8f122e80`, fixture `88019a1a01a7`; 785 unchanged effect identities, target absent |
| RSMB startup-registered apply/render | **PASS**, earlier identified one-frame smoke, not late registration |
| RSMB late registration | **FAIL**, separate historical result |
| Dynamic fixture application | Earlier **PASS**; render not established by that gate |
| Flat-resource experiment | Earlier **FAIL/crash evidence** preserved |
| Current AE PID/project/loaded component identity | **NOT OBSERVED** at handoff |

The blank/clean/no-crash observation and research-module retirement belong to the historical scoped test. Do not assert them as current. The user's last reported Mac checkout was `ce5d80dcff1b2bb1324a42f227a9f79590fa25fd`; GitHub updates do not update that checkout. Recheck worktree changes, actual branch/HEAD and AE before any interaction; preserve local work.

## Next work, in order

1. Reconcile the research branch and continue from the existing reviewed components. Do not add more wrappers or unrelated tests instead of completing the integration.
2. Connect retention/binding + directory adapter + durable journal to a **separate inert-by-default no-scan AEGP** and bounded external supervisor. Use real SDK types, exact build/runtime identities and one fresh owned ASCII directory.
3. Run available SDK build, signing, inert-entry, error/timeout and unified regressions on that exact artifact. A model PASS is not its acceptance. Preserve evidence in one user-facing report where feasible.
4. Only after those gates, request separately specified host approval including private FILE calls, retained provider references, and any needed installation/restart. The first live probe does **not** register or scan plugins: create, roundtrip, single release; require fresh blank/clean/idle state and unchanged PID/start, project revision, complete registry and image list. Timeout/uncertainty stops, retains evidence and forbids automatic retry.
5. After no-scan success and PLUG cleanup/retention review, prepare one fresh embedded-fixture resource-registration experiment. Prove exact new match first, apply/render separately, then finish integration/stability and release gates.

The user wants **one launch and one ZIP**, not repeated ad-hoc terminal experiments. The offline half exists; do not claim all live phases are ready. A failing prerequisite must stop downstream risky phases.

## Permissions and stop conditions

Permission for the earlier installation and one restart is consumed. General instructions to continue or finish do not renew it. No new private host call, suite probe that may load code, installation, restart, debugger attachment or provider-reference mutation without its separate authorization and fresh baseline.

Never merge/release/change main; delete preferences/projects/third-party plugins; close or kill working AE; replay Birth/InitIterator/RequiredPreSearch; enumerate global plugin roots; replace callbacks or the cache predicate; clear caches; force notification; fabricate private objects; guess flags/offsets; unload code; reuse the consumed fixture/claim; or repeat the unchanged scan. Current work does not change the installed product loader.

## Evidence and source recovery

Key records: [U/dvacore](U_DVACORE_CONTRACT_2026-10-01.md), [resident binding](RESIDENT_DIRECTORY_BINDING_2026-09-30.md), [directory adapter](DIRECTORY_SPEC_ADAPTER_2026-09-30.md), [FILE](FILE_OBJECT_CONTRACT_2026-09-30.md), [SDK](SDK25_6_REGISTRATION_REVIEW_2026-09-30.md), [journal](RESOURCE_PASS_JOURNAL_2026-09-30.md), [resource design](SCOPED_RESOURCE_GATE_DESIGN_2026-09-30.md), [aelib](AELIB_RESOURCE_PASS_2026-09-30.md), [PLUG/FLT](PLUG_FLT_RESOURCE_REGISTRATION_2026-09-30.md), [actual scoped host](SCOPED_USER_HOST_2026-09-29.md), [RSMB smoke](RSMB_APPLY_RENDER_PASS_2026-09-29.md).

Private conversation inputs already supplied include SDK `ae25.6_61.64bit.AfterEffectsSDK.tar.zstd` and its ZIP form, original FILE, U/dvacore, PLUG/FLT, AfterFXLib and aelib archives, and earlier PluginSupport/MEE dumps. Source/analysis is available; do not ask for the entire application or recollect these files as a first step. In a new chat, use available attachments/Library and exact file references; do not assume an old sandbox path exists or that old download URLs remain usable. If a required original is actually unavailable, request only that specific existing archive; do not invent a new scan.

Portable prior review: `AEHL-U-dvacore-review-9ea7bcf.zip`, SHA-256 `5c9bb3503fedee0f11d0861c67801fb45055fbd7822f957cf57c765ba47b158a` (rehashed at handoff). Its manifest entries were also verified.

Code/evidence recovery: macOS artifact `11144995740` from run `36824300983` contains `source.tar.gz` for code `9ea7bcf`. Downloaded conversation copy `aehl-noscan-base-9ea7bcf.zip`, SHA-256 `6ca6e7bf34206446a3b057d3b527a93e5a7fb9170afb15bc6c633a42b2477abf`, rehashed at handoff. The name does not imply it implements the no-scan bridge. Prefer the current Git branch for source and documentation; this archive is historical evidence, not permission to overwrite newer files.

Adobe SDK, proprietary binaries, full raw dumps and private host logs stay out of public Git. This handoff only saves documentation; it does not mutate the user's Mac, installed components or settings.
