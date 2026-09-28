# ScriptUI ↔ Native Agent Protocol

Current implementation: source `4357e36732f106233020fccd110c0e9f19a03a76`.
Protocol version remains **1**. New Agent identity fields are additive.

## Location and transport

`Folder.userData/AE Hot Loader/bridge/`, under the macOS user's Application
Support directory. `request.txt` and `response.txt` contain UTF-8 key/value
lines. The client publishes a complete request through a temporary file.
The Agent replies with the matching `request_id`. Ignore replies belonging to
other requests. A timeout means unknown result, not cancellation of a scan.

## Commands

Illustrative request; values below are examples, not runtime evidence:

```text
version=1
command=get_build_identity
request_id=diagnostics-unique-run-id
timestamp=1790625600000
```

- `reload_plugins`: scans configured Adobe plug-in roots using the gated
  AE 25.6 arm64 loader and filter-loading notification. A successful loader
  pass is not proof of registration, application or rendering.
- `get_build_identity`: returns the resident Agent's compiled identity;
  branches before ordinary discovery. It does not scan/load effect bundles
  or access the project, but still performs normal bridge file I/O.

Unknown commands/versions produce an error. Requests are newline-terminated,
limited to 4096 bytes, with a nonempty `request_id` of at most 128 bytes.
The current panel sends only `reload_plugins`; diagnostic UI is not yet added.

## Responses and identity

All current Agent replies include:

```text
version=1
request_id=diagnostics-unique-run-id
status=success
message=<command-specific result>
agent_build_id=<compiled build ID>
agent_git_commit=<full 40-character source commit>
agent_source_clean=true
agent_target=aarch64-apple-darwin
agent_version=0.1.0
```

Status is `success`, `noop` or `error`. The actual message is one line; normal
message sanitization replaces line breaks and equals signs. For
`get_build_identity` it contains the compact compiled JSON record with:
`schema_version`, `component`, `git_commit`, `build_id`, `source_clean`,
`target`, `version`, `loader_path_id` and `dependency_lock_sha256`.
The current generator validates values to avoid protocol delimiters.

`agent_source_clean=false` identifies an explicitly allowed internal dirty
experiment; it does not establish an approved build. An older Agent may omit
identity fields. Missing fields must not be treated as verified identity.
Version-1 clients may ignore additive fields; the existing panel does so.

A diagnostics consumer must compare the returned identity with the intended
artifact manifest, not merely test for `status=success`. The old
`ordinary-discovery-v1` string now identifies the loader path, not a unique
build. Registry presence and apply/render require separate checks.

## Native identity getters and threading

The loaded Agent also exports `AEHotLoader_AgentBuildIdentity` and
`AEHotLoader_AgentImagePath`. They use caller-owned buffers and never report
truncated success. Contracts and generator requirements are described in
[the identity iteration](ITERATION_AGENT_IDENTITY_2026-09-28.md).
Full image paths are available only through the explicit native getter, not
added to normal bridge replies or startup logs.

The Agent processes bridge requests through its resident idle/main-thread
path. The panel reads the Installed Effects Registry around a loader request;
it does not apply effects or change the project. Shell implementation reload
remains separate from these commands. Shared bridge ownership/multiple host
instances, timeout/retry policy and panel lifecycle remain open hardening work.

## Verification limits

[The checkpoint](CI_CHECKPOINT_4357e36.md) verifies actual identity getters in
an isolated macOS process and full native compilation/packaging. The new
bridge query and startup metadata have **not been exercised inside AE**.
No standalone getter or source inspection result substitutes for that gate.
