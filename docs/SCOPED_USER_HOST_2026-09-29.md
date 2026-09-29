# Stage C: explicitly authorized working-host experiment

The user explicitly requested the ordinary working AE instead of an isolated
environment, then approved research-module installation and one AE restart.
This supersedes the isolation prerequisite for this one experiment, not for
release certification. Shared rules were reread (blob 701a8c1).

Baseline: AE 25.6x101 build 101 reports dirty=false, items=0, saved=false,
queued=0, rendering=false. Production Agent and third-party plug-ins remain
unchanged. Never quit unless a fresh blank/clean/idle baseline still passes.

The builder pins explicitly supplied canonical executable and plug-in paths.
The supervisor requires the same explicit paths again, checks loaded identity
and installed hashes, and preserves one-shot/registry/project/PID guards.
Default isolated-host behavior is retained. No shared-root scan, preference
reset, forced quit or private teardown is authorized by this record.

Mandatory before live execution: Python/Node regression, SDK build/signature,
native guards, inert-entry tests, exact installation hash verification, loaded
identity and fresh blank baseline. Success requires exactly the embedded fixture
added to the registry in the same PID with unchanged project revision.
Apply/render are NOT RUN in this registration-only fixture. A native crash is
possible; timeout or absence is FAIL, not grounds for a retry.

Cleanup: retire only the exact hash-verified research bundle to its build
directory. Do not unload native code from the running AE. A loaded module may
remain resident until normal exit; its one-shot latch prevents another scan.

## Executed result

Live registration gate: **FAIL**. No retry. This is not a registration fix.

- Source: `45de0c91112805cfdbc7528bb5747b41b14f13a8`, clean.
- Research Build/Run ID: `scoped-0b8c8f122e80`.
- Manifest SHA-256: `647e1e6479b62282ea61d81d16105b1f3c0ac35839afe5acc7cf61028543beb5`.
- Signed binary SHA-256: `de55a43878dca28a412a8dc00004e7d0c7b70f43fb118870777ed72e1244bc62`.
- Fixture: `88019a1a01a7`, match `AEHL.Embedded.88019a1a01a7`.
- Host: AE 25.6x101 build 101 arm64, PID 42039, started 2026-09-29
  14:15:53 local. Request 12:16:14.268336 UTC, result 12:16:14.923088 UTC.

Local checks: 108 Python, 62 Node, 15 native guard and three inert-entry cases
PASS. SDK build/signature/exports/getter PASS. Installed bundle hashes and
loaded research identity/path PASS. Static audit FAIL with the same five
previously documented findings outside this change; no new findings. CI for
this new source is NOT RUN at this record; previous CI is not substituted.

The one-root native call returned 1 and dyld reported the exact embedded
fixture image loaded. Video modules stayed 339 -> 339, added_modules=0.
All 785 effect identities before/after are byte-identical, target absent;
project revision stays 1. Native result: FAIL, stage=postflight. The outer
supervisor reports `research adapter stopped` because that marker is checked
first; it does not mean the AE process stopped.

Before/after snapshot SHA-256 (both):
`4bac64f5d06aecb2cad76c9497552c234d78f0c85ed9316d09de6034dbf03749`.
Supervisor JSON SHA-256:
`b21c4d66c9b8208545e2ee152bf8ce424148b7daa28afafcecef773a9791c5bd`.
Native loader log SHA-256:
`e9eefd0f8ddd73be00cebe3d7623255d20f2c85f70edcec8abe17887b85188df`.
Evidence lives under `build-ae-hot-loader/scoped-0b8c8f122e80/evidence/`.

An independent read-only AppleEvent postflight initially timed out at 15s.
The visible AE Home screen was dismissed with Escape; the pending script then
produced its record: exact version/build, dirty=false, items=0, saved=false,
queued=0, rendering=false, revision=1, target_matches=0. Same PID/start verified.
No crash was observed. This is not a broad responsiveness/stability guarantee.
Private independent record: current chat `work/ae-scoped-postflight.txt`.

Cleanup PASS: only the hash-verified research bundle was moved out of MediaCore
to the build directory's `retired-installed.plugin`. It is recoverable. No
forced unload or second restart was done; consumed module/fixture can remain
resident until normal AE exit. No preferences or third-party bundles changed.
AE remains open with an empty project. Apply/render NOT RUN by fixture scope.

Next: isolate the missing registry insertion/dispatch step using this noncrashing
embedded-resource result. Do not repeat the unchanged scan or claim that the
historical flat-resource crash or RSMB late registration has been fixed.
