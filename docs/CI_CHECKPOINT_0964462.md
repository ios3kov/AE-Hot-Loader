# Passive bridge inspection checkpoint — 2026-09-28

Source: `0964462a75ce2c232813567dd40779193040ede8`.
Scope: standalone passive environment-data inspector, not an AE Hot Loader
product candidate. No product source, original preflight, workflow or dependency
was changed in this iteration.

## Verified diagnostic checks

- Local Linux: 22/22 new tests PASS; Python compilation PASS.
- The exact handed-over file was also run as a subprocess in an owned synthetic
  Linux HOME: existing response bytes retained; no request created; output
  explicitly left live Agent identity NOT RUN. This was not the user's bridge.
- Research run [36487362836](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36487362836), #12: both jobs SUCCESS.
- Reviewed research evidence: 83/83 Python tests (including all 22 inspector
  tests), 51/51 panel mock tests; no failures or skips.
- macOS build run [36487362750](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36487362750), #246: its static checks and complete Python/panel regression step passed. The full native job was still running when this diagnostic record was authored; no completed native-package claim is made here.

[Research evidence archive 10999563026](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36487362836/artifacts/10999563026)
was downloaded and SHA-256 checked:
`87f300f5d8a0678aa0796bebb0761c66d5d0760df93e1652e2deaf4a5e4157b8`.
Contents: `panel.tap`, `python-tests.txt`, `source-identity.txt`; all were read.
The identity file confirms source commit and attempt 1. Artifact retention is
30 days; this Git record preserves the checkpoint identity, not the full logs.

## Exact diagnostic file

Handed-over filename: `AEHL_Bridge_Inspect_0964462.py`.
Repository path: `tools/inspect_ae_bridge.py`.
Git blob: `d8e11636120087b99cf979560ecc226831d5070b`.
SHA-256: `d936898a9124e81caf1ede6f60db4f83fd9253dee53cb3f3bef151342f7604a1`.

Tests blob: `e8263612628d2cd22d67568173b8673b9f4dabca`.
Tests SHA-256:
`b0cd0283720611c5223764a8af2399c15f0e3410b72c33317132dcf748907835`.
Both Git blobs were fetched at the source commit and matched the local tested
bytes. The handed-over copy matched the inspector SHA-256 and was not modified.

Run on the Mac holding the bridge files:

```sh
python3 "$HOME/Downloads/AEHL_Bridge_Inspect_0964462.py"
```

It writes a new private `Downloads/aehl-bridge-.../report.json` only. It does not
call AE, issue Apple Events, scan plug-ins, publish commands, or delete/replace
bridge files. No running AE is required. Stored identity is compared only to
the immutable reference `04fea70` / `native-36483421984-1`, never labelled as a
verified resident identity. File age and matching IDs do not permit cleanup.

The minimal local report is still required because this development session
cannot read the user's Mac filesystem. Actual user-bridge inspection: NOT RUN.
Real panel roundtrip, controlled cold-start, apply/render and late registration
are not tested by this passive tool. No native bundle is handed over.

This checkpoint and the status update are Markdown-only successors. CI may be
skipped for this documentation commit; that does not skip code regression.
No main merge, installation, process control or release approval occurred.

The uploaded preflight's findings, limits and source hash are recorded in
[AE_HOST_PREFLIGHT_RESULT_2026-09-28](AE_HOST_PREFLIGHT_RESULT_2026-09-28.md).
