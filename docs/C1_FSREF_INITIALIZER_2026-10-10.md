# C1 — initializer patterns, stale output and cross-exec identity

Rules v11.1.0 / 04b606845e0f73ab28b9807bb45682eae4d6ce34.
Baseline fac21240f9e84ccc5017e8e0fb0351e4056a29ed, clean research branch.
Follows [owned FSRef IPC](C1_FSREF_IPC_2026-10-10.md). Development-only own
micro-helper, no AE/debugger launch, installation, expression, private call,
foreign memory read or project/preferences change. C1 PARTIAL / C2 NOT_RUN.

## Acceptance

| ID | Observable requirement | Scope / status |
| --- | --- | --- |
| IN01 | Real CFURLGetFSRef: five fully initialized prefills, alignment classes 0/8 mod16, A/B same-content distinct-inode files, two repetitions | PASS_OWNED_ONLY on clean a67341a, ordinary and ASan/UBSan |
| IN02 | Same owned output address reused for three successful A calls and one nonexistent-file call; preserve Boolean and bytes independently | PASS_OWNED_ONLY on clean a67341a, ordinary and ASan/UBSan |
| IN03 | Reject stale generation, missing entry/return, failed call, expired scope and duplicate capture; accept legitimate repeated successful calls | 9 pure model tests + 1 actual native test passed; final regression receipt separate |
| IN04 | Separate-process comparison in both directions and A→B / B→A creation orders, identical loaded system image UUIDs | FAIL_FOR_SOURCE_SELECTOR on both clean native runs; observations retained |
| IN05 | Warnings-as-errors, ordinary and ASan/UBSan execution, applicable regression, separate critical review, exact source/Evidence/publication | Native/compiler/review complete; exact final regression/CI/archive receipt separate |
| IN06 | Decide natural AE output admission without substituting own results for live frame/initializer/source identity | BLOCKED; source selector and AE frame pairing not established |

## Experiment and interpretation

The new `fsref_initializer.cpp` uses the actual system function on initialized
own storage, with canary bytes outside the exact 80-byte extent. No uninitialized
or AE bytes are read. The matrix covers 40 calls; four serial calls reuse one
address (three A successes and one failure). These are wrapper-labelled own
generations, not observed entry/return tokens or a live AE frame contract.

The controller independently checks the prefill matrix, output/status widths,
guards, source/binary/input hashes, and compares each of the 43 successful
outputs in independently exec-initialized processes. Ordered comparison creates
both references in AB or BA order. Legacy comparison creates only the expected
reference, preserving the previous test's narrower scenario. Failed output is
never passed to File Manager unless it is byte-identical to the prior known-valid
A prefill; that diagnostic comparison cannot authorize a failed invocation.

`ReturnWindow` is a terminal-refusal **serial own protocol model**. Its generation
numbers are explicitly supplied by the wrapper. It does not observe an AE entry,
return, unwind or reentrant stack. Previous nested/unwind controls remain separate.

Identical opaque bytes across tested prefills are a bounded observation, not
proof of every byte's write coverage or canonical representation. Different
representations would also be recorded rather than treated as semantic failure.
No raw FSRef field is decoded into an inode, pointer or private cache identifier.

## New discrepancy and supersession

Both clean a67341a runs (and development attempt 2): all 40 successful matrix outputs have the correct semantic
identity within their producer; outputs are identical within each file/alignment
group across prefills. The failed URL call returns false and retains prior valid
A bytes. Both facts require invocation/normal-return gating.

Cross-exec comparison is **not admitted as a file selector**: of 86 ordered
comparisons, 43 have the wrong identity; the legacy comparator falsely accepts
23 A snapshots against B. Actual producer files have distinct device/inode
identities and identical content. A's snapshot can therefore be accepted as B
in an independently initialized comparison process. Creation-order dependence
is observed; its internal cause remains UNKNOWN.

The previous FI01 receipts remain historical PASS for their exact A-first
scenario; they do not prove symmetric or initialization-order-independent IPC.
Any inference that FI01 establishes an adequate source selector is superseded
by this counterexample. Do not rewrite old receipts as failures or silently seed
matching orders to make this new negative control disappear. Actual AE output
capture remains BLOCKED even if initializer prefills all agree.

The first focused test refused INDEPENDENT_IDENTITY. Its temporary files were
removed by the test fixture; full per-call raw evidence from that first test is
unavailable. A retained attempt 1 reproduces the discrepancy with native output,
compiled binaries and independent comparison receipts. Attempt 2 adds both
creation orders and retains all observations. These dirty-source attempts are
development evidence only; final clean-source receipts are recorded separately.

## Authority and remaining questions

Local Apple SDK: CFURL.h marks CFURLGetFSRef deprecated with “Not supported”;
Files.h defines FSRef as opaque `hidden[80]`, align1, and declares FSCompareFSRefs.
Loaded image UUIDs from the own executable:
CoreFoundation 9b6727627b1f30bc96def176b372d66d;
CarbonCore d884af5b23f7313a97eddd54518ba922.
These are own-runtime identities, not an AE-loaded-image observation or a hash
of independently read shared-cache code. Apple docs describe FSRef as opaque
and warn about APFS/32-bit inode limitations; they do not explain this observed
comparison discrepancy: https://developer.apple.com/documentation/coreservices/fsref

Next: find a file-identity anchor observable in the natural producer before
payload capture that does not depend on opaque cross-process FSRef comparison.
Candidates need exact API/site/input/output/lifetime contracts and their own
negative controls. No unverified private getter, target expression or raw FSRef
layout assumption is authorized by this checkpoint. Actual ASL producer→fork→
allocation→read→PluginSupport copy and writer→installed key remain UNKNOWN.

Private Evidence: `build-ae-hot-loader/fsref-initializer-2026-10-10-fac2124`.
Final native/controller source: a67341a74681d93229b1679d77b1c75eda6c823f.
Ordinary producer PID68748 and ASan/UBSan PID68749 both exit0, stderr empty;
each has 40 matrix + 4 reuse calls, 43 successful outputs, 86 ordered comparisons,
43 wrong BA identities and 23 legacy wrong twin matches. Source/binary/input
pins and identical system image UUIDs verified. All own compiler warnings are
errors; legacy deprecation suppression is local to the intentional control.
Apple system code is not sanitizer-instrumented; write coverage, races and AE
behavior are not certified. Separate final review corrects the IPC assumption,
validates the five actual prefills and preserves future native-test error files.
Original collectors/native helpers remain byte-identical to baseline.
Exact final documentation candidate, regression/CI and archive receipts remain
separate; a docs-only commit does not rerun or relabel these actual native runs.
