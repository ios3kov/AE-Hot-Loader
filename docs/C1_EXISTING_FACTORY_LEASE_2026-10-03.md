# C1 existing factory acquisition and code lifetime

Stage C1 Development research, rules8.0.0 /
132b7cd32873ba7328e3128ffbb33e1929b74d45; starting clean147761b0755da43f1008baf6a34a064a8513ce31.
LEASE-01–08 acceptance recorded in [production plan](PRODUCTION_PLAN.md) before
implementation. Native reference/image ownership Critical; API-SOURCE, thread,
ownership, refusal/repro/evidence, task-close/cleanup apply. SDK25.6_61 inventory
reused, no new Adobe API call. Original ordinary-effect/no-restart product and
A/B/C1/C2/D/release obligations retained. Owned prototype is not an AE adapter.

## Non-creating does not mean read-only

Reused immutable historical factory-identity archive from tested e70d13c693977449e27cf50dcb3e5a388e08a87e,
SHA b10b56a1b6b3edae3246a7de7b6192a139901f27590f9cc72d5102fd6ecbf472,
26 members. No new Adobe body collection/scan. Independent verifier imports no
collector: archive CRC/every manifest payload, original fat Mach-O mapping, all
25 direct/24 conditional branches, result stores, exact nlist next-body boundary,
before/after original-file SHA and complete classref span hash checked.
MEE25.6x101 arm64 SHA18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344,
UUID74a30dba-a08b-367b-bd99-15d6d77e9d52;43944–43c0c contains178 instructions,
span SHA d83f18648d10cd58e84460929e30e0a209b6a659ea03a67a57b73ed183a054a3.

Input x0 is copied to x21 at43958; indirect result location x8 to x19 at4395c.
Conservative normal CFG permits both paths of unknown conditions except the
actual false flag at439cc→43a8c. Allocation call439d8→43c38, ClassWatcher AddObject
439f0→a049c and weak-singleton replacement43a80 are unreachable in that selected
false CFG. This is file control flow, not observed host execution/exception proof.
Static guards4396c/4397c still reach guard acquire and atexit43b64/43ba0 on first
use; mutex lock43988, weak-owner lock4399c and normal unlock43b24 remain reachable.
Even the non-creating path can initialize lifecycle state and retain/release owners.

Absent result stores zero pair at+8 plus primary at+0; retained result stores
adjusted interface/control pair43ae8 after a strong retain43a98. Local owner release
occurs before mutex unlock. Raw output24 bytes and these branches do not establish
supported callable Adobe C++ ABI, initial object reachability, module lifetime,
late-host admission, render drain or whole-effect rollback. Existing tuple decoder
is shape-only; no foreign shared_ptr/refcount/destructor is synthesized.

## Implemented bounded native prototype

[ResidentImageLease.hpp](../experiments/ordinary_discovery/ResidentImageLease.hpp)
retains an already resident image with RTLD_NOLOAD|NOW|LOCAL|FIRST. Before any
owned entrypoint: main thread, exact path/file SHA, Mach-O arm64 UUID, direct code
exports, mapped header/text, exact dlsym/export address correspondence and stable
image snapshots. Absence refuses without loading. Fresh callable lookup and owned
Value recheck source identity. Handle continuously owns code residency; it does not
prove host-wide exclusion or permission to unload a host module. Normal cleanup
balances only the handle acquired by this component. Release/transfer off main
thread terminates before module callbacks; this is an internal programming invariant,
not a user-facing recovery policy. No AE helper/gate integration.

