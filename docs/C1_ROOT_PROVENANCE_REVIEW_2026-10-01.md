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
static roots; durable clean-source collection and full CI are NOT RUN before
code checkpoint.
