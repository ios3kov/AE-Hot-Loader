# Stage C1: bounded diagnostic cleanup observer

Baseline mapped reader code 6c666ca, resident binding code 0c4cd4c and sampler
6a758a8. Canonical rules b27f45467e0a9152fc82c1072438dfed07f0c36e;
AI_ENTRYPOINT/PROCESS/ENGINEERING/NATIVE/TOOLS/WORKFLOW apply. Critical native
research, Development gate. Product scope is unchanged.

## Contract before implementation

- CO-001: one-shot portable observer consumes its attempt before validation.
  Bootstrap the reviewed PLUG global slot → handle → sack → LIST handle →
  header/payload chain and MEE begin/end. Bound counts, alignment, exact spans,
  calls and bytes. Only merge overlapping/adjacent already approved spans;
  never authorize a whole heap region. Never read retained record bodies.
- CO-002: feed the existing double-capture sampler only clipped spans discovered
  through the checked reader. Bootstrap bytes must match first-capture frames;
  re-read the PLUG global afterward. Refuse changes, malformed input, mapping or
  copy failure without retry. Equal bytes cannot detect ABA or prove atomicity.
- CO-003: verify MEE record span mapping before/after sampling even though its
  bodies are not copied. Record diagnostic VM provenance, not allocation/lifetime
  ownership. A nonzero record count is a diagnostic result, never eligibility.
- CO-004: native wrapper freezes two reviewed root profiles, binds already resident
  exact paths/hash/UUID/header/text before/after, runs only on the main thread of
  its current process and checks the runtime image set. No provider load/retain,
  Adobe call, callback execution, teardown, scan or state modification.
- CO-005: diagnostic success/failure plus partial mapping records only. No complete,
  observed, approval, digest or ResourcePassGate conversion. Synthetic mutation,
  malformed chain, exhausted/consumed attempt and owned current-process chain
  tests; compile and sanitizer coverage. Actual AE roots remain NOT OBSERVED.

Kernel operations cannot be preempted by this synchronous observer. A concrete
live candidate still requires external supervision, exact artifact and process/
project identity, fresh scoped authority and safe host baseline. This component
alone is not a live-ready candidate or a registration backend.

## Verification

Focused local tests PASS: 27 nested synthetic cases plus actual owned two-library
root/heap-chain observation, absent provider, wrong thread and unavailable sack
refusals. Tests alone load/initialize/unload their fresh owned providers. The
observer never loads them. Ordered callback values and a nonzero retained record
count are preserved as diagnostic values; no callback invocation or record-body
copy. Bootstrap-change, double-capture-change, global-pointer/mapping-change,
malformed counts/strides/pointers, missing roots and consumed-attempt refusals PASS.

ASan/UBSan synthetic and actual owned resident chain runs PASS without diagnostics.
Code-profile scanner completed; only the known artifact_manifest.py:71 local
argparse false positive remains (exit 1 / review_required, not release approval).
Exact code/test source **1a4201c46202588a53aee25ea8d0ec1dd7dad079**.
Full clean-source local regression PASS: 290 Python without skips, 62 Node,
22 stages, unchanged inventory. Run 8d6a728493b9461bb82baa4649be2917; private
AEHL-checks-_fgikz72.zip SHA-256
`03513f9fb16bc44fb916c12b335f8fa3336ac159248dddf6046eec62df664e86`.
Exact ZIP inventory and all 24 payload hashes independently verified.
Research CI **36929802910 — PASS**; full macOS CI **36929802970 — PASS**.
Clean-source code scanner inventoried 258 supported files with no omissions;
sole known argparse candidate, exit 1/review_required retained.
At most 20 copies (24-reader limit), 12688 bytes for 256 callbacks (16384 limit),
4096-byte chunk limit; retained record containment adds two mapping queries only.
No AE memory read/private call/install/launch or ResourcePassGate integration.
