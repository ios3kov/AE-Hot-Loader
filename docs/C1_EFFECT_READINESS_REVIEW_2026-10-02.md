# C1 effect readiness and descriptor ownership — bounded file review

Stage C1, Development; starting clean research HEAD
`0443f978e0d1b1a973a3658642acf30a800debc3`. Adopted rules **6.2.0**,
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`. AI_ENTRYPOINT,
PROCESS API-SOURCE-001/SAFE-001/regression/evidence, ENGINEERING debugging and
compatibility, TOOLS file diagnostics and NATIVE ownership apply. Collector
maintenance is Standard; dependent private host integration is Critical and
blocked. Product scope is unchanged; this is not Validation or Full Release.

## Question and acceptance

Continue the [publication review](C1_EFFECT_PUBLICATION_REVIEW_2026-10-02.md):
what do actual ReadyFilter/DoLazyGlobalSetup bodies and the path descriptor
constructor change or retain, and can a normal return be mistaken for a usable
effect or safe rollback?

READY-001: collect fixed complete bounded bodies, separate the constructor thunk
from its implementation and class-reference helper, preserve original PLUG/FLT
hashes, require full decoded coverage and addressed state/ownership anchors.
READY-002: distinguish preparation count, routine descriptor, entry pointer,
global dispatch, cached metadata/global data and parameter setup. Keep receiver,
thread, transitive ownership and failure atomicity unknown where unproven.
READY-003: refusal tests for changed anchors/coverage/scope and regression of the
existing collector modes; clean-source collection, independent ZIP/raw branch
checks, available local regression, static review and exact-source CI.

Only file tools are permitted by this block. No process launch/attachment/read,
AE operation, installation, private callback, scan, provider retention, unprep,
global setdown, teardown or retry is performed. Reviewing a setdown function's
file bytes does not invoke or authorize it. Original native helpers/profiles/
ResourcePassGate stay unchanged; prior diagnostic scope is consumed.

## Prepared verification checkpoint

Preliminary pinned-file windows decode completely. Three new focused tests were
added before the new mode; their three expected errors demonstrate the missing
implementation. Clean-source evidence/regression/CI and findings are pending.

## Bounded file findings

`--review effect-readiness` selects nine fixed windows, **1136 instructions /
79 addressed anchors**. Complete bodies end at the next defined text symbol in
the original arm64 PLUG/FLT files pinned by AE256ResourceProfile.hpp. The new
scope introduces no native helper/layout/call. Full disassembly stays private.

| Body, unslid file VM start–end exclusive | Instructions |
|---|---:|
| FCSpec::ReadyFilter, 0x5cea8–0x5d0dc | 141 |
| FCSpec::DoLazyGlobalSetup, 0x5d328–0x5d644 | 199 |
| FCSpec::UnreadyFilter, 0x5d104–0x5d328 | 137 |
| FCSpec::DoGlobalSetdown, 0x5d644–0x5d7dc | 102 |
| FLTp_DoGlobal, 0x906c4–0x90b7c | 302 |
| FLTp_GetStdParams, 0x539ec–0x53a24 | 14 |
| PiPL/path descriptor constructor body, 0xc9b4–0xcc9c | 186 |
| ML::Plugin::CreateClassRef, 0xcc9c–0xcd74 | 54 |
| PiPL/path constructor thunk, 0xcd74–0xcd78 | 1 |

Interpretations below describe only these exact pinned files, not usable private
C++ declarations, runtime receiver attestation, host safety or supported ABI.

1. **Preparation has a count and descriptor contract.** ReadyFilter locks the
   object's recursive mutex, increments a preparation count before testing the
   retained routine descriptor, and only on the first acquisition calls
   PLUG_PrepRoutine. A nonzero result marks the FCSpec failure bit, decrements
   that count and returns 6402. Success copies the descriptor's entry word into
   the effect procedure slot. A null descriptor has a zero-return branch;
   therefore return zero alone is not proof of an actual plugin entrypoint.
   Exception unwinding releases temporary references/lock; that does not
   establish restoration of the preparation count on every exception.
2. **Lazy globals can mutate before later failure.** DoLazyGlobalSetup takes the
   same object lock, tests the global-setup flag and, when unset, calls DoGlobal
   with command 1 and the supplied cache pointer. It then calls GetStdParams;
   errors mark the failure flag and take an exception/translation path. Optional
   byte outputs are written on distinct branches, but their full caller contract
   remains unknown. There is no visible compensating setdown in this body.
3. **Global setup and global data are distinct.** DoGlobal prepares PF_InData,
   calls FLTp_DispatchFilter, and on a nonzero returned error skips its own
   success updates. On setup success it can copy version/flags to the supplied
   cache, enforce flag combinations, set the global-setup bit, report metadata
   mismatches and store returned global data. On setdown command 3 it stores the
   returned global-data handle after successful dispatch. The procedure's
   existence/name is not proof that transitive dispatch is safe late in AE.
4. **Parameter readiness is still a dependent contract.** GetStdParams returns
   zero for an existing canonical effect; otherwise it tail-branches to
   FLTp_DoParamsSetup at 0x535ac. This review does not cover that body's behavior,
   canonical-effect receiver construction, or FLTp_DispatchFilter at 0x98494.
   Global setup may therefore already have succeeded when parameter setup fails.
5. **Unready/setdown are not a generic rollback.** Unready decrements the count
   before PLUG_UnprepRoutine, clears the procedure slot when a descriptor exists,
   and restores the count on a returned unprep error. DoGlobalSetdown tests the
   setup bit, readies the effect, dispatches command 3, then unprepares on the
   normal return path, including a returned global-dispatch error. Neither body
   proves transactional registry removal or rollback after arbitrary exceptions;
   reviewing their bytes grants no authority to invoke them.
6. **Path descriptor construction retains host objects.** The 0xcd74 symbol is
   only a B thunk to the body at 0xc9b4. That body copies the UTF-16 path and
   retains the PiPL InterfaceRef. For a nonempty path it creates an ML::Plugin
   class reference, obtains the PluginImpl interface through an indirect call,
   transfers its reference into the descriptor and calls SetFullPath. The helper
   allocates a shared Plugin object and registers it with ClassWatcher. These
   are ownership/state effects, not proof that its provider binary is pinned for
   a late call's entire lifetime. Empty/null-interface and exception branches
   remain part of the evidence; transitive allocator/watcher/cold paths and
   provider lifetime are not certified.

Consequence: neither ReadyFilter's return nor a registry entry is an acceptance
signal for hot loading. The eventual backend must separately attest actual
entrypoint/provider identity, prepared lifetime, successful global/parameter
setup and subsequent apply/render. Local object locks do not establish AE-wide
thread/quiescence safety. The safe native backend remains **NOT READY**;
registration/apply/render is **NOT RUN** and the historical registration FAIL
remains unchanged. Do not bypass ResourcePassGate or use private teardown as an
unreviewed compensating action.

## Focused implementation checkpoint

All **21 collector tests PASS**, including real LLDB file inspection of owned
arm64 code/data. New refusal cases mutate each of the 79 anchors, reject duplicate
coverage/changed bounds, separate thunk/body/helper and exclude placeholder/global
scan/stream-wrapper symbol routes. Existing search/cleanup/lifecycle/publication/
ownership modes retain their exact windows and pins. Clean-source collection,
independent original-byte/archive checks, full regression/static review and CI
are pending at this checkpoint.

Next file discriminator: FLTp_DispatchFilter's command/entrypoint/host-context
contract and FLTp_DoParamsSetup's mutation/failure behavior, followed by the actual
PluginImpl preparation/provider lifetime. No new live packet is prepared.

## Exact-source evidence and regression closeout

Code/test source **986adb36e2b127c44608ec0a5e30ff165cb6f47d**.
The new clean-source collection PASS: nine windows / 1136 instructions /
79 addressed anchors. Original PLUG/FLT hashes match before/after. Private
22-member ZIP SHA-256
`06a4263298b41f861eea13046dc321a1e0430b73e77cdcc9f7107e8a03716e76`.
All six mode archives independently pass inventory/CRC/every-member hashes,
source identity and complete decoded address coverage. **Every direct B/BL in
all nine new windows (146 branches)** was also decoded independently from the
original arm64 Mach-O words and matched against the archived disassembly.
These checks verify static evidence, not callback behavior in AE.

Independent verifier source SHA
`24466bd72fca2b06e4a4e4309c3f6f1582e03e1f54f993a3a21c07a2af5d28a9`;
private verification record SHA
`b5e872aa9daf60f81c5a5d6a672d6c4825b9c7d367d1017818ac0487cbc1dde2`.
No original Adobe binaries or complete disassembly are published.

| Existing mode at the same source | Instructions | Private ZIP SHA-256 |
|---|---:|---|
| search-abi | 472 | `90bd0e3e1718c0915d04f753c9091f05583ccf0f339da4393e8764d2e93953e6` |
| cleanup | 1390 | `091a8c516dd4f638e89762a70cad930048679507709981c2f4b3f6a0906614d6` |
| lifecycle | 891 | `7534b2a8f98e6d1312639e84faeb2f626c464089f408a94bb262da1174b85f31` |
| publication | 5002 | `294b451b82a8e33b7d22eb8dc43d4b34c324a675f685e8745785c513ceaf6173` |
| ownership | 960 | `11d96e2385a88b320611bf548c1bea9f823eeeb3815fa6e20c7419d37d49e1ce` |

Full clean local macOS regression PASS: **361 Python/no skips, 62 Node,
22 stages**, macOS 26.6.2 arm64. Source before/after is clean and every one of
299 tracked file hashes matches the identified source. Private report ZIP SHA
`f1a7fa64a98121ada9ce4b92deb5745a40a9aec8f3e8627079a6cbb052b0d596`;
independent 25-member inventory/CRC/hash/source checks PASS, receipt SHA
`d9a9e912f6f821864912bf0f38d1baac03637a4737827961bab6b695e50a7fdb`.
An initial manual verifier assertion incorrectly compared the report's boolean
`source_unchanged_after` with a source dictionary; it was corrected after reading
that schema. No source/test/report was changed or test gate weakened.

Bounded code-profile scanner completed every selected check and four workflows:
**404 supported text files / no omissions**, including ignored collected text in
the owned build directory. This scope differs from the older publication audit;
its file count is not a source-completeness or product-security score. Raw exit
**1** retains only `vibe.no_ratelimit_auth`, tools/artifact_manifest.py:71.
Re-inspection confirms local argparse setup, not an HTTP authentication route;
no suppression. Private audit SHA
`3c63b1e166477f608064a41a6cc2baa54ced7ce4f289872b2041a3579413adcb`.
Release readiness remains not assessed by that scanner.

The research branch is pushed at exact 986adb3. Exact-source research CI
37057799645 and full macOS CI 37057799722 were initially in_progress; their final
state will be appended after verification. No merge/release/install/live operation.
Native helpers/profiles/ResourcePassGate are unchanged from the reviewed live
candidate at 0204ab8. The native backend remains NOT READY; actual registration,
apply/render, broader compatibility and full release gates stay open.

## Preliminary follow-up preserved for the next block

While exact-source CI was running, two further file-only complete windows were
captured privately: FLTp_DispatchFilter 0x98494–0x98c80 (507 instructions) and
FLTp_DoParamsSetup 0x535ac–0x539ec (272 instructions). Original FLT pin matched
before/after; only the five documentation closeout files were dirty, and that
explicit state remained unchanged. This scratch capture is **preliminary**, not
the clean-source collector acceptance or native/runtime evidence above.
Private follow-up record SHA
`1645a34b41c3bc0f0089c8bd435098af38d9823c9da242543e17caa0f7c5f5fa`.

The parameter body calls RegisterCanonicalInstance at file VM 0x53758 before
PARAMS_SETUP dispatch at 0x53898. Thus the next review must cover canonical
stream ownership/failure cleanup as well as global-data state; do not assume
that a later setup error leaves the stream factory unchanged. The outer dispatch
body calls FLTHost::DispatchFilter at 0x98640 → 0x38d60. Its actual entrypoint,
provider and host-context contract remain unreviewed in this checkpoint.

Next bounded acceptance block: collect these two bodies and the inner host
dispatch with explicit anchors/refusal checks, review canonical stream retention
and exception paths, then trace PluginImpl preparation/provider lifetime. Only
file tools are in scope; no live call or retry packet is prepared here.

## Final CI and documentation closeout

Exact-source [research CI 37057799645](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37057799645)
and [full macOS CI 37057799722](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37057799722)
both completed/success at **986adb36e2b127c44608ec0a5e30ff165cb6f47d**,
verified from final public GitHub workflow states. Final private receipt SHA
`9b21faa3071145b3c5da7916a825d15aa9b028b4a3a55b3149d84b6d5cd9e3d1`.
Build/sign/package/synthetic smoke success is offline evidence, not AE loading,
registration, apply/render or release approval. Earlier pending checkpoints above
are superseded; READY-001/002/003 are closed within this bounded file-only scope.

Documentation closeout: affected local links and whitespace checks PASS; only
collector/tests and five documentation files differ from the starting checkpoint.
No new native candidate/artifact handoff, private callback or installation.
Next bounded discriminator and remaining Critical host/API/lifetime/release
blockers are unchanged by CI success.
