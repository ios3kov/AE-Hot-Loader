# C1 factory cleanup and dependent code lifetime

Stage C1 Development research, rules8.0.0 /132b7cd32873ba7328e3128ffbb33e1929b74d45.
Clean baseline e4275d199442d3e57924f473c9d2c658bade1ab1; AI_ENTRYPOINT first.
DEP-01–08 acceptance recorded in PRODUCTION_PLAN before implementation. Native
ownership/reentrancy/code lifetime Critical; API-SOURCE/testing/evidence/task-close/
cleanup apply. Existing SDK25.6_61 inventory reused, no new Adobe API/capture.
Original arbitrary ordinary-effect/no-restart product and A/B/C1/C2/D/release retained.

## Selected complete original cleanup paths

Reused historical receiver archive4ca1e665ec418b2bc7cde008b48ac67b1832865a,
resource-factory-receiver-6d31b658-jnlvecb2.zip. Independent verifier imports no
collector: original fat Mach-O/text nlist/body boundaries, raw direct/conditional/
indirect/return branches, selected register/VTT/dataflow and entire ZIP CRC/every
payload checked. Five complete bodies127 instructions: InterfaceRef3e9c–3efc,
zero-shared43dd8–43de4, D1 7540–7584, D2 7410–7540, zero-weak43de4–43e00.
15 direct/13 conditional/4 indirect sites/5 returns; original MEE file pin
18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344,
UUID74a30dba-a08b-367b-bd99-15d6d77e9d52 unchanged before/after.

Selected last strong-reference release can invoke virtual zero-shared at control
vptr+16. Factory control's delegate adjusts x0 by24 to embedded object and tail-
dispatches through its first vtable entry. Complete factory D1 supplies actual
VTT0xef6c0 in x1 to D2, invokes external dvacore UnknownBase cleanup and balances
a remaining weak field. D2 releases BOTH retained24-byte vectors (base fields+32
and+8): their last-owner paths invoke further virtual zero-shared then external
release_weak, before vector storage is freed. Zero-weak recycles104-byte storage.

This corroborates selected transitive teardown, already known as static history;
it is not a new runtime factory observation or complete callback graph. Indirect
runtime targets/provider objects, supported private acquisition/release/thread,
host-wide admission/render drain/atomic whole-effect rollback remain UNKNOWN.
Holding factory memory and its main code image alone does not certify the lifetime
of dynamically supplied callback code. Surviving control storage is not a live
factory or completed render. No count mutation/foreign teardown has been performed.

## Owned dependency bundle and actual native controls

[OwnedFactoryDependencyLease.hpp](../experiments/ordinary_discovery/OwnedFactoryDependencyLease.hpp)
wraps the existing owned nontrivial reference lease. Trusted reviewed profiles
enumerate1–8 unique dependency images, distinct from the factory image, each with
explicit owned version/teardown exports and exact full-body fingerprints. Only
already resident images are retained; bad/absent/duplicate/foreign profiles refuse.
The original factory profile must have the explicit owned anchor before dependency
access. No Adobe profile is accepted or dispatch/helper/gate added.

Every listed code image is held before factory acquisition and throughout result
destruction. Then handles close in explicit reverse order. Output remains at its
original raw heap address across moves. Move assignment cleans the old reference
with its old dependency set before transferring the new set. Partial dependency
acquisition and factory exceptions/malformed completed outputs balance own handles.
Dependency identity rechecks refuse diagnostics after an owned on-disk change;
cleanup uses the still-held original resident code.

The list is trusted owned research configuration, not an automatic discovery of a
host callback graph. Pinning code does not retain arbitrary provider objects, stop
MFR, authorize foreign operations or establish rollback. Completeness of a real
AE/provider list and actual object leases remain separate BLOCKED dependencies.

Fresh native stand: actual factory dylib and TWO providers whose callback addresses
are dynamically supplied, without direct Mach-O links from factory to providers.
The factory's real C++ object destructor calls both actual provider functions.
Harness closes all original library handles and drops its original object owner;
the bundle must preserve code/object lifetime until those calls finish. A consumer
guard stops before any stale callback if a provider unloads early. This is actual
owned native code execution, not a mock callback or an AE lifetime result.

Meaningful TDD: intentionally releasing dependency handles before the reference
fails normal and ASan/UBSan controls with exit85/dependency-unloaded-before-factory-
cleanup; absent/bad-binding/wrong-thread controls pass. Correct order removes that
failure. A preliminary observer omitted the factory image's own unload event and
still failed; corrected observation includes reference release→provider1 callback→
provider2 callback→factory object destruction→factory image unload→provider2 unload→
provider1 unload. Both preliminary results preserved, no retroactive PASS.

Same-lease cleanup reentrancy is guarded before state access: main-thread checking
comes first; diagnostics refuse during cleanup, nested Reset is idempotent, and
move construction/assignment terminate before transfer. This is a local ownership
guard, not whole-host admission or a claim that callbacks cannot occur. Actual
provider1 callback reenters the same lease; provider2 still executes normally before
either provider unloads. Separate reentrant-move child terminates before transfer.
Preliminary unguarded diagnostics failed with exit89; unguarded transfer led to
SIGABRT in the owned child. These failed results are retained. Owned consumer now
disables core generation only for its own child process; no system setting changed.

Five focused Python tests/nine fresh native processes PASS,23.796 seconds; strict
C++17 warnings-as-errors, including actual ASan/UBSan execution. Controls cover
absent factory/provider no creation/load, two actual teardown callbacks/reverse
unload, stable moves/move assignment, malformed result/exception/partial acquisition
cleanup, wrong source/UUID/span/role/anchor/version/missing export/thread, changed
owned file refusal/restoration, same-lease reentrant Reset/Diagnostic/transfer.
Full exact-source runner/scanner/manual/CI/evidence/status reconciliation remains
pending at this implementation checkpoint. Actual Adobe factory
acquisition/release/registration/apply/render NOT RUN; actual AE adapter BLOCKED.
