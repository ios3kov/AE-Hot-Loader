# Stage C1: repeated preparation and cleanup-state gate

Date: 2026-10-01. Branch: research/ordinary-plugin-discovery.
Current code/test source: `52f4f802f6f3f1641f4109d93491b2e96d8ec3d5`.
Continues [cleanup registration review](C1_CLEANUP_REGISTRATION_REVIEW_2026-10-01.md).
C0 remains the recorded live PASS; C1 registration/apply/render remain NOT RUN.

## Scope, rules and restored state

AI_ENTRYPOINT was read first, then refreshed to current canonical rules source
`b27f45467e0a9152fc82c1072438dfed07f0c36e`. Its new trust, task-state,
continuation and API-source requirements apply. PROCESS, ENGINEERING's
Debugging Protocol, NATIVE, TOOLS and WORKFLOW apply to the existing Stage C
product contract; there is no new product scope or external parity reference.
Collector/runner changes are Standard/Development. Private resource-call
integration remains Critical/Development, not a Validation handoff or release.

The user's continuation request authorizes repository development and checks;
existing research-branch commit/push scope persists. It does not renew consumed
C0 live approvals. Historical scan FAIL, startup RSMB PASS and C0 PASS remain
separate. No AE attach/launch/script, installation, private call, provider
retention, callback replacement, global scan, setup replay or teardown occurred.

The target under research remains AE 25.6x101 arm64 on macOS. This block adds
no Adobe SDK call or supported late-registration API claim. The private native
call/reader contract is UNKNOWN beyond the identified static evidence.
Changes use the separate writable clone; the original checkout is preserved.

Acceptance: identify repeated-preparation control flow, collect bounded complete
evidence and table-format consistency, require fresh reviewed cleanup state in
the unbound policy, preserve that state in durable evidence, cover rejection and
state-change cases, run clean-source regression and exact-code CI. A discovered
CI failure was separately reproduced and corrected before closeout.

## Lifecycle evidence

The collector adds `--review lifecycle`: seven bounded complete instruction
windows, one 96-byte file-backed vtable window, and PLUG fixup-chain metadata.
The ordinary search and cleanup modes remain available and passed again.
LLDB data reads validate every requested word address and count. Owned arm64
code/data regression never executes the compiled bundle or Adobe code.

| Window, end exclusive | Decoded instructions |
|---|---:|
| PLUG_PrepRoutine, 0x7de4–0x807c | 166 |
| PLUG_UnprepRoutine, 0x807c–0x82b8 | 143 |
| PLUGp_UnprepRoutine, 0x7c74–0x7d70 | 63 |
| KeepLoaded / SetKeepLoaded / IsPrepped, 0xdff0–0xe028 | 14 |
| PLUG_RoutineDescPriv constructor, 0xc9b4–0xcd74 | 240 |
| MEE PluginCleanupFunc, 0x376ec–0x37a00 | 197 |
| MEE SetdownGeneralPlugins, 0x37f34–0x38044 | 68 |
| Total | **891** |

Collection source: `3e67046653915f3cc75572d8f71b8c77e16d6642`. The collector
and gate bytes are unchanged at current 52f4f80; its later commit fixes only
the runner and runner tests. PLUG/MEE input hashes match the previously pinned
profile before and after collection. Adobe calls = 0. Private ZIP
`resource-lifecycle-756b06b2-cycy8flx.zip`, SHA-256
`8d8a0dbc4fb0b4806569a83b7db8d48d16772d187c7c823cb9f8a4f55fb45667`.
The archive manifest and every payload were independently verified.

Same-source compatibility collections: cleanup, 1390 instructions, ZIP
`resource-cleanup-19532771-38t75z0k.zip`, SHA-256
`ef778006c63ce4ae6e503311cf58174b533305adf6c08fd2091d182f80d59200`;
search ABI, 472 instructions, ZIP `resource-abi-4de6a175-e771f84m.zip`, SHA-256
`7df094fe8e164034e585fb4b35587e80be5dc8a2c02301083c6291b7ed88560d`.
No original Adobe binary, raw disassembly or raw table is committed.

## Repeated preparation does not suppress MEE's entrypoint

