## Сценарий 3. Полный pipeline разработки

> На стадиях Epic planning и review оркестратор следует неизменному `role_execution.mode`: Claude→Codex, Codex→Claude или native subagents. OpenCode использует существующий `native_subagents` как default proposal при первичной настройке. Несовпадение платформы и недоступный выбранный runtime блокируют стадию; fallback отсутствует.

### Исходное состояние

Bootstrap завершён. `EPIC-001` активен:

```text
TASK-001 — DONE
TASK-002 — TODO
TASK-003 — TODO
```

Пользователь открывает новую сессию Codex CLI, Claude Code CLI или OpenCode.

### Шаг 1. Resume и сбор контекста

> **Пользователь:** Продолжи разработку с места остановки.

**Внутреннее действие**

1. Оркестратор читает root router (`AGENTS.md` или `CLAUDE.md`).
2. Явно выбирает `forge-resume-development`.
3. Вызывает `context-collector` с tier `fast` для локального read-only inventory.
4. Сам проверяет итоговый evidence, canonical contradictions и Git diff.

Context collector сообщает:

- ordered planned queue с Epic Start eligibility, затем active/paused Epic;
- TASK statuses и blockers;
- текущий gate;
- implementation/review/selected-test/Epic-Validation/fuzz fingerprints;
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
- constraints, affected surface и risk flags;
- Verification Plan и review focus;
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
- affected surface, risk flags, review focus и selected checks;
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

### Шаг 3A. Выбор delivery track

Delivery track выбирается в approved plan до Task Start и независимо от model tier и `risk level`. Для `fast` оркестратор должен доказать, что изменение ограничено, обратимо, однозначно и имеет детерминированную локальную проверку. Публичный контракт, auth/security/privacy, persistence/data format/schema/migration, concurrency/shared core, dependency/build/package/deploy/runtime infrastructure, внешняя интеграция, critical path, ослабление тестов или неопределённость означают `standard`.

TASK-002 меняет migration и поэтому идёт по `standard`. Простая локальная TASK, которая прошла все fast eligibility checks, после implementer получила бы другой маршрут:

```text
IN PROGRESS
→ orchestrator assurance: fingerprint + bounded diff + test integrity + approved focused checks
→ AWAITING USER ACCEPTANCE
```

Reviewer и tester на fast track не вызываются. Любой провал, расширение surface или сомнение повышает TASK `fast → standard`; после Task Start переход `standard → fast` запрещён. Legacy TASK без поля track считается `standard`. Это не отменяет TDD, Task Acceptance, последующую Epic Validation или fuzzing.

Примеры маршрутизации:

| Изменение | Track | Причина |
| --- | --- | --- |
| Исправить опечатку или локальную документацию с проверяемой ссылкой | `fast` | bounded, reversible, deterministic verification |
| Исправить малую внутреннюю ветку логики с независимым focused test | `fast`, если доказаны все критерии | низкий риск сам по себе недостаточен |
| Изменить public API contract | `standard` | public-contract disqualifier |
| Изменить schema или migration | `standard` | data/migration disqualifier |
| Fast check упал или обнаружен неожиданный affected surface | `fast → standard` | fail-closed escalation |

### Шаг 4. Independent review (`standard`)

Оркестратор переводит TASK `IN PROGRESS → IN REVIEW`. Он вызывает `reviewer` с tier `strong`, только если нет текущего `CLEAN` review для того же production fingerprint; supporting-only revision переиспользует clean review без нового вызова.

Reviewer:

- работает read-only;
- получает exact Review Packet с whole-implementation и production-surface fingerprints, `production_review_paths`, `supporting_evidence_paths`, scoped diffs, acceptance criteria, affected surfaces, risks, implementation и test evidence;
- независимо трассирует каждый acceptance criterion, читает production paths с callers/callees и проверяет adversarial cases, architecture, contracts, data и security; test quality использует как supporting evidence;
- не исправляет код;
- возвращает outcome-affecting production findings и отдельные advisory non-production observations только оркестратору.

#### Ветка A: review нашёл проблему

> **Оркестратор:** Reviewer нашёл нарушение: migration не обрабатывает повторный запуск. TASK возвращается в `IN PROGRESS`; review evidence текущей revision инвалидирован. Implementer получает точный finding.

Цикл повторяется:

```text
implementer fixes
→ revision + 1
→ new whole-implementation and production fingerprints
→ reviewer checks the new production revision
```

