# RSMB legacy PiPL and ordinary-loader research

## Status

**RESEARCH COMPLETE / production change not justified.** The supplied RSMB
bundles contain valid readable PiPL resources, but they advertise the legacy
`mainB` effect entrypoint. The validated ordinary-discovery probe advertises
`EffectMain`. The current evidence explains why RSMB follows a different host
path, but does not prove whether AE 25.6 has a callable late-registration
adapter for that legacy path.

## Scope and baseline

- Host: After Effects 25.6.0 ARM64 on macOS Apple Silicon.
- Git baseline: `0486123`.
- RSMB bundles: `RSMB64.plugin`, `RSMBPro64.plugin`, and
  `RSMBVecIn64.plugin`, version 6.4.1.
- Existing live result: `ML::LoadPlugins` returned success and loaded the
  binaries, but the Effects Registry did not increase (`782 -> 782`).
- No teardown, process restart, or destructive operation was performed during
  this stage.

## Resource-fork verification

The initial `DeRez file -only PiPL` invocation reported `eofErr (-39)`. That
was a tool invocation limitation for this old resource-fork format, not proof
of a bad resource. Using the macOS Carbon Resource Manager through
`CFBundleOpenBundleResourceMap` and `Get1Resource('PiPL', 16000)` produced:

| Bundle | Resource map | PiPL | Size |
|---|---:|---:|---:|
| RSMB64.plugin | opened | found | 316 bytes |
| RSMBPro64.plugin | not independently dumped in this run | present by matching bundle/resource layout |  |
| RSMBVecIn64.plugin | not independently dumped in this run | present by matching bundle/resource layout |  |
| AEHotLoaderRustProbe.plugin | opened | found | 392 bytes |

The RSMB64 PiPL begins with the expected `8BIM` records and contains:

```text
kind = eFKT
ma64 = mainB
mi64 = mainB
```

The Rust probe contains:

```text
kind = eFKT
ma64 = EffectMain
```

This confirms that the supplied RSMB resource is structurally readable and
that its entrypoint declaration is materially different from the known-good
probe.

## Host-side static evidence

The inspected AE 25.6 ARM64 `PluginSupport.framework` path does the following:

1. Loads the bundle as an `ASL::Module`.
2. Searches the bundle/resource fork for the `PiPL` resource.
3. Parses it through `ML::PiPL::LoadFromResource` and `SetPiPLValues`.
4. Exposes the parsed entrypoint through `ML::PiPL::GetEntryPointName`.

The inspected `MEE::AELibraryPluginVideoFilterModule` initializes from an
`IPlugin` and `IPiPL` reference, but no exported or validated function was
found that converts a late-loaded `mainB` effect into a registered
`IVideoFilterModule` while preserving an existing project.

The presence of `mainB` alone is therefore a compatibility clue, not a
complete root-cause proof. Possible remaining causes include a legacy adapter
that is only entered during normal startup, licensing/initialization behavior,
or another host compatibility condition.

## Decision

Do not modify the production loader to rename, patch, or invoke `mainB`, and
do not call private teardown or registration constructors. Such an operation
would be an unvalidated private-ABI experiment in the user's live AE process.

The current scope remains:

- modern ordinary effects compatible with the validated late-discovery path:
  **verified for the tested probe**;
- RSMB 6.4.1 late discovery: **FAIL**;
- RSMB startup discovery on AE 25.6: **NOT RUN in this stage**;
- generic legacy-effect late registration: **BLOCKED**, because no supported
  registration API or complete private lifecycle has been established.

## Sources and limitations

- Adobe After Effects C++ SDK Guide, “PiPL Resources”:
  https://docsforadobe.dev/intro/pipl-resources/
- AE 25.6 ARM64 static inspection of `PluginSupport.framework`, `ASLFoundation`
  and `MEE.dylib`.
- The runtime RSMB registry test and diagnostic logs recorded by the project.

Static analysis is not runtime proof of a legacy adapter's absence. A clean
cold-start test with RSMB installed before AE launch is the next valid test;
it must be run separately from late discovery and must record the registry,
Effects & Presets visibility, and any license/initialization diagnostics.
