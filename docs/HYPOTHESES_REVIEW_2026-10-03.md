# Combined hypothesis review — AE 25.6 / macOS arm64

Date: 2026-10-03. Starting clean research source
`16986dcc759c7d6d4870218e378b100d6afd28b6`.
Rules v8.0.0, pinned `132b7cd32873ba7328e3128ffbb33e1929b74d45`.
User asked to check the three proposed directions in one pass, then asked to
evaluate combinations. Acceptance was fixed in [production plan](PRODUCTION_PLAN.md)
before the checks; the combination row was added after the user's steering.
This record does not change the original product contract or approve a narrower
shell-only product. FEATURE-SET is N/A until such adoption is requested.

## Result boundaries

| Hypothesis | Executed check | Result for the original product goal |
|---|---|---|
| HYP-01: PICA adds an ordinary effect | Exact supplied SDK contract/adapter review, compile-only signature assertions, literal checks in nine hash-verified target files | NOT VERIFIED: actual suite availability, AE ordinary-effect adapter and FLT publication bridge UNKNOWN |
| HYP-02: direct single-effect publication | Reconciliation of pinned ownership, entry, publication, consumer and failure evidence with historical registration-pair results | BLOCKED for native invocation: no reviewed owned receiver, continuous all-consumer exclusion or complete failure contract |
| HYP-03: stable shell swaps compatible code | Actual shell logic with owned C++ shared libraries outside AE, including concurrent/reentrant busy refusal, rejection and rollback | PASS for this owned-process transaction; current AE registration/apply/render NOT RUN; not an arbitrary plug-in loader |
| HYP-04: coherent decision/evidence/checkpoint | New reproducible native test, SDK receipts, source review, README/status/plan/handoff reconciliation | Verification receipts and exact clean-source results recorded in closeout below |
| HYP-05: combine mechanisms | All three pairings and three-way dependency/ownership analysis | Conditional candidate, not a completed native design; adding a shell does not remove late-registration prerequisites |

No AE launch, process inspection, attach, scripting, install, private call, scan,
unload or lifecycle replay was performed. Existing native helpers/profiles/gates
and installed materials are unchanged. Historical one-shot scopes remain consumed;
no executable safe new native packet has been established.

## HYP-01 — PICA contracts and a concrete next discriminator

Primary source is the supplied SDK 25.6_61 in the known Downloads SDK root.
Header SHA-256 inventory and lexical matches are in private
`hypotheses-sdk-16986dc.json`, SHA-256
`7298e0feec64ab0803204946c4702ece072ddf0a72256edf3fcab906ddd63bb2`.
No Adobe headers or binaries are added to Git.

- `Examples/Headers/SP/SPPlugs.h:45-54`: exact suite name is
  `SP Plug-ins Suite`; default revision is **4**, with separate 5/6 constants.
  Do not substitute a higher revision or assume it is exposed by AE.
- `SPPlugs.h:328-378`: revision **6** uses **SPXPlatPluginsSuite** and
  **AddXPlatPlugin**, with XPlatFileSpec, instead of the revision-4 platform file
  type. `SPFiles.h:114-129` specifies version 1 and CFURLRef on macOS. A higher
  revision must use its exact declared structure, not a revision-4 pointer cast.
  Compile-only assertions for the revision-6 signature and its distinction from
  AddPlugin also PASS; source SHA-256
  `6a8c1de64ed8eeebf4db21ffc64b8b6337832cf17ec990a07f70787f354c0c53`,
  receipt-v6 SHA-256
  `0c52c5e8e4b255f4189be31615ef26ca3c95ba8e2d7e37ecd36d86da18a765e2`.
  This offers another declared contract to investigate; AE availability is UNKNOWN.
- `SPPlugs.h:133-150`: AddPlugin needs a plug-in list, platform file specification,
  PiPL, adapter name and adapter-specific information; its output is SPPluginRef.
  That is not a private FILE_Spec, FLT FCSpec or proof of installed-effect identity.
- `SPAccess.h:48-50,240-257`: `SP Access Suite` revision **3**; AcquirePlugin obtains
  an accessor and may load a module. ReleasePlugin may allow unloading; it is not
  an established registration rollback and is not invoked here.
- `SPAdapts.h:45-48,86-118,233-260`: `SP Adapters Suite` revision **3**; adapters
  supply message/data conversion and manage their supported plug-ins. The generic
  adapter protocol does not identify AE's ordinary eFKT adapter or its FLT contract.
- `SPInterf.h:87-104`: the generic messaging interface is limited to PICA plugins;
  a non-PICA plugin requires its adapter's interface.
- `SPBasic.h:82-101`: AcquireSuite can load a suite and ReleaseSuite can unload it.
  Suite availability testing must therefore be scoped as potentially stateful;
  it is not covered by a passive no-new-image diagnostic.

