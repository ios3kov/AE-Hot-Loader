# C1 registration caller, registry access and completion — six-step batch

Stage C1 / Development; clean starting source
`522e0023ea0f7897bbb1f16d3ed01dac9270a4cf`, research/ordinary-plugin-discovery.
Adopted rules v6.2.0, `d966078a9e45fee7ec9ad14f211a9da753d64b8a`.
AI_ENTRYPOINT selects PROCESS API-SOURCE-001 / SAFE-001 / regression and evidence,
ENGINEERING debugging and compatibility, NATIVE ownership/threading and TOOLS
bounded diagnostics. File-only work is Standard; dependent private native host
operation remains Critical / BLOCKED. Product contract unchanged.

## Acceptance fixed before new body review

- REG-001: trace the bounded resource-pass caller/start/finish route in exact
  pinned files; distinguish startup lifecycle from a supported late-entry API.
- REG-002: review effect-registry writer and selected readers, identify their
  locking and returned ownership boundaries; do not infer complete reader coverage.
- REG-003: review relevant render/MFR counters or scopes; distinguish observed
  exclusion from a momentary idle observation or a per-effect mutex.
- REG-004: trace publication order and partial failures/completion against
  existing parameter/canonical mutation evidence; do not invent rollback.
- REG-005: implement the smallest evidenced protective/collector change with
  refusal tests. No native call without its verified ABI and exact operation scope.
- REG-006: independently verify original file bytes and exact-source packages;
  complete local regression, static review and both CI workflows; reconcile
  current status/plan/handoff/compatibility and state progress toward the product.

## Scope and authority

Repo edits, owned offline fixtures, pinned file inspection and push to the
existing research branch are authorized. Prior live scope consumed: no AE
launch/attach, process-state read, scan, install, provider invocation or private
teardown in this batch. No merge/release. Backend NOT READY; real registration /
apply / render remain open. Historical scan FAIL is preserved and not repeated.

Baseline code `56be72b888652da450dc58c0d83c64187218af95`: 376 Python/no skips,
62 Node, 22 available stages and both exact-source CI PASS; ten file modes
independently verified. These results do not verify the next source.

## File review findings (REG-001–004)

Exact aelib SHA `f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f`
and FLT SHA `227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256`
are unchanged. File VM addresses below are research locations, not runtime
pointers or a callable public ABI. New `registry-transaction` collector captures
17 fixed windows / 3063 instructions / 484 addressed anchors. The public notifier
is captured in two adjacent windows, with its associated cold cleanup body;
all other windows cover complete bodies/thunks at these file pins.

