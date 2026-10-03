# C1 provider construction, isolation and publication — combined batch

Stage C1 / Development; starting clean source
`0476ea886419e2a22fe310d8c380d2eeed6f8109`. Adopted rules v6.2.0,
`d966078a9e45fee7ec9ad14f211a9da753d64b8a`. AI_ENTRYPOINT routes PROCESS
API-SOURCE-001, SAFE-001, regression/evidence; ENGINEERING debugging and
compatibility; NATIVE ownership/threading; TOOLS bounded diagnostics. File-only
collector work is Standard; dependent private host integration is Critical /
BLOCKED. Existing product scope, research branch and preserved host remain.

## Acceptance fixed before body review

- ISO-001: review complete pinned provider construction and descriptor/class-reference
  bodies; resolve serialized virtual-slot correspondence without claiming live identity.
- ISO-002: review bounded dispatch guard/counter paths and publication completion;
  separate local locks/counters from a demonstrated host-wide exclusive window.
- ISO-003: bind separately reviewed provider, isolation and completion contracts to
  the unbound transaction plan/approval/journal. Missing or retargeted contracts
  must refuse before any claim or private call; synthetic tests are not native proof.
- ISO-004: add bounded file-only collection/refusal regression; independently verify
  raw bytes and package/source identity; run full exact-source regression and CI,
  update canonical status and assess whether a new live packet is justified.

## Authority and baseline

Repository edits, owned offline fixtures, pinned file inspection and push to the
existing research branch are authorized. Prior live diagnostic authority was
consumed. No install, AE launch/attach, process-state read, scan, provider call,
private teardown, merge or release is part of this batch. Real registration,
apply/render and release remain NOT RUN/open; backend NOT READY.

Previous code evidence: `50e93973309fbff0b65e37b7c6cbb26e4b9422ad`,
372 Python / 62 Node / 22 local stages PASS and both exact-source CI workflows
success. This is the baseline, not evidence for new changes.

## File findings and remaining boundary

Sixteen complete bodies/thunks, **884 instructions / 293 anchors**, from
exact existing PLUG/PluginSupport/FLT pins. Six narrowly selected serialized
slots are collected separately; no complete C++ layout or runtime instance is asserted.

| File path | Complete bounds | Finding |
| --- | --- | --- |
| PluginSupport complete constructor | `4bb34–4bbd0` | Installs address point `ab538`, secondary base `+1d0`; module pair `+128/+130` starts empty. C1 is not a substitute for C2/VTT construction. |
| PLUG provider allocation | `e040–e1dc` | One shared allocation; provider starts at control block `+18`; PluginImpl C2 is called with VTT; final derived table address point `14a38` installed. |
| PLUG class-reference factory | `cc9c–cd74` | Watches the adjusted UnknownBase; returns interface pointer plus owning shared control, not just a raw plugin pointer. |
| PLUG QueryMap bodies | `e274–e304`, `e494–e558` | Exact ML::PluginImpl/IPlugin/Plugin name selection; absent names return zero. These file mappings do not prove a live queried interface. |
| PLUG descriptor constructors | `c9b4–cc9c`, `cd78–d030` | Path constructor creates provider; incoming constructor retains its supplied shared owner, queries implementation and stores raw interface `+48` with owner pair `+50/+58`. Null/error branches remain part of the bodies. |
| PLUG final shared owner / destructor | `e24c–e258`, `e304–e348` | Last-owner callback jumps through provider destructor slot; destructor calls PluginImpl then UnknownBase and releases weak state. Descriptor teardown already releases the owner; no registry rollback follows from that. |
| FLT global dispatch count | `5e1d4–5e1e4`, `5e1e4–5e1f4` | Atomic increments/decrements at **receiver `+bc`**. The name “Global” is not a process-wide counter or registry lock. |
| FLT guard callbacks/destructor | `9af34–9af3c`, `9b1ac–9b1d0`, `98ce0–98d44` | Guard zero decrements that FCSpec counter; guard one decrements the sequence counter via ordinary load/store; ScopeGuard invokes its function and destroys it. No reviewed callback acquires publication isolation. |
| FLT effect-lock creation | `98c80–98ce0` | Thread-safe-rendering flag selects **no effect lock**; otherwise allocates an FLT_EffectLock. This is not a host-wide registration barrier. |
| FLT post-setup | `9284c–92ab8` | Retains descriptor temporarily; optional virtual preparation; missing descriptor marks name/flags; category mutation and unwind. Successful return is not independent registry/application/render completion. |

