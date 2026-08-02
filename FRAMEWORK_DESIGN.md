---
document_type: framework_design
status: approved
language: ru
approved_sections: 7
written_at: 2026-07-30
reviewed_at: 2026-07-30
---

# AI Development Forge v3 — согласованный дизайн фреймворка

## 1. Назначение

AI Development Forge — репозиторный фреймворк совместной разработки с AI-кодовыми агентами. Основные целевые платформы:

- OpenAI Codex CLI;
- Anthropic Claude Code CLI.

Фреймворк должен обеспечивать:

- единый процесс product discovery, system design, planning и implementation;
- канонические документы с однозначным владельцем каждого факта;
- оркестрацию специализированных субагентов;
- восстановление работы без зависимости от истории сессии;
- обязательную пользовательскую приёмку каждой TASK и каждого Epic;
- одновременную генерацию нативных адаптеров Codex и Claude;
- безопасную установку без обязательного CLI-инструмента.

## 2. Основные принципы

1. **Один источник истины для каждого факта.** Не один универсальный файл, а один владелец каждого вида данных.
2. **Документация раньше реализации.** Утверждённые требования и архитектура предшествуют коду.
3. **Пользователь управляет продуктом.** Пользователь принимает требования, ADR, приоритеты, TASK и Epic.
4. **Orchestrator управляет процессом.** Субагенты не управляют друг другом и не меняют канонические статусы.
5. **Состояние хранится в репозитории.** История Codex или Claude является только дополнительным контекстом.
6. **Одна пишущая TASK.** В первой версии код изменяется последовательно одной implementation TASK.
7. **Нативные адаптеры, нейтральный источник.** Codex- и Claude-файлы генерируются из общих определений.
8. **Минимум документов.** Для review, testing, fuzzing и ручной приёмки не создаются отдельные Markdown-отчёты.
9. **Никаких скрытых переходов.** Изменение приоритета, scope, ADR, начало TASK и приёмка требуют явного решения пользователя.
10. **Без внешнего lifecycle layer.** Core framework самостоятельно определяет discovery, investigation, implementation, verification и gates; hooks и MCP не являются условиями его работы.

## 3. Структура репозитория

Следующая структура описывает **целевой проект-потребитель после bootstrap**, а не репозиторий исходного кода AI Development Forge. Сам framework repository хранит `.ai/`, templates, neutral definitions и framework documentation, но не инициализируется собственным bootstrap.

```text
project/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── SPEC.md
├── ARCHITECTURE.md
├── BACKLOG.md
├── DECISIONS.md
│
├── decisions/
│   └── ADR-NNN-<name>.md
│
├── execution/
│   ├── active/
│   │   └── EPIC-NNN-<name>/
│   │       ├── plan.md
│   │       └── tasks/
│   │           └── TASK-NNN-<name>.md
│   ├── paused/
│   └── completed/
│
├── .ai/
│   ├── BOOTSTRAP.md
│   ├── CONVENTIONS.md
│   ├── 01-product-discovery.md
│   ├── 02-system-design.md
│   ├── 03-release-planning.md
│   ├── 04-prepare-workspace.md
│   ├── 05-create-platform-adapters.md
│   ├── 06-final-validation.md
│   ├── project.yaml
│   ├── framework.lock
│   ├── custom/
│   ├── framework/
│   └── templates/
│
├── .codex/
├── .claude/
└── .agents/
```

### 3.1 Роль `.ai/`

`.ai/` содержит bootstrap, нейтральные определения, шаблоны и метаданные установленной версии. Канонические документы проекта не размещаются внутри `.ai/`.

### 3.2 Markdown-файлы состояния

Канонический и execution-слой ограничен следующими типами Markdown-файлов:

- `SPEC.md`;
- `ARCHITECTURE.md`;
- `BACKLOG.md`;
- `DECISIONS.md`;
- `ADR-NNN-<name>.md`;
- `plan.md`;
- `TASK-NNN-<name>.md`.

