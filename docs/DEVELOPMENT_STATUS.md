# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Current stage: **C of A–D**, with open gates in A/B/D. No completion percentage
or release approval. Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md), AGENTS.md
and shared DEVELOPMENT_RULES, reread at unchanged blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

Previous status is preserved at
[immutable checkpoint 1e69244](https://github.com/ios3kov/AE-Hot-Loader/blob/1e69244c760afd8848787c6c86a364ae9a9faa55/docs/DEVELOPMENT_STATUS.md).
Dated evidence is not rewritten. Earlier instructions do not renew risky-action
permissions or supply a current runtime baseline.

## Current continuation — real disk journal, native binding still blocked

Added `ResourcePassJournal.hpp`: concrete disk-backed claim, snapshot, call-marker
and final-result methods for the existing resource-pass backend. `RunJournaled`
requires final evidence persistence before returning PASS. No FILE/PLUG symbols,
AE entrypoint or installable research bridge have been connected.

Exact code/test commit: **`5beb51c1dbd70d1f0c6115578387f27dfab78776`**.
The new 32 cases use actual private files and child processes, including an
eight-process race with one winner, exits after claim/marker, a real partial
write failure and refusal of symlinks, hardlinks, changed records and directory
replacement. The host observations and spec/search callbacks remain synthetic.
No claim of AE registration, power-loss safety or hostile-owner protection.

Research CI `36761528713` and full macOS CI `36761528656`: **PASS**.
macOS Python: **210/210**, including the 32 new journal cases and 63 original
policy cases as nested tests. Research Linux: **204 PASS / six skips**, 210
collected. Node: **62/62**. Existing scoped native guards: **15 PASS**.
Local clang/GCC strict builds, ASan/UBSan and focused clang analysis also passed.
Both CI evidence archive hashes and all three source files were verified.

[Implementation, real checks, scope, hashes and next FILE request](RESOURCE_PASS_JOURNAL_2026-09-30.md).
The new storage component intentionally does not alter scoped::Save: it adds
pinned directory descriptors, record revalidation and directory fsync only for
the future resource pass. Existing scoped-discovery commands remain unchanged.

Native integration is still **BLOCKED** on the unavailable FILE.dylib
implementation and unverified FILE_New/string/ownership/roundtrip contract.
The supplied aelib/PLUG/FLT contain imports, not that implementation. The linked
record includes a minimal copy/hash/archive request for FILE.dylib, tested on an
owned dummy file. It does not contact AE, scan, install or restart anything.

No old authorization is reused. Current AE/project/loaded identity is **NOT
OBSERVED**. Scoped registration FAIL, RSMB startup-registered apply/render PASS
and historical late-registration FAIL are unchanged and separate. Five known
static-audit findings remain open. Product source, main and installed components
are unchanged. No release. CI applies to the exact code commit, not the later
documentation-only head. The earlier record below retains its original scope.

## Earlier implementation — resource-pass transaction policy, not a runnable AE test

Added `experiments/ordinary_discovery/ResourcePassGate.hpp`, 63 synthetic native
cases in `tests/resource_pass_gate.cpp`, and their Python/CI launcher.
Exact code/test commit: **`1d90cb6ced210f340a72f05488a34f78129e2ef6`**.

The C++ policy validates the exact approved plan, owned-root identity, fixture
identity, host version/architecture, main thread, PID/start, loaded-image pins,
blank clean idle project and complete registry. It requires an exclusive claim
before file-spec creation, a path roundtrip, a second pre-call baseline and a
persisted call marker. At most one single-root operation is permitted. Release,
postflight, deadline and exact one-effect delta are checked, including error
paths. Old permission scopes and the historical consumed fixture are rejected.

**The Backend is abstract and unbound; only the synthetic test Model implements
it. There is no new native AE bridge, FILE_New/PLUG_Search binding, AEGP artifact,
installer or runnable user experiment.** Approval fields are supervisor inputs,
not verified user consent. Model claims are in-memory; filesystem durability,
real fresh observations and native ownership are not proven by these cases.
Existing scoped::Save/VerifyScope are the intended integration points and were
not changed. Existing scoped-discovery commands still use their old loader.

[Design, ownership observations, source hashes, tests and integration requirements](SCOPED_RESOURCE_GATE_DESIGN_2026-09-30.md).
The 15-second policy budget only detects expiration between callbacks/after
return; it cannot interrupt a stuck native call. An external bounded supervisor
remains required. Timeout is not permission to repeat or kill the host.

## FILE_Spec boundary refined with existing binaries

The supplied aelib was rehashed unchanged. Its imported FILE_New and FILE_Dispose
resolve through library ordinal 30 to FILE.dylib. The inspected helper creates
a specification from a host string and retains the returned pointer; replacement
and FILE_ScSpec destruction call FILE_Dispose with that pointer. Four raw BL
encodings agree with the identified callsites.

This is static caller/ownership evidence, not a complete native ABI contract.
FILE_New expects a host C++ string with a dvacore allocator. FILE.dylib's
implementation and its exact string/error/retention behavior have not been
verified here. The new policy does not fabricate FILE_Spec or reinterpret a
host string. Native integration remains BLOCKED pending those contracts.

## Exact checks and CI

| Check | Result and scope |
|---|---|
| New C++ model cases | 63/63 PASS on Linux and in macOS CI; no Adobe code |
| Linux AddressSanitizer/UndefinedBehaviorSanitizer | PASS on the 63 model cases with leak detection; not AE memory proof |
| Local Python with warnings as errors | 209 collected: 203 PASS, six macOS-only skips |
| Research CI 36759252657 | PASS; 203 Python PASS/six skips, all 63 nested C++ cases, 62 Node PASS |
| Full macOS CI 36759252333 | PASS; build/sign/package/smoke steps complete; no live AE |
| macOS Python | 209/209 PASS, no skips; new C++ cases included as one Python test |
| Existing native scoped guards | 15 PASS in macOS CI, mock loader |
| Downloaded CI/source verification | PASS; both evidence ZIP hashes and all three new source files checked |
| Live resource backend and fresh fixture/bridge build | NOT IMPLEMENTED / NOT RUN; experiment remains BLOCKED |
| Actual AE resource registration/apply/render | NOT RUN |
| Full static-security audit | NOT RUN again; five historical findings remain unresolved |

The design record was written while the macOS run was in progress. Its final
completion is now independently checked above. macOS evidence artifact
`11118212476` was downloaded; SHA-256:
`4a083827fd26453c7b703aa6d2e131d8d4f39b95a7c70d49e246999dcd0fe38e`.
Its source snapshot matches all three local tested files byte-for-byte. The
build record reports clean source 1d90cb6, arm64, Xcode 16.4 and Apple clang 17.
The research artifact `11118196977` also has a verified downloaded hash, recorded
in the design document. Green CI does not clear unreviewed annotations/warnings.
No CI product package was installed or handed over. Docs follow-ups use [skip ci].

## Retained research and runtime results

The [aelib resource-pass analysis](AELIB_RESOURCE_PASS_2026-09-30.md) connects
ordinary startup enumeration, the hardcoded-cache predicate and setter. Combined
with the separate [MEE resource-retention branch](MEE_RESOURCE_ROUTE_2026-09-30.md)
and [PLUG/FLT publication path](PLUG_FLT_RESOURCE_REGISTRATION_2026-09-30.md), it
supports the missing-resource-pass hypothesis. The original live receiver,
predicate result and root cause are not proven; the loader is not fixed.

| Real host gate | Preserved result |
|---|---|
| Scoped embedded late registration | FAIL: source 45de0c9, scoped-0b8c8f122e80, fixture 88019a1a01a7; 785 unchanged identities, target absent |
| RSMB startup-registered apply/render | PASS, earlier identified one-frame smoke |
| RSMB late registration | FAIL, retained separately |
| Dynamic fixture application | PASS, earlier exact-match add/remove; render NOT RUN |
| Flat-resource failure | FAIL, earlier crash evidence remains |
| Current AE/project/resident identity | NOT OBSERVED; no live Mac access in this iteration |

[Scoped host](SCOPED_USER_HOST_2026-09-29.md),
[RSMB smoke](RSMB_APPLY_RENDER_PASS_2026-09-29.md),
[Dynamic application](REGISTRATION_APPLY_PASS_2026-09-29.md),
[flat-resource crash](RESOURCE_PAIR_CRASH_CORRELATION_2026-09-29.md).
The earlier PID 78417 is not a current baseline. Mac source was last reported
as ce5d80d; no local pull/update is claimed. Reference installed product remains
04fea706 / native-36483421984-1 unless fresh runtime evidence establishes otherwise.

## Earlier development boundary — current continuation takes precedence

Complete the native FILE/PLUG adapter contract and a separate create/roundtrip/
release check, then wire the policy into a separately identified scoped AEGP
and supervisor with actual durable evidence and loaded identities. Freeze one
fresh embedded fixture/root and verify SDK build/signature/inert entry before
requesting any new risky host test. Do not reuse the consumed fixture or old
scoped-discovery request. No further user command is requested for this step.

Keep the installed path predicate and FLT callbacks. Do not use global-folder
helpers, Birth/InitIterator/RequiredPreSearch, callback replacement, cache reset,
forced notification, speculative bool changes or an unchanged scan. No native
unload. New private calls/install/restart require separate authorization and a
fresh identified project/host baseline. The previous permissions are consumed.

The product loader, existing Agent/shell/panel, user settings/projects and
third-party plugins are unchanged. No installation, restart, main change, merge
or release occurred. Proprietary inputs stay private. Stages A/B/D, real-AE
registration, separate apply/render and the release gate remain open.
