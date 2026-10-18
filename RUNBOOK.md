# AI Development Forge — Runbook

## Локальные операции без вызова модели

Восстановление начинайте с `python .ai/tools/forge.py context`: прочитайте metadata, затем Backlog и текущие evidence. `section` извлекает разделы, `fingerprint` хеширует scope, `validate --project --adapters` проверяет структуру, drift и конформанс. `evidence-check <TASK-path>` возвращает вердикты review-freshness/testing/fast-assurance; `evidence-check --epic <EPIC-ID>` — готовность Epic gate. `next-id --kind <task|bug|inv|epic|adr|mut>` выделяет идентификаторы.

Поиск: `query "<термины>" [--kind ...] [--area ...] [--since YYYY-MM]` — ранжированные указатели по durable-записям, включая `execution/completed/` и архив Backlog. Индекс `.ai/local/index.db` пересобирается автоматически и не является evidence.

Для sync используйте `adapters --diff` и утверждённый preview token. Для проверок — `checks <packet.json> --execute`. `role --assignment-file` подставляет нейтральный контракт и выполняет bounded preflight. Нельзя автоматически сменить provider после ошибки.

Статусные правки идут через helpers: `transition task|epic`, `epic-start`, `epic-complete`, `accept-record`, `backlog add-bug|update-row|archive-row|archive-all`, `inv-create`, `commit-scoped`. Мутирующие команды показывают preview и применяются по `--apply TOKEN` с journal-откатом. Терминальные переходы переносят строку в `BACKLOG-ARCHIVE.md` той же транзакцией. `backlog stale-rows --older-than <N>` — read-only отчёт об устаревших строках. Форматы команд: [.ai/tools/USAGE.md](.ai/tools/USAGE.md).

При bounded Task Start grant выполните `task-start-check <TASK-path>`. Приёмка и Git gates остаются отдельными.

## Режим выполнения planner и reviewer

`.ai/project.yaml` хранит `role_execution.mode`: `claude_with_codex` (Claude Code + Codex CLI через `codex exec`), `codex_with_claude` (Codex + Claude Code 2.1.203+), `native_subagents` (внутренние агенты платформы). Для OpenCode-led setup при отсутствии route предлагается `native_subagents`; запись только после approval. Обе роли получают полный neutral contract и тот же Epic assignment или Review Packet.

Выбранный внешний route не имеет fallback: preflight failure, несовпадение оркестратора, timeout, malformed result блокирует стадию. Для переключения измените `role_execution.mode` с подтверждением и выполните adapter sync.

Для `claude_with_codex` используйте managed launcher:

```text
node .claude/forge/codex-role-runner.mjs --preflight
node .claude/forge/codex-role-runner.mjs --role <epic-planner|reviewer> --prompt-file <temporary-file>
```

