# C1 host metadata bridge — bounded file research

Development, Stage C1. Starting clean source e56ef1ea15269478c7f1f4d72f4180f7ae083d12;
rules v8.0.0, 132b7cd32873ba7328e3128ffbb33e1929b74d45. AI_ENTRYPOINT routing and
BRIDGE-01–08 acceptance are in [production plan](PRODUCTION_PLAN.md). Original
arbitrary ordinary-effect/no-restart goal and A/B/C1/C2/D/release obligations remain.
Collector/owned SDK controls are Standard; private invocation remains Critical/gated.
No AE launch, attach, process read, installation, scan, registration or unload.

## Findings and hypothesis reconciliation

The [actual PICA inventory](PICA_INVENTORY_REVIEW_2026-10-03.md) contains two AE.app
records, while known ordinary-effect matches are registered and their files are
NOT_LISTED. This does not establish a public AddPlugin bridge; indirect host/proxy
roles remain unknown. The earlier dynamic fixture registration delta and PiPL-only
late failure remain separate receipts: overall historical registration pair FAIL,
scoped later apply PASS, render/full lifecycle certification not established.
See [combined hypotheses](HYPOTHESES_REVIEW_2026-10-03.md). Do not combine them
into an end-to-end PASS or a proof that arbitrary hot registration is impossible.

New fixed PluginSupport review binds the complete Callback2, Callback1 wrapper,
GetPFPluginData, PFPluginDataToPiPL, GetPiPLs and PF_PluginData destructor bodies:
**6 windows / 744 instructions**. Existing exact file pin, no new native profile:
SHA-256 `4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`,
UUID `64C01AC4-2413-3463-8822-17EE5543052A`, AE 25.6x101 arm64 only.
Unslid addresses in the collector are file evidence, never runtime function pointers.

- Callback2 copies mandatory name/match/category/entry strings, accepts optional
  support URL, builds a 0x38-byte metadata record and appends it to its supplied
  vector. Normal return 0 follows append and temporary-record destruction; caught
  exceptions return 1. Late failure atomicity is not established. A successful
  callback return alone does not demonstrate ordinary-registry insertion. This
  complete body has no direct ordinary-registry call; transitive helpers/release
  targets are not fully reviewed and their side effects remain unknown.
- Callback1 delegates to Callback2 with a null support URL. GetPFPluginData resolves
  the version-2 entry, then version-1 fallback, calls it with the supplied context,
  actual Basic Suite and app/version values; absence of both returns 3. Virtual
  receiver/entry identity and loader lifetime remain unobserved, not callable ABI.
- PFPluginDataToPiPL creates/populates PiPL class references from each metadata
  record and appends interface references to its output vector. Hidden-return and
  virtual calls/reference-release paths are not a C registration contract. No
  direct ordinary-registry insertion appears in this body; transitive publication
  effects remain unknown.
- **On the reviewed uncached GetPiPLs path, the opaque PluginData context is a
  stack-local vector.** The caller initializes it, passes its address to
  GetPFPluginData, converts only a zero result, then destroys every metadata record
  and recycles storage before returning. Exceptional exit also invokes the
  PF_PluginData destructor. A retained context is invalid after that call ends;
  callback replay is NO-GO. This is a concrete lifetime boundary, not a guessed
  long-lived registry handle. Cached PiPL and fallback virtual-provider paths
  remain distinct; no actual runtime receiver was identified.

Actual primary SDK 25.6_61: Headers/AE_PluginData.h opaque pointer/Callback2 and
PluginDataEntryFunction2 declarations; Util/entry.h PF_REGISTER_EFFECT[_EXT2]
macros forward the same pointer, effect kind, API versions and metadata to the
provided callback. These declarations do not grant later context reuse or a
publication transaction. Skeleton uses the immediate host entry callback pattern.
Proprietary headers/disassembly/binaries remain private.

