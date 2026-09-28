# AE Hot Loader development instructions

Before each significant stage, read and apply the current shared
[FSTR-Line DEVELOPMENT_RULES](https://github.com/ios3kov/FSTR-Line/blob/main/DEVELOPMENT_RULES.md).
Reviewed on 2026-09-28: rules blob
`a1760fde8763f789b50b91c20407938b4fcaea4a`.
Do not treat this short entry point as a replacement for the full rules.

Read `docs/DEVELOPMENT_STATUS.md` and `docs/PRODUCTION_PLAN.md` first. Reports
under `docs/archive/` and the dated baseline status describe historical source,
not current release approval. Preserve historical evidence unchanged.

For each stage: state status and scope; define acceptance and checks; record
baseline; implement the smallest related change; run available regression;
review logs; commit and update status with exact evidence and remaining gates.

Keep work in the agreed research branch. Never force-update a changed branch,
merge to main, publish or install a candidate without the relevant authorization
and gates. Preserve the generic Agent, ordinary discovery, Control Shell and
RSMB research when removing out-of-scope adapter references.

Loaded images, registry presence, effect application and rendering are separate
claims. Node mocks and native syntax checks are not live AE evidence. Do not
label unavailable runtime tests PASS; retain BLOCKED/NOT RUN with the cause.

Do not terminate a user's working AE process, delete preferences/projects or
third-party plug-ins, purge shared state, weaken security settings, or call
unverified private teardown/reinitialization functions. Automate only within
owned/authorized test workspaces.

No installable artifact handoff until the mandatory checks pass for the exact
clean, identified candidate. Source commit, Build IDs, final SHA-256, loaded
runtime identity and evidence must be traceable.
