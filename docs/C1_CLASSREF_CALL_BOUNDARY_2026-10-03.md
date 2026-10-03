# C1 native class-reference call boundary

Stage C1 Development research, accepted rules8.0.0 /
132b7cd32873ba7328e3128ffbb33e1929b74d45. Starting clean72fefe9f2cdac41422fe8c1210791a4fc881a494.
CALL-01–08 acceptance in [production plan](PRODUCTION_PLAN.md) before implementation.
Native ABI/unwind/lifetime Critical; API-SOURCE/thread/ownership/refusal/repro,
task-close/cleanup apply. SDK25.6_61 inventory reused; no new Adobe API call.
Original arbitrary ordinary-effect/no-restart product and A/B/C1/C2/D/release retained.
This prepares an owned native call prototype, not an enabled AE diagnostic/adapter.

## Actual file call and destructor boundary

Reused complete bodies from immutable historical receiver4ca1e66 and identitye70d13c
archives, preserving their original identities. No new Adobe body collection or
unchanged scan. Independent verifier imports no collector: original fat Mach-O
mapping, raw direct/conditional/indirect/return instructions, selected register/
result/control-field dataflow, exact next defined-text-symbol boundaries and every
ZIP payload/CRC verified. Four bodies399 instructions: recv-interface-dtor3e9c–3efc,
recv-instance71b4–73e4, recv-create-instance3e150–3e234, factory-classref43944–43c0c.
55 direct/44 conditional branches/10 indirect sites/7 returns checked.
MEE25.6x101 arm64 SHA18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344,
UUID74a30dba-a08b-367b-bd99-15d6d77e9d52 unchanged before/after.

CreateInstanceRef caller sets x8=sp+8 at3e168, w0=1 at3e16c and directly calls43944
at3e170. Callee copies bool x0→x21 and output x8→x19. Previous complete false-CFG
review remains applicable: false skips factory allocation/ClassWatcher/weak replacement,
but static guards/mutex/atexit and owner retention/release can still have side effects.

Interface reference D1 reads control at result+16 (3eac). Instance saves caller's
whole output base x8→x19 (71c8), passes x19→x0 (73b8), calls3e9c (73bc) on cleanup.
Pass the **entire24-byte result**, not the internal pair starting at+8. Incorrect
offset would make this destructor read outside the result. This reference destructor
is distinct from factory-object D1/D2 and its hidden construction table. No foreign
refcount/deleting destructor or guessed C++ class has been invoked.

LLDB displays InterfaceRef<ML::IPiPL>; retained-nm prefix search initially showed
one factory reference symbol. Independent raw original nlist resolves that limited
view:12 defined text entries share3e9c, including factory InterfaceRef D1 and IPiPL
InterfaceRef D1. Exact address/body/dataflow corroborated; names/shared entry do not
establish supported host ABI or the precise compiler/linker folding mechanism.
Preliminary verifier's one-name assertion refused and was corrected from original
metadata; no final claim rests on the preliminary symbol count.

## Implemented native carrier and stable output

[ClassRefCallBridge.S](../experiments/ordinary_discovery/ClassRefCallBridge.S)
provides two narrow macOS arm64/non-arm64e routines. Acquisition transfers owned
entry address to x16, caller result to x8, hardwires w0=0 and calls the entry.
Destruction passes whole result address in x0. Both keep16-byte-aligned stack and
save frame pointer/link register with CFI so an owned C++ exception can unwind.
There is no runtime creation flag, Adobe import or helper/gate integration.

[NativeClassRefCallLease.hpp](../experiments/ordinary_discovery/NativeClassRefCallLease.hpp)
requires the explicit repo-owned version anchor and exact acquisition/destruction
exports. Continuous ImageLease checks pin/UUID/direct exports/resident code; Bind
verifies both reviewed full-body fingerprints; target role/address must match exact
exports before version/acquisition calls. MEE identity profile refuses immediately.
No conversion of an invented C++ return type/function pointer is used for the
nontrivial return: machine carrier writes to opaque raw storage where the owned
callee constructs its actual C++ reference.

Result storage is a stable raw heap allocation with8-byte fences around24-byte
output. Move transfers allocation ownership, preserving the reference object's
address; it does not memcpy a nontrivial C++ object. Completed result is marked only
after normal return. Exception before construction frees raw storage without calling
the result destructor. Malformed completed result still invokes the owned destructor
at the full base before freeing storage/closing its code image. Disk identity changes
refuse Diagnostic while cleanup retains the originally trusted resident destructor.
Wrong-thread release/move terminates before callbacks in fresh owned test children.
Output shape remains diagnostic, not an AE liveness/call capability.

[AE256FactoryReferenceIdentityProfile.hpp](../experiments/ordinary_discovery/AE256FactoryReferenceIdentityProfile.hpp)
is separate immutable **identity-only** MEE profile, not callable ABI. Exact spans:
InterfaceRef D1 at3e9c/96 bytes, SHA bf3f1ce55990c5a427b6d0d87121fece1ec39664ff6c8f004c7dfbb5f578162c;
classref43944/712 bytes, SHA d83f18648d10cd58e84460929e30e0a209b6a659ea03a67a57b73ed183a054a3.
Strict compiled file-only check validates pin, UUID, both spans against original
MEE bytes, without resident access/Adobe calls. Own binder explicitly rejects it.

Sources checked2026-10-03: [Arm AAPCS64 §6.9](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
(2025Q4, issued2026-01-23) for indirect result x8 and stack/frame rules; selected
installed Apple clang21.0.0/Xcode SDK for actual owned compilation/execution.
Apple ARM64 documentation endpoint yielded JS content and its Markdown link failed;
no unavailable Apple page content is claimed. Arm standard is general ABI context;
the actual owned nontrivial C++ return/unwind is tested separately. Neither supplies
an Adobe private declaration/thread/lifecycle contract.

## Focused evidence and retained preliminary results

Four Python tests PASS, six fresh native fixture processes including one ASan/UBSan
run. Owned callee returns an actual nontrivial24-byte C++ Reference, with actual
typed shared ownership entirely inside the dylib. Its internal slot-address map
checks destructor base and would reject copied/shifted reference storage. The owned
block prefix is an opaque test token, not a libc++/Adobe control-block reconstruction.

Real checks: hardwired false, full x8 output/canary bounds, whole-base destruction,
absent/expired no creation, source/UUID/hash/span/tag/anchor/version/missing-target
refusals, worker-thread acquire/release/transfer, malformed output cleanup, actual
exception before output construction through assembly CFI, stable move construction/
assignment, last original owner removal, use through held code after harness dlclose,
release→object destruction before image close. Atomic owned-file replacement refuses
diagnostic and restores original bytes. Actual owned unload is observed/reportable,
not promised for host libraries. No fixture accesses Adobe state or resources.

Meaningful runtime TDD: preliminary bridge passed create=true; normal and sanitized
native controls FAIL with creation-request-forbidden, while bind-refusal control
PASS. Replacing carrier flag with constant false makes all focused checks PASS.
Final ABI/lifetime results do not retroactively mark that preliminary bridge PASS.

Full exact-source regression/scanner/CI and final evidence/documentation/cleanup
reconciliation pending at this implementation checkpoint. Real AE private
acquisition/release/registration/apply/render NOT RUN; actual adapter BLOCKED.
