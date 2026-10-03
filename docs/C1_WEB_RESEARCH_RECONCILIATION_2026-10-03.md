# C1 — external research reconciliation

Date: 2026-10-03. Branch: `research/ordinary-plugin-discovery`.
Clean starting source: `ecc6c28eeea72bcca81e1aae7d1ad70abd95bcec`.
Checkpoint text revised from `0d29d70070cd1131b56255052962c962d66a3a6d` at the
user's explicit request to correct the checkpoint without further research.
The [original published checkpoint][original] remains historical; its checks
and source identities are not reattributed to this revision.
Accepted rules:8.0.0 / `132b7cd32873ba7328e3128ffbb33e1929b74d45`;
AI_ENTRYPOINT first, API-SOURCE-001, AI-STATE-001, TASK-CLOSE-001, CLEANUP-001.
Production-engineering research/review workflow. Target remains AE2025,
macOS arm64, SDK25.6_61. Product scope and A/B/C1/C2/D/release are retained.

## Result and scope

Further original-file continuation, 2026-10-04:
[host-operation boundaries](C1_COMPLETE_HOST_OPERATION_2026-10-04.md) establishes
retained routine transfer into FCSpec, branch-specific readiness after add and
queued numeric-index apply with conditional later catalog lookup. No complete
late context/commit/recovery or full frame-read/lifetime contract follows.
These are local original-file findings, not independent model/web runtime proof.
The source-only and text-correction packets below retain their historical scope.

Later continuation, 2026-10-04: comparison of the supplied three-question model
reports led to [original-file reader research](C1_EFFECT_SUITE_READER_BRIDGE_2026-10-04.md).
The static Effect Suite5/key→FLT writer storage bridge is now substantiated for
the selected files. Actually acquired live suite/known-good effect identity,
late host operation, full consumer lifetime and partial recovery remain UNKNOWN.
This later file result does not relabel the source-only packet below as a host
test or hot-load proof. The completed DOCFIX pass remains historical.

No supported public late-publication mechanism was found in the reviewed SDK
and sources. That result does not prove that every internal route is impossible.
No ordinary third-party effect absent at startup has been registered, applied
and rendered without restarting AE in this packet. Host adapter remains unbound;
mutation safety for the actual changed state, initial factory/ABI/thread/owners
and partial-failure handling remain UNKNOWN. Native trials remain BLOCKED / NOT RUN.

The user's two supplied research attachments and subsequent architectural
argument were audited as external evidence. The final attachment improves the
distinction between an unsupported public route and an unproved internal route.
Its proposed late calls, callback replay and injected errors do not establish
their prerequisites or authorize those operations. Only online reads, exact SDK
reads and repository documentation were performed here.

## Source identity and authority

Exact SDK files are the primary authority for the selected API declarations.
Seven local header/utility files were SHA-256 pinned in the private receipt;
no SDK or Adobe binary source is redistributed. Paths below are relative to
`ae25.6_61.64bit.AfterEffectsSDK/Examples`.

