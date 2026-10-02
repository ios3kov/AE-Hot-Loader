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

## Conditional findings to verify at clean source

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

## Prepared verification checkpoint

Implementation/focused tests prepared. Clean-source publication/default-mode
collection, full available local regression, independent evidence checks, scanner
review and exact-source CI are pending; append their exact results after execution.
Next discriminator: the readiness/lazy-global contract and source/ownership of
PiPL/path-only descriptors, not invoking MissingEffect or bypassing sack cleanup.
