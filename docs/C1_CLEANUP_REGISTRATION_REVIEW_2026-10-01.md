# Stage C1: cleanup registration and retained-state review

Date: 2026-10-01. Code/test source:
`bf8a2cca9345df62e50bb69c144f9a2bbc93f34a`.
Continues [the search ABI review](C1_RESOURCE_ABI_REVIEW_2026-10-01.md).
Stage C1 remains offline preparation; ordinary-effect late registration is not
fixed. C0's recorded live PASS is unchanged.

## Applicable rules and acceptance

AI_ENTRYPOINT was consulted first; canonical AE-Development-Rules source was
refreshed to `f17c056b292631a0832b894050e204a3ca7bc2dd`. Existing product scope
is sufficient: no new discovery interview or reference audit applies.
PROCESS (baseline, Git, identity, regression and evidence), ENGINEERING,
DEBUGGING_PROTOCOL, NATIVE, TOOLS and WORKFLOW controlled initiative apply.
The collector change is Standard/Development; possible private host integration
remains Critical/Development. This is neither a Validation delivery nor an RC.
The refreshed PROCESS section 9 requires full Level 2 for RC; internal
milestones select it by risk and agreed acceptance. No release gate is claimed.

Acceptance for this block: reproducible bounded registration/cleanup evidence,
exact decoded coverage, matching input hashes before/after, retained-state
interpretation with explicit limits, existing search-mode compatibility, owned
LLDB regression, clean-source unified regression and exact-code CI.
No new AE launch, debugger attachment, installation, script, provider retention,
private call, scan, callback replacement, teardown or startup replay is included.

## Reproducible file-only collection

The existing collector now accepts `--review cleanup`; its default remains
`search-abi`. It keeps hash-pinned inputs, no-dependent-image LLDB targets,
disabled initialization scripts, fixed windows of at most 4096 bytes, complete
address/decode validation and exclusive private evidence packaging.
New tests reject duplicate labels, escaping labels, unknown images/scopes and
oversized windows, and check cleanup symbol selection separately from search.

```sh
python3 experiments/ordinary_discovery/collect_resource_search_abi.py --review cleanup
python3 experiments/ordinary_discovery/collect_resource_search_abi.py
```

| Pinned input | SHA-256 |
|---|---|
| PLUG.dylib | `12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22` |
| FLT.dylib | `227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256` |
| MEE.dylib | `18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344` |

| Window, end exclusive | Decoded instructions |
|---|---:|
| PLUG_InstallScan, 0x87e4–0x8a6c | 162 |
| PLUGp_DoCleanups, 0xeb20–0xec1c | 63 |
| FLT_Birth, 0xd7ac–0xdae0 | 205 |
| SetupGeneralPluginScan, 0x36c58–0x36da4 | 83 |
| PluginScanFunc, 0x36da4–0x376ec | 594 |
| PluginCleanupFunc, 0x376ec–0x37a00 | 197 |
| CleanupGeneralPluginScan, 0x37eec–0x37f34 | 18 |
| SetdownGeneralPlugins, 0x37f34–0x38044 | 68 |
| Total | **1390** |

All three original inputs matched before and after collection. Eight complete
windows passed; Adobe calls = 0. Private collector ZIP
`resource-cleanup-374a685e-zxea74ac.zip`, SHA-256
`04d65dc92032efa19848138cfc9932c49ee467e431d45e2b828cdf7bb9722915`.
The default search review also passed again, 105 + 367 instructions, ZIP
`resource-abi-9deb9d91-k15dwmmy.zip`, SHA-256
`ee8f29608bbf1f27cb25b32725127f157d02e9262fa29c3f0c74d1fd5f0ae823`.
These are private transcripts, not distributable Adobe binaries or runtime
addresses. No original payload or raw disassembly is added to Git.

## Registration mapping

PLUG_InstallScan takes sack**, short type count, int* type keys, scan function,
cleanup function and shared context. Its fifth argument x4 is retained in x20;
the sixth x5 is retained in x19. At 0x89fc–0x8a14, a non-null cleanup target and
that context are inserted as a pair into sack+0x10. A null fifth argument skips
that insertion. Scan registration uses a separate sack+0x08 list. A null sack
argument selects the default sack. No custom-sack safety is inferred.

FLT_Birth's normal registration call at 0xd9c4 supplies FLT_PLUGScanFunc as x3,
**null x4**, and its FLT context as x5. This call registers a scanner, not a
cleanup callback. It does not establish a filter-loading notification route.

MEE SetupGeneralPluginScan's call at 0x36d34 supplies PluginScanFunc as x3,
PluginCleanupFunc (0x376ec) as x4 and null x5 to the default sack. Its second call
at 0x36d60 installs AEgx_PluginScanFunc with null cleanup/context. Thus there is
a concrete startup registration source for the general-plugin cleanup target.
These are static caller arguments; the actual running sack and all its current
records have not been observed.

