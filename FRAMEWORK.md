# AI Development Forge v4.6 — Architecture

## Configurable planner/reviewer routing

`epic-planner` and `reviewer` keep neutral definitions and native agents on both platforms. One required `.ai/project.yaml` value selects both roles: `claude_with_codex` means Claude Code orchestration plus the managed `codex-plugin-cc` route; `codex_with_claude` means Codex orchestration plus managed headless Claude Code; `native_subagents` uses the active platform's internal agents. Cross-provider preflight or runtime failure never switches provider implicitly.

Этот документ описывает реализованную архитектуру фреймворка и её обязательные lifecycle-контракты.

## Назначение

AI Development Forge превращает репозиторий в долговременную среду разработки, где:

- продуктовые и архитектурные цели утверждаются пользователем;
- execution-состояние восстанавливается из файлов, а не из истории чата;
- сильная основная модель оркестрирует специализированных субагентов;
- Codex CLI и Claude Code CLI получают нативные adapters из одного нейтрального источника;
- каждый lifecycle-переход имеет явный gate.

## Структура проекта-потребителя

```text
project/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── SPEC.md
├── ARCHITECTURE.md
├── BACKLOG.md
├── DECISIONS.md
├── decisions/
│   └── ADR-NNN-<name>.md
├── execution/
│   ├── active/EPIC-NNN-<name>/
│   │   ├── plan.md
│   │   └── tasks/TASK-NNN-<name>.md
│   ├── planned/EPIC-NNN-<name>/
│   │   ├── plan.md
│   │   └── tasks/TASK-NNN-<name>.md
│   ├── paused/
│   └── completed/
├── quality/mutation-testing/       # optional, создаётся первым явным запуском
│   ├── registry.yaml
│   └── runs/MUT-NNNN.yaml
├── .ai/
├── .codex/agents/
├── .agents/skills/
├── .claude/agents/
└── .claude/skills/
```

Эта структура относится к целевому проекту. Репозиторий исходников Forge не проходит собственный bootstrap.

## Источники истины

| Информация | Единственный владелец |
| --- | --- |
| Целевое поведение продукта | `SPEC.md` |
| Целевая архитектура | `ARCHITECTURE.md` |
| Epic, приоритет, readiness, status и дефекты | `BACKLOG.md` |
| Содержание одного архитектурного решения | соответствующий ADR |
| Навигация по решениям | генерируемый `DECISIONS.md` |
| Стратегия Epic, порядок TASK, verification и fuzzing plans, Epic Validation, fuzzing outcome и user validation | `plan.md` |
| TASK scope, status и implementation/review/test/user evidence | соответствующий TASK-файл |
| Независимая история mutation testing | `quality/mutation-testing/` |
| История файлов | Git |

`README.md`, root routers, agent-файлы и `SKILL.md` являются инфраструктурой, но не владельцами execution-состояния.

## Слой `.ai/`

`.ai/` — копируемый framework bundle:

- `BOOTSTRAP.md` и шесть numbered workflows;
- `CONVENTIONS.md`;
- `framework/manifest.yaml` с release, ownership, agent и skill IDs;
- `framework/contracts.yaml` с lifecycle, transitions, gates, fuzzing и независимыми mutation-testing contracts;
- одиннадцать нейтральных agent definitions;
- шестнадцать portable skills;
- canonical и adapter templates.

Ownership разделён на три категории:

