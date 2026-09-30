# Stage C: false LLDB alarm and concrete MEE factory identified

Date: 2026-09-30. Continues `475f1efce04ddfacdd87a7b243fc748b5916ef71`
on `research/ordinary-plugin-discovery`. Rules were rechecked at unchanged
blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`; AGENTS and PRODUCTION_PLAN
remain applicable. No native product source, installed module, AE process,
main branch, merge or release was changed.

## Acceptance and evidence

Reproduce the collector defect from retained input, preserve it unchanged,
reject genuine/incomplete tool output without rejecting strings in instructions,
verify with real macOS LLDB, and locate the selected factory using static data.
No new in-host scan, debugger attachment, installation or restart is permitted.

Upload `AEHL-MEE-error-20260930-190827.zip`: 262681 bytes; SHA-256
`ca15bd0e23c8b1da2e75ff0e9018b80c781c2f843c44a977666cdb083ed7499c`.
Exactly 13 regular files were read into a new private workspace. All 12 payload
hashes in record.json match; archive bytes were preserved. Key file hashes:

| File | SHA-256 |
|---|---|
| disassembly.txt | `a665fe663eec141dc16c8e2961fad6284e7c41a6b282688fac0cdc03b5efd791` |
| symbols.txt | `a89e7bbe32f74c9cc1a4f3955cc561942b95a44399f97059d3cf627b50995fa6` |
| inspect.lldb | `8747db241a581545ca8b9ec78c066967e3473f9ff6e52013e43dae7c7faa7c5e` |
| selection.json | `e809afa419d36ca406d49f80da040309629be0872ec8e3ddc839d7175c661a73` |

The recorded collector hash matches v2 exactly:
`04c94b6169ef0b40035c135d2cc8ac3da611ee72731b12a75add9c013b94fc17`.
MEE's recorded pre-inspection image hash is
`18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344`.
The binary was not uploaded; no independent rehash was possible. The failed
collector never recorded its after-hash. Original capture_status=FAIL and
image stability NOT VERIFIED are preserved; parsing the transcript does not
retroactively pass that capture or attest the installed/running library.

## Confirmed collector bug

The stdout contains all 96 requested disassembly commands, in order, followed
by quit. Every requested arm64 address is present in its window: 15408 addressed
instructions. Stderr is empty. These are transcript checks, not runtime tests.

The old `b'error:' in output.lower()` condition matches six ordinary instruction
annotations at lines 8557, 8784, 12804, 13506, 14971 and 14994. Two are string
literals and four name std::runtime_error constructors/destructor. None is a
line-level LLDB diagnostic. The precise saved output reproduces the old false
alarm and passes the new bounded-transcript validator without running LLDB.

The original process return code is not separately stored. The identified v2
code reaches this guard only after run_tool accepted exit zero; that is a
source-derived inference, not a new process observation. User LLDB version:
`lldb-2103.0.34.103`. No new AE crash or registration result is inferred.

## Concrete factory and collection now linked statically

The saved MEE disassembly, cross-checked with its nm symbols, identifies:

- `MEE_RegisterVideoFilterFactory` at 0x3dfb8. The 0x3dffc–0x3e02c sequence
  constructs registry GUID `7a7d3cd3-6b81-48f8-bee0-ec40018a4432`; 0x3e044
  creates an AELibraryVideoFilterFactory reference and 0x3e0a0 passes the GUID
  and factory interface to ML::RegisterPluginModuleFactory. This registry GUID
  is distinct from the separately named class-registration identifier.
- `MEE_GetVideoFilterModules` at 0x3e234 calls that factory's Instance at
  0x3e24c and GetModules at 0x3e298. Thus the factory and the collection queried
  by our loader are statically connected, rather than merely name matches.
- This is the same registry GUID selected by the final true flag in the earlier
  [PluginSupport analysis](REGISTRATION_DISPATCH_STATIC_2026-09-30.md).
  It does not prove which path/receiver executed in the failed live experiment,
  that MEE bytes were identical then, or that the flag should change.

Raw disassembly lines 11740–11782 and 11828–11853 contain the two main windows.
Their addressed-line SHA-256 values (LF joined, trailing LF, labels excluded):
`b3b43e1321616cc808dee79e48cb6fea0229351a826f639619a87e20ab64a99b`
and `4b64ef4f82363e8211db3404faf5661184f32c7074eeef7c02ff294570ffde6e`.
Eight structural assertions passed; they are not eight unit or host tests.
The private derived review JSON hash is
`2d7be79ed7b185225f38cb268558db90503fb66b3fa8323b63340a12758eb5a1`.
Full proprietary disassembly and paths are not committed or redistributed.

The old selector prioritized every MEE_* name before concrete factory methods.
Its 96-window limit therefore omitted Create, CreateUnknown, CreateUnknownImpl,
AddModuleToList and GetModules bodies. Their presence in nm is not proof of
implementation semantics. PiPL acceptance/rejection and module insertion still
need those missing bodies; no speculative native operation is justified.

## Fix, focused collection and exact identity

Code/test checkpoint: `1fa62a775b0b0197f51c4e93b86caefba95c43d4`.
Collector Git blob: `57d992404cdb7e1cda82341db1c3e795173efeb9`.
Standalone `AEHL-collect-factory-v3.py`: 14644 bytes; SHA-256
`1e198f5bf92e125c6577b9d60dd30754eb6ba687b290a9df547f22fb982c2d7e`.

The fix keeps nonzero subprocess status fatal, recognizes line-level diagnostic
errors, and additionally requires every requested window, every four-byte
instruction address and final quit. Empty/partial/replayed/misordered output
cannot pass even with exit zero. Instruction strings containing error: remain
ordinary data. Unsupported transcript formats stop rather than imply success.
The CLI approach is retained without introducing Python/LLDB binding dependencies;
[LLDB documents](https://lldb.llvm.org/man/lldb.html) batch/source/no-lldbinit.

`--module MEE --factory-only` selects the identified factory, module and four
registration/setter anchors. On the supplied symbols this means 41 windows:
37 previously missing and four revisited anchors, 14116 bytes total; none
omitted or capped. This is not proof of exhaustive function extents. Ordinary
mode retains the 4096-byte cap; the explicit factory mode allows at most 8192
bytes per window, because CreateUnknownImpl's next-symbol span is 4148 bytes.
Both modes retain the 96-window, subprocess-time and output-size limits.

The focus mode accepts only MEE, pins both main and MEE pre-inspection hashes,
and checks again afterward. It creates a new private output directory and never
changes the prior folder. No arbitrary library path, symbol command, attach,
launch, host expression, script or native plug-in scan is exposed. FLT is no
longer requested at this gate: the selected concrete factory was found in MEE.

## Checks and remaining gates

Local Python 3.13.5 regression: 208 collected, 202 passed and six macOS-only
cases skipped; 55 focused tests passed and two real-LLDB cases skipped locally.
Node v22.16.0: 51 panel and 11 snapshot tests passed. Diff whitespace and Python
compilation checks passed. The exact v3 bytes also validate the retained MEE
transcript and produce the focused selection above. This is not a Mac-host run.

CI for exact code `1fa62a7`: research run `36750543637` and full macOS run
`36750543464` both completed successfully. macOS: 208/208 Python tests,
62 Node tests and 15 scoped mock-loader guards passed. The real LLDB test
compiled an owned arm64 fixture, never executed it, and disassembled a literal
containing error:. The old substring predicate matches; the new validator
accepts both complete instruction windows. The separate old --force failure
still reproduces and fails as expected. Toolchain: Xcode 16.4,
lldb-1700.0.9.502, Python 3.14.7. This is not the user's live AE environment.
Research Linux CI: 202 tests passed, six platform-specific skips, 62 Node passed.

Both evidence ZIPs were downloaded and independently hash-verified:
research artifact `11115050140`, SHA-256
`6a9bb0de1f824408aa285aa69cd0270c1c169e4e52ecb9611b3a030ccdc6e1e7`;
macOS artifact `11114706700`, SHA-256
`8dce528f29e780985e64881c8024041584f8e1738f70563cb89c7b57f4e11c0b`.
Their test logs were read. All four changed code/test files match the downloaded
macOS source snapshot by hash; the handed standalone v3 is byte-identical to
that snapshot's collector. The full build/sign/package/smoke steps completed,
but the native package is neither installed nor handed over. Documentation
follow-ups use [skip ci]; CI belongs to this exact code commit, not a new build.

Historical scoped embedded late registration remains FAIL (source 45de0c9,
Build ID scoped-0b8c8f122e80); RSMB startup-registered apply/render PASS remains
separate from RSMB late-registration FAIL. Current AE project/PID/runtime
identity is NOT OBSERVED here. Five previously known static-audit findings
remain unresolved; that full audit was not rerun. No production-ready or
warning-free claim is made. Stages A/B/D and the release gates remain open.

Next collect only the missing MEE factory code with the identified v3 file:
`python3 "$HOME/Downloads/AEHL-collect-factory-v3.py" --module MEE --factory-only`.
This needs no running AE. Actual focused collection on the user's Mac is NOT
RUN at this record. Stop on mismatch or tool error and preserve the output.
Then trace the factory's PiPL decisions and collection updates offline. No
unchanged in-host scan, bool flip, forced notifier, private teardown or restart.
A future risky experiment still requires separate authorization and a fresh
host/project baseline; the previous install/restart permission is consumed.
