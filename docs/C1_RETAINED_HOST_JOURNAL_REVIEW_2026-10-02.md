# C1 retained diagnostic host journal and independent transaction verification

Stage C1, Critical/Development. Clean baseline
`a3591223a14cd6550e54d8291f13f2f4edd5816e`, research branch. Accepted rules
6.2.0 / d966078a9e45fee7ec9ad14f211a9da753d64b8a: AI_ENTRYPOINT; Process
scope/API/safety/identity/regression/evidence; Engineering input/resource safety,
reproducibility/testing; Tools diagnostic/IPC overlays. Product contract unchanged.
Existing public observation/API contract is reused through injected boundaries;
no Adobe API change, native installation, launch or sensitive host read.

## Objective and acceptance before implementation

Connect the [transaction core](C1_RETAINED_TRANSACTION_REVIEW_2026-10-02.md) to
private exclusive disk evidence and verify the complete transaction separately.
The four-record copied-byte journal stays compatible; the new host journal has
five fixed records: claim (plan/baseline), marker (plan/immediate observation),
native (existing scope/raw-copy diagnostic), after (plan/postflight), result
(plan/provisional decision). No successful native flag alone establishes PASS.

| Requirement | Acceptance |
|---|---|
| RIH-001 | Exact immutable scope/paths/15-second plan, measured scope and raw host observations saved with private 0700 directory/0600 exclusive files, fsync, no overwrite/retry/delete. Any invalid order/write poisons the wrapper. |
| RIH-002 | Preserve independently supplied measured scope plus PID/start, executable/module/version/architecture, project flags/revision, complete ordered effect/image inventories at baseline, immediate pre-read and postflight. Raw paths/names encoded as hex, never executed. |
| RIH-003 | Bounded canonical five-record inventory/framing and field order; maximum 4 MiB record payload, 2 MiB raw observation, 20,000 effects, 8,192 images. Native copied bytes keep 64 KiB/22 reads/6,976 bytes. Excessive or ambiguous evidence refuses. |
| RIH-004 | Python independently verifies all plan/scope/host fields, safe project, exact process/provider/root binding, unchanged revision/registry/resident images (existing immutable system lazy-image policy), and both native captures using the existing copied-byte verifier. Producer-only PASS/unknown/duplicate/missing fields refuse. |
| RIH-005 | Verification is bound to a separately supplied monotonic start; backwards/expired clock before file access or after verification/rechecks cannot PASS. Safe bounded no-follow file/directory reader shared with old verifier, preserving its policy and tests. |
| RIH-006 | Real C++ transaction/capture/disk producer → separate Python verifier end-to-end owned fixtures; mutation/failure/replay/path/mode/deadline cases; full clean regression, separate source/static review and exact-source CI. |

## Trust limits and unresolved integration

These tests prove storage and verification of supplied observations, not that AE
produced them. Measured fields still require a native adapter's independently
checked loaded binding. Start time must originate outside native evidence; it is
not read from producer files. The outer supervisor must start that clock before
publishing its sole request and preserve the attempt on timeout/unknown outcome.
Verifier PASS always has `host_execution_verified: false`; even origin ae-diagnostic
cannot attest to live execution by itself. No hostile same-UID/power-loss guarantee.

The existing disk container is reused for five records, without changing its
resource-registration contract or ResourcePassGate. Two matching snapshots do
not prove atomicity, allocation lifetime, quiescence, repeat safety or plugin
registration. Existing installed/consumed observe-d548b007e316 is preserved and
its concrete live-operation authority stays consumed. Actual seven names NOT RUN.
Next separate external one-shot request supervision and measured native adapter,
then exact inert candidate checks and candidate-specific operation authority.

## Implemented owned-data checkpoint

`RetainedHostJournal.hpp` connects the transaction core to the existing private
exclusive disk container. It saves the immutable plan, all three measured host
observations, the existing raw-copy diagnostic and a provisional decision;
invalid order/plan/path/size/write poisons the adapter. Unsafe but bounded
postflight can remain evidence of FAIL. PASS requires complete guarded sequence.

`verify_retained_host_journal.py` independently checks canonical inventory and
all host/scope/plan fields, project/revision/registry/resident images, both copied
sequences and producer decision. It freezes expected metadata before boundary
callbacks, refuses evidence outside the expected journal path and uses an
independent monotonic start before any IO and after final filesystem rechecks.
Old four-record verifier policy/format remain unchanged; only its bounded
no-follow reader was shared with explicit names/payload/verifier parameters.
No measured native backend or live request was added.

Focused retained family PASS: 27 Python tests; new host verifier has 13 Python
tests and real strict-C++17 producer with 19 nested cases. Actual transaction/
capture/disk → independent Python verification covers empty, raw inline and
maximum eight-name evidence, a 785-effect/82-image fixture, system lazy images,
failed/partial/postflight/marker/final-save cases, poison/replay/oversized evidence,
scope/safety/registry/image/frame mutation, bad framing/inventory, expected-plan
immutability, path ownership/modes/special files and entry/directory replacement.
Expired/backwards deadlines refuse before IO, after semantics and after final IO
identity rechecks. A late persisted producer PASS is explicitly provisional and
rejected by the independent deadline.

Code/test source **dfa78e04d8a1e3f7cae64262a9f13a147aa4a5a3**. Full clean local
regression PASS: 337 Python/no skips, 62 Node, 22 offline stages. Nested C++ cases
are not added to Python counts. Independent report ZIP inventory/member hashes/
CRC and current tracked-source verification PASS; source remained unchanged.
Private report SHA-256
`4de49af465eddd31a8c5f72ba11784865886273eef877af5bc5da1677dddd63a`.

Separate source review covered immutable bindings, claim/marker/partial-final
ordering, poison/no-retry, raw byte/path/name encoding, native reconstruction reuse,
host inventory/safety/change checks, expected-directory binding, independent clock
before/after semantics and final IO, and shared reader preservation. Bounded static
audit completed at exact clean source: 325 supported files, zero omissions in
scope, all selected checks completed. Native C++ reviewed separately; unsupported
file types are outside scanner claims. Raw exit 1 retains only the known
`vibe.no_ratelimit_auth` at `tools/artifact_manifest.py:71`, rechecked local argparse
mode rather than an HTTP/auth route. Private audit SHA-256
`77dd4d2158c9dfb0c47133a83d4811aa4435a950fb3da09f1ea5b382318029f5`.
Exact-source [research CI 37049587798](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37049587798)
and [full macOS CI 37049587807](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37049587807)
both completed/success at dfa78e04d8a1e3f7cae64262a9f13a147aa4a5a3.
Actual seven names NOT RUN; registration/apply/render and release remain blocked.


Documentation-only closeout changes no tested source/candidate. Changed local
documentation links and diff whitespace check PASS. Acceptance RIH-001–006 is
verified within the owned/injected boundary scope above; measured live AE/native
binding and external one-shot request execution remain separate prerequisites.
