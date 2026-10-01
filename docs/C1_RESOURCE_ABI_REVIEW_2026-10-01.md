# Stage C1: bounded resource-search ABI and cleanup review

Date: 2026-10-01. Branch: `research/ordinary-plugin-discovery`.
Code/test source: `5b88779b846d1e0dac5a50ef59f5fafc949d968f`.
Starting remote source: `9c142ed7b5c1f2da16dae0d672e08fff93b74eab`.

## Routing and acceptance

The user's request continues the established tool/panel contract under
AE-Development-Rules, source `05bd9a8d71c11280d972b96caf64b776f2a075d7`.
AI_ENTRYPOINT was read first. No new Product Discovery or Reference Audit is
triggered: neither the product direction nor an external parity target changed.
Delivery Gate is Development. Collector maintenance has Standard risk; native
C1 contract work has Critical risk. Apply Process scope/Git/identity/baseline/
regression/evidence, Engineering safety/debugging/reproducibility/compatibility,
and Helper/Tools resource and IPC boundaries. Render/pixel, user-validation and
public-distribution gates are outside this file-only change.

Acceptance: reproduce and fix the actual collector failure, test with real LLDB
on owned arm64 code, collect complete bounded windows from the reviewed files,
preserve their hashes, run available regressions, and separate static ABI facts
from live safety. No installation, AE launch/attachment, private call, scan,
provider retention, project change or main change is part of this work.

## Reproduction and fix

The unchanged collector stopped with `offline inspection tool failed` on the
real pinned aelib file. Running the exact saved LLDB script exposed
`invalid combination of options for the given command`.

