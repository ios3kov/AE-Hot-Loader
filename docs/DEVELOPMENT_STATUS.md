# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Current stage: **C of A–D**, with open gates in A/B/D. No completion percentage
or release approval. Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md), AGENTS.md
and shared DEVELOPMENT_RULES, rechecked at unchanged blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

The preceding status remains at
[immutable checkpoint 61b14fa](https://github.com/ios3kov/AE-Hot-Loader/blob/61b14fafac48339a47a86d3bdc35f48e28368d2c/docs/DEVELOPMENT_STATUS.md).
Dated evidence is not rewritten. Old instructions do not renew permissions or
establish a current runtime baseline.

## Latest result — plugin initialization and preset scanning separated

The received AfterFXLib binary was independently hashed and matches both
source-before/source-after statements: SHA-256
`ce3aa2f16fe5449a77379a6b622e1a221596e511b86f7708dd3e2f7a3cced01a`.
It was read only, not loaded or executed. Input identity was checked again
after analysis. This is received-file identity, not resident-code identity.

The only direct B/BL reference found to AfterFXLib's PLUG_Search import stub
belongs to CFx::PresetFxSearch. Its caller creates a separate PLUG sack and
installs the FaFX preset callback. This is not the ordinary resource-effect
startup call; copying it would conflate preset scanning with effect registration.
Indirect/transitive calls are not excluded by this direct-reference search.

The ordinary plugin startup boundary is more precise now: MainMain calls
aelib::Birth, and CEggApp::BirthPlugins advances aelib::InitIterator through
the observed stage thresholds before its plugin-scan-complete diagnostic.
The separate preset scan happens afterward. Actual import library ordinals
resolve Birth and iterator advancement to
`aelib.framework/Versions/A/aelib`, a different file from AfterFXLib.
The iterator's implementation, resource-pass inputs and path predicate remain
unobserved. No startup lifecycle call is approved for late invocation.

Forty structural assertions passed: raw import/branch mappings, dependency
ordinals, negative import checks, selected window coverage and addressed
anchors. Seven windows contain 5,016 decoded instructions. This is static
file analysis, not unit tests, an executed startup trace or a live fix.
[Exact identities, addresses, checks and limits](AFTERFX_INIT_ITERATOR_2026-09-30.md).

## Retained research findings

The [PLUG/FLT resource-effect chain](PLUG_FLT_RESOURCE_REGISTRATION_2026-09-30.md)
remains valid within its conditional static scope: an installed FLT callback
can read PiPL resources, set up a PLUG routine and publish a filter into FLT's
registry. A path predicate can skip a file before that callback. The current
loader contains no explicit PLUG_Search or FLT_SetupAEPlugin call. A confirmed
safe missing pass has not yet been demonstrated.

The [MEE resource branch](MEE_RESOURCE_ROUTE_2026-09-30.md) retains resource
plugin references separately and returns no video module on its normal path.
The failed live run's receiver and predicate results are still not observed.
No forced notifier, speculative bool flip or generic extra dispatch is justified.

## Next safe gate

Obtain only the original `aelib.framework/Versions/A/aelib` binary, with
source-before/source-after/copied-byte hash agreement. This target is supported
by actual import ownership and caller instructions, not merely its filename.
No repeat AfterFXLib/MEE/PLUG/FLT collection or new LLDB collector is requested.
The copy/hash/archive command passed shell syntax and an isolated Linux fixture
check, not a Mac execution.

Inspect InitIterator's stage dispatch to locate the normal resource pass and
its predicate/setter initialization. Do not call Birth, advance a live iterator,
rerun subsystem initialization or launch a broad PLUG scan. An eventual live
test needs a falsifiable hypothesis, bounded evidence, fresh host/project/loaded
identity and separate authorization. Previous installation and one-restart
permissions remain consumed.

## Checks and code identity

No product or collector source changed. Last changed code/test remains
`1fa62a775b0b0197f51c4e93b86caefba95c43d4`, collector v3. Its previous CI results
remain historical: research 36750543637 and macOS 36750543464 PASS;
macOS Python 208/208, research Python 202 PASS/six skips, Node 62 PASS and
15 native mock-loader guards PASS. They are not new tests of this analysis.
Full regression and static-security audit were not rerun for this docs-only
continuation; five historical audit findings remain unresolved. Documentation
uses [skip ci], not a newly tested native artifact or release approval.

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
The earlier PID 78417 observation does not establish today's project state.
Local Mac source was last reported as ce5d80d; no local pull/update is claimed.
Reference product remains source 04fea706, Build ID native-36483421984-1.

No installed Agent, shell, panel, third-party effect, settings or project changed;
no native build, main change, merge or release in this continuation. Proprietary
binaries, symbols and raw disassembly stay private, outside the repository.
Scope cleanup, controlled cold-start causality, demonstrated safe registration,
separate apply/render, real panel integration, IPC/repeat/timeout checks,
compatibility and the clean-candidate release gates remain open.
