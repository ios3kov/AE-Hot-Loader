# AE Hot Loader — current development and release plan

Updated: 2026-09-28. Branch: `research/ordinary-plugin-discovery`.
Current verified source and evidence: [DEVELOPMENT_STATUS](DEVELOPMENT_STATUS.md).
The prior plan is preserved [verbatim](archive/PRODUCTION_PLAN_6037df8.md).

## Scope

Primary research: add a previously absent ordinary effect to the running
AE 25.6.0 arm64 host, then prove it can be applied and rendered in the same
process. Adding a new plug-in and replacing the implementation of an already
loaded plug-in are different claims.

Keep the generic Agent, ordinary discovery, Control Shell and RSMB research.
The adapter-specific cleanup direction comes from the original
[status snapshot](DEVELOPMENT_STATUS_2026-09-28.md). Removing outdated adapter
claims from the current plan is not a declaration that those adapters passed
or were integrated. Their historical requirements and results are preserved.

No production loader changes without a demonstrated registration step. Do not
call unverified private shutdown/teardown/reinitialization functions. Do not
merge to `main`, publish, install, purge user state or close a working AE
process as a side effect of these development checks.

## Completed in this iteration

1. The panel compares registry identities rather than trusting loaded module
   counts, preserves partial failures, rejects malformed protocol fields and
   restores the UI after tested I/O failures.
2. Research pushes run 22 panel host-mock tests plus macOS native syntax and
   script parsing checks. Actions and test Node are pinned; reports identify
   the tested source and run.
3. Current product documentation distinguishes historical AE results, new
   automated checks and remaining release gates. Original documents remain
   available unchanged.

These are implementation/limited-regression results, not a release milestone.
See [CI evidence](CI_CHECKPOINT_f274961.md).

## Next stages and predeclared acceptance

### A. Finish scope cleanup and reproducible native checks

- Inventory adapter-only references, fixtures, commands and packaging entries.
- Remove only those outside the retained scope; preserve generic shell tests
  and historical evidence. Full repository-wide cleanup is still NOT RUN.
- Add the full native build/sign/package gate for the research source; the
  current syntax-only job is not a substitute.
- Record generated component Build IDs, exact source state, toolchain/SDK,
  final package SHA-256 and loaded runtime identity where available.

Gate: scoped checks pass, package identity is complete, generic shell/Agent
coverage is retained and no removed item is silently needed by packaging.

### B. Controlled RSMB startup baseline

First establish startup registration independently of late loading. This test
has not been run and no new automated runner is claimed in this iteration.

Required inputs and safeguards:

- authorized isolated AE 25.6.0 arm64 environment and licensed test plug-ins;
- inventory of active bundles, hashes, known dependencies and duplicate names;
- a fresh Run ID, source/runtime identities and a dedicated evidence directory;
- a known initial host state and explicit ownership of the test project;
- bounded timeout with crash/hang detection; no old PASS file reuse;
- preserve user preferences, unrelated plug-ins and unsaved work.

Gate: capture exact effect match names after a controlled cold start, then
apply each required effect and render identified outputs from the owned
fixture. Record startup, apply and render as separate results. A registry-only
observation cannot pass the apply/render gate. No response means NOT RUN,
BLOCKED or FAIL according to the observed stage, never PASS.

### C. Investigate legacy late registration

Use the controlled PiPL-only/dynamic pair and the startup baseline to isolate
the missing registration step. Preserve host identity, exact bundles and
before/after registry identities. Do not blame the legacy entrypoint name
without evidence. Do not broaden support from one fixture to all third-party
plug-ins.

Gate before changing the native path: a repeatable, bounded test demonstrates
that the proposed step registers the intended missing match name without
restart, project corruption or unsafe lifecycle calls. Validate apply/render
separately with a render-capable fixture.

### D. Integration and safety hardening

- Real ScriptUI/Agent round-trip and registry behavior of the updated JSX.
- Panel reopen, multiple instances and shared-bridge ownership.
- Timeout/retry policy while a native scan may still be running.
- Repeated scan, no duplicate registration and unchanged project state.
- Existing-instance behavior and host responsiveness.
- Any future shell-mode integration has its own reload/cache-refresh gate;
  do not silently apply shell claims to the ordinary-discovery button.

## Release gate

Before handing over an installable candidate:

- clean source, reproducible build/package and final artifact identity;
- all applicable Level 1 and Level 2 checks required by DEVELOPMENT_RULES;
- real-AE clean install and runtime identity confirmation;
- intended effect absent before scan, present afterward, applies and renders
  in the same identified process;
- repeat/error/timeout/duplicate and project-safety scenarios;
- applicable host/version/architecture and render compatibility matrix;
- logs investigated, no mandatory FAIL/BLOCKED/NOT RUN;
- documentation and evidence tied to the exact candidate, not an older build.

No completion percentage is assigned while the core legacy registration and
real-AE integration gates remain open.