Local LLDB help lists bounded start/end-address disassembly and forced whole-
function disassembly as different option sets. The [official LLDB command
map](https://lldb.llvm.org/use/map.html#disassemble-an-address-range) documents
the bounded command without `--force`.

Fix `ae325e03843a2254c6d8482a6e497ce927544a13` removes only `--force`. The new
regression compiles two owned arm64 instructions, gets their address from nm,
then executes the actual generated LLDB script without launching the bundle.
It failed on the old command and passed after the fix. Linux explicitly skips
that macOS tool integration; portable policy tests remain applicable.

Follow-up `5b88779` expands the existing two windows through the relevant
callback/search returns and verifies exact decoded coverage. Empty, partial,
duplicate, out-of-window and undecoded output cannot receive collector PASS.
This does not add a callable Adobe binding or make any ABI safe to invoke.

## Identified file-only evidence

| Input | SHA-256 | Reviewed window / decoded instructions |
|---|---|---|
| aelib | `f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f` | `[0x638cc, 0x63a70)`, 105 |
| PLUG.dylib | `12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22` | `[0x8a6c, 0x9028)`, 367 |

Both actual application files matched the pins before and after collection.
Report `resource-abi-988c3160-20zp8981.zip`, SHA-256
`da184dc4a695b9c681be32c0674a9d9d9a140925eb8cac161a8a0e7e6e3ad0f7`.
Final ZIP inventory and every archived payload were independently rechecked
against SHA256.json. Binaries and raw disassembly stay in private local evidence,
outside Git and public artifact handoff.

An additional file-only window `[0xe9f8, 0xed20)` covers ScanFolder,
DoCleanups and an adjacent directory predicate: 202 decoded instructions.
The same input pin was rechecked before/after. Private report
`resource-cleanup-am2e4j_w.zip`, SHA-256
`d0ca678b40f6f32bb285ad00493ff0c41903cb1a664cf25d41ffe8ad1dd634f5`.
It used the same reviewed LLDB-script, coverage and ZIP helpers; this is a
separate bounded analysis, not a new configured collector window.

## Argument evidence — OBSERVED for these exact files only

The defined/imported mangled symbol and the caller agree on ten arguments.
All addresses below are unslid evidence references, not callable offsets.

| Argument | Observed type | Caller location at PLUG_Search |
|---|---|---|
| sack | `PLUG_Sack**` | x0, null selects the existing default sack |
| root count | signed short | w1, 16-bit signed extraction from pointer-array length |
| roots | `FILE_Spec**` | x2, pointer array rather than path strings |
| flags | unsigned short | w3 = 0 in the normal caller |
| search value | short | w4 = 10 in the normal caller; meaning not invented |
| label | `char const*` | x5, U_ZLookupLStrCache result |
| progress | `int (*)(short, char const*, void*, unsigned char*)` | x6, SearchStatFunc |
| progress context | `void*` | x7 = null in the normal caller |
| errors | `int&` | caller stack +0, a pointer to the caller's int |
| cancellation | `unsigned char*` | caller stack +8 |

The caller keeps the folder-owner collection alive across the search and releases
it afterward. That is evidence for the startup caller's borrowed root lifetime;
it does not prove that every downstream registration path retains no state.

SearchStatFunc reads a host-global object and may invoke its virtual method
before returning zero. Reusing that private callback cannot be described as
an inert progress observer or as a newly reviewed public API.

## End-of-pass scope limit — OBSERVED, live implications UNVERIFIED

PLUG_Search reaches PLUGp_DoCleanups at 0x8ef4 with the selected sack and the
supplied progress callback/context. It merges the cleanup error with the search
result, then copies the search's local cancellation byte to the caller output.
Normal return unlocks its recursive mutex; separate unwind paths also exist.

DoCleanups reads the selected sack's callback list at offset 0x10. With a progress
callback, it reports stage 3/empty path and then invokes each stored cleanup
function/context pair. Without a progress callback, it still invokes the stored
cleanup pairs. Null progress does not turn this into a callback-free operation.
The list is selected by the sack, not filtered by the caller's single root here.

Therefore **one root bounds folder enumeration, but does not by itself bound
all end-of-pass host side effects**. Actual cleanup registrations, their retained
state and whether they are safe after startup are not identified by these
windows. They must be reviewed before an AE C1 backend is connected. Do not
replace callbacks, forge a sack, omit cleanup, replay startup or force registry
notifications to work around this gap. Timing checks between calls cannot
interrupt a blocked callback; external timeout remains evidence preservation,
not permission to kill AE or retry.

## Verification

| Check | Result / scope |
|---|---|
| Collector regression | PASS, six cases including real macOS LLDB on owned code |
| Pinned-file bounded collection | PASS, 472 complete decoded instructions, Adobe calls = 0 |
| Supplemental cleanup window | PASS, 202 complete decoded instructions, Adobe calls = 0 |
| Clean-head unified local macOS run | PASS, 264 Python tests, no skips, 62 Node tests, 22 stages |
| Source inventory before/after | PASS, exact clean `5b88779`, unchanged |
| Saved C0 evidence integrity | PASS, local ZIP hash and every payload rechecked; native 2/2 strings, 1/1 spec, three refs and final PASS present; no live rerun |
| Exact-head research CI | PASS, run 36920890724, Linux + macOS offline checks |
| Exact-head full macOS CI | PASS, run 36920890645, product build/sign/package/synthetic smoke; no live AE |
| Native C1 backend / registration / apply / render | NOT RUN / not connected |

Local unified ZIP `AEHL-checks-9_8eiqq0.zip`, SHA-256
`c54774bab957fa1ad2c683850c0c9e515f6a3e36007a59c5f09f51693e6fa70f`.
Nested native cases are included in the Python count, never counted twice.
Unified offline PASS does not claim the full AE pipeline or a product package.

The bounded static code scanner was rerun on the starting clean source (154
supported files) and on the final code plus staged documentation (171 files,
dirty documentation recorded explicitly). Both inspected four workflows, with
no inventory omissions in their selected scopes.
Its only candidate is the previously classified `artifact_manifest.py:71`
argparse false positive; it is a local CLI, not an authentication route.
No scanner finding was suppressed. This is not a full security audit or release
approval; history, dependency advisories and live behavior remain unassessed.

## Next concrete gate

Identify the cleanup registrations used by the existing default sack, review
their end-of-pass/retained-state contract, and then freeze the complete native
resource-call contract. Only afterward connect and test an inert C1 AEGP/backend
and independent one-shot supervisor with a fresh owned fixture.
Installation/live PLUG authorization must be sought against that concrete,
reviewed candidate; it is premature to request a live scan now.
C0 stays the recorded PASS. Ordinary-effect late registration remains unproven.
