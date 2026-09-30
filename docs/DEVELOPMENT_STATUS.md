# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Current stage: **C of A–D**, with open gates in A/B/D. No completion percentage
or release approval. Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md), AGENTS.md
and shared DEVELOPMENT_RULES, rechecked at unchanged blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

The preceding status remains at
[immutable checkpoint 7791cee](https://github.com/ios3kov/AE-Hot-Loader/blob/7791cee394222aa29d6eb9c9a4a2f8757f7dcccc/docs/DEVELOPMENT_STATUS.md).
Dated evidence is not rewritten. Old instructions do not renew permissions or
establish a fresh runtime baseline.

## Latest result — ordinary resource caller, predicate and setter connected

The received `AEHL-aelib-bin.L6qzA9.zip` contains the original aelib binary.
Its independently calculated SHA-256 matches both before/after statements:
`f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f`.
Only file readers were used; no Adobe binary was loaded or executed.

The decoded InitIterator table maps PLUG predicate installation to index 13,
FLT initialization to 26, the resource pass to 31, standard suites to 32, and
the setter/AELibrary pass to 33. These are static indices in this exact binary,
not a recorded startup trace or public API. Resource enumeration precedes the
AELibrary pass; the two must not be conflated.

The resource stage calls PLUG_RequiredPreSearch, then Egg_PlugSearch. That
helper obtains ordinary folders and their owners through MEE_GetPluginsFolders,
then calls PLUG_Search with the default sack. Calling the helper directly
would enumerate the ordinary folder set, not one approved fixture root.

The concrete predicate is SkipHardcoded_PLUGScanFunc: it returns true when
MEE_HardcodedPluginsCache::GetAEPlugin(path) is non-null. PLUG's previously
inspected scan path skips files on true. The failed run's lookup result and
cache contents remain unobserved; do not alter or bypass the predicate.

The setter installed before LoadAEPlugins is local SetupAEPlugin. It delegates
to FLT_SetupAEPlugin and falls back to MEE_SetupAEGPPlugin on a negative result.
Both FLT and MEE module notifications follow LoadAEPlugins in this startup
lane. They are not substitutes for the separate earlier resource pass.

The entire text section decoded with 139753 addressed instructions, no unknown
instructions and empty stderr. Twenty-eight targeted structural assertions
passed, including 16 independently decoded BL targets. These are static-file
checks, not unit tests, runtime execution or a verified registration fix.
[Input identities, switch indices, addresses, checks and limits](AELIB_RESOURCE_PASS_2026-09-30.md).

## Assessment and next safe step

The startup chain now supports a precise missing-resource-pass hypothesis,
consistent with the prior MEE resource-retention path and our wrapper's lack
of an explicit resource pass. The failed live run's actual receiver, predicate
and root cause remain unproven. No product-loader change is justified as a
verified fix yet.

Existing supplied files are sufficient to specify the next bounded research
gate. No full-application archive or repeated per-library collection is needed
for this design step. A whole application bundle, rather than its tiny launcher,
would be the appropriate format for any later broader dependency inspection.

Prepare the gate around the existing scoped harness: resolve FILE_Spec creation
and ownership, use one owned embedded-fixture root rather than global folders,
retain the installed path predicate, pin exact host/modules, and require a
fresh blank/clean/idle project, durable one-shot claim, same PID and exact
registry delta with unchanged project revision. No lifecycle reinitialization,
RequiredPreSearch replay, callback replacement, cache clearing or global search.
Timeout or exit is not permission to retry. Apply/render remains separate.
This is a design boundary, not an implemented or approved runnable experiment.

Every risky live action still needs separate authorization and fresh host/
project/loaded identity. Prior installation and one-restart permissions are
consumed. Do not call Birth, advance InitIterator, force a notifier, unload
native code or repeat the unchanged scan. No new user command is requested.

## Code identity and checks

No product or collector source changed. Last changed code/test remains
`1fa62a775b0b0197f51c4e93b86caefba95c43d4`, collector v3. Previous CI remains
historical: research 36750543637 and macOS 36750543464 PASS; macOS Python
208/208, research Python 202 PASS/six skips, Node 62 PASS and 15 native
mock-loader guards PASS. They are not new tests of this analysis.

Full regression and static-security audit were not rerun for this docs-only
continuation; five prior audit findings remain unresolved. Documentation uses
[skip ci], not a newly tested native artifact or release approval.

## Last real host results — separate and unchanged

| Gate | Result |
|---|---|
| Scoped embedded late registration | FAIL: source 45de0c9, Build ID scoped-0b8c8f122e80, fixture 88019a1a01a7; 785 unchanged effect identities, target absent |
| RSMB startup-registered apply/render | PASS: retained identified one-frame smoke, not broad compatibility certification |
| RSMB late registration | FAIL: retained separately |
| Dynamic fixture application | PASS: earlier exact-match add/remove; render NOT RUN |
| Earlier flat-resource failure | FAIL: retained historical crash evidence |
| Current AE/project/runtime identity | NOT OBSERVED; offline binaries are not a fresh host baseline |

[Scoped host test](SCOPED_USER_HOST_2026-09-29.md),
[RSMB apply/render](RSMB_APPLY_RENDER_PASS_2026-09-29.md),
[Dynamic application](REGISTRATION_APPLY_PASS_2026-09-29.md),
[flat-resource crash](RESOURCE_PAIR_CRASH_CORRELATION_2026-09-29.md).
The earlier PID 78417 observation does not establish current project state.
Local Mac source was last reported as ce5d80d; no local pull/update is claimed.
Reference product remains source 04fea706, Build ID native-36483421984-1.

No installed Agent, shell, panel, third-party effect, settings or project changed;
no native build, main change, merge or release. Proprietary binaries, symbols
and raw disassembly stay private, outside the repository. Scope cleanup,
controlled cold-start causality, demonstrated safe registration, separate
apply/render, real panel integration, IPC/repeat/timeout checks, compatibility
and the clean-candidate release gates remain open.