Derived PLUG table address point `14a38`: Load slot `+20` at `14a58`
binds PluginSupport `PluginImpl::Load`; entry slot `+68` at `14aa0` binds
`PluginImpl::GetEntryPoint`. Shared-owner final slot `149d0` rebases to `e24c`;
the derived destructor slot `14a38` rebases to `e304`. PluginSupport address point `ab538` has those same
slots rebased to `4c440` / `4c568`. File construction → owner → selected provider
method correspondence is now established for these exact bodies/slots. Actual
receiver/ownership in an AE process and safe callable ABI remain unobserved.

## Mandatory separately reviewed contracts

ResourcePassGate now rejects absent/malformed/retargeted receipts and independent
review flags before claim, construction or search. The exact receipt digests are
frozen with the plan, compared with the authorization scope and persisted in
claim/call-started journal records. Existing native-contract and cleanup gates
remain mandatory. This is an **unbound protective policy**, not an AE adapter.

| Receipt | Required content before any future supervisor can attest review |
| --- | --- |
| `provider_contract_sha256` | Exact artifact/image/PID-start/run context; real provider/interface/descriptor identity and owner; owner lifetime through publication and later dispatch; native object creation, exception and thread ABI. A serialized vtable match is insufficient. |
| `isolation_contract_sha256` | Demonstrated exclusive mutation window covering registry readers, dispatch and MFR workers from final fresh safety checks through completion; acquisition/release and reentrancy behavior. Main thread, blank project, idle UI and FCSpec counter zero alone are insufficient. |
| `completion_contract_sha256` | Exact publication route and completion point; fresh exact registry delta; every partial-failure boundary, retained-state evidence and stop/preserve handling. No retry, guessed inverse or unverified private teardown. Apply/render remain separate gates. |

A SHA string or synthetic flag does not verify these requirements. A separately
reviewed supervisor must check receipt bytes and their context; no such native
adapter or real receipts are supplied. Existing approvals lack these fields and
fail closed. This change renews no authority.

## Regression and packet decision

Behavioral red check after adding only data fields: the first missing-provider
case failed because the old policy still allowed the synthetic search. Final
focused checks: collector 36 tests; transaction model 94 refusal/operation cases;
real-files/process journal 35 cases, with all three receipt-retarget attempts
preserving the original claim and stopping the marker/search. Full clean-source
regression: **376 Python/no skips, 62 Node, all 22 available stages PASS** at
clean code/test source `56be72b888652da450dc58c0d83c64187218af95`.
[Research CI 37118807823](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37118807823)
and [macOS CI 37118807775](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37118807775)
both **completed/success** at exact 56be72b. CI build/ABI smoke/package checks do
not run AE or establish ordinary-effect registration.
Full AE pipeline remains BLOCKED; product package and live operations NOT RUN.

Independent original Mach-O verification: all **10** clean-source mode archives
PASS (member inventory, CRC, every SHA-256, source and complete instruction
coverage). New mode: **105 direct / 24 indirect** branch encodings, six original
serialized words and fixup-chain membership, four rebase targets and two import
ordinal/library/name resolutions PASS. This verifier reads original bytes and
import/name tables, independent of collector validators and dyld_info labels.
Earlier entry mode retains 264 direct / 22 indirect / 29 rebases PASS.

