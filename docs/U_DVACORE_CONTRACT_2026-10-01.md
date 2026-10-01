# Stage C: U/dvacore contract and retained directory providers

Date: 2026-10-01. Continues `e96a1c8f31b5aad70c11400b17c1f11e9bbe4154`
on `research/ordinary-plugin-discovery`. Shared DEVELOPMENT_RULES were rechecked
unchanged at `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`; AGENTS and the Stage C
plan apply. Exact new code: **`9ea7bcf57fffee2382c6890459dca89201345395`**.

## Scope and predeclared acceptance

Verify the supplied U/dvacore files and the actual string producer/destructor;
compare their representation with the existing directory adapter; pin the exact
received binaries; resolve the provider-code lifetime gap with a separately
controlled resident-reference operation. Test that operation with owned libraries
on macOS, run the unified regressions, verify downloaded evidence and check the
independent product workflow. Do not execute Adobe code or contact the user's AE.

This is not an installation, live no-scan test, resource registration or release.
Source analysis is not runtime acceptance. No old authorization is renewed.

## Received files

`AEHL-U-dvacore.zBNsk3.zip`: 2,462,478 bytes, SHA-256
`1d617798f475602a8023763b6c3b3e7c5d53c762b255fc652886643346b878bd`.
Only the four expected entries were read into a fresh private workspace;
unexpected paths and links were rejected. Both hash statements are identical,
and their hashes for the two libraries agree with independently received bytes.
Original input hashes were checked again after analysis.

| File | Bytes | SHA-256 |
|---|---:|---|
| U.dylib | 1,372,928 | `aecabb33c5ac5948ad742848c46588398bc690411b70aae7ca3f08a919362daa` |
| dvacore.framework/Versions/A/dvacore | 7,772,464 | `cb6faaf5b745903b80b44105b658ab68186d5065ae47c8a57c9b23e26aa8ecb0` |

Both arm64 slices begin at offset 16,384. U UUID is
`3053EA7E-A176-315D-900B-9F17CC96DBE5`; dvacore UUID is
`4427999D-3DB3-3964-82F7-18DF4FA24D76`. The slice hashes are in the private review.
The previously received FILE.dylib was rehashed unchanged:
`df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864`.
These are received-file identities, not the loaded identities of any AE process.
No Adobe binary or SDK file was executed or added to Git.

## Actual producer and matching destructor

Addresses are unslid references into the identified files, not runtime addresses
accepted from a request. The existing binding still resolves exact direct exports.

U's `U_AsciiToUTF16String(char const*)` begins at 0x4a604. It retains result
storage from x8, zeroes the 24-byte object, obtains input length, reserves storage
and appends UTF-16 units. The appended byte is sign-extended before its 16-bit
mask. This is **not a UTF-8 decoder**. The existing adapter's ASCII-only input
restriction must remain; Cyrillic/non-ASCII paths are not supported by this probe.
No change to that restriction was made.

The actual U import ordinals assign reserve, push_back and the matching UTF-16
string destructor to dvacore.framework, rather than to the test executable's
standard library. A separate similarly named dvacore conversion routine is not
substituted for the path actually called by U.

The reviewed dvacore reserve/push_back bodies use tag/short length at +0x17,
long data at +0, long length at +8 and long capacity at +0x10. Short capacity is
10 UTF-16 units, with termination space. These observations agree with the
existing adapter's bounded decoder for this exact build; they do not certify
another version or authorize constructing a host string by hand.

The matching `basic_string<..., dvacore::allocator::STLAllocator<...>>` D1
destructor is at 0x2b5b5c. Short strings require no heap-buffer recycling. Long
strings call MemoryRecycler::Recycle with data and byte capacity; the destructor
does not delete the caller's result-object storage. U's exception paths invoke
that destructor for its partially constructed result before unwinding. Thus the
adapter must destroy the result only after normal producer completion.

The destructor has a terminate landing path. The recycler has pool/lazy-state
logic, not a demonstrated stateless free. This inspection does not guarantee
that every failure can be caught or that a real first call has no global effects.
Do not use the bridge's catch clauses as protection from terminate, access faults
or an incorrect private ABI. No Adobe allocator was invoked in this iteration.

