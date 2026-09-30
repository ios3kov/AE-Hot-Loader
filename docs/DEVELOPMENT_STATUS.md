# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Stage **C of A–D**; core registration, A/B/D and release gates remain open.
AGENTS.md and PRODUCTION_PLAN apply. Shared DEVELOPMENT_RULES rechecked unchanged:
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

Previous upstream status is preserved at
[61ea087](https://github.com/ios3kov/AE-Hot-Loader/blob/61ea0871cc6e55d9f2669e9d5b4989a0e83f9a15/docs/DEVELOPMENT_STATUS.md).
Dated evidence and the previously delivered local patch remain historical;
their old next steps and permission statements do not authorize a new host run.

## Latest result — actual SDK audit, no public late-registration fix established

The supplied SDK 25.6_61 archive was inspected as source: 160 headers and
109 additional C/C++/Rez files, 269 files total. Fourteen relevant source ranges
were checked against their original bytes. This was a bounded header/sample
audit, not compilation of the SDK or execution of its samples.

The SDK separates several tempting but different operations:

- PF_REGISTER_EFFECT/EXT2 invoke the callback received by
  PluginDataEntryFunction2 with the host-supplied opaque plugin-data pointer.
  They do not supply an independent new-folder scan or arbitrary replay context.
- AEGP_RegisterWithAEGP returns an AEGP ID; AEGP_ApplyEffect requires an already
  installed-effect key. Neither declaration establishes absent-binary discovery.
- PICA really has AddPlugin/AcquirePlugin, but these operate on PICA objects and
  adapters. Their availability to our AE 25.6 AEGP and their connection to the
  ordinary-effect/FLT registry remain NOT VERIFIED, not disproved.
- SPStartupPlugins is host lifecycle; it is not a documented safe single-root
  late pass. Acquiring a suite may itself load code and is not automatically
  a passive no-new-module check.
- FILE_Spec appears once as a forward declaration for an opaque hook handle.
  The searched corpus contains no FILE_New/Dispose/path, PLUG_Search or dvacore
  implementation/contract. Public file-spec types cannot substitute for it.

A supported public ordinary-effect late-registration procedure is therefore
NOT ESTABLISHED by this review. This is not proof that such a path is impossible.
SDK findings do not change the historical FAIL or complete the private adapter.

[Exact SDK input hashes, file/line evidence, limits and implications](SDK25_6_REGISTRATION_REVIEW_2026-09-30.md).
The two uploaded archive representations decode to identical tar bytes. SDK,
Adobe binaries and extraction utilities were not executed or committed to Git.
Redistribution-license review is not declared complete.

## Pending adapter is now on the research branch

The previously delivered local patch `1c0d7e36e81b22b959b43d212b5e2bdb44df97ca`
was recovered without changing its four source/test files or dated document.
The archive manifest, source hashes and entire resulting Git tree were checked.
Writes are available now; no permission setting was changed or bypassed.

New upstream code commit: **`ab5c1cb341e8432a226d8f58d2210c4fe1bbda83`**.
It adds DirectorySpecAdapter.hpp, SelfMemoryRead.hpp and their owned tests on
top of actual 61ea087. Its tree is `83b16579aab213e42b74de870286590d25128cc2`.
The old local commit is not claimed to have become the upstream commit.
[Original adapter implementation record](DIRECTORY_SPEC_ADAPTER_2026-09-30.md)
is retained unchanged; its write-unavailable/NOT RUN statements describe that
older iteration, superseded by the checks below.

The adapter performs create/path-roundtrip/single-release behind an unbound
function table. Tests supply owned producers, not Adobe functions. There is
still no reviewed native symbol resolver, actual FILE binding, no-scan AEGP
artifact or connected live supervisor. Existing scan commands remain unchanged.

## Checks for exact code ab5c1cb

| Check | Result and scope |
|---|---|
| Local unified Linux run | PASS: 236 Python collected, 228 passed/eight platform skips; Node 62/62 |
| Local owned adapter | 27 cases PASS at -O0 and -O2; ASan/UBSan with leak detection PASS |
| Research CI 36772108084 | PASS, both unified Linux and macOS jobs |
| Downloaded macOS unified evidence | Python 236/236 PASS, no skips; Node 62/62 and 15 existing scoped guards PASS |
| Actual macOS owned adapter transport | 27 cases at -O0/-O2 with the arm64 thunk and self-reader; invalid-pointer/bounds checks PASS |
| Downloaded Linux unified evidence | Python 228 PASS/eight skips, 236 collected; Node 62/62 PASS |
| Report/source verification | Both outer hashes, all inner manifest entries and all five recovered file hashes verified |
| Full product macOS CI 36772107919 | PASS: all build/sign/package/smoke/archive-verification steps completed; not live AE |
| SDK header/sample compilation in this audit | NOT RUN; source-reading scope only |
| Native Adobe binding / live no-scan probe | NOT IMPLEMENTED / NOT RUN |
| Full static-security audit | NOT RUN again; five historical findings remain open |

The SDK review did not create new test-count padding. The two adapter Python
cases were already in the local patch; the 27 native cases are nested, not
additional Python tests. The unified local runner still does not build the
product package; its separate full macOS CI was checked independently.

Research artifacts 11124506773 (macOS) and 11124102488 (Linux) were downloaded
and independently hashed. Exact outer/inner hashes are in the SDK review.
The full product workflow's step result was checked; its newly built package
was not installed or handed over. Green CI is not an AE registration PASS and
does not clear unreviewed annotations or historical audit findings.
Documentation follow-ups use [skip ci]; CI remains attached to code ab5c1cb.

## Next engineering boundary

Use the SDK installed-effect APIs as acceptance contracts, not as a loader.
Continue the verified U/dvacore producer/destructor and native FILE symbol/
ownership binding, with the separate no-scan probe and loaded-function provenance.
The private resource pass still requires end-of-pass callback/retained-state
review. A PICA alternative stays open only with evidence for actual provider
availability and ordinary-effect adapter/publication, not from names alone.

No new user-side data collection or test is requested by this iteration. Any
private host call, suite probe that may load code, installation, restart or
attachment requires separately specified approval and a fresh host/project/
loaded-image baseline. Do not reuse the consumed fixture/claim, replay startup,
change callbacks, reset caches, fabricate objects, unload code or repeat the
unchanged scan. No SDK-based shortcut has been wired into the product.

## Preserved real-host results

| Gate | Preserved result |
|---|---|
| Scoped embedded late registration | FAIL: source45de0c9, scoped-0b8c8f122e80, fixture88019a1a01a7; 785 unchanged effect identities |
| RSMB startup-registered apply/render | PASS: historical identified one-frame smoke |
| RSMB late registration | FAIL, separate from the startup smoke |
| Dynamic fixture application | PASS: historical exact-match add/remove; render NOT RUN |
| Flat-resource failure | FAIL: historical crash evidence retained |
| Current AE/project/resident identity | NOT OBSERVED; source/CI evidence is not a current Mac baseline |

No product loader, installed Agent/shell/panel, third-party plugins, user project
or preferences were changed. Mac checkout ce5d80d and old PID78417 remain
historical observations; no local pull or fresh runtime identity is claimed.
No main change, merge, installation, restart, native unload or release occurred.
