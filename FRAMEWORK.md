# AI Development Forge — Architecture

## План тестов до реализации

При планировании эпика и задач обязателен предварительный план тестов (`test_planning` в `.ai/framework/contracts.yaml`). В `plan.md` внутри Epic Verification Plan записываются сквозные сценарии, ожидаемые результаты, ответственные TASK и этап проверки. В TASK внутри Verification Plan — конкретные сценарии с ID, связью с критериями и рисками, входными условиями, независимым источником ожидаемого результата, уровнем проверки и ожидаемой причиной RED либо обоснованием неприменимости.

План составляется до Plan Approval; код тестов появляется при выполнении разрешённой задачи по циклу RED → GREEN → REFACTOR. План допускает уточнения в пределах задачи; неизвестные ожидания и пробелы покрытия устраняются до утверждения. При проверке ID сценариев сопоставляются с фактическими тестами и результатами запуска.

## Planner/reviewer routing

`epic-planner` и `reviewer` имеют neutral definitions и native agents на Codex, Claude Code и OpenCode. Один обязательный `role_execution.mode` в `.ai/project.yaml` выбирает маршрут для обеих ролей: `claude_with_codex`, `codex_with_claude` или `native_subagents`. OpenCode-led setup предлагает `native_subagents` при отсутствии утверждённого route. Cross-provider preflight или runtime failure никогда не переключает provider неявно.

## Локальная автоматизация

`.ai/tools/forge.py` выполняет механические операции на Python 3.11+: metadata inventory, извлечение разделов, fingerprints, структурную валидацию (line budget роутера, BOM/frontmatter агентов, ADR parity, plan-order, структуру INV и mutation-registry, инвариант архива Backlog), генерацию adapters, bounded subprocess checks и агрегацию usage.

Read-only сборка: `next-id`, `evidence-check`, `review-packet`, `checks-new`, `role --assignment-file`, `query` (ранжированные указатели из derived SQLite FTS-индекса; индекс в `.ai/local/index.db` пересобирается детерминированно и никогда не является evidence). Мутации lifecycle (`transition`, `epic-start`, `epic-complete`, `accept-record`, `backlog`, `inv-create`, `commit-scoped`) выполняются через preview/apply с journal-транзакцией и rollback. Хелперы исполняют явно утверждённые изменения — авторизация и приёмка остаются за пользователем и оркестратором.

Кэш команд opt-in: требуются полный набор входов, неизменные команды/runtime/environment и целые логи. Epic Validation кэш не использует. Raw logs и metrics находятся в project-owned `.ai/local/` и не заменяют evidence в TASK/plan.

## Назначение и ответственность

- продуктовые и архитектурные цели утверждаются пользователем;
- execution-состояние восстанавливается из файлов, а не из истории чата;
- сильная основная модель оркестрирует специализированных субагентов;
- Codex CLI, Claude Code CLI и OpenCode получают нативные adapters из одного нейтрального источника;
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
├── BACKLOG-ARCHIVE.md
├── DECISIONS.md
├── decisions/ADR-NNN-<name>.md
├── investigations/INV-NNNN-<name>.md
├── intents/INT-NNNN-<name>.md
├── execution/{active,planned,paused,completed}/EPIC-NNN-<name>/
├── quality/mutation-testing/
├── .ai/
├── .codex/agents/
├── .agents/skills/
├── .claude/agents/
├── .claude/skills/
└── .opencode/agents/
```

Репозиторий исходников Forge не проходит собственный bootstrap.

## Источники истины

| Информация | Владелец |
| --- | --- |
| Целевое поведение продукта | `SPEC.md` |
| Целевая архитектура | `ARCHITECTURE.md` |
| Epic, приоритет, readiness, status и дефекты | `BACKLOG.md` |
| Терминальные строки Backlog | append-only `BACKLOG-ARCHIVE.md` |
| Содержание архитектурного решения | ADR |
| Навигация по решениям | генерируемый `DECISIONS.md` |
| Стратегия Epic, порядок TASK, verification и fuzzing plans, Epic Validation, fuzzing outcome и user validation | `plan.md` |
| TASK scope, status и evidence | TASK-файл |
| История ad hoc исследования | `investigations/INV-NNNN-*.md` |
| История продуктовых запросов | `intents/INT-NNNN-*.md` |
| История mutation testing | `quality/mutation-testing/` |
| История файлов | Git |

`README.md`, root routers, agent-файлы и `SKILL.md` — инфраструктура, не владельцы execution-состояния.

## Слой `.ai/`

`.ai/` — копируемый framework bundle: `BOOTSTRAP.md`, шесть numbered workflows, `CONVENTIONS.md`, `framework/manifest.yaml`, `framework/contracts.yaml`, одиннадцать нейтральных agent definitions, семнадцать portable skills, canonical и adapter templates.

Ownership: framework-owned release files; project-owned `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, optional `investigations/`, `intents/`, `quality/mutation-testing/`, canonical и execution-файлы; generated adapters пересоздаются после collision preview.

