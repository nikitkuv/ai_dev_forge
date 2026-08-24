# AI Development Forge v4.2

## Настраиваемый planner/reviewer route

`.ai/project.yaml` хранит один явный `role_execution.mode` для `epic-planner` и `reviewer`: `claude_with_codex` запускает Forge в Claude Code и делегирует обе роли через `openai/codex-plugin-cc` 1.0.6+ в fresh read-only `gpt-5.6-sol/medium`; `codex_with_claude` запускает Forge в Codex и вызывает установленный Claude Code CLI 2.1.203+ через fresh `claude -p`, JSON output, plan mode и ограниченные read-only tools; `native_subagents` использует внутренних агентов активной платформы без внешнего preflight.

Bootstrap и migration требуют явного выбора. Недоступность выбранного внешнего runtime, несовпадение активного оркестратора и любая ошибка после старта блокируют planning/review без fallback. Forge не устанавливает и не авторизует внешние CLI автоматически.

AI Development Forge — documentation-first фреймворк для совместной разработки с кодовыми агентами, прежде всего Codex CLI и Claude Code CLI.

Фреймворк хранит продуктовый и execution-контекст в репозитории, использует сильную основную модель как оркестратор и генерирует нативных субагентов и skills для обеих платформ.

## Что создаётся

После полного bootstrap целевой проект содержит:

```text
README.md
AGENTS.md
CLAUDE.md
SPEC.md
ARCHITECTURE.md
BACKLOG.md
DECISIONS.md
decisions/ADR-NNN-<name>.md
execution/{planned,active,paused,completed}/
.ai/
.codex/agents/
.agents/skills/
.claude/agents/
.claude/skills/
```

`SPEC`, `ARCHITECTURE`, `BACKLOG`, ADR, Epic plan и TASK являются источниками истины. Отдельные Markdown-отчёты для review, testing, fuzzing, security или ручной проверки не создаются.

## Установка

1. Скопируйте папку `.ai/` из этого репозитория в корень целевого проекта.
2. Откройте проект в Codex CLI или Claude Code CLI.
3. Отправьте один из bootstrap-промптов ниже.
4. Отвечайте на вопросы и подтверждайте каждый из шести этапов отдельно.

Исполняемого CLI у фреймворка нет: установка выполняется копированием `.ai/` и инструкцией агенту.

Не запускайте bootstrap внутри самого репозитория `ai_dev_forge`: он хранит исходный framework bundle, а не является проектом-потребителем.

## Новый проект

```text
Read .ai/BOOTSTRAP.md and initialize this repository as a new project.
Create both Codex and Claude Code adapters.
Communicate with me in Russian and start the product interview.
```

Если описание продукта уже существует, вставьте его в сообщение или приложите/укажите файл. Если описания недостаточно, агент проведёт итеративное product interview.

## Существующий проект

```text
Read .ai/BOOTSTRAP.md and initialize this existing repository.
Analyze the current code and documentation before starting the interview.
Create both Codex and Claude Code adapters.
Communicate with me in Russian.
```

Код, тесты и прежняя документация рассматриваются как evidence, а не как автоматическая продуктовая истина. Конфликты показываются пользователю; найденные баги и technical debt попадают в Backlog только после подтверждения.

## Шесть этапов bootstrap

1. Product Discovery → утверждённый `SPEC.md`.
2. System Design → `ARCHITECTURE.md`, ADR и генерируемый `DECISIONS.md`.
3. Release Planning → `BACKLOG.md` с Epic Roadmap и Defect Queue.
4. Prepare Workspace → strong `epic-planner`, approved queued workspace under `execution/planned/`, затем optional отдельный Epic Start с атомарным move в `execution/active/`.
5. Create Platform Adapters → оба native adapter-набора и `.ai/framework.lock`.
6. Final Validation → проверка структуры, lifecycle, ownership, parity и восстановления без истории сессии.

Первая TASK после bootstrap остаётся `TODO` и требует отдельного Task Start.

