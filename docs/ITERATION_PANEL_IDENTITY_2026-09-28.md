# Panel / packaged Agent identity integration — 2026-09-28

Baseline branch: `research/ordinary-plugin-discovery`, head `9ee5c4e`.
The code is unchanged from verified source `4357e36`; the intervening commit
changes only documentation. Shared DEVELOPMENT_RULES reviewed at blob
`a1760fde8763f789b50b91c20407938b4fcaea4a`.

## Scope and acceptance

Target: ScriptUI + Agent on AE 25.6.0, macOS arm64. No new native loader calls,
rendering changes, installation, process control or changes to `main`.

- Every Reload starts with the existing read-only `get_build_identity` command.
- Compare Build ID, full commit, clean state, target and version with generated
  panel metadata. Missing/old/mismatched replies must not initiate a scan.
- Diagnostics alone never scans or reads/modifies the project or registry.
- Verify identity again on the scan reply; registry presence is still separate
  from successful application/rendering. A timeout does not cancel native work.
- Bound response parsing and bind polling to request IDs. Preserve pending
  requests; do not overwrite them when diagnostics starts.
- Stamp the panel from clean Git source using the same package Build ID as
  the Agent. Test the exact unpacked panel and read the exact unpacked Agent's
  compiled getters, not a separately built library.
- Preserve existing native build/sign/packaging and seven standalone gates.
  All full-package Cargo builds must use `--locked`.

## Implementation and local evidence

`tools/build_panel.py` generates one inline metadata literal from Git and the
Agent package version. It refuses dirty input, malformed values and an existing
output. The template deliberately cannot scan without generated metadata.
No runtime manifest evaluation or mutable global override supplies the expected
identity. This guards accidental mismatched installs, not hostile local code.

The panel provides Diagnostics, verifies before each scan and rechecks the
matching completion reply. It copies the registry immediately before scanning.
A legacy Agent cannot trigger the new scan through an incomplete handshake.
Polling callbacks carry a request ID; completed/timed-out tasks are cancelled.
Pending request files are preserved and temporary names are request-specific.
The Agent implementation and protocol fields are unchanged.

Local Linux/Node 22.16.0/Python 3.13.5 checks: old panel suite 22/22 PASS;
existing Python suites 28/28 PASS; updated panel suite 51/51 PASS; all Python
suites 38/38 PASS, including 10 new generator tests. The updated panel contract
against the old JSX produced 28 failures, 23 passes. These are host/file mocks
and owned temporary Git repositories, not AE runtime evidence.

Fresh macOS CI and package evidence are recorded in a separate checkpoint after
the resulting commit is tested. No old PASS is reused for this source.

## Limits and remaining gates

Real ScriptUI layout/lifecycle, resident Agent diagnostic roundtrip, AE runtime
identity, RSMB startup/apply/render and release acceptance remain NOT RUN or
BLOCKED without an accessible isolated AE environment. Cross-process bridge
ownership, simultaneous panel instances, unknown in-flight scans after timeout
and full component identity coverage are separate open items. This iteration
does not claim to solve them. Reading the exact packaged Agent in a standalone
process is stronger artifact evidence, but still not evidence of AE loading it.

API references: the Adobe ExtendScript File object documentation (encoding,
close/write return values) and AE Application scheduleTask/cancelTask/effects:
https://extendscript.docsforadobe.dev/file-system-access/file-object/
https://ae-scripting.docsforadobe.dev/general/application/
