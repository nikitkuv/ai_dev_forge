# AI Development Forge v3 — Architecture

Этот документ описывает реализованную архитектуру фреймворка. Обоснование решений и полный набор согласованных правил находятся в [FRAMEWORK_DESIGN.md](FRAMEWORK_DESIGN.md).

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
| Стратегия Epic, порядок TASK, Epic fuzzing и validation | `plan.md` |
| TASK scope, status и implementation/review/test/user evidence | соответствующий TASK-файл |
| История файлов | Git |

`README.md`, root routers, agent-файлы и `SKILL.md` являются инфраструктурой, но не владельцами execution-состояния.

## Слой `.ai/`

`.ai/` — копируемый framework bundle:

- `BOOTSTRAP.md` и шесть numbered workflows;
- `CONVENTIONS.md`;
- `framework/manifest.yaml` с release, ownership, agent и skill IDs;
- `framework/contracts.yaml` с lifecycle, transitions, gates и fuzzing outcomes;
- семь нейтральных agent definitions;
- четырнадцать portable skills;
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

`plan.md` не хранит TASK status. TASK-файл хранит единственный lifecycle status, revision/fingerprint evidence и компактные summaries.

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

Оба root router ограничены 150 строками. `.ai/project.yaml` сопоставляет tiers с конкретными моделями:

- `strong`;
- `balanced`;
- `fast`.

Для Codex отдельно задаётся reasoning effort. Aliases и полные model IDs поддерживаются; скрытая замена tier запрещена.

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
| `implementer` | balanced | одна TASK, production-код и тесты |
| `reviewer` | strong | независимый read-only review |
| `tester` | fast | targeted, affected, full tests и configured checks |
| `fuzzer` | balanced | воспроизводимый Epic fuzzing без исправлений |
| `security-auditor` | strong | явный on-demand local security audit |

Субагенты не вызывают друг друга. Одновременно выполняется не более одной code-writing TASK; независимый read-only research может выполняться параллельно.

## Skills

Четырнадцать skills сгруппированы по назначению:

- bootstrap нового и существующего проекта;
- feature/bug intake и reprioritization;
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
3. strong reviewer проверяет только назначенную TASK;
4. tester запускает targeted, affected и полный suite, затем lint/typecheck/build;
5. пользователь тестирует вручную;
6. отдельный Task Acceptance переводит TASK в `DONE`.

Любое изменение кода инвалидирует прежние review и test fingerprints. Task Acceptance не запускает следующую TASK без отдельного разрешения.

## Epic lifecycle и fuzzing

```text
PLANNED → ACTIVE → FUZZING → AWAITING EPIC ACCEPTANCE → COMPLETED
```

Также поддерживаются `PAUSED` и `CANCELLED`.

После принятия последней TASK автоматически запускается read-only fuzzer:

- `PASSED`;
- `NOT APPLICABLE` с rationale и alternative risk coverage;
- `HARNESS REQUIRED`;
- `FINDINGS`.

Harness или remediation создаются как новые TASK через Replan и собственный Task Start. После изменений повторяются review, полный testing и fuzzing.

Только отдельный Epic Acceptance завершает Epic и перемещает его каталог в `execution/completed/`. Следующий Epic автоматически не активируется.

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

Фреймворк не генерирует hooks или MCP-конфигурацию. Проект может добавить их отдельно как project-owned инфраструктуру.

Подробные пользовательские сценарии приведены в [RUNBOOK.md](RUNBOOK.md).
