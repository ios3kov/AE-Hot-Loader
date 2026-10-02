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
