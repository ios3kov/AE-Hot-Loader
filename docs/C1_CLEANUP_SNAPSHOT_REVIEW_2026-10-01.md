# Stage C1: bounded cleanup snapshot preparation

Date: 2026-10-01. Branch: research/ordinary-plugin-discovery.
Baseline: 538bafac1f74d64db409e8fe2df16bccd7672acb.
Rules: b27f45467e0a9152fc82c1072438dfed07f0c36e, AI_ENTRYPOINT first;
PROCESS/API-SOURCE-001, ENGINEERING, NATIVE, TOOLS and WORKFLOW apply.
Existing Stage C product scope, Development gate. Memory-reader preparation is
Critical research; it is not a production ABI or permission to attach to AE.

## Contract and acceptance before implementation

Continues [lifecycle review](C1_REPEAT_PREPARATION_REVIEW_2026-10-01.md).
Prepare an isolated bounded sampler over an injected exact-byte reader, using
only the already recorded file-layout evidence. No AE adapter, automatic address
resolution, attach, host getter, callback invocation, installation or scan.
The scope supplies two independently reviewed root slots and explicit readable
regions; those are input constraints, not proof of allocation ownership.

- CS-001: freeze scope; reject invalid/overlapping/overflowing regions and roots
  before reading. Reject every derived read outside one supplied region.
- CS-002: follow default-sack slot → sack+0x10 → LIST handle → LIST header.
  Require recorded magic, signed nonnegative bounded count and 16-byte entries;
  capture ordered raw target/context pairs without invoking/dereferencing them.
  Missing sack/list/header is unavailable, never an empty observed list.
- CS-003: capture the MEE begin/end pair; validate alignment, order, record stride
  0xb0, bounded count and supplied storage range. Do not inspect retained records
  or invoke their procedures. A nonzero count remains ineligible for C1.
- CS-004: read the complete chain twice, compare every captured address and byte,
  reject any observed change, truncation, failure or exceeded budget. No retry.
- CS-005: report only matching captures, raw callback pairs and retained count.
  Do not produce CleanupObservation, an approval digest, an observed/complete
  attestation or an eligibility decision. Matching reads cannot detect ABA or
  prove an atomic snapshot, future stability, complete callbacks or host safety.
- CS-006: test valid/empty/nonempty snapshots, every trust-boundary rejection,
  root/header/payload/vector changes, exact reads, frozen inputs and budgets.
  On macOS arm64 also read owned fixture memory through existing ReadSelfMemory;
  no foreign process or Adobe library. Run unified regression and exact-code CI.

## Source and unknowns

Existing private evidence identifies LIST magic 0x00d00bee (32-bit), signed
32-bit count at +0x10, signed 32-bit item size at +0x18, payload at +0x48;
PLUG cleanup retrieves target/context as two 64-bit words; MEE advances records
by 0xb0 and loads begin/end together. See prior report for hashes and addressed
windows. No supported Adobe SDK API is added or invented.
LIST pin 72be8af3e75c5e119e94cd6747e6bbbc25ec04f7f11c6451a918d8dea979e791
remains static supplemental evidence, outside the nine-image live profile.

Actual root addresses, provider/resident identity, allocation bounds, relocation
and pointer representation, quiescence/lifetime protection and completeness
remain UNKNOWN/NOT OBSERVED. Dependent live/native resource integration remains
BLOCKED. The isolated sampler cannot satisfy the ResourcePassGate on its own.

## Implemented isolated sampler

CleanupSnapshot.hpp freezes input regions, caps each region at 2 MiB, total
scope at 8 MiB, callbacks at 256 and retained count at 8192. Every read is inside
one supplied region. At most twelve reader calls / 8448 bytes are needed for
both maximum-size captures (enforced ceilings: 12 / 16384). The synchronous
reader must separately enforce its time limit; this sampler cannot preempt it.
No retry or empty-on-error path exists. Null/unavailable LIST is refused.

Targets/context are raw words only, preserve ordering/duplicates, and are never
called or dereferenced. Target nonzero/alignment checks do not prove provider
identity or pointer validity. Nonzero retained count is recorded without reading
record bodies and must still block a later resource pass. Scope regions remain
caller-supplied constraints, not allocator ownership evidence.

Only two matching captures return; their raw frames remain available for a later
independent reviewer. No native reader/backend or eligibility conversion is
connected. In particular, observed/complete fields and the reviewed digest in
ResourcePassGate remain unpopulated by this sampler. ABA, torn-but-repeated
captures and mutation after return remain possible and explicitly unresolved.

## Verification

Focused local macOS arm64 test: PASS, 44 synthetic rejection/change cases plus
owned self-process buffer read and invalid-address refusal through existing
ReadSelfMemory. They are nested within one new Python test, not 44 additional
Python tests. Foreign processes and Adobe calls: zero.

Owned fixture sanitizer run: PASS, AddressSanitizer + UndefinedBehaviorSanitizer,
44 cases and owned self-read; no diagnostic. Initial bounded scanner inspected
244 supported text files, dirty baseline explicitly recorded, no omissions.
The sole heuristic candidate remains artifact_manifest.py:71 local-argparse
false positive; no suppression. This is not a full security audit.

Exact-clean-source unified regression and CI: NOT RUN before code checkpoint.