Прежний review недействителен после изменения production fingerprint. Test-only и другое supporting-only исправление сохраняет `CLEAN` и не вызывает reviewer повторно.

#### Ветка B: review чистый

Оркестратор записывает Review Summary в TASK и переводит её `IN REVIEW → IN TESTING`.

### Шаг 5. Tester (`standard`)

Оркестратор вызывает `tester` с tier `fast` для текущей implementation revision. Её whole-implementation fingerprint должен быть текущим, а production fingerprint — совпадать с новым или переиспользованным clean review.

Tester не пишет тесты и не исправляет код. Он запускает по порядку:

1. новые и изменённые TASK tests;
2. выбранные affected-component tests;
3. bounded `Task fuzz smoke` для affected target или completed harness; для impact `none` проверяет rationale против actual surface;
4. scoped lint, typecheck, build и применимые profile-specific checks.

#### Ветка A: тесты упали

> **Оркестратор:** Выбранные repository-component checks обнаружили regression в import старого JSON. TASK возвращается в `IN PROGRESS`, finding передан implementer. Testing evidence инвалидирован; review инвалидируется только если исправление меняет production fingerprint.

После исправления обязательны:

```text
new implementation revision and fingerprints
→ production changed: повторный strong review → targeted tests
→ supporting-only: preserved CLEAN → targeted tests без reviewer
→ affected tests
→ scoped configured checks
```

Tester не передаёт ошибку implementer напрямую: всем циклом управляет оркестратор.

#### Ветка B: всё зелёное

Оркестратор записывает Test Summary и переводит TASK:

```text
IN TESTING → AWAITING USER ACCEPTANCE
```

Полный project test suite и unscoped global checks не запускаются в обычном TASK pipeline. Они остаются обязательными в Epic Validation. Ранний полный прогон требует явного запроса пользователя и не заменяет этот gate.

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

### Шаг 10. Завершение последней TASK, Epic Validation и fuzzing

После принятия последней TASK оркестратор автоматически выбирает `forge-complete-epic`.

**Внутреннее действие**

1. Проверяет, что все TASK `DONE` и evidence актуален.
2. Устанавливает exact aggregate fingerprint и переводит Epic `ACTIVE → VALIDATING`.
3. Автоматически вызывает `epic-validator` с tier `balanced` для full suite, project-wide checks, critical paths и выбранных quality profiles.
4. Записывает Epic Validation Summary в `plan.md`.
5. Только после passing outcome переводит Epic `VALIDATING → FUZZING` и сверяет approved Epic Fuzzing Plan с итоговыми Task impacts, actual affected surface, alternative coverage и fingerprint.
6. Для текущего approved `not applicable` записывает `NOT APPLICABLE` без вызова subagent; для `applicable`, `unresolved` или противоречащих evidence вызывает read-only `fuzzer`.
7. Записывает Fuzzing Summary в `plan.md` и не создаёт отдельных validation/fuzzing report-файлов.

Epic Validation outcomes: `PASSED`, `PASSED WITH ACCEPTED EXCEPTIONS`, `FAILED` и `BLOCKED`. Failures или blockers возвращают Epic в `ACTIVE`; remediation требует Replan и нового TASK lifecycle. Любое implementation change требует повторной Epic Validation перед fuzzing.

Возможны четыре outcome.

#### `PASSED`

```text
FUZZING → AWAITING EPIC ACCEPTANCE
```

#### `NOT APPLICABLE`

Разрешён только с текущими evidence в plan:

- почему подходящего fuzz target нет;
- какое alternative risk coverage выполнено.
- почему все итоговые Task fuzzing impacts и actual affected surface всё ещё соответствуют approved plan;
- какой aggregate fingerprint совпадает с passing Epic Validation.

Если эти условия выполнены для approved `not applicable`, оркестратор не вызывает fuzzer. При любом расхождении вызывает его.

После этого Epic может перейти в `AWAITING EPIC ACCEPTANCE`.

#### `HARNESS REQUIRED`

```text
FUZZING → ACTIVE
→ Replan diff для новой harness TASK
→ Replan approval
→ отдельный Task Start
→ полный TASK lifecycle
→ повторная Epic Validation
→ повторный FUZZING
```

Fuzzer сам не пишет harness.

#### `FINDINGS`

```text
FUZZING → ACTIVE
→ reproduction evidence в plan
→ Replan remediation TASK
→ Task Start
→ assurance выбранного delivery track/user acceptance
→ повторная Epic Validation
→ повторный FUZZING
```

