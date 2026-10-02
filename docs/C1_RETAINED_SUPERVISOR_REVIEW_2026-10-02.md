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

## Exact source/candidate preparation evidence

Code/test source 0204ab83212d68b19d85b78d0c7239511f301b7b. Full clean local
regression: 353 Python/no skips, 62 Node, 22 stages PASS; source unchanged.
Report SHA `dab580b0db0a15bbce5f2a1c6c264f9cdbc06bdbec41a19d83fbd9da9153c645`;
ZIP CRC/inventory/every member SHA/current tracked source independently verified.
Bounded static audit completed: 332 supported files/no omissions; raw exit 1
retains sole known local argparse false positive at artifact_manifest.py:71,
rechecked separately. Audit SHA
`ab6ae2988e749c62a0add0251648d4c53c126e9d3d4a41b07564db2369ef1ad4`.
Native code separately reviewed; unsupported scanner types outside audit claims.

Exact identity-d5480a2a4090 SDK 25.6 build/sign/strict verification/exports/identity/
inert entry + real self binding/wrong-hash refusal PASS. Four bundle payloads,
74 SDK input hashes and provider profile/file identities independently rechecked.
Candidate binary and private manifest hashes, prospective install/launch scope,
remaining CI status and mandatory authority boundary are recorded in
[C1 retained live scope](C1_RETAINED_LIVE_SCOPE_2026-10-02.md). No install/AE launch
or request publication. Actual seven names NOT RUN; no full release claim.

## Closeout

Exact-source [research CI 37052270787](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37052270787)
and [full macOS CI 37052270804](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37052270804)
both completed/success at 0204ab83212d68b19d85b78d0c7239511f301b7b.
ASan/UBSan strict owned binding/capture fixture: 41 cases PASS, no sanitizer
diagnostics. Leak detection NOT RUN: detect_leaks unsupported by this Darwin
runtime (initial requested leak-enabled run refused before fixture execution).
This adds no live/native lifetime claim. Documentation-only closeout changes no
tested code or candidate bytes; local links/whitespace and unchanged code inventory
checks PASS. RIS-001–006 are closed within the prepared/owned/injected scope.
Actual host diagnostic and installation/loading remain NOT RUN pending fresh
exact authority; registration/apply/render/release remain blocked.

## Subsequent authorized live execution

The exact final identity-d5480a2a4090 candidate/controller at source 0204ab8
completed one explicitly authorized install/launch/read-only diagnostic PASS.
[Live closeout](C1_RETAINED_NAMES_LIVE_PASS_2026-10-02.md) supersedes preparation
NOT RUN statements for that bounded question: seven names, unchanged project/
registry and one explicitly permitted system-image addition. Original private ABI,
provider lifetime and verifier attestation limitations remain. Authority consumed;
ResourcePassGate unchanged; registration/apply/render/release gates remain open.
