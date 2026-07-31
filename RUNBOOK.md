# AI Development Forge v3 — Runbook

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

3. Утверждайте отдельно SPEC, архитектуру/ADR, Backlog, Epic plan, Epic Start, adapters и final validation.
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

- active/paused Epic;
- TASK statuses и blockers;
- текущий gate;
- актуальность implementation/review/test/fuzz fingerprints;
- незавершённый Git diff.

История сессии необязательна. Если результат агента не сохранён в TASK или plan, соответствующий этап выполняется повторно.

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

Skill `forge-prepare-epic` требует:

- status `PLANNED`;
- readiness `READY`;
- удовлетворённые dependencies;
- отсутствие blockers и другого active Epic.

Оркестратор показывает plan и все TASK definitions. После отдельного утверждения plan и Epic Start создаются `execution/active/...`, approved plan и TASK-файлы со status `TODO`.

## 8. Запуск и выполнение TASK

Task Start всегда явный. Перед подтверждением покажите goal, scope, acceptance criteria и required tests.

Skill `forge-run-task` запускает цикл:

```text
Task Start
→ implementer
→ strong reviewer
→ tester
→ AWAITING USER ACCEPTANCE
```

Implementer пишет production-код и тесты. Reviewer не исправляет код и возвращает findings оркестратору. Tester не пишет тесты и запускает:

1. новые/изменённые тесты;
2. affected-component tests;
3. полный test suite;
4. configured lint, typecheck и build.

После любого исправления review и testing выполняются заново. Исключение для полного suite возможно только при объективной невозможности запуска и явном принятии риска пользователем.

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

## 11. Завершение Epic и fuzzing

После принятия последней TASK skill `forge-complete-epic` переводит Epic в `FUZZING` и автоматически вызывает read-only fuzzer для существующих harnesses.

Результаты:

- `PASSED` → ожидание Epic Acceptance;
- `NOT APPLICABLE` → требуются rationale и alternative risk coverage;
- `HARNESS REQUIRED` → Replan и отдельная harness TASK;
- `FINDINGS` → Replan и remediation TASK.

После любых изменений повторяются review, полный testing и fuzzing.

Пользователь отдельно выполняет Epic validation и даёт Epic Acceptance. Только затем Epic становится `COMPLETED` и перемещается в `execution/completed/`. Следующий Epic не запускается автоматически.

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
- `.ai/custom/`;
- framework release.

Skill показывает collision diff, затем атомарно пересоздаёт Codex и Claude adapters, проверяет parity и обновляет `.ai/framework.lock`.

## 15. Миграция

1. Скопируйте новую `.ai/` поверх старой.
2. Попросите агента запустить `forge-migrate-framework`.
3. Проверьте migration diff, obsolete files, adapter collisions и canonical schema changes.
4. Подтвердите точный scope.

Skill создаёт временный backup, обновляет framework-owned files и оба adapters, запускает conformance check и обновляет lock только после успеха. При ошибке восстанавливается backup. Canonical documents требуют отдельного diff и подтверждения.

## 16. Git policy

`.ai/project.yaml` поддерживает:

- `manual` — оркестратор предлагает commit, но ждёт явного разрешения;
- `auto_commit_after_acceptance` — commit разрешён только после clean review, testing, Task Acceptance и перехода TASK в `DONE`.

В commit нельзя включать посторонние пользовательские изменения.

## 17. Проверка фреймворка

`forge-check-framework` выполняет read-only проверку:

- ownership и hashes;
- IDs, frontmatter, links и transitions;
- Backlog/execution alignment;
- adapter parity и лимит routers;
- восстановимость текущего gate без истории сессии.

Исправления выполняются отдельным подходящим skill и через необходимые user gates.
