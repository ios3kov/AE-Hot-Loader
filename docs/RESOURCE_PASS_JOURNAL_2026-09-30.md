# Stage C: disk-backed one-shot resource-pass journal

Date: 2026-09-30. Continues `24ba8baf256ab90f0527b4fca4daa95e22fb21e4` on
`research/ordinary-plugin-discovery`. Shared rules rechecked unchanged at blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`; AGENTS and PRODUCTION_PLAN apply.
Code/test commit: `5beb51c1dbd70d1f0c6115578387f27dfab78776`.

## Scope and acceptance

Move the resource gate's claim/evidence methods from an in-memory test model
to a reusable POSIX filesystem component. Require one winner across competing
processes, refusal after a process exits, refusal on incomplete/tampered files,
private evidence and no returned PASS after evidence failure. Test actual
files/processes, preserve the existing policy and loader, and run regressions.
This does not execute Adobe code, create FILE_Spec or register an effect.

The native FILE boundary is still unresolved. Reinspection of the supplied
aelib, PLUG and FLT import tables finds the host-allocator UTF-16 C++ string
overload of FILE_New and FILE_Dispose, not an independently verified plain-C
path constructor. Received input hashes still match their earlier records.
FILE.dylib implementation bytes are not among the current attachments. A guessed
std::string layout or private call is not a safe substitute. No installation,
restart, debugger attachment or in-host operation was performed or authorized.

## Implemented component

`ResourcePassJournal.hpp` provides DiskJournal, JournaledBackend and
RunJournaled. The claim, before snapshot, call marker, after snapshot and final
result are real files. JournaledBackend implements the storage methods of the
existing resource_pass::Backend; observation, scope verification and FILE/PLUG
operations remain abstract. The tests provide synthetic implementations only
for those unbound host operations. There is no runnable AE backend or artifact.

A future adapter must allocate a dedicated empty 0700 journal directory inside
its owned workspace, separate from ready/request/manifest files. Opening the
journal never creates, clears or deletes the directory. Fixed filenames are
created with O_CREAT|O_EXCL. Any existing entry, including a partial claim or
an orphan marker, blocks a new transaction; an exception poisons that object.

Every parent component is opened relative to a directory descriptor with
O_DIRECTORY|O_NOFOLLOW. The final directory inode/owner/mode is rechecked;
previous record inodes, link counts, mode and exact bytes are revalidated before
and after appending. Files are 0600. Each write is followed by file fsync,
checked close and directory fsync. Partial files are retained, never retried
or deleted. Objects inherited across fork cannot continue a parent's journal.

The exclusive-create semantics are defined in the
[POSIX open/openat specification](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html).
No native loader ABI is derived from that OS documentation.

Length-prefixed byte fields are wrapped in a versioned record with payload
length and a terminator. This is a new format, not the old snapshot protocol.
There are at most five records; a payload is bounded to 24 MiB. Roots, process
identity, pins and registry names may be present only in the private journal,
not public logs. No request token or backend exception text is serialized.

RunJournaled wraps the unchanged policy and only returns PASS if the final
record append also completes. Evidence-write failures remain FAIL even if a
synthetic registry delta was correct. The external supervisor must validate
complete records and independently verify host state; file contents alone,
especially after writer/flush failure, must never certify a live gate.

## Why this does not directly call scoped::Save

The preceding design proposed reusing Save/VerifyScope. Save uses pathname
checks and a temporary file with exclusive rename, but does not provide this
journal's directory-descriptor binding, previous-record verification or parent
directory fsync. A separate, narrowly scoped storage component avoids changing
the already tested old scoped loader while closing those specific requirements.
The change is confined to resource-pass evidence. VerifyScope remains the planned
fixture verifier; its actual wiring and a durable external supervisor are still
not implemented. Existing scoped-discovery commands still run the old loader.

## Checks

Local reconstruction used the previously verified 1d90cb6 CI source archive.
GitHub comparison confirmed only documentation differs up to 24ba8ba. All three
new source files match their remote Git blobs. This is not the user's checkout.

| Check | Result and scope |
|---|---|
| New journal cases | 32/32 PASS, actual temporary files and processes; synthetic host/spec/search |
| Eight-process competition | Exactly one successful transaction, seven refusals |
| Exit after claim / after marker | Retry blocked with original evidence retained |
| Real write failure | RLIMIT_FSIZE induces a partial write in an owned child process; no spec/scan and retry blocked |
| Symlink/FIFO/hardlink/tamper/directory replacement | Expected refusals; no tested redirect or replay |
| Linux clang and GCC strict builds | PASS, C++17, warnings treated as errors |
| Linux ASan/UBSan | PASS on 32 cases, empty diagnostics; parent leak detection enabled |
| Python local regression | 210 collected: 204 PASS, six macOS-only skips |
| Node local regression | 62/62 PASS, host mocks |
| Existing resource policy | All 63 synthetic cases retained within Python regression |
| Research CI 36761528713 | Artifact confirms 210 Python collected, 204 PASS/six skips, both 63/32 native sub-suites, 62 Node PASS |
| Full macOS CI 36761528656 | PASS, all build/sign/package/smoke steps; Python 210/210, 63 policy cases, 32 journal cases, 62 Node, 15 existing scoped guards |
| Full static-security audit | NOT RUN again; five historical findings remain open |
| Native FILE/PLUG backend / AE registration | BLOCKED / NOT RUN |

The 32 C++ cases are nested inside one Python test, not 32 extra Python tests.
Process-exit tests use _exit, not a machine reboot or storage power cut. No
network-filesystem, power-loss, hostile same-UID writer, disk-controller-cache,
or all-syscall-fault guarantee is made. The component is single-threaded per
instance. Private directory permissions are not a boundary against the owner
or root. The deadline cannot interrupt a stuck fsync or native call.

| Source | SHA-256 |
|---|---|
| ResourcePassJournal.hpp | `13553150a6dd84a9f692de42c55abeab5f0fc1181b8d5aaf8f740f423df74004` |
| resource_pass_journal.cpp | `001d2289043a7d926134c3a1035995af5170732322615327040b8d3e3e9d3ba2` |
| test_resource_pass_journal.py | `bb56ba3ee55ce79d737870e86c8634789a1b3aad75e86d75828bc995d64613b3` |

## Remaining boundary

Obtain the exact FILE.dylib implementation before binding FILE_New, path
roundtrip and FILE_Dispose. Review ownership/error/string behavior, then build
a separate creation/roundtrip/release check before any single-root PLUG pass.
Keep the installed predicate and callbacks. Never replay Birth, InitIterator,
RequiredPreSearch, global folder enumeration, notification, or the old scan.

The native integration, fresh fixture, loaded identities, external supervisor
and separate risky-action approval remain required. Historical scoped embedded
registration FAIL, RSMB startup-registered apply/render PASS and RSMB late
registration FAIL stay separate. Current AE/project state is NOT OBSERVED.
No product source, installed component, main, merge or release changed.

## Minimal next data request

The FILE implementation, unlike its callers, is not in the received archive set.
Copy only FILE.dylib into a new private directory and include before/after and
copied-byte verification. This request does not execute the library, start or
contact AE, change installed files, or renew risky-action permission. The command
passed bash syntax and an isolated Linux dummy-file copy/hash/archive test;
its real Mac execution remains NOT RUN. Stop on any error and retain the output.

```sh
(
set -e
umask 077
DIR="/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks"
test -f "$DIR/FILE.dylib" || { echo "FILE.dylib не найден"; exit 1; }
OUT="$(/usr/bin/mktemp -d "$HOME/Desktop/AEHL-FILE-bin.XXXXXX")"
(cd "$DIR" && /usr/bin/shasum -a 256 FILE.dylib) > "$OUT/SHA256-before.txt"
/bin/cp "$DIR/FILE.dylib" "$OUT/"
(cd "$DIR" && /usr/bin/shasum -a 256 FILE.dylib) > "$OUT/SHA256-after.txt"
/usr/bin/cmp "$OUT/SHA256-before.txt" "$OUT/SHA256-after.txt"
(cd "$OUT" && /usr/bin/shasum -a 256 -c SHA256-before.txt && /usr/bin/zip -q "${OUT}.zip" FILE.dylib SHA256-before.txt SHA256-after.txt)
echo "Пришлите: ${OUT}.zip"
)
```

Research evidence artifact `11118881376` was downloaded and independently hashed:
`1fa15c2700903979cc45c6ae50bf1da1164db214a791d5427a27c64480da97ee`.
Local clang static analysis produced no diagnostics for the test translation
unit; this is not the full product audit or a proof of all paths.

Full macOS CI completed successfully. Evidence artifact `11118543101` was
independently downloaded and hashed:
`c0bc9fe5e60bf12f3a74ff163a8015b29252c9fa245061a038a6b8aad03a08d2`.
Its source snapshot matches all three changed code files byte-for-byte. The
build record identifies clean source 5beb51c, arm64, Xcode 16.4 and Apple clang
17.0.0. No CI installable package was handed over or installed. Green workflows
do not clear old/unreviewed warnings. Documentation-only follow-ups use [skip ci].
