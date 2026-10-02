# C1 retained-name external supervisor

Baseline clean `5d9e3e8011321b996c641fd2e7a32885ccee13e6`, rules v6.2.0,
Critical Development diagnostic/IPC/native integration. Native adapter preparation
passed 340 Python/no skips, 62 Node, 22 local stages; candidate
identity-340ea065a0c3 is inert and NOT INSTALLED. This stage connects external
request publication/verification, then rebuilds an exact final candidate. No AE
contact, installation, launch, process stopping, private invocation or release.

## Acceptance before implementation

1. RIS-001: exact manifest hash, candidate identity/safety checks, installed bundle
   hash/signature, ready identity, PID/start/executable and fixed provider files;
   reuse the reviewed public libproc process-identity API, never attach/read AE
   memory from the supervisor. No SDK API change.
2. RIS-002: exclusive attempt claim before any publication, exact request incl.
   final binary hash/read-only review; fresh explicit execution authority required.
   At most one request, including publication exception/unknown outcome; preserve
   files/process/plugin state and refuse reused/ambiguous attempts.
3. RIS-003: independently supplied monotonic nanosecond budget starts BEFORE the
   claim/pre-publication rechecks, lasts exactly 15 seconds; check before and after
   complete verification/final identity/file rechecks. No reset using producer time.
4. RIS-004: derive expected root from unique exact MEE path/header/slide in bounded
   baseline evidence plus pinned static root_vm minus independently checked
   image_base_vm. Bind helper presence and image slide/base arithmetic; ignore
   producer root as a source of expected policy, then verify ALL five records and
   both captures with the existing safe reader/verifier.
5. RIS-005: one private token-free hashed ZIP of fixed native files/attempt/result;
   FAIL/timeout/partial preserve evidence. No execution/registration attestation
   from synthetic transport or producer PASS; host_execution_verified stays false.
6. RIS-006: owned real copied-byte fixtures and injected process/transport verify
   success, identity/root/image tamper, preparation/refusal/replay, publication
   unknown outcome, deadline before/after semantics/final checks, and token absence.
   Full clean local checks, source/static review, exact-source CI and inert rebuild.

## Safety boundary

The previous actual count capture approval is consumed. New live candidate requires
identified operation-specific installation/one-launch/read-only permission and safe
blank-project preflight. This module has no installation/launch/kill route. Static
image-address derivation validates consistency of producer inventory with reviewed
source; it is not external OS memory attestation or hostile same-UID proof. Matching
copies do not prove atomicity/lifetime/quiescence. Actual seven names NOT RUN.

## Implementation/review boundaries

Preparation reuses reviewed libproc PID/start/executable, bundle hashing, signature
and ready binding; fixed MEE profile now includes independently parsed base_vm.
Publication uses the reviewed exclusive macOS rename helper. The new run requires
explicit authority before any claim; mutable record/request metadata is frozen and
paths/readiness rechecked. Unknown publication consumes the claim without retry.

The independent reader loads all five files once without following links, derives
expected root from bounded baseline image inventory and static layout, verifies
all copied frames and host observations, then rechecks filesystem identities.
The claimed root is temporarily used to parse the untrusted inventory's scope
syntax; every field except root must first match trusted policy, and final policy
root is recomputed from MEE header/base/slide before full verification.

The fixed 15-second operation budget covers claim/pre-publication rechecks, request
and capture waiting, semantic/file verification, and final process/provider/helper
rechecks. Preserving failure evidence and ZIP packaging are outside this operation
budget and issue no AE action; this is explicit in result metadata. Expired/late
producer PASS is rejected. No hard preemption/cancellation guarantee is claimed.

Initial native preparation now performs the public safe-project snapshot BEFORE
loaded MEE/self binding; the three persisted transaction snapshots remain separate
fresh measurements. No record-body read precedes the durable transaction marker.
Separate source review covers immutable exact paths/request, loaded self/MEE root,
copy preservation/refusal, unknown publication, scoped clock, exclusive records,
fixed token-free ZIP inventory and no installation/launch/kill/private-call route.

## Focused verification

16 candidate/supervisor Python tests PASS, including 13 new external cases and
41 nested C++ binding/capture cases. Real C++ captured raw-name journal fixtures
are explicitly relocated into synthetic AE scope/image transport, then verified
through the actual safe reader and independent whole-journal verifier. This is
owned fixture evidence, never real AE/host execution. Wrong producer root is
rejected even when every record repeats it; provider/helper inventory and slide
mutation, altered bundle/ready/PID/start, missing authority/path/request retarget,
replay, unknown publication, partial evidence, before/after-verification expiry,
late final file check and backwards clock refuse. Fixed ZIP inventory/CRC/member
hashes and no activation token verified. Code-level inspection caught and fixed
a missing ready-start recheck before publication; its regression now passes.
