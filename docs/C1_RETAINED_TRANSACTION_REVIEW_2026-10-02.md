# C1 retained identity transaction core

Stage C1, Critical/Development. Clean baseline
`d4fbc3f10fe02bdcb26d2261606835a187d36784`, research branch; accepted rules
6.2.0 / d966078a9e45fee7ec9ad14f211a9da753d64b8a. AI_ENTRYPOINT, Process
scope/API/safety/identity/regression/evidence, Engineering code safety/testing/
host-independent core and Tools diagnostic rules apply. Product contract unchanged.
No new/changed Adobe API: reuse existing observation contract, inject the boundary;
actual native binding and external authorization integration remain separate.

## Objective and acceptance defined before implementation

Compose the bounded capture with an immutable exact plan, fresh observations,
exclusive durable claim/read marker and no retry. This stage implements/tests the
transaction core only, without a native helper, disk adapter or live supervisor.
The existing four-record copied-byte journal and verifier stay unchanged.

| Requirement | Acceptance |
|---|---|
| RIT-001 | Atomic consumed attempt before any boundary access, including invalid plan, missing authority, concurrent/reentrant entry and failed claim. Never retry a boundary operation. |
| RIT-002 | Exact authorization for scope/run/source/build/binary/provider/root/PID/start, executable/module/evidence path and fixed 15-second budget. Invalid authority refuses before boundary access. Scope origin preserves fixture versus AE distinction. |
| RIT-003 | Safe blank/clean/idle main-thread AE observation and exact process/provider/root binding before claim and immediately before read. Registry/project/resident-image identity checked again afterward. |
| RIT-004 | Monotonic overflow-safe deadline checked before/after normal operations (completed capture/postflight evidence is saved even after expiry); expired marker never starts capture, expired final save never returns success. Timeout cannot interrupt a synchronous native call; external watchdog is still required. |
| RIT-005 | One durable claim, one marker, at most one capture, one diagnostic save, at most one postflight attempt and one result save. Partial failures preserve evidence; no host stop/cleanup/private call/provider retain or callback execution. |
| RIT-006 | Failure retains concrete bounded stage/reason and durability uncertainty; successful result means guarded copied-byte diagnostic only, not independent/live verification or registration eligibility. Strict compile/owned tests, full available clean regression, source review/static review and exact-source CI. |

## Boundary trust and remaining integration

An injected backend must independently measure loaded binary/provider/root and
process-start identity, enforce private no-overwrite durable storage and marshal
observations on the host main thread. Supplying matching scope fields is not proof
of that measurement or authority. The approval is an input contract, not a consent
UI or a substitute for the user's concrete permission. No code here installs,
launches or inspects AE. Backend result records are provisional producer evidence;
an independent supervisor must check byte evidence, all host observations and its
own elapsed deadline before accepting live PASS. A consumed or uncertain attempt
cannot be retried even if no marker exists.

Existing Safe/SameRuntime image policy is reused: resident images remain exact;
only new immutable /System/Library images are tolerated. The native adapter must
also supply measured binding again in every observation. No promise of atomic
host state, host lifetime/quiescence, provider retention, repeated-entry safety or
ResourcePassGate eligibility follows. Actual seven record names remain NOT RUN.

## Implemented preparation checkpoint

`RetainedIdentityTransaction.hpp` now binds an immutable copied plan and approval,
consumes all attempts atomically before any backend access and composes the
existing retained capture core with fresh observation, exclusive claim, marker,
postflight and provisional result boundaries. Existing journal/verifier, native
profiles/helper and ResourcePassGate are unchanged. The backend is still injected;
there is no native/disk adapter or live request in this checkpoint.

Focused retained family PASS: 14 Python tests, including 101 nested transaction
cases compiled with strict C++17 warnings-as-errors. Transaction success uses the
actual capture core on an empty owned-byte vector (four bounded copies); failure
injection covers each boundary, before/read/after identity and project changes,
expired/backward/overflowed clock, uncertain claim/marker/save, consumed retries,
reentrant/concurrent callers and caller-plan mutation. Completed capture copies
are saved even after deadline; postflight is attempted at most once, and original
failure reasons remain bounded/sanitized. A final save that exhausts the deadline
cannot return PASS; its already-persisted result is provisional and must be
rejected by the future independent supervisor's elapsed-deadline check.

Full clean regression, separate static/source review and exact-source CI pending.
Actual AE record identities remain NOT RUN. Next durable transaction evidence and
independent host verification/external supervision, then a separately identified
inert native candidate. Consumed observe-d548b007e316 authority stays consumed.
