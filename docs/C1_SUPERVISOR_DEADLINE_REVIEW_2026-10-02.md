# Stage C1: external supervisor deadline boundaries

Baseline: clean research head `68fcf73`; candidate native source `7c983c5`.
Accepted rules: `b27f45467e0a9152fc82c1072438dfed07f0c36e`.
AI_ENTRYPOINT selects scoped bug reproduction/fix, PROCESS safety/regression/
evidence and ENGINEERING debugging/documentation. Product scope unchanged;
independent offline work while concrete live diagnostic authority is pending.

## Contract and reproduction

- SD-001: once the diagnostic supervisor's absolute deadline has elapsed during
  preflight, it must not publish a native request. Keep the exclusive attempt
  claim and an identified failure report; refuse reuse without retry.
- SD-002: a valid native diagnostic journal must not turn into supervisor PASS
  when final identity/provider/bundle verification finishes at or after the
  deadline. Preserve the native evidence and failure report; no process stop,
  retry or permission/registration conversion.
- SD-003: retain ordinary timely success and existing failure behavior. These
  deadline checks bound acceptance/publication, not the wall time of a blocking
  filesystem operation or the later report packaging.

Two synthetic transport regressions reproduced the original defects before
the fix: elapsed preflight still published one request; a complete matching
journal was accepted as PASS after final provider verification reached the
deadline. The original focused suite ran seven tests with exactly these two
failures. No Adobe process, private call, actual root read or install occurred.

## Minimal change and focused verification

Two monotonic deadline checks in `run_cleanup_observation_probe.py`: after
preflight before publication, and after final verification before accepting
PASS. Existing exclusive claim, exception handling and token-free report
packaging preserve both failure outcomes. No native source/ABI/SDK API change.

Focused suite: **PASS, seven Python tests**. New cases verify zero publication
and consumed-attempt refusal after preflight expiry, and one publication with
all six native journal files retained after late verification. Existing
identity/tamper/count/order/success/timeout tests remain PASS. These are offline
synthetic evidence only, not live AE observations.

Full clean-source regression and exact-code CI: **NOT RUN** at this code
checkpoint; run next and append exact revision/report identity before closeout.
The older `observe-d548b007e316` artifact was not changed or installed. Its
native source and historic build evidence remain `7c983c5`; they do not verify
this newer external supervisor or establish live C1 eligibility. A future
combined live run must separately identify the supervisor source and exact
native candidate. C0 remains its recorded PASS; ordinary late registration,
apply/render and release gates remain open.
