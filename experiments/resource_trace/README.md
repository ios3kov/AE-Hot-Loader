# Resource-first correlation preparation

## Initializer patterns and cross-exec identity

`python3 -m experiments.resource_trace.fsref_initializer /absolute/fresh/output`
builds an owned actual-system initializer control. Five prefills, two alignment
classes, same-content A/B, serial address reuse and a failed URL are observed.
`--sanitizers` selects ASan/UBSan. Independent exec comparators check both file
identities with both creation orders. A wrong identity is retained as an observed
counterexample, never admitted for AE. Return-window refusals are MODEL_ONLY.
No debugger/AE operation or new capture admission. See
[initializer checkpoint](../../docs/C1_FSREF_INITIALIZER_2026-10-10.md).

## FSRef between processes and through the owned debugger

`fsref_ipc.py /absolute/fresh/output` builds an owned Carbon emitter/comparator;
each is initialized through exec. A's reference is accepted and a different file
with identical bytes is rejected. `--sanitizers` enables ASan/UBSan.

`python3 -m experiments.resource_trace.fsref_debug` additionally requires clean
source and launches only its own fixture through LLDB. An actual nested twin
read and actual C++ unwind validate scope separation; a modified captured journal
must refuse cross-invocation correlation. Only typed initialized own spans and
A's copy are captured. No expression/attach/Adobe operation. Process/debugger
timeouts preserve the unknown outcome for attention instead of killing it.

The later initializer controls expose creation-order-dependent wrong matches;
raw FSRef IPC is BLOCKED as a source selector. These earlier controls establish
only the exercised own process behavior, not permission or
lifetime for ASL's stack output. [Checkpoint](../../docs/C1_FSREF_IPC_2026-10-10.md).

## Source identity controls

`source_anchor.py` builds two owned native controls: a cooperative child with real
kernel fd metadata, actual dup2 and same-inode mutation refusals; and an own-file
FSRef copied-value/twin comparison. Neither launches AE nor reads target memory.
The receipt binds the actual source/binary hashes and exact expected refusal.
These are source-identity controls, not an Adobe capture profile. See
[producer contract](../../docs/C1_SOURCE_ANCHOR_2026-10-10.md) for the selected
ASL Carbon fork path and why its fork reference is not a POSIX fd.

```sh
python3 experiments/resource_trace/source_anchor.py /absolute/fresh/private/output
```

This is the first implementation boundary of the resource-first collector,
separate from the metadata-entry collector in `../startup_trace`. It does not
modify that collector's strict identity equality, sites or transport admission.

`core.py` accepts only `AEHL-RESOURCE-FIXTURE-2 / owned-fixture` transcripts.
It correlates ten ordered events: producer, PiPL model, getter, copied descriptor
name, writer, index, writer return, reader start, retained lookup, reader return.
One run/PID/main-thread token is fixed; input bytes and compiled module digests
are fixed. Owner/object/source-name/target-name/routine tokens remain distinct.
The copied inline name must use different storage, and the reader must copy into
another output buffer. Name equality alone cannot join unrelated descriptors.
Mismatch, replay, unexpected identity, malformed values or budget exhaustion
causes terminal refusal. Missing events leave INCOMPLETE; writer failure leaves
failure recovery UNKNOWN. Accepted input dictionaries are frozen copies.

The selected index arithmetic (writer slot + 703 = key; reader index = slot + 1)
comes from the pinned original-file research, not a public SDK contract. The8192
fixture limit is a diagnostic bound, not an AE capacity claim. Names are restricted
to a short own ASCII nonce; this is not a general UTF/name normalization algorithm.

`fixture.cpp` performs real owned file reads, name parsing/copying, allocations,
shared ownership, vector/name-map insertion and retained lookup. Its23-byte
`eMNA:<own nonce>\0` format and C++ classes are explicitly **models**, not valid
Adobe PiPL structures or FCSpec/Boost ABI. The thread1 token and initial owner
token are model identities, not an independently verified OS main thread or
Adobe control block. Bundle/legacy/cache origins are injected labels to test
provenance discrimination; the fixture does not implement Adobe's producers.
Cache-labelled bytes never become evidence of a current resource read.

`fixture.py` builds only this standalone executable. Execution requires the
exact binary/source hashes registered by the current build; unknown copied
executables refuse before launch. Each run has fresh resource and receipt files;
the executable returns normally without a debugger. Input hashes are checked
before/after and process exit is observed. A timeout retains process identity for
attention, with no automatic kill. No AE executable, install, private function,
memory access, Apply/render, cache/preferences change or old process attach.

Run contract and native controls:

```text
python3 -m unittest discover -s tests -p test_resource_trace.py -v
python3 -m experiments.resource_trace.fixture
```

The second command retains binary, own inputs and receipts in a fresh private
`build-ae-hot-loader/resource-fixture-*` directory. Three labelled producer
controls and alias/writer-failure/changed-owner/changed-output controls have
independent expected results. A PASS establishes only this owned model.

## Remaining admission dependencies

A completed model transcript is deliberately rejected by the existing AE
debugger transport gate. It must not be renamed into a real transport proof.
No actual resource-first LLDB collector or AE profile is admitted here.

Before live use, identify and independently validate exact sites/registers for
the actual resource producer, its return scope and ordinary receiver/type;
establish bounded borrowed-object/name reads and ownership of each backing span;
bind the resource-only candidate and reader sentinel without metadata entry;
verify the actual collector's stop budgets, main-thread/PID/birth/image checks,
own-object selection, detach and lifecycle on an owned debugger fixture. Then a
known-good **startup** observation may prove the continuous own PiPL→FCSpec→
writer→public key relation. Legal late context, full reader/lifetime coverage,
partial failure and post-launch registration remain separate unproved gates.

## Actual owned debugger transport

`python3 -m experiments.resource_trace.debug_fixture` builds a clean-source private
arm64 fixture with one exact NOP probe, then uses a dedicated LLDB listener. It
reads only the probe's immutable wire buffer while that call is stopped, checking
PID/birth/executable, OS main-thread assertion, UUID/file PC, backing extent,
non-executable readable mapping and stop before/after access. No expressions,
attach, broad memory search or Adobe target. Bytes are copied immediately.
`--fault alias` / `writer-failure` / `wrong-owner` / `read-name` exercise correlation
refusal; `--bad-extent` refuses a4097-byte request before process-memory access.
Cleanup removes its breakpoint, detaches without killing, then independently
checks fixture absence. Ambiguous cleanup retains the debugger for attention.

The actual transport receipt is separate from standalone model receipts. It can
validate fixture capture, not Adobe ABI, string backing/lifetime, resource/cache
provenance, installed keys or late registration. The old metadata collector and
its admission are unchanged; this collector cannot admit AE at all.
LLDB API references: [SBProcess](https://lldb.llvm.org/python_api/lldb.SBProcess.html)
and [SBMemoryRegionInfo](https://lldb.llvm.org/python_api/lldb.SBMemoryRegionInfo.html).

Schema2 adds a fixture constructor-generation witness. Cross-reader controls use
a separate same-name descriptor/registry; ABA controls end and reconstruct the
same object type at exactly the same address, preserving name/routine/owner
tokens but changing generation. Both must refuse before joining the reader.
Generation is instrumented fixture evidence, not an inferred Adobe lifetime.
Old schema1 receipts remain historical and are not reinterpreted as schema2.
