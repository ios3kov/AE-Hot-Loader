# AE Hot Loader

Research-stage ScriptUI panel and native Agent for discovering newly installed
After Effects effects without restarting AE. This is **not yet a universal
third-party plug-in loader or a release-approved product**.

Current state: [DEVELOPMENT_STATUS](docs/DEVELOPMENT_STATUS.md).
Next gates: [PRODUCTION_PLAN](docs/PRODUCTION_PLAN.md).
Development requirements: [AGENTS](AGENTS.md).

## Current workflow

`Window → AE Hot Loader → Reload Plugins`

Every Reload first checks the resident Agent's compiled identity against the
panel's generated package identity. Missing or mismatched Build ID, commit,
clean state, target or version blocks the scan. **Diagnostics** performs only
that check and displays the observed builds; it does not scan or read the project.

After a valid handshake, the Agent scans plug-in roots through the version-gated
native loader. The panel copies installed effect **match names** immediately
before the scan and compares them after the matching, identity-checked reply.
It reports observed registry additions/removals, an unchanged registry or errors.
A loaded-binary count is not registration evidence; registry presence is not
proof that an effect applies or renders.

The panel does not apply effects, modify the project or purge caches. A scan
timeout does not cancel the Agent or prove that no work occurred.
Protocol details: [BRIDGE_PROTOCOL](docs/BRIDGE_PROTOCOL.md).

## Evidence and limits

| Area | Status and exact scope |
|---|---|
| Historical ordinary discovery | One modern probe registered, applied and rendered in AE 25.6.0 arm64 without restart |
| Historical paired registration test | Dynamic-entrypoint fixture registered; PiPL-only fixture did not; no apply/render test in that pair |
| RSMB | Late registration FAIL; controlled cold-start and subsequent apply/render NOT RUN |
| Current panel | 51/51 host-mock tests PASS, including tests of exact generated ZIP payload; not yet tested inside AE |
| Build/tooling | 38/38 Python tests, full macOS arm64 build/sign/package, 7/7 standalone native shell gates PASS |
| Packaged Agent identity | Exact extracted Agent's metadata/path getters PASS in standalone macOS process, not AE |
| Compatibility | Only AE 25.6.0/macOS Apple Silicon is the research target; other configurations unverified |

Current exact source, Build ID, hashes, log caveat and test evidence:
[CI_CHECKPOINT_04fea70](docs/CI_CHECKPOINT_04fea70.md).
Historical native results remain in
[the original status](docs/DEVELOPMENT_STATUS_2026-09-28.md) and
[the paired test](docs/TEST_REGISTRATION_PAIR_2026-09-28.md).
Old AE results must not be presented as verification of the updated panel.

## Separate Control Shell work

The generic stable-shell/implementation architecture is retained. Its historical
control test demonstrated implementation A→B→C, busy-render rejection and rollback
without AE restart. This requires a prepared shell and does not prove arbitrary
ordinary plug-in support. The current panel button invokes ordinary discovery,
not shell implementation reload. [Shell ABI](docs/SHELL_ABI.md).

## Development checks and generated panel

```sh
node --test tests/panel.test.cjs
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The repository JSX is an **unstamped source template**, intentionally unable to
scan. Packaging uses `tools/build_panel.py` to generate it from clean Git source
with the same package Build ID as the Agent. Do not install the raw template or
mix panel/Agent files from different packages. The generated file is tested again
after extracting the final ZIP, without modifying its embedded identity.

Both Cargo locks and Rust 1.98.1 are pinned. Full-package Cargo builds use
`--locked`; CI retains environment/source records, final archive and payload
hashes, signed-payload checks and exact packaged Agent identity reports.
These are development artifacts, not installation or release approvals.

Real AE clean-install/runtime identity, ScriptUI/Agent roundtrip, project safety,
repeat/timeout/ownership and applicable release regression remain mandatory.
Existing installation helpers do not imply that a new candidate passed them.

## Historical documentation

The previous [README](docs/archive/README_6037df8.md),
[production plan](docs/archive/PRODUCTION_PLAN_6037df8.md) and
[code audit](docs/archive/CODE_AUDIT_2026-09-28_6037df8.md) are retained verbatim
from `6037df8`. Their claims and relative links belong to that historical snapshot,
not current release approval.
