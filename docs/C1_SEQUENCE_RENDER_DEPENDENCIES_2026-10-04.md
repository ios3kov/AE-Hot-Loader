# C1 — sequence creation and frame registry dependencies

Date: 2026-10-04. Branch: `research/ordinary-plugin-discovery`.
Clean baseline: `983a28b16d005b6854e696626877cd8c6052096d`.
Rules8.0.0 / `132b7cd32873ba7328e3128ffbb33e1929b74d45`, AI_ENTRYPOINT
first; API-SOURCE, AI-STATE, TASK-CLOSE, CLEANUP, NATIVE ownership/threads and
TOOLS bounded diagnostics. Standard offline research; dependent private execution
remains Critical/BLOCKED. The user requested the maximum connected continuation
of the [host-operation packet](C1_COMPLETE_HOST_OPERATION_2026-10-04.md).

Later continuation: [concrete factory/sequence-data/publication contract](C1_PUBLICATION_CONTRACT_2026-10-04.md)
resolves the selected ordinary canonical clone and derived sequence-data methods,
and narrows match-getter reentry. Full nested lifetime/reader coverage/partial
compensation remain open. This earlier checkpoint retains its original evidence
and does not become a live registration/apply/render result.

## Result and practical implication

Two previously missing file bridges are now established for the selected target:
command16 selects the apply task through the original BEE command table, and a
SmartRender path resolves the sequence's numeric index through the same FLT
registry used by the registration writer. The latter lookup obtains an independent
FCSpec owner under the registry mutex before using it outside that lock.

The selected frame path therefore combines **catalog lookup and locally retained
descriptor use**. It is not a demonstrated design where all frame work depends
only on a descriptor captured at ApplyEffect. Nor does a catalog read by itself
make a global render stop necessary: this particular lookup already participates
in the writer's mutex protocol. The remaining problem includes other readers,
partial publication/reentry, phase readiness and lifetime of nested data/code.

No new effect absent at startup has been registered, applied or rendered in AE.
Research/product PARTIAL; native adapter unbound, implementation/trials BLOCKED;
registration/apply/render NOT RUN. All original A/B/C1/C2/D, append/reload/recovery
and release obligations and executable refusal policy remain unchanged.

## Exact scope and evidence

Target remains installed AE2025 **25.6.0.101 / macOS arm64**, SDK **25.6_61**.
All addresses below are unslid original-file addresses, not live pointers, a
validated calling convention or supported private ABI. Offline LLDB disabled
initialization/symbol scripts and dependencies and only disassembled bounded
file ranges. No AE launch/attach/process read, install, scan, suite acquisition,
private call, callback replay, unload or fault injection occurred.

| Input | Exact identity | Role |
|---|---|---|
| FLT.dylib | SHA256 `227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256`; UUID `c8786a71e3133b209494359fb56d705a` | Sequence/frame/node and registry paths |
| BEE.dylib | SHA256 `817b9de9c6d57b5d6988b634842090e1528fe817a5685c8d1ff358553c6660ca`; UUID `161300f373f83ebca751959df40a073b` | Command table/task dispatch |
| SDK25.6_61 | Seven exact unchanged SDK hashes retained in private `SDK-pins.json` | Public key/suite and selector contract |
| Previous CTX source/evidence | Exact baseline above; original/closeout archives unchanged by SHA256 | Apply task/payload and prior ownership evidence |

Collection covers **33 complete bodies /35 contiguous windows /6558 instructions**.
Seven bodies/473 instructions repeat already reviewed registry/ready/procedure/
effect-lock evidence and are excluded from novelty: **26 new bodies /6085
instructions**. Historical apply-task creation/constructor/execution captures are
also reused and separately hash-checked, not counted as new. Old dispatch source
and runtime limits remain in the [dispatch review](C1_EFFECT_DISPATCH_REVIEW_2026-10-02.md).

