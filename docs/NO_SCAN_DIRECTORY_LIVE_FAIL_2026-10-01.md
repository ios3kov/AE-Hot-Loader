# Stage C: first live no-scan directory gate — FAIL and offline remediation

Date: 2026-10-01. Branch: `research/ordinary-plugin-discovery`.

This record preserves the first real no-scan FILE directory-lifecycle attempt.
It does not relabel the result as PASS and does not authorize a retry.

## Live artifact and scope

The live run used:

- source commit: `161b180714a734baf71f8c8cb58440e73f8dcd23`;
- build ID: `noscan-f0aa4a3bd54a`;
- run ID: `directory-probe-11f0a9c60dc44fcea98579536234fd34`;
- AE: 25.6x101 arm64;
- report ZIP SHA-256:
  `727a65d7ba64be8371c40025a4fc2196785216cc77299941d0978a71eb0cff5a`.

The report ZIP integrity and every archived payload hash matched its
`report-hashes.json` manifest.

The run published exactly one authorized request. No plug-in scan or
ordinary-effect registration was requested.

## Preserved live result

Final status: **FAIL**.

The durable result reported:

- claimed: 1;
- call-started: 1;
- postflight observed: 1;
- cleanup_ok: 1;
- final stage: `postflight`.

PID/process-start, project revision and the complete effect registry remained
unchanged. Registry count remained **785**.

The only before/after runtime-image difference was one newly loaded Apple
system framework:

`/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/SafariPlatformSupport`

Image count changed from 1404 to 1405. No image was removed and no new Adobe,
user or plug-in image appeared.

The old gate required byte-identical full image lists, so this system lazy load
correctly caused the existing strict postflight check to fail.

The old evidence format did not persist the complete native lifecycle counters
before the postflight comparison. Therefore this report does **not** prove that
the FILE create/path-roundtrip/single-release operation itself satisfied all
native acceptance counts. It proves only that the private call was entered,
cleanup was reported successful, postflight was observed, and the run stopped
without retry.

## Offline remediation

The gate was hardened after analysis of the report:

1. Native lifecycle evidence is now persisted in a dedicated durable
   `native.txt` immediately after the private call and before postflight.
2. PASS requires exact native evidence:
   - invoked = 1;
   - completed = 1;
   - cleanup_ok = 1;
   - two host strings created and released;
   - one specification created and released;
   - three retained provider references.
3. Existing runtime images may not disappear, move or change identity.
4. New runtime images are permitted only under the immutable
   `/System/Library/` root, covering observed macOS lazy framework loading.
5. Any new Adobe, user or plug-in image remains a FAIL.
6. The external supervisor independently verifies the same native evidence and
   system-lazy-image policy.
7. The durable journal still accepts only fixed record names; `native.txt` is
   the sole newly admitted record.

Current remediated code head:
**`dadd884b4758a351fbc725969ed49d2f9a912781`**.

Exact-head verification:

- research CI `36857286317` — **PASS**;
- full macOS CI `36857286194` — **PASS**.

These are offline/build results only. No second live private FILE call was made.

## Next gate

A second live no-scan attempt is required to determine the native lifecycle
result with the corrected evidence format and system-lazy-image policy.

That attempt is a new risky host operation. The previous authorization was
consumed by the first request and does not authorize a retry.

The next authorization, if granted, remains limited to:

- one fresh helper build/install if needed;
- one AE launch if needed;
- one private FILE directory-lifecycle request;
- retaining the three already-loaded FILE/U/dvacore references;
- no plug-in scan;
- no ordinary-effect registration;
- no automatic retry after an uncertain outcome.