## Канонические документы

`SPEC.md` — target behavior через `FR-*`, `NFR-*`, `BR-*`. `ARCHITECTURE.md` — requirement drivers, компоненты, dependency rules, data ownership, interfaces, trust boundaries, runtime, observability, testing и эволюция данных. `BACKLOG.md` содержит Epic Roadmap и Defect Queue; терминальные строки атомарно переносятся в `BACKLOG-ARCHIVE.md` (append-only, секции по годам). ADR — авторитетное решение; `DECISIONS.md` — только индекс. `plan.md` не хранит TASK status. Approved detailed plans для неактивированных Epic находятся в `execution/planned/`. Epic Start требует satisfied dependencies, пустой `Blocked by`, отсутствия другого active-work Epic и выполняет move `planned → active`.

## Идентификаторы и язык

```text
EPIC-001  TASK-001  BUG-001  ADR-001  INV-0001  INT-0001  MUT-0001
```

Следующий ID = максимальный существующий + 1. TASK numbering не начинается заново в каждом Epic. Для `BUG` и `EPIC` сканируются живой `BACKLOG.md` и архив вместе. Framework control layer — English; канонические документы — на языке пользователя.

## Dual-platform generation

| Codex | Claude Code |
| --- | --- |
| `AGENTS.md` | `CLAUDE.md` |
| `.codex/agents/*.toml` | `.claude/agents/*.md` |
| `.agents/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` |

`AGENTS.md` — единственный полный root router (лимит 150 строк). `CLAUDE.md` содержит только `@AGENTS.md`. `.ai/project.yaml` хранит `role_execution.mode` и сопоставление tiers с моделями и effort.

| Tier | Codex | Claude Code |
| --- | --- | --- |
| `strong` | `gpt-6.1-sol`, `high` | `opus`, `high` |
| `balanced` | `gpt-6-luna`, `xhigh` | `sonnet`, `high` |
| `fast` | `gpt-5.6-luna`, `medium` | `haiku`, `high` |

Проект может переопределить defaults. Скрытая замена tier запрещена. В режиме `native_subagents` Claude Code агенты получают override `effort: high`. `.ai/framework.lock` хранит hashes neutral sources и generated outputs.

## Оркестратор и субагенты

Основная сессия — сильный оркестратор: общается с пользователем, вызывает skills и agents, маршрутизирует findings, изменяет canonical status, управляет gates.

| Agent | Tier | Ответственность |
| --- | --- | --- |
| `context-collector` | fast | canonical/execution/Git/code evidence |
| `documentation-researcher` | fast | внешняя документация |
| `epic-planner` | strong | Epic decomposition, risks, review focus и verification planning |
| `implementer` | balanced | одна TASK, production-код и тесты |
| `reviewer` | strong | независимый read-only review |
| `tester` | fast | focused, affected, fuzz smoke и scoped Task checks |
| `epic-validator` | balanced | полный regression, project-wide checks, critical paths и quality profiles |
| `fuzzer` | balanced | воспроизводимое Epic fuzzing без исправлений |
| `security-auditor` | strong | on-demand local security audit |
| `mutation-runner` | fast | baseline и mutation-backend execution |
| `mutation-analyzer` | strong | semantic analysis текущих mutation candidates |

