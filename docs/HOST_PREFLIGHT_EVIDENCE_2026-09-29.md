# User host preflight evidence — 2026-09-29

Source collector: `AEHL_Preflight_1f8c7fc.py`, SHA-256
`cfb7175f7f394b7bc17f838f8fb5337c9bee5e6fde46125570762c6d6b157865`.

## Observed host

- After Effects `25.6x101`, build 101.
- Three exact RSMB match names are present in the installed effects registry:
  `Smart Motion Blur 3.x`, `RS Motion Blur Pro A 3.x`,
  `RS Motion Blur Pro Vectors 3.x`.
- Project counters were unchanged before/after the read-only probe. The project
  was saved but dirty; no render was active.
- Resident Agent identity was BLOCKED because bridge state already contained
  `response.txt`; the collector correctly did not overwrite or delete it.
- Passive inspection found no `request.txt`, one 127-byte `response.txt`,
  protocol v1, status success, no stored Agent identity fields, and explicitly
  classified it as stored/stale-capable evidence rather than resident identity.
- Cold start, ScriptUI roundtrip, apply, render and late registration remain
  NOT RUN by these reports.

## Interpretation

Registry presence is confirmed for this running host, but it does not establish
that RSMB was cold-start registered by this test or that it applies/renders.
The stored bridge reply cannot identify the currently resident Agent. Before a
new diagnostic query, the old response may be archived rather than deleted,
but only after exact hash/size checks and with no concurrent panel command.

No project, preference, plug-in or process modification was performed by the
evidence collection.
