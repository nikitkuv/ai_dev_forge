# AI Development Forge v4.2 — Runbook

## Codex route для Claude Code

На подготовке Epic и независимом review Claude Code выполняет preflight `codex-plugin-cc`. Доступный runtime получает полный нейтральный контракт роли и тот же Epic assignment или Review Packet, запускается fresh/read-only с `gpt-5.6-sol/high`. Недоступный плагин, Node.js, Codex CLI или login означает fallback на одноимённый Claude subagent с теми же входными данными; начатый Codex run при ошибке блокирует этап.

Поддерживается `codex-plugin-cc` версии `1.0.6` и новее. Установка плагина, запуск `/codex:setup` и авторизация — ручные и необязательные действия.

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
Create both Codex and Claude Code adapters.
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
Create both Codex and Claude Code adapters.
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

Task Start всегда явный. Перед подтверждением покажите goal, scope, acceptance criteria, affected surface, risk flags, Verification Plan и review focus.

Skill `forge-run-task` запускает цикл:

```text
Task Start
→ implementer
→ strong reviewer
→ tester
→ AWAITING USER ACCEPTANCE
```

Implementer пишет production-код и focused tests. Reviewer не исправляет код, получает обязательный Review Packet, независимо трассирует acceptance criteria и выполняет ordered adversarial review protocol. Tester не пишет тесты и запускает:

1. новые/изменённые тесты;
2. выбранные affected-component tests;
3. scoped lint, typecheck, build и применимые profile-specific checks.

Полный project test suite и unscoped project-wide checks не являются Task gate и по умолчанию запрещены implementer, reviewer и tester. Ранний полный прогон допустим только по явному запросу пользователя и не заменяет Epic Validation. После любого исправления structured review и selected testing выполняются заново.

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

После passing Epic Validation автоматически вызывается read-only fuzzer для существующих harnesses.

Результаты:

- `PASSED` → ожидание Epic Acceptance;
- `NOT APPLICABLE` → требуются rationale и alternative risk coverage;
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

## 14. Adapter sync

Используйте `forge-sync-adapters` после изменения:

- neutral agents или skills;
- model mappings;
- `.ai/custom/router-shared.md`;
- framework release.

Skill показывает collision diff, затем атомарно пересоздаёт Codex и Claude adapters, проверяет byte-identical root routers, parity остальных adapters и обновляет `.ai/framework.lock`.

Project-owned `.ai/integrations/` не является render input и не попадает в managed-output hashes. Изменение board scope или другого локального definition не требует adapter sync само по себе.

## 14A. Framework upgrade с локальными интеграциями

`forge-migrate-framework` offline классифицирует integration files как absent/current/older-migratable/malformed/future/custom/collision. Отсутствие — обычный clean path. Framework bundle обновляется отдельно и сохраняет integrations byte-for-byte; unavailable connector не блокирует upgrade.

Older-migratable schema изменяется только отдельным diff и approval с recoverable backup, staged validation и rollback. Malformed/future/custom profile блокирует только свой consumer. Ownership collision блокирует migration до решения. Rollback framework не удаляет external identities или canonical work links.

## 15. Git policy

`.ai/project.yaml` поддерживает:

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