Отдельные `reports/`, progress, checkpoint, user-validation, security, research и fuzzing Markdown-файлы не создаются.

`README.md`, `AGENTS.md`, `CLAUDE.md`, platform agents и `SKILL.md` являются пользовательской или платформенной инфраструктурой, а не источниками execution-состояния.

## 4. Владение информацией

| Информация | Единственный владелец |
|---|---|
| Целевое поведение продукта | `SPEC.md` |
| Целевая архитектура | `ARCHITECTURE.md` |
| Epic, их приоритет, readiness и lifecycle status | `BACKLOG.md` |
| Дефекты и их lifecycle status | `BACKLOG.md` |
| Значимое архитектурное решение | Соответствующий ADR |
| Навигация по ADR | Генерируемый `DECISIONS.md` |
| Стратегия Epic и порядок TASK | `plan.md` |
| TASK scope, acceptance criteria и lifecycle status | Соответствующий TASK-файл |
| Implementation/review/testing/user-validation summary | Соответствующий TASK-файл |
| Epic fuzzing и Epic user-validation summary | `plan.md` |
| История изменения файлов | Git |

Каталоги `execution/active`, `execution/paused` и `execution/completed` являются структурным представлением Epic status из BACKLOG. Orchestrator обновляет BACKLOG и перемещает каталог согласованно. Несоответствие считается ошибкой состояния.

## 5. Язык и технические идентификаторы

Framework control layer всегда написан на английском:

- `.ai/BOOTSTRAP.md` и numbered bootstrap steps;
- `AGENTS.md` и `CLAUDE.md`;
- platform agent definitions;
- skills;
- нейтральные workflow и machine schemas;
- инструкции hooks и MCP, если проект добавит их позднее.

Канонические документы создаются на языке общения пользователя:

- README;
- SPEC;
- ARCHITECTURE;
- BACKLOG;
- DECISIONS и ADR;
- plan и TASK.

Технические ID, status values, пути и команды остаются английскими.

## 6. Идентификаторы

Все идентификаторы глобально уникальны внутри проекта:

```text
EPIC-001, EPIC-002, ...
TASK-001, TASK-002, ...
BUG-001, BUG-002, ...
ADR-001, ADR-002, ...
```

Нумерация TASK не начинается заново внутри Epic. Следующий ID определяется как максимальный существующий ID данного типа плюс один. Удалённые, отменённые и пропущенные номера не переиспользуются.

## 7. Машиночитаемое состояние документов

SPEC, ARCHITECTURE, BACKLOG и plan используют отдельное поле `document_status`, чтобы статус утверждения документа не смешивался с lifecycle:

```yaml
---
document_type: spec
document_status: draft
language: ru
created_at: 2026-07-30
approved_at:
---
```

После явного подтверждения пользователя:

```yaml
document_status: approved
approved_at: 2026-07-30
```

TASK использует два разных поля:

```yaml
definition_status: approved
status: TODO
```

`definition_status` показывает, утверждены ли scope и acceptance criteria, а `status` является единственным lifecycle status задачи.

ADR использует собственный decision lifecycle `PROPOSED | ACCEPTED | REJECTED | SUPERSEDED | DEPRECATED`; отдельный `document_status` ему не нужен.

Frontmatter позволяет восстановить незавершённый bootstrap без отдельного state-файла. Git хранит историю версий, поэтому дополнительные version documents не создаются.

## 8. Канонические документы

### 8.1 SPEC

SPEC описывает утверждённое целевое состояние продукта, а не только уже реализованные возможности.

Основные разделы:

- Product Overview;
- Vision;
- Goals;
- Scope;
- Out of Scope;
- Users;
- Key User Journeys;
- Functional Requirements;
- Non-Functional Requirements;
- Domain Rules;
- External Integrations;
- Constraints;
- Assumptions;
- Success Criteria;
- Glossary.

