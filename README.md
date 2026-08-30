# AI Development Forge v4.7

## Настраиваемый planner/reviewer route

`.ai/project.yaml` хранит один явный `role_execution.mode` для `epic-planner` и `reviewer`: `claude_with_codex` запускает Forge в Claude Code и делегирует обе роли через `openai/codex-plugin-cc` 1.0.6+ в fresh read-only `gpt-5.6-sol/medium`; `codex_with_claude` запускает Forge в Codex и вызывает установленный Claude Code CLI 2.1.203+ через fresh `claude -p`, JSON output, plan mode и ограниченные read-only tools; `native_subagents` использует внутренних агентов активной платформы — Codex, Claude Code или OpenCode — без внешнего preflight. Для OpenCode-led bootstrap при отсутствии утверждённого route предлагается существующий `native_subagents`, но он всё равно записывается только после явного подтверждения; новых режимов нет.

Bootstrap и migration требуют явного выбора. Недоступность выбранного внешнего runtime, несовпадение активного оркестратора и любая ошибка после старта блокируют planning/review без fallback. Forge не устанавливает и не авторизует внешние CLI автоматически.

AI Development Forge — documentation-first фреймворк для совместной разработки с кодовыми агентами Codex CLI, Claude Code CLI и OpenCode.

Фреймворк хранит продуктовый и execution-контекст в репозитории, использует сильную основную модель как оркестратор и генерирует нативных субагентов и portable skills для поддерживаемых платформ.

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
.opencode/agents/
```

`SPEC`, `ARCHITECTURE`, `BACKLOG`, ADR, Epic plan и TASK являются источниками истины. Отдельные Markdown-отчёты для review, testing, fuzzing, security или ручной проверки не создаются.

Mutation testing доступен отдельно через `forge-mutation-test` и никогда не является lifecycle gate. Bare-запрос использует fast `mutation-runner` и возвращает metrics; strong `mutation-analyzer` запускается только по отдельному разрешению и только при наличии текущих candidates. История попыток сохраняется как project-owned `MUT-NNNN` records без изменения Backlog, Epic или TASK.

## Установка

1. Скопируйте папку `.ai/` из этого репозитория в корень целевого проекта.
2. Откройте проект в Codex CLI, Claude Code CLI или OpenCode.
3. Отправьте один из bootstrap-промптов ниже.
4. Отвечайте на вопросы и подтверждайте каждый из шести этапов отдельно.

Исполняемого CLI у фреймворка нет: установка выполняется копированием `.ai/` и инструкцией агенту.

Не запускайте bootstrap внутри самого репозитория `ai_dev_forge`: он хранит исходный framework bundle, а не является проектом-потребителем.

## Новый проект

```text
Read .ai/BOOTSTRAP.md and initialize this repository as a new project.
Create Codex, Claude Code, and OpenCode adapters.
Communicate with me in Russian and start the product interview.
```

Если описание продукта уже существует, вставьте его в сообщение или приложите/укажите файл. Если описания недостаточно, агент проведёт итеративное product interview.

## Существующий проект

```text
Read .ai/BOOTSTRAP.md and initialize this existing repository.
Analyze the current code and documentation before starting the interview.
Create Codex, Claude Code, and OpenCode adapters.
Communicate with me in Russian.
```

Код, тесты и прежняя документация рассматриваются как evidence, а не как автоматическая продуктовая истина. Конфликты показываются пользователю; найденные баги и technical debt попадают в Backlog только после подтверждения.

## Шесть этапов bootstrap

1. Product Discovery → утверждённый `SPEC.md`.
2. System Design → `ARCHITECTURE.md`, ADR и генерируемый `DECISIONS.md`.
3. Release Planning → `BACKLOG.md` с Epic Roadmap и Defect Queue.
4. Prepare Workspace → strong `epic-planner`, approved queued workspace under `execution/planned/`, затем optional отдельный Epic Start с атомарным move в `execution/active/`.
5. Create Platform Adapters → все enabled native adapter-наборы и `.ai/framework.lock`.
6. Final Validation → проверка структуры, lifecycle, ownership, parity и восстановления без истории сессии.

Первая TASK после bootstrap остаётся `TODO` и требует отдельного Task Start.

## Нативные адаптеры

| Codex CLI | Claude Code CLI | OpenCode |
| --- | --- | --- |
| `AGENTS.md` | `CLAUDE.md` → `@AGENTS.md` | `AGENTS.md` |
| `.codex/agents/*.toml` | `.claude/agents/*.md` | `.opencode/agents/*.md` |
| `.agents/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` | `.agents/skills/*/SKILL.md` |

Нейтральные определения находятся в `.ai/framework/`. Полный router генерируется только в `AGENTS.md` и нативно используется Codex и OpenCode; `CLAUDE.md` содержит `@AGENTS.md` и импортирует его в Claude Code без копирования. OpenCode обнаруживает portable skills прямо в `.agents/skills/`, поэтому `.opencode/skills/` не генерируется. Проектные дополнения к router хранятся только в `.ai/custom/router-shared.md`.

Framework defaults для субагентов: Codex `strong = gpt-5.6-sol/medium`, `balanced = gpt-5.6-terra/medium`, `fast = gpt-5.6-luna/medium`; Claude Code `strong = opus/medium`, `balanced = sonnet/medium`, `fast = haiku/medium`. Для OpenCode универсальных defaults нет: включённый adapter требует три явно подтверждённых значения `provider/model-id`, полученных от пользователя или из локального `opencode models`. Forge не устанавливает OpenCode, не настраивает provider и не хранит credentials. В режиме `native_subagents` все Claude Code agent-файлы получают override `effort: high`; настройки Codex, OpenCode и внешнего маршрута `codex_with_claude` не меняются.

Forge управляет только manifest-declared `.opencode/agents/*.md`. `opencode.json`, commands, plugins, skills и пользовательские агенты сохраняются как project-owned файлы.

Сгенерированные adapters вручную не редактируются и применяются через синхронизацию.

## Два TASK delivery track

Каждая TASK получает ровно один delivery track: `fast` или `standard`. Это отдельная ось, не связанная напрямую с model tier (`fast` / `balanced` / `strong`) или `risk level`: низкий риск сам по себе не разрешает fast track.

`fast` предназначен только для ограниченного, обратимого, однозначного изменения с детерминированной локальной проверкой. Он запрещён при изменении публичного контракта, security/privacy/auth, persistence или формата данных, schema/migration, concurrency/shared core, dependencies/build/package/deploy/runtime infrastructure, внешней интеграции, critical path или ослаблении тестов. Неопределённость тоже означает `standard`.

Оба track используют implementer и сохраняют TDD. В `fast` reviewer и tester не вызываются: оркестратор независимо сверяет scope и fingerprint, проверяет целостность тестов и повторяет утверждённые focused checks, после чего TASK может перейти `IN PROGRESS → AWAITING USER ACCEPTANCE`. В `standard` остаётся полный путь implementer → strong reviewer → tester. Любой провал проверки, расширение surface или сомнение монотонно повышает `fast → standard`; обратный переход после Task Start запрещён. Старые TASK без поля track трактуются как `standard`.

Выбор delivery track не меняет Task Acceptance, Epic Validation и fuzzing: эти gates остаются обязательными в прежнем объёме.

## Проверка качества

Обычная TASK использует focused RED/GREEN, выбранные affected-component tests и scoped quality checks, а её Verification Plan фиксирует `Fuzzing impact` и bounded `Task fuzz smoke` либо rationale неприменимости. Review Packet разделяет `production_review_paths` и `supporting_evidence_paths` и хранит отдельный production fingerprint. Strong reviewer независимо проверяет только production surface: исполняемый код и runtime/schema/migration/build/package/deployment artifacts, способные изменить shipped behavior. Ошибки тестов, fixtures, snapshots и dev-only файлов он возвращает отдельными advisory observations; они не мешают `CLEAN` и не запускают новый strong review. Supporting-only исправление сохраняет clean review при том же production fingerprint и повторяет только tester gate. Tester по-прежнему блокирует TASK при падающих, слабых или недостаточных тестах. Canonical-документы служат только контекстом. Полный project test suite и unscoped project-wide lint/typecheck/build не являются Task gate.

Epic planner заранее создаёт Epic Fuzzing Plan и оценивает applicability. После принятия последней TASK Epic переходит в `VALIDATING`; отдельный `epic-validator` запускает полный regression suite, глобальные quality checks, critical-path validation и применимые gates выбранных project profiles. Только текущий passing Epic Validation fingerprint допускается к fuzzing gate. При актуальном approved `not applicable` оркестратор записывает `NOT APPLICABLE` без вызова fuzzer; `applicable`, `unresolved` или противоречащие итоговые evidence требуют read-only fuzzer перед Epic Acceptance.

Можно заранее подготовить несколько `PLANNED + READY` Epic. Каждый approved plan и его `TODO` TASK definitions хранятся в собственном `execution/planned/EPIC-*`; порядок очереди остаётся только в `BACKLOG.md`. Plan Approval не активирует Epic, а Epic Start отдельно проверяет dependencies/blockers и перемещает один eligible workspace в `execution/active/`.

## Внешняя инфраструктура

- Hooks не создаются автоматически.
- MCP-конфигурация не создаётся автоматически.
- Проект может добавить собственные hooks, MCP, API или CLI отдельно.
- `.ai/integrations/` — необязательный project-owned registry; чистый Forge не содержит эту папку и не выполняет connector preflight.

Локальная интеграция описывает provider-neutral capability (`work_source`, `knowledge_source`, `data_source`, `analysis_service` или project-defined profile), разрешённые операции, scope, consumers и platform-local bindings. Само наличие записи не разрешает вызов: выбранный framework/project-owned skill должен явно потреблять совместимый profile.

Kaiten — только пример `work_source`. Для такого profile Forge может хранить двусторонние ссылки `external item ↔ EPIC/BUG/TASK`; остальные типы не получают искусственных связей с Backlog. Framework upgrade работает offline, сохраняет неизвестные project-owned profiles и отделяет замену Forge от отдельно подтверждаемой миграции integration schema. Подробнее: [локальные интеграции](docs/local-integrations.md).

Feature discovery, root-cause investigation, test-driven implementation и evidence verification встроены в Forge lifecycle skills и agent contracts. Внешние process skills не управляют lifecycle проекта.

Mutation backend не входит в обязательные зависимости. Проект отдельно настраивает подтверждённую команду для своего языка; отсутствие backend не мешает bootstrap, adapter sync, migration или обычной разработке и даёт `SETUP REQUIRED` только при явном mutation-запросе.

## Дальнейшая работа

- [Архитектура фреймворка](FRAMEWORK.md)
- [Операционные сценарии](RUNBOOK.md)
- [Миграция между версиями](MIGRATION.md)

Для продолжения разработки попросите основного агента прочитать соответствующий root router и восстановить состояние из `BACKLOG.md`, execution-файлов и Git.