Launcher ищет Codex: `FORGE_CODEX_BIN`, `%APPDATA%\npm\`, каталог `node.exe`, затем PATH. Каждый кандидат проверяется через `codex --version`, `codex exec --help`, `codex login status`. Prompt передаётся через stdin в `codex exec --ephemeral --sandbox read-only`. Из child environment удаляются `BASH_ENV`, `CLAUDE_PLUGIN_DATA`, `CODEX_COMPANION_*`. Разрешённые исправления: установить `@openai/codex`, `codex login`, перезапустить Claude Code или задать `FORGE_CODEX_BIN`.

## Вызов skills

| Действие | Codex CLI | Claude Code |
| --- | --- | --- |
| Явный skill | `$forge-skill-name` | `/forge-skill-name` |
| Root router | `AGENTS.md` | `CLAUDE.md` |

Обычный запрос допустим, но обязательный lifecycle маршрутизируется через Forge skill.

## 1. Новый проект

1. Скопируйте `.ai/` в корень проекта.
2. Отправьте:

```text
Read .ai/BOOTSTRAP.md and initialize this repository as a new project.
Create Codex, Claude Code, and OpenCode adapters.
Communicate with me in Russian and start the product interview.
```

3. Утверждайте SPEC, архитектуру/ADR, Backlog, Epic plan, optional Epic Start, adapters и final validation отдельно.
4. После bootstrap первая TASK остаётся `TODO`.

Skill: `forge-bootstrap-new`.

## 2. Существующий проект

```text
Read .ai/BOOTSTRAP.md and initialize this existing repository.
Analyze the current code and documentation before starting the interview.
Create Codex, Claude Code, and OpenCode adapters.
Communicate with me in Russian.
```

Агент собирает evidence из кода, тестов, документов и Git, показывает конфликты до создания canonical target state. Найденные проблемы попадают в Backlog после решения пользователя.

Skill: `forge-bootstrap-existing`.

## 3. Продолжение разработки

```text
Read the project router, recover development state from canonical files and Git, and report the current gate.
```

Skill `forge-resume-development` определяет ordered `execution/planned/` queue, active/paused Epic, TASK statuses, текущий gate, актуальность fingerprints и незавершённый Git diff. Если результат не сохранён в TASK или plan, этап выполняется повторно. `query` помогает найти прошлый контекст по ADR/INV/INT/TASK.

## 3A. Локальные интеграции

Чистый Forge не имеет `.ai/integrations/`. Проект добавляет definition по `.ai/templates/integration.yaml` и настраивает MCP/API/CLI отдельно. Definition содержит profile, operations, scope, access policy, consumers и bindings, но не credentials. Вызов — только явно выбранным совместимым skill.

Для доски задач используется `work_source` и `forge-intake-external-work`. Product-change кандидаты фиксируются intent-записью (`origin: external-work`) до canonical-изменений; отвергнутые остаются `rejected` INT. Связи с Epic/Bug/Task записываются после approval; доска не становится lifecycle authority. Примеры: [docs/local-integrations.md](docs/local-integrations.md).

## 4. Новая feature или идея

```text
Добавь новую фичу: <описание>.
```

Skill `forge-intake-feature`:

1. резервирует `INT-NNNN` и пишет черновик `intents/INT-NNNN-<name>.md`;
2. дозаполняет шаблон через интервью и показывает запись на подтверждение;
3. уточняет target behavior;
4. создаёт `PLANNED/OUTLINE` Epic со ссылкой на INT;
5. показывает SPEC diff и при необходимости ARCHITECTURE/ADR diff;
6. переводит Epic в `READY` после утверждения requirements, boundaries и dependencies;
7. не изменяет active work без Replan.

Отвергнутая или отложенная идея остаётся INT-записью (`outcome: rejected`/`deferred`) без Epic.

## 5. Новый баг

```text
Зафиксируй баг: <ожидаемое и фактическое поведение>.
```

Skill `forge-intake-bug` определяет происхождение: баг в непринятой TASK возвращает ту же TASK в `IN PROGRESS`; баг в принятом коде получает `BUG-*` со status `OPEN`. Пользователь выбирает severity/priority и способ планирования. Терминальное разрешение архивирует строку той же транзакцией.

## 6. Переприоритизация

Skill `forge-reprioritize-backlog` строит dependency graph и сравнивает его с пользовательским порядком. Конфликтующий порядок объясняется и меняется только после подтверждения. `backlog stale-rows --older-than <N>` подсвечивает кандидатов на отмену; закрытие остаётся явным решением. Легаси-терминальные строки переносятся `backlog archive-all` или `archive-row --id <ID>`.

## 7. Подготовка Epic

Skill `forge-prepare-epic` для Plan Approval требует status `PLANNED`, readiness `READY`, approved requirements и boundaries, явные dependencies/blockers, отсутствие другого workspace для того же Epic. Unsatisfied dependencies блокируют Epic Start, но не подготовку очереди. Оркестратор вызывает `epic-planner`, проверяет предложение и показывает plan и TASK definitions. После Plan Approval создаётся `execution/planned/EPIC-*`; Backlog status остаётся `PLANNED`. Epic Start отдельно проверяет зависимости и перемещает workspace в `execution/active/`.

## 8. Запуск и выполнение TASK

Task Start всегда явный. Перед подтверждением покажите goal, scope, acceptance criteria, affected surface, risk flags, Verification Plan, review focus и delivery track с rationale.

```text
Task Start
→ implementer
├─ fast → orchestrator assurance
└─ standard → strong reviewer → tester
→ AWAITING USER ACCEPTANCE
```

Delivery track — отдельная ось от model tier и `risk level`. `fast` разрешён только для ограниченной, обратимой, однозначной TASK с детерминированной проверкой. Public contract, auth/security/privacy, persistence/data format/schema/migration, concurrency/shared core, dependency/build/package/deploy/runtime infrastructure, внешняя интеграция, critical path, ослабление тестов или неопределённость требуют `standard`. Оба track используют implementer и TDD.

На fast track оркестратор без reviewer и tester проверяет scope, fingerprint, test integrity и повторяет approved focused checks. Standard track использует Review Packet, strong reviewer и tester. Reviewer выполняет adversarial review production surface; дефекты тестов и dev-only artifacts — advisory observations. Tester запускает:

1. новые/изменённые тесты;
2. affected-component tests;
3. bounded `Task fuzz smoke` при итоговом fuzzing impact;
4. scoped lint, typecheck, build и profile-specific checks.

Полный project test suite и unscoped project-wide checks не являются Task gate. После production-исправления заново выполняются strong review и testing; после supporting-only — только selected testing.

## 9. Ручная проверка и Task Acceptance

Пока пользователь тестирует, TASK остаётся `AWAITING USER ACCEPTANCE`. Возможные ответы: принять TASK, запросить исправления, продолжить проверку. Skill `forge-complete-task` переводит TASK в `DONE` после явного Task Acceptance. Task Acceptance и следующий Task Start — разные gates.

## 10. Replan

Изменение scope, порядка или состава TASK активного Epic требует причины, точного diff plan/TASK, подтверждения пользователя. Опечатки и исправления ссылок Replan не требуют. Новая или изменённая TASK требует собственного Task Start.

## 11. Завершение Epic, validation и fuzzing

Skill `forge-complete-epic` переводит Epic в `VALIDATING` и вызывает `epic-validator` для exact aggregate fingerprint: полный regression suite, project-wide lint/typecheck/build, integration/E2E, critical paths и quality-profile gates.

Результаты Epic Validation: `PASSED` → `FUZZING`; `PASSED WITH ACCEPTED EXCEPTIONS` → `FUZZING` после принятия рисков; `FAILED` → `ACTIVE` и Replan; `BLOCKED` → `ACTIVE` и решение по отсутствующей capability.

После passing Epic Validation выполняется fuzzing gate. При approved `not applicable` оркестратор не вызывает fuzzer, если все итоговые Task impacts `none`, surface совпадает с планом, alternative risk coverage прошёл и fingerprint актуален; иначе вызывается read-only fuzzer. Результаты: `PASSED`, `NOT APPLICABLE`, `HARNESS REQUIRED`, `FINDINGS`. После изменений повторяются review, testing, Epic Validation и fuzzing. Epic Acceptance завершает Epic; следующий queued Epic не запускается автоматически.

## 12. Pause и resume

Приостановка требует подтверждения: Epic/TASK получают `PAUSED`, каталог перемещается согласованно с Backlog. Продолжение — через `forge-resume-development` с явным разрешением.

## 13. Security audit

`forge-security-audit` запускается явным запросом с точным scope. По умолчанию strong security auditor local, read-only, без установки инструментов, network и production/external scanning. Findings превращаются в Bug, TASK или Epic по решению пользователя.

## 13A. Ad hoc investigation

```text
Исследуй, почему алгоритм расчёта работает медленно.
```

`forge-investigate` создаёт `investigations/INV-NNNN-<name>.md`, не вызывает субагентов и сам выбирает проверки, experiments, benchmarks или profiling. «Исследуй и исправь» разрешает прямое исправление в пределах проблемы. Outcomes:

- `no_action` — сохранить выводы;
- `promoted` — оформить Bug, Epic или Replan через существующий approval;
- `fixed_directly` — исправить и проверить без TASK workflow;
- `unresolved` — сохранить гипотезы и следующие эксперименты.

При `fixed_directly` INV перечисляет added, modified и removed paths, verification commands/results и fingerprint. Commit не выполняется автоматически. При promotion Epic planner проверяет baseline и использует актуальные выводы через `research_refs`.

## 13B. Standalone mutation testing

Mutation testing не зависит от Task/Epic lifecycle:

```text
Проведи mutation testing для src/billing с тестами tests/billing.
```

Skill `forge-mutation-test` требует exact scope, fingerprint, команды и budget. Bare-запуск — fast `mutation-runner`: baseline, mutation backend, normalized metrics и запись `quality/mutation-testing/runs/MUT-NNNN.yaml`. Forge не устанавливает backend; отсутствие настройки даёт `SETUP REQUIRED`. Strong `mutation-analyzer` — только по явному разрешению при наличии candidates:

```text
Проведи mutation testing для src/billing и проанализируй выжившие мутанты, максимум 20 candidates.
```

Отложенный анализ того же `MUT-0007` не повторяет campaign. Mutation run не меняет Backlog, Epic/TASK status, gates или development evidence.

## 14. Adapter sync

Используйте `forge-sync-adapters` после изменения neutral agents/skills, model mappings, `.ai/custom/router-shared.md` или framework release. Skill показывает collision diff, пересоздаёт adapters, проверяет `AGENTS.md`, `@AGENTS.md` импорт, OpenCode agents, skills parity и обновляет `.ai/framework.lock`. `.ai/integrations/` не является render input.

## 14A. Framework upgrade с локальными интеграциями

`forge-migrate-framework` классифицирует integration files как absent/current/older-migratable/malformed/future/custom/collision. Framework bundle обновляется offline и сохраняет integrations byte-for-byte. Older-migratable schema меняется отдельным diff и approval с backup. Malformed/future/custom profile блокирует только свой consumer.

## 15. Git policy

- `role_execution.mode` — `claude_with_codex`, `codex_with_claude` или `native_subagents`;
- `platforms.opencode.enabled` и три явных OpenCode model ID формата `provider/model-id`;
- `manual` — commit после Task Acceptance требует отдельного разрешения;
- `auto_commit_after_acceptance` — commit разрешён после clean review, testing, Task Acceptance и `DONE`.

До Task Acceptance commit запрещён. В commit нельзя включать посторонние изменения.

## 16. Проверка фреймворка

`forge-check-framework` выполняет read-only проверку: ownership и hashes, IDs, frontmatter, links и transitions, Backlog/execution alignment, adapter parity и лимит routers, восстановимость текущего gate без истории сессии. Исправления — отдельным skill через необходимые user gates.
