# AI Development Forge

Documentation-first фреймворк для совместной разработки с кодовыми агентами Codex CLI, Claude Code CLI и OpenCode. Продуктовый и execution-контекст хранится в репозитории; сильная основная модель оркестрирует специализированных субагентов, а adapters генерируются из одного нейтрального источника.

## Что создаётся

```text
README.md
AGENTS.md
CLAUDE.md
SPEC.md
ARCHITECTURE.md
BACKLOG.md
BACKLOG-ARCHIVE.md
DECISIONS.md
decisions/ADR-NNN-<name>.md
investigations/INV-NNNN-<name>.md
intents/INT-NNNN-<name>.md
execution/{planned,active,paused,completed}/
.ai/
.codex/agents/
.agents/skills/
.claude/agents/
.claude/skills/
.opencode/agents/
```

`SPEC`, `ARCHITECTURE`, `BACKLOG`, ADR, Epic plan и TASK — источники истины. `INV-NNNN` хранит каноническую историю ad hoc исследования, `INT-NNNN` — продуктовых запросов. Терминальные строки Backlog автоматически переносятся в append-only `BACKLOG-ARCHIVE.md`; живой файл остаётся размером с активный горизонт. Mutation testing доступен отдельно через `forge-mutation-test` и никогда не является lifecycle gate.

## Установка

1. Скопируйте папку `.ai/` из этого репозитория в корень целевого проекта.
2. Откройте проект в Codex CLI, Claude Code CLI или OpenCode.
3. Отправьте bootstrap-промпт ниже.
4. Подтверждайте каждый из шести этапов отдельно.

Глобальная установка CLI не требуется: скопируйте `.ai/` и дайте агенту bootstrap-инструкцию. Не запускайте bootstrap внутри самого репозитория `ai_dev_forge`.

### Новый проект

```text
Read .ai/BOOTSTRAP.md and initialize this repository as a new project.
Create Codex, Claude Code, and OpenCode adapters.
Communicate with me in Russian and start the product interview.
```

### Существующий проект

```text
Read .ai/BOOTSTRAP.md and initialize this existing repository.
Analyze the current code and documentation before starting the interview.
Create Codex, Claude Code, and OpenCode adapters.
Communicate with me in Russian.
```

Код и прежняя документация — evidence, а не автоматическая продуктовая истина. Конфликты показываются пользователю; баги попадают в Backlog только после подтверждения.

## Шесть этапов bootstrap

1. Product Discovery → утверждённый `SPEC.md`.
2. System Design → `ARCHITECTURE.md`, ADR и генерируемый `DECISIONS.md`.
3. Release Planning → `BACKLOG.md` с Epic Roadmap и Defect Queue.
4. Prepare Workspace → `epic-planner`, approved queued workspace under `execution/planned/`, optional Epic Start.
5. Create Platform Adapters → enabled native adapter-наборы и `.ai/framework.lock`.
6. Final Validation → проверка структуры, lifecycle, ownership, parity и восстановления без истории сессии.

Первая TASK после bootstrap остаётся `TODO` и требует отдельного Task Start.

## Нативные адаптеры

| Codex CLI | Claude Code CLI | OpenCode |
| --- | --- | --- |
| `AGENTS.md` | `CLAUDE.md` → `@AGENTS.md` | `AGENTS.md` |
| `.codex/agents/*.toml` | `.claude/agents/*.md` | `.opencode/agents/*.md` |
| `.agents/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` | `.agents/skills/*/SKILL.md` |

Нейтральные определения находятся в `.ai/framework/`. Router генерируется в `AGENTS.md` и используется Codex и OpenCode; `CLAUDE.md` содержит только `@AGENTS.md`. OpenCode обнаруживает portable skills в `.agents/skills/`. Проектные дополнения к router — `.ai/custom/router-shared.md`. Сгенерированные adapters не редактируются вручную и применяются через синхронизацию.

Framework defaults для субагентов: Codex `strong = gpt-6.1-sol/high`, `balanced = gpt-6-luna/xhigh`, `fast = gpt-5.6-luna/medium`; Claude Code `strong = opus/high`, `balanced = sonnet/high`, `fast = haiku/high`. Для OpenCode универсальных defaults нет: включённый adapter требует три явно подтверждённых `provider/model-id`. Forge не устанавливает OpenCode и не хранит credentials. В режиме `native_subagents` Claude Code agent-файлы получают override `effort: high`.

## Planner/reviewer route

`.ai/project.yaml` хранит один явный `role_execution.mode` для `epic-planner` и `reviewer`:

- `claude_with_codex` — Forge в Claude Code делегирует обе роли Codex CLI через fresh ephemeral read-only `codex exec`, pinned `gpt-6.1-sol/high`;
- `codex_with_claude` — Forge в Codex вызывает Claude Code CLI 2.1.203+ через fresh `claude -p`, JSON output, plan mode, read-only tools;
- `native_subagents` — внутренние агенты активной платформы без внешнего preflight.

Bootstrap и migration требуют явного выбора. Недоступность выбранного runtime, несовпадение оркестратора и любая ошибка блокируют planning/review без fallback. Forge не устанавливает и не авторизует внешние CLI.

## TASK delivery track

Каждая TASK получает ровно один delivery track: `fast` или `standard`. Это отдельная ось от model tier и `risk level`: низкий риск сам по себе не разрешает fast track.

