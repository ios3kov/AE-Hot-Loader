# AE Hot Loader — current development status

Updated: 2026-10-01. Branch: `research/ordinary-plugin-discovery`.
Stage **C of A–D**; core registration, A/B/D and release gates remain open.
AGENTS.md and PRODUCTION_PLAN apply. Shared rules rechecked unchanged:
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
Previous status is preserved at
[immutable e96a1c8](https://github.com/ios3kov/AE-Hot-Loader/blob/e96a1c8f31b5aad70c11400b17c1f11e9bbe4154/docs/DEVELOPMENT_STATUS.md).
Dated evidence is unchanged; previous instructions do not renew permissions.

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

## Checks for exact code 9ea7bcf

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

Connect the reviewed binding/retention, directory adapter and durable journal
to a separate inert-by-default no-scan AEGP and its external supervisor. This is
still missing; existing scoped-discovery commands continue to run the old loader.
No new user command or additional library collection is requested now.

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
