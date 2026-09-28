# Verified native research checkpoint — 2e27203

Date: 2026-09-28. Source commit:
`2e272035802dfbc5b1b9a285e69339786c64944d`.
Source tree: `cf9489b68c05b123148db96e9080c79fa49833ff`.
Build ID: `native-36474593472-1`. This is an internal build, not release approval.

Native [run #238, 36474593472, attempt 1](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36474593472)
completed **SUCCESS**, job `109104991459`.
Research [run #4, 36474593395](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36474593395)
also passed both jobs. The declared scope is in
[the iteration plan](ITERATION_NATIVE_GATE_2026-09-28.md); its pre-run record
is preserved rather than retroactively relabelled.

## Environment and source identity

The macOS job checked the exact commit, clean Git state and arm64 host before
building. Environment: macOS 15.7.9 arm64; Xcode 16.4 (16F6); macOS SDK 15.5;
Apple clang 17.0.0; Rust/Cargo 1.98.1; Node 22.23.2; Python 3.14.7.
Deployment target: macOS 11.0. This build target is not an AE compatibility claim.

## Performed checks

| Check | Result | Scope |
|---|---|---|
| Rust formatting, shell metadata/contract, native syntax | PASS | Existing checks retained |
| ScriptUI panel host mocks | PASS: 22/22 | Actual JSX under Node, not AE |
| Package manifest unit tests | PASS: 14/14 | Filesystem and identity checks |
| Default-v1, candidate-v2, candidate-v3, Agent and Control Shell builds | PASS | macOS arm64 compilation/linking |
| Bundle assembly, ad-hoc signing, plist/export/minimum-OS checks | PASS | Not notarization or trusted publisher signing |
| Seven standalone native smoke/negative gates | PASS | Details below; no AE process |
| Final ZIP extraction, manifest and signatures | PASS | 24 payload files; final ZIP unchanged |
| Downloaded archive and source verification | PASS | Independently rechecked in Linux container |
| Updated panel/Agent in real AE; RSMB startup/apply/render | NOT RUN | Runtime unavailable; no new host evidence |

The seven native gates, preserved from the existing pipeline, produced:

1. Bundled default -> candidate -> unchanged -> bundled rollback -> unchanged:
   return codes `0, 0, 1, 0, 1`.
2. Shell enumeration helper: one shell reloaded, then unchanged.
3. Duplicate shell keys: `-4203`, with zero shells reloaded.
4. Simulated in-flight call: `-4112`; after completion reload `0`, then unchanged `1`.
5. Wrong implementation key: `-4111`; previous valid implementation unchanged.
6. Runtime ABI mismatch: `-4116`; previous valid implementation unchanged.
7. Unterminated implementation label: `-4113`.

These run outside AE in owned runner directories. Shell helper discovery is
not ordinary-effect registration, and a simulated busy call is not an AE MFR
test. Native loader/registration implementation was not changed in this stage.

## Artifacts and independently checked hashes

[Internal artifact 10992694673](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36474593472/artifacts/10992694673):
`AEHotLoader-internal-2e272035802dfbc5b1b9a285e69339786c64944d-36474593472-1`.
The downloaded outer artifact ZIP has 779360 bytes and SHA-256:
`590ddcc503f805d529f38a27ede99a770be9f9fa37a5d2ab3bb0c652ab916527`.

Its inner `AEHotLoader-mac-arm64-shell-reload-v1.zip` has 789485 bytes and SHA-256:
`03a428fc78bee19524d7a492fe47d4be6c3498775cbe8e2188db9671e91e3b23`.
The legacy inner filename does not mean the current panel reloads shell
implementations. It invokes ordinary discovery; shell tests are separate.

[Evidence artifact 10992941543](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36474593472/artifacts/10992941543):
`native-evidence-2e272035802dfbc5b1b9a285e69339786c64944d-36474593472-1`.
The downloaded ZIP has 99827 bytes and SHA-256:
`573f0d02b8274688e56f993e96644447305c9a58c34d3c5adc7b757b30669937`.

It contains the source archive, build environment, panel TAP report, manifest
unit-test output, final package checksum, payload manifest and two generated
Cargo lockfiles. Both artifacts have 30-day retention; identities are retained
here, but expired full artifacts require a new identified build, not an assumed
recreation of these bytes.

After download, both outer hashes, the inner ZIP hash and every one of the
24 payload hashes were independently checked. The package manifest exactly
matched the evidence copy and the declared commit/Build ID. The exported source
was safely extracted and its Git tree recomputed: it matched the source tree
above. Signatures were checked on macOS by CI, not re-executed on Linux.

## Log review and limitations

No compiler warning was seen in the reviewed native job log. Two
`CFBundleExecutable Does Not Exist` messages came from the existing
`PlistBuddy Set || Add` fallback. The Add, plist lint and signature checks
succeeded. Signature replacement messages and the asserted negative-test
errors are expected outcomes, not unexamined failures.

Cargo lockfiles were generated and retained but are not yet committed;
dependency selection between future runs is not frozen. The Rust toolchain
action still uses its version ref; its resolved action SHA was
`ce678459e9fc7500d337468f904b95f1b5c10b5e`. No bitwise reproducibility is claimed.
The package Build ID and file hashes do not establish runtime identity inside
AE. The manifest correctly leaves `runtime_identity_verified=false`.

No installation, AE restart, user project change, GPU/render validation or
RSMB controlled cold-start occurred. RSMB late-registration remains FAIL in
historical evidence. Mandatory real-AE and release gates remain open.

## Documentation successor

The follow-up changes only README and current status/plan/evidence Markdown.
Its checks are relative-link validation, whitespace review and a Git file-list
comparison. `[skip ci]` avoids rebuilding unchanged native/test/CI sources
solely to record results; it is not a native PASS for the successor commit.
The retained package remains exactly the one built from `2e27203` and is not
modified. A future package including newer documentation needs a new identity
and applicable checks. No package is handed over for installation here.
