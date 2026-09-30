# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Current stage: **C of A–D**, with open gates in A/B/D. No completion percentage
or release approval. Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md), AGENTS.md
and the shared DEVELOPMENT_RULES, rechecked at unchanged blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

The preceding status remains available at
[immutable checkpoint 475f1ef](https://github.com/ios3kov/AE-Hot-Loader/blob/475f1efce04ddfacdd87a7b243fc748b5916ef71/docs/DEVELOPMENT_STATUS.md).
Dated evidence is not rewritten; old next-step instructions do not override
this page, renew permissions or establish a current runtime baseline.

## Latest result — false collector alarm resolved; concrete factory identified

The supplied MEE error archive was inspected. All 12 payload hashes match its
record; all 96 requested windows and 15408 addressed instructions are present,
followed by quit, with empty stderr. The v2 collector mistook six instruction
annotations containing error: or std::runtime_error:: for a debugger failure.
This defect is reproduced from the actual saved output. The original capture
still lacks its after-image hash, so its FAIL and unverified image stability
are preserved; transcript validation alone does not make it a complete capture.

Static MEE code now links the selected registry GUID
`7a7d3cd3-6b81-48f8-bee0-ec40018a4432` to
`ML::AELibraryVideoFilterFactory`. MEE_GetVideoFilterModules calls that same
factory's Instance/GetModules. This establishes a concrete static inspection
target, not the failed live run's receiver, rejection reason or a safe fix.

The prior selector gave every MEE_* function priority over factory methods.
Consequently the capped output omitted the key Create/CreateUnknown/
CreateUnknownImpl/AddModuleToList/GetModules bodies. Their symbols exist but
implementation semantics are not established. [Exact findings and evidence](MEE_FACTORY_TRANSCRIPT_FIX_2026-09-30.md).

## Verified collector v3

Code/test commit: `1fa62a775b0b0197f51c4e93b86caefba95c43d4`.
Collector blob: `57d992404cdb7e1cda82341db1c3e795173efeb9`.
Standalone `AEHL-collect-factory-v3.py`: 14644 bytes; SHA-256
`1e198f5bf92e125c6577b9d60dd30754eb6ba687b290a9df547f22fb982c2d7e`.
The standalone file is byte-identical to the successful macOS CI source snapshot.

Nonzero subprocess exits still fail. Validation now distinguishes diagnostic
lines from instruction data and requires every expected command/address plus
final quit; empty, partial, replayed and misordered transcripts fail closed.
The old --force correction is retained.

New explicit mode: `--module MEE --factory-only`. It pins the known main/MEE
image hashes and reads only the identified factory/module and related anchors.
On the supplied symbols: 41 windows, 37 previously missing plus four revisited
anchors, 14116 bytes, no cap/omission. This does not prove exhaustive function
boundaries. Ordinary mode retains 4096 bytes/window; explicit factory mode
allows 8192 to include the observed 4148-byte next-symbol span. The 96-window,
timeout/output limits and before/after image checks remain. FLT is not requested
at this gate because the concrete selected factory was found in MEE.

## Checks for exact source 1fa62a7

| Check | Result and scope |
|---|---|
| Local Python regression | 202 PASS, six macOS-only skips; 208 collected |
| Local focused checks | 55 PASS, two real-LLDB skips on Linux |
| Local Node | 62 PASS; panel/snapshot mocks, not AE |
| Saved MEE transcript and focused selection | PASS, supplied-file analysis only |
| Research CI | PASS, run 36750543637; 202 Python PASS, six skips, 62 Node PASS |
| Full macOS CI | PASS, run 36750543464; build/sign/package/smoke steps complete |
| macOS Python | 208/208 PASS, no skips |
| Real macOS LLDB regression | PASS: valid error: string accepted; old incompatible --force still fails |
| Native scoped guards | 15 PASS, mock loader, not AE |
| Downloaded evidence/source identity | PASS; both evidence ZIP hashes and all four changed code/test files verified |
| Actual v3 factory-only collection on user's Mac | NOT RUN; next bounded file-only request |
| Full static-security audit | NOT RUN again; five historical findings remain unresolved |

Real LLDB tests used Xcode 16.4/lldb-1700.0.9.502 and compiled an owned arm64
fixture without executing it. The user's saved transcript came from
lldb-2103.0.34.103 and was checked offline, not by a new host run. Detailed
artifact IDs/hashes are in the linked record. Documentation commits use
[skip ci]; CI applies to exact code 1fa62a7. The native package is not handed
over or installed. Green CI does not clear unreviewed warnings or certify AE.

## Last real host results — separate and unchanged

| Gate | Result |
|---|---|
| Scoped embedded late registration | FAIL: source 45de0c9, Build ID scoped-0b8c8f122e80, fixture 88019a1a01a7; 785 unchanged effect identities, target absent |
| RSMB startup-registered apply/render | PASS: historical identified one-frame smoke, not broad certification |
| RSMB late registration | FAIL: historical result, not repaired by startup smoke |
| Dynamic fixture application | PASS: earlier exact-match add/remove; render NOT RUN |
| Earlier flat-resource failure | FAIL: historical crash evidence, not fixed |
| Fresh current AE/project/runtime identity | NOT OBSERVED; offline file inspection is not a live baseline |

[Scoped host test](SCOPED_USER_HOST_2026-09-29.md),
[RSMB apply/render](RSMB_APPLY_RENDER_PASS_2026-09-29.md),
[Dynamic application](REGISTRATION_APPLY_PASS_2026-09-29.md),
[flat-resource crash](RESOURCE_PAIR_CRASH_CORRELATION_2026-09-29.md).
The earlier PID 78417 observation is not a fresh blank/clean/idle baseline.
Local Mac source was last reported as ce5d80d; no local pull/update is claimed.
Reference product remains source 04fea706, Build ID native-36483421984-1;
no installed Agent, shell, panel or third-party effect changed.

## Next safe gate

Collect only the exact v3 diagnostic with `--module MEE --factory-only`.
It does not require AE running, attach, launch, script, scan, unload or install.
It writes a new private Desktop archive and preserves prior evidence. Stop on
hash mismatch or tool error. Then inspect the missing factory's PiPL decisions
and module-collection updates offline. Do not infer registration success from
candidate counts, loaded images, disassembly or tests of the collector.

Any risky live operation still needs a falsifiable hypothesis, bounded evidence,
fresh host/project/loaded identity and separate authorization. The prior install
and one-restart permissions are consumed. No unchanged in-host scan, speculative
bool flip, forced notifier, private teardown, preference reset or native unload.

Scope cleanup, controlled cold-start causality, demonstrated safe registration,
separate apply/render, real panel integration, IPC/repeat/timeout checks,
compatibility and clean-candidate release gates remain open. No native product
source, main, merge or release was changed in this continuation.
