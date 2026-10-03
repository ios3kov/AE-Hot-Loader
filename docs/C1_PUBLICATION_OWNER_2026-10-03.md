# C1 PiPL/routine owner and ordinary-effect publication

Development, Stage C1, rules v8.0.0 / 132b7cd32873ba7328e3128ffbb33e1929b74d45.
Starting clean source e0488682ad4e720328465e24cee26c64b982a500 on the agreed research
branch. AI_ENTRYPOINT routing, scope/authority and OWNER-01–08 acceptance fixed
before new body collection in [production plan](PRODUCTION_PLAN.md).
Collector Standard; private native invocation Critical/gated. Original arbitrary
ordinary-effect/no-restart goal, A/B/C1/C2/D and release gates remain unchanged.
No AE process read/attach/launch/install/invocation/scan/retain/unregister/unload.

## Question and exact file scope

[Previous metadata review](C1_PLUGIN_METADATA_BRIDGE_2026-10-03.md) establishes a
stack-local PluginData context destroyed before GetPiPLs returns. Follow the
copied PiPL/provider ownership into routine descriptors without replaying that
context, and distinguish the routine roster from actual ordinary-effect publication.

New `--review publication-owner` scope: **12 complete windows / 2403 instructions /
248 addressed anchors**, original AE 25.6x101 arm64 files only. No callable pointer
or supported C/C++ ABI is manufactured from file addresses. Existing profile pins:
PLUG SHA-256 `12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22`;
PluginSupport SHA-256 `4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`.
No native helper/profile/ResourcePassGate or SDK changes. Bodies/Adobe files stay
private; code contains fixed bounds and selected structural anchors only.

| Complete window, end exclusive | Instructions | What it binds |
|---|---:|---|
| PLUG ScanData RegisterRoutine 6d50–6f74 | 137 | Record validation, global roster mutex, construct then append |
| PLUG PiPL/path RegisterRoutine 6fa8–7150 | 106 | Existing route recollected alongside new owner variants |
| PLUG PiPL/IPlugin RegisterRoutine 7228–7430 | 130 | Retained provider/descriptor ownership before roster lock |
| PLUG RegisterRoutineMinimal 7668–7914 | 171 | Minimal callback descriptor, not a proved effect loader |
| PLUG UnregisterRoutine 7914–7c74 | 216 | Conditional unprep/dispose, roster erase and failure/no-op |
| PLUG provider descriptor cd78–d030 | 174 | PiPL owner and queried PluginImpl interface/reference retention |
| PLUG NewRoutineDesc d474–d6d8 | 153 | Legacy PiPL handle, callback and path descriptor construction |
| PLUG GetPiPL 10074–1072c | 430 | Resource/cache handle copying, private PiPL conversion/architecture checks |
| PluginSupport InternalLoadPiPLs 4ca10–4d0fc | 443 | Module/resource vector, reference and exceptional cleanup |
| PluginSupport LoadPiPLs 4d164–4d24c | 58 | Module ownership around resource loading |
| PluginSupport PiPL PopulateFromPluginData 43d7c–442a8 | 331 | Copied fields, localization and identity adjustment delegates |
| PluginSupport PiPL CreateClassRef 192f4–193cc | 54 | Object/control-reference creation and ClassWatcher enrollment |

## Owner/lifetime findings (OWNER-01–03)

1. **Routine roster publication is distinct from ordinary-effect publication.**
   ScanData, PiPL/path, PiPL/IPlugin and Minimal variants append shared descriptor
   owners to PLUGp_G's vector at +10/+18/+20 under its recursive mutex at +38.
   The returned descriptor uses arm64 hidden return storage x8 and Boost ownership;
   PiPL/provider arguments are private InterfaceRef objects with separate ownership.
   None of these complete bodies directly invokes FLT RegisterNewFilter. Transitive
   helper/virtual/destructor side effects remain unknown, not asserted absent.
2. ScanData validates both record markers and PLUG global state markers before
   calling NewRoutineDesc under the roster lock. The PiPL/path and PiPL/IPlugin
   variants construct the descriptor and retain interfaces **before** acquiring
   that lock, then append and release the lock before return. Construction-time
   virtual calls therefore are not protected by that later roster mutex.
3. The PiPL/IPlugin descriptor requires non-null provider/interface inputs, calls
   provider slot +30 for a path and queries the `ML::PluginImpl]` interface via
   slot +18. It stores PiPL reference fields at +30/+38/+40, a queried provider
   pointer/control pair at +48/+50/+58, and a PiPL-derived flag at +60. References
   can retain those objects beyond the temporary PluginData context. Their actual
   live identity, factory/provider compatibility, validity duration and thread
   contract remain unobserved. A guessed opaque interface is not an invocation API.
4. Legacy GetPiPL has a cached-handle branch and a resource-file branch. It duplicates
   or copies resource bytes before ML::PiPL::Create, manages resource handles/file
   closure, and checks architecture-related private properties. This is a distinct
   serialized-resource path; it does not call the metadata callback in this body.
   NewRoutineDesc can invoke a ScanData callback before path/descriptor construction;
   callback error throws and local owner cleanup follows. Its target is unknown.
