# Locked dependencies and loaded Agent identity — 2026-09-28

Baseline branch head: `0ae66042dc262b35af4daa25bdd37ebf0229f1a9`.
Prior verified native source: `2e272035802dfbc5b1b9a285e69339786c64944d`,
run 36474593472 / build `native-36474593472-1`.
Shared rules reviewed: FSTR-Line `DEVELOPMENT_RULES.md`, blob
`a1760fde8763f789b50b91c20407938b4fcaea4a`.

## Scope and acceptance defined before the change

1. Track the exact two Cargo locks retained by the verified native build;
   no dependency version upgrades, manual checksum edits or ABI changes.
2. Generate Agent identity from actual Git HEAD, clean/dirty state, target,
   version, build ID and dependency-lock SHA-256. Unknown/foreign source must
   not claim a valid clean identity; dirty experiments cannot pass CI.
3. Expose metadata of the loaded Agent and its image path through bounded
   C exports. Null/short buffers must fail, never return truncated success.
4. Add a read-only bridge query, preserving protocol v1 and ordinary discovery.
5. Run generator tests, locked native builds, real dylib getter checks and the
   existing full native/synthetic gates. Keep live-AE verification separate.

## Dependency baseline

`core/Cargo.lock` and `agent/Cargo.lock` are copied byte-for-byte from verified
artifact 10992941543 (run 36474593472). Archive SHA-256:
`573f0d02b8274688e56f993e96644447305c9a58c34d3c5adc7b757b30669937`.
Core blob: `c3fa99358f53cbc303c4908104798f64d2dafc68`.
Agent blob: `fbc4786328dfebc67319fc2023ae4f9b1f4647fe`.
The new locked-build job explicitly uses `--locked` for both crates. The
existing full-package workflow also checks Git diffs after the build, so an
unexpected edit to the now-tracked locks fails that gate. Rust remains 1.98.1.
No intentionally changed schema/state/runtime ABI or algorithm is introduced.

## Agent diagnostics

`agent/build.rs` invokes `tools/agent_build_identity.py` (Python 3 + Git required).
Metadata is compiled into Agent constants, not read back from the installed
file. It contains the actual checked-out commit and package build ID; the old
`ordinary-discovery-v1` string is retained as loader-path identity only.

- `AEHotLoader_AgentBuildIdentity(char*, size_t)` returns complete JSON.
- `AEHotLoader_AgentImagePath(char*, size_t)` resolves the currently loaded
  image using `dladdr` on a hidden, non-interposable function in that image.
- Both return 0 for success, -1 for invalid buffer, -2 for insufficient space;
  image lookup can return -3. Output is emptied on a short non-null buffer.
- Callers own the writable buffer and its valid capacity.
- `command=get_build_identity` returns metadata through the existing bridge;
  it returns before native discovery, without accessing the project.
- Every reply includes `agent_build_id`, `agent_git_commit`,
  `agent_source_clean`, `agent_target`, `agent_version`. Existing v1 clients
  can ignore these additional fields. The panel does not yet display them.
- Startup logging includes immutable metadata. Full local image paths are not
  added to normal replies/logs; the path getter is for explicit diagnostics.

Clean Git checkouts are required by default. For an internal dirty experiment,
`AEHL_ALLOW_DIRTY=1` is permitted outside CI and metadata says `source_clean=false`.
Git-less source exports deliberately cannot invent a source identity. Generated
Python caches and native build directories are ignored; locks remain tracked.

## Verification scope

Local baseline: existing 22 panel tests and 14 manifest tests passed.
Generator: 14 tests passed in owned temporary Git repositories on Linux.
Remote native/identity/packaging gates: NOT RUN at this record's authoring;
record exact commit, run, artifact/hash and results in a separate checkpoint.
Real AE diagnostics request/startup/runtime binding: BLOCKED in this session,
which has no accessible AE process. A standalone dylib test is not an AE test.

The identity test never calls `EntryPointFunc` or a private loader. Its evidence
contains the exact signed test dylib, its SHA-256, read-back metadata/path and
generator test results. It does not approve any later rebuilt artifact.
The full-package build produces a separate build ID and package; do not confuse
that package with the identity-job library even at the same commit.

## Limits and next gate

This stage identifies the Agent only. Per-build shell/implementation/panel
identities, UI diagnostics display, bridge ownership, full scope cleanup and
controlled RSMB startup/apply/render tests remain open. No private registration
step, render code, user installation, main merge or release is changed here.

Sources:
- https://doc.rust-lang.org/cargo/commands/cargo-build.html#manifest-options
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/dladdr.3.html
