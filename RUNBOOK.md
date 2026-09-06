# AI Development Forge v4.9 — Runbook

## Локальные операции без вызова модели

Начинайте восстановление с `python .ai/tools/forge.py context`: прочитайте все страницы metadata, затем Backlog и выбранные текущие evidence. `section` извлекает нужные разделы, `fingerprint` хеширует явный scope, `validate --project --adapters` проверяет структуру и drift. Не вызывайте context-collector для успешной механической инвентаризации.

Для sync используйте `adapters --diff`, затем применяйте утверждённый preview token. Для проверок — `checks <packet.json> --execute`; reuse требует явного полного dependency scope и не применяется к Epic Validation. `role` выполняет один bounded preflight внутри вызова. Нельзя автоматически сменить provider после ошибки.

При уже выданном bounded Task Start grant выполните `task-start-check <TASK-path>` и проверьте eligibility; повторное согласование той же неизменной задачи не требуется. Приёмка результата и Git gates остаются отдельными. Форматы команд и ограничения: [.ai/tools/USAGE.md](.ai/tools/USAGE.md).

## Режим выполнения planner и reviewer

Перед Epic planning и независимым review оркестратор читает `.ai/project.yaml`: `claude_with_codex` требует работу из Claude Code и локально установленный/авторизованный Codex CLI с `codex exec`; `codex_with_claude` требует работу из Codex и установленный/авторизованный Claude Code CLI 2.1.203+; `native_subagents` запускает одноимённые внутренние агенты Codex, Claude Code или OpenCode без внешней проверки. Для OpenCode-led setup при отсутствии утверждённого route предлагается существующий `native_subagents`, но записывается только после approval; новых режимов и fallback нет. Обе роли всегда получают полный neutral contract и тот же Epic assignment или Review Packet.

Выбранный внешний route не имеет fallback: недоступный preflight, несовпадение оркестратора, permission failure, timeout, malformed result или ошибка после старта блокирует стадию. Для переключения измените `role_execution.mode` с явным подтверждением и выполните adapter sync.

Для `claude_with_codex` агент выполняет только managed launcher:

```text
node .claude/forge/codex-role-runner.mjs --preflight
node .claude/forge/codex-role-runner.mjs --role <epic-planner|reviewer> --prompt-file <temporary-file>
```

Launcher сам ищет Codex: сначала явный абсолютный `FORGE_CODEX_BIN`, затем на Windows `%APPDATA%\npm\codex.exe|cmd|bat`, каталог текущего `node.exe` и только потом inherited PATH. Каждый кандидат реально проверяется командами `codex --version`, `codex exec --help` и `codex login status`; сломанный wrapper пропускается в пользу следующего кандидата. Prompt читается из временного файла и передаётся через stdin в `codex exec --ephemeral --sandbox read-only`. Launcher удаляет из child environment `BASH_ENV`, `CLAUDE_PLUGIN_DATA`, `CODEX_COMPANION_APP_SERVER_ENDPOINT` и `CODEX_COMPANION_SESSION_ID`, поэтому соседний Codex, stale plugin broker и его named pipe не участвуют в запуске.

Если preflight недоступен, агент сообщает точную диагностику и останавливает роль. Он не копирует `codex`, `codex.cmd`, `codex.ps1`, `node.exe` или другие wrappers в `~/bin`, не создаёт постоянный либо временный `BASH_ENV`, не удаляет и не перенаправляет plugin state, не завершает чужие процессы и не трогает pipe. Разрешённые исправления со стороны пользователя: установить/обновить `@openai/codex`, выполнить `codex login`, перезапустить Claude Code после изменения PATH либо однократно задать `FORGE_CODEX_BIN` абсолютным путём к настоящему executable. `codex-plugin-cc` можно оставить для его slash-команд, но Forge planner/reviewer его runtime не используют.

Этот runbook описывает повседневные действия. Детальные алгоритмы находятся в skills; основной агент должен явно выбрать нужный skill и сохранить результат в canonical файлах.

## Вызов skills

| Действие | Codex CLI | Claude Code |
| --- | --- | --- |
| Явный skill | `$forge-skill-name` | `/forge-skill-name` |
| Root router | `AGENTS.md` | `CLAUDE.md` |