Independent original section bytes, nlist next-symbol boundaries, complete
transcript coverage/hashes, **1673 direct branch destinations across the33
bodies**, seven index/sequence/owner field accesses and three encoded table
rebases agree. BEE command16 row is checked as bounded original data, including
flags0 and task-spec short19. The exact SDK enum independently confirms
SMART_RENDER24 / SMART_RENDER_GPU31. These checks do not execute host code.
The initial historical-task label filter matched no captures; it was corrected
to the actual saved names and an explicit three-capture assertion added before
final PASS. Original bytes/transcripts were not changed.

Private original evidence:
`/private/tmp/aehl-sequence-render-3vrnri_6/original-evidence.zip`, SHA256
`4bfa1545fd5abc3ef333856f3b7abad31c7fc819732ddbc1efc6e0a744dae84c`;
134 unique members /133 hashed payloads, complete manifest/CRC/hash PASS.
Contains bounded transcripts, original data excerpt, capture/check scripts,
source/SDK pins, original-file fixup inventory and reused task transcripts.
Full Adobe binaries and SDK sources are not redistributed. Source/docs/audit/
publication receipts are retained beside it. Previous evidence is preserved.

| ID | Observable acceptance | Result / remaining boundary | State |
|---|---|---|---|
| SEQ-01 | Reconcile CTX/reader/dispatch evidence and exact baseline/pins | Original/SDK/previous-archive identity checked; remote branch matches baseline; both baseline workflows success | DONE, bounded sources |
| SEQ-02 | Bind command16 to actual apply task and its execution method | Original table rebases, constructor vtable and DoTask slot connect the prior task/payload to command16 | DONE statically; live execution NOT RUN |
| SEQ-03 | Trace ordinary sequence creation and canonical resolution | NewGuts/constructors and GetCanonicalStream boundary inspected; full TDB factory/virtual selection and live identity unresolved | PARTIAL |
| SEQ-04 | Establish sequence/clone/destruction ownership and nested lifetimes | Numeric index, owned sequence-data/parameter handles and raw sequence links distinguished from FCSpec owner; transitive lifetime unresolved | PARTIAL |
| SEQ-05 | Identify selected frame lookup and retained descriptor path | Node→sequence index→FLT registry owner→readiness→SmartRender dispatch established in exact files | DONE for selected static path; full callbacks/live route NOT RUN |
| SEQ-06 | Compare actual changed writer state with consumer protection/reentry | Selected lookup uses same registry mutex and retains before unlock; whole read set and safe publication/reentry unproved | PARTIAL |
| SEQ-07 | Separate local error cleanup from complete operation recovery | Sequence creation/render/dispatch error exits inspected; no demonstrated whole-registry compensation | PARTIAL |
| SEQ-08 | Independently verify/document/review/preserve and commit/push | Raw checks PASS; exact documentation/source/audit/publication receipts retained beside original archive | DONE for bounded closure; native gates open |

Packet:4 bounded tasks DONE /4 PARTIAL. No product stage or private safety gate
is closed merely by these file findings.

## Command16 actually selects the apply task

Complete `BEEp_DoCommand` `610490–6115f8` was collected in two adjacent windows.
It masks the short command, obtains `BEE_G_cmd_tab` at `103e8a0`, and indexes
32-byte rows (`6105b8–6105d0`). Row16's encoded rebases are:

- `103eaa8` → `612710`, the already captured apply-task creation function;
- `103eab0` → `612758`, the neighboring marshaling function. Its body is not
  inspected here; a nonzero pointer alone does not prove its behavior.

The dispatcher calls the creation pointer at `610888` when a command payload
exists without an incoming task, stores the result into task-spec `+20`, and
reaches `BEEp_DoTask` through its ordinary command path. Complete DoTask
`6455fc–645938` loads that task at `645784`, resolves virtual slot `+10`, and
calls it at `6457b0`. The prior task constructor installs vtable address point
`ffcbb8`; encoded rebase `ffcbc8` → `512200` identifies the prior inspected
`BEE_ApplyEffectTask::Execute` body. This supplies the table/virtual bridge that
CTX left open; it is not inferred solely from adjacent symbol names.