### Шаг 11. Epic Acceptance

После допустимого fuzzing outcome пользователь проводит Epic-level manual validation.

> **Оркестратор:** Все TASK приняты, Epic Validation прошла на текущем fingerprint, selected quality-profile gates выполнены, fuzzing outcome — `PASSED`. Epic acceptance criteria выполнены. Проверьте сквозной сценарий создания, сохранения и завершения задачи. После проверки явно подтвердите Epic Acceptance.

#### Пользователь нашёл проблему

Epic возвращается в `ACTIVE`. Оркестратор предлагает Replan diff и новую TASK. После её полного lifecycle Epic Validation и fuzzing повторяются.

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

> **Оркестратор:** EPIC-001 завершён. Следующий queued planned workspace по Backlog order — EPIC-002; он eligible для Epic Start. Активировать его или пока остановиться?

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
  ├── fast → orchestrator assurance ────────────────┐
  │          failure/uncertainty → standard         │
  └── standard → IN REVIEW → IN TESTING ───────────┤
               reviewer       tester               │
               failure ───────────────► IN PROGRESS│
                                                   ▼
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
| `epic-planner` | strong | при подготовке Epic | нет | нет |
| `implementer` | balanced | после отдельного Task Start | да, только TASK scope | нет |
| `reviewer` | strong | после implementation revision | нет | нет |
| `tester` | fast | после clean review | нет | нет |
| `epic-validator` | balanced | после `DONE` всех planned TASK | нет | нет |
| `fuzzer` | balanced | после passing Epic Validation для `applicable`, `unresolved` или противоречащих evidence | нет | нет |
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
| Получен Epic Validation outcome | `plan.md` |
| Получен Epic fuzzing outcome | `plan.md` |
| Получен Task manual feedback | тот же TASK-файл |
| Получен Epic-level feedback | `plan.md`; remediation через новую TASK |
| Изменились neutral agents, skills или model mappings | adapter sync и `.ai/framework.lock` |

## Gates, которые нельзя объединять по умолчанию

| Gate | Что он разрешает | Что он не разрешает |
| --- | --- | --- |
| SPEC Approval | утвердить target behavior | проектировать или писать код |
| ADR Approval | принять одно архитектурное решение | автоматически утвердить весь ARCHITECTURE |
| Plan Approval | создать или обновить approved `execution/planned/` workspace | активировать Epic |
| Epic Start | атомарно переместить один eligible workspace `planned → active` и сделать Epic `ACTIVE` | запустить первую TASK |
| Task Start | запустить одну конкретную TASK | расширить её scope |
| Replan | изменить approved plan/TASK composition | автоматически запустить новую TASK |
| Task Acceptance | перевести одну TASK в `DONE` | запустить следующую TASK |
| Epic Acceptance | завершить Epic после Epic Validation и fuzzing | активировать следующий Epic |
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
9. hashes/revision/fingerprint, Review Packet, Epic Validation и fuzzing evidence.

Если результат субагента существовал только в старом чате и не был записан в TASK или plan, соответствующий этап считается недоказанным и выполняется снова.

## Короткая памятка пользователю

- Копируйте только `.ai/`, затем дайте bootstrap-промпт.
- Утверждайте каждый numbered bootstrap step отдельно.
- Пользователь владеет priority и окончательными решениями.
- Epic Start, Task Start, Task Acceptance и Epic Acceptance — разные gates.
- Implementer пишет production-код и тесты; tester тесты не пишет.
- Любая Task-правка кода инвалидирует assurance выбранного delivery track: fast повторяет orchestrator assurance либо повышается до standard, а standard повторяет нужные review/testing gates; aggregate changes также инвалидируют Epic Validation и fuzzing.
- Проблема в непринятой TASK остаётся в этой TASK.
- Проблема в принятом коде получает `BUG-*` только после подтверждения.
- После последней TASK автоматически запускается полный Epic Validation; затем обязательный fuzzing gate либо подтверждает текущий `NOT APPLICABLE` без subagent, либо вызывает read-only fuzzer для `applicable`, `unresolved` или противоречащих evidence.
- Security audit запускается только вручную.
- История чата полезна, но не является источником истины.
- Следующая TASK и следующий Epic никогда не стартуют автоматически.

Связанные документы:

- [README](README.md) — установка и quick start;
- [FRAMEWORK](FRAMEWORK.md) — архитектура и контракты;
- [RUNBOOK](RUNBOOK.md) — краткие операционные действия;