Six named windows cover 529 addressed instructions: U producer, dvacore D1,
reserve, push_back, Allocate and Recycle. Coverage was checked for contiguous
requested spans. **24 targeted structural assertions passed**, including seven
BL targets independently decoded from raw instruction words. These are not unit
tests or executed Adobe branches; no exhaustive allocator audit is claimed.
LLVM 17/apple-m1 was used as a file reader. The shipped export parser also
accepted the actual U producer, dvacore destructor and four FILE exports without
executing the images. Compiled profile bytes match all three complete SHA-256s.

## Implemented profile and provider lifetime retention

`AE256DirectoryProfile.hpp` contains validated compile-time digest literals for
FILE, U and dvacore and the exact expected application location. It contains no
Adobe function address, initialization hook or call. The fixed profile is build
data, not a configurable user/IPC address list.

`ResidentDirectorySession.hpp` adds `BindRetainedOnce` and the fixed profile
factory. Raw `Bind` remains a point-in-time resolver; its logic is unchanged.
The new wrapper:

1. Requires the main thread, same process, an explicit retention-authorization
   assertion, an unused session and no DYLD_/LD_LIBRARY_PATH overrides.
2. Validates the existing resident files, exports and code bytes before changing
   reference counts. An absent image is refused, not loaded to satisfy the check.
3. Consumes its in-process attempt before acquiring up to three references with
   `RTLD_NOLOAD | RTLD_LAZY | RTLD_LOCAL`. There is no fallback load, dlsym,
   RTLD_NODELETE, plugin scan or lifecycle replay.
4. Stores each acquired handle immediately, compares image snapshots, then
   repeats the full binding under the retained references. Preliminary pointers
   are not exposed to the caller.

