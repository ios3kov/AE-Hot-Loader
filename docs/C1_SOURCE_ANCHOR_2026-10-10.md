# C1 source identity and the selected resource producer

Rules11.1.0/source04b6068; baseline9a56e13; branch
`research/ordinary-plugin-discovery`. C1 PARTIAL; private append BLOCKED;
C2/late-add NOT_RUN. No AE launch/install/attach/target-memory read/private call.

## Acceptance and bounded result

| ID | Observable criterion | Result |
| --- | --- | --- |
| SA01 | Query the real owned child's open file using kernel metadata | PASS focused native control; exact candidate receipt separate |
| SA02 | Same fd number, byte-identical second file via actual dup2 | PASS specific SOURCE_FILE_CHANGED; child payload reads0 |
| SA03 | Same inode, changed bytes | PASS specific SOURCE_CONTENT_CHANGED; child payload reads0 |
| SA04 | Identify one selected producer's data/length/allocation/release operations | PASS_FILE_ONLY7 bodies/648 instructions; live target UNKNOWN |
| SA05 | Critical review, applicable regression, identified source and preserved Evidence | Final candidate receipts separate |

`source_anchor.cpp` forks only its own cooperative child. The parent pins birth,
UID/parent PID and asks `proc_pidfdinfo(PROC_PIDFDVNODEINFO)` for exactly that
child's reported fd before and after the fixture's operation. It compares device
and inode with its own held file. A second pre-read byte check of the held file
detects the same-inode mutation; returned child bytes are checked again before
success. The same fd number is not an identity witness.

Operations/events and the interval with no further child mutation are instrumented
fixture behavior, not passive observation of arbitrary fd generations. This does
not establish an Adobe object's lifetime or a general fd-monitor implementation.
Kernel-query authority/behavior against AE remains untested. All failure paths
close owned pipes and allow the child to finish; no kill/attach/expression.

`fsref_anchor.cpp` also executes the legacy API family on two own files with
identical contents. Natural CFURLGetFSRef succeeds; FSCompareFSRefs accepts a copy
of A's reference and rejects B with errFSRefsDifferent. FSRef is80bytes,
FSIORefNum4bytes, ByteCount8bytes in the pinned local SDK. The narrow deprecated
API warning suppression is limited to this explicit compatibility probe. This
establishes an own-process copied-value comparison, not cross-process AE capture
or a current supported Adobe API contract.

## Producer result: direct fd transfer was the wrong assumption

Fresh file-only PluginSupport pin:
`4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`,
UUID64c01ac4-2413-3463-8822-17ee5543052a.
Fresh ASLFoundation pin:
`f1c3c7256f8a986f39519387511436577a3d65fb9d04a672bbb115c1871a3fe7`,
UUID408bb5bb-bd1a-31ac-9fa6-e033644ce8ee.

PluginSupport URL overload0x41cec dispatches through module slot0x40 at0x41d28.
The selected ASL base vtable address point0x31680 has dyld rebase
0x316c0→0x24f00 (LoadResourceFromURL), and slot0x38 rebase
0x316b8→0x25220 (UnloadResource). File fixups, not raw chained pointer equality,
establish these selected targets. The live receiver could select another vtable.

The selected ASL URL implementation0x285fc executes:

```text
CFURLGetFSRef → FSGetDataForkName → FSOpenFork
→ FSGetForkSize → operator new[] → FSReadFork → FSCloseFork
→ returned allocation/actual count
→ PluginSupport vector copy → SetPiPLValues → module UnloadResource/delete[]
```

This is a Carbon fork API path. FSIORefNum must not be passed to the POSIX fd
query merely because both have integer representation. An internal POSIX-open
bridge would require separate observed evidence. The source-first alternative
is the naturally initialized FSRef output; no target CF getter need be invoked.

| Candidate point | File-established operands / limits |
| --- | --- |
| ASL0x28630 | After CFURLGetFSRef; w0 success;80-byte output at x29-0x78 |
| ASL0x28660 | After FSOpenFork; status in w0;4-byte fork reference at x29-0x7c |
| ASL0x286a8 | After FSGetForkSize; signed64 size at sp+8; require success |
| ASL0x286c0 | new[] result in x0; requested allocation size in x21 |
| ASL0x286dc/0x286e0 | FSReadFork operands/result; destination x4, requested count x3, actual-count output x5=sp (8bytes), OSErr return in w0 |
| ASL0x286e4 | Host propagates only low32bits of actual count; no read-status branch here |
| PS0x41d70 | memcpy destination x0, returned source x1, propagated count x2 |
| PS0x41d8c | Release dispatch; selected ASL UnloadResource uses delete[] |

Never read the requested size as if it were initialized length. Non-null result
alone does not prove read success. Future observer must independently reject
failed reads, negative/excessive sizes, count truncation and count>allocation.
The current4KiB diagnostic cap remains; full32-byte name tails are not assumed
initialized. Success return points are candidates, not admitted live sites.

## What is still missing

The selected caller keeps a module shared owner and copies bytes before its
normal release. This narrows where to look; it does not prove the actual resource
belongs to our marker, that no opaque call invalidates it, or exception/reentrant
cleanup. A natural FSRef output could break initial selection only after a
reviewed80-byte stack-output/initializer/continuation contract is admitted.
Copied FSRef comparison inside the controller and cross-process value behavior
still need verification for that proposed route. A successful read must then be
linked to the same PiPL allocation generation and executed copy operands.

No production/AE transport is broadened. Existing metadata and resource debugger
collectors stay unchanged. Payload origin labels and fixture success cannot close
startup writer→public reader. The next gate is a narrow source-identity output
contract at ASL0x28630, then allocation→read→copy→release for the same invocation.

Private receipt root: `build-ae-hot-loader/source-anchor-2026-10-10-9a56e13`.
Raw Adobe binaries/full SDK are not redistributed. Preserve original transcripts,
failed/preliminary run identity and exact final native/verification receipts.
