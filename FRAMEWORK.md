# AI Development Forge v4.2 — Architecture

## Preferred Codex routing in Claude Code

`epic-planner` and `reviewer` keep their neutral definitions and native agents on both platforms. When Claude Code preflight finds `codex-plugin-cc`, Node.js 18.18+, Codex CLI, and authentication, it invokes the managed launcher with a fresh read-only `gpt-5.6-sol/high` task. Otherwise it invokes the matching native Claude subagent with the same contract and assignment. A failure after Codex task creation is never retried through Claude.

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
| Стратегия Epic, порядок TASK, verification plan, Epic Validation, fuzzing и user validation | `plan.md` |
| TASK scope, status и implementation/review/test/user evidence | соответствующий TASK-файл |
| История файлов | Git |

`README.md`, root routers, agent-файлы и `SKILL.md` являются инфраструктурой, но не владельцами execution-состояния.

## Слой `.ai/`

`.ai/` — копируемый framework bundle:

- `BOOTSTRAP.md` и шесть numbered workflows;
- `CONVENTIONS.md`;
- `framework/manifest.yaml` с release, ownership, agent и skill IDs;
- `framework/contracts.yaml` с lifecycle, transitions, gates и fuzzing outcomes;
- девять нейтральных agent definitions;
- пятнадцать portable skills;
- canonical и adapter templates.

Ownership разделён на три категории:

- framework-owned release files поставляются текущей версией Forge;
- project-owned `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, canonical и execution-файлы сохраняются;
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

Оба root router имеют byte-identical содержимое и ограничены 150 строками. `.ai/project.yaml` сопоставляет tiers с конкретными моделями и effort. Framework defaults:

| Tier | Codex | Claude Code |
| --- | --- | --- |
| `strong` | `gpt-5.6-sol`, `high` | `opus`, `high` |
| `balanced` | `gpt-5.6-terra`, `medium` | `sonnet`, `high` |
| `fast` | `gpt-5.6-luna`, `medium` | `haiku`, `high` |

Проект может явно переопределить defaults. Aliases и полные model IDs поддерживаются; скрытая замена tier запрещена.

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
| `tester` | fast | selected focused, affected и scoped Task checks |
| `epic-validator` | balanced | полный regression, project-wide checks, critical paths и quality profiles |
| `fuzzer` | balanced | воспроизводимый Epic fuzzing без исправлений |
| `security-auditor` | strong | явный on-demand local security audit |

Субагенты не вызывают друг друга. Одновременно выполняется не более одной code-writing TASK; независимый read-only research может выполняться параллельно.

## Skills

Пятнадцать skills сгруппированы по назначению:

- bootstrap нового и существующего проекта;
- feature/bug/external-work intake и reprioritization;
- Epic preparation и durable resume;
- Task execution/completion и Epic completion;
- security audit;
- framework conformance check;
- adapter synchronization.

Codex вызывает skill как `$forge-...`, Claude Code — как `/forge-...`. Mandatory lifecycle использует явный skill routing, а не только implicit matching.

Feature discovery и root-cause investigation встроены в intake skills. Test-driven implementation и evidence-before-transition встроены в Task lifecycle и role-specific agent contracts. Внешние process skills не управляют gates, canonical artifacts, status transitions, agent routing или Git actions.

## TASK lifecycle

```text
TODO
  → IN PROGRESS
  → IN REVIEW
  → IN TESTING
  → AWAITING USER ACCEPTANCE
  → DONE
```

Также поддерживаются `PAUSED` и `CANCELLED`. Блокировка хранится отдельно в `blocked_by`.

Цикл выполнения:

1. отдельный Task Start;
2. implementer пишет код и необходимые тесты;
3. strong reviewer получает обязательный Review Packet и по ordered protocol проверяет acceptance traceability, diff/context, adversarial cases, архитектуру, контракты, данные, безопасность и тесты;
4. tester запускает focused, selected affected и scoped quality checks; полный project suite и unscoped global checks остаются Epic gate;
5. пользователь тестирует вручную;
6. отдельный Task Acceptance переводит TASK в `DONE`.

Любое изменение кода инвалидирует прежние review и test fingerprints. Commit этой TASK запрещён до явного Task Acceptance и перехода в `DONE`. При `manual` policy после acceptance требуется отдельное разрешение на commit. Task Acceptance не запускает следующую TASK без отдельного разрешения.

## Epic lifecycle, validation и fuzzing

```text
PLANNED → ACTIVE → VALIDATING → FUZZING → AWAITING EPIC ACCEPTANCE → COMPLETED
```

Также поддерживаются `PAUSED` и `CANCELLED`.

После принятия последней TASK отдельный `epic-validator` на точном aggregate fingerprint запускает полный project suite, project-wide lint/typecheck/build, integration/E2E, requirement coverage и применимые quality-profile gates. Только `PASSED` или `PASSED WITH ACCEPTED EXCEPTIONS` после явного принятия риска переводит Epic в `FUZZING`.

Затем автоматически запускается read-only fuzzer:

- `PASSED`;
- `NOT APPLICABLE` с rationale и alternative risk coverage;
- `HARNESS REQUIRED`;
- `FINDINGS`.

Harness или remediation создаются как новые TASK через Replan и собственный Task Start. После изменений повторяются structured review, selected Task testing, полный Epic Validation и fuzzing.

Только отдельный Epic Acceptance завершает Epic и перемещает его каталог в `execution/completed/`. Следующий Epic автоматически не активируется.

## Quality gates и project profiles

Universal Task baseline требует approved definition и boundaries, objectively verifiable acceptance criteria, affected surface и risk flags, focused behavior evidence, selected affected/scoped checks, current structured review, reproducible manual verification и explicit Task Acceptance.

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

## Синхронизация адаптеров

Adapter sync пересоздаёт обе платформы как одну операцию, проверяет parity и обновляет lock только после успеха.

## Внешние интеграции

Фреймворк не генерирует hooks, MCP/API/CLI-конфигурацию или credentials. Проект может добавить их отдельно как project-owned инфраструктуру.

Универсальный optional registry находится в `.ai/integrations/`; его отсутствие — clean baseline. Определения используют semantic capability profiles, operation allowlist, resource scope, access/data policy, consumers и platform-local bindings. Регистрация не даёт implicit tool authority: effective permission — пересечение integration definition, выбранного consumer skill и user authorization.

Built-in profiles задают общий контракт для `work_source`, `knowledge_source`, `data_source` и `analysis_service`; только `work_source` имеет framework consumer `forge-intake-external-work`. Custom profiles сохраняются и вызываются только project-owned consumers. Неизвестный или повреждённый profile блокирует свой consumer, а не остальной lifecycle.

`work_source` нормализует тикеты разных провайдеров, включая Kaiten, и после approval хранит provider-neutral связи в Backlog `Sources`, TASK `external_sources`, Epic coverage matrix и `.ai/integrations/work-items.yaml`. Внешний status никогда не заменяет Forge gates.

Framework update и integration-schema migration — две операции. Upgrade не вызывает connectors, не включает локальное содержимое в managed-output hashes и сохраняет project-owned файлы. Старую поддерживаемую schema можно отдельно мигрировать после preview/approval/backup; unknown future schema сохраняется byte-for-byte. Подробнее: [локальные интеграции](docs/local-integrations.md).

Подробные пользовательские сценарии приведены в [RUNBOOK.md](RUNBOOK.md).
