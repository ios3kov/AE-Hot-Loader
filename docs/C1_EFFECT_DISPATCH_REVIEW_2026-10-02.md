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

1. `FLTp_DoParamsSetup` publishes a canonical instance at `0x53758`, before
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
