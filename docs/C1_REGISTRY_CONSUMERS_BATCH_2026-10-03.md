# C1 registry consumers and failure review — five-block pass

Stage C1 / Development; initial clean source e42588fc5d19e2e8a423fefa55ca8b64cc1a560a.
Rules v8.0.0 / 132b7cd32873ba7328e3128ffbb33e1929b74d45 adopted by the
user's explicit request. Acceptance was fixed in PRODUCTION_PLAN before body
review/implementation. Existing product scope and all A/B/C/D/release obligations
are retained. Authority: repository/owned offline fixtures/pinned file inspection
and research branch commit/push; consumed diagnostic scope is not renewed.
No installation, AE launch/attach/read, native invocation, teardown or release.

## PASS-01 — baseline and task control

Exact VERSION/annotated tag/source and published GitHub release verified.
Standard self-test: 140 files, 43 executed cases PASS; two Windows-only cases
and PowerShell parser NOT RUN locally. Generated map and three actual routing
contexts PASS. No feature-set change requested, FEATURE-SET-001 conditional N/A.
[Adoption](RULES_ADOPTION_8_0_0_2026-10-03.md) and existing canonical records
now contain current authority, baseline and retained whole-product obligations.
Documentation links and final reconciliation remain part of PASS-05.

## PASS-02 and PASS-03 — bounded file findings

Only pinned FLT arm64 file
SHA-256 `227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256`.
VM locations below are file research positions, never live addresses/public ABI.
New `registry-consumers` mode: 14 fixed complete bodies/helper bodies,
2413 decoded instructions, 150 addressed structural anchors. Preliminary
capture is preserved privately, but is not final clean-source evidence.

| Complete file window | Observed behavior | Limit / implication |
|---|---|---|
| Registry destructor `46cc–4918` | Locks receiver `+50` at `4700`, calls DisposeFCSpec `4740`, releases vector owners, destroys primary map `480c`, unlocks `4820`, destroys mutex `4828`, then remaining containers | Destruction is a multi-object teardown, not a safe late-registration rollback or all-reader admission barrier. Actual singleton lifetime/caller contract unknown; never invoke it. |
| UpdateEffectFromPrefs `5480–5854` | Recursively locks same `+50` (`54bc`); virtual name/version reads precede PREF_Helper construction `5684`. DoesKeyExist `56ac` / GetTextPrefData `56f8` errors branch to integer exception allocation/throw `5790/57a4`, `57b0/57c4`. Success may change GlobalFlags2 `572c`. Unwind releases strings/scoped lock `5804/582c/5848` | Combined with prior RegisterNewFilter publishing vector/map/index before prefs `530c`, this is a concrete post-publication failure path. No inverse registration mutation in the reviewed local unwind. Transitive rollback/exception ABI remain unproven; not a reproduced AE failure. |
| ReplaceByNewerFilter `5854–5c34` | Locks `589c`, overwrites indexed vector owner `58c8` before virtual name read `5924`, map insertion/update `5ab0/5b50`, copied index `5bac`, prefs `5bb8`. Local unwind releases owners/strings/scoped lock | Replacement adds separate mutation order and is not an evidenced rollback. Prior escaped shared owners can survive a container change; ownership alone does not establish dispatch exclusion. |
| ReplaceEffectWithMissingInstance `5c34–606c` | Locks `5c7c`, FindFilterPtr `5c8c`, erases map `5df4`, calls placeholder registration `5e1c→993a4`, then edits vector/end/index (`5ea0/5eb8/5ec4/5f48`) | This route creates the previously identified missing-effect placeholder, not a real loaded effect. It mutates state and cannot substitute for safe rollback or hot registration. |
| GetEffectSettingsForPluginManager `7448–7aec`, owner release `7aec–7b4c` | Creates a separate shared settings object/control block (`7488/74b4/74cc`), copies metadata/preferences, can throw preference errors `7a08/7a28`; shared owner release is separate | Signature accepts a scoped lock; no acquisition in this body. Settings snapshots are not a persistent registry/publication lease, nor complete reader coverage. |
| GetAllEffectSettingsForPluginManager `7b4c–80a8`, pair release `80a8–8138` | Holds `+50` (`7b98`) across primary and secondary map loops; temporary FCSpec owners retained `7c04/7e20`, settings objects generated `7c28/7e44` and retained in caller's output set `7ca4/7ec0`. Unlocks `7fe0` | An additional consumer locks, but output snapshots outlive this lock. No all-reader/dispatch/MFR exclusion contract follows from this individual operation. |
| UpdateEffectSettingsFromPluginManager `8138–8840` | Locks `8180`, finds/retains effect, writes preferences `8604`, reapplies them `8640`; after iteration calls PREF_UpdateFile `871c`, error throw `877c`, unlock/owner cleanup on unwind | This is a mutating settings/persistence route. Late error and local cleanup are not an atomic registry+preferences transaction. PREF internals/canonical rollback remain unknown. Do not call it as a synchronization helper. |
| Project write Start `31da0–31e58`, Reset `31e88–31ed8`, destructor `31ed8–31f38` | Uses boost get/set_tss_data (`31de4/31e10/31f00/31f20`) on `_MergedGlobals` key `e9d20`, storing/resetting a thread-specific set | These are project serialization bookkeeping scopes, not global reader exclusion. Start duplicate-object flag can throw; no registry mutex or global worker drain in these complete bodies. |
| Project read Start `31fc8–32080`, destructor `320b0–32214` | Uses get/set_tss_data (`3200c/32038/321c8`) on distinct key `e9d28`; destructor disposes saved parameter strings `32168` before clearing thread-specific state | Another thread-local bookkeeping map, not a lock shared by all registry/dispatch/MFR consumers. Raw address/TSS import confirmation is required in final evidence. |