| Source | Version / identity | Scope |
|---|---|---|
| `Headers/AE_PluginData.h:61–94`; `Util/entry.h:40–69` | SDK25.6_61; hashes in baseline receipt | Opaque host context, callback2, entry2 and registration macro |
| `Headers/AE_Effect.h:815–845,912–921,1195–1218` | SDK25.6_61; SHA256 `5432df9bb447cefce2f96c1477d6beccd4686b7236d460c803beab76dae1d537` | Dynamic flags, MFR selector guarantee, actual selector names |
| `Headers/AE_GeneralPlug.h:2173–2197,2742–2832,2960–2963` | SDK25.6_61; hashes in baseline receipt | Installed-effect iteration/apply, AEGP hook registration and AEGP ID |
| `Headers/SP/SPPlugs.h:103–150`, `SPAccess.h:240–257`, `SPCaches.h:97–116` | SDK25.6_61; hashes in baseline receipt | PICA add/acquire/cache declarations; no established ordinary-effect bridge |
| [Symbol exports][symbol] | File commit `449b8c5eaf4c8619d2abffe00dbbb22a92bc5f1a`, 2025-02-05; blob `789a74a03843ad26355a3775f3c13ebef1d31a43` | Adobe-authored SDK guidance in a community-maintained mirror; compare exact headers |
| [MFR][mfr], [selectors][selectors] | File commit `1ff44f1326c6a304725d41bbba3ec47f909cc80a`, 2025-02-11; blobs `e065ebdb452d4f157773876ce5c62a11e04db4e2`, `cb2f461d39b6382c3d9e02c3dd0818fb929fd553` | Host dispatch and selected flag semantics; not a registry mutation API |
| [Premiere reload][ppro] | File commit `8f424b5fb42c41e2ffc15886289f707bb02067f0`, 2025-01-27; blob `03d0b6cd976ab8449ac96acfc0e1e7d504782111` | Premiere launch cache; do not transfer to AE |
| [Effect Manager][manager] | Adobe Help, read 2026-10-03 | Enable/disable applied at restart; not proof of universal impossibility |
| [Startup scan crash log][scanlog] | Author's AE17.1.2 / x86-64 report, 2020-08-14; checked before this text-only revision | `PLUGp_ScanFile`, `PLUG_GetPiPL`, `FLT_PLUGScanFunc` observed in a scan/load stack; no late-call/owner/inverse contract |
| [MediaCore crash log][medialog] | Author's AE17.0.6 / x86-64 report, 2021-01-07; checked before this text-only revision | `ML::LoadPlugins` / `ML::PluginSupport::LoadAllPlugins` and `ae::prem::MediaCoreData`; no installed-effect-registry bridge established |
| [AEXCompat loading investigation][loading], [world-safety source][worlds] | Commit `7113ebfeccfccfc29c1ba009a06c1cfff6a56c56`, 2026-10-03; blobs `0f6ff85ef1edbfc23acd87069c5d80fcfd361dd7`, `9349d167414ba29e69e1e3221895506f80f88772` | Original author's compatibility-host code/observations; Windows effects and a different host |

The rolling PiPL guide now includes SDK26.5 and Premiere27-only additions; the
official UXP Application page labels relevant entries Since27.0. Neither expands
SDK25.6 availability. Forum dates, reported platform and exact AE version are
separate fields. A current webpage is not exact-target runtime evidence.

## Reconciliation of material claims

CONFIRMED below means the stated bounded source fact, not AE runtime acceptance.

| Claim from supplied research | Verdict and evidence | Consequence |
|---|---|---|
| `PF_REGISTER_EFFECT` is a standalone exported registration function | CONTRADICTED by `entry.h`: it is a macro invoking the supplied callback | A breakpoint needs the actual callback/dispatch target; the macro is not a host symbol |
| Symbol-export guidance proves callback creation exclusively while parsing PiPL at startup | UNSUPPORTED: [symbol] describes export visibility and an entry example | Neither retained context lifetime nor late re-entry is specified |
| Saving `inPtr`/callback makes later replay valid | UNKNOWN: `AE_PluginData.h` only requires passing the opaque context back to the supplied callback | Identify the host owner, creation/destruction, module binding and legal call scope first |
| The registry has no locks and is structurally immutable | CONTRADICTED for selected operations by [registry transaction evidence](C1_REGISTRY_TRANSACTION_BATCH_2026-10-03.md): recursive mutex at receiver+0x50 | Selected locking exists; full reader coverage, retained readers and safe late insertion are still unproved |
| `GLOBAL_SETUP` is always the first possible selector | TOO BROAD: `AE_Effect.h` allows ABOUT at any time | Host lifecycle ordering cannot be inferred from one numeric selector or sample |
| All effect flags are immutable during execution | CONTRADICTED by exact SDK QUERY_DYNAMIC_FLAGS support and named allowed flags, including camera/light usage | PiPL remains static; this is not permission to change MFR capability arbitrarily or add an effect |
| Parameters can be freely redefined after initialization | NOT SUPPORTED; parameter setup defines the layout | A forum's once-per-session phrasing does not prove new match-name registration impossible; exact SDK spells the selector `PF_Cmd_PARAMS_SETUP` |
| MFR global-setup serialization supplies an external registry transaction | UNSUPPORTED: [mfr] and exact header describe host-driven selectors | No caller-held exclusion covering registry iteration, UI, other work and future admission is documented |
| `U_SuspendContext` is an `AEGP_SuspendContext` alias/global guard | UNSUPPORTED by selected SDK and contradicted as a universal guard by [SUS scope](C1_SUSPEND_CONTEXTS_2026-10-03.md) | Current-context transfer/one callback completion is not all-consumer drain |
| Premiere `PF_SetNoCacheOnLoad` proves runtime hot reload | CONTRADICTED by [ppro]: next launch/relaunch cache behavior | No AE late-publication conclusion follows |
| Absence of `PF_UNREGISTER_EFFECT` proves rollback impossible and a crash inevitable | UNSUPPORTED inference | Whole-effect recovery remains UNKNOWN; actual crash/failure is not invented |
| `GLOBAL_SETDOWN` is the inverse of partial registration | UNSUPPORTED; [selectors] explicitly separates setdown from module unload | Trace rollback of containers, canonical names, preferences and callbacks separately |
| PICA installed-plugin list equals the ordinary effect registry | CONTRADICTED for observed ordinary effects by [PICA inventory](PICA_INVENTORY_REVIEW_2026-10-03.md) | NOT_LISTED rules out equivalence for that scope, not every hypothetical hidden bridge |
| A June2024 forum report verifies AE2025 entry2 behavior | NOT ESTABLISHED: [original report][plist] omits the exact AE version | Keep author-reported bundle-metadata/startup behavior as a lead, not target-version proof |

