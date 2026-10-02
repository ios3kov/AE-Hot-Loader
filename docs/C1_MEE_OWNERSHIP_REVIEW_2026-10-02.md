# C1 MEE retained-state ownership — reproducible file review

Stage C1, Development. Baseline clean research HEAD
`ee0d6e1b4e65a8d5ab346d0fdf6a4d151638d8fc`.
AE-Development-Rules 6.0.0 / `bb8b769404ddd5b97462812a4e6b430e8bfefe13`,
AI_ENTRYPOINT, PROCESS identity/evidence/regression, ENGINEERING debugging/API
sources, NATIVE and TOOLS apply. Product scope is unchanged. The collector is
offline tooling; dependent private runtime integration remains Critical.
Existing one-shot diagnostic authority is consumed; no new AE action is included.

## Question and acceptance

The [live diagnostic](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md) found seven retained
records, but captured only vector bounds/count, not record bodies or module names.
This review asks who retains those records and which paths initialize, mutate,
finish or release their state in the pinned MEE file. It cannot identify all seven
live modules or certify repeated entrypoint invocation.

Acceptance: fixed hash-pinned windows, complete decoded coverage, reproducible
addressed checks for retention/state overwrite/callback/release/vector reset,
explicit file-only scope, independent report hashes, focused refusal tests,
clean-source available regression and exact-source CI. No scanner, private call,
provider retention, callback replay, setup/setdown execution or new installation.

## Reproducible tooling

The existing resource collector adds `--review ownership` without changing its
search/cleanup/lifecycle modes or native profiles. It selects only MEE, with the
previously reviewed SHA-256:
`18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344`.

```sh
python3 experiments/ordinary_discovery/collect_resource_search_abi.py --review ownership
```

Five complete windows cover 960 instructions and 61 addressed structural anchors:

| File window, end exclusive | Instructions | Anchors |
|---|---:|---:|
| SetupGeneralPluginScan, 0x36c58–0x36da4 | 83 | 9 |
| PluginScanFunc, 0x36da4–0x376ec | 594 | 13 |
| PluginCleanupFunc, 0x376ec–0x37a00 | 197 | 17 |
| CleanupGeneralPluginScan, 0x37eec–0x37f34 | 18 | 7 |
| SetdownGeneralPlugins, 0x37f34–0x38044 | 68 | 15 |

Structural checks fail on changed addressed operands/calls or incomplete,
duplicate, out-of-window or undecoded instructions. Complete decoded text alone
does not pass the ownership checks. Report fields retain actual record identity,
allocation/lifetime/quiescence and safe repeat invocation as NOT OBSERVED/PROVEN.
These are structural evidence checks, not executed Adobe branches or certification.

## Ownership/state interpretation

The setup, cleanup and finish windows resolve to the same MEE vector root VM
`0x10fd70`, with end at `0x10fd78`, matching the separately reviewed root metadata.
PC-relative address interpretation is file-based; no callable address is produced.

| Path | Static observed action | Consequence for this experiment |
|---|---|---|
| Scan append | Copies routine descriptor/control-block pair; increments retained control-block count; copies state/name; stores marker; advances end by 0xb0. Slow path is typed vector append. | Records are retained shared host state, not temporary folder-enumeration results. Exact per-record live ownership remains unknown. |
| PluginCleanupFunc | Iterates existing records; successful prep continues; marks +0xa8; zeros state range +0x10–+0x8f; invokes saved entrypoint with operation value 3 and state pointer. | A repeat pass can revisit and rewrite existing state. The operation's repeat contract is unproven for each actual plugin. |
| CleanupGeneralPluginScan | Invokes record+0x80 callback with record+0x10 state, advancing by 0xb0. | This finish path is not a demonstrated release of vector records; callback effects remain plugin-specific. |
| SetdownGeneralPlugins | Invokes record+0x58 callback; clears marker; unpreps; decrements shared control blocks and invokes virtual release paths; resets vector end. | Teardown can release retained state and affect code lifetime. It is not an authorized way to make this baseline eligible. |
| SetupGeneralPluginScan replay | Releases existing retained descriptors/name storage and resets vector end before installing scan callbacks. | Replaying setup can discard retained state. No isolation or idempotence is inferred. |

The `GeneralPlugin` stride is 0xb0. File instructions distinguish a descriptor/
control-block pair at +0/+8, mutable state at +0x10–+0x8f, name storage starting
at +0x90 and marker +0xa8. This is a bounded file-layout interpretation, not a
portable C++ ABI or permission to dereference an arbitrary live record/string.

