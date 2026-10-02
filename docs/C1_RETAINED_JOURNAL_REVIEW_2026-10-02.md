# C1 retained identity journal and independent verifier

Stage C1, Critical/Development. Baseline clean
`c64c75c800dc6cad3dc1715ef4d864e45826991d`, agreed research branch.
Rules 6.2.0 / `d966078a9e45fee7ec9ad14f211a9da753d64b8a`: AI_ENTRYPOINT,
Process scope/API/identity/regression/evidence/safety, Engineering code safety/
test/reproducibility/compatibility, Tools diagnostic/IPC and Native memory rules.
Product contract unchanged. Consumed live observer authority remains consumed.

## Objective and requirements

Save the [capture core](C1_RETAINED_CAPTURE_REVIEW_2026-10-02.md)'s raw evidence
so a separate implementation can reconstruct both captures, ordered names and
read budgets rather than trusting producer flags. Own-fixture tests only; no
installation, provider binding, actual AE read or new native candidate.

| Requirement | Acceptance |
|---|---|
| RIJ-001: complete copied-byte evidence | Retain ordered copied-byte frames with existing mapping provenance for both captures, including four vector reads. Failure retains partial frames but no successful snapshot. |
| RIJ-002: exact run/candidate binding | Validated run/source/build/binary/process-start/provider/root and explicit owned-fixture/AE-diagnostic origin; every journal record matches separately supplied expected scope. No activation tokens in evidence. |
| RIJ-003: durable one-shot records | Reuse existing owned 0700-directory/0600 exclusive-file journal container; fixed claim/marker/native/result sequence; any invalid operation or write failure poisons the wrapper, never retry/overwrite/delete. |
| RIJ-004: independent semantic verification | Bounded strict framing/field inventory, exact read order/shape, matching copies/mappings, name bounds/termination/overlap consistency, budgets and final status. Unknown fields, duplicates, missing records or producer-only success refuse. |
| RIJ-005: safe evidence reads | Bounded regular owned files, exact private mode, no symlink/hardlink/special-file traversal, rechecked file/directory identity; preserve evidence on refusal. |
| RIJ-006: scoped validation | C++ producer/disk-journal → Python independent verifier end-to-end fixtures plus corruption/refusal cases, full available clean regression, bounded static review and exact-source CI. |

## Trust and scope boundaries

The existing journal envelope is a storage format, not resource-registration
permission. This new scope uses four fixed records; it does not borrow the old
observer's six-record native transaction or claim project/registry postflight.
The independent verifier checks supplied bytes against separately supplied expected
identity. It cannot attest to live execution or defend against an authorized
same-UID operator fabricating all expected bytes. Owned-fixture results cannot
be relabelled as actual AE evidence. Native pre/postflight, actual loaded binding,
external one-shot supervision, deadlines and concrete operation authority remain
required before live use.

Names are raw hex bytes with preserved order/duplicates, not executed text,
portable module paths or established provider attribution. No complete-state/
lifetime/repeat-safety or ResourcePassGate eligibility is emitted. Raw addresses
and copied plugin state stay in private evidence, not repository/public reports.

## Preparation checkpoint

Implemented `RetainedIdentityJournal.hpp`, independent Python
`verify_retained_identity_journal.py` and ordered completed-copy frames in the
capture core. The read shape/call/byte limits and native profiles stay unchanged.
Scope serialization binds run/source/build/binary/process-start/provider/root
with explicit origin; actual AE mode requires the reviewed MEE hash/UUID.
Every record is independently compared against separately supplied expected scope.

The C++ wrapper reuses the existing durable journal container, poisoning itself
on invalid order or failed save, and writing four fixed records. Native frames
retain raw bytes plus exact mapping provenance. A partial failure remains FAIL;
no successful snapshot or decoded identities appear. Records/payloads are capped
at 64 KiB, copied bytes at 6,976 and frames at 22. Journal methods require
serialized calls in the owning process, like the reused disk container.

The independent verifier reconstructs both pointer/name read sequences from raw
frames, checks all vector rechecks, whole record equality, names and overlapping
copies, mapping consistency, budgets and exact field inventory. It preserves
ordered names as hex, without assuming UTF-8 or invoking their content. It walks
parent directories through no-follow FDs, bounds directory inventory and file
reads, checks owned 0700/0600 modes and rechecks file/directory identity. Invalid
expected scope refuses before opening evidence. Its PASS always says
`host_execution_verified: false`: journal consistency alone is not live proof.

Focused journal suite PASS: 11 Python tests and 17 nested C++ journal cases.
The C++ producer writes actual owned private journals; the separate Python code
verifies empty, inline/raw-byte and maximal eight-name evidence. Tests refuse
producer-only/failed PASS, binding mismatches, corruption of either capture or
vector rechecks, name/mapping/budget/field errors, malformed framing, missing
files, symlinks/hardlinks/FIFOs/modes, entry changes and directory replacement.
Related capture/decoder focused tests also PASS. Full clean-source regression,
static review and exact-source CI are recorded below. Mandatory acceptance was defined before editing. Current actual seven names remain NOT RUN; ordinary-effect
late registration/apply/render and release remain blocked. Next after this stage:
separate host transaction/supervisor and an exact inert native candidate, then its
reviewed validation packet and operation authority.


## Exact-source verification

Code/test source **59becab0056fae08b450cbb4471466b427427744**.
Full clean local regression PASS: 323 Python/no skips, 62 Node, 22 offline stages;
tracked source remained unchanged. Nested C++ cases are not added to Python count.
Private offline report SHA-256
`952466d4399da3ced6a898729b8795374b20855188062b1c729f8dfe623dc84e`.
Independent archive inventory/member hashes/CRC and current tracked-source hashes
PASS. No live operation requested; full AE pipeline remains BLOCKED.

Separate review covered bounded serialization/field framing, raw trace ownership,
expected-scope origin, two-pass reconstruction, fixed journal ordering/poisoning,
no-follow directory traversal and file/directory rechecks. Bounded static audit
completed at exact clean source: 320 supported files, zero omissions in that
scope, all selected checks completed. Native code reviewed separately; unsupported
file types remain outside scanner claims. Raw exit 1 retains the sole known
`vibe.no_ratelimit_auth` at `tools/artifact_manifest.py:71`: verified local argparse
mode option, not an HTTP/auth route. Reviewed false-positive; no new finding.
Private audit SHA-256
`b4b92a815013d71def7a9d6388b64c9534e5a44da82eb83feee3f0530480e32f`.
[Research CI 37046241769](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37046241769)
and [full macOS CI 37046241807](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/37046241807)
both completed/success at that exact source. Changed local documentation links
and `git diff --check` PASS. This documentation-only closeout does not change the
tested code or any native candidate. Existing native profiles, old journals and
ResourcePassGate are unchanged. Retained capture-core changes only add bounded
copied-frame evidence storage; the new journal/verifier are separate.
