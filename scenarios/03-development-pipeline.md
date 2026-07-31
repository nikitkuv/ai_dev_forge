## Сценарий 3. Полный pipeline разработки

### Исходное состояние

Bootstrap завершён. `EPIC-001` активен:

```text
TASK-001 — DONE
TASK-002 — TODO
TASK-003 — TODO
```

Пользователь открывает новую сессию Codex CLI или Claude Code CLI.

### Шаг 1. Resume и сбор контекста

> **Пользователь:** Продолжи разработку с места остановки.

**Внутреннее действие**

1. Оркестратор читает root router (`AGENTS.md` или `CLAUDE.md`).
2. Явно выбирает `forge-resume-development`.
3. Вызывает `context-collector` с tier `fast` для локального read-only inventory.
4. Сам проверяет итоговый evidence, canonical contradictions и Git diff.

Context collector сообщает:

- active/paused Epic;
- TASK statuses и blockers;
- текущий gate;
- implementation/review/test/fuzz fingerprints;
- незакоммиченные изменения;
- следующий допустимый переход.

> **Оркестратор:** Восстановлено состояние:
>
> - `EPIC-001` — `ACTIVE`;
> - `TASK-001` — `DONE`;
> - `TASK-002` — `TODO`, dependencies satisfied;
> - `TASK-003` ждёт TASK-002;
> - code-writing TASK сейчас нет;
> - текущий gate — отдельный Task Start для TASK-002.
>
> Цель TASK-002: реализовать SQLite repository и migration пустой базы. Запустить TASK-002?

### Шаг 2. Task Start

До подтверждения оркестратор показывает:

- goal;
- scope и out of scope;
- acceptance criteria;
- constraints;
- required tests;
- manual verification.

> **Пользователь:** Да, запускай TASK-002.

**Внутреннее действие**

- Проверяются `definition_status: approved`, `status: TODO`, dependencies и blockers.
- Только оркестратор меняет `TODO → IN PROGRESS`.
- В TASK фиксируется `current_gate` и новая implementation revision.
- Оркестратор выбирает `forge-run-task`.

### Шаг 3. Implementer

Оркестратор вызывает `implementer` с tier `balanced` и передаёт только одну TASK.

Implementer читает:

- TASK-002;
- Epic plan;
- связанные `FR-*`, `NFR-*`, `BR-*`;
- архитектуру и ADR;
- релевантный код и тесты;
- repository instructions.

Implementer:

- пишет production-код;
- пишет необходимые тесты;
- использует TDD по умолчанию для bug fixes и meaningful business logic;
- не изменяет canonical status;
- не вызывает reviewer или tester;
- не рефакторит unrelated code.

Он возвращает оркестратору компактный результат:

```text
TASK: TASK-002
Files changed: repository implementation, migration, tests
Tests added: repository contract, empty database migration
Focused checks: passed
Fingerprint candidate: конкретный воспроизводимый Git tree или scoped diff hash
```

**Внутреннее действие**

Оркестратор записывает в тот же TASK-файл:

- Implementation Summary;
- revision;
- current fingerprint;
- список изменённых файлов и тестов.

Отдельный implementation report не создаётся.

### Шаг 4. Independent review

Оркестратор переводит TASK `IN PROGRESS → IN REVIEW` и вызывает `reviewer` с tier `strong`.

Reviewer:

- работает read-only;
- проверяет только TASK-002 и заявленный fingerprint;
- сверяет code, tests, architecture, ADR и acceptance criteria;
- не исправляет код;
- возвращает findings только оркестратору.

#### Ветка A: review нашёл проблему

> **Оркестратор:** Reviewer нашёл нарушение: migration не обрабатывает повторный запуск. TASK возвращается в `IN PROGRESS`; review evidence текущей revision инвалидирован. Implementer получает точный finding.

Цикл повторяется:

```text
implementer fixes
→ revision + 1
→ new fingerprint
→ reviewer checks the new revision
```

Нельзя считать прежний review действительным после любого изменения кода.

#### Ветка B: review чистый

Оркестратор записывает Review Summary в TASK и переводит её `IN REVIEW → IN TESTING`.

### Шаг 5. Tester

Оркестратор вызывает `tester` с tier `fast` для exact reviewed revision.

Tester не пишет тесты и не исправляет код. Он запускает по порядку:

1. новые и изменённые TASK tests;
2. affected-component tests;
3. полный project test suite;
4. configured lint;
5. configured typecheck;
6. configured build.

#### Ветка A: тесты упали

> **Оркестратор:** Полный suite обнаружил regression в import старого JSON. TASK возвращается в `IN PROGRESS`. Результаты testing и review инвалидированы. Finding передан implementer.

После исправления обязательны:

```text
new implementation revision
→ повторный strong review
→ targeted tests
→ affected tests
→ full suite
→ configured checks
```

Tester не передаёт ошибку implementer напрямую: всем циклом управляет оркестратор.

#### Ветка B: всё зелёное

Оркестратор записывает Test Summary и переводит TASK:

```text
IN TESTING → AWAITING USER ACCEPTANCE
```

Если полный suite объективно невозможно запустить, оркестратор объясняет точную причину и риск. Исключение допустимо только после явного принятия риска пользователем.

### Шаг 6. Ручная проверка пользователя

> **Оркестратор:** TASK-002 прошла independent review и required testing. Для ручной проверки:
>
> 1. запустите TaskFlow с пустой базой;
> 2. создайте задачу;
> 3. перезапустите приложение;
> 4. убедитесь, что задача сохранилась;
> 5. повторно запустите migration и убедитесь, что данные не дублируются.
>
> TASK остаётся `AWAITING USER ACCEPTANCE`. Сообщите результат проверки.

Пока пользователь тестирует, таймаута нет. TASK не становится `DONE` автоматически.

### Шаг 7. Что происходит, если пользователь нашёл проблему

#### Случай 1. Ошибка относится к acceptance criteria текущей TASK

> **Пользователь:** После второго запуска migration создаётся дубликат. Исправь.

**Внутреннее действие**

- Новый `BUG-*` не создаётся.
- Feedback записывается в User Validation и Iteration History того же TASK-файла.
- TASK возвращается `AWAITING USER ACCEPTANCE → IN PROGRESS`.
- Старые review/test fingerprints инвалидируются.
- Повторяется implementer → reviewer → tester → manual validation.

#### Случай 2. Пользователь просит новый scope внутри текущего Epic

> **Пользователь:** Заодно добавь шифрование локальной базы.

> **Оркестратор:** Шифрование не входит в approved scope TASK-002 и требует архитектурного решения. Я не добавлю его молча. Можно:
>
> 1. оформить новый Epic;
> 2. выполнить Replan активного Epic и добавить отдельную TASK после ADR;
> 3. оставить идею запланированной.

Изменение plan/TASK composition требует:

1. причины;
2. точного diff;
3. явного Replan approval;
4. отдельного Task Start новой TASK.

#### Случай 3. Найден дефект в ранее принятом коде

> **Пользователь:** Пока тестировал, заметил, что старая функция экспорта ломает кириллицу.

> **Оркестратор:** Это не scope TASK-002 и относится к ранее принятому коду. Зафиксировать новый `BUG-*` в Defect Queue?

Только после подтверждения создаётся `BUG-NNN` со status `OPEN`. Пользователь задаёт priority и выбирает дальнейшее планирование.

### Шаг 8. Task Acceptance

Когда ручная проверка успешна:

> **Пользователь:** TASK-002 проверил, всё работает. Принимаю TASK.

Оркестратор выбирает `forge-complete-task` и повторно проверяет:

- status `AWAITING USER ACCEPTANCE`;
- совпадение implementation/review/test revision и fingerprint;
- наличие manual verification;
- принятие возможных test exceptions.

**Внутреннее действие**

1. User Acceptance записывается в тот же TASK.
2. TASK переходит `AWAITING USER ACCEPTANCE → DONE`.
3. Связанный `SCHEDULED` Bug при необходимости становится `RESOLVED`.
4. При `git.policy: manual` оркестратор показывает exact scoped files и proposed commit.

> **Оркестратор:** TASK-002 принята и переведена в `DONE`. Предлагаемый commit включает только scoped changes TASK-002. Выполнить commit?

Commit требует отдельного разрешения при manual policy.

### Шаг 9. Следующая TASK — отдельный gate

После Task Acceptance оркестратор может показать следующую TASK, но не запускать её.

> **Оркестратор:** Следующая eligible TASK — TASK-003. Её goal и acceptance criteria: ... Запустить TASK-003?

Сообщение «принимаю TASK-002» не запускает TASK-003. Одно пользовательское сообщение может принять предыдущую и запустить следующую TASK только если явно содержит оба решения.

### Шаг 10. Завершение последней TASK и Epic fuzzing

После принятия последней TASK оркестратор автоматически выбирает `forge-complete-epic`.

**Внутреннее действие**

1. Проверяет, что все TASK `DONE` и evidence актуален.
2. Переводит Epic `ACTIVE → FUZZING`.
3. Автоматически вызывает read-only `fuzzer` с tier `balanced` для существующих harnesses.
4. Записывает Fuzzing Summary в `plan.md`.
5. Не создаёт `fuzzing-report.md`.

Возможны четыре outcome.

#### `PASSED`

```text
FUZZING → AWAITING EPIC ACCEPTANCE
```

