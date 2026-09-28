# Verified research checkpoint — f274961

Date: 2026-09-28.
Commit: `f274961b14c28696b96e151d335924c76162f9c6`.
Run: [36472758795, attempt 1](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36472758795).
Conclusion: **SUCCESS**. This record describes that exact source/configuration.

| Check | Result | Evidence |
|---|---|---|
| Panel host-mock regression | PASS: 22/22, 0 failures/skips | job 109098841726, Node 22.23.2, Ubuntu 24.04 |
| Native C++ syntax, arm64 target, warnings as errors | PASS | job 109098841862, macos-15 |
| Root command script parsing | PASS | same native job, zsh -n |
| Source identity and evidence upload | PASS | panel job and archive below |
| Prior Node 20/punycode/url.parse warnings | Not present in reviewed replacement panel-job log | action versions changed; JSX/tests unchanged |
| Full native build, installation and live AE | NOT RUN | Outside these automated jobs |

Panel Git blob: `ff6fcab47c915265fa3e36d36d0ebce303b111ba`.
Panel SHA-256:
`b8b8146bb361c2aa9811830dafb5a087ef2d82b1735d891f9f3e10e3988bdfc0`.
Test runner SHA-256:
`82d23f3bb80df5aeb3fb10b91e90e453cd4c166e654f5b7fccb6477b814844bd`.

[Evidence archive 10992526995](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36472758795/artifacts/10992526995):
`research-evidence-f274961b14c28696b96e151d335924c76162f9c6-36472758795-1`.
ZIP SHA-256:
`8bc126b332b2eea760b5ffdd07c583ef217e95e819dac83c9b3be1cf401dfb53`.
Size: 1535 bytes. Retention: 30 days.
Contents: `source-identity.txt`, `panel.tap`. Source identities include the
commit, GitHub Run ID/attempt, Node version and panel/test SHA-256 values.

The first run and its dependency warnings are retained separately in
[CI_EVIDENCE_2026-09-28](CI_EVIDENCE_2026-09-28.md). That record is not rewritten
to hide the warning-producing configuration.

The new pinned action configuration passed both jobs and uploaded evidence.
No change to the native loader or private registration ABI was made here.
No actual AE process, project, GPU or installed plug-in was exercised by these
jobs. This is not a clean-install, full native build or release readiness claim.

Documentation consolidation following this checkpoint is limited to Markdown
files. Historical README/plan/audit copies retain their original blob SHAs;
current entry points explicitly identify their historical scope. The checks
for that docs-only commit must be read from its own workflow run, not inferred
from this checkpoint.
