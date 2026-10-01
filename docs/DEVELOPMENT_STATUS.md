# AE Hot Loader — current development status

Updated: 2026-10-01. Branch: `research/ordinary-plugin-discovery`.
Stage **C of A–D**; core registration, A/B/D and release gates remain open.
Current continuation handoff: [CHAT_HANDOFF_2026-10-01_STAGE_C_CURRENT.md](CHAT_HANDOFF_2026-10-01_STAGE_C_CURRENT.md).
AGENTS.md and PRODUCTION_PLAN apply. Current canonical rules:
AE-Development-Rules `b27f45467e0a9152fc82c1072438dfed07f0c36e`, starting with
AI_ENTRYPOINT.md. Older rule/permission/environment statements below belong
to their named checkpoints and do not supersede this continuation.
Previous status is preserved at
[immutable e96a1c8](https://github.com/ios3kov/AE-Hot-Loader/blob/e96a1c8f31b5aad70c11400b17c1f11e9bbe4154/docs/DEVELOPMENT_STATUS.md).
Dated evidence is unchanged; previous instructions do not renew permissions.

## Current Stage C1 — bounded cleanup snapshots prepared offline

Code/test head: **`6a758a811790e68846d9ecb9a78c0c16df069c9d`**.
CleanupSnapshot.hpp reads an injected exact-byte source within explicit regions,
following sack/list metadata and reading the MEE vector begin/end. It preserves
ordered callback target/context words, validates counts/strides/overflow and
compares two complete bounded captures. Any read failure/change stops without
retry. Limits: 256 callbacks, 8192 retained records, 12 reads / 16384-byte budget.
No callback, LIST getter, Adobe function or foreign process was invoked.

This is isolated observer preparation, not the live observer or C1 backend.
Matching captures do not prove atomicity/completeness, allocation ownership,
provider identity, valid pointer representation or future stability. No automatic
conversion supplies ResourcePassGate's observed/complete/digest fields. Actual
AE callback/vector state remains **NOT OBSERVED**. The existing empty-state
restriction remains necessary and must not be relaxed.

Focused regression: **PASS**, 44 nested synthetic cases and real owned-process
buffer inspection on macOS arm64. Address/undefined-behavior sanitizers: **PASS**.
Clean-source unified local regression: **PASS**, 271 Python without skips,
62 Node, 22 stages; source inventory unchanged. Current research CI
**36926349585 — PASS**; full macOS CI **36926349591 — PASS**.
These are offline/build results, not registration proof.

Current contract, evidence and remaining gate:
[C1_CLEANUP_SNAPSHOT_REVIEW_2026-10-01.md](C1_CLEANUP_SNAPSHOT_REVIEW_2026-10-01.md).
Prior [lifecycle review](C1_REPEAT_PREPARATION_REVIEW_2026-10-01.md) is preserved:
repeat preparation can return success and invoke existing general plugins again;
270-test / exact 52f4f80 CI results remain that checkpoint's evidence.

Next: reviewed root/provider identity, memory-range provenance and a host
lifetime/quiescence strategy before any complete observation claim. Critical
unknown behavior blocks native C1 integration; independent file-only preparation
remains allowed. C0 remains recorded live PASS; C1 registration/apply/render are
**NOT RUN**. Original checkout remains preserved at 182d058; development uses a
separate research-branch clone. No installable/live candidate is handed off.

## Second live no-scan result — PASS; Stage C0 closed

The second authorized no-scan request ran from source
**`182d058254203236414602acdd9901b8749d89cc`**, build
`noscan-8f9cb9fea71c`, run
`directory-probe-d097765fede949f5b9958b2897687df2`.

Report ZIP SHA-256:
`f767e891359a3e73dc41eefe4124fe63dc0cf4dde123c2d7efa7444cd35bc62a`.

The uploaded report was independently rehashed and every archived payload was
verified against `report-hashes.json`.

Result: **PASS**.

Exact native lifecycle evidence:

- invoked = 1;
- completed = 1;
- cleanup_ok = 1;
- strings created/released = 2/2;
- specs created/released = 1/1;
- retained provider references = 3.

Before/after host evidence is byte-identical: project revision 1, runtime image
count 1402, and complete registry count **785** all remained unchanged. No lazy
system image appeared in this run. `plugin_scan_requested=false`.

This closes the no-scan FILE ownership/binding gate: **Stage C0 = PASS**.

See [NO_SCAN_DIRECTORY_LIVE_PASS_2026-10-01.md](NO_SCAN_DIRECTORY_LIVE_PASS_2026-10-01.md).

Ordinary-effect late registration is still NOT fixed. The historical registration
FAIL remains unchanged. The next development gate is Stage C1: a single-root
resource-registration experiment, first prepared and reviewed offline. Any live
private PLUG/resource-registration call requires fresh authorization; the second
no-scan approval was consumed by this PASS.

## First live no-scan result — FAIL; evidence gap remediated offline

The first real no-scan request ran from source
**`161b180714a734baf71f8c8cb58440e73f8dcd23`**, build
`noscan-f0aa4a3bd54a`, run
`directory-probe-11f0a9c60dc44fcea98579536234fd34`.

Report ZIP SHA-256:
`727a65d7ba64be8371c40025a4fc2196785216cc77299941d0978a71eb0cff5a`.

Result: **FAIL at postflight**. The single request was published; call-started,
postflight and cleanup evidence were present. PID/process-start, project
revision and the full effect registry stayed unchanged at **785** effects.

The only before/after image delta was one new Apple system framework,
`/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/SafariPlatformSupport`.
No image was removed and no Adobe/user/plug-in image was added.

The old gate required byte-identical image lists, so the system lazy load caused
the FAIL. The old journal also did not persist the complete native lifecycle
counts before postflight, so this report cannot prove the FILE
create/roundtrip/single-release acceptance even though cleanup was reported
successful. No retry was performed.

Offline remediation is complete at code head
**`dadd884b4758a351fbc725969ed49d2f9a912781`**:

- `native.txt` is durably written immediately after the private call;
- PASS requires exact string/spec/release/retention counts;
- existing runtime images must remain exact;
- only newly loaded `/System/Library/` images may be tolerated;
- new Adobe/user/plug-in images still fail;
- the external supervisor independently checks the same contract.

Exact-head research CI **`36857286317`** — PASS.  
Exact-head full macOS CI **`36857286194`** — PASS.

See [NO_SCAN_DIRECTORY_LIVE_FAIL_2026-10-01.md](NO_SCAN_DIRECTORY_LIVE_FAIL_2026-10-01.md).

A second live request is **NOT RUN** and needs fresh authorization because the
first one-shot approval was consumed.

## Live-ready one-shot launcher checkpoint

Current live-launcher code/test head is **`3852192406da5af539b9100114393584642e9197`**.

Added `RUN_LIVE_NO_SCAN_GATE.command`, a fail-closed one-shot launcher for the
authorized Mac. It:

- requires the research branch and a clean checkout;
- fast-forwards only, never resets or overwrites local work;
- refuses to touch an already-running After Effects session;
- requires the reviewed AE 25.6 application path;
- locates an already-extracted SDK or accepts `AEHL_SDK`;
- builds the unique inert no-scan AEGP with the reviewed builder;
- installs only that newly named helper into the user MediaCore root, never
  replacing another plug-in;
- verifies installed bytes/signature before AE launch;
- launches After Effects exactly once with the one-shot activation token;
- waits for exact helper-ready evidence;
- invokes the existing supervisor exactly once with the approved private FILE
  and provider-retention flags;
- contains no `PLUG_Search`, old `ML::LoadPlugins` path or ordinary-effect scan.

Dedicated launcher source-policy tests were added. The unified macOS research
runner also syntax-checks all top-level `.command` files.

Exact-head verification for `3852192`:

- research CI **`36855482114`** — PASS;
- full macOS CI **`36855482175`** — PASS.

This makes the one-shot launcher **ready for the authorized Mac gate**, not a
live AE PASS. No private FILE call, provider-reference retention or new helper
installation was executed by CI.

The user's explicit authorization in this chat covers this one no-scan gate:
the unique helper installation / one AE launch if needed, the private FILE call,
and retaining the three already-loaded FILE/U/dvacore references until process
exit. It does not authorize a plug-in scan, ordinary-effect registration,
additional retries or later Stage C1 operations.

## Current Stage C checkpoint — identity + final ZIP evidence hardened; CI green

Current Stage C code/test head is **`c1e20e4ab4d4a4f6654f67df7dbb224f0790b5be`**.
The external no-scan supervisor now reads the process start tuple through macOS
`proc_pidinfo(PROC_PIDTBSDINFO)`, matching the exact `sec.usec` identity written
by the AEGP. Preparation refuses a loaded-helper start identity that differs from
the supervisor's host identity **before request publication**. The later native
journal must still match that same AEGP start identity. A real macOS self-process
regression covers the libproc representation; Linux records that case as an
explicit platform skip.

The no-scan report packager now also verifies the final ZIP inventory and every
archived payload against `report-hashes.json`, then prints the final report
SHA-256. The request/token is still excluded from the report ZIP.

Exact-head research CI **`36854509313`** completed successfully on Linux and
macOS. Exact-head full macOS CI **`36854509275`** also completed successfully,
including the Python/Node/no-scan regressions, existing product build/sign/package
and smoke gates. These are still offline/build evidence only; no private Adobe
function was executed by CI and no live AE registration result changed.

CI coverage was also corrected at **`6009c18552c5d6be0e64b7af7e0f315fac840c0e`**:
changes under `experiments/**` now trigger the full macOS workflow instead of
only the research workflow.

The five previously recorded static-scanner candidates were revisited. Four real
workflow-policy issues in `dual-pipl.yml` were fixed/classified through
`54eb513dc3526f75f1446e3a80223fa3a06eea7c` and
`da5d3a8e5a69b9cb719997ddba835e1a56f5d896`; all current workflow `uses:`
references are SHA-pinned and every checkout disables credential persistence.
The fifth historical candidate remains the previously reviewed local-argparse
false positive. **Known five candidates are resolved/classified; a new full
static-security audit is still NOT RUN.** See
[STATIC_AUDIT_CLOSEOUT_2026-10-01.md](STATIC_AUDIT_CLOSEOUT_2026-10-01.md).

README and the current production plan now describe AE Hot Loader as a **tool**
with internal AEGP helpers and distinguish the no-scan safety helper from the
ordinary effect being researched.

Live AE remains **NOT RUN / NOT OBSERVED** for this checkpoint. The user's
`/Users/os3kov/Documents/AE-Hot-Loader/` checkout, current AE PID/project and
installed/loaded no-scan helper are still not accessible from this environment.
The real folder-object gate therefore remains pending.

Before that live gate, the exact no-scan AEGP still needs a dedicated SDK build,
sign/hash/inert verification and installed/loaded identity on the authorized Mac.
Because the AEGP must be present in AE, any new installation and AE launch/restart
also require fresh authorization if needed. Separately, publishing the one-shot
request requires explicit approval for the private FILE call and retaining the
three already-loaded FILE/U/dvacore references until process exit. The first live
run remains folder create → path roundtrip → single release only, with **no plug-in
scan or ordinary-effect registration**.

## Previous code checkpoint — ready/journal process identity binding; CI green

Current code head is **`a0d08f46c45c56b2695b82d2ff71d7e5da08a6c1`**. The existing
no-scan folder-object gate now writes the native process start identity into
`ready.txt`, and the external supervisor requires the later native journal to
contain that exact same start identity. PID equality alone can no longer satisfy
the cross-process evidence check. A negative owned-fixture test proves that a
mismatched start identity fails the run and still preserves the one ZIP report.

This is a hardening of the already connected no-scan gate, not a new Adobe call,
plug-in scan or registration path. The change adds no private API, no provider
load, no installation and no restart.

Exact-head research CI **`36842766751`** completed successfully. Exact-head full
macOS CI **`36842766786`** also completed successfully for the same code head.
The macOS product pipeline remained synthetic/build-only; its packaged panel
regression reported 51/51 Node tests. Live AE, private FILE execution, retained
Adobe provider references, dedicated user-Mac SDK candidate build and the real
folder lifecycle remain **NOT RUN / NOT OBSERVED** here.

## Previous code checkpoint — timeout contract hardened; CI green; live host still NOT RUN

Previous code head was **`0e63156cbbbd3b1ec1c37ca6d8701af1cd5ed7e9`**. Four commits after `763c6e7` hardened the one-shot supervisor deadline: the native directory call remains bounded at 15000 ms, the external supervisor must allow at least a 5000 ms margin, and shorter timeouts are rejected before request publication. The final test-only adjustment aligns the PASS fixture with that reviewed floor. No plug-in scan or registration call was added.

Exact-head CI is green: research run **`36835180596`** and full macOS run **`36835180654`** both completed successfully. These remain offline/build evidence only; dedicated SDK build on the user's Mac, local checkout identity, current AE/PID/project/module baseline, private FILE call, provider-reference retention and real folder lifecycle are still **NOT RUN / NOT OBSERVED** here. No installation, restart, live Adobe call, merge, release or `main` change was performed.

## Post-checkpoint result — no-scan bridge connected in source; live host still NOT RUN

The separate inert-by-default no-scan AEGP and external one-shot supervisor are now
connected in source. The implementation was introduced at `422abba40644216ae9076ed4f148172ae9fe72c0`;
macOS CI then exposed test-fixture paths traversing the platform `/tmp`/`/var`
symlinks. Production path guards were not weakened. The fixtures were canonicalized
at `bdbb98940f8daab64332ec517ef0052e5793775d`, and the current code was hardened at
**`763c6e7e2fa73ef58fa38353c9ac41b21f26b02c`** so a clean checkout can create the
build parent and `adapter-stopped.txt` is retained in the single failure ZIP.

The AEGP has no plug-in scan/registration call in this probe path. Without the exact
startup token, exact host/module identity and private owned directories it returns
inert. After a separately published exact one-shot request, the native operation is
limited to one newly owned directory object, exact path roundtrip and one release.
The supervisor publishes at most one request, never retries an uncertain native
outcome, and packages one sanitized report ZIP. These are source/offline properties;
they do not prove execution inside After Effects.

Research CI **`36833660016`** passed on Linux and macOS. Full macOS CI
**`36833660022`** passed for exact code `763c6e7`: Python 243 tests, no-scan gate
11 cases, owned directory 28/28, resource gate 63, resource journal 32 and existing
scoped guards 15; product build/sign/package/smoke/archive checks also completed.
The dedicated no-scan AEGP SDK build and any live AE call were **NOT RUN** by these
workflows. Green CI therefore remains offline evidence only.

The user's Mac checkout and current AE/PID/project/resident-module state are still
**NOT OBSERVED** in this chat; the previously reported local `ce5d80d` state has not
been confirmed or updated here. No installation, AE launch/restart, private Adobe
call, provider-reference retention in AE, project/preferences change, third-party
plug-in change, merge, release or `main` change was performed.

Fresh live authorization is still required for the private FILE call and retaining
three already-loaded provider references until process exit. Previous install/restart
permission remains consumed. The first live gate remains folder lifecycle only;
`PLUG_Search` and ordinary-effect registration are explicitly outside that run.

## Historical continuation checkpoint — 2026-10-01

This records the state saved at checkpoint `90c257c`; the post-checkpoint section
above is the current continuation state.

[CHAT_HANDOFF_2026-10-01.md](CHAT_HANDOFF_2026-10-01.md) is the restart point for
the next chat. It preserves the exact code/CI identity, historical AE outcomes,
consumed permissions, existing private-input inventory and remaining integration.
This save changes documentation only. Code remains `9ea7bcf57fffee2382c6890459dca89201345395`;
research CI `36824300893` and macOS CI `36824300983` were rechecked successful.
No new tests or live AE operations were run. The no-scan AEGP and live supervisor
are still not connected; registration remains unproven. Documentation uses [skip ci].
The user's Mac checkout and current AE state were not inspected or updated.

## Latest result — U/dvacore checked; provider retention tested on macOS

The supplied U/dvacore archive was independently hashed. Both binaries agree
with its matching before/after statements. Their actual producer/destructor and
storage bodies match the directory adapter's representation for this exact build.
The converter is ASCII-only, not UTF-8; non-ASCII probe paths remain blocked.
The destructor recycles host-allocated storage and has a terminate path, so not
every native failure is catchable. No Adobe binary was loaded or executed.

Added `AE256DirectoryProfile.hpp` with exact received FILE/U/dvacore digests,
and `ResidentDirectorySession.hpp` with a controlled already-loaded-reference
wrapper. Exact code commit: **`9ea7bcf57fffee2382c6890459dca89201345395`**.
It validates providers, retains up to three RTLD_NOLOAD references, then rebinds
under those references. Missing images are refused, never loaded as a fallback.
There is no dlsym, startup replay, plugin scan or automatic AE entrypoint.

The wrapper intentionally keeps acquired references until process exit, including
partial failure; it never unloads a provider. **This changes loader reference
counts and must be included in future explicit host-test approval.** Its boolean
is only a supervisor assertion, not verified consent or a durable claim. The
existing disk journal and fresh host/project guards still have to be connected.

The macOS test uses three OWNED libraries. After the wrapper retains them, the
test closes all original references and successfully runs the directory lifecycle
through the remaining references. Image-list, missing-image, bad-digest,
permission-assertion, environment-override and repeat-attempt checks passed.
This proves the tested owned-provider behavior, not execution of FILE/U/dvacore.

[Exact input identities, static findings, lifetime tradeoff, checks and limits](U_DVACORE_CONTRACT_2026-10-01.md).
U/dvacore implementation availability is no longer the current blocker.

## Checks for exact code 763c6e7

| Check | Result and scope |
|---|---|
| Research CI 36833660016 | PASS, Linux + macOS; unified offline result explicitly says full AE pipeline BLOCKED |
| Full product macOS CI 36833660022 | PASS; Python 243, no-scan gate 11, owned directory 28/28, resource gate 63, resource journal 32, scoped guards 15 |
| No-scan source integration | PRESENT: inert entry, one-shot journal/supervisor, one ZIP, no plug-in scan in this probe path |
| Dedicated no-scan AEGP SDK build | NOT RUN in the cited workflows |
| Real AE folder-object lifecycle | NOT RUN; private FILE/provider-retention authorization still required |
| Ordinary-effect late registration/apply-render | NOT RUN; historical registration FAIL unchanged |
| User Mac checkout / current AE state | NOT OBSERVED in this chat |
| Full static-security audit | NOT RUN again; five historical findings remain open |

Commit `422abba` initially failed macOS automation only because new security tests
used temporary paths whose parents are symlinks on macOS. The code now canonicalizes
only those owned test fixtures; the production no-symlink checks remain strict.
Commit `763c6e7` additionally fixes clean-build parent creation and preserves the
AEGP stop marker in failure reports. No live Adobe evidence is inferred from CI.

## Preserved checks for exact code 9ea7bcf

| Check | Result and scope |
|---|---|
| Received-file integrity and 24 structural assertions | PASS, six named windows / 529 instructions; not runtime tests |
| Actual export parsing and compiled profile hashes | PASS; file-only, Adobe calls=0 |
| Local unified Linux | PASS: 238 collected, 229 PASS/nine platform skips; Node 62 |
| Research CI 36824300893 | PASS on Linux and macOS |
| Downloaded macOS unified report | All 21 stages PASS; Python 238/238, Node 62 and existing scoped guards 15 |
| Owned provider retention and directory lifecycle | PASS on macOS arm64, including calling after original references are closed |
| Full product macOS CI 36824300983 | PASS, all build/sign/package/smoke/archive-verification steps completed |
| Downloaded research reports and source identity | Both outer hashes, all inner entries and five changed source hashes verified |
| Real AE no-scan AEGP/supervisor | NOT CONNECTED / NOT RUN |
| Actual resource registration/apply-render | NOT RUN; historical registration FAIL unchanged |
| Full static-security audit | NOT RUN again; five historical findings remain open |

The Python count remains 238: the new retention scenario extends an existing
test. Nested native cases are not counted again. Local parser ASan/UBSan passed
with empty diagnostics, not a full audit or AE memory proof. The unified local
runner still does not build the product; that separate workflow was checked.
No product ZIP was installed or handed over. Green CI does not clear unreviewed
warnings. Docs use [skip ci]; CI belongs to the exact code commit above.

## Next concrete integration gate

The source connection is complete; the next gate is the exact SDK build plus
preparation/inert verification on the authorized Mac, followed by exactly one live
folder-object run only after fresh authorization for the private FILE call and
provider-reference retention. The live run must still begin from a fresh blank,
clean, idle AE 25.6 host and produce one report ZIP without any plug-in scan.

This chat cannot inspect or update `/Users/os3kov/Documents/AE-Hot-Loader/` or the
running AE process, so local checkout synchronization, SDK build identity, loaded
artifact identity and live baseline remain blocked on access to that Mac. No new
library collection or repeat of the unchanged ordinary plug-in scan is justified.

Before a live call, verify SDK build, inert entry, exact artifact/loaded identity,
fresh blank/clean/idle host state, one owned ASCII directory, and separately
specified authorization including provider-reference retention. Require exact
path roundtrip, single successful release and unchanged PID/project/registry/
module list. Do not treat the authorization flag or stored observations as consent
or a fresh baseline. No automatic retries after uncertain native outcomes.

The subsequent PLUG pass still needs end-of-pass callback and retained-state
review. Do not invoke global-folder helpers, Birth/InitIterator/RequiredPreSearch,
replace callbacks, bypass the cache predicate, clear caches, force notifications,
change the old bool, unload code or repeat the unchanged scan. Previous installation
and one-restart permissions are consumed. New risky actions need separate approval.

## Preserved actual host results

| Gate | Preserved result |
|---|---|
| Scoped embedded late registration | FAIL: 45de0c9 / scoped-0b8c8f122e80 / fixture88019a1a01a7; 785 unchanged effects |
| RSMB startup-registered apply/render | PASS: earlier identified one-frame smoke |
| RSMB late registration | FAIL, retained separately |
| Dynamic fixture application | PASS, earlier add/remove; render NOT RUN |
| Flat-resource failure | FAIL, earlier crash evidence retained |
| Current AE/project/resident identity | NOT OBSERVED; offline files and CI are not a live baseline |

The SDK review did not establish a public ordinary-effect late-registration
procedure; PICA ordinary-effect publication remains unverified, not disproved.
No product loader, installed Agent/shell/panel, third-party plugin, user project,
preferences or main changed. No merge, release, installation, restart or live
Adobe call. Proprietary inputs and raw dumps remain private, outside Git.
