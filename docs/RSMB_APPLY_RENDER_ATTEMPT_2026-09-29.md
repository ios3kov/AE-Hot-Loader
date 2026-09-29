# Controlled RSMB apply/render host attempt — 2026-09-29

## Scope and identity

- Branch state before this documentation record: `d016564ddbe7a0a8fef5e0de8eec6feb30995afa` on
  `research/ordinary-plugin-discovery`.
- Harness source: `d19edca897bf2fec051ca6bc74d931416307759e`.
- Reference Agent source / Build ID: `04fea7060c7ef7ebc4a315b5c39364850287e294` /
  `native-36483421984-1`. This identity was verified by an earlier, separate
  live preflight; it was not queried by this attempt.
- Target host: After Effects `25.6x101`, macOS Apple Silicon arm64.
- Private preflight attempt IDs:
  `aehl-preflight-32c0718f34e44dd3b5cc21cf739df17b` and
  `aehl-preflight-e6a6330c230c45078bffd2779c6cd794`.
- Exact checked launcher SHA-256:
  `fddafcd2dbe2330b3cbfb5b31c3297f26648a4d91731701c929e68a210e0a09a`.
- Exact checked JSX SHA-256:
  `d691874c217c650d7ae994256dcd2d2e25b292904193e99a2269bb6058d52935`.
- Exact preflight collector SHA-256:
  `cfb7175f7f394b7bc17f838f8fb5337c9bee5e6fde46125570762c6d6b157865`.

The extracted launcher, JSX and collector were byte-identical to the harness
payload present at `d19edca` and still present at `d016564` before execution.

## Planned assertion

The controlled gate may claim only that an already registered
`Smart Motion Blur 3.x` can be added by exact match name, render one 64x64
frame, and leave the same AE process with a newly blank, clean project. Its
preconditions are a single AE process and a blank, unsaved, clean, idle host
project, plus fresh Agent identity and registry checks.

## Result

Overall controlled gate: **BLOCKED**.

Both fresh preflight attempts detected an active render in a saved, non-blank
project outside the test's ownership and stopped with `Blocked: AE is
rendering; diagnostic bridge request not sent`. They intentionally did not
publish a bridge request, create a disposable project, apply RSMB, or invoke
the JSX runner.

| Check | Status | Evidence / scope |
| --- | --- | --- |
| Fresh preflight collection | BLOCKED | Both attempts found an active AE render before a safe diagnostic query. |
| Agent identity in this attempt | NOT RUN | No bridge request was sent. |
| Bridge request | NOT RUN | The collector explicitly did not publish one. |
| Registry check in this attempt | NOT RUN | The formal gate did not pass its preflight. |
| Blank/clean baseline | BLOCKED | Required owned idle baseline was unavailable. |
| RSMB add / apply | NOT RUN | JSX was not invoked. |
| One-frame render | NOT RUN | No owned render was started. |
| Cleanup | NOT RUN | The JSX runner did not start. |
| Output SHA-256 | NOT RUN | No owned render output was created. |
| Same-PID postflight | NOT RUN | The JSX runner did not start. |

No RSMB compatibility conclusion follows from this attempt. In particular, it
does not change the separate statuses for controlled cold-start causality or
historical late registration.

## Safety and next step

No harness mutation, plug-in reload, installation, restart, preference change,
private teardown or process termination was attempted. This attempt has no
post-snapshot, so it does not claim `project_unchanged` PASS. The private host
evidence remains outside the repository.

When AE is again running exactly one instance with a blank, unsaved, clean and
idle project, rerun the same verified launcher. That run must perform fresh
pre/postflight, preserve the full evidence directory and output hash, and be
recorded separately as PASS, FAIL or BLOCKED according to its observed stage.
