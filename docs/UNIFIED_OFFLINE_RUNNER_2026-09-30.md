# Stage C: one run for the implemented offline checks

Date: 2026-09-30. Continues `56683d873edbafb1b489e331458c14783422b6d0` on
`research/ordinary-plugin-discovery`. Shared rules checked unchanged at blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`; AGENTS and PRODUCTION_PLAN apply.

## Scope and predeclared acceptance

The user requested one invocation and one final report instead of separate
manual test commands. This iteration consolidates **implemented offline
checks**, not unfinished AE integration. Keep the FILE/PLUG binding, no-scan
probe, live registration, render and risky-operation authorization blocked.
No additional intermediate user run is requested.

Acceptance: fixed sequential stages, clean exact source identity before and
between stages and after the run, stop after failure, retain partial logs,
report every unstarted stage as NOT RUN, one private hash-verified ZIP per run,
and no false full-pipeline PASS. Verify real child success/failure/timeout,
output bounds, dirty/changed source, archive integrity and distinct report IDs.
Run the actual complete offline sequence on Linux and macOS through CI, not
just mocked orchestration. Keep the existing full macOS product build workflow
unchanged and inspect its result separately.

## Implementation

`tools/run_research_checks.py` is the common developer/CI entry point.
`RUN_OFFLINE_CHECKS.command` invokes it from its own checkout and writes its
report to the Desktop. It is **not** the future live-AE runner and does not
install dependencies, change Git, install a plugin, or grant host permission.
Do not run the old scoped-discovery scripts expecting the new resource path.

The implemented sequence records tool versions, checks shell metadata/contracts,
runs Python discovery (which includes compilation/execution of owned native
test fixtures), then Node panel and snapshot suites. On macOS arm64 it also
checks the three native source translation units, parses the existing .command
scripts without executing them, and compiles/runs the existing 15-case scoped
guard with its mock loader. Python's real macOS LLDB/ABI tests remain enabled.
Linux's platform skips are individually recorded; they do not become passes.
No skipped Python cases are accepted in the macOS target profile.

The research workflow's existing job names are retained. Each platform runs
the same runner and uploads its single report ZIP. The full macOS build/sign/
package/smoke workflow is deliberately separate and unchanged: it already
checks an identified product package; this consolidation does not replace it
or claim the product was built by the new local command. Final live-AE and
product-package orchestration is still incomplete.

The runner accepts only an output parent and optional full expected commit;
there is no arbitrary command list, host address, scan root, consent bypass,
install or restart option. The private worker mode only runs unittest and
writes counts. Tests execute trusted checked-in code; this is not a sandbox
for malicious test source or a hostile same-UID writer.

## Source, evidence and failure semantics

Before test execution the runner checks a clean Git tree including untracked
files, records HEAD and SHA-256 of tracked bytes, and repeats that comparison
between stages and after completion. It does not stash/reset/discard changes.
Reports/work files live in a new directory outside the checkout. No previous
report is overwritten or used to satisfy this run. Snapshot checks detect
persistent changes, not an adversary changing/restoring bytes between checks.

Each fixed stage has a 120-second limit and 8 MiB combined-output limit.
Only newly created test process groups may be stopped on failure/timeout.
No process is selected by AE name or by a user-supplied PID. These are ordinary
OS timeout bounds, not a real-time guarantee for process creation, a stuck
kernel or power-loss durability. A killed runner/storage failure may leave only
partial evidence; no completed archive is claimed if packaging fails.

Reports contain SUMMARY.txt, report.json, logs and a hash manifest. They do not
include compiled executables, original Adobe libraries, or private research
uploads. ZIP entries and hashes are reread before the output is announced.
The new directory is private and the ZIP mode is 0600. No upload from the Mac
is performed. Private paths can appear in test logs; do not publish them blindly.

`offline_status=PASS` and exit 0 certify only the declared offline scope.
`full_pipeline_status` is always BLOCKED while the native host backend is
unbound. `product_package_status=NOT RUN` refers to this runner, not the
independent existing macOS CI. New live registration/apply/render is NOT RUN;
historical embedded FAIL and RSMB startup smoke PASS/late-registration FAIL
are not reclassified. The five historical audit findings remain unresolved.

## Checks and follow-through

The focused regression uses actual child processes, temporary Git repositories
and report archives. The first timeout test made an invalid assumption that a
Python interpreter would emit output within 200 ms. It was corrected to test
an owned shell/sleep process with PID/termination verification; output
preservation is separately tested on a nonzero process. No runner behavior
was relaxed to make that check pass.

Local working source was reconstructed from the independently hash-verified
macOS evidence archive for code 847b7de. GitHub comparison confirmed that only
documents changed between that code and 56683d8. This is not the user's Mac
checkout or a claim to have pulled it. Local temporary Git identity is explicitly
separate from the remote code commit tested in CI.

Pre-commit checks and exact remote CI results are recorded in the current
DEVELOPMENT_STATUS follow-up once inspected; do not infer a pass from this
implementation description. No installable AE artifact is being handed over.

The next core engineering task remains the verified FILE host-string producer/
destructor binding and a separate no-scan ownership probe, followed by review
of PLUG end-of-pass callbacks. Only after that can the actual authorized live
stages be connected to one full user run. Offline green checks do not close
those gates. Prior installation/restart permissions remain consumed; main,
installed plugins, settings and projects remain unchanged.

Implementation references: Python's [subprocess documentation](https://docs.python.org/3/library/subprocess.html)
for new process sessions and timeout limitations, and [unittest TestResult](https://docs.python.org/3/library/unittest.html)
for explicit testsRun/skipped counts. Neither documents Adobe's private ABI.
