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
| Host journal + independent transaction verifier | [owned evidence review](C1_RETAINED_HOST_JOURNAL_REVIEW_2026-10-02.md), no native candidate | Focused owned-data PASS; full/CI pending; AE NOT RUN | UNKNOWN for AE; supplied host observations are not live attestation |
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
