# Uploaded host preflight and passive bridge follow-up — 2026-09-28

## Baseline and source evidence

Development baseline: `8678aa7743edcb79005dac8237f0dfd5e03a5740`, branch
`research/ordinary-plugin-discovery`. Shared DEVELOPMENT_RULES was rechecked;
blob `a1760fde8763f789b50b91c20407938b4fcaea4a` is unchanged.

The user supplied the requested `report.json` in this development conversation.
Run ID: `aehl-preflight-a4c98635a6604fe28141ecbcbaf15128`.
Input file SHA-256:
`4c579cad2feb9df478cb12ea7f7f017d34fdd636d4e2fce7aad4e6cf5fb01149`.
Reported collector SHA-256 matches the handed-over `1f8c7fc` collector:
`cfb7175f7f394b7bc17f838f8fb5337c9bee5e6fde46125570762c6d6b157865`.
This is supplied runtime evidence, not an AE execution performed by this session.
The raw report remains in the conversation, not copied into the public repo.

## What the uploaded report supports

| Check | Result | Scope |
|---|---|---|
| Read-only before/after snapshots | PASS | AE scripting version 25.6x101, build 101 |
| RSMB registry presence | PASS | All three exact match names below, before and after |
| Observed project counters | PASS, unchanged | Item/revision/queue/saved/dirty/rendering fields only |
| Resident Agent identity | BLOCKED | Existing bridge request/response; diagnostic query was NOT sent |
| Product ScriptUI roundtrip | NOT RUN | Snapshot collector is not the packaged ScriptUI panel |
| Controlled startup, apply/render and late registration | NOT RUN | No such operation in this collector |

Exact matches: `Smart Motion Blur 3.x`, `RS Motion Blur Pro A 3.x`,
`RS Motion Blur Pro Vectors 3.x`. Total registry count was 785 in both snapshots.
The project was already dirty before the test and remained dirty afterward;
this is not evidence that the collector made it dirty. Do not restart/quit AE,
close the project, or erase IPC state to progress this test.

The uploaded report does not identify which bridge file existed or its contents.
It does not establish a stale request, a dead Agent, a failed identity comparison
or an unsupported plug-in. `collection_status=COMPLETE` means data collection
finished, not that the Agent or product gate passed. Historical RSMB late-load
FAIL is not changed by these registry-only snapshots.

## Scoped follow-up and predeclared acceptance

Goal: identify the blocking existing file(s) without another active AE probe.
Only `tools/inspect_ae_bridge.py` and its regression tests are added. The original
collector, panel, Agent, private loader, dependencies and package are unchanged.

Acceptance: no Apple Events, process/network calls, commands or writes/deletes
in the bridge; read at most 16 KiB per existing record; reject symlinks, pipes,
wrong owner, incomplete/duplicate/unsupported fields and observed replacement;
redact messages, raw correlation IDs, unknown fields and paths. Record the
stored build metadata separately from live identity. Always leave resident
Agent identity NOT RUN and request execution state UNKNOWN.

The two file snapshots are not atomic and do not prove exclusive IPC ownership.
Matching stored IDs, success text, Build ID or modification time does not prove
that a request has completed, that a reply is fresh, or that deletion is safe.
The duplicated bounded-read primitive is intentional for a single standalone
non-installing diagnostic file; it is not a replacement for the live collector.

Run `python3 tools/inspect_ae_bridge.py` on the Mac holding the bridge files.
No running AE is required by this inspector and it never starts one. It creates
only a unique `Downloads/aehl-bridge-.../report.json`, with directory mode 0700
and report mode 0600. The report remains local; no automatic upload occurs.

## Available verification

- Local Linux: 22/22 new regression tests PASS, including the real CLI in an
  owned temporary HOME with process calls prohibited and bridge bytes retained.
- Python compilation check: PASS. Original collector byte equality: PASS.
- A test-mock reference needed correction after splitting the standalone tool;
  the final local run passed all 22 tests, none removed or skipped.
- Fresh macOS/research CI for the resulting commit: pending at authoring; record
  the actual run separately. Existing workflows already discover `test_*.py`.
- Actual user bridge inspection: NOT RUN until the local file is executed.
- This file is a minimal environment-data diagnostic, not an installable product
  candidate, a native loader change, or an AE Hot Loader release approval.

Inspector SHA-256:
`d936898a9124e81caf1ede6f60db4f83fd9253dee53cb3f3bef151342f7604a1`.
Tests SHA-256:
`b0cd0283720611c5223764a8af2399c15f0e3410b72c33317132dcf748907835`.
The final handed-over inspector must match the committed blob and these bytes.

Next: interpret the passive report, then obtain a fresh resident identity before
any authorized owned-project apply/render test. No automatic cleanup or restart
is authorized by a blocked diagnostic report.

File-I/O reference: https://docs.python.org/3.11/library/os.html (bounded reads,
file metadata and no-follow/nonblocking flags). Existing protocol contract:
`docs/BRIDGE_PROTOCOL.md`. No new host API is introduced.
