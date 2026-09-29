# Stage C: offline SDK serialization control

Rules reread in full; current remote blob remains
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
Baseline Git: `77bbd471af75daacc26e85d9da8b6ab48683183d`.
Historical interrupted resource-pair Build ID: `79a6ce4be9f7`;
its FAIL and unknown process-exit cause remain unchanged.

## Requirement and acceptance

Compare the diagnostic builder's PiPL serialization with SDK 25.6 Rez output
for identical property values, including ARM64 entrypoint and zero flags.
Require byte equality, bounded subprocesses and no host/plugin installation.
This isolates serialization, not runtime dispatch or standalone-file support.

The new RegistrationControl.r declares properties using the local SDK's
AE_General.r. check_sdk_pipl.py compiles it with Rez, extracts raw bytes with
DeRez and compares against build_registration_pair.pipl. Temporary resources
are confined to a unique owned directory. No executable is loaded.
Initial collector execution failed decoding DeRez's non-UTF8 comments;
explicit Mac Roman decoding corrected this collector error before comparison.

## Evidence

Run ID: `sdk-pipl-control-20260929T112309Z` (local macOS arm64).
Command: `python3 experiments/ordinary_discovery/check_sdk_pipl.py --sdk <SDK Examples>`.
SDK: `AfterEffectsSDK_25.6_61_mac/ae25.6_61.64bit.AfterEffectsSDK/Examples`.
New native Build ID: N/A; no native executable built or installed.

- Byte comparison: PASS, 312 bytes on each side.
- Both payload SHA-256: `d31811537dcb689cdfac4efd14635632c99be373dcd1b1e2b29fc375cdf6a526`.
- SDK AE_General.r SHA-256: `a21776f5087f4afb6a63d1c815696b44e3b68bc166546c3a9cf0a7d791eb60c5`.
- Control source SHA-256: `75be478023bb00ec6e33f9dd8c7b090622c7b3fee0d3fe9832b7863a338da7f3`.
- Python discovery regression: PASS, 92/92.
- New live AE test: NOT RUN; prior interrupted scan is not yet diagnosed.
- Legacy late-registration repair: BLOCKED; no safe corrective step proven.

Static skill audit exited 1: three unpinned Actions and default checkout
credential retention in the pre-existing dual-pipl workflow are confirmed
hardening debt outside this experiment. The rate-limit warning at
tools/artifact_manifest.py:71 is a false positive: local argparse CLI, no HTTP
route. No whole-product audit PASS or release readiness claim is made.

## Decision

The tested serialization matches the SDK; do not change byte order blindly.
This is one controlled value set, not exhaustive serialization verification.
It does not prove AE accepts a standalone .PiPL file, that resource bytes reach
the late-registration parser, or that the flat fixture caused process exit.
Next isolate standalone-file parsing versus embedded-resource dispatch and
obtain request/PID-correlated diagnostics before another live scan. A scoped
scan must be demonstrated, not assumed: the current Agent scans shared roots.
Do not repeat the failed full-root scan, change production loader behavior,
switch product scope to Shell, or restart/install into the working host here.

Reference: https://ae-plugins.docsforadobe.dev/intro/pipl-resources/
