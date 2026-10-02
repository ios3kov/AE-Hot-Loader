# C1 retained identity capture — owned-chain preparation

Stage C1, Critical/Development. Baseline
`cd5e06af90ae640aa6913a1d8f6d16ed9ef2f3c6`; agreed research branch.
Rules 6.2.0 / `d966078a9e45fee7ec9ad14f211a9da753d64b8a`: AI_ENTRYPOINT,
Process scope/API/identity/baseline/regression/evidence/automation, Engineering
safety/test/reproducibility/compatibility, Tools and Native memory/host boundaries;
diagnostics/testing/IPC overlays. Product contract unchanged; no discovery/parity
task. [Compatibility scope](C1_COMPATIBILITY_2026-10-02.md) remains exact-build.

## Objective and acceptance

Prepare a separate one-shot capture core for the
[owned-buffer decoder](C1_RETAINED_IDENTITY_DECODER_2026-10-02.md). Copy bounded
records and external name payloads from an injected mapped-memory backend,
requiring matching data/mappings before exposing diagnostic identities.
This stage uses synthetic/owned allocations only. No new live host operation.

| Requirement | Observable acceptance |
|---|---|
| RIC-001: one attempt | Atomic claim before backend access. Success, invalid input, mismatch and copy error consume; competing caller performs no second capture. |
| RIC-002: bounded supported shape | Explicit pinned layout, aligned nonzero 16-byte root; 0–8 records of stride 0xb0; existing decoder name cap 255+NUL. No truncation/configurable expansion. |
| RIC-003: mapped and coherent copies | Existing Reader validates before/after mappings and exact sizes; repeated addresses retain mapping identity. Names may overlap each other only coherently, not record/root state. |
| RIC-004: no retarget/retry | Two captures, four root reads total. Compare second root before derived reads and second records before names; reject changed bytes/mapping without retry. |
| RIC-005: bounded evidence and isolation | At most 22 copy attempts / 6,976 bytes. Failure retains read provenance, no successful snapshot/decoded identities. No callback/private function/provider retention or eligibility conversion. |
| RIC-006: scoped verification | Strict C++17 synthetic negative cases and actual owned-self-memory smoke; full clean available regression/static review/exact-source CI. AE runtime remains NOT RUN. |

## Implementation and data ownership

`experiments/ordinary_discovery/RetainedIdentityCapture.hpp` is separate from
`CleanupObserver`, the consumed native observer and ResourcePassGate. Its only
entry takes layout/root by value and an explicitly supplied backend. The existing
`MappedMemoryRead::Reader` provides unchanged per-copy bounds/protection/query
checks; the new core imposes its tighter fixed total budget.

Each capture reads vector bounds, optional exact record block, then the decoder's
name-copy inventory and a matching vector recheck. The second capture must match
the first vector before reading its record address, and match record bytes before
deriving external name addresses. Every repeated address must retain mapping
metadata. Both captures independently decode/validate string termination and
overlap consistency. Successful output owns copied vector/records/name bytes and
ordered diagnostic identities. No externally supplied code/function is called
other than the injected reader backend's query/copy contract.

Maximum eight long names uses 4×16 root bytes + 2×1,408 record bytes + 16×256 name
bytes = 6,976 bytes / 22 copies. Empty vectors use four 16-byte root copies only;
an allocated empty vector does not trigger a record copy. Mapping checks perform
queries separately from copy accounting. Their own existing fixed depth bound
remains unchanged. Names exceeding the supported shape are refused, not clipped.

This is a matching-copy diagnostic, not atomic snapshot or allocator ownership
proof. A changing state can leave/return to the same bytes between observations.
No complete cleanup/lifetime/repeat safety claim is emitted. Root/provider
binding and operation authority remain caller prerequisites, not claims implied
by accepting an integer root. SelfBackend enforces the existing current-process,
main-thread read restriction; no foreign-process API is introduced.

## Preparation tests

Focused strict C++17/Python wrapper PASS: 46 nested synthetic cases, including
zero/seven/eight records, full budget boundary, inline/external/aliased names,
unknown layout, invalid vectors, root/state overlaps, excessive lengths,
unreadable/executable/short mappings, short/extra copies, root/record/name/mapping
changes, incoherent aliases, exceptions and consumed failure/success/concurrency.

Actual macOS arm64 owned heap test also PASS: one record with external name,
8 copies / 428 bytes, ordered raw name confirmed. Worker-thread read is refused
and consumes the attempt. Zero Adobe calls, callback invocations, foreign-process
reads or provider loads. Nested cases are not added to Python test count.
Clean-source full regression/static review/CI pending at this preparation record.

## Remaining path to a concrete host diagnostic

Next prepare independently verified snapshot serialization/journal and external
one-shot supervisor, then an exact inert native candidate with pinned resident
provider/root, SDK/header/source/Build ID/final hashes and refusal/inert checks.
Do not silently attach this core to the consumed observer or combine read budgets.
Prepare installation/rollback and exact validation packet before requesting its
separate operation authority. No installable candidate is handed off here.

Actual seven AE record names remain NOT RUN. A later real matching-copy PASS
would identify diagnostic labels only; descriptor/provider attribution and private
repeat/lifetime/quiescence still need evidence. Zero-record ResourcePassGate stays
unchanged. C0 PASS; registration/apply/render NOT RUN; release BLOCKED. No teardown,
startup replay, retained-reference clearing, broad scan or gate relaxation.
