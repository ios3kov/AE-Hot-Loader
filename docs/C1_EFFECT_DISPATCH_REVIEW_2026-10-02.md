# C1 effect dispatch and parameter failure paths — bounded file review

Stage C1, Development. Starting clean research HEAD
`2627c9e69cc41451c44347d1dba35be50dab88e0`; adopted rules **6.2.0**,
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`. AI_ENTRYPOINT,
PROCESS API-SOURCE-001/SAFE-001/regression/evidence, ENGINEERING debugging and
compatibility, TOOLS file diagnostics and NATIVE ownership apply. Collector
maintenance is Standard; dependent private host implementation remains Critical
and blocked. Product contract is unchanged; no release/validation delivery.

## Question and acceptance

Continue the [readiness review](C1_EFFECT_READINESS_REVIEW_2026-10-02.md): trace
parameter setup and outer/inner dispatch through the saved procedure invocation,
and distinguish local handle/exception cleanup from canonical-state rollback.

DISPATCH-001: collect complete fixed bounded FLT bodies at the exact existing
file pin, reject changed anchors/decode/bounds, preserve hash/source identity and
private report integrity. Include the generic dispatch constructor, optional
exception selector, hardware callback and both actual procedure-call lanes.
DISPATCH-002: document canonical publication-before-setup, command/data flow,
saved indirect procedure, crash context and failure/exception side effects.
Do not infer receiver identity, provider lifetime, AE thread safety or rollback
from a normal return, diagnostic wrapper or file-only interpretation.
DISPATCH-003: focused refusal/owned-tool tests, existing-mode regression,
clean-source file collection, independent archive/raw branch checks, full
available local regression, bounded static review and exact-source CI.

Only existing pinned files and owned test code are inspected/executed. No AE
launch/attachment/process read/install/private call/scan/provider retain/teardown
or retry. Original native helpers/profiles/ResourcePassGate remain unchanged;
prior live diagnostic authority is consumed. This block cannot approve a live
experiment or implementation using guessed private C++ interfaces.

## Bounded file findings

The exact FLT file remains pinned to SHA-256
`227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256`.
Eight complete function windows cover **1939 instructions and 86 anchors**.
Preliminary text is private and is not clean-source acceptance evidence.

1. `FLTp_DoParamsSetup` calls RegisterCanonicalInstance at `0x53758`, before
   dispatching command 4 (PARAMS_SETUP) at `0x53898`. Handle allocation failure,
   dispatch error and parameter-count mismatch have subsequent failure paths.
   The local transient handle is freed; no explicit canonical unregister appears
   in this complete body. Transitive factory/callback behavior remains unknown:
   this observation does not prove that rollback is impossible or absent elsewhere.
2. Outer dispatch selects project/sequence context, increments dispatch state and
   installs cleanup callbacks before entering host dispatch at `0x98640`.
   Full callback bodies and matching state restoration are outside this scope.
   A procedure pointer alone is therefore insufficient to reproduce this route.
3. Host dispatch initializes output state, obtains a procedure through receiver
   virtual slot `0x10` (`0x38dd0`/`0x38dd4`) and saves it. The generic constructor
   copies a seven-word dispatch payload; this does not establish provider retention.
   Actual receiver type, procedure identity and provider lifetime are unobserved.
4. The host passes false at `0x38f20` to the optional machine-exception wrapper.
   This selects the crash-context lane, not the machine-exception jump-buffer lane.
   Both lanes were collected to prevent confusing them. Even the false branch
   installs/restores a hardware/unhandled-exception handler. Its callback forwards
   to the previous handler when present. These are host-side effects, not rollback.
5. The selected lane pushes crash context, loads the saved procedure and six
   command/data arguments, calls it indirectly at `0x3b8e0`, then pops context.
   Unwind cleanup also pops it. There is no nearby null-procedure guard between
   that saved load and invocation. This is file evidence, not a validated ABI.
6. The alternate lane calls the saved procedure at `0x3b530` after setjmp and
   restores jump-buffer state. Its error policy can return 14 or deliberately
   crash. It is not selected by the observed host call and is not a safe fallback.
   Error reporting/notification and transient cleanup do not prove transactional
   reversal of prior canonical registration/global setup.

## Implementation and verification checkpoint

Added a fixed `effect-dispatch` collector mode, scoped symbol inventory, exact
address/opcode anchors and explicit UNKNOWN/NOT PROVEN/NOT RUN report claims.
Refusal tests cover each changed anchor, incomplete/duplicate coverage and
unreviewed boundaries. Native helpers, profiles and ResourcePassGate are unchanged.
Clean-source collection, independent archive/raw branch checks, full regression,
static review and exact-source CI remain pending until the implementation commit.

The next file-only discriminator is PluginImpl provider preparation/retention and
canonical stream-factory retention/error behavior. No live packet is executable.
Backend NOT READY; registration/apply/render/release gates remain open.

## Clean-source verification — local and exact-source CI PASS

Implementation source **8aec890b95e0eea0216582f43bee0109c31700f3**.
Focused collector suite **24 PASS**. The 86 changed-anchor refusals and coverage/
window refusals pass; preliminary real-file comparison initially caught an
incorrectly transcribed final unwind address (`0x3b7fc` versus actual `0x3b800`).
The anchor was corrected before the clean implementation commit. No host call
was involved and no evidence was weakened.

All seven modes collected successfully at this same clean commit. New dispatch
archive `build-ae-hot-loader/resource-effect-dispatch-393c7e78-a3s337hb.zip`,
SHA-256 `e3e72645f9578b41f1d2bbe83d16d93447f2cb6d741690f6acedb819d995bae6`,
contains 19 members. Complete coverage **1939 instructions / 8 bodies / 86 anchors**.
Original file pins match before/after. Reports remain private, not product packages.

Independent verifier `../private-live/verify_effect_dispatch_20261002.py`, SHA-256
`2ac8ec65e0b3a8bc79ba3b264c96a28314bde3b3f733c3c92077b6b982d37437`,
verified every member hash, manifest inventory, ZIP CRC, exact source, coverage,
original input pins and **all 377 direct B/BL** in the new mode from original
arm64 Mach-O bytes. It separately matched raw BLR x8 at `0x38dd4`, `0x3b530`,
`0x3b8e0`. This confirms instruction correspondence, not recipient identity.
All seven archives PASS. Result `dispatch-independent-8aec890.json`, SHA-256
`70f9de45bb7c9a9269f34b46eed8c3ab5045d56104db53ce71471f6c4079e1d1`.

Full local regression **364 Python / no skips, 62 Node, 22 stages PASS**.
Report `/private/var/folders/bs/39klz7cd52z6xkm817vj0zjm0000gn/T/AEHL-checks-_c2xmt6g.zip`,
SHA-256 `e2ef8ebafc39b6751263cc4ac7b314f5c5856281b62ce8b7987236a5f7f47a01`.
Independent ZIP inventory/CRC/member hashes/300 tracked source hashes and unchanged
source PASS; receipt `dispatch-local-independent-8aec890.json`, SHA-256
`f2367ae9dc2a204538248c711e11218b770a9633323505637ff79e6caa9db807`.
The runner labels live/product/release gates BLOCKED/NOT RUN as required.

Static review is complete for the bounded diff and current source. Scanner
`dispatch-audit-8aec890.json`, SHA-256
`6a727d63a2d7efc0de74e9594386e1537d0718ef892876cb7a615d5a9c17972a`,
records 556 text files / no inventory omissions / 4 workflow files inspected.
The scope includes ignored text evidence and omits unsupported files/history/
runtime/dependency-vulnerability checks. Raw exit 1 is retained: its sole
`vibe.no_ratelimit_auth` finding at `tools/artifact_manifest.py:71` is the same
local argparse entrypoint, not an auth route. Manual source review confirms this;
no rule was suppressed. This is not security or release certification.

Both GitHub workflows completed/success on exact implementation source:
[research CI 37060170220](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37060170220)
and [macOS CI 37060170144](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37060170144).
Private final receipt `dispatch-ci-8aec890-final.json`, SHA-256
`f8442f15615bf458f2e7fdfe5ae99c72620fda9c1579c4741ee6aaf7287109de`.
CI build/sign/package/synthetic checks are not actual AE loading or rendering. Main, native helpers/profiles and ResourcePassGate are
unchanged. No AE operation or new live packet. DISPATCH-001/002/003 PASS in their bounded offline scope. Registration/apply/render remain NOT RUN,
backend NOT READY, historical late-registration FAIL unchanged.

## Next-scope locator, not acceptance evidence

A separate file-only symbol locator at
`../private-live/provider-factory-symbols-b72chktk` rechecked the existing
PLUG/aelib/FLT file pins before/after nm. PLUG's PluginImpl load/free/entrypoint
symbols are imports from **PluginSupport**; FLT's canonical registration and
unregistration symbols are imports from **TDB**. The remaining lifetime/rollback
question therefore crosses these providers. Imported symbol names do not establish
function semantics. Their bodies and exact additional file pins are not yet
reviewed. Start the next bounded review there; do not call those functions.
An earlier locator stopped on an incorrectly assumed aelib path before nm for
that input; its partial private output is preserved and is not evidence. The
completed locator uses the collector's reviewed framework path and validation.