- framework-owned release files поставляются текущей версией Forge;
- project-owned `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, optional `quality/mutation-testing/`, canonical и execution-файлы сохраняются;
- generated adapters пересоздаются после collision preview.

## Канонические документы

`SPEC.md` описывает утверждённое target behavior через наблюдаемые `FR-*`, измеримые `NFR-*` и инварианты `BR-*`.

`ARCHITECTURE.md` связывает requirement drivers с компонентами, dependency rules, data ownership, interfaces, trust boundaries, runtime, reliability, observability, testing и эволюцией данных.

`BACKLOG.md` содержит только:

- Epic Roadmap;
- Defect Queue.

Все сохранённые будущие идеи становятся `PLANNED` Epic. `OUTLINE` разрешает сохранить неполную идею; `READY` требуется для активации.

ADR является авторитетным решением. `DECISIONS.md` генерируется из ADR frontmatter и служит только индексом.

`plan.md` не хранит TASK status. TASK-файл хранит единственный lifecycle status, revision/fingerprint evidence и компактные summaries. Approved detailed plans для ещё не активированных Epic находятся в `execution/planned/`; все их TASK остаются `TODO`.

Несколько `execution/planned/EPIC-*` могут существовать одновременно. Они не создают новый Epic status: Backlog сохраняет `PLANNED + READY`, а приоритет и порядок определяются только строками Backlog. Plan Approval пишет planned workspace. Epic Start отдельно требует satisfied dependencies, пустой `Blocked by`, отсутствие другого active-work Epic и атомарно выполняет move `planned → active` вместе с `PLANNED → ACTIVE`.

## Идентификаторы и язык

ID глобальны внутри проекта и не переиспользуются:

```text
EPIC-001
TASK-001
BUG-001
ADR-001
MUT-0001
```

Следующий ID равен максимальному существующему ID данного типа плюс один. TASK numbering не начинается заново в каждом Epic.

Framework control layer написан на английском. Канонические документы генерируются на языке общения пользователя. Технические IDs, status values, paths, commands и model IDs остаются английскими.

## Dual-platform generation

Один набор neutral sources генерирует:

| Codex | Claude Code |
| --- | --- |
| `AGENTS.md` | `CLAUDE.md` |
| `.codex/agents/*.toml` | `.claude/agents/*.md` |
| `.agents/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` |

`AGENTS.md` — единственный полный root router и ограничен 150 строками. `CLAUDE.md` содержит только `@AGENTS.md`, поэтому Claude Code импортирует тот же router без дублирования. `.ai/project.yaml` хранит `role_execution.mode` и сопоставляет tiers с конкретными моделями и effort. Framework defaults:

| Tier | Codex | Claude Code |
| --- | --- | --- |
| `strong` | `gpt-5.6-sol`, `medium` | `opus`, `medium` |
| `balanced` | `gpt-5.6-terra`, `medium` | `sonnet`, `medium` |
| `fast` | `gpt-5.6-luna`, `medium` | `haiku`, `medium` |

Проект может явно переопределить defaults. Aliases и полные model IDs поддерживаются; скрытая замена tier запрещена.

В режиме `native_subagents` генерация применяет к Claude Code режимный override `effort: high` для всех native agents. Он не изменяет Codex agents или effort внешнего маршрута `codex_with_claude`.

`.ai/framework.lock` хранит версии и hashes neutral sources и generated outputs, чтобы обнаруживать drift и ручные изменения.

## Оркестратор и субагенты

Основная сессия — сильный оркестратор. Для неё нет subagent-файла. Только оркестратор:

- общается с пользователем;
- вызывает skills и agents;
- маршрутизирует findings;
- изменяет canonical status;
- управляет gates.

| Agent | Tier | Ответственность |
| --- | --- | --- |
| `context-collector` | fast | локальное canonical/execution/Git/code evidence |
| `documentation-researcher` | fast | официальная внешняя документация |
| `epic-planner` | strong | read-only Epic decomposition, risks, review focus и verification planning |
| `implementer` | balanced | одна TASK, production-код и тесты |
| `reviewer` | strong | независимый read-only review |
| `tester` | fast | selected focused, affected, bounded fuzz smoke и scoped Task checks |
| `epic-validator` | balanced | полный regression, project-wide checks, critical paths и quality profiles |
| `fuzzer` | balanced | воспроизводимый Epic fuzzing без исправлений, когда план или итоговые evidence требуют вызов |
| `security-auditor` | strong | явный on-demand local security audit |
| `mutation-runner` | fast | bounded baseline и mutation-backend execution с normalized runtime evidence |
| `mutation-analyzer` | strong | отдельно разрешённый semantic analysis только текущих mutation candidates |

Субагенты не вызывают друг друга. Одновременно выполняется не более одной code-writing TASK; независимый read-only research может выполняться параллельно.

## Skills

Шестнадцать skills сгруппированы по назначению:

- bootstrap нового и существующего проекта;
- feature/bug/external-work intake и reprioritization;
- Epic preparation и durable resume;
- Task execution/completion и Epic completion;
- security audit;
- standalone mutation testing;
- framework conformance check;
- adapter synchronization.

Codex вызывает skill как `$forge-...`, Claude Code — как `/forge-...`. Mandatory lifecycle использует явный skill routing, а не только implicit matching.

Feature discovery и root-cause investigation встроены в intake skills. Test-driven implementation и evidence-before-transition встроены в Task lifecycle и role-specific agent contracts. Внешние process skills не управляют gates, canonical artifacts, status transitions, agent routing или Git actions.

## TASK delivery tracks

Фреймворк определяет ровно два delivery track: `fast` и `standard`. Delivery track независим от model tier и `risk level`: названия model tier не выбирают процесс, а низкий риск без доказанной ограниченности не разрешает `fast`.

Fast eligibility является fail-closed. TASK должна быть ограниченной, обратимой и однозначной, а её проверка — детерминированной и локальной. `fast` запрещён для публичных контрактов, auth/security/privacy, persistence и форматов данных, schema/migration, concurrency/shared core, dependency/build/package/deploy/runtime infrastructure, внешних интеграций, critical paths, ослабления тестов и любой неопределённости в surface или verification. Все остальные TASK получают `standard`; legacy TASK без поля track также считается `standard`.

Оба track используют implementer и сохраняют focused RED/GREEN. `fast` не вызывает reviewer или tester: оркестратор независимо проверяет актуальный fingerprint, границы diff, test integrity и повторяет утверждённые checks. `standard` сохраняет strong reviewer и tester. Провал fast assurance, изменение eligibility или сомнение немедленно повышает TASK `fast → standard`; `standard → fast` после Task Start запрещён.

## TASK lifecycle

```text
TODO
  → IN PROGRESS
  → fast: orchestrator assurance
  → standard: IN REVIEW → IN TESTING
  → AWAITING USER ACCEPTANCE
  → DONE
```

Также поддерживаются `PAUSED` и `CANCELLED`. Блокировка хранится отдельно в `blocked_by`.

Общий цикл выполнения:

1. отдельный Task Start;
2. implementer пишет код и необходимые тесты;
3. для `fast` оркестратор выполняет fast assurance без reviewer/tester и при успехе переводит TASK прямо в `AWAITING USER ACCEPTANCE`;
4. для `standard` Review Packet классифицирует production и supporting paths и фиксирует whole-implementation и production-surface fingerprints; strong reviewer по ordered protocol проверяет production surface, а tester запускает focused, selected affected, применимый bounded Task fuzz smoke и scoped quality checks;
5. пользователь тестирует вручную;
6. отдельный Task Acceptance переводит TASK в `DONE`.

В `standard` изменение production surface инвалидирует прежние review и test evidence и требует нового strong review; supporting-only изменение при неизменном production fingerprint сохраняет clean review и повторяет tester gate. В `fast` любое изменение инвалидирует fast assurance и требует его повторения, а потеря eligibility повышает TASK до `standard`. Commit запрещён до явного Task Acceptance и перехода в `DONE`. При `manual` policy после acceptance требуется отдельное разрешение на commit. Task Acceptance не запускает следующую TASK без отдельного разрешения.

## Epic lifecycle, validation и fuzzing

```text
PLANNED → ACTIVE → VALIDATING → FUZZING → AWAITING EPIC ACCEPTANCE → COMPLETED
```

Также поддерживаются `PAUSED` и `CANCELLED`.

При подготовке Epic `epic-planner` создаёт evidence-based Epic Fuzzing Plan с applicability, targets, harness readiness, Task mapping, reproducible campaign и alternative risk coverage. Каждая TASK отдельно хранит `Fuzzing impact` и `Task fuzz smoke` в своём Verification Plan.

После принятия последней TASK отдельный `epic-validator` на точном aggregate fingerprint запускает полный project suite, project-wide lint/typecheck/build, integration/E2E, requirement coverage и применимые quality-profile gates. Только `PASSED` или `PASSED WITH ACCEPTED EXCEPTIONS` после явного принятия риска переводит Epic в `FUZZING`.

В `FUZZING` оркестратор не вызывает fuzzer для approved `not applicable`, только если все итоговые Task impacts равны `none`, affected surface совпадает с планом, alternative coverage прошёл и fingerprint актуален; тогда он записывает `NOT APPLICABLE`. Для `applicable`, `unresolved` или противоречащих итоговых evidence автоматически запускается read-only fuzzer. Fuzzing gate сохраняет четыре outcome:

- `PASSED`;
- `NOT APPLICABLE` с rationale и alternative risk coverage;
- `HARNESS REQUIRED`;
- `FINDINGS`.

Harness или remediation создаются как новые TASK через Replan и собственный Task Start. После изменений повторяется assurance выбранного delivery track, затем полный Epic Validation и fuzzing.

Только отдельный Epic Acceptance завершает Epic и перемещает его каталог в `execution/completed/`. Следующий Epic автоматически не активируется.

## Quality gates и project profiles

Universal Task baseline требует approved definition и boundaries, выбранный delivery track, objectively verifiable acceptance criteria, affected surface и risk flags, focused behavior evidence, selected affected/scoped checks, актуальный fast assurance либо standard review/testing, reproducible manual verification и explicit Task Acceptance.

Universal Epic baseline требует `DONE` для всех planned TASK, requirement-to-evidence coverage, полный project suite, project-wide lint/typecheck/build, cross-component и critical-path validation, applicable profile gates, current documentation/operational evidence, допустимый fuzzing outcome, отсутствие непринятых blocking risks и explicit Epic Acceptance.

Профили компонуются; backend + frontend образуют full-stack coverage:

| Profile | Дополнительные gates |
| --- | --- |
| `backend` | API/schema contracts, authorization, persistence/migration, idempotency, concurrency, failure handling |
| `frontend` | component behavior, critical E2E, accessibility, responsive states, browser compatibility, production build |
| `ml` | data quality, leakage prevention, reproducibility, baseline comparison, metric uncertainty, artifact lineage, training-serving parity |
| `data_pipeline` | schema evolution, idempotency, backfill, data quality, lineage, partial-failure recovery |
| `infrastructure` | validate/plan/dry-run, least privilege, rollback, drift, secret handling, deployment smoke |
| `library_cli` | public API compatibility, packaging, supported runtimes, install/upgrade, CLI exit and stream contracts |

Конкретные команды берутся только из подтверждённого repository/build/CI evidence, сохраняются в `.ai/project.yaml` и утверждённом Epic Verification Plan. Пустая конфигурация требует явного `not applicable` или blocker; агент не придумывает замену.

## Defect Queue

Дефект в непринятой TASK остаётся частью этой TASK. Дефект в принятом коде получает `BUG-*` после решения пользователя.

Основной переход:

```text
OPEN → SCHEDULED → RESOLVED
```

Severity описывает последствия, а priority задаётся пользователем.

## Security

`security-auditor` вызывается только явно пользователем и использует tier `strong`. По умолчанию он:

- работает локально и read-only;
- не устанавливает инструменты;
- не использует network;
- не сканирует production или внешние targets.

Расширение scope требует отдельного точного разрешения. Принятые findings превращаются в существующую TASK, Bug или Epic; отдельный security report не создаётся.

## Standalone mutation testing

`forge-mutation-test` запускается только по явному запросу и не зависит от наличия или статуса Epic/TASK. Он не меняет Backlog, lifecycle, gates, review/testing/validation/fuzzing evidence, acceptance или commit permissions.

Новый запуск фиксирует точный production/test scope, backend и версию, команды, budgets и fingerprint. Fast `mutation-runner` сначала выполняет обычный baseline, затем вызывает только подтверждённый mutation backend и возвращает normalized metrics: generated, killed, survived, no coverage, timeout, invalid/error, duration и backend-reported score. Если backend отсутствует, результат `SETUP REQUIRED` записывается без установки инструмента или изменения конфигурации.

По умолчанию запуск metrics-only и strong model не используется. `mutation-analyzer` вызывается только после отдельного разрешения и только если текущий результат содержит candidates и положительный analysis budget. Все mutants killed — analyzer пропускается. Deferred analysis использует сохранённый `MUT-NNNN` без повторения campaign; stale fingerprint или artifact checksum блокирует анализ. Большие candidate sets анализируются bounded batches с явным `partial` и remaining count.

Каждая попытка получает независимый `MUT-NNNN` и сохраняется в project-owned `quality/mutation-testing/`. Findings не создают Bug, TASK, Epic или Replan автоматически. Любое remediation начинается только отдельным решением пользователя через существующий lifecycle; mutation record может хранить лишь информационные ссылки на уже утверждённую работу.

## Синхронизация адаптеров

Adapter sync пересоздаёт обе платформы как одну операцию, проверяет parity и обновляет lock только после успеха.

## Внешние интеграции

Фреймворк не генерирует hooks, MCP/API/CLI-конфигурацию или credentials. Проект может добавить их отдельно как project-owned инфраструктуру.

Универсальный optional registry находится в `.ai/integrations/`; его отсутствие — clean baseline. Определения используют semantic capability profiles, operation allowlist, resource scope, access/data policy, consumers и platform-local bindings. Регистрация не даёт implicit tool authority: effective permission — пересечение integration definition, выбранного consumer skill и user authorization.

Built-in profiles задают общий контракт для `work_source`, `knowledge_source`, `data_source` и `analysis_service`; только `work_source` имеет framework consumer `forge-intake-external-work`. Custom profiles сохраняются и вызываются только project-owned consumers. Неизвестный или повреждённый profile блокирует свой consumer, а не остальной lifecycle.

`work_source` нормализует тикеты разных провайдеров, включая Kaiten, и после approval хранит provider-neutral связи в Backlog `Sources`, TASK `external_sources`, Epic coverage matrix и `.ai/integrations/work-items.yaml`. Внешний status никогда не заменяет Forge gates.

Framework update и integration-schema migration — две операции. Upgrade не вызывает connectors, не включает локальное содержимое в managed-output hashes и сохраняет project-owned файлы. Старую поддерживаемую schema можно отдельно мигрировать после preview/approval/backup; unknown future schema сохраняется byte-for-byte. Подробнее: [локальные интеграции](docs/local-integrations.md).

Подробные пользовательские сценарии приведены в [RUNBOOK.md](RUNBOOK.md).