## PASS-04 — decision before a native adapter

**NO-GO for constructing a live registration adapter from the reviewed routes.**
This is a safety/readiness decision for these mechanisms, not proof that the
product is impossible. Individual recursive registry locking, zero active-effect
count, loading-done flag, project serialization scopes and settings snapshots
fail to establish continuous all-reader/dispatch/MFR exclusion. Local cleanup
and replacement/placeholder/destructor paths do not establish failure atomicity
or safe rollback. Exact receiver/provider identity/lifetime are still unknown.
The seven retained general-plugin records continue to prevent the unchanged
resource-pass policy; no repeat or private teardown is justified.

A future adapter needs an independently evidenced admission/drain mechanism
that keeps a single exclusion window continuously through native calls, reentry
and postflight, plus actual ownership and complete publication/error semantics.
Until then adapter implementation and a new executable live packet remain
BLOCKED. Additional body collection alone does not satisfy this requirement.
Next engineering decision must identify a specific prospective exclusion
provider and its proof procedure before extending private ABI research; an
alternative that changes the no-restart product goal requires a user decision.

## PASS-05 — implemented reproducible evidence and verification

Collector now packages this fixed scope and explicit non-runtime claims; native
profile/helper/policy and installed diagnostic remain unchanged. Three focused
new tests initially failed because this mode did not exist. Full focused
collector suite now has 42 passing tests: altered mutation/lock/TSS/error anchors,
missing/duplicate instructions and retargeted bounds reject; file-only script and
symbol inventory boundaries checked. All such fixture transcripts are synthetic.
No installable artifact is created by this mode.

Clean code/test source **a293c90e615dd4a67c2d559422ac990756d79908**.
All twelve collector archives independently PASS: CRC/member uniqueness/hash
inventory, exact source, complete instruction coverage and original-file hashes.
For new consumer mode, raw Mach-O corroborates 342 direct/44 indirect branches,
eight mutation/local-flag stores, five ADRP/ADD address paths to e9d20/e9d28 and
two original indirect-symbol-table import names for boost get/set_tss_data.
Across consumer/transaction/entry/isolation modes: 1289 direct/161 indirect
branches, 33 rebases and two raw import resolutions. No live state read.

