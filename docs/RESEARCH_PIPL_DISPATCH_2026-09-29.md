# Stage C: flipper lifetime and PiPL dispatch, offline

Rules blob: `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608` (unchanged).
Objective: determine whether the exact AE 25.6 arm64 PluginSupport image
installs its resource byte converter before the normal PiPL fallback and
identify the method selected by the virtual call. Acceptance: a repeatable
read-only collector, exact image hash, calls and vtable entries mapped without
executing the image. This is static evidence, not proof of the path taken by
the failed live scan.

## Identity

- Collector source: `6aab977101aa00240350d05d8d00aacb5cbf833e`, clean.
- Inspected image SHA-256:
  `4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`.
- Run ID: `pipl-static-4f966662b8ea4136bfa0c105bc66c0b9`.
- Local evidence: `build-ae-hot-loader/evidence/<Run ID>/record.json`,
  `disassembly.txt`, `vtables.txt`. Adobe disassembly remains local/ignored.
- Disassembly SHA-256:
  `38de20a6c2a480891eaebb381c53abad93edb405021f2784064bed2a47db38b9`.
- Vtable dump SHA-256:
  `09fbd4ca502b85649f5f5461453e539f356033407a48a0c7c20785b0bb2e92e5`.
- New native Build ID: N/A; no plugin or Agent was built, installed or loaded.

Reproduce with `python3 experiments/ordinary_discovery/inspect_pipl_fallback.py
--profile dispatch --image <exact PluginSupport path> --output-parent
build-ae-hot-loader/evidence` on the identified host. The collector uses
offline LLDB target creation and otool; it never launches or attaches to AE.

## Observations

1. `ML::PluginImpl::GetPiPLs` at 0x4c72c first returns cached data if present.
   Otherwise, at 0x4c77c it constructs `InstallPiPLFlipper`. At 0x4c790 it
   attempts dynamic PluginData. When no PiPL results exist, it dispatches the
   virtual slot +0x88 at 0x4c7e0. It destroys the flipper at 0x4c918 on the
   ordinary exit path (and at 0x4c968 on the inspected exception path).
2. The flipper constructor at 0x45f64 calls `CoreEndianGetFlipper` and can
   install Adobe's `PiPLEndianFlipProc` for the Resource Manager/PiPL type.
   Its destructor at 0x45ff8 can restore a previously found callback. The
   exact callback state in a particular AE process remains unobserved.
3. The AEPlugin vtable's slot corresponding to +0x88 points to 0x210c,
   `ML::AEPlugin::LoadPiPLs`; the PluginImpl vtable's slot points to 0x4d164,
   `ML::PluginImpl::LoadPiPLs`. The code at 0x210c tries the AEPlugin module
   and calls 0x4d164 if the result remains empty. Both can reach
   `InternalLoadPiPLs` at 0x4ca10. The actual receiver type at the late scan
   is not established by a vtable dump.
4. As separately recorded, `InternalLoadPiPLs` enumerates standalone PiPL
   URLs before falling back to Resource Manager ID 16000. The inspected base
   URL reader copies file bytes; the Resource Manager path can invoke a PiPL
   converter. The standalone public API control confirmed this distinction
   for a bounded header in its own process.

## Assessment and next gate

The image contains a coherent route from the ordinary GetPiPLs call to an
installed Resource Manager converter and then to AEPlugin/PluginImpl PiPL
loading. This weakens the blanket hypothesis that AE lacks PiPL conversion.
It does not establish that late-discovered PiPL-only bundles take this route,
that parsing succeeds, or that AE inserts a new effect into its registry.

The raw standalone `.PiPL` fixture remains unsuitable for another live scan:
its disk header has a 201326592 native-order count if passed through without
conversion. Its earlier timeout/host exit remains FAIL with unknown cause.
Do not infer that it caused the exit, change third-party bytes, or invoke a
private registration/teardown routine from this static evidence.

Next design a bounded, isolated host trace using only a new embedded-resource
fixture, with request/PID correlation, safe baseline, and explicit observations
at resource read, parsed PiPL and registry insertion. The current shared-root
scan and user-working AE are unsuitable for a speculative repeat. Obtain an
owned isolated host before that runtime gate. A controlled cold-start RSMB
gate, render-capable late fixture and product panel/IPC gates remain separate.

| Check | Status |
|---|---|
| Offline collector, exact image and vtable capture | PASS |
| Python regression after collector commit | PASS: 92/92 |
| Diff whitespace check | PASS |
| Static code audit | FAIL: five pre-existing candidates; review required |
| In-host receiver/flipper invocation | NOT RUN |
| PiPL-only late registration | FAIL: historical live gate, unchanged |
| Safe corrective registration step | BLOCKED: not demonstrated |

The static audit findings are the previously reviewed unpinned CI actions,
checkout credentials and one false-positive CLI rate-limit heuristic. No
product or release gate was promoted to PASS by this research.
