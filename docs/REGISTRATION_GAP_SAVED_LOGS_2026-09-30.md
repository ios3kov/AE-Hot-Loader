# Stage C: original scoped logs received and verified

Date: 2026-09-30. Review ID: `gap-upload-20260930-174224`.
Continuation of `eec578a3067643c6f6484ff05c455f02a1a29b0a` on
`research/ordinary-plugin-discovery`. AGENTS.md was reread; the shared rules
still have blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

This record supersedes the unavailable-original-logs limitation and narrows
the output-consumer hypothesis in
[the earlier offline review](REGISTRATION_GAP_OFFLINE_2026-09-30.md).
That historical review is not rewritten. No native source or analyzer changed.

## Acceptance and scope

Verify the uploaded bytes against the hashes recorded before this upload;
run the identified existing analyzer; independently compare snapshots and
cross-check both logs; distinguish a recorded signature from runtime ABI proof.
Keep all inputs unchanged. Do not send an AE request, scan, install, restart,
attach, unload or call a private function. This is evidence analysis, not a
new registration attempt, release gate or installable artifact handoff.

## Inputs and exact identity

User upload: `AEHL-logs-20260930-174224.zip`, 11,341 bytes, SHA-256
`0bec2097f468dec751340e7237d40ad1d8b31fc5517020308756590e8b789901`.
The archive contains exactly four regular files, no symlinks. It was read and
copied into a new analysis workspace, not extracted over existing files.

| File | SHA-256 | Identity check |
|---|---|---|
| before.txt | `4bac64f5d06aecb2cad76c9497552c234d78f0c85ed9316d09de6034dbf03749` | PASS: matches historical record |
| after.txt | `4bac64f5d06aecb2cad76c9497552c234d78f0c85ed9316d09de6034dbf03749` | PASS: matches historical record |
| native-loader.log | `e9eefd0f8ddd73be00cebe3d7623255d20f2c85f70edcec8abe17887b85188df` | PASS: matches historical record |
| native-diagnostic.log | `e9f925561bd84173091aa8eff9fdf878540c3bd3837f1a32370b671c6fe988fd` | Newly calculated, no prior hash substituted |

Historical identity source: [SCOPED_USER_HOST_2026-09-29](SCOPED_USER_HOST_2026-09-29.md).
The corresponding recorded source is `45de0c91112805cfdbc7528bb5747b41b14f13a8`,
research Build ID `scoped-0b8c8f122e80`, fixture `88019a1a01a7`.
This archive does not contain the manifest, ready/claim records or supervisor;
it does not independently repeat installed/resident build or PID verification.
Raw paths, pointer addresses and the full third-party effect inventory remain
in the private upload, not in Git. No proprietary disassembly is uploaded here.

## Actual saved-log analysis

The unchanged analyzer from code commit
`626babcf1c4bf6df25a0c2df9d0eb74c4e77a691` was reconstructed from the fetched
file and its Git blob verified as
`3bf2d78e3b6575fb9c02475ae9076efa8a8e9628` before execution.
This identifies the exact bytes, not an approximately equivalent script.
It ran on the received inputs with their pre-recorded hashes using Python
3.13.5 with warnings treated as errors. Exit 0, no stderr.

Analyzer output SHA-256:
`c1d8013f5ebe9bbb11731a101766e65baf4b77f6b33b75aa6d7f03b8642d6d0c`.
Private chat artifact: `registration-gap-verified.json`.

Observed in those saved bytes:

- Raw loader return: 1; output vector bounds are all null in both logs.
- One fixture image is reported. The modern PluginDataEntryFunction2 address
  is null; EffectMain has a non-null address. Neither proves invocation, nor
  does that single lookup establish absence of every older entrypoint.
- Video modules: 339 before, 339 after, added=0.
- Exactly 785 effect identities in each snapshot; snapshots byte-identical;
  intended match absent; recorded project revision stays 1.
- The identified wrapper skips its notifier call with added=0. No notifier
  return record appears. This inference concerns the wrapper, not all host
  internals or an independently captured call stack.

The diagnostic log agrees with the loader log on root, return, vector and
image records. They share a producer; agreement is not an independent host
observation. The byte comparison was performed separately from the analyzer.

Analysis **PASS** means that saved evidence was successfully verified/read.
The exact-addition check is **FAIL**. The historical live gate remains **FAIL**;
there was no new live gate. Parsed PiPL, runtime receiver, module rejection
reason and a corrective registration operation remain unobserved.

