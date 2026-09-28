# Verified panel / packaged Agent checkpoint — 04fea70

Date: 2026-09-28. Source: `04fea7060c7ef7ebc4a315b5c39364850287e294`.
Build ID: `native-36483421984-1`.
Scope and predeclared acceptance: [iteration](ITERATION_PANEL_IDENTITY_2026-09-28.md).

## Runs and checks

- Full macOS build #243, [run 36483421984](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36483421984), attempt 1: SUCCESS.
- Native job [109134389378](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36483421984/job/109134389378): SUCCESS.
- Research checks #9, [run 36483422020](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36483422020), attempt 1: both jobs SUCCESS.

| Check | Result | Exact scope |
|---|---|---|
| Panel contract | PASS: 51/51 | Node host/file mocks, source with test identity |
| Exact unpacked panel contract | PASS: 51/51 | Unmodified generated JSX from final ZIP, expected commit/Build ID supplied independently |
| Python regression | PASS: 38/38 | 14 Agent identity, 14 manifest, 10 panel generation tests |
| Locked native builds | PASS | Three core variants and Agent, Rust/Cargo 1.98.1; tracked locks unchanged |
| Native static checks and script parsing | PASS | Existing checks retained |
| Standalone native shell gates | PASS: 7/7 | Reload/rollback, discovery, duplicates, synthetic busy call, invalid key/runtime ABI/string |
| Ad-hoc signing and final ZIP extraction | PASS | Signature verification before/after packaging; not notarization or installation |
| Exact packaged Agent getters | PASS: 2 getters / 16 calls | Loaded extracted Agent in standalone macOS process, no AE entrypoint called |
| Independent downloaded archive verification | PASS | Outer digests, inner ZIP, all 24 payload hashes and expected inventory |
| Downloaded generated JSX rerun | PASS: 51/51 | Linux Node 22.16.0 host mocks, not AE |
| Live panel / resident Agent / RSMB | NOT RUN | No accessible isolated After Effects runtime |

The packaged Agent test is now in the full-package job and tests that package's
Agent binary, not the separate identity-workflow library from older checkpoints.
The recorded native binary SHA-256 equals the Agent entry in the package manifest.
Its returned metadata matches the generated panel and package commit/Build ID.
The seven changed source files in the retained source export also matched the
locally tested files byte-for-byte.

Environment: macOS 15.7.9 arm64; Xcode 16.4 (16F6), SDK 15.5;
Apple Clang 17.0.0; Rust/Cargo 1.98.1; Node 22.23.2; Python 3.14.7.
Full details are retained in `build-environment.txt`.

## Immutable artifact identities

Internal package storage: [artifact 10997517015](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36483421984/artifacts/10997517015).
Outer artifact ZIP SHA-256:
`50b79f230ed3156b8a0f2c490b4fe37cc329a78ed1b4e99d0476b040196ee928`.
Inner `AEHotLoader-mac-arm64-shell-reload-v1.zip` SHA-256:
`807fc92ababeb5d9632d8a90073587356b41f101c9b0fc291f7d982274c8cb2c`.

Evidence storage: [artifact 10997112408](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36483421984/artifacts/10997112408).
Evidence ZIP SHA-256:
`0439d3b821845a77417a286107331f9b1ac147bb4ae5cebf60edc402dc150400`.
Both storage artifacts have 30-day retention. IDs and hashes are retained here;
rebuild/retest the pinned source if the archives expire.

Key payload SHA-256:

- Generated panel: `7476f58cf4c613770d180921f4e876a96a453cd67bcd7c0d7c377678f3a976e2`.
- Packaged Agent binary: `532985d9183eec0ca2e436cc9f891a61e4b3173930e3c653411ff1d2dc63c3b7`.
- Manifest: `e199e3648b8b8f110d33384b2d0076d4b2b7b1a55ed6695158e15b7374cc0b25`.

Evidence includes `packaged-agent-runtime.json`, `packaged-panel.tap`,
`panel.tap`, `python-tests.txt`, `artifact-manifest.json`, `package.sha256`,
both dependency locks, the build environment and source export.
The native report explicitly records `host_entrypoint_called=false` and
`live_ae_status=NOT RUN`. It is not evidence that AE loaded this build.

## Log review and limitations

One non-blocking action warning remains: the SHA-pinned Rust action rejects
the redundant `toolchain` input. Its [pinned source](https://github.com/dtolnay/rust-toolchain/blob/ce678459e9fc7500d337468f904b95f1b5c10b5e/action.yml)
hardcodes 1.98.1; the log and build record confirm that exact version was used.
Remove the redundant input in subsequent CI cleanup; do not claim a warning-free
workflow. Existing PlistBuddy Set/Add fallback and ad-hoc signature replacement
messages were followed by successful plist and signature verification.

No new native registration mechanism, real AE test, RSMB compatibility result,
installation or release approval is claimed. Cross-process bridge ownership,
multi-panel lifecycle and scan cancellation remain open. The following
Markdown-only status/protocol update does not relabel this retained artifact
or substitute its own commit for the tested source.