Функциональные требования получают ID `FR-*`, нефункциональные — `NFR-*`, бизнес-правила — `BR-*`. Требования формулируются наблюдаемо и снабжаются проверяемыми acceptance criteria.

SPEC не содержит архитектуру, библиотеки, задачи, проценты выполнения или статусы реализации.

### 8.2 ARCHITECTURE

ARCHITECTURE описывает утверждённую целевую архитектуру. Для существующего проекта первоначальная версия восстанавливается из кода, тестов и документации, а затем утверждается пользователем.

Документ описывает:

- system context и boundaries;
- архитектурные drivers;
- компоненты и их responsibilities;
- допустимые зависимости;
- data ownership;
- data flow;
- interface и event contracts;
- runtime и deployment;
- trust boundaries;
- security, reliability и observability;
- testing strategy;
- data evolution и compatibility;
- risks и known limitations;
- ссылки на ADR.

ARCHITECTURE может содержать технические решения, но не содержит task-level implementation steps.

### 8.3 BACKLOG

BACKLOG содержит:

1. `Epic Roadmap`;
2. `Defect Queue`.

Он не содержит TASK, процентов выполнения или execution summaries.

Все сохраняемые продуктовые идеи становятся `PLANNED` Epic. Грубая идея может иметь readiness `OUTLINE` и не иметь утверждённых requirements. Перед активацией Epic обязан получить readiness `READY`.

Пользователь задаёт `P0–P3` и порядок строк внутри приоритета. Агент анализирует зависимости, предупреждает о конфликте и предлагает изменение, но ничего не переставляет самостоятельно.

### 8.4 DECISIONS и ADR

ADR-файл является источником истины для одного значимого решения. `DECISIONS.md` автоматически генерируется из ADR frontmatter и служит только индексом.

ADR обязателен для значимых, долгосрочных, cross-cutting или труднообратимых решений. Он не нужен для локальных implementation details.

Принятый ADR не переписывается задним числом. Изменение решения оформляется новым ADR с `supersedes`.

### 8.5 plan

`plan.md` владеет:

- целью и ожидаемым результатом Epic;
- implementation strategy;
- зависимостями и рисками;
- порядком TASK;
- Epic acceptance criteria;
- обязательными quality gates;
- Epic-level fuzzing и user-validation summaries.

`plan.md` не владеет TASK status и не содержит `Current Status`.

### 8.6 TASK

TASK-файл владеет:

- TASK status;
- goal, context, scope и out of scope;
- constraints;
- acceptance criteria;
- required tests и manual verification;
- references на requirements, ADR и компоненты;
- compact workflow state;
- implementation, review и testing summaries;
- user-validation history;
- user acceptance metadata.

Полные ответы субагентов и длинные tool logs не сохраняются.

## 9. Bootstrap

### 9.1 Запуск

Пользователь копирует `.ai/` в корень проекта и явно просит агента прочитать `.ai/BOOTSTRAP.md`.

Новый проект:

```text
Read .ai/BOOTSTRAP.md and initialize this repository as a new project.
Create both Codex and Claude Code adapters.
Communicate with me in Russian and start the product interview.
```

Существующий проект:

```text
Read .ai/BOOTSTRAP.md and initialize this existing repository.
Analyze the current code and documentation before starting the interview.
Create both Codex and Claude Code adapters.
Communicate with me in Russian.
```

Без явной ссылки на `.ai/BOOTSTRAP.md` первичная сессия не обязана обнаружить framework bundle.

### 9.2 Preflight

`BOOTSTRAP.md` выполняет preflight без отдельного Step 00:

- определяет new/existing mode;
- определяет язык;
- проверяет существующие canonical и platform files;
- определяет незавершённую инициализацию;
- собирает model mapping;
- выбирает Git policy;
- предупреждает о возможной перезаписи пользовательских файлов.

### 9.3 Шесть этапов

