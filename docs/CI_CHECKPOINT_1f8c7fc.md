# Host preflight checkpoint — 2026-09-28

Source: `1f8c7fc2f7955961eed96b7769ee831603d9bd11`.
Scope: minimal non-installing environment-data collector, not a product release.

## Verified automated checks

- Research run [36485879331](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36485879331), #11: SUCCESS.
- macOS run [36485879419](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36485879419), #245: build job 109142538687 SUCCESS, including all build/package and existing native gates.
- Local regression: 61/61 Python tests; 51/51 panel host-mock tests.
- The 23 new Python tests include execution of nine cases against the collector's actual emitted JSX under a Node host mock.
- Research CI also parses the diagnostic launcher using zsh on macOS.
- The copied diagnostic file was executed on Linux and returned exit 2 / BLOCKED without attempting any host subprocess. Its AE runtime stages stayed NOT RUN.

The full macOS job's success is not an After Effects runtime result. No claim
of warning-free logs is made; the existing reviewed Rust-action warning remains
outside this collector's changes. No new product package is handed over here.

## Minimal diagnostic handoff identity

File: `AEHL_Preflight_1f8c7fc.py`, byte-identical to
`tools/collect_ae_host.py` at the source commit above.

Git blob: `4496e79d41e2981e76c39bcb3defbd1c1f429415`.
SHA-256: `cfb7175f7f394b7bc17f838f8fb5337c9bee5e6fde46125570762c6d6b157865`.

The script records its own SHA-256 in the generated report. The filename
identifies this collector source; its embedded expected Agent identity still
intentionally refers to the immutable product checkpoint `04fea70` /
`native-36483421984-1`, not to an unspecified newer build. A mismatch is reported,
not repaired by installation or process control.

This is the minimal safe environment-data request permitted when the actual
Mac is inaccessible. It does not distribute or install an AE Hot Loader
candidate. It reads a running AE via DoScriptFile and sends only the diagnostic
bridge command. Working projects are not modified by the script. No native
scan, application, rendering, quit/restart, preference reset or network upload
is performed. Pending foreign bridge files block the query and are preserved.

Actual Apple Events/AE execution of this collector: **NOT RUN**. Product
ScriptUI roundtrip, controlled cold-start, RSMB apply/render, and late
registration: **NOT RUN by this collector**. The user's local report is needed
to establish the current host state before the next authorized runtime stage.

Only report.json is requested, not projects, crash dumps or entire logs.

## Documentation-only record

This file is a Markdown-only successor to the tested source. CI is skipped
for this record only; no code, test, workflow or handed-over file is altered.
The code/source checks above belong to `1f8c7fc`, not to this document's commit.
`main` and the user's installation were not modified.

See [iteration scope and safety](ITERATION_AE_HOST_PREFLIGHT_2026-09-28.md).
