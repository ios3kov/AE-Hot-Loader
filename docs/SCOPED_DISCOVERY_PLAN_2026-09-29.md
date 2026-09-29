# Stage C: research-only scoped discovery gate

Rules blob: `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
Baseline: source `f966790`; fixture `88019a1a01a7` passed offline checks.
The broad-root scan previously crashed AE. Its FAIL is retained.

## Decision and requirements

The installed Agent (`native-36483421984-1`, SHA-256
`532985d9183eec0ca2e436cc9f891a61e4b3173930e3c653411ff1d2dc63c3b7`)
exports identity and EntryPointFunc only. `LoadPluginFolder` is a local symbol;
`QueuePluginFolder` is absent. Do not assume the source's C linkage makes a
function dynamically callable in the packaged Rust library.

Build a separate research AEGP using the existing native loader implementation.
Only its two diagnostic log destinations are redirected in a generated build
copy into the owned experiment directory. The product Agent and bridge stay
unchanged. Use SDK RegisterSuite5 idle hook and UtilitySuite6 script execution;
the local Adobe SDK declarations are the interface authority.

1. Pin one clean embedded fixture manifest and every signed file hash at build
   time. No request-supplied root or shared-root enumeration.
2. Require the exact test-host executable path under the owned build directory,
   an explicit per-build environment token, main-thread execution and a request
   naming the current PID. The module stays inert in the working AE.
3. Validate the root, all file hashes and directory entries immediately before
   the native call. Reject links, extra files/directories and changed bytes.
4. Persist an exclusive one-shot claim before any loader call. Replays, reloads
   and process restarts must not retry a consumed experiment.
5. Read a fresh blank/unsaved/clean/idle project and full registry before/after.
   Require the target absent before, exactly that registry addition afterward,
   and the same project revision. Preserve snapshots and loader return separately.
6. No install, startup, debugger attachment or discovery in the current user
   host during offline preparation. An isolated AE host remains a runtime
   prerequisite; an environment token alone is not proof of isolation.
7. An external supervisor verifies the pinned manifest, loaded helper identity
   and file hashes, exact PID/executable/start time, and untouched evidence
   namespace. Publish one complete request atomically without replacement;
   bound waiting to 1–60 seconds, preserve pending state on timeout/crash and
   never terminate AE. Independently verify snapshots and call identity before
   accepting native PASS. Use an exclusive supervisor claim against overlap.

## Predeclared checks

- Native guard tests: one exact root/call, wrong PID/token, changed file,
  extra entry/link, unsafe baseline, loader error, unexpected delta, replay.
- AEGP compile/link with SDK 25.6 declarations and warnings as errors.
- Ad-hoc signature, exports, identity and final per-file hashes.
- Existing Python regression and relevant static audit.
- Supervisor negative cases: wrong host, stale request, incomplete/incorrect
  result, timeout, process exit and replay. Atomic request/result publication
  must keep a single hard link and expose only complete records.
- Real AE idle-hook/registry/project-safety/timeout/crash gate: NOT RUN until
  an isolated host and external bounded supervisor are established.

No render, performance, MFR or generic third-party compatibility claim follows
from this registration-only experiment. No release or user handoff is implied.
