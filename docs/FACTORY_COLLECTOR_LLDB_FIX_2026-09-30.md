# Stage C: collector option failure reproduced and corrected

Date: 2026-09-30. Continues `687ff5192f5740fe6384e02fc3c7966a0b86a03a`
on `research/ordinary-plugin-discovery`. AGENTS.md and the current shared
DEVELOPMENT_RULES were consulted; the existing A-D production plan is unchanged.
Scope: repair the offline diagnostic, not the native plugin loader.

## Acceptance and safety

Read the actual partial archive; identify the failed command; reproduce its
failure using real LLDB against an owned synthetic Mach-O; verify the corrected
command; retain bounded commands, input identity, failure evidence, and existing
regression coverage. Do not run or attach to AE, install, restart, scan, change
private loader flags, modify main, merge or publish a release. Historical runtime
results and the consumed installation/restart authorization remain unchanged.

## Received failure evidence

Upload: `AEHL-AfterFXLib-error-20260930-184842.zip`, 1,622,563 bytes.
Archive SHA-256:
`f698df6fce664675f8804e7745bd02842c51166b0f3985e09bcca4837821b644`.
Ten regular entries were read into a separate analysis directory, with bounded
sizes and no directory traversal or symlinks. The original upload is unchanged.
Full proprietary symbols and private paths are not committed.

| Input | SHA-256 |
|---|---|
| disassembly.txt | `855bd22b753bad5ace890c1da54f567a9e8f9aa8feceb85808cf5016a0ec89d7` |
| disassembly.txt.stderr | `fd2a1a23588c253c57076808cbeba6eafb7595156fc3a65cdda13cb0fa09233c` |
| inspect.lldb | `9956f83303b0fd507d2a2d45c6542c55fa01987e8cae3f7687863bf3c03a84ef` |
| symbols.txt | `b95e127cd163e179df6a17aedf0661373457c76323941afe6aae3a84d06302be` |
| libraries.txt | `9ece9140fc692d3ec65a868cf429b64144146875a4497603073bf87040588598` |
| selection.json | `648270e2b470c53c8128ba61d59bea991fdd51862805c0f14008042adbb6d666` |
| headers.txt | `d244bf486da1956394506840c2fc7af06050834533a6c603df8a27ec3127cf22` |

The original collector copy matches SHA-256
`10097a09b97876d6bbf4fce9c5abf5a5ebc300826d5dfefac906859a8863f89c`.
LLDB accepted the offline target and settings, then rejected its first
`disassemble --start-address 0x7b28 --end-address 0x804c --force` command with
`invalid combination of options for the given command`. No instruction body
was captured. This is a diagnostic CLI failure, not an observed AE crash or a
new plugin-registration result.

The old collector saved record.json only at successful completion. Accordingly,
this partial upload has no durable before/after AfterFXLib hash record. Do not
invent one or claim the binary was independently rehashed here.

## Cause, fix and test gap

