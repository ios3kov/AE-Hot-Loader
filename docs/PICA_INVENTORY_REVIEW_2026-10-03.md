# Public PICA plug-in inventory — 2026-10-03

Stage C1, Development preparation for a bounded Validation diagnostic.
Rules: AE-Development-Rules v8.0.0 at
`132b7cd32873ba7328e3128ffbb33e1929b74d45`; AI_ENTRYPOINT first, then
AI-STATE/API-SOURCE/SAFE/REPRO/TEST-CONTROL/TASK-CLOSE/CLEANUP and native/thread/
ownership/tools diagnostics/IPC overlays. Acceptance INV-01–08 is recorded
before implementation in [PRODUCTION_PLAN](PRODUCTION_PLAN.md). Original
ordinary-effect workflow, A/B/C1/C2/D and release obligations remain open.

## Decision and primary contracts (INV-01/02)

Actual SDK: AE SDK 25.6_61, Examples/Headers, not redistributed. Exact inputs
are hashed by the clean-source builder. SPPlugs.h: rev4 at lines 157–191,
rev6 at 379–413; SPFiles.h: Mac value FSRef at 174–185; SPAdapts.h public
adapter getters. Native static assertions bind the actual declarations.
SPFiles.h conversion-specific caller-owned CFURL comments at 288–291 do not
establish ownership for the separate GetPluginXplatFileSpec getter. Rev6 getter
is signature-checked only, never invoked. Use rev4 GetPluginFileSpecification:
caller-provided SPPlatformFileSpecification value containing FSRef, converted
with Apple's public FSRefMakePath into an owned 4096-byte UTF-8 buffer.
No CFURL retain/release, guessed lifetime, opaque handle conversion or private ABI.

Primary OS authority is the Files.h selected by `xcrun --show-sdk-path` under
CoreServices/CarbonCore, FSRefMakePath declaration/contract at 4061–4087.
The builder explicitly selects that SDK with -isysroot and records path/hash
before/after. FSRefMakePath is deprecated since macOS 10.8 but present in the
actual selected SDK. Only the two owned/native conversion calls locally suppress
the deprecation warning; other warnings remain errors. A real owned-file
FSPathMakeRef/FSRefMakePath roundtrip is required in the inert prerequisite.
This is an exact Mac research contract, not a future cross-platform guarantee.

SPPlugs.h 492–499 property acquisition may send a plug-in message and change its
property list. No GetPluginProperty/FindPluginProperty, plug-in acquisition,
AddPlugin/AddXPlatPlugin/AddAdapter, startup/shutdown, scan or unload is used.
AcquireSuite itself may load modules; that possibility is explicit in the live
scope. No global list/object is freed: only this diagnostic's iterator is deleted
once; two bounded suite leases remain until controlled host exit.

Known anchors are the existing owned Control Shell and Rust Probe ordinary-effect
bundles in user MediaCore, match names OS3KOV.AEHotLoader.ControlShell and
OS3KOV.AEHotLoader.RustProbe. Builder pins binary/resource/Info.plist bytes,
CFBundleExecutable, source declaration SHA and presence of each ASCII match literal
in its resource. The native observer pins binary/resource before and after and
requires both match names in the same public AE effect baseline. This establishes
bounded metadata/file association, not a runtime source-origin or publication proof.
Neither known binary was loaded in the previous recorded dyld inventory despite
both registered matches; no lazy effect load is required or triggered here.

Exact returned bundle OR main-binary path is a positive LISTED correlation.
No basename/prefix/child guess or implicit normalization. Repeated entries are
retained. NOT_LISTED requires complete enumeration and every path resolved;
otherwise a missing hit is UNKNOWN. File/path/adapter errors retain raw codes.
Even LISTED does not establish that AddPlugin can publish ordinary effects.

## Implementation and bounded failure handling (INV-03/04)

Separate PicaInventory helper, builder and independent file observer reuse only
reviewed public snapshot, resident-image binding and private durable I/O primitives.
New build/run/token and unique prospective bundle; no shared mutable-state reset.
Exact source/host/module/binary/PID/start/token byte scope, consume-before-call,
main-thread idle execution, exclusive durable per-stage files and no replay.
Limits: 2048 entries, 1 MiB serialized entry payload, 4095 path bytes and 256 adapter
name bytes; incremental per-entry journal avoids quadratic disk output.
Native 10-second cooperative deadline checks surround SDK calls and writes;
a blocked host API cannot be preempted. The external 30-second deadline writes
one TIMEOUT and preserves process/partial evidence, without retry or termination.
A failed getter is unresolved evidence; failed stage, changed baseline, missing
durability or exceeded bound is STOPPED. No negative claim from partial output.

Before/after same owned blank clean idle project, registry identities and runtime
binding required. Existing loaded images cannot disappear; potential suite-load
additions are recorded separately. Known-file hashes and registered matches must
stay stable. Independent verifier binds entry deltas/terminal, NULL-end stage,
claim, known-file evidence and every journal to the exact request identity.

Focused owned tests: 19 Python cases, including one aggregate C++ test containing
27 labelled owned/synthetic policy scenarios; all PASS, no skips. File tests use
real private durable files with synthetic host/providers. The C++ policy tests
cover failure injection, deadlines, one-shot refusal, empty/partial/error results,
2048-entry and aggregate-payload bounds. They do not execute AE.

## Completed preparation and remaining live steps (INV-05–08)

