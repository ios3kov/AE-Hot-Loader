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

First code checkpoint `81adde7b815f6a95752d45177e78ce8a35e58397` passed full
clean local regression: 300 Python/no skips, 62 Node, 22 stages; private report
run `c27c5a6d482e4c63a8d324a862cf2e1e`, ZIP SHA-256
`8af6fea338eadedbb32690240f89a7c3093592751e783cb0316659ce3523c724`.
Inventory and all archived hashes independently verified. That checkpoint's
scan covered 266 supported files/no omissions; raw exit 1, sole known local
argparse false-positive. It does not verify the follow-up change below.

## Same defect in the no-scan sibling

Review identified the same missing deadline checks in the C0 supervisor, which
is also the diagnostic supervisor's common helper module. Two additional
synthetic tests reproduced both failures there (12-test suite, two failures
before fix). Apply the same SD-001/002 contract to this sibling: checks before
publication and before PASS, with no host action or historical-evidence rewrite.
The existing post-publication timeout fixture now supplies the additional
pre-publication clock observation; its one-publication/no-retry assertion is
unchanged. C0 is not rerun and its historical live evidence remains identified
at its original source. The defect reproduction here is offline transport only.

## Final combined verification

Exact code/test source **f4f84aa5a41fd86cc76ee2d702fe61e9b61d16e2**.
Focused supervisor family: **PASS, 27 Python tests**, including the four new
expiry regressions in two supervisors and the existing scoped supervisor.
Clean full local regression **PASS: 302 Python, no skips; 62 Node; 22 stages**.
Run `1d131fb00e3c4749b3c0504911781381`, macOS 26.6.2 arm64/Python 3.14.2.
Private ZIP `AEHL-checks-egdtk4_4.zip` SHA-256
`dd7e0777ea95999857bce874050fb9cc02725fb7fe80dbd617fc20d265e264ca`.
Complete ZIP inventory, every archived payload hash and unchanged clean source
inventory independently verified. Source inventory SHA-256
`b457704d3c26611c1fbe0d5d92770d4665a9943e6982c303e566bce0c61315b2`.

Offline code-profile scanner completed at the same clean source: 266 supported
files, no omissions; raw exit **1** / `review_required`, sole previously reviewed
`vibe.no_ratelimit_auth` false-positive at local `tools/artifact_manifest.py:71`.
Private scan JSON SHA-256
`14267d7f10e2c65915c55d775647c8bb7f275e2c3b5e48ad42e1b4ef59373bb9`.
This bounded text scan does not assess overall security or release readiness.

Exact-source research CI **37024297435** and full macOS CI **37024297373**
are both **completed / success (PASS)**, verified against the full source SHA
above. Research CI covers Linux/macOS offline checks; macOS product CI includes
build/sign/package and synthetic regression. Neither runs the actual live C1
diagnostic or proves ordinary-effect late registration. This scoped offline
deadline remediation is complete; live authority/registration gates remain open.

Separate diff review confirms changes are the two external deadline checks per
supervisor, four regression tests and the corresponding extra clock observation
in the old timeout fixture. No timeout values, native source, SDK contract,
provider profile, host eligibility or release policy were weakened. A deadline
failure after native completion may retain a valid native result, but overall
supervisor status stays FAIL and cannot authorize the next gate.

The older `observe-d548b007e316` artifact was not changed or installed. Its
native source and historic build evidence remain `7c983c5`; they do not verify
this newer external supervisor or establish live C1 eligibility. A future
combined live run must separately identify the supervisor source and exact
native candidate. C0 remains its recorded PASS; ordinary late registration,
apply/render and release gates remain open.