Full local regression: **382 Python/no skips, 62 Node, 22 stages PASS** on macOS
arm64 / Apple clang 21 / Node 24.12.0. Independent runner archive verification:
25 members, 307 tracked source files and unchanged clean source after execution.
Local product package NOT RUN; full AE pipeline BLOCKED; live request false.
Three new collector tests bring the focused suite to 42; guard policy and journal
are unchanged. Prior 880b55f and the pre-commit exploratory capture stay historical.

Bounded static audit: raw exit 1 / review_required, all selected checks completed;
1333 inventoried files / 931 unsupported / no omissions; four workflows scanned.
Sole vibe.no_ratelimit_auth at tools/artifact_manifest.py:71 reviewed as the
unchanged local argparse CLI false positive; raw finding retained. This does not
certify dependencies, history, whole-product security, runtime or release.

Research CI [37120969285](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120969285)
and macOS CI [37120969284](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37120969284)
completed/success at exact a293c90; CI uses pinned Node 22.23.2. CI native/package
and owned-host smoke evidence does not establish Adobe registration/apply/render.

Private local evidence (not an installable handoff):

| Record | SHA-256 |
|---|---|
| build-ae-hot-loader/resource-registry-consumers-cb8375b9-mp4r5i1x.zip (31 members) | eb895040ea0bda9f797d2ab922bef5e27a6129d45f78175da8d6ab64fedc7a24 |
| /private/var/folders/bs/39klz7cd52z6xkm817vj0zjm0000gn/T/AEHL-checks-e_equ6vu.zip | a81d603363633169c01164d3c3928b72fc7a114cdc9c8cc959168c61b8671e18 |
| ../private-live/consumer-collection-a293c90.json | 0647efb864dfd7474445d8d38613c9b56525ae435678fdecbd38081b9d8220d4 |
| ../private-live/consumer-independent-a293c90.json | f6f5601ed0dcd925007b8729888e7d9fcda6ad185a89a87af62c8ddb51062ff9 |
| ../private-live/consumer-fields-a293c90.json | 9660203e0319c3b9e81610f2d492396a52228de52d436b23ef79dc5576005229 |
| ../private-live/consumer-local-independent-a293c90.json | 80dc0428dc7c3a60c09fd2175b418002929562d79cd0419fc12f1f082d54d5ce |
| ../private-live/consumer-audit-a293c90.json | 24a8aff506e9f02319e5c3917822f29196c9ce52c35cdeaceffe77b1ad9b7878 |
| ../private-live/consumer-review-a293c90.json | a999e9ae07ef5c8e3f26903b615b6d1045ad6edbbb9bef5f6f537dfbd5bebab4 |
| ../private-live/consumer-ci-a293c90.json | 4acf3d224388a1721058794bdf91b5cf3ac2bcf2c7bb487ee46bd2e74b0f080f |
| ../private-live/rules-v8-adoption-a293c90.json | 0f5a2e15bbb09040514d296ea049a8c371a58904e570f30482edb8f61f150c50 |

Reproduce with collector --review registry-consumers and
run_research_checks.py --expected-commit a293c90e615dd4a67c2d559422ac990756d79908
from that clean source. Independent verifier scripts in private-live:
verify_consumer_final_20261003.py, verify_consumer_fields_20261003.py and
verify_consumer_local_20261003.py. Their saved receipts above bind exact archives.
Documentation-only closeout is separate from the tested code/test source.

Acceptance reconciliation: PASS-01–05 complete within the defined offline scope;
PASS-04 is a NO-GO safety decision for these routes, not native registration PASS.
Current canonical status/plan/handoff/compatibility/adoption and local links checked.
All retained whole-product obligations remain explicitly open as below.


## Whole-product reconciliation and cleanup

C1 backend NOT READY; registration/apply/render NOT RUN; historical unchanged
scan FAIL preserved. C0 historical diagnostic PASS is retained without repeating
it. A/B integrated acceptance, D hardening/compatibility, final package and release
gates stay open as mapped in PRODUCTION_PLAN. No goal or acceptance removed.
Cleanup assessment: unique owned private capture/scripts/reports and old/new rules
checkouts remain needed for provenance; no expendable repository files identified.
No deletion, move, preference/project/plugin alteration or backup purge performed.
