# C1 retained names — authorized live diagnostic PASS, 2026-10-02

Stage C1, Validation; accepted rules **6.2.0**, source
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`. Pinned AI_ENTRYPOINT,
PROCESS scope/evidence/regression, ENGINEERING API/debugging, NATIVE host/memory,
TOOLS IPC/diagnostics and MAC-001 apply. Product registration scope is unchanged.

## Question, authority and execution

Question: identify the raw names in the observed legacy MEE GeneralPlugin records
without invoking, releasing or reinitializing them. Acceptance: exact candidate,
closed-host installation preflight, one launch/request, blank-project observations,
bounded matching copies and independent evidence checks. This is separate from
late registration, lifecycle safety and release acceptance.

The user replied **«делай»** to the concrete request to install this unique
candidate, launch AE 25.6 once and perform one read-only name diagnostic.
Fresh process-absence verification PASS immediately before copying and before
launch. The prepared [scope](C1_RETAINED_LIVE_SCOPE_2026-10-02.md) was executed;
that one-shot authority is now consumed. No permission was inferred from an old
release/continuation command. No new live operation is included in this closeout.

Only `AEHLRetainedd5480a2a4090.plugin` was installed under the user's MediaCore.
Destination was absent; candidate and installed inventories/hashes/signature
PASS. All three previously installed AEHL helpers remained byte-identical.
Pinned AE was launched once; observed PID **28774**, start
**1790968785.735274** stayed identical through final verification. At closeout
it was left running with the consumed, inert helper; neither was removed/killed.

Diagnostic UTC **2026-10-02T19:19:57.611491+00:00** through
**2026-10-02T19:20:02.250759+00:00**. Native/external checks PASS within the
reviewed 15-second operation budget. Evidence packaging is outside that budget;
there is no hard-preemption or cancellation guarantee.

## Exact identities and preserved evidence

| Identity | Value |
|---|---|
| Code/test source | `0204ab83212d68b19d85b78d0c7239511f301b7b` |
| Clean documentation HEAD at launch | `7e137e0ef2bf8cb1d52c926d419c51fa2f94c44a` (same 194 non-document source files) |
| Build | `identity-d5480a2a4090` |
| Run | `retained-identity-c1398e7b82f04b80a3a8aeb6dc59dedc` |
| Final binary SHA-256 | `5e87b628434775d702da2c04475d8121d7ad0ecdddb0b28d23582fcb7510c530` |
| Private manifest SHA-256 | `b0ed7a0f1e51d3949a279b94f02faa6b508cb1f127fa5af448eea24836b85968` |
| Host | AE **25.6x101**, build **101**, **arm64** |
| OS at documentation closeout (file-only system query) | macOS **26.6.2**, build **25G83** |
| Host executable SHA-256 | `464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6` |
| MEE SHA-256 | `18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344` |
| MEE UUID | `74a30dbaa08b367bbd9915d6d77e9d52` |
| Private diagnostic ZIP SHA-256 | `c0cb5db1e2682e2b7d31e98c916c76f4a447889a4d3689e759790d37c11ce1a8` |
| Orchestration source SHA-256 | `cce280b5736354ac02bbec74d47ce24a335085a7ce7b908931dad0bee0a873f3` |
| Orchestration result SHA-256 | `bb7eb65ccb35f1cb53286c191dac7bfb9bc5d3a4e2af3a34752a67000d53e937` |
| File-attribution collector SHA-256 | `b8ad1bd1717dc32f533e8094130385aa620afefce9b85d6dd93d367775f21281` |
| File-attribution result SHA-256 | `eb52d3397717bae794d4aef9bf1defe8d4a574028369e43ddb37450b8c6f2780` |
| Current-file signature result SHA-256 | `883cc9feaead48ee783cc7bd43f32072aeb76b6dd727f8121a3413c92d7c1c9d` |

Private evidence is in the owned workspace `work/private-live/retained-identity-d5480a2a4090-live`;
the ZIP remains in the ignored candidate build directory. Tokens, copied native
addresses/bodies and private activation manifests are not published in Git.

Pre-handoff checks remain bound to source 0204ab8: **353 Python/no skips,
62 Node, 22 stages**, real SDK 25.6 build/sign/hash/identity/inert checks PASS;
[research CI 37052270787](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37052270787)
and [full macOS CI 37052270804](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37052270804)
completed/success. Native/controller reviews retain API/lifetime limitations.
This closeout changes documentation only; it does not relabel offline tests as
live registration tests.

## Actual observations

Seven records; **8 bounded copy calls / 2578 bytes**, two matching capture
sequences. Six names inline, one external long name. At baseline, immediately
before capture and after capture: owned blank/unsaved/clean/idle project,
items=0, queue=0, revision=**1**, registry=**786 identical effect identities**.
The older session's 785 is a different startup baseline, not late registration.

Resident image counts are **1407 → 1408 → 1408**, not strict equality. The sole
addition is `/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/SafariPlatformSupport`;
no removals or changed existing tuples. Immediate and after inventories match.
This satisfies the already reviewed system-image-addition policy in
`verify_retained_host_journal.same_host`; no policy was relaxed for this run.
It does not certify arbitrary lazy initialization or host-wide atomicity.

| Raw captured name | Current installed file correspondence | Exact static teardown symbol |
|---|---|---|
| AEGP Driver | Required/AEGPDriver.plugin | `__ZL15AEGPD_DeathHookPv` |
| Photoshop Layered Export | Plug-ins/Format/PS Layer Export.plugin | `__ZL18PS3ExportDeathHookPv` |
| Photoshop Layer Import | Plug-ins/Format/PS Layer Import.plugin | `__ZL18PS3ImportDeathHookPv` |
| Easy Ease | Plug-ins/Keyframe/EasyEase.plugin | `__ZL17EasyEaseDeathHookPv` |
| Exponential Scale | Plug-ins/Keyframe/ExpScale.plugin | `__ZL18ExpInterpDeathHookPv` |
| Sequence | Plug-ins/Keyframe/Sequence.plugin | `__ZL15Stack_DeathHookPv` |
| Time-Reverse Keyframes | Plug-ins/Keyframe/TRKeys.plugin | `__ZL15TRKeysDeathHookPv` |

File-only attribution uses already archived callback words/image header+slide,
then current hash-stable arm64 file __text ranges and exact symbols. Driver's
finish word additionally corresponds to `__ZL17AEGPD_CleanupHookPv`; the other
six finish words are null. All raw marker words are 1; this is not a safety flag.
No callback, descriptor, control block or state object was invoked/dereferenced
by this follow-up. No debugger, attachment or new AE memory read was used.

Strict signatures for these seven **current installed files** PASS outside the
sandbox. The initial sandbox attempts reported invalid signatures and unavailable
authority; the identical files passed the read-only checks outside that restricted
context. Both results are preserved, not hidden. This does not attest to the
loaded UUID/content of all seven providers: only MEE/helper binding was measured
under the live scope. File correspondence is bounded evidence, not full provider
identity, allocation lifetime, quiescence or safe repeat-invocation proof.

## Independent checks and interpretation

ZIP unique inventory (10 members), CRC, every member SHA and activation-token
absence PASS. Five archived native records match disk evidence; archived
supervisor matches its saved result. Independent semantic replay of saved bytes
matches the original native summary using expected manifest/process identities
and MEE root derived from archived loaded-image metadata plus the fixed file
layout. Replay uses a frozen fixture clock: it is **offline semantic verification**,
not a second live deadline measurement. The original supervisor budget result
remains separately source-bound. `host_execution_verified=false` is preserved:
the verifier does not independently attest actual AE execution or resist an
adversarial same-user producer; orchestration provides bounded runtime provenance.

No private Adobe call, provider retention, registration, retry, root write,
teardown, setup replay, AE termination or project edit occurred.

The seven names and file correspondence indicate normal AE driver, Photoshop
format and keyframe-assistant state in this blank session. Combined with the
[retained ownership review](C1_MEE_OWNERSHIP_REVIEW_2026-10-02.md), replaying the
general resource setup/cleanup path can affect already initialized modules.
This is a reason to preserve the zero-record ResourcePassGate, not to clear
records or invoke death hooks. Hot loading itself remains unproven; historical
late-registration FAIL is unchanged. C1 registration, C2 apply/render, lifecycle,
product integration and release gates remain open.

## Next authorized discriminator

Continue **file-only** research of ordinary-effect-specific publication or
isolation from the existing GeneralPlugin state. Start from the pinned PLUG/PIN/
MEE windows and existing resource/ownership evidence. Require a complete bounded
call path, exact input/state ownership, global side effects and refusal criteria;
record absence of a usable route honestly. Do not substitute dyld visibility for
registry insertion, or duplicate/replay global setup to bypass the current gate.
An offline finding alone does not make a native backend ready. Any new live
operation needs its own prepared, reviewable scope and relevant authority.
