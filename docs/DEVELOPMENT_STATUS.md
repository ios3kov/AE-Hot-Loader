# AE Hot Loader — current development status

Updated: 2026-09-28. Branch: `research/ordinary-plugin-discovery`.
The branch head identifies current development; verified builds have separate
source, Build ID, artifact hash and evidence identities.

## Latest verified source

Source: `4357e36732f106233020fccd110c0e9f19a03a76`.

- Full macOS build **#240**, run 36478417321: SUCCESS;
  package Build ID `native-36478417321-1`.
- Agent identity **#2**, run 36478417282: SUCCESS;
  standalone library Build ID `identity-36478417282-1`.
- Research checks **#6**, run 36478417347: SUCCESS.

The two builds are different artifacts. The identity test library is not the
Agent binary from the full package. Exact identities and checks are recorded
in [CI_CHECKPOINT_4357e36](CI_CHECKPOINT_4357e36.md).
This status is a documentation-only successor; no tested artifact was modified.
No release approval, installation or merge to `main` was performed.

## Changes in this iteration

Both Cargo lockfiles are tracked, copied byte-for-byte from the previous
verified build; dependency versions and Rust 1.98.1 were not upgraded. A new
CI job builds both crates with `--locked` and verifies the locks stay unchanged.
The existing full-package job also passed its tracked-source diff checks.

Agent metadata is generated from actual Git HEAD, clean/dirty state, build ID,
target, version and the dependency-lock hash. Unknown source is rejected;
dirty experiments are explicitly marked and prohibited in CI. The loaded
Agent exposes bounded metadata and image-path getters. A read-only
`get_build_identity` bridge command returns before native discovery; every
reply includes Agent identity fields, and startup logging includes metadata.
See [BRIDGE_PROTOCOL](BRIDGE_PROTOCOL.md).

The current panel does not yet display or compare these new identity fields.
Its existing registry comparison remains unchanged. The native registration
path, private ABI, Control Shell and rendering code were not changed.

## Verification for source 4357e36

| Check | Status | Exact scope |
|---|---|---|
| Panel regression | PASS: 22/22 | Shipped JSX under Node host mocks, not AE |
| Package manifest tests | PASS: 14/14 | Inventory, hashes, identity and path rejection |
| Identity generator tests | PASS: 14/14 | Owned temporary Git repositories |
| Locked core and Agent builds | PASS | macOS arm64, unchanged tracked locks |
| Loaded Agent identity and image-path getters | PASS | 2 getters, 16 calls in standalone macOS process |
| Full native build, ad-hoc signing and packaging | PASS | Internal package, not release approval |
| Existing native shell gates | PASS: 7/7 | Standalone synthetic tests, not real AE/MFR |
| Downloaded archives and 24 package payload files | PASS | Independent hashes/inventory check |
| New bridge diagnostics and startup inside AE | BLOCKED | No accessible AE process in this session |
| Packaged Agent identity read-back inside AE | NOT RUN | Static embedded metadata is not runtime evidence |
| RSMB controlled cold-start/apply/render | NOT RUN | Historical late-registration FAIL remains |
| Full adapter-specific scope cleanup | NOT RUN | Generic shell and historical research preserved |

The first implementation had formatting/workflow failures, fixed before these
passing checks; their history is retained in
[CI_FIX_AGENT_IDENTITY](CI_FIX_AGENT_IDENTITY_2026-09-28.md).
Older AE results remain historical, not tests of this new Agent.

## Next gates

Integrate identity checks into the exact packaged Agent and diagnostic UI;
complete remaining component identities and scope cleanup. Prepare controlled
RSMB startup/apply/render tests, then isolate legacy late registration. Real
panel/Agent, repeat/timeout/IPC ownership and project-safety checks remain
required before handoff. No unverified private teardown or reinitialization.
