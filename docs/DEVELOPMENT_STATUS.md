# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Stage **C of A–D**; registration, A/B/D and release gates remain open.
AGENTS.md and PRODUCTION_PLAN apply. Shared rules were rechecked unchanged:
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

Previous status is preserved at
[immutable checkpoint 1b6f072](https://github.com/ios3kov/AE-Hot-Loader/blob/1b6f072d38fc66e2b56cf0b98aeea9f5a82c6c8b/docs/DEVELOPMENT_STATUS.md).
Dated evidence is unchanged; earlier instructions do not renew permissions.

## Latest implementation — resident binding tested through three owned libraries

Added ResidentImageBinding.hpp and NativeDirectoryBinding.hpp. The resolver
selects named direct exports from an already resident exact-path arm64 library,
checks its file hash, UUID/header and code bytes, and wires the existing
DirectorySpecAdapter. It does not load libraries, use dlsym, execute resolvers
or invoke Adobe code. The fixed symbol profile is build data, not user/IPC input.

The macOS integration test now traverses the complete binding through three
separately compiled OWNED libraries, then creates a directory spec, verifies
its path, releases two strings and disposes the spec once. Resident-image-list
checks pass. The test libraries and allocator are ours, not Adobe's. A second
set checks missing images, bad hashes, wrong thread and incomplete profiles.

Initial code **1422392 FAILED macOS compilation** due to const-qualified address
conversion. It is corrected in **`31868ab019e58600bb0a79f260bcbe2fd69cad00`**,
with explicit typed conversion and portable coverage. No checks were disabled.
[Implementation, failure, source hashes, CI evidence and limits](RESIDENT_DIRECTORY_BINDING_2026-09-30.md).

## Checks for exact corrected code 31868ab

| Gate | Result and scope |
|---|---|
| Local unified Linux | PASS: 238 collected, 229 passed/nine macOS skips; Node 62 PASS |
| Supplied FILE export parsing | PASS, four actual exports; file analysis only |
| Local parser sanitizers and focused analysis | PASS/no diagnostics; not a complete product audit |
| Research CI 36776672299 | PASS, both unified Linux and macOS jobs |
| Downloaded macOS report | 21 stages PASS; Python 238/238, no skips; Node 62 and existing scoped guards 15 PASS |
| Real resident binding -> directory lifecycle | PASS with three owned providers on macOS arm64; Adobe calls=0 |
| Full macOS CI 36776672316 | PASS, all build/sign/package/smoke/archive-verification steps completed |
| Downloaded unified source/report verification | PASS, both outer hashes, all inner manifest entries and five new source hashes |
| Actual U/dvacore implementation/profile | BLOCKED: required original implementations/pins not available among inspected inputs |
| No-scan AEGP entrypoint and live supervisor | NOT CONNECTED / NOT RUN |
| AE resource registration/apply/render | NOT RUN; historical registration FAIL unchanged |
| Full static-security audit | NOT RUN again; five historical findings remain open |

Only two Python cases were added. Their internal checks and earlier native
cases are not counted again as extra Python tests. The local unified runner
still does not build product packages; full macOS packaging CI is separate.
No product ZIP was handed over or installed. Green CI does not clear known or
unreviewed warnings. Documentation follows with [skip ci]; CI belongs to 31868ab.

## Actual remaining blocker and next gate

The binding requires reviewed U.dylib/dvacore producer/destructor behavior and
actual binary pins before it can target Adobe. Exact symbol names from FILE's
imports alone do not establish their native contracts. The linked record contains
one tested file-copy request for BOTH original libraries; no SDK, FILE, PLUG or
FLT recollection and no in-host scan are requested.

Image snapshots are point-in-time observations, not a dyld lock/lifetime lease.
Concurrent remove/readd can escape comparisons. Resolve that lifetime boundary
before any real call, then wire the no-scan operation to a separate identified
one-shot research AEGP and external supervisor with fresh host/project/root
checks. Hashes do not prove ABI compatibility or grant consent. No live profile,
authorized probe artifact or automatic request path has been created.

A later resource pass still needs review of PLUG's end-of-pass callbacks and
retained state. Do not replay startup/RequiredPreSearch, enumerate global roots,
replace callbacks, bypass the cache predicate, force notification, fabricate host
objects, clear caches, change the old bool or unload code. The previous installation
and one-restart permissions remain consumed. All new risky host actions need
separate explicit authorization. Existing scoped commands still run the old loader.

## Preserved actual host results and scope

| Gate | Preserved result |
|---|---|
| Scoped embedded late registration | FAIL: 45de0c9 / scoped-0b8c8f122e80 / fixture88019a1a01a7; 785 unchanged identities |
| RSMB startup-registered apply/render | PASS: historical identified one-frame smoke |
| RSMB late registration | FAIL, separate from startup smoke |
| Dynamic fixture application | PASS: historical add/remove; render NOT RUN |
| Flat-resource failure | FAIL: historical crash evidence retained |
| Current AE/project/resident identity | NOT OBSERVED; CI and file analysis are not a Mac baseline |

The [SDK audit](SDK25_6_REGISTRATION_REVIEW_2026-09-30.md) did not establish a
supported public late-registration procedure. PICA availability/ordinary-effect
publication remain unverified, not disproved. SDK and proprietary binaries stay
private and out of Git. Reference installed product remains historical
04fea706/native-36483421984-1 unless fresh evidence establishes otherwise.
No product loader, installed Agent/shell/panel, third-party plugin, project,
preferences or main changed. No merge, installation, restart or release occurred.