## Нативные адаптеры

| Codex CLI | Claude Code CLI |
| --- | --- |
| `AGENTS.md` | `CLAUDE.md` |
| `.codex/agents/*.toml` | `.claude/agents/*.md` |
| `.agents/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` |

Нейтральные определения находятся в `.ai/framework/`. `AGENTS.md` и `CLAUDE.md` генерируются с byte-identical содержимым. Проектные дополнения к ним хранятся только в `.ai/custom/router-shared.md`.

Framework defaults для всех субагентов: Codex `strong = gpt-5.6-sol/medium`, `balanced = gpt-5.6-terra/medium`, `fast = gpt-5.6-luna/medium`; Claude Code `strong = opus/medium`, `balanced = sonnet/medium`, `fast = haiku/medium`. Проект может явно переопределить их в `.ai/project.yaml`; генератор записывает resolved mapping в нативные agent-файлы обеих платформ. В режиме `native_subagents` все Claude Code agent-файлы получают режимный override `effort: high`; настройки Codex и внешнего маршрута `codex_with_claude` не меняются.

Сгенерированные adapters вручную не редактируются и применяются через синхронизацию.

## Проверка качества

Обычная TASK использует focused RED/GREEN, выбранные affected-component tests и scoped quality checks. Strong reviewer получает обязательный Review Packet, независимо трассирует каждый acceptance criterion и проверяет code-review diff, соседний код, adversarial cases, архитектуру, контракты, данные, безопасность и качество тестов. Canonical-документы служат ему только контекстом и не являются объектом review: их ошибки исправляет оркестратор и они не создают code findings. Полный project test suite и unscoped project-wide lint/typecheck/build не являются Task gate.

После принятия последней TASK Epic переходит в `VALIDATING`. Отдельный `epic-validator` запускает полный regression suite, глобальные quality checks, critical-path validation и применимые gates выбранных project profiles. Только текущий passing Epic Validation fingerprint допускается к fuzzing и последующему Epic Acceptance.

Можно заранее подготовить несколько `PLANNED + READY` Epic. Каждый approved plan и его `TODO` TASK definitions хранятся в собственном `execution/planned/EPIC-*`; порядок очереди остаётся только в `BACKLOG.md`. Plan Approval не активирует Epic, а Epic Start отдельно проверяет dependencies/blockers и перемещает один eligible workspace в `execution/active/`.

## Внешняя инфраструктура

- Hooks не создаются автоматически.
- MCP-конфигурация не создаётся автоматически.
- Проект может добавить собственные hooks, MCP, API или CLI отдельно.
- `.ai/integrations/` — необязательный project-owned registry; чистый Forge не содержит эту папку и не выполняет connector preflight.

Локальная интеграция описывает provider-neutral capability (`work_source`, `knowledge_source`, `data_source`, `analysis_service` или project-defined profile), разрешённые операции, scope, consumers и platform-local bindings. Само наличие записи не разрешает вызов: выбранный framework/project-owned skill должен явно потреблять совместимый profile.

Kaiten — только пример `work_source`. Для такого profile Forge может хранить двусторонние ссылки `external item ↔ EPIC/BUG/TASK`; остальные типы не получают искусственных связей с Backlog. Framework upgrade работает offline, сохраняет неизвестные project-owned profiles и отделяет замену Forge от отдельно подтверждаемой миграции integration schema. Подробнее: [локальные интеграции](docs/local-integrations.md).

Feature discovery, root-cause investigation, test-driven implementation и evidence verification встроены в Forge lifecycle skills и agent contracts. Внешние process skills не управляют lifecycle проекта.

## Дальнейшая работа

- [Архитектура фреймворка](FRAMEWORK.md)
- [Операционные сценарии](RUNBOOK.md)
- [Миграция между версиями](MIGRATION.md)

Для продолжения разработки попросите основного агента прочитать соответствующий root router и восстановить состояние из `BACKLOG.md`, execution-файлов и Git.
