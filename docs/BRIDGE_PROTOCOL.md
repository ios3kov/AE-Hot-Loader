# ScriptUI ↔ Native Agent Protocol

Version 1 with additive compiled Agent identity fields. Panel handshake
integration: `04fea70`. Native Agent protocol implementation is unchanged by
that iteration. Target: research on AE 25.6.0 / macOS Apple Silicon.

## Transport

Directory: `Folder.userData/AE Hot Loader/bridge/` (macOS Application Support).
Files: `request.txt` and `response.txt`. UTF-8 `key=value` lines, final newline.
The new panel publishes a request-specific temporary file only after successful
write/close and refuses to overwrite an existing pending request. Responses
are consumed only for the current request ID; recognized duplicate fields,
unsupported versions/statuses and incomplete/oversized responses are rejected.
The panel bounds response reads at 16 KiB. This is not a multi-client lock.

## Commands and sequence

Example diagnostic request, with a newly generated ID/timestamp for each run:

```text
version=1
command=get_build_identity
request_id=1720000000000-1-123456
timestamp=1720000000000
```

`get_build_identity` returns compiled metadata before native discovery. It does
not scan plug-ins, apply an effect or modify a project. `reload_plugins` invokes
the gated ordinary-discovery path; loaded module counts do not prove effect
registration, application or rendering. Unknown commands/versions return errors.
The Agent bounds requests at 4096 bytes and IDs at 1–128 characters.

**Diagnostics:** send `get_build_identity`, compare identity, display the result,
then stop. No registry snapshot or native scan follows.

**Reload Plugins:** send `get_build_identity`; require a successful matching
identity; copy registry match names immediately before a new `reload_plugins`
request. Recheck identity on its matching reply, then compare registry identities.
Do not report apply/render success from a registry delta.

Both buttons share the panel's pending-operation guard. Scheduled polls carry
the request ID; stale callbacks and stale replies cannot complete a later phase.
Each phase has a 30-second panel timeout. Diagnostic timeout means no scan was
dispatched by that operation. Scan timeout means unknown outcome, not cancellation.

## Replies and required identity fields

```text
version=1
request_id=1720000000000-1-123456
status=success
message=<diagnostic JSON or loader summary>
agent_build_id=<compiled Build ID>
agent_git_commit=<40-character commit>
agent_source_clean=true
agent_target=aarch64-apple-darwin
agent_version=0.1.0
```

Statuses: `success`, `error`, `noop`. Only `success` is a valid diagnostic
handshake. A loader `success` is not registration/render evidence. Partial
loader errors remain errors even if the registry grows.

The panel compares all five `agent_*` fields to its generated inline metadata.
An older Agent without those fields, a dirty build or any mismatch blocks the
scan. Its diagnostic text identifies observed panel/Agent builds. The diagnostic
`message` is never executed or used to supply expected identity.

`tools/build_panel.py` generates expected metadata from clean Git source using
the same `PACKAGE_BUILD_ID` and Agent package version. The repository JSX is a
template and cannot scan until stamped. No runtime manifest or global override
changes the expected identity. This protects against accidental mismatched
installation, not malicious code running as the same user.

Agent metadata JSON also includes `schema_version`, `component`,
`dependency_lock_sha256` and `loader_path_id`. The existing Agent sanitizes
message separators/newlines and emits its compiled identity on every reply.

## Native diagnostics and execution context

The existing exported getters are `AEHotLoader_AgentBuildIdentity` and
`AEHotLoader_AgentImagePath`. Both take caller-owned buffers/capacities, return
0 for a full NUL-terminated result, -1 for invalid arguments and -2 for
insufficient space. They do not silently truncate. Image path comes from the
loaded module; the normal panel reply does not expose that path.

Agent discovery runs from the resident AEGP idle path. The panel only performs
file IPC and read-only registry snapshots; it does not access `app.project`.
Generic Control Shell implementation reload remains separate from this command.

Evidence: [CI_CHECKPOINT_04fea70](CI_CHECKPOINT_04fea70.md) tests the exact packaged
Agent getters outside AE and the generated panel under mocks. Real AE roundtrip,
shared-process ownership, multiple panels/reopen and in-flight timeout/retry
remain separate mandatory integration gates.