1. `01-product-discovery.md` → утверждённый SPEC.
2. `02-system-design.md` → утверждённая ARCHITECTURE, DECISIONS и начальные ADR.
3. `03-release-planning.md` → утверждённый BACKLOG.
4. `04-prepare-workspace.md` → выбранный Epic, plan и TASK.
5. `05-create-platform-adapters.md` → оба platform adapters.
6. `06-final-validation.md` → проверка структуры, ссылок, lifecycle и adapter parity.

Каждый этап завершается пользовательским подтверждением.

Step 04 включает отдельный Epic Start gate. Первая TASK остаётся `TODO` до отдельного Task Start gate.

### 9.4 Existing-project discovery

Агент анализирует существующий код, тесты и документацию, но не принимает найденное поведение за продуктовую истину без подтверждения пользователя.

Обнаруженные баги, technical debt, missing tests, dependency risks и architecture violations сначала показываются как кандидаты. Они попадают в BACKLOG только после пользовательского решения.

## 10. Platform adapters

Одновременно создаются:

```text
Codex                         Claude Code
AGENTS.md                     CLAUDE.md
.codex/agents/*.toml          .claude/agents/*.md
.agents/skills/*/SKILL.md     .claude/skills/*/SKILL.md
```

`AGENTS.md` и `CLAUDE.md` являются byte-identical короткими lifecycle routers и не превышают 150 строк каждый.

Нейтральные определения находятся в `.ai/framework/`. Сгенерированные platform files вручную не редактируются. Project-specific router additions находятся только в `.ai/custom/router-shared.md` и одинаково попадают в оба router.

Framework не создаёт hooks и MCP. Проект добавляет их отдельно при необходимости.

## 11. Models

Нейтральные agent definitions используют capability tiers:

- `strong`;
- `balanced`;
- `fast`.

`.ai/project.yaml` сопоставляет tier с concrete model и effort. Framework задаёт defaults:

| Tier | Codex | Claude Code |
| --- | --- | --- |
| `strong` | `gpt-5.6-sol`, effort `high` | `opus`, effort `high` |
| `balanced` | `gpt-5.6-terra`, effort `medium` | `sonnet`, effort `high` |
| `fast` | `gpt-5.6-luna`, effort `medium` | `haiku`, effort `high` |

Проект может явно переопределить любой default в `.ai/project.yaml`.

Adapter-generation workflow записывает concrete model:

- в `model` и `model_reasoning_effort` Codex TOML agent;
- в `model` и `effort` Claude agent frontmatter.

Поддерживаются provider aliases и полные model IDs. Изменение mapping выполняется в одном месте и синхронизируется во все соответствующие agents.

Главный orchestrator не является субагентом. Его модель задаётся основной сессией или platform project configuration. Framework предупреждает, если orchestrator не соответствует tier `strong`, но не выполняет скрытое model downgrade или upgrade.

## 12. Субагенты

| Agent | Tier | Доступ и ответственность |
|---|---|---|
| `context-collector` | fast | Локальный read-only сбор canonical, execution, Git и code context |
| `documentation-researcher` | fast | Официальная внешняя документация; network только при необходимости |
| `implementer` | balanced | Production-код и тесты; не меняет canonical status |
| `reviewer` | strong | Read-only review одной TASK |
| `tester` | fast | Запуск тестов и проверок; не исправляет код и тесты |
| `fuzzer` | balanced | Epic fuzzing; не исправляет код |
| `security-auditor` | strong | On-demand read-only security audit |

Только orchestrator вызывает субагентов. Субагенты не вызывают друг друга. Reviewer, tester, fuzzer и security-auditor возвращают результат orchestrator, который переносит только значимую summary в существующий TASK или plan.

Одновременно выполняется не более одной code-writing TASK. Независимый read-only research может выполняться параллельно.

## 13. Skills

Framework создаёт:

```text
forge-bootstrap-new
forge-bootstrap-existing
forge-intake-feature
forge-intake-bug
forge-reprioritize-backlog
forge-prepare-epic
forge-resume-development
forge-run-task
forge-complete-task
forge-complete-epic
forge-security-audit
forge-check-framework
forge-sync-adapters
```