Resource scan/publication is still the candidate chain from PiPL/path through
PLUG_RegisterRoutine, FLTp_AddEffect and RegisterNewFilter. Shared cleanup,
all-reader/MFR exclusion, actual receiver/thread/lifetime, completion and failure
rollback remain open; temporary metadata does not remove those blockers. Stable
owned-shell switching remains a narrower fallback with its existing owned tests;
it cannot satisfy arbitrary third-party registration by itself. No scope adoption.

## Implementation and prepared checks

New `--review plugin-metadata` mode retains clean-source/input checks, exact
coverage, bounded file-only tools and exclusive archive/hash validation. Structural
anchors bind copy/dispatch/conversion/normal and exceptional teardown. Reports
explicitly retain unknown publication/receiver/lease/rollback and NOT RUN live work.
Three new parser/refusal tests cover fixed scope, missing/duplicate/undecoded rows,
changed targets/operands and unreviewed bounds; synthetic controls are not AE proof.
TDD baseline: 3 expected errors before mode implementation; afterwards all **45**
collector tests PASS, including actual owned arm64 LLDB file controls.

`PluginMetadataContract.cpp` uses actual SDK types with compile-time assertions,
and actual macros with owned callbacks. It checks pointer identity/metadata and
success/error forwarding across v1/v2; no fabricated Adobe object dereference and
no Adobe code loading. Preliminary actual-SDK arm64 compile/owned execution PASS.
Clean-source receipts, independent file/archive review, full regression/scanner
and exact-source CI are pending this prepared checkpoint; older CI is not reused.
Private preliminary bodies: build-ae-hot-loader/bridge-preliminary-kww12gpr,
explicit dirty/preliminary scope only.

## Acceptance and next gate

BRIDGE-01 reconciliation complete. BRIDGE-02 bounded route review complete, but
acceptance of a usable ordinary-registry bridge remains BLOCKED. BRIDGE-03 context
lifetime boundary established; full invocation contract remains BLOCKED.
BRIDGE-04 minimal host experiment BLOCKED on mechanism/ownership/publication.
BRIDGE-05 research-tool checks prepared; host-experiment tests NOT RUN.
BRIDGE-06 clean-source checks/CI/doc closeout pending.
BRIDGE-07/08 live run/interpretation NOT RUN, dependent on a confirmed safe bridge
and a concrete new live scope. No permission question is needed for a guessed call.
Backend NOT READY; no merge/release readiness or completion percentage claimed.

Next: trace the copied PiPL/path handoff to the actual effect publication owner and
establish the host admission/drain/completion/rollback contract. Saving this
metadata callback/context or retrying unchanged PICA cannot meet that gate.
Cleanup preserves SDK, third-party plugins/projects, previous consumed helper and
session, historical evidence. Current owned controls/private receipts are retained
for reproducibility; no loaded-file deletion, shared cleanup or forced termination.

## Clean-source verification closeout

Code/test source **9e35d1ea5820cbf239b787b00a346f35c49a47bb**, clean before and after
collection/checks. Actual collection: **6 windows / 744 instructions / 139 anchors**,
all exact PluginSupport input hashes unchanged. Independent verification checks
15-member ZIP uniqueness/CRC/every payload digest, exact source and scope fields,
full instruction coverage and original arm64 Mach-O bytes: **109 direct B/BL,
67 conditional branches, 23 indirect BR/BLR and 8 returns** agree with transcripts.
This verifies file correspondence, not transitive side effects or live execution.

Local unified runner: **421 Python, no skips / 62 Node / 22 stages PASS**, 332 tracked
files bound to the exact clean source. Independent ZIP/source-byte checks PASS.
The 27 nested native policy cases remain one Python test, not added to its count.
An initial shortened expected-SHA argument was rejected before any check; the
accepted run used the full SHA. No timeout extension or weakened check.

