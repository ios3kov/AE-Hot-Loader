# Resource representation pair: prepared gate

Stage C, rules blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608` unchanged.
Question: does a standalone .PiPL resource behave differently from an embedded
.rsrc resource during the already-tested ordinary late-discovery path?

## Identified input and offline results

- Source: `ddf42e55850a5afbd3c6135eca27731d0bcb5252`, clean build.
- Build ID: `79a6ce4be9f7`.
- Directory: `build-ae-hot-loader/resource-pair-79a6ce4be9f7`.
- Manifest SHA-256: `f673e5889993644560efc8f13a56a8c0d7548ca25e49857daf82f4bca7ce7615`.
- Exact matches: `AEHL.Rsrc.79a6ce4be9f7` and `AEHL.Flat.79a6ce4be9f7`.
- Both export only EffectMain; no dynamic registration entrypoint.
- Both use the unchanged SDK lifecycle implementation; render unsupported.
- Resource property sets differ only in name/match identity (unit test PASS).
- Both __TEXT,__text dumps are identical (diff exit 0); normalized text dump
  SHA-256 `e2fc9f64460c7598ec25b179ba0c83f83d7968b5083a010e95c65cac42871b06`.
  Full binary hashes differ and are recorded in the manifest; do not claim
  whole-file equality.
- Compilation, ad-hoc signatures and exports: PASS. Python regression: 92/92 PASS.
- Public resource reads without executable loading: PASS for both, 320 bytes.
  Rsrc URL count 0; Flat URL count 1.
- Rsrc payload SHA: `8becb5e8a6b3e4298512f5a3304a33551de15f7f3df8343f52b310618e92eae6`.
- Flat payload SHA: `69730ece7f62bbfa15a1d610642cd3bcb2e4c29702654775daf33c4d6c9677b3`.
- Reader executable SHA: `a5b4f3ca0c0fd128db1af25185c09ec53b8a85c9eadfce63d183b0d9ac91155a`.

## Predeclared live gate

Require one running AE 25.6 host, fresh Agent identity PASS, blank unsaved clean
idle project, unchanged preflight state, both exact names absent. Only then
copy the hash-verified pair into its new owned MediaCore subdirectory and issue
one existing ordinary reload request. Require matching response identity,
bounded timeout, same PID/start and unchanged project counters. Record each
exact registry result independently. Retire only the hash-verified owned
installation into the unique evidence folder; do not unload resident code.
No apply, render, quit, preferences changes, third-party edits or private
teardown. Preserve pending/foreign bridge state on timeout.

Neither registry presence nor offline resource reading proves runtime apply or
render. Flat success would support a resource-path hypothesis only for this
fixture, not fix RSMB. Both failing would leave dispatch/parser/registry-stage
hypotheses open. Startup control for this new pair is separate and NOT RUN.

## Live attempt — FAIL

Run `late-a60748b4fc87423f9ed6a4f4ba612aae` under the build directory above.
Fresh baseline: AE 25.6x101 PID 21778, start Sep 29 12:49:13 2026; Agent
`native-36483421984-1` identity PASS; blank unsaved clean idle project and
unchanged-project checks PASS. Both exact names absent. The collector's generic
registry/RSMB wording is not applicable to these overridden match-name inputs;
absence is the intended precondition, not a startup compatibility failure.

One reload request was published. No matching response arrived within 35 seconds:
overall gate FAIL, registry outcome BLOCKED, postflight BLOCKED. Neither fixture
can be classified registered or unregistered after this attempt. PID-specific
ps checks did not find PID 21778, and UI application inventory reported AE not
running. This is stronger than the earlier collector-only failure, but the cause
is still unknown; no crash report was found in the initial DiagnosticReports
search. No automatic restart or repeat request was made.

The shared Agent log snapshot ends at entry to ML::LoadPlugins for user MediaCore.
It has no per-record timestamps/PIDs/request IDs, so it does not prove the exact
failure point or implicate either fixture. Preserve it as supporting evidence,
not a correlated crash stack. Snapshot stored as `agent-log-snapshot.txt`.

Cleanup PASS: verified the complete exact installed file set against the manifest,
then moved the owned `AEHLResourcePair79a6ce4be9f7` directory to this run's
`retired-timeout` folder. Original installation path absent; files recoverable.
No bridge files were removed, no third-party files changed, and no host process
was terminated by the runner. At inspection request/response files were absent.
Result JSON SHA-256:
`fb1018541f4f9f10589907887fb17b914d6841be57dc0c0ff9aaa24437f316e9`.

Do not repeat this fixture in the working host until the interrupted scan is
diagnosed. Next: examine flat payload format/byte order against host parsing
and seek process-exit evidence, offline first. Build and resource-read PASS do
not establish that the flat resource is accepted by AE. Original historical
registration outcomes and prior Dynamic application PASS remain unchanged.