| Exact-source evidence | Identity |
| --- | --- |
| New collector archive, 53 members | `build-ae-hot-loader/resource-provider-isolation-3f834b3e-lrpf34lp.zip`; SHA-256 `c65efb7d71c874d12f2ff2893f977abff6a3ef0efe5c1cd8a2aa0ec1407f337e` |
| Full local regression archive, 25 members / 304 tracked file hashes | `/private/var/folders/bs/39klz7cd52z6xkm817vj0zjm0000gn/T/AEHL-checks-c14udi_m.zip`; SHA-256 `81e2455b9cfdb8b8c831a6238e60962936904efb0a3bafec9c01a3cf69402ec2` |
| Independent collector receipt | `../private-live/isolation-independent-56be72b.json`; SHA-256 `2baff6e9b8e512cac210042c28b2b84ee4636ee45272c0ab653e15bee43fe035` |
| Independent local regression receipt | `../private-live/isolation-local-independent-56be72b.json`; SHA-256 `bb698abba4932f968768dcca7248db4f60bc3f927400a27379f876e7e7a61016` |
| Static review, raw exit 1 / review_required | `../private-live/isolation-audit-56be72b.json`; SHA-256 `f8e4618cfb7243c5b2663bde2a03880d880dac5b4656db291f4f154b99ea10d8` |

Static scope: 793 bounded text files, no omissions, 520 unsupported files;
all selected checks completed including four workflows. The sole heuristic
`vibe.no_ratelimit_auth` at `tools/artifact_manifest.py:71` was reviewed again:
local argparse mode selection, no HTTP authentication route. Retain raw finding;
not a security certification. History, runtime, dependency vulnerabilities and
other omitted assessments are not PASS. Private evidence is not committed as a
redistributable Adobe binary dump. The independent helper initially selected the
previous archive list and correctly rejected its old source; selection was fixed,
then all ten current-source archives passed. Original receipts were preserved.

**No executable live packet justified.** File ownership correspondence is narrower
and stronger; host-wide isolation and native completion/failure semantics remain
NOT PROVEN. Historical retained general-plugin records still block an unchanged
resource scan. Backend NOT READY; registration/apply/render/release remain open.

Next concrete offline targets: caller of the resource pass and registry reader /
writer synchronization, including MFR/reentrancy; trace actual publication end
and the effect-registry insertion versus parameter/canonical mutations. Only
then reassess a distinct isolated adapter and exact operation packet. Never
attempt a private call to substitute for missing safety proof.


Private evidence identity: `../private-live/verify_provider_isolation_20261003.py`; SHA-256 `d6d740a04ec0445bb3e0c556f023e865068aa41c33be2f215428677833aefd86`.

Private evidence identity: `../private-live/verify_isolation_local_20261003.py`; SHA-256 `d1e90ec8d0fd295068e3b6b7e9886adeb37ce148626acc502d3de48b741ed26b`.

Private evidence identity: `../private-live/isolation-collection-56be72b.json`; SHA-256 `9b6bcb107b35a514368182ad33a8a5155fd5536d7fe5a000bed760aefcd27dd5`.

Final exact-source CI receipt: `../private-live/isolation-ci-56be72b-final.json`; SHA-256 `105d5055d6eb26d2d2f17bd9dd0ec379f5c514477a3341f52b78f99f97d89bb1`.

## Closeout

ISO-001/002: PASS for the defined bounded file review; runtime identity and
host-wide isolation/completion remain explicitly NOT PROVEN. ISO-003: PASS for
unbound refusal/scope/journal behavior, with 15 added gate/journal scenarios.
ISO-004: PASS for available exact-source local/CI/evidence verification and
canonical documentation; packet assessment is BLOCKED on the stated missing
native contracts. No criterion asserts a real registration or native safety PASS.
Only documentation changed after this code/test source; the closeout commit
uses `[skip ci]`. The exact green CI identity remains 56be72b, not that later
source identity. Original baseline and private receipts are preserved.
