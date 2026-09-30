# Stage C: scoped resource-pass policy and integration boundary

Date: 2026-09-30. Continues `1e69244c760afd8848787c6c86a364ae9a9faa55`
on `research/ordinary-plugin-discovery`. AGENTS, current status, PRODUCTION_PLAN
and the shared DEVELOPMENT_RULES were read; rules blob remains
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

**Implemented: an unbound C++ transaction policy and executable model tests.
NOT implemented: an AE backend, private ABI binding, new AEGP artifact or a
runnable resource-registration experiment.** This is a preparation step, not
a loader fix or an instruction to install/run anything on the user's Mac.

The user's instruction to proceed follows preparation of a bounded test. It
is not treated as a replacement for the separate risky-operation authorization
required by the preceding checkpoint. The original installation and restart
authorization remains consumed.

## Scope and acceptance

Define an exact one-root transaction; require fresh host/project observations,
loaded-image pins, a new explicit approval and a durable one-shot claim; test
failure handling, release ordering and exact registry acceptance without Adobe
execution. Preserve the product loader and existing scoped harness. Run the
available Python/Node regressions, compile/run the synthetic C++ cases, check
memory diagnostics, compare uploaded source bytes and inspect CI separately.

Current runtime baseline remains the historical `scoped-0b8c8f122e80` FAIL,
source `45de0c9`, fixture `88019a1a01a7`, 785 unchanged effects. The new policy
explicitly rejects that consumed fixture identity. RSMB startup-registered
apply/render PASS and historical RSMB late-registration FAIL stay separate.
No new host state, installed identity or late-registration success is claimed.

## Additional FILE_Spec ownership evidence

The previously supplied aelib bytes were read again and independently hashed:
`f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f`.
No binary was loaded as code. The arm64 symbol table's library ordinal 30 maps
both FILE_New's string overload and FILE_Dispose to `FILE.dylib`.

In the inspected FILESpecFromDVA<Dir> helper, a path value is obtained, passed
to FILE_New at 0x63688, and the returned x0 is retained. Replacing an existing
owned value calls FILE_Dispose at 0x6369c before storing the new value. The
FILE_ScSpec destructor at 0x3a4f0 loads that pointer, clears its storage and
calls FILE_Dispose at 0x3a50c when non-null. These callers pass the pointer,
not an invented FILE_Spec buffer or pointer-to-pointer ownership structure.
The temporary path string is subsequently released by the host allocator.

Four direct branches were checked against their raw 32-bit instruction words:
FILE_New at 0x63688 -> 0x8ba34; FILE_Dispose at 0x6369c and 0x3a50c ->
0x8b26c; PLUG_Search at 0x6399c -> 0x8b53c. These are static checks, not
executed private calls or a complete ABI proof. The ordinary folder-owner
collection remains live through PLUG_Search and is released after it.

This supports the intended ownership pattern but does NOT finish the native
contract. FILE_New accepts a host C++ string with a dvacore allocator, not a
UTF-8 char pointer. FILE.dylib's implementation bytes were not supplied, and
post-search retained-reference semantics are not established by these callers.
Do not manufacture FILE_Spec, reinterpret std::string, transplant raw pointers
or reuse the old loader's assumed string layout as a proven FILE_New ABI.

## Implemented policy

Source/test commit: `1d90cb6ced210f340a72f05488a34f78129e2ef6`.

- `experiments/ordinary_discovery/ResourcePassGate.hpp`: standard C++17 policy;
  no SDK dependency, Adobe symbol binding, entrypoint or production integration.
- `tests/resource_pass_gate.cpp`: 63 named synthetic cases, including success,
  refusal, errors, state changes and one-shot behavior.
- `tests/test_resource_pass_gate.py`: compiles/runs those cases as one Python
  unittest, under both existing CI regression workflows. Compilation failure
  is an error, not a silently skipped test.

The policy freezes the plan and binds approval to its entire scope: new Run ID,
source, bridge hash, fixture-manifest hash, root, match, host path, image pins and
time budget. Both approval flags default false. **Those fields are assertions
from a future trusted supervisor, not a consent-verification mechanism.**
Setting them in test data does not grant user authorization or verify an ABI.

The proposed native adapter must supply these operations:

1. Validate the exact owned embedded-fixture inventory and collect fresh host,
   loaded-module, project and registry observations on the main thread.
2. Publish a durable exclusive claim before creating a file specification.
   Existing, partial or consumed records must refuse replay. Reuse the existing
   scoped::Save/VerifyScope facilities instead of weakening their checks.
3. Create a host-owned specification for exactly the approved root; verify its
   path roundtrip. Recheck inventory, PID/start, project revision and registry
   immediately before the single-root operation.
4. Persist a call marker, then perform at most one resource pass. The backend
   accepts one opaque specification, not a caller-supplied list of global roots.
5. Release that specification once; retain one postflight attempt on normal
   return or an exception. Do not repeat a failed observation automatically.
6. Accept only zero return, zero reported errors, no cancellation, successful
   release, unchanged PID/start/project/images and exactly the new fixture match
   added to the complete registry. Recheck the fixture inventory afterward.

