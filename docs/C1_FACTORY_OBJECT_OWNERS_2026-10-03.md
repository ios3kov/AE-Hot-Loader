# C1 actual factory object owners and host prerequisites

Stage C1 Development research, rules8.0.0 /132b7cd32873ba7328e3128ffbb33e1929b74d45.
Clean baseline4a89b3ffeea929015156f65b32a8bcdc0ef3c637; AI_ENTRYPOINT first.
OBJ-01–12 acceptance recorded in PRODUCTION_PLAN before new capture. Native
ownership/ABI/reentry Critical, fixed collector Standard; API-SOURCE, exact-source
verification, TASK-CLOSE and CLEANUP apply. Existing SDK25.6_61 inventory reused;
no new Adobe API call, native host adapter or installable candidate.
Original ordinary-effect/no-restart product and A/B/C1/C2/D/release retained.

## Selected original-file owner chain

Pinned AE25.6x101 arm64 MEE and PluginSupport. Addresses below are file locations,
never live pointers or a public callable ABI. New factory-objects mode covers
eight complete bodies /325 instructions, all325 instruction anchors, and five
serialized destructor slots. Existing receiver/identity/admission/provider/
isolation/entry/registry bodies are reused with historical identities preserved.

| Owner boundary | Selected file evidence | Meaning and limit |
|---|---|---|
| Factory → modules | Constructor73e4 zeroes two vectors; Create7660 inserts module into +8/+10/+18 before Init; GetModules8e84 returns separately retained references; destructor7410 releases both vectors | Module roster and ordinary effect registry are distinct. Object retention alone cannot establish successful Init/SetupFilter/publication. |
| Factory → special plug-ins | CreateUnknownImpl retains a plug-in in separate +20/+28/+30 vector on its special lane, then returns null/status0 | Factory can retain a plug-in without publishing a ready effect. Actual branch/receiver in AE not observed. |
| Module → PluginImpl/PiPL | Constructor3df8 zeroes +d8…+100; existing Init408c retains PluginImpl triple+d8/+e0/+e8 and PiPL triple+f0/+f8/+100 | Selected stored controls are strong owners, conditional on actual receiver/query correspondence. No live foreign count read or modification. |
| Last module owner → cleanup | Selected control zero-shared9560 gets object+18, invokes first virtual slot, then recycles288-byte object. Original serialized module slot ee760 targets complete D1 3efc, ee768 targets D0 4010; control slot ef910 targets9560 | Corroborates this exact file class's destructor route, not every runtime provider target. |
| Module destructor → children | D1 3efc decrements PiPL control+100 first (3f3c/3f4c), then PluginImpl control+e8 (3f54/3f64); last-owner lanes call virtual zero-shared+10 and release_weak. Base cleanupbb68 destroys recursive mutex; UnknownBase and final weak field+118 follow | Child destruction precedes mutex destruction. The destructor itself does not acquire this mutex or establish render drain; child virtual callbacks/reentry remain possible. |
| PluginImpl → module and other owners | Reused base D2 4bbd0 releases module control+130, then other control+100, then clears+e8 and invokes its adjusted deleting slot. Complete D1 4bd14 delegates to D2/UnknownBase and releases weak+1e0. Init4becc obtains+e8 via incoming virtual slot+58 and adjusted virtual slot0 | +e8 is separately owned through private virtual operations. Do not equate it with the incoming IPlugin shared triple, or assume an independently retained code handle covers this object. Actual concrete class/full callback graph remain UNKNOWN. |
| Module-handle handback | Reused PluginImpl GetModuleHandle4d368 writes object+128/control+130 into hidden result x8 and increments retained control | Returns a retained pair on its selected valid lane; no lock in this complete body. Caller must already have a valid PluginImpl and correct private ABI/thread contract. |
| ASL final owner / unload flag | Reused complete ASL destruction and table/zero-shared bodies; SetUnloadOnDestroy only stores byte+10. Selected destructors clear flag/reclaim storage without CFRelease(bundle), CFBundleUnloadExecutable or dlclose | Final object release is not a demonstrated code-unload event. Process-wide permanence, safe provider unloading and actual runtime targets are not proved. |

## Cache getter is an operation, not a read-only probe

