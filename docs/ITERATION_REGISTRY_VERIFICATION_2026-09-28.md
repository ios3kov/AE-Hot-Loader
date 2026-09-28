# Registry verification iteration — 2026-09-28

## Baseline and rules

Baseline: `6037df83cd65188866a40f2d22f13cb17d0fff36`, branch
`research/ordinary-plugin-discovery`; panel blob
`726a50f3127d1b14813b4bdd04c281a7a0743ec0`.
Rules: [FSTR-Line DEVELOPMENT_RULES](https://github.com/ios3kov/FSTR-Line/blob/main/DEVELOPMENT_RULES.md),
reviewed blob `a1760fde8763f789b50b91c20407938b4fcaea4a`.

Target: ScriptUI panel + existing Agent on AE 25.6.0 / macOS arm64.
The native loader, private ABI, installed bundles and user projects are unchanged.
The observed baseline defect is that the panel repeats an Agent message based
on loaded module counts without checking Installed Effects Registry identities.

## Acceptance criteria defined before implementation

- Copy `app.effects` match names before dispatch and after the matching reply.
- Loaded module counts alone must never imply registration or render success.
- Compare identities, not just counts; detect removals and duplicates.
- Preserve partial errors even when the registry grows.
- Reject unsupported replies; ignore old request IDs; timeouts mean unknown.
- Restore the UI on I/O errors; close opened files; do not publish failed writes.
- Reject repeated clicks while a request is pending.
- Read-only host integration: do not access or mutate `app.project`.
- Research branch pushes must run regression tests; no release/deploy actions.

## Implementation

`ui/AE Hot Loader.jsx` independently compares registry match names. It reports
only observed registry changes and explicitly leaves apply/render unverified.
No registry API or private lifecycle function was added to the Agent.
Agent protocol v1 is unchanged: its `success` remains a completed loader pass,
not proof of effect registration. Non-panel consumers must verify the registry.
The legacy backend label `new_effect_modules` in older reports must not be
interpreted as the number of newly registered effects.

`tests/panel.test.cjs` runs the actual JSX inside a Node VM with host/file mocks.
It is not an emulation of AE's renderer, ScriptUI engine or native ABI.
`.github/workflows/research-ci.yml` adds portable regression and macOS C++
syntax/installer parsing on research pushes, PRs and manual dispatch. It does
not replace the existing full macOS build or the real-AE release gate.

## Available evidence

The baseline panel was reconstructed byte-for-byte and verified against its
Git blob SHA before running the same tests.

| Check | Result | Scope |
|---|---|---|
| Baseline regression | FAIL: 18/22; 4/22 passed | Reproduces missing guards in host mocks |
| Updated panel regression | PASS: 22/22 | Node 22.16.0, Linux x86_64, host mocks only |
| Fresh GitHub CI | NOT RUN at authoring | Record the run for the resulting commit separately |
| Live ScriptUI + Agent registration | BLOCKED | No accessible AE process in this session |
| RSMB controlled cold-start/apply/render | NOT RUN | No change to the historical RSMB result |
| Render/GPU/performance profiling | N/A for this iteration | No render code changed; no speed claim |

Test logs identify each assertion. CI records commit, run/attempt, Node version
and SHA-256 of both the tested JSX and test runner. Reports are uploaded even
when tests fail. No installable build is being handed to the user here.

## Limitations and release gate

A registry delta is an observation, not proof that this scan caused every
change or that an effect can render. Repeated-panel lifecycle and cross-panel
IPC ownership are still separate open items. Timeout does not cancel the
native scan. No automatic purge, process termination or user-state cleanup is
introduced. The panel must be validated in real AE before release.

Full native build, signing, real AE interaction, clean installation, existing
project safety and applicable Level 2 regression remain mandatory before an
artifact is handed over. No merge to `main` or publication is authorized by
this iteration.

## Sources

- [Application.effects](https://ae-scripting.docsforadobe.dev/general/application/#appeffects)
  documents read-only installed-effect identities.
- [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
  documents branch filters, job permissions and triggers.
- Historical baseline: `DEVELOPMENT_STATUS_2026-09-28.md` and
  `TEST_REGISTRATION_PAIR_2026-09-28.md`; neither is reclassified as new evidence.