Canonical path validation in the policy is lexical; it does NOT replace the
backend's real ownership, symlink and file-hash checks. The required image-pin
keys are AfterEffects, FILE, FLT, MEE, PLUG, PluginSupport and aelib. No actual
live set has been populated or verified in this iteration; test hashes are
synthetic. Additional dependency requirements must be assessed with the adapter.

The abstract Backend is intentionally unimplemented except for the test Model.
Its observations, durable storage and private operation are not independently
proven by these tests. A returned policy PASS is only a decision over supplied
observations; the independent external supervisor must still verify evidence
bytes and runtime identity before a live gate could pass.

The maximum policy budget is 15 seconds. Deadline checks occur between callbacks
and after return; they cannot interrupt a blocked host/native call. A bounded
external supervisor and cooperative cancellation semantics remain required.
A timeout must retain the claim and must never force unload, kill AE or retry.

## Binding requirements and forbidden shortcuts

No native backend may be connected until FILE_New's string ABI, error behavior,
ownership and release contract are reviewed; loaded-function/module provenance
is verified; and the exact single-root PLUG_Search argument/callback contract is
specified. A first separate adapter check should only create, roundtrip and
release a specification before any resource scan is proposed.

The later scan must retain the installed skip predicate and existing FLT scan
callback. It must not call Egg_PlugSearch or MEE_GetPluginsFolders (global roots),
Birth/InitIterator/RequiredPreSearch (lifecycle), replace callbacks, clear caches,
force module notification, change the loader's bool, or perform another
ML::LoadPlugins pass alongside the resource pass. Otherwise it would no longer
isolate the missing-resource-pass hypothesis.

Any native bridge must be a separately identified research-only build, not a
change to the installed Agent or product button. Existing ScopedDiscovery.cpp,
its builder and its supervisor still run their original path; **do not use
those existing commands expecting this new resource policy to be connected.**
Fresh fixture build, native binding, SDK build/signing/inert-entry tests, real
storage/supervisor integration, explicit new approval and a fresh live baseline
remain mandatory before a user-run experiment. Apply/render remains separate.

## Verification

| Check | Result and limits |
|---|---|
| Local native model | PASS, 63/63 named cases, Linux x86_64, clang C++17 |
| AddressSanitizer + UndefinedBehaviorSanitizer | PASS, same 63 model cases with leak detection; not AE memory coverage |
| Local Python with warnings as errors | 209 collected: 203 PASS, six macOS-only skips |
| Local Node | 62/62 PASS, panel/snapshot mocks |
| Source byte comparison with Git blobs | PASS for all three new files |
| Research CI for 1d90cb6 | PASS, run 36759252657; 203 Python PASS/six skips, all 63 nested native cases, 62 Node PASS |
| Full macOS CI for 1d90cb6 | IN PROGRESS when this record was written, run 36759252333; no full PASS asserted |
| Native AE backend / resource bridge artifact | NOT IMPLEMENTED; experiment BLOCKED |
| New real AE registration/apply/render | NOT RUN |
| Current AE/project/loaded identities | NOT OBSERVED |
| Full static-security audit | NOT RUN again; five previously recorded findings remain unresolved |

The 63 C++ cases are nested in one Python test; they are not added again to the
209 Python count. Model claims are in-memory: their replay tests do not prove
filesystem durability, crash survival, restart safety or storage race freedom.

Research evidence artifact `11118196977` was downloaded and independently hashed:
`3d34e83a4a1a942f04939b870b7237a89743cdc7495954a567f35cf44fc4688c`.
Its source record identifies 1d90cb6; Python output confirms all 63 unique cases,
209 collected tests and six skips. Node TAP files confirm 51 + 11 passes.
The macOS workflow is tracked separately; a green research job is not substituted
for its final result. Green CI does not clear unreviewed annotations/warnings.

| New source | SHA-256 |
|---|---|
| ResourcePassGate.hpp | `1bc259f7a91e12ff632b480f18e0d52671e25be4b19d830df8cb6e2f219eff7e` |
| resource_pass_gate.cpp | `f67cb3bc61be713dc3792b51b8e1efb7ff0e6be3511a89554ecf8adeb685de80` |
| test_resource_pass_gate.py | `383f67a6f771172ed5b5ecd8dea9b5efda0a9e33894365941e198c6648f07448` |

Local regression used the previously hash-verified CI source archive for 1fa62a7
plus the three new files. GitHub comparison to 1e69244 confirmed intervening
changes were documentation-only; each new tested file matches its pushed Git
blob. This was a reconstructed working copy, not the user's Mac checkout.
The source evidence ZIP hash is
`8dce528f29e780985e64881c8024041584f8e1738f70563cb89c7b57f4e11c0b`.

No installation, restart, main change, merge, release, project/settings mutation
or third-party-plugin change occurred. Documentation follow-ups use [skip ci];
verified code and CI identities above remain explicit. No installable artifact
or new command is being handed to the user. The next development work is the
native adapter contract and its isolated checks, not a speculative live scan.
