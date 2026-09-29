# Stage C: recovered crash evidence for the resource-pair timeout

Shared rules blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608` rechecked.
This record extends, rather than rewrites, the initial
[resource-pair gate](RESOURCE_PAIR_GATE_2026-09-29.md). Its overall FAIL remains.
Objective: establish whether the observed missing AE process was a crash in
the same scan, using a recovered local minidump. Acceptance: exact PID,
time window and Agent-to-PiPL stack chain; preserve the dump and working AE.

## Identities and evidence

- Original run ID: `late-a60748b4fc87423f9ed6a4f4ba612aae`.
- Original fixture source: `ddf42e55850a5afbd3c6135eca27731d0bcb5252`;
  Build ID `79a6ce4be9f7`.
- Baseline resident Agent Build ID `native-36483421984-1`, source
  `04fea7060c7ef7ebc4a315b5c39364850287e294`; identity PASS then.
- Correlation collector source: `ce5f5a36a20e99db0f7c4c5352a38b4876afd277`,
  clean. No new native/plugin Build ID; this is a read-only diagnostic script.
- Analysis run ID: `crash-link-5baa173057ff4bb091ef8fed4d725c69`.
- Local sanitized record:
  `build-ae-hot-loader/evidence/<Analysis Run ID>/record.json`, SHA-256
  `1b695d33674223eaaf425fe82ae0f083d44a46b65a0b093e9d1beeb323c57520`.
- Original baseline/result SHA-256:
  `81fa63aa1e4c724db0440d20c498cc88ac4c1cd8bcbb5ed0de2f7cd46c351e43`
  / `fb1018541f4f9f10589907887fb17b914d6841be57dc0c0ff9aaa24437f316e9`.
- Crashpad minidump SHA-256:
  `4fafb3612fda558ed4f5454e698709665a55172113367af4ad2b863d4d81ef25`.
  The raw dump stays in the user's existing local Crashpad store; it is not
  copied into Git, logs or a distributable artifact. The record omits paths,
  project data and raw stack memory.

## Recovered observations

Baseline file was written at 13:13:19 local time. Minidump header time is
11:13:21 UTC (13:13:21 local); Crashpad completed it at 13:13:22. The
result FAIL was written at 13:14:20. Minidump process PID 21778 matches the
baseline PID 21778 and the subsequently absent PID. The exception is
`EXC_BAD_ACCESS`, followed by Adobe's signal handler and abort path.

The crashing thread's recovered chain includes, in order toward the Agent:

`ML::PiPL::LoadFromResource(module, CFURL*)` →
`ML::PluginImpl::InternalLoadPiPLs` →
`ML::PluginImpl::LoadPiPLs` →
`ML::PluginImpl::GetPiPLs` → `ML::AddPlugin` →
`ML::LoadPluginList` → `ML::LoadPlugins` →
`AEHotLoaderAgent::LoadPluginFolder` → Agent discovery idle hook.

This confirms that the failed run caused a real AE crash during PiPL URL
loading through the ordinary scan. It also confirms the fallback receiver was
PluginImpl in this stack. The old shared log did not establish either fact.

The minidump contains the exact test flat fixture name
`AEHLPairFlat79a6ce4be9f7`. That supports attribution but does not identify
the CFURL argument or prove the precise faulting file. The signal handler
obscures the original faulting instruction; `LoadFromResource +144` is a
recovered return/caller location. The raw flat PiPL's byte order is a strong
specific hypothesis, not a proven exception cause. Do not claim a host bug,
RSMB fix or arbitrary third-party crash on this evidence.

## Disposition and next gate

| Check | Status | Scope |
|---|---|---|
| PID/time/stack correlation | PASS | Exact original run and recovered minidump |
| Original resource-pair discovery gate | FAIL | AE crashed before matching bridge response |
| Exact faulting CFURL and instruction | BLOCKED | Not recovered from available dump |
| Registry and independent postflight | BLOCKED | AE process terminated |
| New in-AE experiment | NOT RUN | No repeat scan |
| Python regression after safeguard | PASS | 93/93 |
| Static code audit | FAIL | Five pre-existing workflow/heuristic findings |

The research builder now requires an explicit offline-only opt-in to reproduce
the retired flat pair. Safeguard source `9a35e66`; default resource-pair build
fails before output creation. Historical files and evidence remain intact.

Next runtime investigation must use an isolated AE host, one owned embedded
resource fixture, a scoped root, and request/PID-correlated crash evidence.
First prove the scope is isolated from user/third-party plug-ins. Observe
registry state separately from loader return. No production loader change,
private teardown, host restart, install, merge or release was performed in
this diagnostic stage.
