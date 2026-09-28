# Controlled PiPL-only versus dynamic registration test

## Status

**PASS for the stated diagnostic claim; no production change.** In one live
After Effects 25.6 ARM64 process, the current Agent registered a probe that
exported `PluginDataEntryFunction2` and did not register an otherwise matching
probe that only had PiPL plus `EffectMain`.

This is a loader-path observation, not a claim that every PiPL-only plugin is
unsupported by After Effects. It is also not a RSMB fix.

## Baseline and controlled inputs

- Baseline commit before the test: `3654ad0`.
- Host: After Effects 25.6.0 ARM64, macOS Apple Silicon.
- Test Run ID: `registration-pair-2e8c5394d5e6`.
- AE PID before/after: `73375`.
- Project before/after: `items=0 dirty=false`.
- Both bundles were newly built from the same `RegistrationPair.cpp`.
- Both PiPLs declared `EffectMain`, identical category/version/flags, and
  unique short match names. The only intended difference was the exported
  `PluginDataEntryFunction2`.
- Test bundles were installed only under the test-owned directory
  `AEHLRegistrationPair2e8c5394d5e6`; after the test, that directory was moved
  into the run's `retired-installed` evidence directory.

## Procedure

1. Built and signed both fixtures with the run-specific manifest.
2. Captured a registry snapshot and verified neither match name was present.
3. Verified hashes after copying both bundles into the test-owned plug-in root.
4. Sent one `reload_plugins` request through the existing bridge.
5. Captured a second registry snapshot and process identity.
6. Retired the test-only installed directory after hash verification.

No AE quit, launch, teardown, project mutation, effect application, or render
was performed.

## Evidence

The local run directory is:

```text
build-ae-hot-loader/registration-pair-2e8c5394d5e6/
```

It contains the generated manifest, `before.txt`, `after.txt`, process records,
bridge request/response, agent log copy, and retired installed bundles.

The bridge response was:

```text
version=1
request_id=pair-2e8c5394d5e6
status=success
message=ordinary-discovery-v1: scanned:3 loaded:364 new_effect_modules:9
```

Registry result:

```text
before: count=785
after:  count=786
added:  AEHL.Dynamic.2e8c5394d5e6	AEHL Dynamic 2e8c5394d5e6	AE Hot Loader Diagnostic
```

The PiPL-only match `AEHL.PiPL.2e8c5394d5e6` was absent after the scan. Agent
diagnostics confirmed both images loaded and showed:

```text
PiPL probe:    PluginDataEntryFunction2=0x0, EffectMain=non-null
Dynamic probe: PluginDataEntryFunction2=non-null, EffectMain=non-null
```

The identical process identity and unchanged project state rule out a host
restart or project mutation as the explanation for this result.

## Interpretation

The current `ML::LoadPlugins` path does not register a PiPL-only fixture in
this controlled test. It does register the fixture with the dynamic entrypoint
used by the validated ordinary-discovery path. This provides a concrete,
reproducible host-side difference relevant to RSMB, whose bundles expose only
`mainB` and no `PluginDataEntryFunction2`.

The result does not prove that RSMB's `mainB` itself is invalid, nor that AE's
normal startup scan cannot load it. RSMB startup registration remains a
separate test. No private function was added or invoked.

## Checks

| Check | Status |
|---|---|
| Clean fixture build and export audit | PASS |
| Unique match names absent before scan | PASS |
| Same-process Agent scan | PASS |
| Dynamic fixture registered | PASS |
| PiPL-only fixture registered by current path | FAIL |
| AE PID unchanged | PASS |
| Project unchanged | PASS |
| Test-only installation retired | PASS |
| Apply/render | NOT RUN; registration-only fixture |
