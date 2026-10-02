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