## Correction: the output is not an unconsumed list of plugin objects

The loader log contains the demangled resolved signature. Its first parameter
is a reference to `vector<basic_string<unsigned short, ...>, ...>`, using the
logged dvacore allocator. The full signature has six parameters, including
`ML::ModuleOwnership` and a final bool. The resolver address matches the
subsequent call address in the same log.

Thus the recorded parameter type is a vector of 16-bit-code-unit strings,
not `IVideoFilterModule` objects. Its recorded output is empty. The specific
hypothesis that this run left returned plugin objects waiting to be registered
is not supported and is no longer the next experiment.

This does NOT determine what the string vector is for, what the raw return 1
means, or whether the normal startup caller performs other necessary work.
It does not establish ownership, a callable private ABI, or a safe new flag.
The existing analyzer intentionally reports memory element type UNOBSERVED;
the signature observation is a separate source-level interpretation here.

The remaining useful boundary is PiPL acquisition/interpretation through
video-module creation, acceptance and global publication. First inspect that
path offline in the exact PluginSupport image, rather than guessing a
notifier call or repeating the same in-host scan.

## Current Mac state: only what the user supplied

The supplied terminal output reports the local research branch at `ce5d80d`,
with no working-tree changes listed. No fetch was run, so the displayed origin
tracking line is not proof that GitHub is at the same commit.

The main AE process in that output is PID 78417, started on 2026-09-30 at
17:40:29 local. It differs from the historical test PID 42039. The other listed
processes include crash handlers/helpers, not additional proven main hosts.
This is a user-supplied process snapshot, not direct access to the Mac.
Current project state, responsiveness, runtime version and resident module
identity remain **BLOCKED**; the old empty-project baseline is not reused.
The used installation/restart permission is not renewed by the new process.

RSMB startup-registered apply/render **PASS**, RSMB late-registration **FAIL**,
and the earlier flat-resource failure remain separate historical results.

## Checks and next bounded collection

Input hash verification, actual analyzer execution, independent snapshot
comparison and cross-log consistency: **PASS**, saved-data scope only.
No behavior/source changes: full Python/Node/native regression was not rerun;
previous CI belongs to its original code commits. The five known static-audit
findings remain unresolved. This documentation-only change uses [skip ci].

Next request reads only the exact PluginSupport file and writes a new private
Desktop directory/archive. It neither loads that library as code nor contacts
AE. Refuse an image-hash mismatch; compare the file hash again after inspection.
The command below passed `bash -n` locally; macOS tool execution is NOT RUN
here. Apple documents -t/-v/-V as text disassembly and -arch as architecture
selection in its [otool manual](https://github.com/apple-oss-distributions/cctools/blob/main/man/otool-classic.1).
Full disassembly remains private/ignored and is not to be committed to Git.

```sh
(
set -e
umask 077
APP="/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app"
BIN="$(/usr/bin/find "$APP/Contents" -type f -path '*/PluginSupport.framework/Versions/A/PluginSupport' -print -quit)"
test -n "$BIN" || { echo "PluginSupport не найден"; exit 1; }
OUT="$(/usr/bin/mktemp -d "$HOME/Desktop/AEHL-offline.XXXXXX")"
/usr/bin/shasum -a 256 "$BIN" > "$OUT/image-before.txt"
EXPECTED="4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832"
test "$(/usr/bin/awk '{print $1}' "$OUT/image-before.txt")" = "$EXPECTED" || { echo "Версия PluginSupport изменилась"; cat "$OUT/image-before.txt"; exit 1; }
/usr/bin/otool -arch arm64 -tvV "$BIN" > "$OUT/disassembly.txt"
/usr/bin/nm -arch arm64 -n "$BIN" > "$OUT/symbols.txt"
/usr/bin/otool -arch arm64 -s __DATA_CONST __const "$BIN" > "$OUT/vtables.txt"
/usr/bin/shasum -a 256 "$BIN" > "$OUT/image-after.txt"
/usr/bin/cmp "$OUT/image-before.txt" "$OUT/image-after.txt"
(cd "$OUT" && /usr/bin/zip -q "${OUT}.zip" ./*.txt)
echo "Пришлите: ${OUT}.zip"
)
```

Stop if the image differs, inspection fails or hashes change. Do not install
anything, regenerate the failed scan or use guessed private function addresses.
An eventual runtime hypothesis still needs separate risk authorization and a
fresh identified host/project baseline before testing.