`fast` — только ограниченное, обратимое, однозначное изменение с детерминированной локальной проверкой. Он запрещён для public contract, security/privacy/auth, persistence/data format, schema/migration, concurrency/shared core, dependencies/build/package/deploy/runtime infrastructure, внешних интеграций, critical path, ослабления тестов и любой неопределённости. Оба track используют implementer и TDD. В `fast` reviewer и tester не вызываются: оркестратор проверяет scope и fingerprint, test integrity и повторяет approved checks. В `standard` — implementer → strong reviewer → tester. Любой провал повышает `fast → standard`; обратный переход после Task Start запрещён. Старые TASK без поля track трактуются как `standard`. Task Acceptance, Epic Validation и fuzzing остаются обязательными.

## Проверка качества

Обычная TASK использует focused RED/GREEN, affected-component tests и scoped quality checks. Verification Plan фиксирует `Fuzzing impact` и bounded `Task fuzz smoke` либо rationale неприменимости. Review Packet разделяет `production_review_paths` и `supporting_evidence_paths` с отдельным production fingerprint. Strong reviewer проверяет только production surface (исполняемый код и runtime/schema/migration/build/package/deployment artifacts); ошибки тестов и dev-only файлов — advisory observations. Tester блокирует TASK при падающих, слабых или недостаточных тестах. Полный project suite и unscoped project-wide lint/typecheck/build не являются Task gate.

Epic planner создаёт Epic Fuzzing Plan и оценивает applicability (`applicable`, `not applicable`, `unresolved`). После последней TASK `epic-validator` запускает полный regression suite, project-wide checks, critical-path validation и quality-profile gates. При актуальном approved `not applicable` оркестратор записывает `NOT APPLICABLE` без вызова fuzzer; `applicable`, `unresolved` или противоречивые evidence требуют read-only fuzzer перед Epic Acceptance.

Можно заранее подготовить несколько `PLANNED + READY` Epic. Plan Approval не активирует Epic; Epic Start проверяет dependencies/blockers и перемещает один workspace в `execution/active/`.

## Python-автоматизация

Повторяемые операции выполняются локально через `.ai/tools/forge.py`: контекст, извлечение разделов, fingerprints, структурная валидация и конформанс, генерация adapters, запуск checks, агрегация метрик. Статусные правки идут через preview/apply с journal-транзакцией и rollback: `transition`, `epic-start`, `epic-complete`, `accept-record`, `backlog`, `inv-create`, `commit-scoped`. Хелперы исполняют уже утверждённые изменения; авторизация, семантические gates и приёмка остаются за пользователем и оркестратором. Для разработки самого Forge:

```text
python -m venv .forge-venv
.forge-venv/Scripts/python -m pip install -r .ai/tools/requirements.txt
.forge-venv/Scripts/python .ai/tools/forge.py validate
.forge-venv/Scripts/python -m unittest discover -s tests -p "test_*.py" -v
node --test tests/*.test.mjs
```

На Linux/macOS путь — `.forge-venv/bin/python`. Python-инструменты необязательны для проектов-потребителей. Подробности: [.ai/tools/USAGE.md](.ai/tools/USAGE.md), [инвентаризация автоматизации](docs/deterministic-automation.md).

## Внешняя инфраструктура

- Hooks, MCP-конфигурация и credentials не создаются автоматически.
- `.ai/integrations/` — необязательный project-owned registry; чистый Forge его не содержит.
- Kaiten — пример `work_source`. Такой profile может хранить связи `external item ↔ EPIC/BUG/TASK`; остальные типы не получают искусственных связей с Backlog.
- Framework upgrade работает offline и сохраняет project-owned profiles. Подробнее: [локальные интеграции](docs/local-integrations.md).

Mutation backend не входит в обязательные зависимости; Forge не устанавливает backend автоматически. Отсутствие backend не мешает обычной разработке и даёт `SETUP REQUIRED` только при явном mutation-запросе. `mutation-runner` возвращает metrics-only; strong `mutation-analyzer` запускается только по отдельному разрешению.

## Intent records

Материальные запросы новых фич, продуктовых изменений и external work фиксируются `intents/INT-NNNN-<name>.md`: intake резервирует ID, дозаполняет шаблон через короткое интервью и подтверждает запись до создания Epic. Каждый INT имеет один outcome (`draft/accepted/promoted/rejected/deferred/superseded`). Отвергнутые и отложенные идеи сохраняются с rationale; Epic planner читает INT как первичный вход. Баги и bootstrap intent-записей не создают.

## Ad hoc исследования

`forge-investigate` позволяет основному агенту исследовать проблему без создания Epic/TASK и без вызова субагентов. Материальный результат сохраняется в `investigations/INV-NNNN-<name>.md` с outcome: `no_action`, `promoted`, `fixed_directly` или `unresolved`. Для `fixed_directly` INV фиксирует added, modified и removed paths, влияние, проверки, результаты и revision либо scoped-diff fingerprint. Commit требует отдельного разрешения. Позднее intake или Epic planner может использовать `research_refs: [INV-NNNN]`.

## Миграция между версиями

Из корня обновляемого проекта выполните staging-команду из [MIGRATION.md](MIGRATION.md#подготовить-ai-next): временный sparse clone оставит в проекте `.ai-next/`. Затем откройте проект в Codex/Claude Code/OpenCode:

```text
Прочитай .ai-next\MIGRATE.md и сам проведи миграцию Forge в этом проекте.
Сам запусти preview, спроси только необходимые решения и финальное подтверждение,
после подтверждения сам примени миграцию. Не проси меня переносить preview_token или собирать команды.
```

Preview не пишет ничего и возвращает `preview_token`; apply выполняет одну транзакцию с backup-журналом и rollback. Ручной режим:

```text
python .ai-next/tools/forge.py migrate
python .ai-next/tools/forge.py migrate --apply PREVIEW_TOKEN
```

## Дальнейшая работа

- [Архитектура фреймворка](FRAMEWORK.md)
- [Операционные сценарии](RUNBOOK.md)
- [Миграция между версиями](MIGRATION.md)