Субагенты не вызывают друг друга. Не более одной code-writing TASK одновременно; независимый read-only research может выполняться параллельно.

## Skills

Семнадцать skills: bootstrap нового и существующего проекта; feature/bug/external-work intake и reprioritization; Epic preparation и resume; Task execution/completion и Epic completion; security audit; mutation testing; ad hoc investigation; framework conformance; adapter sync. Codex вызывает skill как `$forge-...`, Claude Code — `/forge-...`. Mandatory lifecycle использует явный skill routing.

## TASK delivery tracks

Два delivery track: `fast` и `standard`. Delivery track независим от model tier и `risk level`: низкий риск не разрешает `fast` без доказанной ограниченности.

Fast eligibility fail-closed: ограниченная, обратимая, однозначная TASK с детерминированной локальной проверкой. `fast` запрещён для public contract, auth/security/privacy, persistence/data format, schema/migration, concurrency/shared core, dependency/build/package/deploy/runtime infrastructure, внешних интеграций, critical paths, ослабления тестов и неопределённости. Legacy TASK без track получает `standard`.

Оба track используют implementer и focused RED/GREEN. `fast` не вызывает reviewer или tester: оркестратор проверяет fingerprint, diff, test integrity и повторяет approved checks. `standard` сохраняет strong reviewer и tester. Провал fast assurance или потеря eligibility повышает TASK `fast → standard`; обратный переход после Task Start запрещён.

## TASK lifecycle

```text
TODO → IN PROGRESS
  → fast: orchestrator assurance
  → standard: IN REVIEW → IN TESTING
  → AWAITING USER ACCEPTANCE → DONE
```

Также поддерживаются `PAUSED` и `CANCELLED`. Блокировка хранится в `blocked_by`.

1. отдельный Task Start;
2. implementer пишет код и тесты;
3. `fast` → orchestrator assurance → `AWAITING USER ACCEPTANCE`;
4. `standard` → Review Packet, strong reviewer по production surface, tester (focused, affected, bounded Task fuzz smoke, scoped checks);
5. пользователь тестирует вручную;
6. отдельный Task Acceptance → `DONE`.

В `standard` изменение production surface инвалидирует review и test evidence; supporting-only изменение при неизменном production fingerprint сохраняет clean review и повторяет tester gate. В `fast` любое изменение инвалидирует fast assurance. Commit запрещён до Task Acceptance и `DONE`. При `manual` policy после acceptance требуется отдельное разрешение на commit.

## Epic lifecycle, validation и fuzzing

```text
PLANNED → ACTIVE → VALIDATING → FUZZING → AWAITING EPIC ACCEPTANCE → COMPLETED
```

`epic-planner` создаёт Epic Fuzzing Plan с applicability (`applicable`, `not applicable`, `unresolved`), targets, harness readiness и Task mapping. Каждая TASK хранит `Fuzzing impact` и `Task fuzz smoke` в Verification Plan.

После последней TASK `epic-validator` запускает полный project suite, project-wide lint/typecheck/build, integration/E2E, critical paths и quality-profile gates. `PASSED` или `PASSED WITH ACCEPTED EXCEPTIONS` → `FUZZING`. При approved `not applicable` (все итоговые Task impacts `none`, surface совпадает с планом, alternative coverage прошёл) оркестратор записывает `NOT APPLICABLE` без вызова fuzzer; иначе запускается read-only fuzzer. Outcomes: `PASSED`, `NOT APPLICABLE`, `HARNESS REQUIRED`, `FINDINGS`. Harness и remediation создаются как новые TASK через Replan. Epic Acceptance завершает Epic, перемещает каталог в `execution/completed/` и архивирует строку.

## Quality gates и project profiles

Universal Task baseline: approved definition, delivery track, verifiable acceptance criteria, affected surface и risk flags, focused behavior evidence, selected checks, current assurance, manual verification и explicit Task Acceptance. При планировании TASK заполняется `Planned Change Map`: часть системы, пути, символы, действия и причины; косвенно затронутые потребители фиксируются отдельно.

