# Research CI evidence — 2026-09-28

## First verified research checkpoint

Commit: `721794e2601f134018b04ccceeeb531cb72cb4a8`.
Run: [36472464396, attempt 1](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36472464396).
This is evidence for that exact commit, not blanket approval of later changes.

| Check | Status | Evidence |
|---|---|---|
| Actual panel JSX under Node host mocks | PASS: 22/22 | job 109097858453, Node 22.23.2, Ubuntu 24.04 |
| C++ syntax with arm64 target, warnings as errors | PASS | job 109097857965, macos-15 |
| Root installer/helper zsh parsing | PASS | same native-syntax job |
| Live AE / native integration / rendering | NOT RUN | GitHub runner tests do not execute AE |

Tested panel SHA-256:
`b8b8146bb361c2aa9811830dafb5a087ef2d82b1735d891f9f3e10e3988bdfc0`.
Panel Git blob: `ff6fcab47c915265fa3e36d36d0ebce303b111ba`.
Test runner SHA-256:
`82d23f3bb80df5aeb3fb10b91e90e453cd4c166e654f5b7fccb6477b814844bd`.

[Evidence archive 10992366968](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36472464396/artifacts/10992366968):
`research-evidence-721794e2601f134018b04ccceeeb531cb72cb4a8-36472464396-1`.
ZIP SHA-256:
`266d59a06b1f403deb8c9da17a86e4a05edecbfc4f6d6a5d541f6d5b620c10c9`.
It contains `source-identity.txt` and `panel.tap`; artifact retention is 30 days.
This document retains the checkpoint identity after artifact expiration; rerun
the pinned tests if the full archive is no longer available.

## Follow-up: CI dependency warnings

The first run passed but emitted Node 20 action deprecation, `punycode`, and
`url.parse()` warnings from `actions/setup-node@v4` / `upload-artifact@v4`.
They originate in action dependencies, not the JSX. They were not hidden or
reclassified as clean runtime evidence.

The follow-up uses the officially published Node 24 actions:
`setup-node` v7.0.0 and `upload-artifact` v7.0.1, pinned to commit SHAs.
Checkout is also pinned to the previously tested SHA; credentials are not
persisted. Test Node is pinned to 22.23.2 and automatic package caching is off.
The JSX and tests are unchanged. Acceptance: both jobs and evidence upload
must pass again, with the deprecation warnings absent. Until a new run is
reviewed this follow-up is implemented, not yet verified.

No release package, installation, user process control or merge to main is
part of these checks. RSMB late registration remains unresolved.
