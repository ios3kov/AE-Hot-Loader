# C1 PIN cleanup — bounded file review

Stage C1, Development, critical native research under AE Development Rules 6.0.0.
This is independent file-only work following the
[successful authorized diagnostic](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md).
It changes neither native adapters nor a runtime registration profile.

## Question and reviewed source

The first archived callback target, interpreted using the captured PIN image
slide, matches the current local PIN file's `PINp_CleanupFunc` at VM `0x113c94`.
PIN's loaded UUID/content was not captured, so this remains file attribution,
not complete runtime-provider identity proof.

Reviewed PIN file SHA-256:
`63c1fc4869b0d440d98bb5b1ce7931f07f70f494685b32ea9afdafecd4e72210`;
file UUID `11A71CEB-5A06-3FB7-92C7-0037233B101B`, arm64,
read/execute `__TEXT` VM range `[0, 0x224000)`.

The smallest useful bounded question is whether this cleanup entrypoint is inert
or reaches a host state operation. File inspection finds:

1. `[0x113c94, 0x113c98)`: one tail branch into `PINp_SortModules`.
2. `[0x113c98, 0x113d7c)`: 57 decoded instructions through the next exact defined
   text symbol. It reads the global `PINp_G` range, calls an introsort over
   `PIN_ModuleInfo` with `PINp_ModCompareFunc`, and has error/exception paths.

This establishes a global sorting path in that exact file. It does not establish
the comparator's full effects, allocation ownership, synchronization, safe repeat
behavior or quiescence. No callback was executed by this review.

## Reproducible collector and refusal contract

`experiments/ordinary_discovery/collect_pin_cleanup.py` fixes the exact file,
hash, UUID, executable text mapping and two windows. It requires a clean source,
checks file identity before and after collection, exact ordered symbol boundaries,
complete decoded address coverage, and 11 structural anchors including the
cleanup branch, global-range read, introsort call and return/unwind paths.
No arbitrary input path/window, process attach/launch or dependent-image loading
is enabled. Existing shared bounded tool/ZIP helpers are reused.

The private source-bound report retains scripts, metadata, selected symbols,
disassembly and an independently self-checked hash inventory. Runtime-provider
identity and lifetime/quiescence are explicitly NOT PROVEN in its record.
Production native profile and all existing live artifacts remain unchanged.

Five focused tests PASS: shifted/missing/duplicate/unexpected symbol boundaries,
wrong/ambiguous UUID or text protection/range, truncated/duplicate/undecoded
cleanup windows, changed tail target, complete-but-wrong sort instructions and
an unreviewed window are refused. Existing independently captured local file
windows also pass the collector's complete coverage/structural checks.
Full clean-source regression and collected report are pending at this preparation
checkpoint; append their exact identities after execution.

## Remaining gate

The live diagnostic's seven retained MEE general-plugin records remain a concrete
ResourcePassGate blocker. This PIN review does not clear them or prove complete
cleanup. Do not relax zero-record acceptance, call setdown, replace callbacks or
repeat startup. Next review retained-state ownership/lifetime and PIN comparator/
synchronization semantics from files before designing another live question.
Additional live authority is not inferred from the consumed diagnostic scope.
Registration/apply/render and release remain blocked; C0 remains PASS.
