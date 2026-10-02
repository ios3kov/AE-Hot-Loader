# C1 ordinary-effect publication — bounded file review

Stage C1, Development. Starting clean research HEAD
`c4542aed922a77f7b5da0720b105bfeb94be68fd`; rules **6.2.0**,
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`.
AI_ENTRYPOINT, PROCESS API-SOURCE-001/SAFE-001/regression/evidence,
ENGINEERING debugging/compatibility, TOOLS file diagnostics and NATIVE ownership
apply. Collector maintenance is Standard; possible private host integration
remains Critical and blocked. No new Product Discovery or release gate applies.

## Question and acceptance

After [identifying seven retained names](C1_RETAINED_NAMES_LIVE_PASS_2026-10-02.md),
can an ordinary effect reach publication without replaying existing general-plugin
setup/cleanup? Review the pinned file path and its refusal/ownership side effects;
a static route is not a safe native ABI or permission to invoke it.

PUB-001: preserve exact original PLUG/FLT files, select fixed complete bounded
function windows including contiguous chunks for larger functions, reject gaps/
unknown decode/changed structural anchors, and package source-bound private evidence.
PUB-002: distinguish resource effect, descriptor retention, actual registry
publication and Missing Effect placeholder routes. Keep unknown indirect receiver,
state, post-setup/readiness/global-initialization and exception contracts explicit.
PUB-003: correct the reproduced diagnostic false positive without accepting real
LLDB errors or incomplete/undecoded output; retain existing collector modes.

Acceptance: focused refusal/owned-tool tests, real pinned-file collection and
independent archive/operand checks, available clean-source regression, bounded
static review and exact-source CI. Original native helpers/profiles/ResourcePassGate
must remain unchanged. No AE process read, attachment, launch, installation,
private callback, scan, provider retention, setup replay or teardown is authorized
or performed by this block. Existing live diagnostic scope is consumed.

## Collector failure reproduced and corrected

The preliminary PLUGp_ScanFile window decoded all 215 instructions with empty
stderr and successful LLDB exit, but the old whole-text `error:` substring test
rejected symbol comments containing `std::runtime_error::runtime_error` and
`std::runtime_error::~runtime_error`. The failed private transcript is preserved.

The collector now first requires exact decoded address coverage, then removes
only inline comments on those addressed instruction lines for diagnostic matching.
Command output, instruction text and stderr remain checked for `error:`/`fatal:`.
Actual command errors and undecoded/partial output still refuse collection.
Five new tests were run before implementation (five expected errors), then all
**18 collector tests PASS**, including real LLDB on owned arm64 code/data.
This fixes evidence collection; it does not repair effect loading.

## Reproducible publication scope

`collect_resource_search_abi.py --review publication` adds 13 fixed windows and
83 addressed static anchors. Existing search-abi/cleanup/lifecycle/ownership modes
and their pins remain unchanged. No new function is loaded or called.

Pinned PLUG SHA: `12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22`.
Pinned FLT SHA: `227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256`.
All VM references below are unslid file evidence, not runtime callable addresses.
Large FiltSetup/AddEffect functions are each split into adjacent at-most-4096-byte
windows without omitting their return/unwind branches.

## Conditional file findings, verified at clean source

- Resource lane: PLUGp_ScanFile predicate/callback → FLT_PLUGScanFunc →
  FLTp_FiltSetup → PLUG_RegisterRoutine(PiPL, path) → post-setup →
  FLTp_AddEffect → FLT_FilterRegistry::RegisterNewFilter. Existing PLUG_Search
  still runs sack-wide cleanup; selecting one file/root does not isolate it.
- Path-only setup has explicit kind/metadata/duplicate rejection paths, constructs
  and retains a routine descriptor and can prepare the filter/do lazy globals
  after publication. Direct setup is therefore not a harmless registry insertion.
- AddEffect can add to a disabled list, reject/dispose or replace an existing
  filter. RegisterNewFilter retains into a vector before unique-map insertion;
  its collision branch replaces the map value. It is not transactional rollback
  or a safe duplicate guard for a caller-created FCSpec.
- **FLT_RegisterEffectIfMissing is a placeholder route**: the absent branch
  constructs an FCSpec, installs FLTp_MissingEffectMain and calls RegisterNewFilter.
  Its name does not mean loading a missing plugin from disk. The adjacent lazy
  wrapper can replace an effect with a missing instance on a handled failure.
  Registry presence alone can therefore be false evidence for real hot loading.

These are bounded interpretations of pinned files. Full downstream indirect
interfaces, lifetime, locking/thread contract and late-host safety remain UNKNOWN.
The safe ordinary-effect backend is **NOT READY**; the zero-record gate stays
unchanged. Actual registration/apply/render remains NOT RUN; historical FAIL
is not repaired by these observations.

## Historical prepared verification checkpoint (closed below)

Implementation/focused tests prepared. Clean-source publication/default-mode
collection, full available local regression, independent evidence checks, scanner
review and exact-source CI are pending; append their exact results after execution.
Next discriminator: the readiness/lazy-global contract and source/ownership of
PiPL/path-only descriptors, not invoking MissingEffect or bypassing sack cleanup.

## Exact-source collection and regression closeout

Code/test source **db4799e2d964a68be761d71924bc5c693d13dea3**.
Publication collection PASS: **13 complete windows / 5002 decoded instructions /
83 addressed structural anchors**, original PLUG/FLT hashes stable before/after.
Private ZIP SHA-256:
`d18de38e7b942f9528e8bdd15bdd8b2b0c0abb13adbbc1d1ef7079d64b3ad9dc`.
Independent 30-member inventory/CRC/every archived hash/complete-address coverage
PASS. **48 direct BL targets** independently decoded from original arm64 instruction
bytes match the selected anchors. These are static assertions, not runtime tests.
Independent verifier source SHA
`99def2371a07f1b8953bd0c974f5cb1040db2309609cde6677de7e57f41b0234`;
private verification record SHA
`cb0133a011f32a65281e74606722ef8f25a468c9e8560b28627fe7bb17827c90`.
No original Adobe binaries or complete disassembly are published.

| Complete function window, end exclusive | Instructions |
|---|---:|
| PLUGp_ScanFile, 0xf6c0–0xfa1c | 215 |
| PLUG_RegisterRoutine(PiPL,path), 0x6fa8–0x7150 | 106 |
| FLT_PLUGScanFunc, 0x8cf98–0x8d250 | 174 |
| FLTp_FiltSetup, 0x8d250–0x8ef8c (two contiguous chunks) | 1871 |
| FLTp_AddEffect, 0x8b2d4–0x8cc70 (two contiguous chunks) | 1639 |
| RegisterNewFilter, 0x5014–0x53f0 | 247 |
| FiltPostSetup, 0x9284c–0x92ab8 | 155 |
| ScReadyFilter constructor, 0x146c8–0x14838 | 92 |
| FCSpec::DoLazyGlobals, 0x5e504–0x5e764 | 152 |
| FLTp_RegisterEffectAndDoLazyGlobals, 0x99268–0x993a4 | 79 |
| FLT_RegisterEffectIfMissing, 0x993a4–0x997e4 | 272 |

All four existing modes collected again at this exact source and their archives
independently verified. This checks compatibility of the affected collector; it
does not repeat any live AE experiment.

| Mode | Instructions | Private ZIP SHA-256 |
|---|---:|---|
| Default search-abi | 472 | `8eabbec5bc33579e179cb08856f65d587cc4cd05c3c7d3676fe9745eda7b18f1` |
| cleanup | 1390 | `11f7f96263fd395f92f20959c014bf8ac5ee264fc7c8801ca629129fcc32c520` |
| lifecycle | 891 | `3c8c853afd07d79f6fd066f408bd357d4a976171dec569600fda40cdade074af` |
| ownership | 960 | `379df6221afd9ab9908b7d7b4f54dff02f696826b82b13d00d89e80cee044117` |

Full clean local macOS regression PASS: **358 Python/no skips, 62 Node, 22 stages**;
all tracked source hashes matched the clean source before/after. Report SHA
`56a49bfab3d3a54e467b1479bec64c0e205763e0a0fff935c64eff2de1d0ba57`.
Independent exact ZIP inventory/CRC/member hashes/source inventory PASS. An initial
invocation supplied an incorrect expected commit and was BLOCKED before any test
stage; preserved report SHA
`47e86f7b56e5c4a38df6c82bf429162a8ded75f5918ed50c4f77842079420dcb`.
The subsequent PASS uses the full actual Git SHA; no guard was weakened.

Bounded code-profile scanner at clean db4799e completed all selected checks:
**346 supported files / no omissions**, four workflows included. Raw exit **1**
retains only the re-inspected `vibe.no_ratelimit_auth` finding at
`tools/artifact_manifest.py:71`: local argparse setup, not an HTTP auth route.
Nothing was suppressed; whole-security/release readiness remains not assessed.
Private audit SHA `c4feed809bccd5cee00df8e2d9ea39181658e1f6da122b688326ce8f807b6881`.

Exact-source [research CI 37055729740](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37055729740)
completed/success. [Full macOS CI 37055729761](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37055729761)
also completed/success at exact db4799e (verified final GitHub workflow state).
Final private CI receipt SHA
`c9e67fea9c5eb2ad726493a3362e4ec1cfb4c9654fd37983855219df6d6bc897`.
These remain build/offline evidence, not host registration/apply/render.
Native helper/profile/ResourcePassGate bytes are unchanged from the reviewed live
candidate. No new SDK artifact, native backend, installation or live authority.

## Two concrete downstream delegates and remaining contract

Supplemental same-source file-only windows `0x983c8–0x983d0` and
`0x9a204–0x9a20c` each contain two complete instructions: dereference the supplied
shared-pointer object's first word, then tail-branch respectively to
`FLT_FCSpec::ReadyFilter()` at static 0x5cea8 and
`FLT_FCSpec::DoLazyGlobalSetup(...)` at static 0x5d328. Both original B immediates
were independently decoded and matched; this is not runtime receiver attestation.
Private supplemental ZIP SHA
`0cef958ba868f2488fca9ceeb1aa1b3c43bc44b0da5738ec90e5268f7dd2061e`;
exact archive/CRC/member hashes and input preservation PASS.

The sampled FCSpec::DoLazyGlobals (0x5e504) is a separate canonical-stream wrapper,
not the body reached by the resource setup's FLTp_DoLazyGlobals (0x9a204).
Do not treat it as complete evidence for that indirect/delegated setup contract.
The full readiness/global-setup bodies, the PiPL/path descriptor constructor,
provider retention, repeat behavior, exception cleanup/partial registry mutation,
locking/thread restrictions and runtime ownership are still unreviewed.

Next authorized work: a bounded file-only review of those exact downstream bodies
and the path-only descriptor construction, with complete windows and independent
raw-call checks. Define ownership/refusal criteria before any native design.
ResourcePassGate is unchanged; no forged sack, omitted cleanup, callback
replacement, placeholder registration or direct private call is an approved
workaround. A usable safe registration route has not yet been established.

## Review verdict

PUB-001/002/003 are complete for this bounded file/tooling stage: exact windows,
refusal behavior, source/pin preservation, conditional path/placeholder separation,
private evidence integrity, local regression and both exact-source CI PASS.
Current status/plan/handoff/compatibility records are reconciled; local Markdown
links/whitespace and unchanged native/profile bytes checked. No installer/runtime
artifact or product behavior changed, so no new installation/live test is claimed.
Full supported private registration contract and product release remain blocked
on the explicitly listed downstream/runtime gates. Continue the named file-only
readiness/global-setup and descriptor-ownership review before native integration.
