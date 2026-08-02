# AI Development Forge v3

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
execution/{active,paused,completed}/
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
4. Prepare Workspace → утверждённый Epic plan и TASK-файлы, затем отдельный Epic Start.
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

Framework defaults для субагентов: Codex `strong = gpt-5.6-sol/high`, `balanced = gpt-5.6-terra/medium`, `fast = gpt-5.6-luna/medium`; Claude Code `strong = opus/high`, `balanced = sonnet/high`, `fast = haiku/high`. Проект может явно переопределить их в `.ai/project.yaml`; генератор записывает resolved mapping в нативные agent-файлы обеих платформ.

Сгенерированные adapters вручную не редактируются и применяются через синхронизацию.

## Внешняя инфраструктура

- Hooks не создаются автоматически.
- MCP-конфигурация не создаётся автоматически.
- Проект может добавить собственные hooks и MCP отдельно.

Feature discovery, root-cause investigation, test-driven implementation и evidence verification встроены в Forge lifecycle skills и agent contracts. Внешние process skills не управляют lifecycle проекта.

## Дальнейшая работа

- [Архитектура фреймворка](FRAMEWORK.md)
- [Операционные сценарии](RUNBOOK.md)
- [Подробные пошаговые сценарии и диалоги](FRAMEWORK_WORKFLOWS.md)
- [Утверждённый подробный дизайн](FRAMEWORK_DESIGN.md)

Для продолжения разработки попросите основного агента прочитать соответствующий root router и восстановить состояние из `BACKLOG.md`, execution-файлов и Git.