#### `NOT APPLICABLE`

Разрешён только с двумя записями в plan:

- почему подходящего fuzz target нет;
- какое alternative risk coverage выполнено.

После этого Epic может перейти в `AWAITING EPIC ACCEPTANCE`.

#### `HARNESS REQUIRED`

```text
FUZZING → ACTIVE
→ Replan diff для новой harness TASK
→ Replan approval
→ отдельный Task Start
→ полный TASK lifecycle
→ повторный FUZZING
```

Fuzzer сам не пишет harness.

#### `FINDINGS`

```text
FUZZING → ACTIVE
→ reproduction evidence в plan
→ Replan remediation TASK
→ Task Start
→ implementer/reviewer/tester/user acceptance
→ повторный FUZZING
```

### Шаг 11. Epic Acceptance

После допустимого fuzzing outcome пользователь проводит Epic-level validation.

> **Оркестратор:** Все TASK приняты, full testing актуален, fuzzing outcome — `PASSED`. Epic acceptance criteria выполнены. Проверьте сквозной сценарий создания, сохранения и завершения задачи. После проверки явно подтвердите Epic Acceptance.

#### Пользователь нашёл проблему

Epic возвращается в `ACTIVE`. Оркестратор предлагает Replan diff и новую TASK. После её полного lifecycle fuzzing повторяется.

#### Пользователь принимает Epic

> **Пользователь:** Epic проверил. Принимаю EPIC-001.

**Внутреннее действие**

1. `BACKLOG.md`: `AWAITING EPIC ACCEPTANCE → COMPLETED`.
2. Acceptance записывается в `plan.md`.
3. Каталог атомарно перемещается:

```text
execution/active/EPIC-001-core/
→ execution/completed/EPIC-001-core/
```

4. Следующий Epic не активируется автоматически.

> **Оркестратор:** EPIC-001 завершён. Следующий planned candidate — EPIC-002. Подготовить его plan или пока остановиться?

---

## Дополнительные рабочие ветки

### Новая feature во время разработки

> **Пользователь:** Добавь идею совместных списков задач.

Оркестратор использует `forge-intake-feature`:

1. уточняет target behavior;
2. после подтверждения создаёт `PLANNED/OUTLINE` Epic;
3. показывает SPEC diff;
4. при необходимости показывает ARCHITECTURE/ADR diff;
5. не меняет active TASK;
6. переводит Epic в `READY` только после утверждения requirements и dependencies.

Все будущие идеи сохраняются как Epic, а не как отдельный список «когда-нибудь».

### Новый баг вне manual validation текущей TASK

> **Пользователь:** Зафиксируй баг: завершённые задачи исчезают после обновления приложения.

Оркестратор использует `forge-intake-bug`:

1. уточняет expected/actual behavior и reproduction;
2. определяет, относится ли дефект к непринятой TASK;
3. после подтверждения создаёт `BUG-*` только для принятого кода;
4. пользователь задаёт severity, priority и способ планирования;
5. Bug остаётся `OPEN`, становится `SCHEDULED` через TASK и `RESOLVED` после принятого исправления.

### Reprioritization

> **Пользователь:** Перемести EPIC-004 выше EPIC-003.

Оркестратор использует `forge-reprioritize-backlog`, строит dependency graph и сообщает, если поздний Epic блокирует ранний.

> **Оркестратор:** EPIC-004 зависит от data model из EPIC-003. Если переместить EPIC-004 выше, он останется `PLANNED` и `Blocked by EPIC-003`. Изменить порядок несмотря на блокировку?

Порядок меняется только после ответа пользователя.

### Pause и resume

При pause:

1. требуется подтверждение пользователя;
2. Epic/TASK получают `PAUSED`;
3. каталог Epic перемещается в `execution/paused/` согласованно с Backlog;
4. текущий gate сохраняется в файлах.

При resume оркестратор не угадывает прежний status, а использует `forge-resume-development` и просит явное разрешение на возврат к работе.

### Security audit

Security audit нигде не вызывается автоматически.

> **Пользователь:** Проведи security audit storage и import boundaries.

Оркестратор использует `forge-security-audit` и strong `security-auditor`.

По умолчанию audit:

- local;
- read-only;
- без network;
- без установки инструментов;
- без production/external scanning.

Расширение scope требует отдельного разрешения. Принятые findings превращаются в существующую TASK, Bug или Epic. Отдельный security report Markdown не создаётся.

---

## Карта основного TASK pipeline