The constructor sets the concrete vtable address point to 0x14930. The bounded
serialized table and matching symbols map +0x30 to KeepLoaded (0xdff0) and
+0x40 to IsPrepped (0xe01c). dyld_info confirms pointer format 6 in the
0x14000 segment. Interpretation uses Apple's
[fixup-chains.h](https://github.com/apple-oss-distributions/dyld/blob/main/include/mach-o/fixup-chains.h),
DYLD_CHAINED_PTR_64_OFFSET and its 36-bit target field. This is file-image
consistency, not a resident receiver or a callable runtime address.

IsPrepped extracts bit 2 of the halfword at descriptor+0x28. PrepRoutine calls
KeepLoaded through +0x30 at 0x7eec. If it returns nonzero and bit 2 is already
set, the branch at 0x7efc reaches 0x7f50, sets status zero and returns. There
is no nonzero "already prepared, skip this record" status on that path.
Other branches can load a platform routine, update flags and global counters;
they do not provide a general idempotence guarantee.

MEE PluginCleanupFunc tests the prep result at 0x377a0: zero continues to the
saved entrypoint invocation at 0x37800. Its body does not read the record+0xa8
marker as a skip guard. Thus the identified already-prepared success path does
not itself prevent another operation-3 entrypoint call. The meaning and repeat
safety of operation 3 for each actual installed general plugin remain UNKNOWN.
Nonzero entrypoint results can clear state fields and continue the callback;
a successful PLUG_Search result alone would not prove absence of these effects.

Unprep is not a corrective workaround. It warns/returns nonzero when the prep
bit is absent, consults KeepLoaded, and can reach internal cache/eviction/unload
paths, clear the bit and change a counter. Setdown also invokes saved callbacks.
These branches were inspected, not called. Never unprep, unload or replay setup
to make a live baseline fit the experiment.

Thirteen addressed structural assertions and two table mappings passed. Private
review JSON SHA-256:
`51c7fb996a6596253656573fb4224ec6dafe9ba9a718ccdf63dcf39817512157`.
These are saved-text checks, not additional runtime/unit tests.

## Implemented conservative policy and journal

ResourcePassGate now binds a reviewed callback-inventory SHA-256 into the plan
and exact approval. Every baseline, immediate pre-call and successful postflight
must include a complete observed cleanup inventory matching that digest.
Unknown/missing observation is distinct from an observed empty vector.
Any retained general-plugin record blocks this candidate; there is no exception
for IsPrepped, KeepLoaded or null progress. Pre-call changes stop before the
call marker/search; post-call changes fail the result. Claims remain one-shot.

The journal serializes the approved digest and observed completeness/count in
claim/before/call-started/after records as applicable. Synthetic tests check
these bytes and twelve new rejection/change/replay cases. Native contract cases:
**82**, plus **32** real-files/processes journal cases; host observations/search
remain synthetic. Neither boolean attestations nor a well-formed digest prove
an actual complete callback inventory. No native reader or C1 backend is bound.
Observed zero retained records is necessary here, not sufficient for call safety.
All callback targets/context, reader consistency and native behavior still need
separate review. The conservative restriction must not be relaxed to get green.

## Continued read-only inventory preparation

PLUG's list imports resolve to LIST.dylib, absent from the current nine-image
live profile. Its original file was inspected in two bounded windows:
LIST_GetItem 0x2bfc–0x2c94 (38 instructions) and LIST_GetNumItems
0x2ffc–0x3038 (15 instructions). The handle is dereferenced; the body checks
magic 0x00d00bee and reads count at +0x10. Item retrieval reads element size
at +0x18 and copies from +0x48 + index*size. Its error branch can report an
error, so it must not be invoked as a supposedly inert reader.

New file-only LIST SHA-256, matching before/after:
`72be8af3e75c5e119e94cd6747e6bbbc25ec04f7f11c6451a918d8dea979e791`.
Private supplemental ZIP `resource-list-layout-5loyitaz.zip`, SHA-256
`adb96516ef20d4a4e1614d1c08fb047866b0ddaafe9ab812f3bcf6a57366f01d`,
source 52f4f80. It is a new static input, not retrospective resident-image proof
or adoption into the live profile. Allocation bounds, handle stability, actual
callback list and MEE vector identity remain unobserved. A native reader must
be reviewed before it can supply the policy's positive fields.

## CI failure, fix and verification

Local 3e67046 regression passed, 268 Python / 62 Node / 22 stages. Research CI
36924662951 passed Linux but failed macOS in test_real_output_limit:
killpg raised PermissionError during cleanup. The original failed artifact
11194030165 was downloaded and independently matched outer SHA-256
`2e095fdb7b0056d03d75d698ec9827ecd1656138bb5411d867fa2d44d4128e61`.
That failure remains FAIL, not a retroactive PASS.

52f4f80 handles denial only when the direct owned child is proven exited. The
bounded-output result remains FAIL and its pipe closes. Denial for a live child
still propagates. A new regression reproduced the prior exception before the
fix, then passed; the live-child denial test also passed. No limit, timeout or
required check was weakened, and no non-owned process was signalled.

| Gate | Current result |
|---|---|
| Collector regression | PASS, 10 tests, real owned file-backed code/data inspection |
| Clean current-source local macOS regression | PASS, 270 Python, no skips; 62 Node; 22 stages |
| Current source inventory before/after | PASS, exact clean 52f4f80, unchanged |
| Current research CI | PASS, [36925153427](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36925153427), Linux + macOS |
| Current full macOS CI | PASS, [36925153460](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36925153460), build/sign/package and synthetic smoke; no AE |
| Actual running callbacks / retained state | NOT OBSERVED |
| Native reader, C1 backend and live candidate | NOT READY |
| C1 registration/apply/render | NOT RUN |

Current local ZIP `AEHL-checks-_3fg_3z8.zip`, SHA-256
`5d5e61979bb4b360a1290dccfa2abfde03b03ecf732f8a44cd28fa287ef312c7`.
Nested native cases are included in the Python count, not counted twice.
The bounded code scanner inspected 237 supported files on clean code source
and 242 files with staged documentation (explicitly dirty source). Both report
no inventory omissions and the sole candidate is the known
artifact_manifest.py:71 local-argparse false positive. No finding was suppressed.
This is not a full security audit. CI results above belong to exact code source
52f4f80; the subsequent documentation-only checkpoint does not inherit a new
code/test run.

Current dependent gate: a complete fresh read-only callback/retained-state
observation with reviewed LIST/provider identity and consistency limits. No
positive live observation is inferred from this static record or synthetic
fixtures. Critical unknown callback behavior blocks connecting/executing C1,
as AI_ENTRYPOINT section 4.1 and PROCESS API-SOURCE-001 require. Continue only
independent file-only reader preparation until that prerequisite is resolved;
seek live approval against a concrete reviewed observer/candidate, never repeat
the resource call merely to see whether unrelated callbacks are safe.