Clean-source code/test candidate **525000b6915423b7d387f10e846f972472570754**,
build **inventory-a96d55e17240**, run
**pica-inventory-35f19062c0114be199aaaec144692bb6**. Actual AE SDK arm64 compile,
local ad-hoc sign/strict verification, exactly two exports, identity getter,
inert/null/token/wrong-host/refused-self-hash and real owned FSRef roundtrip PASS.
Final binary SHA-256:
`8cb9534868406b4223e4b55c209a2addab8126baefdf6c5d14bf65947df24bb8`.
Private manifest SHA-256:
`17fdd6a5841e8f97c126149ac073d287ba5e69261ce3943cc1c5185a09ffcfce`.
Selected OS Files.h SHA-256:
`84311d08bf2ff05c2960c104193dd0690e9c07e20ce1667200d66f7639ac546e`.
Manifest independently verified against candidate/known files. Control empty,
prospective destination absent; no installation or AE operation performed.
Prospective bundle is user MediaCore/AEHLInventorya96d55e17240.plugin; only this
unique new bundle is in any proposed installation scope.

Full local regression **418 Python / no skips, 62 Node, 22 stages PASS**.
27 native policy scenarios count as one of the 418 Python cases. Source and all
330 tracked file hashes unchanged. Runner report `/private/tmp/AEHL-checks-xz3j4hdn.zip`,
25 members, independent CRC/member/SHA checks PASS; report SHA-256
`910ea6fa9f65a250eed0100a262e4fd520331ab6a8e28066150e45a8d429b424`.
Python stage 82.648 seconds, unittest body 81.216 seconds, original 120-second limit.
The previous source 9b1fdca run hit that Python-stage deadline, preserving partial
FAIL in `/private/tmp/AEHL-checks-0yugzmbe.zip`, SHA-256
`32d290e5d52ef249d5d57a5a87ff66ef8a798328d62ded518348ce67cb005bc9`.
It is not relabelled PASS. Focused runner 24 cases PASS; module discovery 418 cases
in 0.415 seconds. Root cause of the one-off earlier timing is not established.
Final pass used the same limits; no test or check was weakened or suppressed.

Bounded static review completed at clean 525000b; raw exit **1**, sole retained
`vibe.no_ratelimit_auth` at tools/artifact_manifest.py:71: local argparse CLI,
not a network/auth endpoint. No new finding; raw report kept at
`/private/tmp/aehl-inventory-525000b-audit.json`, SHA-256
`178ae71cc90b0146dc563735988c2d8f3ec44c7314ae354f98b1d7375799a55e`.
Manual review checked SDK/file ownership, main-thread gate, one-shot identity,
incremental durability, exact/no-guess correlation, bounded failure cleanup and
preserved product requirements. Both CI workflows completed/success at exact 525000b:
[research 37124717978](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37124717978),
[macOS 37124718156](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37124718156).

Private reviewed packet inside ignored build folder: `inventory-private.zip`,
six identified candidate/config/manifest members, CRC/member check PASS, SHA-256
`9e54ccea7abd0fe23f9bbc449e4902768322c0015d1d349ee0e359f313c3547e`.
Manifest/config contain the unused one-shot token and remain private; no raw
control/manifest/SDK/binary is published or committed. Older failed/intermediate
builds are preserved as unapproved private evidence, not alternative candidates.

The accepted eight-step proposal authorizes six preparation steps; live step is
conditional on the concrete reviewed packet and actual operation authority.
Previous PICA availability permission was one-shot and is consumed. Do not inspect
or mutate the current AE session during preparation. A fresh exact packet must
identify the new helper, potential suite load, global plug-in iterator and public
file/adapter getters, with one owned blank clean idle session and closed-host
installation guards. No forced quit, project reset or removal of loaded helpers.

INV-07/08 remain NOT RUN pending that gate. Registration/apply/render NOT RUN,
backend NOT READY. Cleanup retains previous installed inert helper/session,
proprietary SDK, known/third-party plug-ins and historical/private evidence.
Only owned temporary test workspaces are disposable. No main merge or release.

## Final reconciliation and cleanup

| Acceptance | Result | Exact evidence |
|---|---|---|
| INV-01 | PASS | Actual SDK type assertions, value FSRef/public OS conversion contract; 74 SDK inputs + OS header hashed |
| INV-02 | PASS (contract) | Exact known bundle/binary/resource/source association, baseline match requirement; LISTED/NOT_LISTED/UNKNOWN owned file tests |
| INV-03 | PASS (implementation) | Separate inert one-shot identity-bound native helper and independent observer; unique private packet |
| INV-04 | PASS (owned/synthetic) | 19 Python cases including 27 native policy scenarios; preserved raw errors, failures, deadlines and uncertainty |
| INV-05 | PASS (prerequisite) | Clean 525000b SDK arm64 build/sign/exports/hash/inert and real owned FSRef roundtrip; actual AE NOT RUN |
| INV-06 | PASS | 418 Python/no skips, 62 Node, 22 stages; ZIP/source verification, bounded review and both exact-source CI success |
| INV-07 | NOT RUN | New live inventory permission/closed-host guard pending; no install, launch or AE inspection |
| INV-08 | NOT RUN | Depends on actual INV-07 inventory; no finding inferred from synthetic fixtures |

Private review-receipt.json SHA-256: `6e6a7bc7ad3915b0940d3f215ca22ea3b894f4d3973f19f8bc5ed49d8504fde5`.
The code/test source and native candidate remain 525000b; this documentation-only
closeout records those exact results rather than claiming another runtime/build.
User-facing progress: a safe discriminating inventory experiment is now ready;
ordinary-effect publication, apply/render and no-restart product proof remain open.
No older obligation is removed, weakened or silently accepted. No AddPlugin,
private registration adapter, merge or release authorization is inferred.

Cleanup review: owned temporary test fixtures cleaned by their context managers;
runner/private packet/raw failed report and intermediate builds retained for audit.
Installed previous consumed helper/session, existing known and third-party plug-ins,
SDK and historical evidence preserved. No host forced quit or preferences/project
change. The unused new helper token remains private and applies to only this packet.