The bounded SDK Headers/Util name scan found no `AEGP_SuspendContext`,
`PF_UNREGISTER_EFFECT` or `SetRenderSuppression` declaration. This is an inventory
result, not a proof about all private implementations. `SPAddPlugin` exists in the
PICA headers; it must not be silently erased from the inventory or promoted to an
ordinary effect publication contract.

## Useful independent evidence

[AEXCompat's loading investigation][loading] reports resolving metadata through
`PluginDataEntryFunction` for Windows effects whose render exports have other
names. Its revised measurements distinguish module loading from successful
selector dispatch. This is a useful check against assuming every render entry is
named `EffectMain`; it does not establish PiPL absence or late registration in
our native macOS AE target. A callback into a substitute host publishes only what
that substitute host implements.

[Its original world-safety implementation][worlds] documents a plugin-owned
thread calling a host pixel-format callback, and distinguishes discoverability
under a lock from the returned world's lifetime. The related author's particle
study uses a Windows AE26.3x87 reference. This adds a concrete consumer class to
our coverage checklist: plugin/provider-owned threads and deferred callbacks,
beyond the selected BEE/housekeeper/executor paths. Whether those consumers read
our target registry, and which host lifetime protects them, remains UNKNOWN.
Its SRWLOCK protects its own world lookup, not AE's FLT registry.

The 2006 effect-reload and 2015 manually loaded AEGP examples concern other
lifecycle tasks. Neither proves ordinary third-party late publication in AE2025.
The first attachment's lack-of-lock/impossible conclusions and the latest
attachment's remaining-route priority therefore receive different verdicts.

The public crash logs independently corroborate participation of the three named
PLUG/FLT scan symbols in those historical builds. `FLTp_FiltSetup`,
`FLTp_AddEffect` and `FLT_FilterRegistry::RegisterNewFilter` remain grounded in
this project's original-file artifacts. `ML::LoadPlugins` is present in the
MediaCore log: do not describe it as absent from public search. Its bridge to
the ordinary installed-effect registry is not established by that stack.
Effect Manager's restart behavior remains a product signal, not a prohibition
of an internal append operation.

## Corrected hypotheses and next evidence

The internal startup publication chain is a retained hypothesis, not the only
logically possible private solution. Trace the Effect Suite readers/apply path
to the actual owner and then relate it to startup publication; neither a key nor
a `this` pointer is presumed to encode registry identity. The selected SDK declares
`AEGP_InstalledEffectKey` as `A_long`, not a pointer type; its internal mapping
still needs evidence. An adapter, index or copied record can explain different
objects on the writer/reader paths.

| Hypothesis | Retained or corrected checkpoint |
|---|---|
| H1 | Public late-add route not found; internal impossibility is not proved |
| H2 | `dlopen` plus an owned `PluginDataEntryFunction2` callback is not target registry proof without a valid host load-context |
| H3 | PICA is not treated as the ordinary registry without exact ordinary-path LISTED and installed-key correlation; existing NOT_LISTED remains bounded evidence |
| H4 | Correlate a known-good startup publication through descriptor ownership and reader/key/apply mapping; differing `this` values alone do not reject FLT |
| H5 | Replace worker-thread AEGP iteration with permitted main-thread enumeration before, at actual reentry opportunities and after publication; observe another effect's preview/MFR separately |
| H6 | Determine whether in-flight rendering reads the mutable installed catalog or separately retained stable descriptors; prove safety of the actual changed state |
| H7 | Retain actual descriptor/module/callback owners with a substantiated lifetime and thread contract |
| H8 | Establish atomic commit or recovery from partial failure; unregister of a successful session-resident record is a separate requirement |
| H9 | Existing-effect reload, CEP and Premiere cache behavior remain outside ordinary late-add acceptance |

For H6, global render drain is one possible protective design, not a requirement
for every safe append architecture. Stable retained descriptors can remove the
need to drain rendering only when existing instances do not use invalidated
mutable state and other changed state, callbacks and reentry remain safe. MFR
selector guarantees alone say nothing about installed-catalog access. Possible
alternatives include main-thread confinement with controlled reentry, retained
immutable snapshots, or complete synchronization of the affected readers.
None is established for the target build here; the current executable refusal
policy is unchanged.

| Operation | Requirement for append-only publication until session end |
|---|---|
| Rollback of an unfinished insertion | Required if mutation can leave visible partial state on failure; alternatively establish a non-failing commit after preparation |
| Unregister of a successfully published record | Required only if accepted behavior includes removal/unload/re-registration within that session |

Vector-before-map publication and collision replacement prove neither atomicity
nor safe rollback. Failure recovery includes whichever indices, names, preferences,
owners and callbacks the discovered operation changes. Session residency is a
hypothesis for late-add; retained A/B/C2 and other existing product obligations
are not silently removed or satisfied by it.

The three proposed actions are conditional experimental plans, not operations
performed or authorized by this text-only correction:

1. **H4 — known-good startup calibration.** An owned ordinary fixture installed
   before launch must connect writer arguments to count/iteration/match-name and
   `AEGP_ApplyEffect`, including descriptor owner after return, thread and
   destruction/release boundaries. Follow intermediate indexes/copies before
   rejecting a writer as unrelated.
2. **H5 — one new match name after launch.** Only a substantiated connection and
   the technical safety prerequisites permit testing idle without preview/cache,
   preview/MFR of another effect, and another AEGP's actual main-thread reentry.
   A key must resolve to the new match name, apply and recognizable real output;
   existing keys/apply must remain valid. Main-thread code cannot enumerate
   "during" a synchronous call unless an actual reentry opportunity exists.
3. **H8 — the interruption boundary inside the calibrated registration.**
   Establish that a failure before completion leaves the entry unobservable, or
   that a complete compensating path restores changed state, or that commit
   cannot fail after preparation. This is partial-failure recovery, not removal
   of a live successful record. No deliberately interrupted host call is run here.

No worker-thread AEGP call is a valid window. Pause, Flush, U_SuspendContext and
Death are not publication transactions. Three successful windows do not prove
race freedom. A failed direct inserter call can expose a missing context or
completion step and does not disprove all late-publication routes.
Implementation remains BLOCKED: no substantiated callable host entry, no live
AE2025 arm64 Effect Suite correlation, no demonstrated render/read-set contract,
and no partial-failure rule. C1 research is already the current stage; one
successful late call does not close its acceptance gates.

No startup calibration, install, launch/attach, callback replay, late insertion,
fault injection, unload, preference mutation or user-project operation ran here.
No further search or original-body investigation follows the user's correction
request in this revision. Previously collected preliminary symbol-location
evidence is retained privately and is not presented as a live suite contract.

## Previous packet acceptance, verification and retention

NET-01–05: DONE for documentation research: pinned sources/SDK, corrected claim
matrix, useful new consumer class and explicit next dependency order. No native
contract is promoted to VERIFIED.164 local document links and diff whitespace
checks PASS;241 tracked non-Markdown files and seven exact SDK files unchanged.
Raw scanner exit1/review_required is retained:254 text files,123 unsupported,
no omissions, nine completed checks. Its sole unchanged local artifact-manifest
CLI finding was manually reviewed as a false positive; no suppression or green
scanner verdict is invented. Source scope is a precommit dirty snapshot of ecc6c28
plus four documentation changes, not an old clean-commit PASS.
Local full executable regression is NOT RUN for Markdown-only edits. Exact commit,
push/remote equality, automatically triggered CI state and final source-byte
checks are recorded separately in the private closeout receipt. No old CI outcome
is inherited. This packet is documentation research; product PARTIAL.

Private baseline/source-hash/check/scanner receipts are retained under
`/private/tmp/aehl-web-research-9wj5i8wr`. Attachment hashes:
`271ac2ed9252c3d1fa7096108d0969870b60bb19a8586a29cfe7753753386293`,
`55cdcd905a51c03da9a4c0d9b74a1a634354e11486f7bb45d5fcf3a51f1a128c`.
No raw external report or SDK excerpt is copied into distributable artifacts.
Cleanup assessment: retain the owned scanner snapshot and receipts as evidence;
no deletion or relocation is needed. Historical evidence and unknown materials
remain untouched; the packet creates
no installable artifact or product/runtime readiness claim.

## Checkpoint correction verification

Current edit baseline: clean `0d29d70070cd1131b56255052962c962d66a3a6d`.
DOCFIX-01–03 cover the user's text-only correction, preservation of product/native
refusals, and documentation/source/publication checks; DONE for documentation.
167 local links/table shapes/diff PASS,241 non-Markdown and373 files outside
the four edited documents unchanged. Their current results and
exact publication/CI state are retained in
`/private/tmp/aehl-reader-route-d6u09f1y`. This is a documentation correction,
not a new completed reader/body investigation or live safety proof. No executable
file, native profile, SDK, existing gate or historical evidence is changed.
Local full executable regression is NOT RUN for this Markdown-only revision.
Owned preliminary symbol inventories and documentation receipts remain retained;
no cleanup removal is needed.

[symbol]: https://github.com/docsforadobe/after-effects-plugin-guide/blob/449b8c5eaf4c8619d2abffe00dbbb22a92bc5f1a/docs/intro/symbol-export.md
[mfr]: https://github.com/docsforadobe/after-effects-plugin-guide/blob/1ff44f1326c6a304725d41bbba3ec47f909cc80a/docs/effect-details/multi-frame-rendering-in-ae.md
[selectors]: https://github.com/docsforadobe/after-effects-plugin-guide/blob/1ff44f1326c6a304725d41bbba3ec47f909cc80a/docs/effect-basics/command-selectors.md
[ppro]: https://github.com/docsforadobe/after-effects-plugin-guide/blob/8f424b5fb42c41e2ffc15886289f707bb02067f0/docs/ppro/plug-ins-reloaded.md
[manager]: https://helpx.adobe.com/after-effects/desktop/apply-effects-and-animation-presets/effects-and-animation-presets/effect-manager.html
[plist]: https://community.adobe.com/questions-529/plugin-loading-issue-56930
[loading]: https://github.com/onmokoworks/AEXCompat/blob/7113ebfeccfccfc29c1ba009a06c1cfff6a56c56/docs/AE_EFFECT_LOADING_INVESTIGATION_2026-07-22.md
[worlds]: https://github.com/onmokoworks/AEXCompat/blob/7113ebfeccfccfc29c1ba009a06c1cfff6a56c56/minihost/src/worker_world_safety.cpp
[scanlog]: https://community.adobe.com/t5/after-effects-discussions/after-effects-keeps-crashing-on-startup/td-p/11361271
[medialog]: https://community.adobe.com/t5/after-effects-discussions/i-have-a-problem-with-after-effects/td-p/11733793
[original]: https://github.com/ios3kov/AE-Hot-Loader/blob/0d29d70070cd1131b56255052962c962d66a3a6d/docs/C1_WEB_RESEARCH_RECONCILIATION_2026-10-03.md