New complete GetSerializedCache576c–5974 first retains the module's PiPL control
(57a8–57b8), replaces caller's PiPL triple (57c0/57c4), and releases the caller's
previous control (57e8–580c). It then copies three status fields, temporarily
retains PluginImpl (+e0/+e8 at584c–585c), and invokes QueryMap virtually at5884
for the exact11-byte ML::IPlugin query name. This is an interface query, not a
new ownership implementation or evidence that the underlying+e8 object is the
same interface. It replaces/releases the caller's prior IPlugin owner, then
balances temporary ownership. Null/query-miss lanes can replace outputs with
empty references; previously held controls can still run last-owner callbacks.

The complete body contains no local mutex acquisition. Read-only source naming
does not prevent output ownership changes, virtual callbacks or partial output
replacement. A later failure cannot be treated as an atomic read with unchanged
old outputs. No such getter has been invoked in AE.

## Acquisition, host admission and rollback decision

Existing-only factory classref(false) skips factory allocation but may initialize
guards/atexit, lock and retain/release references. Instance/CreateInstanceRef can
create. GetSharedFromThis reads object/vtable before obtaining retained ownership.
The new module chain does not supply initial safe live reachability, a supported
private C++ declaration or actual host thread/idle contract. Owned ABI stands
prove only their explicitly declared owned contracts.

Prior original registry transaction/consumer review remains applicable:
selected recursive locks release before subsequent consumers; zero active-effect
count is a snapshot; project read/write bookkeeping is thread local; default
SetdownAsync returns a ready future. None supplies continuous all-reader/dispatch/
MFR admission exclusion and drain. The observed registry+50 mutex is a concrete
candidate boundary, but selected render scopes do not take it and consumer
ownership outlives it. It cannot be promoted to the missing exclusion provider.

Prior publication/consumer bodies show vector/map/index publication before
preference/lazy-global failures. Local cleanup, placeholder replacement and
selected disposal are not a demonstrated whole-effect inverse. Module/PiPL owner
destruction likewise does not establish registry/canonical/preferences rollback.

**NO-GO for actual AE adapter and executable registration/apply/render trial.**
This packet substantiates a selected object-owner chain and rejects an unsafe
cache-as-read probe. Supported acquisition/release/thread, initial reachability,
actual provider identity/transitive callbacks, enforceable admission/drain and
whole-effect rollback remain required. This is not proof the product is
impossible. No unchanged scan, speculative foreign release or host gate bypass.

## Conditional live trial acceptance — BLOCKED

A concrete future single-fixture trial needs all of the following before commands
or installation can be prepared:

1. A supported or specifically reviewed non-creating acquisition boundary, exact
   retained receiver/object/provider correspondence and thread/idle conditions.
2. Continuous host-owned admission exclusion and completion/drain across callbacks,
   MFR, call and postflight; mutex ownership and a zero count alone cannot qualify.
3. Complete publication/failure semantics and reviewed recovery preserving original
   registry/project/plugin/preferences state; no guessed private teardown.
4. Exact clean adapter/supervisor/helper/fixture identities, actual inert/refusal
   checks and current disposable AE environment. Preserve the installed helper and
   all non-owned state; stop once on unknown outcome, with no automatic retry.
5. Separate observations of image load, effect registry entry, applying the uniquely
   named owned effect and comparing render output. Each stage retains failure or
   NOT RUN independently; owned native tests cannot supply these AE results.

OBJ-11 decision is BLOCKED on1–3; there is no executable host packet. Offline
collection/checks continue within authorized repository/file research scope.

## Implementation and preliminary verification

The existing collector adds only the fixed factory-objects scope. Exact file pins,
clean source, complete instructions, original-format rebases and exact vtable
targets are required. Outputs explicitly mark actual owners NOT OBSERVED,
thread/owner contract UNKNOWN, native experiment BLOCKED and registration/apply/
render NOT RUN. No native profile, bridge, ResourcePassGate backend or SDK changed.

Four meaningful parser/refusal tests failed against the previous collector
(missing scope/constants), then the73-method focused collector suite passed.
Controls alter retain/release/query/unwind instructions, missing/duplicate bounds,
table target/bind/high/reserved/format/fixup coverage and symbol scope.
These synthetic transcripts test refusal only. Preliminary private exploration
under build-ae-hot-loader/object-owner-inventory-3hfc2g5s is dirty-plan evidence;
it will not substitute for the final clean collection/original-byte review.

Exact-source full runner/scanner/manual/original archive/CI and final task
reconciliation are pending at this code preparation checkpoint.

