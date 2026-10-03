# C1 compatibility scope under rules 6.2.0

This is a bounded research inventory, not a complete product API/artifact audit.
Baseline `bed0de67d7e91b56ac51d5c9efb39653f0a534ad`; accepted rules 6.2.0,
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`. Separate Test Status from
Compatibility Status; do not infer a supported AE range from a single build.

| Component / exact configuration | Candidate / evidence | Test Status | Compatibility Status / scope |
|---|---|---|---|
| Historical diagnostic, AE 25.6x101 arm64 | observe-d548b007e316, native source 7c983c5; [live record](C1_DIAGNOSTIC_LIVE_PASS_2026-10-02.md) | PASS | LIMITED: one read-only count/callback diagnostic, no effect registration/apply/render claim |
| Owned-buffer decoder, C++17 | source 15c528f; [decoder evidence](C1_RETAINED_IDENTITY_DECODER_2026-10-02.md) | PASS | AE compatibility UNKNOWN: owned fixtures and CI only; no native installable candidate |
| New record/name capture | [owned-chain core](C1_RETAINED_CAPTURE_REVIEW_2026-10-02.md), exact source eb559ed, no native candidate yet | Full available owned-data/CI PASS; NOT RUN in AE | UNKNOWN; offline adapter preparation cannot establish live identity/lifetime |
| Record/name journal + independent verifier | [owned evidence review](C1_RETAINED_JOURNAL_REVIEW_2026-10-02.md), no host candidate | Full available owned-data regression and both CI PASS at 59becab; AE NOT RUN | UNKNOWN for AE; journal structure does not attest to host execution |
| Record/name transaction core, injected boundary | [transaction review](C1_RETAINED_TRANSACTION_REVIEW_2026-10-02.md), exact source 836c29d, no native/disk adapter | Full available owned-data regression and both CI PASS at 836c29d; AE NOT RUN | UNKNOWN for AE; injected binding/approval inputs do not attest to runtime or authorize operations |
| Host journal + independent transaction verifier | [owned evidence review](C1_RETAINED_HOST_JOURNAL_REVIEW_2026-10-02.md), no native candidate | Full available owned-data regression and both CI PASS at dfa78e0; AE NOT RUN | UNKNOWN for AE; supplied host observations are not live attestation |
| New native name adapter + independent supervisor, AE 25.6x101 arm64 exact diagnostic scope | [native review](C1_RETAINED_NATIVE_CANDIDATE_REVIEW_2026-10-02.md), [controller](C1_RETAINED_SUPERVISOR_REVIEW_2026-10-02.md), source 0204ab8, identity-d5480a2a4090 | 353 local Python/no skips, 62 Node, SDK build/sign/hash/identity/inert PASS; both exact-source CI PASS; [one authorized live name diagnostic PASS](C1_RETAINED_NAMES_LIVE_PASS_2026-10-02.md) | LIMITED to one read-only diagnostic on this exact AE build; allocation lifetime, safe replay, registration and broader versions UNKNOWN |
| File-only effect-publication collector, exact pinned PLUG/FLT arm64 files | source db4799e; [publication review](C1_EFFECT_PUBLICATION_REVIEW_2026-10-02.md) | Local 358 Python/62 Node PASS; 5002 instructions/83 anchors/48 raw BL checks PASS; both exact-source CI PASS | UNKNOWN for runtime: conditional private file path and placeholder exclusion, no native registration ABI or supported-version claim |
| File-only readiness/descriptor collector, pinned PLUG/FLT arm64 files | source 986adb3; [readiness review](C1_EFFECT_READINESS_REVIEW_2026-10-02.md) | 361 local Python/62 Node PASS; 1136 instructions/79 anchors/146 raw branches PASS; both exact-source CI PASS | UNKNOWN for runtime: private state/ownership/failure-path review, no native ABI or broader support claim |
| File-only effect-dispatch collector, pinned FLT arm64 file | source 8aec890; [dispatch review](C1_EFFECT_DISPATCH_REVIEW_2026-10-02.md) | 364 local Python/62 Node PASS; 1939 instructions/86 anchors/377 direct branches/3 indirect sites PASS; both exact-source CI PASS | UNKNOWN for runtime: saved-procedure/crash/error-path correspondence only; receiver/provider lifetime and canonical rollback unproven |
| File-only provider/canonical-factory collector, pinned PluginSupport/TDB arm64 files | source 49a8531; [retention review](C1_PROVIDER_FACTORY_REVIEW_2026-10-03.md); TDB pin scoped offline only | 368 local Python/62 Node PASS; 1365 instructions/146 anchors/257 direct/26 indirect branches PASS; both exact-source CI PASS | UNKNOWN for runtime: references/maps/destruction paths only; actual identities, safe lifetime/unregistration/rollback unproven |
| Full tool, other AE builds/versions/platforms | no complete exact distributed-candidate/runtime evidence | NOT RUN | UNKNOWN; no minimum/current endpoint interpolation |

## Relevant API/layout inventory and omissions

- Existing observer public SDK entry/idle/script hooks remain tied to its exact
  reviewed native source/header identities in the
  [candidate review](C1_OBSERVER_CANDIDATE_REVIEW_2026-10-01.md). No new Adobe API
  call is introduced by the decoder/capture core. Documented minimum AE remains
  unestablished by this bounded inventory; the selected research host is 25.6x101.
- MEE GeneralPlugin record/string layout is a private file interpretation for
  SHA-256 `18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344`,
  UUID `74a30dbaa08b367bbd9915d6d77e9d52`, arm64. It is not a public SDK ABI and
  must not be selected automatically for another file/build/architecture.
- `MappedMemoryRead` calls the existing current-process Mach mapping/read backend
  only when explicitly supplied. Its own page/protection/boundary tests are not
  foreign Adobe allocation or lifetime evidence. No installed AE binary/version
  is changed to simulate missing capability.
- New capture-core refusal scope: unknown layout, invalid vector, excessive
  count/name length, failed/unreadable mapping, changing copied bytes/mapping,
  retargeted root and repeated invocation. Actual results belong to its dated
  capture review, once implemented.
- Full generic Agent/Control Shell, panel/JSX APIs/runtime, generated native SDK
  candidate, package dependencies/PiPL/OS imports and distribution audit are
  omitted from this bounded C1 inventory; they need the final candidate's audit.
  These material omissions prevent a full STATIC-COMPATIBLE/VERIFIED claim.

## Future live/remote packet requirements

The next diagnostic first needs an exact clean source, Build ID, final binary/
package hashes, SDK/header identities, reviewed one-shot adapter/journal/supervisor,
inert/refusal checks and independently verified report format. Target the same
hash-pinned AE 25.6x101 arm64 research configuration first; this choice isolates
layout interpretation rather than proving broad product support.

Before execution, record installation/rollback preserving existing plugins,
deterministic blank/unsaved/clean/idle disposable fixture, expected loaded identity,
bounded copy inventory, stop/no-retry behavior, sanitized evidence paths and
separate exact operation authority. A real operator record must retain observed
AE/OS/build/architecture, received hashes and actually loaded identity. No new
packet is declared executable at this checkpoint. Other supported-version targets
are selected from actual API/runtime boundaries once the production route exists;
do not install every AE locally or promise an untested range.

Current product release remains BLOCKED on C1/C2/registration/apply/render and
remaining acceptance. Successful count/name observation cannot waive these gates.

## Latest candidate preparation supersedes earlier no-candidate statements

The rows above for earlier portable checkpoints keep their historical scope.
An exact separate diagnostic native candidate and external controller now exist
at 0204ab8, with final bytes and planned operation documented in
[C1 retained live scope](C1_RETAINED_LIVE_SCOPE_2026-10-02.md). Public SDK API
reuse, indirect resident/Mach binding paths, native exports and SDK input hashes
are recorded in the native/controller reviews. This is a bounded C1 inventory;
full product audit/other versions/product registration remain omitted and block
release. No live authority is inferred from completed build preparation.

## Live diagnostic closeout

Exact candidate identity-d5480a2a4090 was installed and loaded once under explicit
scope; read-only names PASS. This closes the bounded diagnostic test question
only. Earlier portable rows retain their historical no-host scope. No supported
version range, loaded identity of all seven attributed providers, private lifecycle
or ordinary-effect registration compatibility is inferred. Scope is consumed;
next work is offline publication/isolation research.
