# C1 — external research reconciliation

Date: 2026-10-03. Branch: `research/ordinary-plugin-discovery`.
Clean starting source: `ecc6c28eeea72bcca81e1aae7d1ad70abd95bcec`.
Accepted rules:8.0.0 / `132b7cd32873ba7328e3128ffbb33e1929b74d45`;
AI_ENTRYPOINT first, API-SOURCE-001, AI-STATE-001, TASK-CLOSE-001, CLEANUP-001.
Production-engineering research/review workflow. Target remains AE2025,
macOS arm64, SDK25.6_61. Product scope and A/B/C1/C2/D/release are retained.

## Result and scope

No supported public late-publication mechanism was found in the reviewed SDK
and sources. That result does not prove that every internal route is impossible.
No ordinary third-party effect absent at startup has been registered, applied
and rendered without restarting AE in this packet. Host adapter remains unbound;
actual admission/drain, initial factory/ABI/thread/owners and whole-effect inverse
remain UNKNOWN. Native trials remain BLOCKED / NOT RUN.

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

## Next evidence and safe dependency order

The internal startup publication chain is a retained hypothesis, not the only
logically possible private solution. The next useful work should test new caller,
context and recovery edges, rather than recapture unchanged Pause/Flush/SUS bodies.

| Order | Bounded research question | Observable evidence / refusal criterion |
|---|---|---|
| 1 | Which original host caller creates the metadata callback context and owns the publication receiver? | Exact source-image/body identities, context creation/destruction, module association, retained owners and legal thread; a cached raw pointer alone fails |
| 2 | What host entry establishes selector exclusion, and which consumers can bypass it? | Trace callers outside the already reviewed dispatcher/per-effect lock; include UI, installed-key readers, future MFR admission, host queues and plugin-owned callbacks. A snapshot counter or one executor flush fails |
| 3 | Is there a full per-record failure inverse before any late mutation? | Original error/unwind paths restore vector/map/index/canonical/preferences/notifications while preserving old effects and owner lifetimes. Setdown, missing stub or process teardown alone fails |
| 4 | After a safe instrumentation contract and current live authority exist, calibrate startup publication against public installed keys | Known-good owned fixture, exact native identities, callback/descriptor↔installed-key/match-name correlation. This is calibration, not late-load acceptance |
| 5 | Only after1–4 and exact safety checks, evaluate late publication and recovery | New ordinary third-party binary absent at startup: registry→apply→render without restart, stable existing effects, bounded repeated/error recovery |

The latest attachment's H2 null/fabricated/retained callback trials, H5 late calls
under active preview, H6 preference/menu mutation and H8 deliberately interrupted
insertion are not the next authorized operations. They depend on currently
missing technical contracts. Public AEGP calls must respect their main-thread
contract: another AEGP iterator is not license to call suites from a random
worker thread. A few successful trial windows cannot establish universal race
freedom; documented coverage and continuous exclusion are required independently.

No startup calibration, install, launch/attach, callback replay, late insertion,
fault injection, unload, preference mutation or user-project operation ran here.

## Packet acceptance, verification and retention

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

[symbol]: https://github.com/docsforadobe/after-effects-plugin-guide/blob/449b8c5eaf4c8619d2abffe00dbbb22a92bc5f1a/docs/intro/symbol-export.md
[mfr]: https://github.com/docsforadobe/after-effects-plugin-guide/blob/1ff44f1326c6a304725d41bbba3ec47f909cc80a/docs/effect-details/multi-frame-rendering-in-ae.md
[selectors]: https://github.com/docsforadobe/after-effects-plugin-guide/blob/1ff44f1326c6a304725d41bbba3ec47f909cc80a/docs/effect-basics/command-selectors.md
[ppro]: https://github.com/docsforadobe/after-effects-plugin-guide/blob/8f424b5fb42c41e2ffc15886289f707bb02067f0/docs/ppro/plug-ins-reloaded.md
[manager]: https://helpx.adobe.com/after-effects/desktop/apply-effects-and-animation-presets/effects-and-animation-presets/effect-manager.html
[plist]: https://community.adobe.com/questions-529/plugin-loading-issue-56930
[loading]: https://github.com/onmokoworks/AEXCompat/blob/7113ebfeccfccfc29c1ba009a06c1cfff6a56c56/docs/AE_EFFECT_LOADING_INVESTIGATION_2026-07-22.md
[worlds]: https://github.com/onmokoworks/AEXCompat/blob/7113ebfeccfccfc29c1ba009a06c1cfff6a56c56/minihost/src/worker_world_safety.cpp