The earlier [repeated-preparation review](C1_REPEAT_PREPARATION_REVIEW_2026-10-01.md)
already establishes that the prepped-success path does not suppress the saved
operation-3 invocation. This review makes the corresponding ownership/state
anchors reproducible; it does not retroactively change that evidence.

## Preparation verification and next discriminator

Focused collector suite PASS: 13 tests, including real file-backed inspection on
owned arm64 code/data. Existing saved MEE windows pass all 61 new anchors.
Full clean-source regression, source-bound collection and CI remain pending at
this preparation checkpoint; append exact results after execution.

Current ResourcePassGate still requires zero retained records and complete
reviewed cleanup. The actual seven-record baseline remains ineligible; no native
gate or profile was weakened. C0 stays PASS; registration/apply/render NOT RUN.

Next safe discriminator: prepare an owned-buffer retained-record identity/layout
decoder and a separately reviewed diagnostic contract that identifies actual
records without invoking them. Name/string, descriptor/provider identity, range/
allocation and mutation limits must be resolved before any new live candidate.
Also retain the PIN comparator/global synchronization question. Do not claim that
count seven identifies seven particular modules or proves safe lifecycle.
Additional live authority must target that concrete prepared diagnostic.

## Exact-source closeout

Code/test source **095a219253bf86bea82fa06fc00ac6c87e6f0b05**.
Actual ownership collection PASS: five complete windows / 960 instructions /
61 structural anchors. Private source-bound report SHA-256:
`c8d92041ac586f34b4a1cd2293458f20052ff3a0528e6111075687590f4373b5`.
Independent exact archive inventory/CRC/payload hashes PASS.

Default search mode compatibility PASS: 472 instructions; report SHA-256
`20ed121b26d7acd50c2f6c41aff42a1a6652bdd0aa551b3f6972a0de0107f2b0`.
Independent archive/hash verification PASS. No existing mode/profile changed.

Full clean local regression PASS: **310 Python/no skips, 62 Node, 22 stages**,
source unchanged after execution. Private regression report SHA-256
`30788e2df1c52fa0f8d7b443e9bd10f0a599b8d4ffb3bd904a8d70f71c4b6429`.
Independent archive inventory/payload hashes PASS. Research CI **37038542355**
and full macOS CI **37038542153** both verified completed/success at exact source
095a219253bf86bea82fa06fc00ac6c87e6f0b05. These build/offline checks are separate
from the historical live diagnostic; no new live operation occurred.

Bounded code-profile audit completed all selected checks: 294 supported text
files, no omissions. Raw exit 1/review_required retained for the sole previously
classified local argparse false-positive at tools/artifact_manifest.py:71.
Scope digest `db050ad8c5b8e7f8744a1a09337a0378521b07d7c20a7b9f6ce4678377aabcf5`;
private report SHA-256
`06a419090dc39294343b011210ef80a677660c9982142b90a85ad0cdd03797c3`.
This is not full security or release certification.

## Legacy general-plugin records and modern AEGP are distinct routes

The setup window installs first type `AEgp` (0x41456770) with PluginScanFunc /
PluginCleanupFunc, then `AEgx` (0x41456778) with AEgx_PluginScanFunc and a null
cleanup target. The GeneralPlugin retained vector and operation-3 callback path
must not be silently treated as the public modern AEGP initialization ABI.

Supplemental file-only inspection at the same clean source pins the same MEE
file and decodes the complete AEgx_PluginScanFunc window `[0x37a00, 0x37eec)`:
315 instructions. It calls MEE_GetGPList at 0x37ca4 and appends a distinct typed
`AEgxPluginLoadAtom` at 0x37cd8; the fast path advances that queue by eight bytes
(0x37cc4–0x37cc8). This separates the modern queue from GeneralPlugin's 0xb0
record route. It does not identify each of the seven actual captured records.
Private supplemental ZIP SHA-256:
`3fcec686ae6ecf3045725ac94d53e29d40325b8c6d21ae48c7a526beeb948145`;
independent archive/hash verification PASS. No function was invoked or attached.

The [AE SDK Guide entry-point contract](https://ae-plugins.docsforadobe.dev/aegps/implementation/)
describes modern AEGP initialization once during launch and subsequent messaging
through registered hooks. Its signature begins with SPBasicSuite*. That public
contract does not define the internal MEE operation-3 record protocol or establish
repeat safety for its actual entries. This distinction prevents transferring a
public AEGP lifecycle assumption to an unidentified legacy retained record.

Ownership-flow review is complete for this bounded file question. Actual record
identity, owned/borrowed object lifetime, complete cleanup, atomicity/quiescence,
PIN comparator/synchronization and safe repeat behavior remain open. The zero-
record gate and native helper bytes are unchanged. No release/merge/main update.
