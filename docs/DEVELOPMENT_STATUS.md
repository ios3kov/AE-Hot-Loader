# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Current stage: **C of A–D**, with open gates in A/B/D. No completion percentage
or release approval. Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md), AGENTS.md
and shared DEVELOPMENT_RULES, rechecked at unchanged blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

The preceding status is preserved at
[immutable checkpoint 8489d5c](https://github.com/ios3kov/AE-Hot-Loader/blob/8489d5c51cd08389e1f3c52a0985f53510e361a1/docs/DEVELOPMENT_STATUS.md).
Dated evidence remains unchanged. Old instructions do not renew permissions
or establish a fresh runtime baseline.

## Latest result — separate resource-effect registration chain mapped

The user supplied original PLUG.dylib and FLT.dylib in
`AEHL-PLUG-FLT.WyTSaS.zip`. Both received binaries were independently hashed
and match the identical before/after source statements. They were only read,
never loaded or executed. Input hashes were rechecked after analysis.

New conditional static chain: FLT_Birth installs FLT_PLUGScanFunc into PLUG's
scan list; PLUG_Search's file path invokes matching callbacks. The FLT callback
reads resource PiPLs and reaches FLTp_FiltSetup. A successful accepted path
registers a PLUG routine, then FLTp_AddEffect reaches the actual FLT filter
registry vector/map. Routine registration and effect publication are distinct.

A path predicate supplied to PLUG_Birth can skip a file before that callback.
Its concrete implementation and the normal caller's inputs are not identified.
The empty-input notifier does not enumerate these resource effects; forcing it
is not the missing resource pass. Neither PLUG_Search nor FLT_SetupAEPlugin
is explicitly called in the current InternalLoader.cpp, whose blob remains
`df64e125a984199e45cd777eef8c16a556ec393b`.

Together with the prior MEE resource-retention branch, this supports a concrete
missing-pass hypothesis, not proof of the failed live run's receiver, predicate
or root cause. Do not add a speculative private call, fabricate scan data,
change the bool, rerun initialization or trigger a broad PLUG scan.

Local LLVM 17 decoded the two arm64 text sections: 14572 and 165100 addressed
instructions, with full section-address coverage and no unknown words in the
final apple-m1 decoding. Sixteen BL targets were checked directly against raw
instruction words and eight additional text anchors passed. These **24
structural assertions** are static evidence, not unit or live-AE tests.

See [binary identities, exact addresses, checks, limitations and next request](PLUG_FLT_RESOURCE_REGISTRATION_2026-09-30.md).
No product/collector source, native build, installation, restart, main change,
merge or release in this continuation. Proprietary binaries and raw dumps stay
private, not in Git.

## Next safe gate

Inspect the normal resource-pass caller before considering a bounded runtime
test. The already received AfterFXLib symbols import PLUG_Search from PLUG,
but the failed earlier dump contains no instruction bodies. Obtain only the
original AfterFXLib binary with source-before/source-after/copy hash agreement;
the linked report includes a tested file-copy command. No repeat MEE/PLUG/FLT
collection or LLDB collector is requested. The identity of the path-predicate
owner remains unresolved; an import is not proof of actual invocation.

The file-copy command passed bash syntax and an isolated Linux fixture check,
not a Mac host run. It does not require AE running or execute any Adobe code.
Stop on missing files or changed hashes and preserve partial evidence.

Any risky host test requires a specific falsifiable hypothesis, fresh host/
project/loaded identity, bounded evidence and separate authorization. The
installation and one-restart permissions remain consumed. No unchanged scan,
forced notifier, private teardown, native unload or preference reset is allowed.

## Collector and prior automated checks

Last changed code/test commit remains
`1fa62a775b0b0197f51c4e93b86caefba95c43d4`, collector v3, blob
`57d992404cdb7e1cda82341db1c3e795173efeb9`, SHA-256
`1e198f5bf92e125c6577b9d60dd30754eb6ba687b290a9df547f22fb982c2d7e`.
Its complete MEE capture is recorded in
[MEE_RESOURCE_ROUTE](MEE_RESOURCE_ROUTE_2026-09-30.md); the historical v2
incomplete capture is not retrospectively promoted to PASS.

Prior CI for that exact code: research `36750543637` PASS, macOS
`36750543464` PASS; macOS Python 208/208, research Python 202 PASS/six skips,
Node 62 PASS, native scoped guards 15 PASS. These are prior checks, not new
tests of a product change or real-AE integration.
[Collector checks](MEE_FACTORY_TRANSCRIPT_FIX_2026-09-30.md).
This documentation-only continuation uses [skip ci]. Full regression and
static-security audit were not rerun; five historical findings remain open.

## Last real host results — separate and unchanged

| Gate | Result |
|---|---|
| Scoped embedded late registration | FAIL: source45de0c9, Build ID scoped-0b8c8f122e80, fixture88019a1a01a7; 785 unchanged effects, target absent |
| RSMB startup-registered apply/render | PASS: historical identified one-frame smoke, not broad certification |
| RSMB late registration | FAIL: retained separately from startup smoke |
| Dynamic fixture application | PASS: earlier exact-match add/remove; render NOT RUN |
| Earlier flat-resource failure | FAIL: historical crash evidence, not fixed |
| New live registration/apply/render | NOT RUN |
| Current AE/project/runtime identity | NOT OBSERVED; received binaries are not a live baseline |

[Scoped host test](SCOPED_USER_HOST_2026-09-29.md),
[RSMB apply/render](RSMB_APPLY_RENDER_PASS_2026-09-29.md),
[Dynamic application](REGISTRATION_APPLY_PASS_2026-09-29.md),
[flat-resource crash](RESOURCE_PAIR_CRASH_CORRELATION_2026-09-29.md).
The earlier PID78417 observation is not a fresh blank/clean/idle baseline.
Local Mac source was last reported as ce5d80d; no local pull/update is claimed.
Reference product remains source04fea706, Build ID native-36483421984-1;
no installed Agent, shell, panel or third-party effect changed.

Scope cleanup, controlled cold-start causality, demonstrated safe registration,
separate apply/render, real panel integration, IPC/repeat/timeout checks,
compatibility and clean-candidate release gates remain open.