Apple's [dlopen manual](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/dlopen.3.html)
explicitly describes RTLD_NOLOAD handles as reference-counted without loading a
missing image. The reviewed [dyld implementation](https://github.com/apple-oss-distributions/dyld/blob/main/dyld/DyldAPIs.cpp)
has a NOLOAD early return with a reference increment before dependency loading
and initialization. This supports the OS contract, not identity of the user's
dyld version or a private Adobe ABI. No Apple implementation code was copied.

**Retention is a real reference-count change, not passive inspection.** The
wrapper intentionally retains at most three references until process exit,
including partial-acquisition failures. It never calls dlclose, since dropping
the last reference could unload host code. This is a bounded research lifetime
tradeoff, not a leak-free general-purpose library manager. A later authorized
host test must explicitly include this effect. Process exit reclaims the state;
this code must not force exit as cleanup.

The boolean parameter is only a supervisor assertion, not user-consent evidence.
The session's attempt flag is not the durable transaction journal. A future
single identified AEGP must first claim that journal, verify explicit approval
and the fresh host/project/root, then use the wrapper. Multiple independently
loaded copies or a failed prevalidation are not covered by this in-memory flag.
No AEGP entrypoint or supervisor currently invokes the new wrapper in AE.

Retained references protect the target code under dyld's reference-count
contract, assuming stable loader configuration and no hostile interposition.
They are not a lock over unrelated modules, a complete event trace of transient
image changes, or proof of Adobe thread/global-state safety. A detected change
or partial acquisition is a failure, not permission for an automatic retry.

## Checks for exact code 9ea7bcf

The existing macOS resident test was extended, rather than adding test-count
padding. Three newly compiled owned providers are first loaded by the test.
The wrapper acquires its NOLOAD references, after which the test closes all its
original references. All three images remain resident; the actual bound directory
create/roundtrip/release then succeeds. Repeat retention is refused and the
reference count remains three. Missing image, missing approval, loader override
and bad digest are also refused. No Adobe library is loaded by these tests.

| Check | Result and scope |
|---|---|
| Received hashes and source-before/source-after agreement | PASS; original files retained |
| 24 structural assertions / six named windows | PASS; file analysis only |
| Actual export parser and complete compiled digest agreement | PASS; Adobe calls=0 |
| Local parser ASan/UBSan | PASS, empty diagnostics on supplied U/core parsing; not macOS retention or host-memory coverage |
| Local unified Linux | PASS: 238 collected, 229 PASS/nine macOS-only skips; Node 62 PASS |
| Research CI 36824300893 | PASS, both unified jobs |
| Downloaded macOS unified report | 21 stages PASS; Python 238/238, Node 62, existing scoped guards 15 PASS |
| Owned resident lifetime plus directory lifecycle | PASS on macOS arm64; originals released, retained references keep providers callable; Adobe calls=0 |
| Full product macOS CI 36824300983 | PASS; all build/sign/package/smoke/archive-verification steps completed |
| Actual AE no-scan probe / registration / apply-render | NOT RUN; no entrypoint or live supervisor connected |
| Full static-security audit | NOT RUN again; five historical findings remain open |

The count remains **238 Python tests**; the retention scenario is inside an
existing test. Existing 27 directory, 63 policy and 32 journal cases remain
nested, not added again. The local runner still does not build product packages;
product CI is a separate result. No product ZIP is handed over or installed.

Local source was reconstructed from the previously verified 31868ab CI snapshot
(SHA-256 `8250760b47ac0f41ad300bea735ddea802e4940d295adb48645cf4b5b729ea90`)
plus these five files; intervening e96a1c8 was documentation-only. The local clean
identity `0d9d63bc2916dab789e8eea29d058a191c420f85` is not the upstream commit.
Git writes used the actual e96 tree as their base. Downloaded CI reports identify
9ea7bcf and match all five tested source-file hashes below.

| Source | SHA-256 |
|---|---|
| AE256DirectoryProfile.hpp | `cfbc1351715a43b0e5a60c68d68d6ab152a22b2c648930b6c4f20e692dadb0fe` |
| ResidentDirectorySession.hpp | `dbd99bdb6ff26e0ca5afdcd8d0aafc218ef2d6bb6dbac7563c8504fb72563477` |
| NativeDirectoryBinding.hpp | `e7143683e27c008398e134d2a499144978be18cf99bcbb9a79ba522e21f3bc0e` |
| resident_image_binding.cpp | `2f9d73ab6a25047f232cb14910915b12ed501037f151fb1adf826312ff024aed` |
| test_resident_image_binding.py | `4f8e03009a0318c355cd39b969e93c0108f7057eaf444d82e320063ca63b4a6f` |

## Verified evidence

Both research artifacts were downloaded. Outer hashes, all inner manifest entries,
exact source identity and five changed source hashes were independently checked.
The macOS Python log includes the actual NOLOAD-retention success record; a green
job label alone was not substituted for that test result.

| Artifact | ID / SHA-256 |
|---|---|
| macOS Actions archive | `11144247759` / `6b36035e7da972c4e50d1e31acd5c7afa9c407bd9880c7e729d9374522f6cf20` |
| macOS inner report | `f79ca40f012767ea2ec4b47580d72c8e344334e3176ed87b2660e0ae4091df77` |
| Linux Actions archive | `11144571845` / `ad6f6eb92ec0bde75d5195078717c7758600e231e1eabb4ec9d500e45e483062` |
| Linux inner report | `7d8ee442e18f09f47364ade33142b8fb2f36eb4a4faa68a46517403e049a638f` |
| Private provider-contract-review.json | `b254680058281b4dd2af0f0742702a820f1476752fbfae6795eabc4fa30d8e4d` |

The macOS report identifies macOS 15.7.9 arm64 and Python 3.14.7. The product
workflow's final step results were checked separately; its package was not
independently executed in AE. Green CI does not clear old or unreviewed warnings.
Documentation follow-ups use [skip ci]; verified code remains 9ea7bcf.

## Next boundary and preserved results

U/dvacore implementation availability is no longer the blocker. The exact file
profile and retained-binding component now exist. Next wire an identified,
inert-by-default no-scan AEGP to the existing directory adapter and durable
journal, with an external supervisor. Verify SDK build, loaded identity, refusal
paths and inert entry before proposing a separately authorized host run.
That run must require fresh blank/clean/idle state, one owned ASCII directory,
exact roundtrip and single release, unchanged PID/project/registry and no new
module loading or unloading. No current live host state has been observed here.

The later PLUG resource pass still needs end-of-pass callback/retained-state
review. It is not safe merely because one root is supplied. Do not add a broad
search, reinitialize startup, bypass the cache predicate, replace callbacks,
force notification, or rerun the unchanged ML scan.

Historical scoped registration remains FAIL (45de0c9 / scoped-0b8c8f122e80 /
fixture88019a1a01a7, 785 unchanged effect identities). RSMB startup-registered
apply/render PASS and RSMB late-registration FAIL remain separate. Current
AE/project/loaded identity is NOT OBSERVED. No product loader, installed component,
user settings/project, third-party plugin or main changed. No merge, release,
installation, restart or native Adobe call. Original permissions remain consumed.
