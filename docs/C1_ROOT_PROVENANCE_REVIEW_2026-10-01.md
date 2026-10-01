# Stage C1: static root provenance and indirection review

Date: 2026-10-01. Research branch baseline: 45d3298a9a8feb245f4de251cad4750375f208a5.
Rules b27f45467e0a9152fc82c1072438dfed07f0c36e, AI_ENTRYPOINT read first;
PROCESS/API-SOURCE-001, ENGINEERING, NATIVE, TOOLS, WORKFLOW apply.
Existing product contract; Development gate. Independent file-only research,
Standard tooling with Critical dependent native integration still blocked.
No new SDK/host API, no AE launch/attach/read/script/call, installation or scan.

## Contract before implementation

Continues [snapshot preparation](C1_CLEANUP_SNAPSHOT_REVIEW_2026-10-01.md).
Determine static root provenance from the exact PLUG/MEE inputs. Preserve the
nine-image live profile; supplemental metadata is not resident identity proof.

- RP-001: parse bounded thin arm64-all little-endian MH_DYLIB or FAT32 containing
  exactly one arm64-all slice. Reject missing/duplicate/unsupported architecture,
  overlapping/truncated slices, invalid load commands/segments/sections/UUID.
- RP-002: resolve exactly one requested N_SECT non-debug symbol via bounded
  LC_SYMTAB/nlist_64, validating its section ordinal and VM containment. Require
  the reviewed symbol value, root extent, exact writable non-executable __DATA
  zero-fill section and UUID. No zero-fill bytes are read as serialized state.
- RP-003: record symbol/base/section/root VM metadata and image-relative offsets,
  including explicit pointer-indirection semantics. Never emit a runtime address,
  read a process, resolve/call a function, or infer allocation/completeness.
- RP-004: collect only pinned original files read-only, verify hashes before/after,
  require clean source identity, record private manifest/ZIP hashes. No original
  binary, symbols dump or raw disassembly in Git.
- RP-005: cover malformed command/slice/symbol/section boundaries and both real
  owned compiled zero-fill symbols on macOS arm64 and portable byte fixtures.
  Run full offline regression and exact-code CI; keep live gates NOT RUN.

## Already recorded addressed control flow

PLUG_Search 0x8ac8–0x8acc forms PLUGp_G; null-sack branch 0x8c28 reads
PLUGp_G+0x08 into x26, then 0x8b00 dereferences x26 into the actual sack.
PLUG_InstallScan corroborates at 0x893c/0x884c. Thus PLUGp_G+8 is the
**sack-handle pointer slot**, not CleanupSnapshot's sack_slot. A future reader
must read that slot to obtain the handle address, then read the handle to obtain
the sack. The sampler's supplied sack_slot is that separately validated handle
address; it is not automatically the global slot. Prior sampler contract is
unchanged and still unbound.

MEE PluginCleanupFunc 0x37724–0x3772c forms MergedGlobals.195+880 (0x370)
and loads vector begin/end. Symbol values and containment will be independently
checked against Mach-O metadata below. No capacity/record allocation or lifetime
contract is inferred from these two words.

## Source basis and unknowns

Apple's installed macOS 27.0 SDK loader.h (segment_command_64, section_64,
S_ZEROFILL) and nlist.h (nlist_64, N_STAB/N_TYPE/N_SECT, one-based section
ordinal) are the format sources. These are binary-format definitions, not an
Adobe late-registration API. Private PLUG/MEE identities and addressed bodies
are preserved in prior reports. Unknown runtime slide/header, resident identity,
heap ranges, handle lifetime, callback behavior and quiescence block dependent
native integration and complete-observation claims.

## Verification

Focused local macOS arm64 regression: PASS, 13 Python tests including actual
owned compiled zero-fill metadata inspection. That library was never loaded.
Initial fixture failures exposed linker-format assumptions (string-table prefix,
16-byte names and debug aliases) and were fixed with specific regression cases;
duplicate real N_SECT root definitions remain refused. This is format coverage,
not Adobe/runtime compatibility proof.

Implementation: pure bounded Mach-O parser + fixed PLUG/MEE collection request.
The collector reuses reviewed original-file validation, exclusive private writes
and ZIP verification. It caps file reads at 256 MiB, freezes root requests and
records only metadata/identities. There is no runtime-address or sampler-scope
conversion. Focused original-file inspection matched the pinned hashes and
static roots; exact clean-source collection now PASS at
**efe05f2f7d320ffb026ff963188079c06f4aca49**.

| Provider | Symbol VM | Reviewed root VM / extent | Zero-fill section | UUID |
|---|---|---|---|---|
| PLUG | 0x18488 | 0x18490 / 8 bytes | __DATA,__common, ordinal 13 | d4ddb055e565378fb8f433ac0bb2253d |
| MEE | 0x10fa00 | 0x10fd70 / 16 bytes | __DATA,__bss, ordinal 12 | 74a30dbaa08b367bbd9915d6d77e9d52 |

Both slices have base VM 0, FAT slice offset 16384, exact reviewed hashes before/
after. PLUG section range is 0x18488 + 320 bytes; MEE section range is 0x10f080
+ 28512 bytes. The metadata records serialized_root_bytes=null; never decode
zero-filled file padding as a current sack or an empty live vector.

Private collection ZIP resource-roots-8e75fd87-cp3a2bav.zip SHA-256:
`8056742d352ce0bfd62c3e79e2f7e5978763aaf940740d8296abc82bfe653228`.
Manifest and all three payload hashes independently verified. Original provider
files were not modified and no raw Adobe bytes/disassembly are committed.

Exact-clean-source local unified regression: PASS, 284 Python without skips,
62 Node, 22 stages; source inventory unchanged before/after. Private ZIP
AEHL-checks-sy_ac_cx.zip SHA-256:
`935a094cb7df202e97603a11cbea235d8f80893e057c9fdfdd220200cfae150c`.
Run ID feaa841baa3b4587902d0be97ebb96b4; every archived payload hash verified.

Research CI [36927550112](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36927550112):
PASS, Linux + macOS, exact efe05f2. Full macOS CI
[36927550048](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36927550048):
PASS (build/sign/package/synthetic smoke). These are offline/build checks, not registry or runtime-state evidence.

Bounded scanner: 248 supported files, no omissions, clean efe05f2 source.
Exit 1/review_required is retained: sole known artifact_manifest.py:71
local-argparse false positive. No finding suppressed; not a full security audit.
Documentation closeout does not inherit a new code/test run.

## Next step and preserved gates

Continue resident module/header/text identity and root VM containment checks on
owned fixtures before preparing a concrete live diagnostic observer. No loaded
Adobe identity or actual root/state has been observed. Lifetime, heap allocation
and quiescence remain unresolved; matching snapshots cannot become a complete
inventory. Native resource backend NOT READY; C1 registration/apply/render NOT
RUN. C0 stays its recorded live PASS. No private mutex call, setup/setdown/unprep
or repeated scan is authorized by static addresses or these test results.
