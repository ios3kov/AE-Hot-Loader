# AE Hot Loader — current development status

Updated: 2026-09-30. Branch: `research/ordinary-plugin-discovery`.
Current stage: **C of A–D**, with remaining gates in A/B/D. No completion
percentage or release approval is assigned. Follow [PRODUCTION_PLAN](PRODUCTION_PLAN.md).
Shared DEVELOPMENT_RULES rechecked at unchanged blob
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`; AGENTS.md remains applicable.

The preceding chronological status is retained verbatim at
[immutable checkpoint e9993ef](https://github.com/ios3kov/AE-Hot-Loader/blob/e9993ef081b1cd0e7080064ec5ddbe0c716e2e0a/docs/DEVELOPMENT_STATUS.md),
rather than duplicating historical "current" and "next" instructions here.
Dated evidence records are unchanged. This page describes development state;
it does not reclassify historical results or identify a new tested native build.

## Latest evidence — main executable imports implementation from AfterFXLib

The supplied `AEHL-factory.Z7cgNu.zip` was inspected and hashed. Matching
before/after statements report main executable SHA-256
`464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6`.
The binary itself was not supplied for independent hashing.

The symbol table attributes EggMain and startup imports to AfterFXLib; its
arm64 dependency list names AfterFXLib.framework. AfterFXLib is therefore the
next concrete search target, NOT a proven owner of the selected factory.
The concrete factory, PiPL acceptance and reason for registration failure remain
unresolved. [Input identities, findings and limits](FACTORY_MAIN_IMAGE_2026-09-30.md).

Earlier [PluginSupport analysis](REGISTRATION_DISPATCH_STATIC_2026-09-30.md)
showed that ML::LoadPlugins returns a candidate count, not registered-effect
count. Its final bool restricts factory selection; this does not prove true is
wrong. Recognition and returned-reference handoff already occur inside AddPlugin.
Do not flip that bool or insert speculative notification/registration calls.
The [original scoped logs](REGISTRATION_GAP_SAVED_LOGS_2026-09-30.md) were
verified against their previously recorded hashes. Their output vector is empty
and its recorded signature describes strings, not unconsumed plugin objects.

## New file-only collector and exact identity

Added `experiments/ordinary_discovery/collect_factory_image.py` in `d31b8da`.
Code/test checkpoint: `9fdb39b751c96f6e34adcf5df9d8f94183153b37`.
Collector Git blob: `f72624c35389eedf3ccb9c6b226b5acb2c8d7b15`.
Collector SHA-256:
`10097a09b97876d6bbf4fce9c5abf5a5ebc300826d5dfefac906859a8863f89c`.
The standalone chat copy `AEHL-collect-factory.py` is byte-identical.

It reads the known AfterFXLib file, gathers symbols/dependencies/headers and
at most 96 address-selected offline disassembly windows, each bounded to 4096
bytes or the next known text symbol. It records omitted/capped windows, input
hashes and file hashes in a new private Desktop archive. These are heuristic
windows, not guaranteed complete functions or exhaustive factory coverage.

The collector never attaches to, launches, scripts, stops or scans AE. LLDB
creates an offline target with no dependents and script/init loading disabled.
Tool invocations are bounded; failure preserves partial evidence. Main-image
identity is pinned; AfterFXLib's own hash is a first observation, not a prior
independent identity assertion. It does not modify the installed files.
This is a diagnostic data request, not an installable AE product handoff.

## Verification for the new collector

| Check | Result and exact scope |
|---|---|
| Focused local parser/command tests | PASS, 20 synthetic tests, Python warnings treated as errors |
| Additional full-flow checks | PASS, five mocked scenarios; committed counterparts also passed in research CI |
| Exact collector bytes vs Git blob | PASS |
| Research CI for 9fdb39b | PASS, run 36745551046; native-syntax and panel-contract |
| Python in research Linux CI | 176 collected: 172 PASS, four macOS-only supervisor cases skipped |
| New committed collector tests in that job | PASS, all 25, no real Adobe-image execution |
| Node in research CI | PASS, 51 panel + 11 snapshot tests, no AE |
| Full macOS CI for 9fdb39b | IN PROGRESS at this record, run 36745551281; no final PASS asserted |
| Preceding macOS CI for 0ca114dd | CANCELLED, run 36745344719; skipped later stages are not PASS |
| Actual new collector run on user's Mac | NOT RUN; next requested data collection |
| Local real LLDB execution | BLOCKED: Linux LLDB cannot start without its libpython3.11 dependency |
| Full static-security audit | NOT RUN again; five historical findings remain unresolved |

The research job 109990710114 log was read: checkout 9fdb39b, exact test names,
counts and four skips were verified. Evidence artifact 11112107888 has the
Actions-reported upload SHA-256
`0edf298e6f96ddac15b147846ba7ab11b6362894e0e106cbde3f4ab683e6ac7e`.
This is not an independently downloaded archive hash. CI annotations are not
cleared by green jobs; no warning-free claim is made. Documentation follow-ups
use [skip ci]. A documentation head is not a newly tested native artifact.

## Last real host results — retained separately

| Gate | Result |
|---|---|
| Scoped embedded late registration | FAIL: source 45de0c9, Build ID scoped-0b8c8f122e80, fixture 88019a1a01a7; 785 unchanged effect identities, target absent |
| RSMB startup-registered apply/render smoke | PASS: the previously identified one-frame test, not broad compatibility certification |
| RSMB late registration | FAIL: historical result, not repaired by the startup smoke |
| Dynamic fixture application | PASS: earlier exact-match add/remove gate; render NOT RUN |
| Earlier flat-resource failure | FAIL: historical crash evidence remains, not declared fixed |
| Fresh current AE/project/runtime identity | BLOCKED: no direct Mac access or fresh identified project snapshot |

See [scoped host test](SCOPED_USER_HOST_2026-09-29.md),
[RSMB apply/render](RSMB_APPLY_RENDER_PASS_2026-09-29.md),
[Dynamic application](REGISTRATION_APPLY_PASS_2026-09-29.md) and
[flat-resource crash correlation](RESOURCE_PAIR_CRASH_CORRELATION_2026-09-29.md).
The previously supplied PID 78417/start-time observation is not a current
blank/clean/idle project baseline. Local Mac source was last reported as ce5d80d;
no pull, installation or local update is claimed.

Reference product package remains source
`04fea7060c7ef7ebc4a315b5c39364850287e294`, Build ID `native-36483421984-1`.
[Reference identity and checks](CI_CHECKPOINT_04fea70.md). Nothing in this
continuation replaces the installed Agent, shell, panel or third-party effects.

## Next safe gate and remaining work

Run only the exact standalone collector on the Mac and inspect its new archive.
It does not need AE open. Missing files, hash changes or tool failures stop
collection; do not regenerate the failed scan. After receipt, locate the
concrete factory and trace its PiPL acceptance and module-publication path
using the actual bounded windows and their declared limitations.

Any subsequent risky host operation needs a falsifiable hypothesis, bounded
instrumentation, fresh host/project/loaded identity and separate authorization.
The previous installation and one-restart permission are consumed. No speculative
private dispatch, teardown, unload, preference reset or unchanged scan is allowed.

Remaining production gates include scope cleanup, controlled RSMB cold-start
causality, a demonstrated safe late-registration operation, separate apply/render,
real ScriptUI roundtrip, IPC ownership/reopen/timeout/repeat checks, compatibility
and the final clean-candidate gate. No native source, production installation,
main, merge or release was changed by this continuation.
