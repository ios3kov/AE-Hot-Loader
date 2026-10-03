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

Five focused Python test methods/eight fresh native consumer processes PASS,
23.796 seconds (1+1+2+1+3 variants). Nine was a preliminary arithmetic error;
native variants are not added again to the Python count.

## Final DEP-01–08 reconciliation

The bounded owned callback-code lifetime packet is complete at clean tested source **a75a5aa15044b4a4606e5fe39a4185f018fbfab4**. Fresh unified runner /private/tmp/AEHL-checks-1aqo0h86.zip, SHA **b59cea43e8fe5b6fb32400379535d2f56e6d43226c7ad8ed07b91477dc4b4f2c**: 464 Python tests/no skips, 62 Node, all 22 stages PASS. All 365 tracked Git/working/copied bytes matched before and after; source-proof SHA **84c579aa63ba01905a065f080f831485412c4e1df68df6313c102bc5f911c947**. ZIP integrity and all manifest payloads checked.

Fresh-clone scanner reviewed 242 supported text files and 123 unsupported file types, omissions[]. All selected checks completed. Raw exit1/review_required/release_readiness=not_assessed retained. One heuristic at tools/artifact_manifest.py:71 matches the local argparse choice verify; the manifest CLI has no HTTP/auth route. Manual false-positive review, no suppression. Scanner SHA **57f0180eff1155e3357e3ccf7437fb8a0a3c5f72c53c1a3e8709e5fdc8b86711**; manual review SHA **b375f581abbc9ff5cc5268c2e0df46cba81907b10de1888da400968f4efbe925**. Native files received separate strict compilation, actual execution and ASan/UBSan.

Research CI [37144996949](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37144996949) and macOS CI [37144996954](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37144996954) both completed successfully at exact source; panel-contract, native-syntax and macOS build jobs passed.

Independent original review SHA **4fe54e64d6ee112c0099e967b23df0314d90f9278989559df6592f065635ab15** binds five complete reused MEE cleanup bodies: 127 instructions, 15 direct, 13 conditional, 4 indirect sites, 5 returns. Pinned MEE bytes and UUID unchanged. Selected paths release the factory and two retained vectors/weak owners. Actual indirect provider targets/full host callback graph remain unknown.

Retained regular and ASan/UBSan three-module stands SHA **f7d12f87492fbde9eda51c2c9ff14188090854fc7739d3fdd00b86c045c8eeda** bind exact binaries, commands, output, and unchanged-after hashes. Actual dynamically supplied callbacks ran during factory destruction after harness handles and original owner dropped. Event order 2,30,40,1,3,41,31 records reference release, both callbacks, object destruction, factory unload, then provider unload in reverse. Reentrant Diagnostic refuses, nested Reset is idempotent, reentrant transfer terminates before state transfer. Five focused methods run eight fresh consumer processes; nine was an incorrect preliminary count.

Wrong-order and reentry TDD failures and fixes remain preserved. The first unload observer that omitted factory unload remains labelled FAIL. Private evidence under build-ae-hot-loader/dep-closeout-final-a75a5aa-hhb7z2ok; RETENTION.json SHA **c7f7f95cdb807f47980872587137f779f8fdfe04f9b2e8eda92fc61f84e1e95b** binds source, runner, scanner, manual/original review, CI and native files. Only the packet-owned clean scanner clone was removed after byte-proof checks; historical/shared/app/SDK/project/plugin state untouched.

| Requirement | Result | Remaining dependency |
|---|---|---|
| DEP-01 | Five complete cleanup bodies independently reviewed against original bytes and control/vector transitions | Complete host callback graph unknown |
| DEP-02 | Object, factory image, and listed provider code lifetimes distinguished | Provider object ownership/hidden dependencies unknown |
| DEP-03 | Owned lease retains 1–8 unique, already-resident pinned provider images with exact exports and code fingerprints | No Adobe profile or auto-discovery |
| DEP-04 | Factory result destroyed before providers; handles close in reverse order; move assignment releases old bundle first | No host-wide admission/render barrier |
| DEP-05 | Two actual owned callbacks run after harness handles and original owner drop; regular/sanitized sequence pass | Does not establish Adobe behavior |
| DEP-06 | Wrong-order, profile, source, version, thread, partial, exception and reentry controls checked | Actual host semantics unknown |
| DEP-07 | 464 Python/no skips, 62 Node, 22 stages; scanner/manual/original/native checks and both exact-source CI complete | AE registration/apply/render NOT RUN |
| DEP-08 | Plan/status/handoff/compatibility/checkpoint/retention/corrections/cleanup reconciled | A/B/C1/C2/D/release remain open |

Product remains partial; the AE adapter is not ready. Actual AE acquisition/release, provider-object lifetime, full dependency graph, registration, apply and render remain unknown or not run. Next establish the actual receiver's callback/provider-object ownership and thread contract, then prove host-wide late-entry exclusion, render/MFR drain and whole-effect rollback. This packet does not establish ordinary effect discovery or creation without restarting AE.