Можно формулировать запрос обычным языком. Оркестратор всё равно должен явно маршрутизировать обязательный lifecycle через соответствующий Forge skill.

## 1. Новый проект

1. Скопируйте `.ai/` в корень проекта.
2. Отправьте:

```text
Read .ai/BOOTSTRAP.md and initialize this repository as a new project.
Create Codex, Claude Code, and OpenCode adapters.
Communicate with me in Russian and start the product interview.
```

3. Утверждайте отдельно SPEC, архитектуру/ADR, Backlog, Epic plan, optional Epic Start, adapters и final validation.
4. После bootstrap первая TASK остаётся `TODO`.

Skill: `forge-bootstrap-new`.

## 2. Существующий проект

После копирования `.ai/` отправьте:

```text
Read .ai/BOOTSTRAP.md and initialize this existing repository.
Analyze the current code and documentation before starting the interview.
Create Codex, Claude Code, and OpenCode adapters.
Communicate with me in Russian.
```

Агент сначала собирает evidence из кода, тестов, документов и Git. Он показывает конфликты с намерением пользователя до создания canonical target state. Найденные проблемы остаются кандидатами, пока пользователь не решит добавить их в Backlog.

Skill: `forge-bootstrap-existing`.

## 3. Продолжение разработки

Пример запроса:

```text
Read the project router, recover development state from canonical files and Git, and report the current gate.
```

Skill `forge-resume-development` определяет:

- ordered `execution/planned/` queue и Epic Start eligibility;
- active/paused Epic;
- TASK statuses и blockers;
- текущий gate;
- актуальность implementation/review/test/fuzz fingerprints;
- актуальность Epic Validation fingerprint и выбранных quality profiles;
- незавершённый Git diff.

История сессии необязательна. Если результат агента не сохранён в TASK или plan, соответствующий этап выполняется повторно.

## 3A. Локальные интеграции

Чистый Forge не имеет `.ai/integrations/`: никакой connector preflight не запускается, а bootstrap, lifecycle, adapter sync и migration работают без дополнительных требований.

Для локальной capability проект вручную добавляет definition по `.ai/templates/integration.yaml` и отдельно настраивает MCP/API/CLI. Definition содержит profile, semantic operations, scope, access policy, consumers и platform bindings, но не credentials. Интеграция вызывается только явно выбранным совместимым skill.

Для доски задач используется profile `work_source` и skill `forge-intake-external-work`. Запрос может назвать тикет или попросить прочитать configured queue. Агент показывает retrieval boundary, классификацию и split/combine proposal, затем использует обычные feature/bug/Replan/Plan Approval gates. Связи с Epic/Bug/Task записываются только после approval; доска не становится lifecycle authority и не изменяется.

Knowledge/data/analysis/custom profiles используют тот же registry, но не получают `EPIC/BUG/TASK` links. Полные примеры: [docs/local-integrations.md](docs/local-integrations.md).

## 4. Новая feature или идея

Запрос:

```text
Добавь новую фичу: <описание>.
```

Skill `forge-intake-feature`:

1. уточняет target behavior;
2. после подтверждения создаёт `PLANNED/OUTLINE` Epic;
3. показывает SPEC diff;
4. при необходимости показывает ARCHITECTURE/ADR diff;
5. переводит Epic в `READY` только после утверждения requirements, boundaries и dependencies;
6. не изменяет active work без Replan.

Новая функция не добавляется незаметно в TASK, которую пользователь тестирует вручную.

## 5. Новый баг

Запрос:

```text
Зафиксируй баг: <ожидаемое и фактическое поведение>.
```

Skill `forge-intake-bug` сначала определяет происхождение:

- баг в непринятой TASK возвращает ту же TASK в `IN PROGRESS` без нового `BUG-ID`;
- баг в ранее принятом коде после подтверждения получает `BUG-*` со status `OPEN`.

Пользователь отдельно выбирает severity/priority и способ планирования: Replan активного Epic, новый Bugfix Epic или оставить Bug открытым.

## 6. Переприоритизация

Skill `forge-reprioritize-backlog` строит dependency graph и сравнивает его с пользовательским порядком.

Если более поздний Epic блокирует более ранний, оркестратор:

1. объясняет конфликт;
2. предлагает перестановку;
3. спрашивает пользователя;
4. меняет порядок только после подтверждения.

Если порядок сохраняется, Epic остаётся `PLANNED` с `Blocked by`. Active work не меняется как побочный эффект.

## 7. Подготовка Epic

Skill `forge-prepare-epic` для Plan Approval требует:

- status `PLANNED`;
- readiness `READY`;
- approved requirements и boundaries;
- явно объявленные dependencies и blockers;
- отсутствие другого workspace для того же Epic.

Unsatisfied dependencies, blockers или другой active Epic не мешают подготовить очередь, но блокируют Epic Start. Оркестратор вызывает strong read-only `epic-planner`, независимо проверяет его предложение и показывает plan и все TASK definitions. После Plan Approval создаётся `execution/planned/EPIC-*` с approved plan и `TODO` TASK-файлами; Backlog status остаётся `PLANNED`.

Несколько planned workspaces могут сосуществовать, но их порядок определяется только Backlog. Отдельный Epic Start повторно проверяет dependencies, `Blocked by` и отсутствие другого active-work Epic, затем атомарно перемещает один каталог `execution/planned/ → execution/active/` и меняет status `PLANNED → ACTIVE`. Первая TASK всё равно требует отдельного Task Start.

## 8. Запуск и выполнение TASK

Task Start всегда явный. Перед подтверждением покажите goal, scope, acceptance criteria, affected surface, risk flags, Verification Plan, review focus и выбранный delivery track с rationale.

Skill `forge-run-task` запускает цикл:

```text
Task Start
→ implementer
├─ fast → orchestrator assurance
└─ standard → strong reviewer → tester
→ AWAITING USER ACCEPTANCE
```

Delivery track — отдельная ось от model tier и `risk level`. `fast` разрешён только для ограниченной, обратимой, однозначной TASK с детерминированной локальной проверкой. Публичный контракт, auth/security/privacy, persistence/data format/schema/migration, concurrency/shared core, dependency/build/package/deploy/runtime infrastructure, внешняя интеграция, critical path, ослабление тестов или неопределённость требуют `standard`. Legacy TASK без track также получает `standard`.

Оба track используют implementer и TDD. На fast track оркестратор без reviewer и tester независимо сверяет scope и fingerprint, проверяет test integrity и повторяет approved focused checks. Успех разрешает прямой переход `IN PROGRESS → AWAITING USER ACCEPTANCE`. Провал, дрейф eligibility или сомнение повышает TASK `fast → standard`; обратный переход после Task Start запрещён. Standard track использует обычные Review Packet, strong reviewer и tester, описанные ниже.

Implementer пишет production-код и focused tests. Review Packet разделяет production paths и supporting evidence и фиксирует отдельный production fingerprint. Reviewer не исправляет код и выполняет ordered adversarial review protocol для production surface. Только production findings влияют на outcome; дефекты тестов, fixtures, snapshots и dev-only artifacts идут отдельными advisory observations и совместимы с `CLEAN`. Runtime configuration, schemas, migrations, packaging, production build и deployment artifacts считаются production, если могут изменить shipped behavior. Canonical-документы остаются контекстом. Tester получает observations, не пишет тесты и запускает:

1. новые/изменённые тесты;
2. выбранные affected-component tests;
3. bounded `Task fuzz smoke`, если итоговый fuzzing impact затрагивает target или готовый harness; для `none` сверяет rationale с actual surface;
4. scoped lint, typecheck, build и применимые profile-specific checks.

Полный project test suite и unscoped project-wide checks не являются Task gate и по умолчанию запрещены implementer, reviewer и tester. Ранний полный прогон допустим только по явному запросу пользователя и не заменяет Epic Validation. После production-исправления заново выполняются strong review и selected testing. После supporting-only исправления clean review сохраняется при совпадающем production fingerprint, а selected testing выполняется заново без вызова strong reviewer.

## 9. Ручная проверка и Task Acceptance

Пока пользователь тестирует, TASK остаётся `AWAITING USER ACCEPTANCE` без таймаута.

Возможные ответы:

- принять TASK;
- запросить исправления;
- продолжить ручную проверку.

Skill `forge-complete-task` переводит TASK в `DONE` только после явного Task Acceptance и записывает решение в тот же TASK-файл.

