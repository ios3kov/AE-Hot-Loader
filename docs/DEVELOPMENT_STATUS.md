# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Current stage: **C of A–D**, with remaining gates in A/B/D. No completion
percentage or release approval is assigned. Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md).
Shared DEVELOPMENT_RULES and AGENTS.md remain applicable.

The preceding status is preserved at
[immutable checkpoint 687ff51](https://github.com/ios3kov/AE-Hot-Loader/blob/687ff5192f5740fe6384e02fc3c7966a0b86a03a/docs/DEVELOPMENT_STATUS.md).
Dated evidence is not rewritten. Historical wording describes its own checkpoint,
not current permissions, runtime identity or an independently retested artifact.

## Latest result — offline collector failure corrected and checked with real LLDB

The user supplied the failed AfterFXLib collection. LLDB created an offline
target but rejected the first disassembly command: the collector combined
explicit start/end addresses with the incompatible --force option. The previous
mock test expected that invalid string and did not exercise the real parser.
This is a diagnostic defect, not a new AE crash or registration result.

Code/test checkpoint: `4d31a39cbb3a0acec9adc5fbdd6f6a139c0c5673`.
The collector removes --force, retains bounded address windows, saves input
identity before the first tool, preserves structured failure evidence, records
LLDB version, and supports literal allowlisted module choices MEE and FLT.
Default AfterFXLib behavior is retained; unknown/duplicate choices and failures
stop collection without retry. No native product source or private ABI changed.

Real macOS LLDB tests now reproduce the old option failure and verify the
corrected command against an owned arm64 Mach-O. The fixture is compiled/read,
never executed. Full macOS CI and research CI both passed for this exact source.
[Failure evidence, changes, exact hashes, tests and next gate](FACTORY_COLLECTOR_LLDB_FIX_2026-09-30.md).

Collector Git blob: `49780e919f5e0128479cb35f26f578d7e71dce03`.
SHA-256: `04c94b6169ef0b40035c135d2cc8ac3da611ee72731b12a75add9c013b94fc17`.
The standalone `AEHL-collect-factory-v2.py` matches the source snapshot downloaded
from the successful macOS CI run byte-for-byte. It is a file-only diagnostic,
not an installable AE product or a new release candidate.

## Research narrowed using the already supplied partial data

AfterFXLib's dependency list names MEE.dylib and FLT.dylib; its symbol table
attributes undefined imports to those modules. They are the next concrete
inspection targets, not yet proven owners of the selected plugin factory.
The partial archive contains no instruction body or durable AfterFXLib image
hash record. Do not invent either. Generic Factory-name matches are not proof
of a plugin-factory implementation. The old AfterFXLib scan need not be repeated.

The earlier [PluginSupport review](REGISTRATION_DISPATCH_STATIC_2026-09-30.md)
showed candidate-count return semantics, restricted factory selection by the
final bool, and recognition/returned-reference handoff within AddPlugin.
The [verified original logs](REGISTRATION_GAP_SAVED_LOGS_2026-09-30.md) show an
empty string output vector and no new video modules. These observations do not
justify changing the bool or forcing notification. PiPL acceptance and the
missing module-publication step remain unresolved.

## Verification for code 4d31a39

| Check | Result and scope |
|---|---|
| Local focused tests, warnings as errors | 25 PASS; two real macOS cases skipped on Linux |
| Research CI | PASS, run 36747955033 |
| Research Python | 183 collected: 177 PASS, six platform-specific skips |
| Node | PASS, 51 panel plus 11 snapshot tests |
| Full macOS CI | PASS, run 36747954818, all build/sign/package/smoke steps complete |
| macOS Python | PASS, 183/183, no skipped tests |
| Real macOS LLDB option regression | PASS, both legacy-failure and corrected-disassembly cases |
| Native scoped guards | PASS, 15 mock-loader cases, not AE |
| Exact diagnostic vs downloaded CI source | PASS |
| Actual corrected MEE/FLT collection | NOT RUN, next requested file-only collection |
| Full static-security audit | NOT RUN again; five historical findings remain unresolved |

The real debugger tests used Xcode 16.4 and lldb-1700.0.9.502. Both research and
macOS evidence archives were downloaded and independently hashed. The detailed
record contains the artifact IDs, hashes and limitations. Green CI does not
clear unreviewed warnings or establish runtime AE compatibility. Documentation
follow-ups use [skip ci]; CI remains tied to the exact code commit above.

## Last real host results — retained separately

| Gate | Result |
|---|---|
| Scoped embedded late registration | FAIL: source 45de0c9, Build ID scoped-0b8c8f122e80, fixture 88019a1a01a7; 785 unchanged effect identities, target absent |
| RSMB startup-registered apply/render smoke | PASS: previously identified one-frame test, not broad compatibility certification |
| RSMB late registration | FAIL: historical result, not repaired by the startup smoke |
| Dynamic fixture application | PASS: earlier exact-match add/remove; render NOT RUN |
| Earlier flat-resource failure | FAIL: historical crash evidence remains, not declared fixed |
| Fresh AE/project/runtime identity | BLOCKED: offline file inspection is not a fresh live-host snapshot |

See [scoped host test](SCOPED_USER_HOST_2026-09-29.md),
[RSMB apply/render](RSMB_APPLY_RENDER_PASS_2026-09-29.md),
[Dynamic application](REGISTRATION_APPLY_PASS_2026-09-29.md) and
[flat-resource crash correlation](RESOURCE_PAIR_CRASH_CORRELATION_2026-09-29.md).
The earlier PID 78417 observation is not a fresh blank/clean/idle baseline.
Local Mac source was last reported as ce5d80d; no local pull/update is claimed.

Reference product remains source `04fea7060c7ef7ebc4a315b5c39364850287e294`,
Build ID `native-36483421984-1`.
[Reference identity and checks](CI_CHECKPOINT_04fea70.md).
No installed Agent, shell, panel or third-party effect was changed.

## Next safe gate

Run only the exact corrected diagnostic with `--module MEE --module FLT`.
It does not need AE open and produces two new private Desktop archives. It
reads only allowlisted files, never launches/attaches/scripts/scans AE, and
preserves old evidence. Review omitted/capped windows before claiming complete
coverage. Stop on errors or changed identities; do not regenerate the failed
in-host scan. After receipt, locate the concrete factory and trace its PiPL
acceptance and video-module publication using the saved offline data.

Any risky live operation requires a falsifiable hypothesis, bounded evidence,
fresh host/project/loaded identity and separate authorization. The installation
and one-restart permission are consumed. No speculative private dispatch,
teardown, unload, preference reset or unchanged scan is allowed.

Remaining gates include scope cleanup, controlled RSMB cold-start causality,
a demonstrated safe late-registration operation, separate apply/render, real
ScriptUI roundtrip, IPC ownership/reopen/timeout/repeat checks, compatibility
and the final clean-candidate gate. No main change, merge or release occurred.
