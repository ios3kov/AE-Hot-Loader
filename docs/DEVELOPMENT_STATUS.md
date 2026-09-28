# AE Hot Loader — current development status

Updated: 2026-09-28. Working branch: `research/ordinary-plugin-discovery`.
The branch head identifies current development; verified builds have separate
commit/artifact/evidence identities.

## Latest verified build

- Source: `2e272035802dfbc5b1b9a285e69339786c64944d`.
- Build ID: `native-36474593472-1`.
- Full macOS [run #238](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36474593472): SUCCESS.
- Research [run #4](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36474593395): SUCCESS.
- Internal package built, signed and verified; not approved for installation/release.
- This status is a documentation-only successor. The retained package still
  belongs to `2e27203`, not to a later documentation commit.
- `main` unchanged; no Release or user installation performed.

Full identities, hashes, logs and limitations:
[CI_CHECKPOINT_2e27203](CI_CHECKPOINT_2e27203.md).
The previous [dated status](DEVELOPMENT_STATUS_2026-09-28.md) and
[panel checkpoint](CI_CHECKPOINT_f274961.md) remain historical evidence.

## Implemented

The panel compares `app.effects` match names before dispatch and after the
matching reply, instead of treating loaded-module counts as registration.
It preserves partial errors and checks protocol/I/O failure paths. A timeout
means an unknown result, not cancellation. Apply/render is not checked by the
panel. Direct bridge consumers must still verify registration separately from
the unchanged Agent's `success` response.

The existing full macOS build pipeline now runs for research branches. It
retains native shell tests and adds 14 manifest tests, clean-source/toolchain
records, per-file package SHA-256, final ZIP checksum and extraction/signature
verification. The source export was independently matched to its Git tree.
The host registration code and private ABI were not changed.

Current docs separate build evidence from live-AE and historical shell claims.
Historical evidence under `docs/archive/` is unchanged.

## Verification matrix for source 2e27203

| Check | Status | Scope / limitation |
|---|---|---|
| Panel host-mock regression | PASS: 22/22 | Actual JSX under Node, not AE |
| Manifest unit tests | PASS: 14/14 | Integrity, inventory, identity and path rejection |
| Rust/C++ static checks and command parsing | PASS | No user installation |
| Full native build, ad-hoc signing and packaging | PASS | macOS arm64 CI, not release approval |
| Standalone native smoke/negative gates | PASS: 7/7 | Shell tests outside AE; not ordinary discovery or AE MFR |
| Final ZIP and 24 payload hashes | PASS | CI roundtrip and independent download verification |
| Updated panel/Agent in real AE | BLOCKED | No accessible AE runtime in this session |
| RSMB controlled cold-start/apply/render | NOT RUN | Historical late-registration FAIL unchanged |
| Full adapter-specific reference/fixture cleanup | NOT RUN | Generic shell and research preserved |
| Release / installation / merge to main | NOT RUN | No candidate approved for handoff |

## Remaining work

Freeze dependency lockfiles; generate verifiable runtime identities; complete
scope cleanup. Establish controlled RSMB startup/apply/render evidence and
isolate missing legacy late registration. Run real panel/Agent, repeated-scan,
timeout/ownership and project-safety gates before handoff. Follow
[PRODUCTION_PLAN](PRODUCTION_PLAN.md); do not invoke unverified private
teardown/reinitialization functions or turn mock tests into live-AE PASS.
