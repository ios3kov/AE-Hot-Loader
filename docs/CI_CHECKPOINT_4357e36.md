# Verified Agent identity checkpoint — 4357e36

Date: 2026-09-28. Source: `4357e36732f106233020fccd110c0e9f19a03a76`.
Source tree: `59fb7ba47d5311dc9c7b4e9dc64470150e37ef0b`.
This record describes the exact builds below, not a later rebuilt artifact.

## Standalone Agent identity — PASS

[Run 36478417282 / attempt 1](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36478417282),
job 109117807106; Build ID `identity-36478417282-1`.
Generator tests: 14/14 PASS. Both crates built with `--locked`; locks unchanged.
The actual ad-hoc-signed Agent dylib was loaded through ctypes on macOS arm64.
Both metadata and image-path getters passed eight calls each: null/zero/short
buffers, exact capacity and repeat stability. Read-back commit, clean state,
build ID, target, version and lock hash matched expectations. The image-path
getter resolved this loaded library. No AE entrypoint or private loader was
called. This is **not a live AE integration test**.

[Artifact 10995710483](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36478417282/artifacts/10995710483)
contains the tested dylib, `runtime.json` and `generator-tests.txt`.
Archive SHA-256:
`7ea5e5ded3dc0b15ed1a68eb111770cc6bb3e0140737c6c36832c02dd630105f`.
Tested dylib SHA-256:
`4619b1b03a592f7f306928585cb70b8331fe9eaeee2f5dc940b4ef9958f0ddf5`.
Downloaded archive, library hash and runtime record were independently checked.

## Full native package — PASS within CI scope

[macOS run #240 / 36478417321 / attempt 1](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36478417321),
job 109117807137; Build ID `native-36478417321-1`.
Environment: macOS 15.7.9 arm64, Rust/Cargo 1.98.1, Xcode 16.4,
macOS SDK 15.5, Node 22.23.2. No user installation was executed.

- Static checks, full core/Agent/Control Shell builds and ad-hoc signing: PASS.
- Panel host mocks: 22/22 PASS; manifest tests: 14/14 PASS.
- Seven retained standalone shell gates: PASS, including swaps/rollback,
  duplicate rejection, busy-call rejection, wrong key/runtime ABI and invalid
  ABI strings. These do not test ordinary discovery or real AE rendering/MFR.
- Final archive extraction, signatures and 24-file manifest verification: PASS.
- Tracked-source/lockfile diff checks: PASS.

[Package artifact 10994252267](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36478417321/artifacts/10994252267)
outer ZIP SHA-256:
`76eb6189bc14a8ac25c79c0d09e1d951e5ff4529dec1cf060587c6e3a97f32c5`.
Inner `AEHotLoader-mac-arm64-shell-reload-v1.zip` SHA-256:
`b699e29840cb1f0bcc37865a5ec3d6b67a33df703fe7ea76a15ce54a4194501b`.
Packaged Agent executable SHA-256:
`e89e5d62bbe2ceb479d87f5d20b993bea361f716ea74e4aef3604abfc417b4e8`.

[Evidence artifact 10994466829](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36478417321/artifacts/10994466829)
SHA-256:
`cf2994e66ec57ea7cae56d6ffd6d061b8341dafc345708330d0746005d25bc7f`.
It retains source archive, environment, locks, manifest, checksum and test logs.

Independent download verification confirmed both outer archives, inner ZIP,
all 24 payload hashes and exact inventory. The source archive's recomputed Git
tree matches the tree above. Embedded package Agent metadata matches the
package build ID and commit **by static inspection only**. Its getters were
not executed in the full-package job; the standalone identity job uses a
different binary. Neither result proves that AE loaded this package.

[Research run #6 / 36478417347](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36478417347)
also passed the panel and native-syntax checks for the same source.

## Dependency and failure history

Exact tracked locks came from the earlier verified run 36474593472:
core SHA-256 `17303a333b7cfb0f5883fd92e0d64db516885a5e200a4396e921996e15ccbcfc`;
Agent SHA-256 `be6a473fef9d5a0bff2f75413b2df77d8d8a3cb8b1e0de4292561447e7e90195`.
No dependency versions or lock checksums were edited.

Initial source `72dd50a` failed formatting in native run 36477934165 and
workflow validation in identity run 36477932628. The corrected source above
passed; the failures are preserved in
[the correction record](CI_FIX_AGENT_IDENTITY_2026-09-28.md).

Artifact retention is 30 days. IDs/hashes do not replace unavailable test logs;
repeat the appropriate tests if evidence expires. This documentation-only
successor changes no tested binary, source or workflow configuration.

## Not approved by these checks

Real AE diagnostics/registration/apply/render, user installation, GPU and
project-safety acceptance were not executed. RSMB late registration remains
unresolved. No release or merge to `main` is approved by this checkpoint.