The reused execute body loads signed-short task field `+12` and calls
`BEEp_ApplyNewEffect`. The earlier numeric-index payload and project-clone queue
findings remain valid; clone application is distinct from per-frame rendering.
Command processing also changes undo/project/context state. It is not a standalone
registration entry and its undo task does not undo installed-catalog publication.

## Sequence state is not automatically a retained FCSpec

`FLT_NewSequence` `ea68–ea7c` forwards to NewGuts with the sequence setup lane.
`FLT_NewSequenceWithData` `ea7c–ec10` calls NewGuts at `eaac`, then deals with
sequence data and resetup (`eb28`), including temporary state restoration and
translated exceptions. These lanes must not be treated as one error contract.

Complete `FLT_FCSeqSpec::NewGuts` `deb0–e5e8` obtains a local FCSpec owner
through `FLTp_InsaneMagicChecker` at `df34`. It calls ReadyFilter (`df7c`) and
lazy globals (`e000`) before requesting a named stream from the AE stream
factory (`e200`). The returned stream is dynamically checked as FCSeqSpec,
stored in the output, and receives the numeric index at sequence `+20a`
(`e230`). Parameter lock/setup/seek and optional dialog paths follow. The actual
TDB factory implementation and indirect stream construction remain boundaries;
matching names or a return pointer do not prove their live identities.

Complete ordinary constructor `5b668–5b914` initializes a TDB named stream,
finds the index from the match name (`5b71c`), stores short `+20a`, creates
sequence-data at `+228` and allocates parameter-table handle `+230`. It obtains
another local FCSpec owner at `5b788` for flags and subsequently releases that
local owner. Complete clone constructor `5b968–5bd78` copies the index-containing
word at `+208`, creates new sequence data, handles flattened data/parameter
handles and consults the magic checker. Copying that word is not copying a
shared FCSpec owner.

Complete `FLT_SequenceData::NewSequenceData` `6bc34–6be78` resolves the sequence
index (`6bc50–6bc58`) before choosing a virtual implementation. Its base
constructor `6b750–6b830` retains a raw sequence pointer at `+18`, obtains a
local registry owner for capability flags, and releases that local owner before
return. Selected concrete derived implementations and TDB base state are not
fully reviewed. Therefore these bodies do not prove either presence or absence
of a persistent FCSpec/code owner somewhere else in the complete instance.

FCSeqSpec destructor `5bf74–5c07c` unregisters idle participation, conditionally
sets down sequence data, frees parameter/owned state and invokes virtual sequence-
data destruction before its TDB base. Sequence-data setdown `6b970–6bc0c`
uses the sequence through the magic checker and readiness path. This is additional
lifetime dependence, not a registry-wide inverse. GetCanonicalEffect
`5ca64–5cae4` uses the stream's match name and TDB canonical-stream lookup;
it is separate from installed-registry ownership and can fail its dynamic cast.

## A concrete frame path reads the registry, then retains FCSpec

Complete FLTp_BaseNode `40878–40994` stores the sequence pointer at node `+98`
(`4092c`). Render-node and node constructors retain callback interfaces and
prepare parameter/context information; they do not turn that selected raw field
into proof of the sequence's enclosing lifetime. Complete frame constructor
`37510–37694` likewise stores its sequence pointer at frame `+10` (`375dc`).

Complete `FLTp_Node::Render` `44c50–45cac`, collected in two contiguous windows,
contains this selected path:

```text
node+98 → sequence+20a (numeric index)
        → FLTp_GetFCAddress(short)
        → FLT_FilterRegistry::GetFilterFromIndex
        → independently retained FCSpec
        → ReadyFilter / scoped readiness
        → SmartRender dispatch structures
        → FLTp_DispatchFilter
```

The index load at `44ef4–44ef8` feeds GetFCAddress at `44f00`; it is not a key
enumeration probe from an AEGP worker. The short wrapper `9839c–983c8` obtains
the registry singleton and calls GetFilterFromIndex. The already known complete
getter `4b9c–4c4c` locks registry `+50`, reads vector `+30/+38`, copies a
pointer/control pair, increments its strong count at `4c10`, writes it to the
result at `4c14`, then unlocks at `4c1c`. No pointer to a movable vector slot
is returned by this selected path.