[NativeExistingFactoryLease.hpp](../experiments/ordinary_discovery/NativeExistingFactoryLease.hpp)
uses only [OwnedFactoryAbi.hpp](../experiments/ordinary_discovery/OwnedFactoryAbi.hpp):
four explicitly declared repo-owned C exports, exact version,24-byte trivial
object/opaque-owner/generation result. It never reconstructs C++ shared ownership
from integers. A nonnull owner is released exactly once through the same module's
declared nonthrowing release operation, including malformed-result refusal.
All-zero absence closes the module lease. Move transfers the existing acquisition;
move assignment releases its former acquisition first. Reference destruction
precedes image close. Value refuses empty/wrong-thread/changed-source use.
Trusted owned ABI is required; hostile module output is not made safe by shape checks.

Fresh test dylib implements actual mutex-protected weak singleton and heap Owner
holding typed std::shared_ptr entirely inside the module. Only explicit test Seed
creates a Factory; Acquire merely weak-locks. No test code touches Adobe objects.
Generation is our owned ABI field, not an Adobe classref field/layout inference.

Platform sources checked2026-10-03: installed selected Xcode SDK dlfcn.h and
Apple clang21.0.0; [Apple dlopen manual](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/dlopen.3.html)
documents refcounted NOLOAD handles and FIRST symbol scope. [Arm AAPCS64](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
describes x8 indirect result passing. Declared owned contract and real compiled
cross-module calls substantiate this prototype; neither source supplies Adobe ABI.

## Focused verification and preliminary failures

Five focused Python tests PASS, six fresh native fixture processes, including one
ASan/UBSan run. Absent/expired acquisition creates nothing; malformed interface or
generation releases the acquired owner; wrong hash/UUID, zero UUID and worker-thread
acquire refuse before acquisition. Wrong-version/missing-release native modules
acquire zero references. Move assignment/constructor leave moved-from leases empty,
last original strong owner can disappear while transferred owner remains usable;
final strong destruction exactly once. Reacquisition after expiry stays absent;
explicit replacement uses a new generation. Harness drops its original dlopen handle
while final lease still calls Value, then observes release→object destructor before
image close. Tests report whether actual image unload occurs; no unload guarantee
or Adobe lifetime claim follows from that observation.

Initial strict compiler refusals retained (nontrivial defaulted C aggregate and
const code-address conversion), repaired without suppressing warnings. Runtime TDD
added atomic replacement of the fresh owned file: before Function identity recheck,
two normal/sanitized tests FAIL; after recheck all five focused tests PASS. Replacement
never truncates a mapped file, restores original bytes; cleanup still releases the
originally trusted owner through resident code. Initial missing-header test log was
not retained; no acceptance claim is based on it.

## Exact-source verification and final reconciliation

Tested clean code **a9a7f7211f9d2ee2e12cae05600a4dbcb6045e2b**. Private unified runner
/private/tmp/AEHL-checks-sqjmfuec.zip SHA **8cc8ef710d2930d89f0f385b50058514265cdd839424033318ba0169a6f50f63**:455 Python/no skips,
zero failures/errors/expected failures/unexpected successes;62 Node; all22 stages
PASS. Python79.886 seconds. Independent ZIP CRC/every manifest payload and all353
Git blob/working source bytes verified, source_unchanged_after=true. Source-proof
SHA **6ceae6aca0e23a9a5fe72a98eb7c260a635a9a08af1e49f7edc26cfc90d36c29**. No installable AE candidate or runtime result is claimed.

Scanner on fresh clean local Git clone:353 tracked Git/working/copied byte hashes
equal;238 supported text files,115 unsupported type files, omissions[]; all selected
checks complete. C++/headers are among unsupported regex types and were separately
manually reviewed/strictly compiled/executed with ASan/UBSan. Raw exit1 /
review_required /release_readiness=not_assessed retained; sole candidate
vibe.no_ratelimit_auth tools/artifact_manifest.py:71 is the local argparse mode
choice 'verify', no HTTP/auth route/listener. Manual false-positive review, no
suppression. Raw scanner SHA **c56af1c3b4059af8f1b78b7e367e1da7e1184784f217274d0239d0609fe17ebb**; manual review SHA **7c86d637f8809b1a75141b321ea889cf43e2a4118aac8f8fd56dce4021d95697**.

Research CI [37141951178](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37141951178)
and macOS CI [37141951225](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37141951225)
both completed/success at exact tested source above. Linux/macOS own distinct
platform applicability; local455/no-skips is macOS arm64, not a Linux native claim.
CI builds/smokes/archives are offline and do not prove AE loading/registration/render.

Separate current raw original-body receipt SHA **7316d3312e3e1e679aeb4ceb4631e98d477d701b2bebc575a978d31018001709**.
Both separate exact-artifact native and ASan/UBSan stands retain executable/dylib
bytes, commands, hashes, stdout and unchanged-after results: receipt SHA **2ad03dda7ed68027394abd2fc2daf74781de31e97e35077348258de20639be77**.
Both observe unload_observed=1 after release→factory destruction; fresh fixture
modules only, no Adobe image/reference teardown. Owned ABI lifetime is PASS;
the corresponding actual Adobe ABI/lifetime operation remains BLOCKED/NOT RUN.

Durable private receipts: build-ae-hot-loader/lease-closeout-a9a7f72-koet973k; retained native
artifacts: build-ae-hot-loader/lease-native-a9a7f72-mba7cscu. RETENTION.json SHA
**5fb7722f45469a3ba3871ece70a03044b1c73e29dd963cfb974dc318132b5a8d** covers the runner, source proof, independent verifier/receipt,
raw scanner/manual review, platform sources, compiler/TDD/focused observations,
CI and cleanup receipt plus exact native artifact hashes. Preliminary compiler
and runtime FAIL logs preserved; no retrospective PASS applied to those attempts.
Historical original capture retains its original source identity. Fresh scanner
clone removed only after clean/no-unique-commit check, complete byte proof and
retention; ephemeral fixtures cleaned by their own TemporaryDirectory. Retained
artifacts, original/shared/historical materials, app/SDK/projects/plugins untouched.

| Requirement | Final bounded result / evidence | Remaining dependency |
|---|---|---|
| LEASE-01 |178-row original body, all branch/store/nlist/pin/archive checks PASS; false skips creation, guards/atexit still reachable | AE execution NOT OBSERVED |
| LEASE-02 | x0/x8/result stores and selected lifetime/lock exits documented | Private callable ABI/initial live receiver UNKNOWN |
| LEASE-03 | Resident-only exact-pin/UUID/export RAII image lease implemented, actual owned cross-dylib code lifetime PASS | Foreign host lifecycle authority/admission not established |
| LEASE-04 | Explicit owned24-byte opaque reference/version ABI and consumer implemented | Not Adobe InterfaceRef or production bridge |
| LEASE-05 | Real weak acquisition, absent/expired no creation, ownership moves/destruction and code residency PASS, actual owned unload observed | Actual AE factory acquisition/release NOT RUN |
| LEASE-06 | Wrong source/UUID/version/export/ref/thread and stale-call refusals PASS; TDD repaired; ASan/UBSan PASS | Trusted owned contract, not hostile-output or AE liveness certification |
| LEASE-07 |455 Python/62 Node/22 stages, raw scanner/manual review and both exact-source CI reconciled | Full AE registration/apply/render and broader compatibility NOT RUN |
| LEASE-08 | Source/ZIP/native-artifact/CI/retention/cleanup and current docs reconciled | Original A/B/C1/C2/D/release gates retained OPEN |

Eight blocks close the bounded owned-code/lifetime research packet; full product
is **PARTIAL**. Actual AE adapter remains BLOCKED: establish the real retained
receiver and callable acquisition/release/thread contract, then safe late-host
admission/drain/whole-effect rollback before registration/apply/render. This pass
does not bypass ResourcePassGate, repeat unchanged scan, merge or release.
Docs-only closeout must compare every non-document Git blob/working byte against
the tested code; evidence does not relabel its later documentation SHA as tested.
