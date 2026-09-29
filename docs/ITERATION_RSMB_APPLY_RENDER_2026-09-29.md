# Controlled RSMB apply/render gate — 2026-09-29

## Baseline before implementation

Private host evidence confirms After Effects 25.6x101 is currently running with
a blank, unsaved, clean project. Resident Agent identity exactly matches source
`04fea7060c7ef7ebc4a315b5c39364850287e294`, Build ID
`native-36483421984-1`; all three RSMB registry match names are present.

The private report is not committed. DEVELOPMENT_RULES blob
`a1760fde8763f789b50b91c20407938b4fcaea4a` was reviewed before this stage.

## Goal / acceptance

This gate proves only that startup-registered `Smart Motion Blur 3.x` can be
added by exact match name and render one 64x64 frame, while preserving the
required blank/clean host state.

Required gates: fresh Agent identity PASS; exact blank/clean preflight; exact
RSMB registry presence; `canAddProperty` and `addProperty` success; non-empty
owned render output; disposable test project closed with
`DO_NOT_SAVE_CHANGES`; blank/clean postflight; same AE PID; output SHA-256.

No `reload_plugins`, installation, third-party mutation, preference reset,
project save/open, AE quit/restart or private teardown is part of this stage.
Cold-start causality and late registration remain separate.

## Existing mechanism / research

The project already used Effect Parade add + Render Queue in
`experiments/ordinary_discovery/render.jsx`. Current scripting docs confirm
match names are valid for `canAddProperty` / `addProperty`, OutputModule.file
is writable, and RenderQueue.render() is synchronous:

- https://ae-scripting.docsforadobe.dev/property/propertygroup/
- https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/
- https://ae-scripting.docsforadobe.dev/renderqueue/renderqueue/
- https://ae-scripting.docsforadobe.dev/general/application/

## Implementation

`experiments/ordinary_discovery/render_rsmb.jsx` refuses mutation unless the
current project is exactly blank, unsaved, clean and idle. It then creates a
disposable project, applies RSMB, renders one frame, closes without saving and
recreates a blank project. Its companion command runs the existing read-only
Agent/RSMB preflight before and after the JSX, verifies the AE process did not
change and writes SHA-256 evidence for render output.

The outer Apple Event/subprocess timeout bounds the client wait but cannot
forcibly cancel work already accepted by AE; the render is intentionally one
64x64 frame to reduce this risk. This is a render compatibility smoke only,
not temporal-quality, MFR, bit-depth, color, performance or license coverage.

Real AE apply/render status remains **NOT RUN** until the user's host executes
the checked runner.