Universal Epic baseline: все TASK `DONE`, requirement-to-evidence coverage, полный project suite, project-wide checks, critical-path validation, applicable profile gates, допустимый fuzzing outcome и explicit Epic Acceptance.

| Profile | Дополнительные gates |
| --- | --- |
| `backend` | API/schema contracts, authorization, persistence/migration, idempotency, concurrency, failure handling |
| `frontend` | component behavior, critical E2E, accessibility, responsive states, browser compatibility, production build |
| `ml` | data quality, leakage prevention, reproducibility, baseline comparison, metric uncertainty, artifact lineage, training-serving parity |
| `data_pipeline` | schema evolution, idempotency, backfill, data quality, lineage, partial-failure recovery |
| `infrastructure` | validate/plan/dry-run, least privilege, rollback, drift, secret handling, deployment smoke |
| `library_cli` | public API compatibility, packaging, supported runtimes, install/upgrade, CLI exit and stream contracts |

Команды берутся только из repository/build/CI evidence и сохраняются в `.ai/project.yaml`. Пустая конфигурация требует явного `not applicable` или blocker.

## Defect Queue

Дефект в непринятой TASK остаётся частью TASK. Дефект в принятом коде получает `BUG-*` после решения пользователя.

```text
OPEN → SCHEDULED → RESOLVED
```

Severity описывает последствия, priority задаётся пользователем.

## Security

`security-auditor` вызывается только явно. По умолчанию local, read-only, без установки инструментов, network и production/external scanning. Расширение scope требует отдельного разрешения. Findings превращаются в TASK, Bug или Epic.

## Standalone mutation testing

`forge-mutation-test` запускается по явному запросу и не зависит от Epic/TASK. Forge не устанавливает backend автоматически. Не меняет Backlog, lifecycle, gates, acceptance или commit permissions. Fast `mutation-runner` выполняет baseline и mutation backend, возвращает normalized metrics; отсутствие backend даёт `SETUP REQUIRED`. По умолчанию metrics-only; strong `mutation-analyzer` вызывается только после отдельного разрешения при наличии candidates и положительного budget. Каждая попытка получает `MUT-NNNN` в `quality/mutation-testing/`. Remediation — только отдельным решением пользователя.

## Intent records

Материальные feature, product-change и external-work запросы фиксируются `intents/INT-NNNN-<short-name>.md`. Intake резервирует ID, заполняет шаблон и подтверждает запись до retention в Backlog. Outcome: `draft`, `accepted`, `promoted`, `rejected`, `deferred` или `superseded`. Epic row ссылается на INT опциональной колонкой `Intent`; материальные открытые вопросы блокируют `OUTLINE → READY`.

## Ad hoc investigations

`forge-investigate` — lifecycle-independent workflow основного оркестратора без generated subagents. Каждое материальное исследование получает `INV-NNNN` в `investigations/`. Outcomes: `no_action`, `promoted`, `fixed_directly`, `unresolved`. Для `fixed_directly` INV содержит path-level ledger добавленных, изменённых и удалённых файлов, verification и fingerprint. Backlog, plan и TASK могут хранить `research_refs`.

## Синхронизация адаптеров

Adapter sync пересоздаёт enabled platform adapters, проверяет parity и обновляет lock. Codex и OpenCode используют `AGENTS.md` и `.agents/skills/`. `opencode.json`, commands, plugins, skills и unlisted agents остаются project-owned.

## Внешние интеграции

Hooks, MCP/API/CLI-конфигурация и credentials не генерируются. Optional registry — `.ai/integrations/` с semantic capability profiles, operation allowlist, scope, consumers и bindings. Регистрация не даёт implicit tool authority. `work_source` нормализует тикеты и хранит связи с Backlog/TASK/Epic. Framework update и integration-schema migration — две операции. Подробнее: [локальные интеграции](docs/local-integrations.md).

Пользовательские сценарии: [RUNBOOK.md](RUNBOOK.md).
