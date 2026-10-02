# C1 diagnostic — authorized, blocked before live execution

Date: 2026-10-02. Stage C1, critical native/IPC research, Development.
Accepted rules: AE-Development-Rules 6.0.0,
`bb8b769404ddd5b97462812a4e6b430e8bfefe13`; AI_ENTRYPOINT, process safety,
identity/evidence, native debugging and one-shot IPC requirements apply.

## Authority and exact identity

The user explicitly replied **«разрешаю»** to the concrete pending scope:
install only `AEHLCleanupd548b007e316.plugin`, launch AE once only if no session
is running, and perform one read-only diagnostic capture in a fresh blank,
unsaved, clean, idle test project. Preserve working sessions and all evidence;
no automatic retry on refusal/failure/timeout.

This grants the diagnostic authority previously missing after automatic-review
rejection. It does not authorize private FILE/PLUG/resource calls, provider
retention, registration, callback replay, teardown or terminating AE.
The earlier rejection remains historical evidence; this attempt was permitted
by tool review and then refused by the orchestrator's environment preflight.

- Clean research branch HEAD: `05b07b1e8e3243492f6b63a907fe2947491f43c9`.
- Reviewed external supervisor source: `f4f84aa5a41fd86cc76ee2d702fe61e9b61d16e2`.
- Native candidate source: `7c983c5b5adfde0300f2370e5772ed757ab6b613`.
- Candidate: `observe-d548b007e316`, unchanged native bytes.
- Manifest SHA-256:
  `9f305a648b43a6569ccb70165169c2ed021d7977ddfbd9b84f3725d0bbdff100`.
- Native binary SHA-256:
  `cfbfa87038d2640a558ca0e30ca5c5d8b171aef8d8be4934f5c25f281950be56`.

## Preflight checks and refusal

The private orchestration verifies clean HEAD/branch, unchanged reviewed
supervisor family and native adapter/builder, exact manifest/payload inventory,
local signature, pinned host/providers, empty private control/journal directories
and an absent unique installation destination before live side effects.
These checks passed. The final process-list precondition then found an existing
After Effects session. Read-only PID/executable confirmation found PID **84352**,
the reviewed After Effects 2025 executable. No project, environment or internal
state of that existing session was inspected.

Result: **BLOCKED**, exit 2:

> existing AE/aerender session; preserved without changes

The unique installation destination remains absent. Control and journal remain
empty; no orchestration/native claim exists. Installation, AE launch, request
publication, internal-state capture, private Adobe calls, process termination
and retries were all **NOT RUN**. No diagnostic ZIP exists for this attempt.
The existing session was preserved. The native one-shot request was not consumed.

Private token-free preflight evidence SHA-256:
`014308a64d9e7259bd82527a896b06f55fed423dfee080236d3e50ae5dfd9f97`.
Evidence and the reviewed orchestration are retained in the owned local private
workspace; executable payloads/tokens/internal-state artifacts are not published.

## Next step and remaining gates

The blocker is now **environment safety, not missing diagnostic permission**.
The user must save their work and close the existing AE session normally before
resuming the exact authorized diagnostic. Do not terminate it, change its
project to satisfy a test baseline or poll/relaunch automatically. On explicit
resumption, repeat preflight and verify the same unused candidate; scope remains
one diagnostic with a fresh safe baseline, not any registration operation.

C0 stays PASS. Complete cleanup/allocation/lifetime/quiescence/repeat behavior
remain unproven; diagnostic PASS would not establish ResourcePassGate eligibility.
Native C1 registration backend NOT READY; registration/apply/render NOT RUN.
Historical late-registration FAIL and mandatory release gates remain unchanged.
Publication permission persists once those gates actually pass.
