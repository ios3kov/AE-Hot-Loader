# Existing-host preflight — 2026-09-28

Baseline: branch `research/ordinary-plugin-discovery`, head `adee341`;
implementation/package source `04fea7060c7ef7ebc4a315b5c39364850287e294`,
Build ID `native-36483421984-1`. Shared DEVELOPMENT_RULES blob reviewed:
`a1760fde8763f789b50b91c20407938b4fcaea4a` (unchanged).

## Goal and acceptance defined before tests

Unblock the real-host test with one minimal, non-installing diagnostic request.
This session has Linux tools and GitHub, not an authorized macOS/AE execution
channel. It must not invent a real AE PASS or repeatedly install candidates.

- Detect exactly one already-running AE; do not issue start, quit or kill.
- Target AE 25.6, including its observed scripting version `25.6x101`.
- Read project counters and the three exact RSMB registry identities only.
- Ask the resident Agent for `get_build_identity`, never `reload_plugins`.
- Compare to the identified reference package, never accept missing identity.
- Correlate before/after snapshot, fresh run token, PID and process birth.
- Bound subprocess waits, bridge reads and response waits; preserve pending
  requests on timeout and pre-existing bridge state. Never delete preferences.
- Keep output local, with no project names/paths/content or complete registry.
- Tests must exercise the emitted JSX and bridge publication/validation.
- Cold-start, panel UI, application, rendering and late registration stay
  explicitly NOT RUN. This collector is not the product release gate.

## Changes

`tools/collect_ae_host.py` collects two read-only snapshots via the documented
macOS `DoScriptFile` route, allowing AE idle callbacks between invocations.
It sends one bounded diagnostic bridge request and preserves foreign state.
`experiments/host_preflight/COLLECT_AE_PREFLIGHT.command` is a launcher; it does
not install Python, the Agent, the panel or third-party plug-ins.

Use only an idle running host. An existing request or response blocks the
bridge portion rather than authorizing cleanup. This is not a cross-process
locking redesign: simultaneous bridge clients remain unsupported. The outer
wait cannot cancel work already accepted by AE. A process change invalidates
the collected single-host evidence. Apple Events permissions and scripting
file access may block collection; the tool does not change security settings.

The reference package is immutable, not automatically the newest branch head.
A mismatch is useful evidence that the intended Agent is not resident, not a
reason to replace files or restart an unsaved project automatically.

Run from the repository on the Mac:

```sh
python3 tools/collect_ae_host.py
```

A unique private directory under Downloads contains `report.json` and the
snapshots. Only `report.json` is needed for diagnosis. Review any diagnostic
report before public upload; no automatic network transfer is performed.

## Evidence / limits

Local Linux validation: 61/61 Python tests, including 23 preflight tests;
the preflight suite also executes nine cases against the actual emitted JSX
under a Node host mock. Existing panel regression: 51/51 PASS. The actual
collector executed on Linux and correctly returned BLOCKED with runtime stages
NOT RUN. These results do not verify Apple Events or After Effects behavior.

Fresh GitHub CI for the resulting commit is not yet reviewed at authoring.
No live AE execution is available in the development session. This is a
minimal environment-data request, not an installable AE Hot Loader candidate
or a release approval.

Historical `RESEARCH_RSMB_REGISTRY_FOLLOWUP_2026-09-28.md` already records all
three RSMB identities in a different process, but did not control startup or
apply/render. Reusing that observation as a cold-start PASS is prohibited.
After preflight, the next authorized runtime stage is an owned empty-project
apply/render fixture and controlled startup, with separate evidence.

## Sources

- Adobe scripting/permissions overview:
  https://helpx.adobe.com/in/after-effects/desktop/automate-in-after-effects/automate-animation/scripts.html
- Adobe-derived scripting guide, AppleScript DoScriptFile:
  https://ae-scripting.docsforadobe.dev/introduction/overview/#how-to-include-after-effects-scripting-in-an-applescript-mac-os
- Project counters/revision (dirty is supplemental, not an ownership proof):
  https://ae-scripting.docsforadobe.dev/general/project/
- Repository protocol: `docs/BRIDGE_PROTOCOL.md`.
