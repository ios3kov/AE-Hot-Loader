# RSMB registry follow-up

## Scope and acceptance

Baseline source: `b65f951`. Target: AE 25.6 ARM64. This read-only research
iteration checks SDK entrypoint requirements and observes the running host's
registry without closing its project. Required checks: a fresh registry
snapshot, exact RSMB match names, process identity, and source/installed file
hash comparison. This is not a controlled cold-start or a late-load gate.

## Correction to the previous interpretation

The SDK explicitly permits any effect entrypoint name specified in PiPL:
https://ae-plugins.docsforadobe.dev/effect-basics/entry-point/

Consequently, `mainB` versus `EffectMain` does **not** establish a different
effect ABI or a required legacy adapter. Absence of dynamic registration
exports remains a difference worth testing independently of the effect
entrypoint name. The earlier statement that the name explains the failure
was not supported by evidence. No startup-only requirement is established.

The previous resource report also omitted completed checks from its table:
Carbon Resource Manager successfully read RSMBPro64 (324 bytes) and
RSMBVecIn64 (336 bytes), as well as RSMB64 (316 bytes). These are readability
checks, not proof that every property is accepted by AE.

## Fresh observation

Run ID: `rsmb-baseline-1790621205439`.

`experiments/ordinary_discovery/snapshot.jsx` was executed through macOS
AppleScript `DoScriptFile` with a 30-second Apple Event timeout and 40-second
external command timeout. Result returned `0`.

```text
version=25.6x101
items=0 dirty=false
count=785
Smart Motion Blur 3.x          RSMB              RE:Vision Plug-ins
RS Motion Blur Pro A 3.x       RSMB Pro          RE:Vision Plug-ins
RS Motion Blur Pro Vectors 3.x RSMB Pro Vectors  RE:Vision Plug-ins
```

Process observed before this snapshot: PID `72664`, start time
`Mon Sep 28 20:46:27 2026`. This differs from the earlier late-load session.
No quit or launch command was issued by this iteration. The intervening
startup sequence was not controlled or monitored, so this observation must
not be promoted to a clean cold-start PASS.

The source and installed RSMB trees matched across all 15 files (30 hash
records, including both copies). Local raw evidence is under
`build-ae-hot-loader/ordinary-discovery/rsmb-baseline-1790621205439/`:
`registry.txt`, `processes.txt`, and `hashes.json`. This ignored build directory
is local evidence, not durable release artifact storage. The relevant
registry result is transcribed above for the Git record.

The shared Agent log ends with `ordinary-discovery-v1` startup messages and
contains earlier loader operations. Without timestamps/PIDs on those records,
it cannot independently tie the loaded Agent identity to this snapshot.

## Results

| Check | Status | Scope |
|---|---|---|
| Fresh registry observation | PASS | All three exact RSMB match names present |
| Source/installed file equality | PASS | All 15 files in supplied bundles |
| SDK entrypoint name check | PASS | Arbitrary PiPL-declared name permitted |
| Controlled cold-start | NOT RUN | Startup occurred outside this test |
| RSMB apply/render and panel visibility | NOT RUN | Registry-only observation |
| New late-registration gate | NOT RUN | RSMB already registered in this process |

Historical late registration remains FAIL; current registry presence does not
erase that result. The next discriminating experiment is a controlled pair of
owned probes with PiPL-only versus dynamic registration, holding effect code
and entrypoint naming constant. It requires unique match names absent from
the host baseline and per-run registry checks. This can investigate the
registration difference while preserving the running AE process.
