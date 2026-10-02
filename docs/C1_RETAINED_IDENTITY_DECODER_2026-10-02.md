# C1 retained-record identity decoder — owned buffers

Stage C1, Development. Baseline clean research HEAD
`ce6d5a6c9fcce3ff4b3b9294455574e4c3f9cac8`.
AE-Development-Rules 6.0.0 / `bb8b769404ddd5b97462812a4e6b430e8bfefe13`,
AI_ENTRYPOINT, PROCESS identity/evidence/regression, ENGINEERING debugging/API
sources and TOOLS apply. NATIVE governs the later Critical host integration;
this change is portable offline research code. No product contract change.
The consumed diagnostic authority does not cover another live capture.

## Objective and acceptance

The [live diagnostic](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md) captured seven
retained records' count, without bodies or names. Prepare a decoder for future
owned copies, preserving raw identity fields and names without calling or
dereferencing anything. Actual live identities remain NOT RUN.

| Requirement | Observable acceptance |
|---|---|
| RID-001: bounded exact input | Explicit layout; at most eight 0xb0-byte records; exact payload size; overflow/unsupported-layout refusal. No truncation. |
| RID-002: explicit name-copy inventory | Inline names up to 22 bytes; external names up to 255 bytes plus NUL; exact index/address/size/terminator; no missing, extra or duplicate copies; overlapping copies agree byte-for-byte. |
| RID-003: lossless diagnostic interpretation | Keep order and duplicates, opaque integer fields, raw marker and name bytes, including non-UTF-8/embedded NUL. Results own their name bytes. No symbol/provider or filename attribution. |
| RID-004: no host authority or gate conversion | No Reader, host access, pointer conversion, callable function, record invocation, provider retention or ResourcePassGate eligibility. Native helper/profile untouched. |
| RID-005: source-bound evidence | Strict C++17 focused regression, complete available clean-source regression, bounded static review, exact-source CI and documentation closeout. |

## Pinned layout interpretation

Source: [MEE ownership review](C1_MEE_OWNERSHIP_REVIEW_2026-10-02.md), its
source-bound ownership report SHA-256
`c8d92041ac586f34b4a1cd2293458f20052ff3a0528e6111075687590f4373b5`,
and the complete saved MEE scan/callback windows. MEE file SHA-256
`18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344`,
UUID `74a30dbaa08b367bbd9915d6d77e9d52`, AE 25.6x101 arm64.

The scan addresses 0x3723c/0x37240/0x37244/0x37300 distinguish name destination
+0x90, signed string tag and external pointer/length copy. Callback addresses
0x37838/0x3783c/0x37840 distinguish inline/negative-tag external storage;
0x37868 loads external length +0x98 and 0x37874 loads pointer +0x90.
This is a file-derived interpretation of this layout, not a portable standard
library ABI. The 22-byte inline cap follows the 24-byte storage minus tag and
terminator. External capacity representation is deliberately opaque.

| Record offset | Diagnostic interpretation |
|---|---|
| +0 / +8 | Descriptor / retained control integer words |
| +0x10 | Opaque state/refcon word |
| +0x58 / +0x80 | Teardown / finish address words, never converted or invoked |
| +0x90 | Inline raw name bytes, or external address word |
| +0x98 | External name length word |
| +0xa7 | Nonnegative inline length; high-bit tag selects external storage |
| +0xa8 | Raw preparation marker, not a safety flag |

The caller selects `Layout::Mee256Arm64`; that enum is not a runtime identity
check. A future adapter must independently establish the pinned provider before
selecting it. No encoding or per-plugin ownership semantics are assumed.

## Implementation and refusal behavior

`experiments/ordinary_discovery/RetainedRecordIdentity.hpp` consumes immutable
caller-owned `Bytes`. `Plan` validates record bounds/name representation and
returns only integer-indexed bounded name-copy requests. `Decode` requires exact
caller-supplied `NameCopy` inventory and rejects incoherent overlaps. It reads
little-endian words by byte assembly, never by C++ host-object casts. Inputs
cannot be mutated concurrently; the API has no callbacks or reader that could
retarget them during decoding. The output owns its raw name bytes.

Maximum input is 1,408 record bytes and eight 256-byte name copies. Empty records,
empty names and duplicate/aliased identities are preserved. Invalid count, layout,
size, range, string termination or copy binding throws before any result is
returned. No partial/complete-observation or eligibility flag is emitted.

38 nested native cases cover RID-001–004: strict bounds, raw little-endian fields,
empty/maximal names, encoding preservation, reversed external-copy order,
duplicate records, shared/overlapping names and conflicting-copy refusals.
The Python wrapper compiles with C++17 and warnings as errors, runs owned
fixtures, and requires zero host/record calls. Focused suite PASS. Full clean
regression/static review/CI are pending at this preparation checkpoint.

## Remaining diagnostic contract

This decoder alone does not make a new live candidate reviewable or establish
seven actual names. Before any new host operation, prepare and verify:

1. New independently identified one-shot helper/journal/supervisor, with exact
   source, artifact hashes and consumed-attempt behavior; old observer unchanged.
2. Exact runtime process/provider identity and vector/record/name readable ranges,
   mapped-read budgets, overflow limits and count refusal. Mapping alone is not
   allocator ownership or lifetime proof.
3. Bounded matching vector, record and name captures with rechecked root/count,
   exact inventory and refusal on mutations; no retry or private function calls.
4. Independent archive verification binding all copied data to the selected
   layout, PID/start, provider and capture. Raw addresses/data remain private.
5. Separate actual operation authority and fresh clean/idle project preflight.

Names would remain diagnostic labels until tied to descriptor/provider identity;
even successful name capture would not prove repeat initialization safe. Current
ResourcePassGate retains the zero-record requirement. C0 PASS; ordinary effect
registration/apply/render NOT RUN; release BLOCKED. PIN comparator/global
synchronization, lifetime, repeat behavior and Stage C2 remain open.