5. LoadPiPLs obtains a retained ASL module through virtual slot +20 and passes it
   to InternalLoadPiPLs; references are released on normal/exceptional return.
   InternalLoadPiPLs enumerates bundle PiPL resource URLs, loads each resource into
   PiPL objects, queries IPiPL and appends output references. An empty result can
   reach the alternate module-resource loader. Both use hidden return vectors;
   local CF/string/vector/module cleanup is not effect-registry rollback.
6. PopulateFromPluginData writes copied/localized fields, kind/version/reserved
   values and URL into the PiPL object, then calls category/match-name adjustment
   delegates. Source metadata strings alone cannot attest to final effective
   identity; actual registered identity still needs the independently captured
   registry. CreateClassRef also calls ClassWatcher::AddObject; enrollment of a
   PiPL object is not ordinary-effect registry insertion. Those delegates' full
   transitive contracts are outside this fixed review and remain unknown.

The ordinary-effect path still uses the independently reviewed
[FLT setup/AddEffect/RegisterNewFilter](C1_EFFECT_PUBLICATION_REVIEW_2026-10-02.md).
The file model now separates metadata storage, PiPL object tracking, PLUG routine
roster and FLT effect registry. It supplies structural owner boundaries, not an
actual live provider/receiver or a supported late-entry contract.

Primary public SDK cross-check: Headers/AE_GeneralPlug.h in actual SDK 25.6_61,
SHA-256 `30d12ec3eb5af1a902c7414053b1be1da0204b226e0b1cdc71272be1e137000c`.
Selected AEGP effect-suite declarations enumerate installed-effect keys, query
names/match names and apply an installed key to a layer. ML::IPiPL, ML::IPlugin,
PLUG_RegisterRoutine and RegisterNewFilter literals are absent from that exact
header. This bounded lexical result does not prove global API absence. Public
AEGP handles cannot be cast into these private InterfaceRef/shared-pointer types.
No new SDK API call was added. Previous SDK owned macro receipt remains historical
at 9e35d1e; unchanged source/types are not presented as a new SDK test here.

## Exclusion, completion and rollback (OWNER-04–05)

The new PLUG roster mutex differs from the previously reviewed FLT registry mutex
at receiver +50. Each is scoped to selected bodies. It does not establish a
continuous joint lease spanning provider construction, canonical registration,
parameters/global setup, effect publication and escaped owners/readers/MFR.
Recursive locking permits same-thread reentry. Prior render-count zero and idle
observations remain snapshots. No observed global admission/drain mechanism.

UnregisterRoutine takes the PLUG mutex, validates state, dynamic-casts the supplied
routine owner and searches its roster. **Not found returns 0**, so success does not
prove an entry was removed. If a found routine is prepared, the path can call
PLUGp_UnprepRoutine, then DisposeRoutineDesc. Either nonzero result exits before
roster erase; otherwise vector entries move and its end is changed, while reference
release can invoke virtual destruction. It is a stateful operation with teardown
and local failure paths, not a passive inspection or established inverse for the
FLT registry/canonical factory/parameters/preferences/global setup. No direct FLT
registry erase appears in this body; transitive effect/lifecycle cleanup unknown.
Do not invoke it as speculative recovery or promise safe executable unloading.

Register variants append owners but expose no proved whole-effect completion
result. Local unwind destroys temporaries/scoped locks, without establishing an
inverse ordinary-effect transaction. The Minimal variant constructs a flagged
callback descriptor (0x20), not a verified route for arbitrary ordinary effects.
Name similarity and returned handles cannot replace registry/apply/render evidence.

## Prepared implementation and verification

The collector retains fixed file hashes, clean source check, bounded offline LLDB
(no dependencies/launch/attach/expressions), full decoded coverage and archive
integrity. New reports state distinct roster/lock scope and unknown actual provider,
ABI, host-wide exclusion and rollback; registration/apply/render NOT RUN.
Three new refusal/catalog/scope tests started with 3 expected errors, then all
**48** collector tests PASS, including existing real owned arm64 LLDB controls.
Synthetic operand/branch/coverage cases verify refusal only; they are not AE proof.
Separate review checked construct-before-lock versus append/return, normal and
exceptional reference cleanup, not-found versus erase and private/public types.

Preliminary private bodies: build-ae-hot-loader/owner-preliminary-bw_lt5jz,
dirty/preliminary only. Final clean-source collection/independent original-byte
and archive verification/full regression/scanner/exact-source CI pending at this
prepared checkpoint. No installable helper or live experiment was manufactured.

## Acceptance and next gate

OWNER-01 bounded handoff research complete; safe end-to-end bridge unproven.
OWNER-02/03 structural owners/lifetime review complete, actual receiver/provider/
thread/invocation contract BLOCKED. OWNER-04/05 reviewed lock/failure boundaries,
but required host-wide exclusion/completion/rollback BLOCKED. OWNER-06 host
experiment BLOCKED; research-tool refusal checks PASS. OWNER-07 final checks/CI
pending. OWNER-08 live experiment/interpretation NOT RUN, depends on confirmed
mechanism and concrete new live authority. This is not eight completed host steps.

Next discriminator: the supported late-entry/admission/drain contract joining the
retained provider/routine owner to FLT publication. More PiPL construction alone
or PLUG unregister as guessed rollback does not meet it. Native backend NOT READY;
no merge/release or scope change. Preserve consumed helpers/session, third-party
plugins/projects, SDK and historical private evidence. Retain current owned/private
research receipts for reproducibility; no shared-state cleanup or loaded-file removal.