```text
TODO
  │ explicit Task Start
  ▼
IN PROGRESS
  │ implementer + implementation evidence
  ▼
IN REVIEW
  │ strong reviewer
  ├── findings ───────────────► IN PROGRESS
  ▼ clean
IN TESTING
  │ tester: targeted + affected + full suite + configured checks
  ├── failure ────────────────► IN PROGRESS → review again
  ▼ pass
AWAITING USER ACCEPTANCE
  ├── fixes within scope ─────► IN PROGRESS
  ├── new scope ──────────────► Replan gate
  └── explicit acceptance ────► DONE
```

## Кто вызывается и когда

| Роль | Tier | Когда оркестратор вызывает | Может менять код | Может менять canonical status |
| --- | --- | --- | --- | --- |
| Основной оркестратор | strong | основная сессия | делегирует production-код implementer | да |
| `context-collector` | fast | bootstrap existing, resume | нет | нет |
| `documentation-researcher` | fast | когда нужна официальная внешняя документация | нет | нет |
| `implementer` | balanced | после отдельного Task Start | да, только TASK scope | нет |
| `reviewer` | strong | после implementation revision | нет | нет |
| `tester` | fast | после clean review | нет | нет |
| `fuzzer` | balanced | после принятия последней TASK Epic | нет | нет |
| `security-auditor` | strong | только явный запрос пользователя | нет | нет |

Субагенты не вызывают друг друга. Все результаты возвращаются оркестратору.

## Какой файл изменяется на каждом этапе

| Событие | Основной владелец записи |
| --- | --- |
| Изменилось target behavior | `SPEC.md` после user approval |
| Изменилась target architecture | `ARCHITECTURE.md` и при необходимости новый ADR |
| Изменились priority, readiness, Epic status или Bug status | `BACKLOG.md` |
| Принято архитектурное решение | соответствующий ADR; `DECISIONS.md` регенерируется |
| Изменились Epic strategy или TASK order | `plan.md` через Replan |
| Изменились TASK scope, status или evidence | соответствующий TASK-файл |
| Получен Epic fuzzing outcome | `plan.md` |
| Получен Task manual feedback | тот же TASK-файл |
| Получен Epic-level feedback | `plan.md`; remediation через новую TASK |
| Изменились neutral agents, skills или model mappings | adapter sync и `.ai/framework.lock` |

## Gates, которые нельзя объединять по умолчанию

| Gate | Что он разрешает | Что он не разрешает |
| --- | --- | --- |
| SPEC Approval | утвердить target behavior | проектировать или писать код |
| ADR Approval | принять одно архитектурное решение | автоматически утвердить весь ARCHITECTURE |
| Plan Approval | утвердить стратегию и TASK definitions | активировать Epic |
| Epic Start | сделать один Epic `ACTIVE` | запустить первую TASK |
| Task Start | запустить одну конкретную TASK | расширить её scope |
| Replan | изменить approved plan/TASK composition | автоматически запустить новую TASK |
| Task Acceptance | перевести одну TASK в `DONE` | запустить следующую TASK |
| Epic Acceptance | завершить Epic после fuzzing | активировать следующий Epic |
| Commit authorization при `manual` | создать показанный commit | включить unrelated изменения |

## Как восстановить процесс без истории чата

Новая сессия читает данные в следующем порядке:

1. `.ai/project.yaml` и `.ai/framework.lock`;
2. `SPEC.md`;
3. `ARCHITECTURE.md`;
4. `DECISIONS.md` и ADR;
5. `BACKLOG.md`;
6. active или paused Epic `plan.md`;
7. все TASK-файлы этого Epic;
8. Git status и diff;
9. hashes/revision/fingerprint evidence.

Если результат субагента существовал только в старом чате и не был записан в TASK или plan, соответствующий этап считается недоказанным и выполняется снова.

## Короткая памятка пользователю

- Копируйте только `.ai/`, затем дайте bootstrap-промпт.
- Утверждайте каждый numbered bootstrap step отдельно.
- Пользователь владеет priority и окончательными решениями.
- Epic Start, Task Start, Task Acceptance и Epic Acceptance — разные gates.
- Implementer пишет production-код и тесты; tester тесты не пишет.
- Любая правка кода требует нового review и нового полного testing.
- Проблема в непринятой TASK остаётся в этой TASK.
- Проблема в принятом коде получает `BUG-*` только после подтверждения.
- После последней TASK автоматически запускается read-only Epic fuzzing.
- Security audit запускается только вручную.
- История чата полезна, но не является источником истины.
- Следующая TASK и следующий Epic никогда не стартуют автоматически.

Связанные документы:

- [README](README.md) — установка и quick start;
- [FRAMEWORK](FRAMEWORK.md) — архитектура и контракты;
- [RUNBOOK](RUNBOOK.md) — краткие операционные действия;
- [FRAMEWORK_DESIGN](FRAMEWORK_DESIGN.md) — обоснование согласованных решений.

