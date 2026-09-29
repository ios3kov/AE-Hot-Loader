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

Live result: NOT RUN at this planning checkpoint.