Codex использует `$skill-name`, Claude Code — `/skill-name`. Пользователь может формулировать запрос обычным языком; router явно выбирает требуемый skill.

Mandatory lifecycle не полагается только на implicit skill matching. Orchestrator явно называет skill и agent при делегировании.

Role-specific implementation/review/testing/fuzzing contracts находятся в agent definitions, а не дублируются отдельными skills.

## 14. Forge-native engineering methods

Engineering methods являются частью существующих lifecycle skills и role-specific agent contracts, а не отдельным слоем оркестрации:

- `forge-intake-feature` восстанавливает контекст, уточняет observable outcome и границы, предлагает альтернативы при материальном выборе и завершает discovery на соответствующем canonical approval gate;
- `forge-intake-bug` воспроизводит дефект, собирает evidence, трассирует divergence, проверяет минимальные root-cause hypotheses и не меняет production/test files до отдельного Task Start;
- `forge-run-task` и `implementer` выполняют focused RED/GREEN cycle для bug fixes и meaningful business behavior, с явным not-applicable rationale для documentation, generated artifacts и simple configuration;
- `reviewer`, `tester`, `forge-run-task` и `forge-complete-task` требуют актуальные revision/fingerprint и fresh evidence перед переходом к user acceptance.

Forge lifecycle behavior определяется только bundled Forge skills, `.ai/framework/contracts.yaml` и generated agent definitions. Внешние process skills не добавляют gates, canonical или report artifacts, status transitions, agent routing или Git actions.

## 15. TASK lifecycle

```text
TODO
  ↓ Task Start gate
IN PROGRESS
  ↓ implementer
IN REVIEW
  ↓ reviewer
IN TESTING
  ↓ tester
AWAITING USER ACCEPTANCE
  ↓ Task Acceptance gate
DONE
```

Дополнительные состояния:

- `PAUSED`;
- `CANCELLED`.

Блокировка хранится отдельным `blocked_by`, а не lifecycle status.

Любое отрицательное review, testing или user-validation возвращает TASK в `IN PROGRESS`. Любое изменение кода делает прежние review и test results недействительными.

Task Acceptance и разрешение начать следующую TASK являются двумя отдельными gates. Они могут быть даны одним сообщением только при явном указании обоих решений.

Framework не выполняет отдельную автоматическую проверку атомарности TASK перед Start gate. Разделение TASK выполняется через Replan только при фактической необходимости.

## 16. Implementation, review и testing

Implementer:

- пишет production-код и необходимые тесты;
- использует TDD по умолчанию для bug fixes и значимой бизнес-логики;
- может обоснованно отметить TDD как неприменимый для documentation, generated files или простого configuration work;
- не меняет canonical statuses.

Reviewer:

- проверяет только назначенную TASK;
- оценивает correctness, regressions, security implications, architecture compliance и test coverage;
- не пишет и не исправляет код;
- возвращает findings только orchestrator.

Tester после положительного review запускает:

1. тесты, добавленные или изменённые TASK;
2. тесты затронутых компонентов;
3. полный project test suite;
4. настроенные lint, typecheck и build checks.

Tester не пишет тесты. Missing coverage возвращается implementer через orchestrator.

Полный suite обязателен для каждой TASK. Исключение допускается только при объективной невозможности локального запуска и после явного пользовательского согласия с указанным риском.

## 17. User validation

Пока пользователь тестирует вручную, TASK остаётся `AWAITING USER ACCEPTANCE` без таймаута.

Пользователь может:

- принять TASK;
- запросить изменения;
- оставить TASK на ручном тестировании.

Баг внутри непринятой TASK возвращает ту же TASK в `IN PROGRESS` и не создаёт `BUG-ID`.

Новая функция не добавляется незаметно в текущую TASK. Пользователь выбирает:

