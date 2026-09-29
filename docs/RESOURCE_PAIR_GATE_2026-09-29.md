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