Render retains the local result and readiness scoper (`44f04–44fe4`), passes
FCSpec into SmartRender structures at `45118–4513c`, and selects command24 or31
at `45398–453a4`. Both values match the exact SDK selectors. It passes the
resolved FCSpec and sequence to outer dispatch at `453d4–453f4`. The previous
complete outer/host/procedure-call bodies remain historical evidence; actual
recipient/entrypoint identity, all callback effects and live execution are not
promoted by this connection. Cleanup includes unready/scoper/owner destruction
on normal and error lanes (`456c4`, `45c7c–45c88`).

Frame setup `37a00–37e20` has another acquisition through the magic checker
(`37a68`), readiness/lazy setup and eventual frame dispatch. Complete checker
`97ecc–9839c` selects a sequence index when its mask includes that lane and
calls the same registry getter. Ownership is established only for the resulting
local owner; the selected path does not establish all reader coverage.

## Writer protection, reentry and error boundaries

The selected getter and the known registration writer both lock registry `+50`.
The writer appends shared-owner slots to vector `+30/+38` and later updates name
map, index/preferences before unlock. A copied FCSpec owner can survive slot
movement on this selected path; this does not protect every nested field or all
readers. Late invocation, collision/replacement and partial failure remain
separate, unproved contracts.

The mutex is recursive. The writer's virtual match-name call at `50a8` follows
its vector update and precedes later map/index work while the lock is held.
Whether that concrete callee can reenter a reader, and what state such a reader
would see, is still UNKNOWN. Sharing the mutex establishes ordinary conflicting
access protection for this lookup; it does not establish failure atomicity or
exclude same-thread reentry into intermediate publication.

Known ReadyFilter `5cea8–5d0dc` uses FCSpec mutex `+170`, a readiness count and
retained routine preparation. It publishes an effect-procedure field at `+d0`
with an atomic exchange; the known getter reads that field with acquire semantics.
This descriptor-local mechanism is not the registry transaction or a complete
module lifetime proof. The known optional effect-lock helper can omit its lock
for thread-safe effects; it is not an all-reader catalog barrier.

| Boundary | Observed cleanup | What it does not establish |
|---|---|---|
| NewGuts sequence/parameter failure | Frees local parameter handle, invokes instance virtual cleanup and clears sequence output (`e3d4–e404`) | Reversal of prior lazy globals/canonical registration or installed insertion |
| Sequence-data constructor/clone failure | Local shared owners/handles/base state unwind | Complete concrete derived/TDB/provider lifetime and factory rollback |
| DoTask exception | Translates selected errors and restores command/context bookkeeping | Installed-registry transaction rollback |
| SmartRender failure | Scoped readiness/local owners/render context and dispatch objects unwind | Complete publication recovery, callback drain or code unload safety |

No fault injection occurred. Absence of an erase in these bounded bodies does
not prove that compensation is impossible elsewhere.

## Next dependency and verification limits

Do not repeat the now established command-table bridge or ask more general SDK
search questions about catalog versus descriptor. Next connected offline work:

1. Complete concrete stream-factory/sequence-data selection and its retained
   module, canonical-stream and callback ownership/error boundaries.
2. Trace the writer's actual match-name callback and remaining index/name/UI
   readers through mutation/reentry; map late publication preparation versus
   externally visible commit and partial-error compensation.
3. Prepare a bounded known-good startup calibration only after instrumentation,
   admissible main-thread calls and current host authority are concrete. Actual
   live suite/effect/frame identity remains a separate gate. Late private calls
   remain blocked until the complete legal host operation and safety prerequisites
   are established.

All33 reviewed bodies are file evidence for these exact binaries. This is not a
proof of all AE builds, a race-free operation, successful hot-add, supported ABI,
product completion or release readiness. Full local executable regression is
NOT RUN for Markdown-only changes; current documentation/raw audit/source checks
and exact commit/remote/CI states are retained separately. Main/release/installed
plugins/preferences/projects are unchanged. No evidence was deleted.