Compile-only static assertions against the unmodified supplied headers confirm
default suite revisions and exact AddPlugin/AcquirePlugin function-pointer types:
**PASS**, Apple clang / arm64 / C++17. Initial compile failed because the SDK's SP
include root was omitted; both logs are retained. Adding that existing include
root fixed the build, without stubs or altered SDK types. This is signature
evidence only, not AE suite availability or ordinary-effect registration.
Private source SHA-256:
`931ebada2bccba44fa2644d090b0a9f4622b2cc218f2954fec51d2308cc015bb`;
receipts in `hypotheses-sdk-compile-16986dc/`.

Five exact literals (three suite names and SPAddPlugin/SPAcquirePlugin) are absent
from the nine files pinned by AE256ResourceProfile.hpp, after verifying every
whole-file hash. This narrowly describes a lexical search. It does not inspect
all installed AE files or establish absence of suites/functions at runtime.
The bounded SDK source matches likewise do not establish an AE effect adapter.

Next discriminator: establish an AE-supplied provider for the exact required
suites, then identify an existing ordinary-effect adapter and its ownership /
publication semantics. A future suite probe needs an identified helper, fresh
host/project/image baseline, explicit potential-load scope and no AddPlugin,
AcquirePlugin, scan, startup replay or registration in that availability-only
phase. Do not manufacture adapterInfo or cast between unrelated opaque handles.

## HYP-02 — actual blocker and historical counterexample

The pinned resource chain is:
PLUGp_ScanFile callback → FLT_PLUGScanFunc → FLTp_FiltSetup →
PLUG_RegisterRoutine(PiPL,path) → post-setup → FLTp_AddEffect →
FLT_FilterRegistry::RegisterNewFilter.
See [publication review](C1_EFFECT_PUBLICATION_REVIEW_2026-10-02.md),
[entry/lifetime](C1_ENTRY_LIFETIME_BATCH_2026-10-03.md),
[provider/isolation](C1_PROVIDER_ISOLATION_BATCH_2026-10-03.md) and
[consumers/failure](C1_REGISTRY_CONSUMERS_BATCH_2026-10-03.md).

Choosing one file does not isolate PLUG_Search's sack-wide cleanup. Individual
locks, idle hooks, zero active count and thread-local project scopes do not prove
a continuous exclusion window for registry readers, escaped owners, later
dispatch and MFR. Preference failure can occur after publication; local unwinding
does not prove an inverse registration. Private unload/teardown is not recovery.

The [historical pair](REGISTRATION_PAIR_RESULT_2026-09-29.md) recorded a late
dynamic-fixture registry delta in one AE process, while its PiPL-only sibling
remained absent. Overall pair acceptance was **FAIL** because the fixture had an
incomplete effect lifecycle and an observed parameter-count error. A later
[identified dynamic fixture](REGISTRATION_APPLY_PASS_2026-09-29.md) had scoped
application PASS on a disabled layer; render NOT RUN and full visual error
certification BLOCKED. These distinct sources/results must not be stitched into
one end-to-end PASS. Historical RSMB/PiPL-only late failures remain unchanged.

Thus an absolute hypothesis that AE can never admit any late effect is not
supported by existing observations. A general safe loader for an arbitrary
ordinary effect remains unproven. New invocation needs the actual receiver /
provider, admission/drain guarantee and completion/error contract; the current
offline findings supply none of those live receipts.

## HYP-03 — new reproducible owned-process execution

`tests/test_shell_native_transaction.py` compiles the current shell source and
eight owned C++ fixture libraries. No Adobe or Rust implementation is loaded.
The private shell copy changes only three routing expressions: shared log path,
HOME lookup to a task-specific variable, and TMPDIR lookup to a task-specific
variable. Exact replacement counts and reverse reconstruction of original source
are asserted. User HOME/TMPDIR and shared Loader logs are not changed.
Original wrapper SHA-256:
`2735956536f79937c96c887a8bb189f6e8345e2f072910ad2ee83cbba4d0233d`.

Fifteen labelled transaction checks execute actual shell logic:

- Bundled runtime establishes the baseline before incompatible external code;
  bundled repeat returns unchanged.
- A→B changes the actual dispatched implementation; repeat B is unchanged.
- Wrong protocol, state, key, runtime and missing ABI exports are refused, with
  the previous implementation still dispatched.
- Malformed executable is refused without replacing the implementation.
- Reentrant reload from an active EffectMain call returns busy without mapping
  the candidate; a concurrent held native call also returns busy promptly without
  mapping it. A real worker handshake uses fixture-owned atomic state.
- After that worker returns, B→C dispatch succeeds and the content-derived
  generation changes; deleting the owned candidate returns to bundled A, repeat
  rollback is unchanged, and the old owned generation remains retained.

