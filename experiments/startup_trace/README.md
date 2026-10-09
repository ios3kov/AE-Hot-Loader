# Owned normal-startup register trace

This experiment answers one bounded question: do the normal writer and the
actually acquired public match-name reader use the same own FCSpec/registry
receiver? It never invokes a private function or publishes a late effect.

`core.py` validates a strictly ordered, bounded chain for one PID/birth/main
thread. `image.py` parses original file bytes. `profile.py` admits only pinned
Adobe images/sites and exact trace-enabled own bundles, or the isolated fixture.
`lldb_collector.py` launches a fresh target, captures registers at admitted PCs,
removes its breakpoints and detaches. `launch.py` retains debugger stdin until
safe detach/exit is recorded. No expression evaluation, object memory reads,
existing-process attach, target kill, project mutation, Apply or render.

The trace-enabled SDK pair exports inert noinline sentinels. Its observer repeats
one public GetEffectMatchName call only after identifying its own match name on
the main thread within the original request deadline. The default build retains
its prior behavior. Target files and symbol-derived sentinel addresses are pinned
before execution; loaded PC/module/path and acquired function are checked live.

## Controls and admission

Run `python3 -m unittest discover -s tests -p test_startup_trace.py` for synthetic
order/identity/budget/file refusals. These inputs never count as AE evidence.
`fixture.py` creates one tiny executable under a fresh private
`build-ae-hot-loader/trace-fixture-*` directory. `launch.py --profile <absolute>
--sha256 <digest> --output <fresh absolute directory>` permits only that fixture.
Use a supported debugger environment; a sandbox transport failure is retained.

For AE, first commit the reviewed source, run the research checks and build the
exact SDK candidate with startup_calibration/build.py `--trace-identity`, its
expected commit, fresh run ID and prospective host/module pair. No preparation
command installs or launches AE. Only `launch.py --manifest <absolute manifest>
--sha256 <digest> --transport-proof <absolute fixture result> --transport-sha256
<digest> --execute-owned-startup` admits a unique pair and one new host.
It first requires a complete safely detached fixture result for the exact clean
source/collector bytes; a partial/stale/synthetic result does not establish that
runtime gate. It refuses an existing AE/aerender, used control directory, changed image/source,
unknown site, different callback/key/root/descriptor, worker thread, replay or
budget exhaustion. READY permits one read-only registry request; SDK receipt must
independently agree with the register trace. A publication failure stays UNKNOWN;
no retry, fallback, private call or deadline renewal is permitted.

Successful register correspondence is not atomic commit, full ownership,
complete render-readset or hot-add proof. C1 remains PARTIAL; C2/late-add NOT_RUN.
The host remains for manual closure. Exact owned bundles must be retained outside
plugin discovery only after fresh host absence and bundle/inventory verification.

Limits: startup180s; subsequent controller120/native110s;256 accepted events and
256 stop events;1MiB trace/log bytes. A blocked synchronous debugger launch may
not return to the collector deadline loop: the launcher records MANUAL_ATTENTION
and retains the debugger. The real fixture must verify launch/stop/detach behavior for each exact
source before AE admission. Never auto-quit an unknown target.

LLDB API reference: [SBTarget](https://lldb.llvm.org/python_api/lldb.SBTarget.html),
[SBProcess](https://lldb.llvm.org/python_api/lldb.SBProcess.html),
[SBLaunchInfo](https://lldb.llvm.org/python_api/lldb.SBLaunchInfo.html).

Journal final paths become visible only after full write/flush/fsync and exclusive
hard-link publication. Failed publication retains a pending file and does not
replace an existing receipt. Ambiguous stops refuse and retain bounded thread
reason metadata; no unknown frames/registers or object memory are inspected.

`--retire-owned-pair` may validate a historical admission after collector source
changes, while retaining exact image/site/candidate/bundle checks and two fresh
host-absence guards. This cleanup-only source comparison exception never admits
execution. Installation bytes are moved outside discovery and retained.

The58a0673 AE attempt observed four callback/conversion/PiPL events, then refused
an ambiguous stop; writer and reader were not reached. The post-run corrections
are separate from that historical native evidence. See the current C1 checkpoint.
