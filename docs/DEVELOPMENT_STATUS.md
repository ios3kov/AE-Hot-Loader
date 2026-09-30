# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Current stage: **C of A–D**, with open gates in A/B/D. No completion percentage
or release approval. Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md), AGENTS.md
and shared DEVELOPMENT_RULES, rechecked at unchanged blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

The preceding status is preserved at
[immutable checkpoint 454806c](https://github.com/ios3kov/AE-Hot-Loader/blob/454806c96d1c2f869d5d00461a03b3182ce52c83/docs/DEVELOPMENT_STATUS.md).
Dated evidence remains unchanged. Old next-step instructions do not renew
permissions or establish a current runtime baseline.

## Latest result — complete v3 capture; resource and video-module paths separated

The user supplied `AEHL-MEE.tk18ws_t.zip`. All 12 payload hashes match its
record. Recomputed selection and actual v3 transcript validation pass:
41 windows, 3529 addressed instructions, 14116 bytes, no omitted/capped windows,
empty stderr and final quit. The before/after MEE hash statements match the
pinned image. Binary bytes were not supplied for independent image hashing.
This completes the requested file-only capture, not live registration.

New static finding: the identified AELibraryVideoFilterFactory checks the
PiPL resource-origin predicate. On the normal resource branch it retains the
IPlugin reference in a separate collection at factory+0x20, writes output
status zero and returns no video module. CreateUnknown only appends non-null
modules to the collection at +0x08 read by GetModules. AddModuleToList for this
concrete factory is a bare return instruction.

The retained-vector trace name mentions PLUG, but the shown branch does not
establish an actual PLUG registration call. A non-resource lane separately
constructs a video module and invokes a host setter callback during SetupFilter.
These paths are consistent with the historical dynamic/resource contrast;
the failed live run's receiver and predicate values remain unobserved.
Do not claim a proven live root cause or a repaired loader.

Four virtual-table entries were cross-checked with PluginSupport's constructor,
neighboring symbols and predicates, interpreting serialized chained-rebase
words rather than treating them as resident pointers. The original fixup-format
header and live receiver were not supplied; those limits remain explicit.

See [exact input hashes, 33 structural assertions, static addresses and next gate](MEE_RESOURCE_ROUTE_2026-09-30.md).
All 33 assertions pass on the supplied text; these are not unit or runtime tests.
Original inputs remain unchanged. No product/collector code, native build,
installation, restart, main change, merge or release in this continuation.

## Collector and prior automated checks

The successful uploaded collection used unchanged v3:
code/test commit `1fa62a775b0b0197f51c4e93b86caefba95c43d4`,
collector blob `57d992404cdb7e1cda82341db1c3e795173efeb9`, SHA-256
`1e198f5bf92e125c6577b9d60dd30754eb6ba687b290a9df547f22fb982c2d7e`.
The old v2 false-alarm capture remains a historical incomplete capture; its
missing after-image hash is not repaired by validating its transcript.

Prior CI for exact code 1fa62a7: research `36750543637` PASS, full macOS
`36750543464` PASS; macOS Python 208/208, research Python 202 PASS/six skips,
Node 62 PASS, native scoped guards 15 PASS. These are the previously recorded
checks, not new tests of a product change or real-AE integration.
[Collector fix and CI evidence](MEE_FACTORY_TRANSCRIPT_FIX_2026-09-30.md).

Full regression and static-security audit were not rerun for this docs-only
change. Five historical audit findings remain unresolved. Documentation uses
[skip ci]; a new documentation head is not a newly tested native artifact.

## Last real host results — separate and unchanged

| Gate | Result |
|---|---|
| Scoped embedded late registration | FAIL: source 45de0c9, Build ID scoped-0b8c8f122e80, fixture 88019a1a01a7; 785 unchanged effect identities, target absent |
| RSMB startup-registered apply/render | PASS: historical identified one-frame smoke, not broad certification |
| RSMB late registration | FAIL: retained separately from startup smoke |
| Dynamic fixture application | PASS: earlier exact-match add/remove; render NOT RUN |
| Earlier flat-resource failure | FAIL: historical crash evidence, not fixed |
| Current AE/project/runtime identity | NOT OBSERVED; file collection is not a live baseline |

[Scoped host test](SCOPED_USER_HOST_2026-09-29.md),
[RSMB apply/render](RSMB_APPLY_RENDER_PASS_2026-09-29.md),
[Dynamic application](REGISTRATION_APPLY_PASS_2026-09-29.md),
[flat-resource crash](RESOURCE_PAIR_CRASH_CORRELATION_2026-09-29.md).
The earlier PID 78417 observation is not a fresh blank/clean/idle baseline.
Local Mac source was last reported as ce5d80d; no local pull/update is claimed.
Reference product remains source 04fea706, Build ID native-36483421984-1;
no installed Agent, shell, panel or third-party effect changed.

## Next safe gate

Do not repeat MEE collection or the unchanged in-host scan. Inspect the resource
effect path in PLUG and FLT, whose dependency names/imports are present in the
supplied data. Identify its normal caller and relation to the host setter;
do not confuse an AEGP scan path with ordinary effect registration.

The linked report contains a read-only request that copies just PLUG.dylib and
FLT.dylib into a private Desktop archive, records before/after source hashes
and checks copied bytes. Original binaries permit independent hashing and
local offline analysis without another heuristic LLDB collector. The copy/archive
command passed shell syntax and an isolated Linux fixture check; actual Mac
execution is not yet observed. The local offline reader successfully inspected
an owned synthetic arm64 Mach-O without executing it. Proprietary binaries and
raw disassembly must remain private, never committed to the repository.

No discovered name or static branch authorizes private host calls. A risky live
experiment still requires separate consent, a falsifiable hypothesis, bounded
evidence and fresh host/project/runtime identities. Previous installation and
one-restart permissions are consumed. No forced notifier, speculative bool flip,
private teardown, preference reset or native unload.

Scope cleanup, controlled cold-start causality, demonstrated safe registration,
separate apply/render, real panel integration, IPC/repeat/timeout checks,
compatibility and the clean-candidate release gates remain open.
