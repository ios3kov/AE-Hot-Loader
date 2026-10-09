# AE Hot Loader development instructions

Start with [AE Development Rules AI_ENTRYPOINT](https://github.com/ios3kov/AE-Development-Rules/blob/04b606845e0f73ab28b9807bb45682eae4d6ce34/AI_ENTRYPOINT.md)
and select the applicable canonical modules before each significant stage.
Adopted on 2026-10-09 at the user's explicit migration request:
AE-Development-Rules **11.1.0**, tag `v11.1.0`, peeled source
`04b606845e0f73ab28b9807bb45682eae4d6ce34`.
See [current binding-predicate scope and native reconciliation](docs/C1_EFFECT_SUITE_READER_BRIDGE_2026-10-04.md#binding-predicate-packet--2026-10-09).
Previous v11.0.1 and v11.0.0 adoptions remain historical.
Previous v8.0.0 adoption and Evidence remain historical and unchanged.
Before a significant step, select risk/component/delivery rules and relevant
feature overlays (IPC, diagnostics, testing, distribution). Do not silently
replace this accepted source with the latest main. Older baseline
`b27f45467e0a9152fc82c1072438dfed07f0c36e` remains historical.
Historical FSTR-Line rule identities in dated evidence remain historical.
State the current project
stage before each significant step; do not invent a completion percentage.
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

The user explicitly permits normal quit of owned diagnostic AE sessions without
waiting for manual closure. Verify fresh PID/birth/executable and safe debugger
detach, request ordinary quit, and independently confirm absence before retirement
or another launch. Preserve unknown unsaved work; this is not permission for
force termination, save-discard, unrelated window/project reads or shared changes.

No installable artifact handoff until the mandatory checks pass for the exact
clean, identified candidate. Source commit, Build IDs, final SHA-256, loaded
runtime identity and evidence must be traceable.

For Validation, define pre-handoff safety prerequisites separately from the
intended user-validation question and final release acceptance. A pending
user-validation question does not block an otherwise safe identified test build;
missing mandatory safety checks or actual live-operation authority still block
the affected action. Full Release evaluates all applicable required checks.

Apply the adopted MAC-001 to the macOS distributable: exact artifact integrity,
documented installation, actual host loading and selected-channel evidence.
Unsigned or locally ad-hoc-signed artifacts may qualify after these checks.
Do not require paid accounts, distribution certificates or remote signing/
notarization services. Existing local signing/verification remains part of the
reviewed build profile; its PASS is not install/AE-load PASS. Do not weaken system
security or remove quarantine automatically. Windows distribution is outside
the current Mac-only native research scope; reassess WIN-001 if that scope changes.

For significant multi-block work, TASK-CLOSE-001 requires a requirement/task/
acceptance/check/Evidence mapping and final reconciliation in the existing plan
and checkpoint. FEATURE-SET-001 applies to requested feature-set changes;
preserve retained obligations. CLEANUP-001 requires an ownership-aware cleanup
assessment; unknown materials and historical evidence stay in place.
