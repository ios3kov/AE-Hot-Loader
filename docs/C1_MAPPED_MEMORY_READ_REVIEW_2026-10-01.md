# Stage C1: current-process mapped memory reads

Baseline 09b3f7d (root binding source 0c4cd4c). Rules b27f45467e0a9152fc82c1072438dfed07f0c36e,
AI_ENTRYPOINT/PROCESS/ENGINEERING/NATIVE/TOOLS/WORKFLOW. Existing Stage C scope,
Development gate; Critical read-only native research. Continues
[resident root binding](C1_RESIDENT_ROOT_BINDING_REVIEW_2026-10-01.md).

## Contract before implementation

- MR-001: portable checked reader with fixed call/byte/chunk budgets, exact bytes
  or refusal; compare requested range/protections/mapping metadata before/after.
  Query/copy failure, truncation, executable/non-readable/cross-region/overflow
  request or changed mapping refuses without retries or empty-success fallback.
- MR-002: native backend targets only mach_task_self, main thread, with at most
  sixteen mach_vm_region_recurse steps per query. Request the verified V0 info
  count, reject other counts, bound nesting and check containment of the original
  requested address. Never enumerate all regions, attach, select a foreign PID,
  alter protections, allocate/unload provider state or call Adobe functions.
- MR-003: reuse ReadSelfMemory for the actual bounded copy. Query again afterward;
  record diagnostic mapping provenance and counters, never allocator ownership,
  lifetime/quiescence/completeness/approval or ResourcePassGate eligibility.
- MR-004: synthetic boundary/failure/change/budget coverage and actual owned
  mmap pages, guard/non-readable/cross-boundary/invalid-address/main-thread
  refusals. Tests alone create/protect/release their own pages. No AE operation.
- MR-005: full clean-source local regression and exact CI; preserve current live
  NOT OBSERVED/NOT RUN and no automatic native-resource integration.

## Operating-system API source check before implementation

Selected source: installed macOS 27.0 SDK. mach_vm.h lines 305–313 declare
mach_vm_region_recurse(vm_map_read_t, address*, size*, depth*, info*, count*).
vm_region.h defines vm_region_submap_info_data_64_t, the V0 count and fields;
vm_prot.h defines READ=1, WRITE=2, EXECUTE=4. Use the V0 count for the fields
being consumed, not the SDK's latest V3 count as an unverified kernel assumption.
An owned-page trial on local macOS 26.6.2 arm64 passed before repository changes:
readable mapping, protected own page, cross-boundary and address-1 refusals.
Existing mach_vm_read_overwrite helper is unchanged. No Adobe SDK API added.

SDK source SHA-256: mach_vm.h `e30059fbf2083226bc7cb63c8a8f3e4f596baedb838df6dadc6c886c9ed7b390`;
vm_region.h `7d2b0fa4aad4d46f88243ccbbbad0dba77037b602b8838160da5a6882f14aea2`;
vm_prot.h `681f2ecfefaf600a5b30efd941f5b71068df07144cde888d32c7c100a14bc209`.

Mapping object_id is a diagnostic VM identifier, not an allocation handle or a
lifetime lease. Mapping equality and matching bytes cannot detect ABA or guarantee
atomicity, complete callbacks or safe third-party repeat behavior. This reader
cannot preempt a synchronous kernel operation; external supervision/deadline still
must bound an eventual live diagnostic. No candidate/live authority is implied.

## Verification

Focused local macOS arm64 test PASS: 29 synthetic cases nested in one Python
test plus actual owned mapped-page inspection. Includes before/after mapping
changes, request/read budgets, exact-copy/query failures, invalid/overflowing/
non-readable/executable/out-of-region requests and permanent refusal after any
failed read. Native owned guard/cross-boundary/address-1/thread refusals PASS.
No provider loaded, no foreign process or Adobe memory read.

Owned fixture AddressSanitizer + UndefinedBehaviorSanitizer run PASS with no
diagnostics. The test alone creates/protects/releases its own pages; the reader
changes no mapping or protection. At most 24 reads / 16384 bytes / 4096 per chunk,
with up to 16 query steps before and after a copy. Mapping records are diagnostics
only and do not populate ResourcePassGate's complete/observed/digest fields.

Code/test source **6c666ca6877baac7d56717be4f9d9ec22a982cea**. Clean full local
regression PASS: 288 Python without skips, 62 Node, 22 stages, unchanged inventory.
Run 756b80356ace48c687828349ee8514d5; private ZIP
AEHL-checks-b6cr9xba.zip SHA-256
`67d6a90b1d11041bb0529de9f95825434d78c7a2222a52cf5fa9336d72dba7bf`.
Exact manifest inventory/all 24 payloads independently verified.
Research CI **36929256787 — PASS**; full macOS CI **36929256802 — PASS**.

Clean-source code scanner completed for 256 supported files with no omissions.
Exit 1 / review_required retains the known local argparse false positive at
artifact_manifest.py:71. No other candidate; runtime/full security readiness
is not assessed. Live AE roots NOT OBSERVED; C1 registration/apply/render NOT RUN.
Next bounded diagnostic observer composition and concrete candidate preparation;
no ResourcePassGate integration or renewed private-call authority.
