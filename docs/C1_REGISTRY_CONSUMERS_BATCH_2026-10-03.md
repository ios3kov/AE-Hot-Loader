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

## PASS-02–03 — bounded file findings

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

Clean final-source collection, independent original-byte/package verification,
full regression, bounded static review, both CI and final checkpoint reconciliation
are pending. Old PASS at 880b55f remains historical, not current evidence.

## Whole-product reconciliation and cleanup

C1 backend NOT READY; registration/apply/render NOT RUN; historical unchanged
scan FAIL preserved. C0 historical diagnostic PASS is retained without repeating
it. A/B integrated acceptance, D hardening/compatibility, final package and release
gates stay open as mapped in PRODUCTION_PLAN. No goal or acceptance removed.
Cleanup assessment: unique owned private capture/scripts/reports and old/new rules
checkouts remain needed for provenance; no expendable repository files identified.
No deletion, move, preference/project/plugin alteration or backup purge performed.