Task Acceptance и следующий Task Start — разные gates. Одно сообщение может разрешить оба действия только если явно содержит оба решения.

## 10. Replan

Изменение scope, порядка или состава TASK активного Epic требует:

1. причины;
2. точного diff plan/TASK;
3. подтверждения пользователя;
4. только затем изменения файлов.

Опечатки и исправления ссылок Replan не требуют. Новая или изменённая TASK всё равно требует собственного Task Start.

## 11. Завершение Epic, validation и fuzzing

После принятия последней TASK skill `forge-complete-epic` переводит Epic в `VALIDATING` и автоматически вызывает `epic-validator` для exact aggregate fingerprint. Он запускает полный regression suite, project-wide lint/typecheck/build, integration/E2E, critical paths и применимые quality-profile gates.

Результаты Epic Validation:

- `PASSED` → `FUZZING`;
- `PASSED WITH ACCEPTED EXCEPTIONS` → `FUZZING` только после явного принятия точных рисков пользователем;
- `FAILED` → `ACTIVE`, Replan и remediation TASK;
- `BLOCKED` → `ACTIVE` и явное решение по отсутствующей capability или environment.

После passing Epic Validation Epic входит в обязательный fuzzing gate. Для approved `not applicable` оркестратор не вызывает fuzzer, только если все итоговые Task fuzzing impacts равны `none`, actual affected surface совпадает с approved Epic Fuzzing Plan, alternative risk coverage прошёл и fingerprint совпадает с Epic Validation. В этом случае он записывает `NOT APPLICABLE` с freshness evidence. Для `applicable`, `unresolved` или противоречащих итоговых evidence автоматически вызывается read-only fuzzer.

Результаты:

- `PASSED` → ожидание Epic Acceptance;
- `NOT APPLICABLE` → требуются rationale, passing alternative risk coverage и текущий fingerprint; outcome может записать оркестратор по skip-условиям или вернуть вызванный fuzzer;
- `HARNESS REQUIRED` → Replan и отдельная harness TASK;
- `FINDINGS` → Replan и remediation TASK.

После любых изменений повторяются structured review, selected Task testing, полный Epic Validation и fuzzing.

Пользователь отдельно выполняет Epic-level manual validation и даёт Epic Acceptance. Только затем Epic становится `COMPLETED` и перемещается в `execution/completed/`. Следующий queued Epic из `execution/planned/` показывается в Backlog order, но не запускается автоматически.

## 12. Pause и resume

Приостановка active work требует подтверждения пользователя. Соответствующие Epic/TASK получают `PAUSED`, а Epic directory перемещается согласованно с Backlog.

Для продолжения используйте `forge-resume-development`. Возврат к работе также требует явного разрешения; статус не восстанавливается по догадке.

## 13. Security audit

Запускайте `forge-security-audit` только явным запросом с точным scope.

По умолчанию strong security auditor:

- local и read-only;
- без установки инструментов;
- без network;
- без production/external scanning.

Расширение каждого ограничения требует отдельного разрешения. Пользователь решает, какие findings превратить в Bug, TASK или Epic. Отдельный security report не создаётся.

## 13A. Ad hoc investigation

Для свободного исследования вне Backlog явно вызовите `forge-investigate`:

```text
Исследуй, почему алгоритм расчёта работает медленно.
```

Основной агент создаёт `investigations/INV-NNNN-<name>.md`, не вызывает субагентов и сам выбирает подходящие локальные проверки, experiments, benchmarks или profiling. Если запрос содержит «исследуй и исправь», он также разрешает прямое исправление в пределах этой проблемы; иначе код и тесты не меняются до отдельного разрешения.

После исследования выберите исход:

- `no_action` — сохранить выводы и ничего не делать;
- `promoted` — оформить обычный Bug, Epic или Replan через его существующий approval;
- `fixed_directly` — основной агент исправляет и проверяет проблему без TASK workflow;
- `unresolved` — сохранить гипотезы, blocker и следующие эксперименты.

При прямом исправлении INV перечисляет added/modified/removed paths, объясняет изменения, фиксирует verification commands/results, риски и revision/commit либо scoped-diff fingerprint. Commit не выполняется автоматически. При promotion обе стороны получают ссылку `INV-NNNN`; поздний Epic planner проверяет baseline и relevant paths и использует актуальные выводы вместо полного повторного исследования.