| Evidence | Bounded finding | Remaining uncertainty |
|---|---|---|
| aelib InitIterator `61134–61fe8`; Egg_PlugSearch `63914–63aa0` | Startup calls FLT_Birth `61420`, required pre-search `61ae4`, resource helper `61b04`, then a separate LoadAEPlugins/FLT notify/MEE notify phase `6158c/615a4/615ac`; cleanup follows `615e4/61600`. Egg obtains host folders/owners `6394c`, passes default sack and all folders to PLUG_Search `6399c`, throws on nonzero `639a4/63a68`, destroys local owners on unwind `63a80`. | Initialization phase correspondence is not a supported late-entry contract. Never replay startup or invoke the global helper as a scoped scan. Existing jump-table evidence remains historical; no new live caller observation. |
| FLT registry instance/ctor `458c–46cc` | Instance accessor reads a global pointer; constructor initializes containers, clears loading flag `+48`, constructs recursive mutex `+50`. | No actual receiver/initialization/lifetime observation. |
| HasFilter `4a24–4b9c`, FindFilterPtr `4c4c–4f74`, index `4b9c–4c4c`, FindFilterIndex `4f74–5014` | Three selected readers take the same receiver `+50` mutex (`4a50/4c90/4bcc`). Find and index retain the returned Boost owner under lock (`4f30/4c10`) then unlock; FindFilterIndex reads index `+218` from returned owner and releases it. | This is selected-reader coverage. Shared ownership does not extend the registry lock over consumers, callbacks or later dispatch; no claim that all readers lock or remain excluded. |
| RegisterNewFilter `5014–53f0` | Holds recursive mutex `+50` (`5054`); vector owner append and end publish `5098` precede name allocation/virtual name callback `50a8` and map emplace `5254`. Index write `5300` and UpdateEffectFromPrefs `530c` precede unlock `531c`. Duplicate key lane replaces map owner `5350`, releases old owner and rejoins index/preferences. Unwind releases locals/scoped lock. | No explicit inverse container erase in this body; transitive atomicity/rollback UNKNOWN. This is a partial-mutation risk requiring review, not a proven runtime failure or permission to undo/unregister private state. Recursive locking permits same-thread reentry; it is not global quiescence. |
| Registry NotifyFilterLoadingDone `606c–60cc` | Locks `+50`, sets byte `+48=1` at `6098`, unlocks; no plugin enumeration in this body. | Completed flag is not successful effect registration and does not establish an exclusive window. Selected reader bodies above still lock regardless of this flag. |
| Public FLT notifier `8f360–906c4`, cold `a53b8–a541c` | Empty supplied vector skips module setup `8f398→8fa88`. Module lane calls FiltSetup `8f7ec`; caught selectors can discard/report exceptions and continue iteration (`8fa54–8fa84`). Utility callback setup `8fa8c` and registry done `8fa94` follow. Optional later diagnostic serialization uses CPU executor/task submission (`8fc18/8fc30`) and file write `8ff94`; notifier is not a harmless registration-only primitive. | No live result, complete exception ABI, executor/callback completion, rollback or failure atomicity proof. Do not equate normal return/loading flag with all modules succeeding or invoke this global startup notifier. |
| Render scopes `30e10–30e74`, wrapper `78138–7813c` | Per-RenderState nesting counter `+98` uses ordinary load/store; transitions 0↔1 atomically increment/decrement global active-effects count at file `e9af8`. Count accessor is an ordinary load `30e6c`; wrapper branches to it. No registry mutex in these small complete bodies. | Zero is a snapshot, not admission control; it neither prevents new rendering nor proves all MFR/async work is represented. No live count was read and no synchronization primitive was established. |

## Protective implementation (REG-005)

`ResourcePassGate` now requires a supervisor-bound publication-window identity
and fresh, complete, exclusive lease evidence at baseline, immediately before
call and postflight. Missing evidence, unknown/nonzero active-render count,
uncompleted registry lifecycle, wrong review/window, zero epoch and a changed
lease epoch refuse the operation or revoke PASS. Epoch is an external lease
identity, not an invented native registry revision. A review digest/boolean or
zero counter alone does not establish the lease.

The unbound `search_one_root` seam receives the exact expected lease. A future
reviewed native adapter must atomically validate the still-held same lease at
native entry and keep it continuously across reentrant callbacks and postflight.
Releasing/reacquiring or checking a flag before subsequently locking is invalid.
This policy implements no Adobe exclusion mechanism and makes no native call.
The durable marker remains consumed if an adapter detects loss before calling.
Journal now preserves window/review/epoch/exclusion/worker/lifecycle observations;
claim/marker bindings reject a retargeted window and never overwrite evidence.

Focused red regression reproduced the previous policy accepting a model without
any publication observation (test assertion failed before the change). Focused
checks now PASS: 129 gate cases (+35), 38 real-file/process journal cases (+3),
39 Python collector cases (+3); all host observations/calls are synthetic.
Final catalog review also reproduced and fixed omitted counter/wrapper/notifier
symbols in the selected symbol inventory. Their disassembly/bytes were already
captured; the focused regression now requires all five actual symbol families.
No weakened tests, native profile changes, installable candidate or host operation.

## Verification / closeout (REG-006)

Pending clean source collection, independent original-byte/archive checks,
full local regression, static review and both exact-source CI workflows. No
current runtime or release claim is made while these checks are pending.

## Progress and next decision

REG-001–005 have bounded offline findings and tested refusal behavior. We have
identified specific lock/ownership boundaries, a nonexclusive render counter,
startup-only caller sequencing and completion paths that can mask module errors.
These narrow the next experiment and prevent misleading success criteria; they
do not yet implement hot registration.

Next offline work: registry lifetime/accessor consumers beyond the selected
readers, transitive preference/canonical writes and exception contracts, then
an enforceable all-reader/dispatch/MFR exclusion route or a documented inability
to provide it. Only a justified isolated adapter can produce a new reviewable
live packet. Reassess go/no-go before requesting host operation authority.
Backend NOT READY; registration/apply/render NOT RUN; A/B/D/release remain open.