This is one aggregate Python test, not fifteen additional Python tests. The
fixture returns an integer through the dispatch ABI; it does not render a frame,
exercise Rust persistent state, validate an AE parameter schema or publish a new
host effect. Historical [live shell evidence](SHELL_LIVE_TEST.md) stays separate.
ABI/state/identity restrictions remain necessary. An arbitrary third-party
EffectMain library without this explicit protocol is not a supported candidate.

## HYP-05 — combinations and the missing bridge

| Combination | Useful role / feasibility | Missing proof or product implication |
|---|---|---|
| PICA + single-effect publication | PICA could provide load/access/context, then an AE adapter could publish the ordinary effect | Must prove actual AE suite/provider and adapter linkage into FLT, ownership/lifetime, exclusion and complete failure semantics; avoid publishing twice if the adapter already registers |
| Single-effect publication + shell | Register a new stable shell once, then swap compatible implementations | Registering that shell during this AE session still has the same unresolved C1 contracts; preinstalling it at normal startup narrows the product |
| PICA + shell | PICA could potentially acquire a compatible implementation for an already registered shell | Explicit implementation ABI/state/runtime/key still required; current shell already loads compatible code directly, so PICA adds no demonstrated benefit for that route |
| All three | Initial host admission/registration and later implementation updates can be separated | Adding mechanisms does not produce an admission barrier or a safe ownership conversion; no executable combined adapter is justified yet |

Most useful same-goal research candidate is **PICA + the ordinary-effect adapter /
publication path**. Its first discriminating question is suite/provider and
adapter availability, not a new broad rescan. A stable shell is a separately
verified update mechanism for compatible own effects; adopting it as the entire
product needs an explicit scope decision. An opaque PICA reference, private
descriptor and shell protocol cannot be joined by guessed pointer casts.

## Closeout and retained acceptance

Code/test source **65edce84340fd919e738be65100a8ea73d1c2c31**.
Full available local regression: **383 Python/no skips, 62 Node, 22 stages PASS**.
The new fifteen shell transaction checks count as one aggregate Python test.
Independent archive/source/log verification: 25 members, 309 tracked files,
CRC/complete hash inventory/source unchanged PASS. Private archive
`AEHL-checks-dz_04_xh.zip`, SHA-256
`de171f3e1db08dbfb908b974bc5723cb3db25e718e726f31a491c2611c218054`;
verification receipt `hypotheses-independent-65edce8.json`, SHA-256
`7321f18c27f1034e4ec38c87cce4d665751d3ab0e54b122423840f05e98713ee`.
The first verifier assumed TAP output; it was corrected to the observed Node
spec formatter without rerunning or relabelling the product tests.

Bounded static audit at clean 65edce8: all nine selected checks completed,
1538 inventoried / 1089 unsupported files, no omissions, four workflows scanned.
Raw exit **1 / review_required** retained. Sole finding is the previously reviewed
`vibe.no_ratelimit_auth` at tools/artifact_manifest.py:71: local argparse CLI,
not an HTTP authentication route. No suppression or false green exit added.
Private report `hypotheses-audit-65edce8.json`, SHA-256
`3c84ac425db40f6aacf9288a8b1e1aed070ae5a1cf307932a5988411895686a3`.
Source/scope review receipt `hypotheses-review-65edce8.json`, SHA-256
`8dcdedd54fa353a6e72de841a2e4ed89b41f011caef4aa5752104e2adf68a067`.
[Research CI 37121857027](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37121857027)
completed/success at exact 65edce8, with native-syntax and panel-contract jobs
successful. [macOS CI 37121857015](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37121857015)
also completed/success at the same exact source, including build/ABI smoke/package
roundtrip. CI does not run AE. Private CI receipt
`hypotheses-ci-65edce8.json`, SHA-256 `99308e172cfc57a492521b176fe41c3738991085f96ea6a7798bd83a2cb72552`.
SDK/hash/unchanged-native-field verification receipt `hypotheses-fields-65edce8.json`,
SHA-256 `53b08e3dec465189e1a36d6a714000fcea568a972396cd0ecfc20f5f942a1089`.

HYP-01 SDK/file checks complete but runtime mechanism unverified; HYP-02
reconciliation complete but native call BLOCKED; HYP-03 owned-process check PASS;
HYP-05 combinations assessed, with no justified executable combined adapter.
The investigation does not satisfy original registration/apply/render acceptance.
Documentation-only closeout is distinct from the code/test source above.
README's stale v6.2 and pending diagnostic statements are corrected to current
v8/C1 state. No acceptance is weakened: new late ordinary-effect registration,
apply, render, A/B integration, D hardening/compatibility and release remain open.
Cleanup assessed: only owned disposable test directories may be removed by the
test; historical SDK/native evidence, installed helpers, third-party plug-ins and
unknown materials remain preserved. No merge, release or installable handoff.