## 13B. Standalone mutation testing

Mutation testing не является частью Task/Epic lifecycle и может запускаться в любой момент, включая отсутствие active work:

```text
Проведи mutation testing для src/billing с тестами tests/billing.
```

Skill `forge-mutation-test` требует exact scope, fingerprint, подтверждённые baseline/backend commands и resource budget. Bare-запрос запускает только fast `mutation-runner`: ordinary baseline, затем mutation backend, normalized metrics и запись `quality/mutation-testing/runs/MUT-NNNN.yaml`. Он не устанавливает backend; отсутствие настройки даёт сохранённый `SETUP REQUIRED`.

Для немедленного strong analysis укажите его явно:

```text
Проведи mutation testing для src/billing и проанализируй выжившие мутанты, максимум 20 candidates.
```

Даже после разрешения `mutation-analyzer` пропускается, если candidates нет, baseline упал, setup отсутствует, artifacts stale или budget равен нулю. Если candidates больше budget, record получает `analysis.status: partial` и remaining count.

Можно сначала получить дешёвые metrics, а позже проанализировать тот же результат без повторного campaign:

```text
Проанализируй mutation run MUT-0007, максимум 20 candidates.
```

Deferred analysis требует current fingerprint и artifact checksum. Mutation run никогда не меняет Backlog, Epic/TASK status, gates или development evidence и ничего не создаёт автоматически. Если пользователь решит улучшить тесты или исправить вероятный product defect, он отдельно запускает существующий feature/bug/Replan workflow; `MUT-*` хранит только informational disposition references.

## 14. Adapter sync

Используйте `forge-sync-adapters` после изменения:

- neutral agents или skills;
- model mappings;
- `.ai/custom/router-shared.md`;
- framework release.

Skill показывает collision diff, затем атомарно пересоздаёт Codex, Claude и enabled OpenCode adapters, проверяет полный shared `AGENTS.md`, точный импорт `@AGENTS.md` в `CLAUDE.md`, OpenCode agents в `.opencode/agents/`, shared skill discovery из `.agents/skills/`, parity и обновляет `.ai/framework.lock`. Он не создаёт `opencode.json` или `.opencode/skills/` и сохраняет project-owned OpenCode commands, plugins и unlisted agents.

Project-owned `.ai/integrations/` не является render input и не попадает в managed-output hashes. Изменение board scope или другого локального definition не требует adapter sync само по себе.

## 14A. Framework upgrade с локальными интеграциями

`forge-migrate-framework` offline классифицирует integration files как absent/current/older-migratable/malformed/future/custom/collision. Отсутствие — обычный clean path. Framework bundle обновляется отдельно и сохраняет integrations byte-for-byte; unavailable connector не блокирует upgrade.

Older-migratable schema изменяется только отдельным diff и approval с recoverable backup, staged validation и rollback. Malformed/future/custom profile блокирует только свой consumer. Ownership collision блокирует migration до решения. Rollback framework не удаляет external identities или canonical work links.

## 15. Git policy

`.ai/project.yaml` поддерживает:

- `role_execution.mode` — один из `claude_with_codex`, `codex_with_claude`, `native_subagents` для обеих read-only ролей;
- `platforms.opencode.enabled` и, когда он `true`, три явных OpenCode model ID формата `provider/model-id`; provider и credentials Forge не настраивает;
- `manual` — после Task Acceptance и перехода TASK в `DONE` оркестратор предлагает commit, но ждёт отдельного явного разрешения;
- `auto_commit_after_acceptance` — commit разрешён только после clean review, testing, Task Acceptance и перехода TASK в `DONE`.

До явного Task Acceptance commit запрещён. Commit не заменяет acceptance. В commit нельзя включать посторонние пользовательские изменения.

## 16. Проверка фреймворка

`forge-check-framework` выполняет read-only проверку:

- ownership и hashes;
- IDs, frontmatter, links и transitions;
- Backlog/execution alignment;
- adapter parity и лимит routers;
- восстановимость текущего gate без истории сессии.

Исправления выполняются отдельным подходящим skill и через необходимые user gates.
