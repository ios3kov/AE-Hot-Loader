# C1 read-only diagnostic — live PASS, registration remains blocked

Date: 2026-10-02. Stage C1, critical native/IPC research, Development under
AE-Development-Rules 6.0.0 / `bb8b769404ddd5b97462812a4e6b430e8bfefe13`.
This closes the exact authorized diagnostic question, not registration acceptance.

## Authority, preflight and identity

The user explicitly granted the concrete diagnostic scope with «разрешаю».
Initial preflight preserved an existing AE session and refused before installation.
After the user closed it, process absence was verified and the user separately
confirmed full AE exit. No application was terminated by the orchestration.
[The prior environment refusals](C1_DIAGNOSTIC_PREFLIGHT_BLOCKED_2026-10-02.md)
remain historical; this successful run supersedes that blocker.

- Clean repository HEAD at execution: `b3a8536f63d7ca9d680053173f8ae13dc2f7c254`.
- External supervisor source: `f4f84aa5a41fd86cc76ee2d702fe61e9b61d16e2`.
- Native candidate source: `7c983c5b5adfde0300f2370e5772ed757ab6b613`.
- Build: `observe-d548b007e316`.
- Run: `cleanup-observer-04b0a1783d0d4cb7bb17f9efe70f85aa`.
- Manifest SHA-256:
  `9f305a648b43a6569ccb70165169c2ed021d7977ddfbd9b84f3725d0bbdff100`.
- Native binary SHA-256:
  `cfbfa87038d2640a558ca0e30ca5c5d8b171aef8d8be4934f5c25f281950be56`.
- AE 25.6x101, arm64; PID `94174`, native start identity `1790959406.991820`.
- UTC execution: `2026-10-02T16:43:26.827903+00:00` to
  `2026-10-02T16:43:41.825479+00:00`.

Preflight rechecked clean source, unchanged reviewed supervisor/native sources,
exact candidate/installed payload inventory and signature, pinned host/providers,
fresh private evidence directories, unique absent install destination, and no AE.
Only the unique helper was installed; AE was launched once; exact ready/PID/start
identity was bound before publishing exactly one read-only request.

## Verified result

| Observation | Result |
|---|---|
| Diagnostic transaction and independent supervisor verification | PASS |
| Ordered cleanup callback pairs | 2, both contexts zero |
| Retained general-plugin records | 7 |
| Bounded copies | 20 calls, 496 bytes |
| Effect registry before/after | 785 / 785, exact equality |
| Project | Blank, unsaved, clean, idle; revision unchanged |
| PID/start/module and resident images | Unchanged |
| Lazy system images added | 0 |
| Private Adobe calls/provider retention/registration | NOT RUN |
| Retry/AE stop/project mutation | NOT RUN |

Unwrapped before/after snapshot payloads have the identical SHA-256:
`abc1b62ec1d7fcf1bf29b40ea3530a6ebdda1ca707f800ff179081b0892d8697`.
Journal envelopes have separate sequence metadata; equality here applies to the
snapshot payloads, not complete journal files.

Diagnostic report ZIP SHA-256:
`54976e137d928861a5cffd8288e4dccc10a3b347f95b766dab89f297554b16f4`.
Independent verification PASS: unique exact ZIP inventory, CRC, all ten archived
payload hashes, stripped activation environment/command, activation-token absence
in every archived file, and re-run native evidence verification. Private report
and raw addresses stay in the owned local evidence folder, not the public repo.

The supervisor's `installation_performed=false` / `ae_launch_performed=false`
describe that supervisor's own operations. The separately retained orchestration
record correctly records both as **true** for the combined authorized run.
Its SHA-256 is
`a41006db54705bbdc9f5ed4b43df7930c24a2bf75b94f32a8b816bee83a60fe1`;
executed private orchestration source SHA-256 is
`420cc6f8079cb938e09c64a1cb5e80fb3084e7f352e3a1a621143495c571b45d`.
These independently bind the installation/launch record outside the original ZIP.

## Bounded file-only callback attribution

Using only archived image path/slide and callback targets, then local provider
files (no new AE read or callback invocation):

- Second callback matches the pinned MEE file's exact symbol at VM `0x376ec`,
  `PluginCleanupFunc`. Its retained-state effects remain governed by the earlier
  [cleanup/lifecycle review](C1_RESOURCE_ABI_REVIEW_2026-10-01.md).
- First callback points into the archived PIN image range and matches the current
  local PIN file's exact symbol at VM `0x113c94`, `PINp_CleanupFunc`.
  File SHA-256 `63c1fc4869b0d440d98bb5b1ce7931f07f70f494685b32ea9afdafecd4e72210`,
  UUID `11A71CEB-5A06-3FB7-92C7-0037233B101B`.
  The target lies in the file's `__TEXT` range `[0, 0x224000)`.
  This is file-based attribution; PIN's loaded UUID/content was not separately
  captured by this diagnostic, so complete runtime PIN identity remains unproven.

File-only inspection of `[0x113c94, 0x113c98)` finds a tail branch to
`PINp_SortModules` at `0x113c98`. The complete next-symbol-bounded window through
`0x113d7c` reads `PINp_G` and calls an introsort over `PIN_ModuleInfo` with
`PINp_ModCompareFunc`, with exception/error return paths. This callback is not
an inert observer: the statically observed path sorts host global state.
Sorting/lifetime/thread/quiescence and comparator effects are not certified.
Private disassembly output hashes:
`7ea21915ec619b7288960d625b5be76e78b75294774bfa699b8afac638e266b8`
and `121bcc134ce2a2e35e697ee085ba5ed5d93a247138e3d516f9f52ee0cf86b3f5`.
No debugger attached, dependencies loaded or process executed during file review.

## Consequence and next work

The diagnostic succeeded and found a concrete **ineligible** baseline for the
current ResourcePassGate: retained general-plugin count is **7**, while the gate
requires zero plus a complete reviewed cleanup observation. Do not rewrite that
condition, clear records, replace callbacks, run setdown or replay startup.
This diagnostic does not manufacture `complete`, `observed` or an eligible digest.

The exact one-shot diagnostic authority/request are now consumed. AE and the
installed consumed/inert helper remain preserved; no automatic shutdown/removal.
Any additional live capture or private operation needs its own concrete scope.
Next independent work is a reproducible bounded PIN callback/file review and
the retained-state/lifetime contract. Native C1 backend remains NOT READY;
registration/apply/render NOT RUN. C0 remains PASS; historical late-registration
FAIL and release blockers remain. Publication permission persists after actual
mandatory gates pass.