Actual SDK owned contract: C++17 arm64 `-Werror` compile and **4** owned callback
cases PASS. Six SDK headers + owned source + selected OS SDKSettings.json pinned
before/after (8 inputs). SDK declaration hashes: AE_PluginData.h
`25be4a7620bc1c8fbcde7828304e9a207e9cabd0aaf3060f12c4e15c71ff52ca`, entry.h
`2ae54d29d4bd28fc55585d7b36dd7bf93046352648bfdb9c10eca0f9905669d4`.
Owned binary SHA-256 `14d18a8a0914def66b7b8711f8c8b307d53fca937cd2375bd1216bbabd97ad35`.
Dependency inventory initially refused the unlisted OS SDK settings input;
explicitly pinning that selected settings file allowed the clean control receipt.
No SDK modification, stub header or Adobe execution. CI does not have this local
Adobe SDK control; its own checks remain separately scoped.

Static scanner raw exit **1**, `review_required`: sole known
`vibe.no_ratelimit_auth`, tools/artifact_manifest.py:71. Independent source review
confirms local argparse create/verify modes, no network request handler/auth route;
false positive retained with raw evidence, not suppressed or relabelled exit 0.
Separate code review checked fixed-mode bounds, exact image/provider pin, full
coverage/call operand refusals, clean source enforcement, archive integrity and
report unknowns. No native invocation/profile/gate or product scope changed.

Private receipt locators (not published; no SDK/disassembly/binary in Git):

| Receipt | SHA-256 |
|---|---|
| build-ae-hot-loader/resource-plugin-metadata-54cac067-xazeta5_.zip | 437ff6db106adb177217b386495a710fede1393d6febd6fc1a2412f646db21da |
| same folder / independent-review.json | ff5a9d577fda84bfb4897da4a122674f40a4839419199879d5152f397ee91fce |
| same folder / owned-sdk-contract.json | faa7b120b5bee77286dfcc1313db643912308501117b754239ffdd958e8575d6 |
| /private/tmp/AEHL-checks-0zzr6fs5.zip | bc92cc14a4df31d159ab7809365266bd2be045f98063b51ed0d5f0b1bf697a03 |
| /private/tmp/aehl-metadata-regression-independent.json | 1d3d5e29d7768f5e482ac407ed38f79ed350a3b9b0fba3bfba739588af9629e6 |
| /private/tmp/aehl-plugin-metadata-9e35d1e-audit.json | bcf4d4b6102298339cc08631e288590170fa4a67ff6c43461d8fa6b484fa9935 |

Exact-source [research CI 37126661037](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37126661037)
completed/success; [macOS CI 37126661063](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37126661063)
completed/success, both at exact 9e35d1e. All research jobs and macOS build
completed/success; native package/owned smoke tests are not live AE certification.
The following records supersede preparation statements above; historical receipts
remain unchanged. No live operation in this pass, no merge or release.

| Requirement | Final research status | Outstanding acceptance |
|---|---|---|
| BRIDGE-01 | PASS: hypotheses reconciled | Separate old runtime/lifecycle scopes retained |
| BRIDGE-02 | File research PASS; usable bridge BLOCKED | No ordinary-registry publication contract identified |
| BRIDGE-03 | SDK/context boundary PASS; invocation contract BLOCKED | Actual owner/admission/drain/completion/failure/rollback |
| BRIDGE-04 | BLOCKED, executable host experiment NOT RUN | Mechanism/safety prerequisite remains absent |
| BRIDGE-05 | Research tooling/local SDK checks PASS; host experiment tests NOT RUN | Depends on 04 |
| BRIDGE-06 | PASS: local checks/review/docs and both exact-source CI completed/success | Runtime/release gates remain independently open |
| BRIDGE-07 | NOT RUN | Depends on 04 and concrete new live scope |
| BRIDGE-08 | NOT RUN for live result; file interpretation complete | Depends on 07 |

This is not eight successful host steps. It eliminates unsafe callback replay and
narrows the missing handoff to the publication owner, while the original product
remains unimplemented at that boundary. No further unconditional live action is
justified. Next pass should establish that handoff and its transaction contract.