LLDB assigns explicit end-address to option group 1, while force belongs to
other groups. The combination is invalid. Primary reference:
[LLVM Options.td, disassemble options](https://github.com/llvm/llvm-project/blob/main/lldb/source/Commands/Options.td).
The previous mock test asserted the invalid string and never executed LLDB;
its green result did not validate the real command parser.

Changes in collector source `7885797` and tests through
`4d31a39cbb3a0acec9adc5fbdd6f6a139c0c5673`:

- Remove only --force from bounded explicit start/end disassembly commands.
- Save collector/module/input identity before the first inspection tool.
  On failure, record FAIL and preserve partial outputs; a post-failure image
  hash remains unverified rather than silently inheriting the earlier value.
- Save the actual LLDB version. Exclude record.json from its own hash map.
- Add explicit module choices AfterFXLib, MEE and FLT, with literal paths.
  Reject unknown/duplicate choices and stop after a failed module without retry.
  The default remains AfterFXLib for compatibility with existing callers.
- Correct the mocked command contract and add actual macOS LLDB regression.

The corrected collector was compared byte-for-byte with the source.tar.gz
saved by the macOS CI run, not only with the conversational code text.
Collector Git blob: `49780e919f5e0128479cb35f26f578d7e71dce03`.
Collector SHA-256:
`04c94b6169ef0b40035c135d2cc8ac3da611ee72731b12a75add9c013b94fc17`.
The standalone `AEHL-collect-factory-v2.py` is exactly those bytes. This is a
file-only diagnostic handoff, not an installable AE product or native release.

## New information already recovered, without another capture

The symbol selection was regenerated from the uploaded nm text and equals the
saved selection exactly: 117 matching addresses, 96 selected, 21 omitted.
Every generated LLDB command equals the saved script after removing --force.

The supplied dependency list explicitly identifies MEE.dylib and FLT.dylib in
Contents/Frameworks. The nm listing attributes 63 undefined imports to MEE and
67 to FLT. It does not expose the requested direct factory/getter/notifier
implementation in AfterFXLib. These dependencies are now the next bounded
inspection targets, not proven owners of the selected factory. Generic
Factory-name matches in AfterFXLib are not factory-identification evidence.
Do not repeat the same broad AfterFXLib capture merely to retry its first window.

## Verification

Verified code/test source: `4d31a39cbb3a0acec9adc5fbdd6f6a139c0c5673`.

| Check | Result and scope |
|---|---|
| Local focused suite, warnings as errors | 25 PASS; two real macOS cases explicitly skipped on Linux |
| Python 3.9 grammar | PASS for the diagnostic and added/changed tests |
| Research CI | PASS, run 36747955033 |
| Research Python | 183 collected: 177 PASS, six platform-specific skips, not 183 passes |
| Node | PASS, 51 panel plus 11 snapshot cases |
| Full macOS CI | PASS, run 36747954818; all build/sign/package/smoke steps completed |
| macOS Python | PASS, all 183, no skipped tests |
| Real macOS LLDB regression | PASS: old options reproduce failure, corrected options decode arm64 mov/ret |
| Native research guards | PASS, 15 mock-loader cases; not a live AE test |
| Exact diagnostic vs CI source archive | PASS |
| Corrected capture of actual MEE/FLT files | NOT RUN, next requested collection |
| Fresh AE/project/runtime state | BLOCKED; an offline target does not establish a live host baseline |
| Late plugin registration repair | BLOCKED; historical scoped registration remains FAIL |

The real LLDB tests used Xcode 16.4, SDK 15.5, Apple clang 17 and
`lldb-1700.0.9.502` on the macOS arm64 CI runner. The small assembly fixture was
compiled and read, never executed. No Adobe image was loaded as code.

Both CI evidence archives were downloaded, rehashed and inspected:

- Research artifact `11113531418`, SHA-256
  `ed8894b91a4dddd66722ad1b39ac614f53cdaaf48c28c1374f8a9081444673df`.
- macOS artifact `11113123066`, SHA-256
  `f95abbb7ba69acf644b331b2237daebde43b43f6efeea12a26ce7f0504238bf0`.

The latter contains clean-source identity, both explicit REAL_LLDB result
markers, the 183-test result, guard output and the exact source snapshot.
[Research CI](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36747955033)
and [macOS CI](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36747954818)
apply to that code commit. Documentation follow-ups use [skip ci]. The full
five-finding static-security audit was not rerun and remains unresolved; green
CI is not a warning-free or release-approval claim.

## Next step and stop conditions

Run the exact standalone diagnostic with `--module MEE --module FLT`. It creates
separate fresh private Desktop directories and two ZIPs. It only reads the
allowlisted library files; it never sends an AE request, launches/attaches to
AE, installs a plugin, resets preferences or changes a project. Main-image
identity remains pinned; library hashes are first observations, checked again
on completion. At most 96 windows per library, up to 4096 bytes each, are
inspected with the existing time/output limits. Selection remains heuristic;
omissions and capped windows must be reviewed before making completeness claims.

Stop on any error or identity change; keep prior evidence. After receiving the
new data, trace recognition and module publication offline. Do not infer a
safe private registration operation from a symbol name or alter the final loader
bool without supporting evidence. RSMB startup-registered apply/render PASS,
historical RSMB late-registration FAIL and the scoped embedded FAIL remain
separate. Any risky live experiment still needs new authorization and a fresh
host/project/runtime identity baseline.