- принять текущую TASK и создать новый `PLANNED/OUTLINE` Epic;
- расширить активный Epic через Replan;
- отложить идею.

Несвязанный дефект ранее принятого кода получает `BUG-ID`. Пользователь определяет, блокирует ли он приёмку текущей TASK.

## 18. Replan

Изменение состава, порядка или scope TASK активного Epic требует Replan gate.

Orchestrator:

1. показывает причину;
2. показывает plan diff;
3. ждёт пользовательское подтверждение;
4. только затем создаёт, отменяет, разделяет или переставляет TASK.

Исправление опечаток и ссылок Replan gate не требует.

## 19. Epic и BACKLOG lifecycle

### 19.1 Readiness

```text
OUTLINE → READY
```

Epic с readiness `OUTLINE` сохраняет будущую идею, но не может быть активирован. `READY` требует утверждённых requirements, границ и зависимостей.

### 19.2 Epic status

```text
PLANNED
   ↓ Epic Start gate
ACTIVE
   ↓ все TASK приняты
FUZZING
   ↓ fuzzing пройден
AWAITING EPIC ACCEPTANCE
   ↓ Epic Acceptance gate
COMPLETED
```

Дополнительные состояния:

- `PAUSED`;
- `CANCELLED`.

Следующий Epic не активируется автоматически после завершения текущего.

### 19.3 Priority и порядок

Пользователь задаёт priority и порядок. Context collector строит граф dependencies. Orchestrator предупреждает, если более поздний Epic блокирует более ранний, и спрашивает, менять ли порядок.

Если пользователь сохраняет конфликт, заблокированный Epic остаётся `PLANNED` с `Blocked by`.

## 20. Defect Queue

Defect lifecycle:

```text
OPEN
  ↓ создана связанная TASK
SCHEDULED
  ↓ исправление принято пользователем
RESOLVED
```

Дополнительные конечные состояния:

- `REJECTED`;
- `DUPLICATE`;
- `WONT_FIX`.

Severity описывает последствия, priority — пользовательский порядок исправления.

Баг активной непринятой TASK остаётся частью этой TASK. Баг в принятом коде получает отдельный `BUG-ID`.

Связанный с активным Epic баг может стать новой TASK через Replan. Независимый срочный баг может создать Bugfix Epic. Приостановка текущей работы требует пользовательского подтверждения; Epic и TASK получают `PAUSED`.

## 21. Fuzzing

После принятия последней TASK Epic автоматически переходит в `FUZZING`. Дополнительное подтверждение на запуск существующих fuzz harnesses не требуется, поскольку fuzzer работает read-only.

Возможные результаты:

- `PASSED`;
- `HARNESS REQUIRED`;
- `FINDINGS`;
- `NOT APPLICABLE`.

`NOT APPLICABLE` требует обоснования отсутствия подходящих targets и описания альтернативного покрытия рисков.

Если target существует, но harness отсутствует, результатом является `HARNESS REQUIRED`. Orchestrator создаёт техническую TASK через Replan и отдельный Task Start gate. Harness пишет implementer.

Fuzzing использует воспроизводимые инструменты, фиксированные seeds и budgets, сохраняет crashing inputs и проверяет воспроизводимость findings.

После любого исправления выполняются review, полный testing и повторный Epic fuzzing.

## 22. Epic Acceptance

После успешного fuzzing Epic переходит в `AWAITING EPIC ACCEPTANCE`.

Если пользователь обнаруживает проблему:

1. Epic возвращается в `ACTIVE`.
2. Orchestrator предлагает Replan.
3. Создаётся новая TASK.
4. TASK проходит полный lifecycle.
5. Fuzzing повторяется.
6. Epic снова ожидает пользовательскую приёмку.

Только после Epic Acceptance статус становится `COMPLETED`, а каталог перемещается в `execution/completed/`.

## 23. ADR Approval

ADR lifecycle:

