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

Full exact candidate checks, scanner, CI and final source/retention reconciliation
are pending at this implementation checkpoint. Live AE calls/registration/apply/
render NOT RUN; actual AE adapter BLOCKED by technical contracts above.