PLUGp_DoCleanups reads sack+0x10 and invokes the saved target/context pairs,
passing through progress/context. There is no root argument or root predicate.
Null progress takes a separate loop that still invokes the cleanup targets.
Both loops **stop on a nonzero cleanup return**; eligible installed records are
not proof that every callback runs on every pass. This refines the earlier
review's shorthand about iterating the installed list.

## Retained state and end-of-pass effects

PluginScanFunc reads the shared GeneralPlugin vector, checks candidate names,
and can call PLUG_RegisterRoutine at 0x37108. The successful record path copies
a shared routine descriptor, increments its shared reference count and appends
a GeneralPlugin record (0x371ec–0x3726c, 0x37308–0x3731c). The typed slow-path
append corroborates the vector interpretation. This is general-plugin state,
not ordinary-effect registry publication.

PluginCleanupFunc reads the same global vector begin/end at 0x37724–0x37730
and advances by 0xb0 bytes per record. It receives no search-root limit and
does not test a per-pass membership marker in this body. On each eligible
record it calls PLUG_PrepRoutine at 0x3779c. A nonzero result skips the remaining
work for that record. On zero it sets record+0xa8, reads a saved routine entry
at descriptor+0x08, creates a FILE specification and can invoke that entry
at 0x37800 with operation 3 and the record's state block. Failure branches zero
state fields; normal/handled branches dispose the owned FILE specification.
The special-name branch can transfer a stored pointer into a MEE global.
Null progress removes progress calls, not these preparation/entrypoint actions.

Neither PluginCleanupFunc nor CleanupGeneralPluginScan empties the vector.
The latter iterates saved record+0x80 callbacks and invokes them with
record+0x10. Its name alone must not be interpreted as releasing scan state.
SetdownGeneralPlugins separately invokes record+0x58 callbacks, checks and
clears +0xa8, calls PLUG_UnprepRoutine, releases retained records and resets
the vector end. It is a teardown path, not an authorized way to isolate C1.
SetupGeneralPluginScan also releases existing records before registration;
replaying it would destroy retained state and is outside the experiment.

Consequently, **one root bounds enumeration, but does not bound all callback
effects to that root**. This is a conditional static interpretation, not proof
that PLUG_PrepRoutine succeeds twice, a third-party entrypoint is invoked again,
or the running vector is nonempty. Those outcomes remain unobserved.

## Verification and remaining gate

| Check | Result |
|---|---|
| Collector unit/regression suite | PASS, 8 cases, including real LLDB on owned arm64 code |
| Cleanup collection and input identity | PASS, 1390 decoded instructions, eight windows |
| Default search collection compatibility | PASS, 472 decoded instructions |
| Unified clean-head local macOS regression | PASS, 266 Python tests, no skips; 62 Node tests; 22 stages |
| Tracked source inventory before/after | PASS, exact clean bf8a2cc, unchanged |
| Exact-code research CI | PASS, [run 36922542782](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36922542782), Linux + macOS |
| Exact-code full macOS CI | PASS, [run 36922542905](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36922542905), build/sign/package/synthetic smoke, no live AE |
| Actual running sack/vector/callback identity | NOT OBSERVED |
| Native C1 registration/apply/render | NOT RUN |

Unified local ZIP `AEHL-checks-thwt2du9.zip`, SHA-256
`16eac5a157f270387d592b6208978e725c4c0b664c4bdd462ed96861c4fd3a90`.
Nested native cases are included in the Python count, not counted twice.
Independent ZIP manifest/payload verification and **27 addressed structural
assertions** passed. The private review JSON SHA-256 is
`e85e75d1ad160df40d00e5228429860cc0bf8347c2d80e327d25633f2f8d3572`.
These assertions check saved instruction text; they are not additional unit
tests or executed Adobe branches.
The bounded static code scan inspected 178 supported files on the clean code
head, then 198 files with staged documentation (dirty source explicitly
recorded), including four workflows, with no inventory omissions. Its sole
candidate remains the classified local argparse false positive in
artifact_manifest.py:71; nothing was suppressed.
This scanner is not a full security audit or release certification.

Next safe discriminator: review PLUG_PrepRoutine's repeated-preparation/error
contract and the caller's expected general-plugin lifecycle; determine what
read-only baseline could establish current callback/state eligibility without
altering it. Freeze the native contract only after those effects are bounded.
Do not skip/replace cleanup, forge a sack, replay setup, invoke setdown or
assume idempotence from names. No native C1 backend or live candidate is ready.
Fresh live approval belongs to a later concrete, reviewed candidate.