```text
PROPOSED → ACCEPTED
         ↘ REJECTED

ACCEPTED → SUPERSEDED
         → DEPRECATED
```

Только пользователь переводит ADR из `PROPOSED` в `ACCEPTED`. Если необходимость ADR обнаружена во время TASK, TASK приостанавливается до решения.

## 24. Security auditor

Security auditor:

- вызывается только явно пользователем;
- использует tier `strong`;
- по умолчанию анализирует только локальный repository;
- не изменяет код;
- не устанавливает инструменты;
- не использует network;
- не сканирует production или внешние targets.

Network access, установка scanner, загрузка vulnerability database и active scanning требуют отдельного разрешения с точным scope.

Findings возвращаются orchestrator. После пользовательского решения они превращаются в `BUG-*`, TASK или Epic. Отдельный security report не создаётся.

## 25. Восстановление после прерывания

Session history не является источником истины.

`forge-resume-development` восстанавливает:

- активный или paused Epic из BACKLOG и execution tree;
- current TASK из TASK statuses;
- текущий gate из workflow state;
- последние review/test/user-validation summaries;
- незавершённые изменения из Git status и diff.

Если вызванный субагент не оставил зафиксированного результата, этап считается незавершённым и запускается повторно.

## 26. Git policy

Поддерживаются:

```text
manual
auto_commit_after_acceptance
```

По умолчанию используется `manual`.

Commit TASK является отдельным gate после явного Task Acceptance и перехода TASK в `DONE`; до подтверждения пользователя commit запрещён.

В manual mode orchestrator после принятия TASK предлагает изменённые файлы и commit message, но не выполняет commit без отдельного разрешения пользователя.

В automatic mode commit допустим только после:

1. положительного review;
2. полного testing;
3. явного Task Acceptance;
4. перевода TASK в `DONE`.

Task commit никогда не является доказательством или заменой Task Acceptance и не может предшествовать ему.

## 27. Final validation invariants

Bootstrap, adapter sync и resume проверяют:

- отсутствие template placeholders в approved documents;
- существование обязательных canonical files;
- корректность frontmatter;
- уникальность ID;
- валидность status values и transitions;
- не более одного активного Epic;
- не более одной текущей code-writing TASK;
- соответствие execution directory Epic status;
- корректность ссылок FR/NFR/BR/EPIC/TASK/BUG/ADR;
- отсутствие TASK status в plan;
- отсутствие implementation status в SPEC и ARCHITECTURE;
- parity Codex и Claude roles, skills и lifecycle rules;
- лимит 150 строк для `AGENTS.md` и `CLAUDE.md`;
- отсутствие default hooks и MCP;
- возможность восстановить текущий gate без session history;
- отсутствие production-code changes во время bootstrap.

## 28. Не входит в первую версию

- Framework CLI и команды `forge` как executable.
- Self-bootstrap framework repository: в нём не создаются project canonical documents, execution workspace или generated root adapters.
- Framework-provided hooks.
- Framework-provided MCP servers.
- Параллельные code-writing TASK.
- Автоматическое изменение пользовательского priority.
- Автоматическая активация следующей TASK или Epic.
- Отдельные report/state/progress Markdown-файлы.
- Скрытые network или security scans.

## 29. Критерии готовности реализации дизайна

Дизайн считается реализованным, когда:

1. `.ai/` поддерживает new и existing bootstrap.
2. Все templates соответствуют утверждённым ownership и lifecycle rules.
3. Одновременно генерируются нативные Codex и Claude adapters.
4. Семь субагентов имеют согласованные models, permissions и contracts.
5. Все lifecycle skills доступны на обеих платформах.
6. Core workflow самостоятельно реализует engineering methods и работает без внешнего lifecycle layer, hooks, MCP и CLI.
7. TASK хранит все task-level summaries без report-файлов.
8. Epic проходит mandatory fuzzing и отдельный Epic Acceptance.
9. Resume восстанавливает процесс только из repository state.
