# Stage C1: resident data-root binding preparation

Baseline dae3066 (static metadata code efe05f2); rules b27f45467e0a9152fc82c1072438dfed07f0c36e,
AI_ENTRYPOINT/PROCESS/ENGINEERING/NATIVE/TOOLS/WORKFLOW. Existing Stage C scope,
Development gate, Critical native-memory research. Continues
[root provenance](C1_ROOT_PROVENANCE_REVIEW_2026-10-01.md).

## Contract before implementation

- RB-001: reuse ResidentImageBinding's exact canonical file hash, unique already-
  resident path, main-thread, loaded header/slide, UUID/header/text-byte checks.
  Never load/resolve by dlsym/invoke a provider function or select another process.
- RB-002: validate a reviewed nonzero aligned root extent in exactly one
  __DATA,__bss/__common S_ZEROFILL section with read/write non-execute protections,
  no read-only-after-fixups flag, zero file offset and checked VM/size arithmetic.
  The supplied root profile is a reviewed-file contract, not arbitrary live input.
- RB-003: derive the candidate address from the verified resident header plus
  image-relative root offset; verify file/layout/image-set identity again. Return
  only root extent and identity, not a function pointer, lifetime lease, heap
  ownership, observation completeness or resource-call eligibility.
- RB-004: portable malformed-data boundary tests and real owned-library tests:
  absent-image refusal without loading, exact root address/read, wrong hash/root/
  section/thread refusal, unchanged image set. Only tests load/unload their own
  freshly compiled library. Adobe libraries are never loaded or invoked.
- RB-005: full clean-source regression and exact CI; preserve C0's recorded PASS
  and C1 resource/apply/render NOT RUN. Record limitations before live adoption.

## Source and unresolved gates

Use existing Mach-O parser and resident checks, the actual SDK loader.h section
layout, and the exact PLUG/MEE static root collection/UUIDs. Sentinel exported
symbols are solely address/code identity anchors; no signature/behavior is assumed
and no call is made. PLUG PLUG_Search and MEE MEE_GetGPList are never invoked.
This reuses existing operating-system APIs and adds no Adobe host API.

The root binder does not inspect a callback list or heap allocation. Point-in-
time identity is not a dyld lifetime lock, main-thread checking is not proof of
quiescence, and readable zero-fill metadata is not proof of complete live state.
No resource backend or automatic approval/snapshot conversion is connected.

## Verification

Focused macOS arm64 regression PASS: three Python tests. Portable malformed
metadata rejects protections, file-backed sections, ambiguous segments/sections,
root extent/overflow and overlapping VM segments. Real owned-library binding
proves absence refusal, exact root address and changed owned data read, hash/UUID/
section/extent/thread refusal and unchanged image set. The binder loads nothing;
only the test loads/unloads its own freshly compiled library.

Bounded file-only Describe checks also passed on exact pinned PLUG/MEE bytes,
using export identity anchors without invoking them. No live Adobe provider,
root memory or callback was read. No profile was adopted into resource approval.

Code checkpoint and exact clean regression/CI evidence: NOT RUN before commit.
