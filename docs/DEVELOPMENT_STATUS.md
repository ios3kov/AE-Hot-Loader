# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Stage **C of A–D**, with open A/B/D and release gates. No completion percentage.
Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md) and AGENTS.md. Shared rules were
rechecked unchanged at blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

Previous state is preserved at
[immutable checkpoint ad1ec8d](https://github.com/ios3kov/AE-Hot-Loader/blob/ad1ec8d2f49fc262260a6986d0566ac763f5c7d7/docs/DEVELOPMENT_STATUS.md).
Dated evidence is unchanged. Old instructions do not renew permissions.

## Latest result — FILE contract inspected; indirect-result primitive verified

The received FILE.dylib was independently hashed and matched both uploaded
before/after statements. SHA-256:
`df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864`.
Its code was read as data, never loaded or executed. The original inputs remain
unchanged. Twenty-five structural assertions passed; these are not runtime tests.

The constructor copies its input host string and owns File/Dir members.
FILE_InqUnicodePath returns a host object indirectly through x8, not a borrowed
char pointer. FILE_Dispose can close resources and unload an associated module;
it has no leading null guard and is not an unconditional free. Consequently the
first host probe must create/roundtrip/release only its own ordinary directory
specification, without resource or executable loading. Borrowed plugin objects
must not be disposed; a release error is not permission to retry.

A recheck found that PLUG_Search also invokes sack cleanup callbacks after its
root loop. One supplied root does not by itself restrict all end-of-pass effects.
The active cleanup list and post-startup safety still require review; do not
remove or bypass callbacks to make the experiment appear scoped.

Implemented `HostIndirectResult_arm64.S`: four register-transfer/tail-call
instructions, no Adobe addresses, resolver, automatic execution or host binding.
It is linked only to an owned C++ test producer. The new tests check exact
assembled words and actual nontrivial return, destruction, canaries and exception
propagation on macOS arm64. This is NOT a complete FILE adapter or AE probe.

Exact code/test commit: **`847b7ded4be07995b42facfba38bac0f9d52f060`**.
[FILE findings, source/input hashes, checks and limits](FILE_OBJECT_CONTRACT_2026-09-30.md).

## Checks for exact code 847b7de

| Check | Result and scope |
|---|---|
| Local cross-assembly and strict C++ syntax | PASS; no Adobe code |
| Local Python | 212 collected: 205 PASS, seven platform-specific skips |
| Local Node | 62/62 PASS; panel/snapshot mocks |
| Research CI 36763733179 | PASS; 205 Python PASS/seven skips, 62 Node PASS |
| Full macOS CI 36763733162 | PASS; build/sign/package/smoke steps complete |
| macOS Python | 212/212 PASS, no skips |
| Real owned arm64 ABI test | Six cases PASS at both -O0 and -O2; includes exception/destructor checks |
| Existing resource policy / disk journal | 63 / 32 cases retained as nested Python tests |
| Existing native scoped guards | 15 PASS; mock loader |
| Downloaded evidence/source | Both evidence ZIP hashes and all three new files verified |
| Actual FILE/PLUG binding and no-scan AE probe | NOT IMPLEMENTED / NOT RUN |
| Full static-security audit | NOT RUN again; five historical findings remain open |

macOS evidence identifies clean source, Xcode 16.4 and Apple clang 17.0.0.
The owned producer is not Adobe's string or allocator. Green CI does not certify
AE compatibility or clear unreviewed warnings. No CI product package is handed
over. Documentation uses [skip ci]; verification belongs to the code commit.

## Next bounded implementation

Connect a verified host string producer/destructor, FILE_New, path return and
FILE_Dispose only after exact symbol/module provenance and ownership review.
The assembly primitive does not validate targets; never accept call addresses
from requests or users, or fabricate a host string/FILE_Spec layout.

Prepare a separate no-scan create/roundtrip/release probe before a registration
attempt. Require a fresh owned root, one-shot journal, loaded-image identity,
exact path roundtrip, successful single release, unchanged PID/project/registry
and no new module loading or unloading. The real backend and external supervisor
remain unbound. Existing scoped-discovery commands still run the old loader.
The later PLUG pass additionally needs review of cleanup callbacks and retained
state. Do not use global-folder or initialization helpers, alter the path
predicate, clear caches, force a notifier or repeat the unchanged scan.

No new user command or collection is requested now. Any private host call,
installation, restart or debugger attachment needs separate authorization and
a fresh identified host/project baseline. Earlier permissions are consumed.

## Preserved results and boundaries

| Actual host gate | Historical result |
|---|---|
| Scoped embedded late registration | FAIL: source 45de0c9, build scoped-0b8c8f122e80, fixture 88019a1a01a7; 785 unchanged effects |
| RSMB startup-registered apply/render | PASS: previously identified one-frame smoke |
| RSMB late registration | FAIL, separate from startup smoke |
| Dynamic fixture application | PASS, earlier add/remove test; render NOT RUN |
| Flat-resource failure | FAIL, earlier crash evidence retained |
| Current AE/project/resident identity | NOT OBSERVED |

[Scoped host evidence](SCOPED_USER_HOST_2026-09-29.md),
[RSMB smoke](RSMB_APPLY_RENDER_PASS_2026-09-29.md),
[resource policy](SCOPED_RESOURCE_GATE_DESIGN_2026-09-30.md),
[disk journal](RESOURCE_PASS_JOURNAL_2026-09-30.md),
[startup resource route](AELIB_RESOURCE_PASS_2026-09-30.md).
The old PID 78417 and Mac source ce5d80d are historical observations, not a fresh
baseline. No local pull/update, installed-component identity or blank project
is asserted. No product loader, installed Agent/shell/panel, user project,
settings or third-party plugin changed. No main update, merge, install, restart
or release. Proprietary inputs remain private. The live registration fix,
separate apply/render, integration, compatibility and release gates remain open.
