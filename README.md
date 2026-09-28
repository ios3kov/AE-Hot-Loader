# AE Hot Loader

Research-stage ScriptUI panel and native Agent for discovering newly installed
After Effects effects without restarting AE. This is **not yet a universal
third-party plug-in loader or a release-approved product**.

Current development state: [DEVELOPMENT_STATUS](docs/DEVELOPMENT_STATUS.md).
Next gates: [PRODUCTION_PLAN](docs/PRODUCTION_PLAN.md).
Development requirements: [AGENTS](AGENTS.md).

## Current workflow

`Window → AE Hot Loader → Reload Plugins`

The current Agent scans plug-in roots through the version-gated native loader.
The panel snapshots installed effect **match names** before dispatch and after
the matching reply. It reports observed registry additions, an unchanged
registry, or errors. A loaded-binary count is not registration evidence, and
registry presence is not proof that the effect applies or renders.

The panel does not apply effects, modify the project or purge caches.

```text
ScriptUI panel → AEGP Agent → ML::LoadPlugins
                              + FLT_NotifyFilterLoadingDone
              ← reply + independent app.effects comparison
```

## Evidence and limits

| Area | Status and exact scope |
|---|---|
| Historical ordinary discovery | One modern probe registered, applied and rendered in AE 25.6.0 arm64 without restart |
| Historical paired registration test | Dynamic-entrypoint fixture registered; PiPL-only fixture did not; no apply/render test in that pair |
| RSMB | Late registration FAIL; controlled cold-start and subsequent apply/render NOT RUN |
| Current panel | 22/22 automated host-mock tests PASS; updated JSX not yet tested inside AE |
| Native checks | C++ arm64 syntax and root zsh script parsing PASS; not a full build or runtime gate |
| Compatibility | Only AE 25.6.0/macOS Apple Silicon is the research target; other configurations unverified |

Historical native results are recorded in
[the original status snapshot](docs/DEVELOPMENT_STATUS_2026-09-28.md) and
[the paired test](docs/TEST_REGISTRATION_PAIR_2026-09-28.md).
The new panel evidence is [recorded separately](docs/CI_CHECKPOINT_f274961.md).
Old AE results must not be presented as verification of the updated panel.

## Separate Control Shell work

The repository also retains a generic stable-shell/implementation architecture.
Its historical control test demonstrated implementation A→B→C, busy-render
rejection and rollback without AE restart. This requires a prepared shell and
does not prove support for arbitrary ordinary plug-ins.

The **current research panel request invokes ordinary discovery, not shell
implementation reload**. Shell integration and automatic cache refresh must
be treated as separate work. The generic [shell ABI](docs/SHELL_ABI.md) remains
available; prior adapter-specific plans are historical, not current readiness
claims.

## Development checks

```sh
node --test tests/panel.test.cjs
```

This runs the shipped JSX under mocked host/file APIs, not under ExtendScript
or After Effects. GitHub research checks also run arm64 C++ syntax checks and
parse the root command scripts on macOS. The workflow records source hashes
and uploads test reports. It does not install anything or publish a release.

The latest checked source is identified in
[the CI checkpoint](docs/CI_CHECKPOINT_f274961.md). Full native build/signing,
clean-install verification and applicable real-AE regression remain required
before distributing a new package. Existing installation helpers are not
proof that a new package has passed that gate.

## Historical documentation

The previous [README](docs/archive/README_6037df8.md),
[production plan](docs/archive/PRODUCTION_PLAN_6037df8.md) and
[code audit](docs/archive/CODE_AUDIT_2026-09-28_6037df8.md) are retained verbatim
from `6037df8`. Their historical claims and relative links belong to that
snapshot, not the current scope. They are not release approvals.
