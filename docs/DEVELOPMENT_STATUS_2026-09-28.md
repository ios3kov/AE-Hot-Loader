# AE Hot Loader — текущий статус разработки

Дата: 2026-09-28  
Ветка: `research/ordinary-plugin-discovery`  
Последний commit: `0c2fb4f test: record PiPL registration pair result`  
Состояние рабочего дерева на момент записи: clean

## Целевая конфигурация

- After Effects 25.6.0 (`25.6x101`)
- macOS Apple Silicon / arm64
- ScriptUI panel + AEGP Agent
- private AE ABI используется только для проверенного AE 25.6 arm64

## Что подтверждено

### Ordinary discovery

Для современного ordinary effect-плагина подтверждён путь:

```text
ScriptUI → Agent → ML::LoadPlugins → FLT_NotifyFilterLoadingDone
```

AE остаётся открытым. Эффект появляется в реестре, может быть применён и
отрендерен в том же процессе. Runtime Build ID проверенного Agent:
`ordinary-discovery-v1`.

### Контрольный парный тест регистрации

В одном процессе AE проверены два собственных плагина с одинаковым
`EffectMain`, PiPL и параметрами:

- PiPL-only — не зарегистрирован;
- с `PluginDataEntryFunction2` — зарегистрирован.

Evidence:

- Test Run ID: `registration-pair-2e8c5394d5e6`;
- AE PID до/после: `73375`;
- registry: `785 → 786`;
- проект: `items=0 dirty=false` до и после;
- тестовые bundles после проверки из активного test-root убраны.

Это подтверждает ограничение текущего late-loader, но не доказывает, что
RSMB несовместим с обычным startup scan.

### RSMB

Проверены реальные bundles:

- `RSMB64.plugin`;
- `RSMBPro64.plugin`;
- `RSMBVecIn64.plugin`.

PiPL всех bundles читается штатным macOS Resource Manager. RSMB использует
legacy-имя entrypoint `mainB`, но документация Adobe разрешает произвольное
имя, если оно совпадает с PiPL. Поэтому `mainB` само по себе не считается
причиной отказа.

В одной из последующих AE-сессий все три RSMB присутствовали в реестре:

```text
count=785
RSMB
RSMB Pro
RSMB Pro Vectors
```

Эта сессия не была полностью контролируемым cold-start тестом, поэтому
результат имеет статус наблюдения, а не финального startup PASS.

Текущий статус RSMB:

- обычная late-registration: **FAIL**;
- PiPL/resource readability: **PASS**;
- controlled cold-start: **NOT RUN**;
- apply/render после controlled startup: **NOT RUN**.

## In-process reinitialization

Безопасный teardown/reinitialize plugin-core при открытом проекте не найден.
Пути `SPShutdownPlugins`, `MEE_Plugins_Terminate`, filter-registry teardown и
другие private lifecycle-функции не вызываются.

Статус: **BLOCKED for implementation**.

## Control Shell

Ранее подтверждён общий stable-shell workflow:

- startup registration;
- bundled implementation;
- A→B→C reload;
- busy-render rejection;
- rollback к bundled implementation;
- работа без перезапуска AE.

Это подтверждает архитектуру shell/implementation, но не является доказательством
поддержки произвольных third-party ordinary plugins.

## ElasticGrid и Stellar Gradient

Очистка ветки от этих компонентов **ещё не выполнена на момент этой записи**.
В репозитории остаются их упоминания в README, production plan, code audit,
shell documentation и тестовых командах. Отдельные tracked-исходники
адаптеров в этой ветке не обнаружены; есть ссылки и связанные тестовые
материалы.

Планируемое действие: отдельным commit удалить adapter-specific references,
тестовые команды/fixtures и документацию, относящуюся только к ElasticGrid и
Stellar Gradient, сохранив общий Control Shell, Agent, ordinary discovery и
RSMB research.

## Последние commits

```text
0c2fb4f test: record PiPL registration pair result
3654ad0 test: keep registration pair match names within host limit
0b8299a test: add controlled PiPL registration pair
1cfe3c3 research: qualify RSMB startup registry evidence
b65f951 research: verify RSMB legacy PiPL resources
0486123 research: assess in-process plugin core reinit
```

## Следующие шаги

1. Завершить отдельную очистку ElasticGrid/Stellar Gradient из ветки.
2. Зафиксировать новый clean commit и проверить отсутствие их упоминаний в
   production scope.
3. Подготовить controlled cold-start RSMB test с уникальным Run ID,
   baseline, timeout, registry check и apply/render gate.
4. Не менять production loader до появления доказанного registration step.

## Статусы проверок

| Область | Статус |
|---|---|
| AE 25.6 arm64 ordinary discovery для проверенного modern probe | PASS |
| PiPL-only versus dynamic registration pair | PASS для заявленного наблюдения |
| RSMB PiPL readability | PASS |
| RSMB late-registration | FAIL |
| RSMB controlled cold-start | NOT RUN |
| In-process plugin-core reinitialization | BLOCKED |
| Control Shell workflow | PASS в проверенном scope |
| ElasticGrid/Stellar cleanup | NOT RUN |
