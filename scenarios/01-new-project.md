## Сценарий 1. Инициализация нового проекта с нуля

> В Claude Code `epic-planner` и `reviewer` предпочитают `codex-plugin-cc` с `gpt-5.6-sol/high`; отсутствие runtime сохраняет штатный Claude-subagent fallback.

### Исходное состояние

В репозитории может не быть ничего, кроме `.git/`, краткого product brief или нескольких исходных заметок. В нём ещё нет canonical документов и platform adapters.

Пользователь копирует в корень проекта только папку `.ai/` из AI Development Forge.

```text
taskflow/
└── .ai/
```

Bootstrap не запускается автоматически после копирования. Его начинает основной агент по явному запросу пользователя.

### Шаг 0. Стартовый запрос

> **Пользователь:**
>
> Read .ai/BOOTSTRAP.md and initialize this repository as a new project.  
> Create both Codex and Claude Code adapters.  
> Communicate with me in Russian and start the product interview.

**Внутреннее действие**

1. Оркестратор явно выбирает `forge-bootstrap-new`.
2. Полностью читает `.ai/BOOTSTRAP.md`, conventions, manifest, contracts и шесть numbered workflows.
3. Проверяет, что открыт проект-потребитель, а не сам репозиторий `ai_dev_forge`.
4. Проверяет Git status и возможные столкновения с существующими файлами.
5. Не создаёт код, hooks, MCP или отдельные отчёты.

### Шаг 1. Bootstrap preflight и конфигурация

Оркестратор должен зафиксировать настройки, без которых interrupted bootstrap нельзя надёжно продолжить.

> **Оркестратор:** Прежде чем формировать продуктовые документы, нужно согласовать настройки проекта:
>
> - язык canonical документов — русский;
> - генерируем обе платформы — Codex CLI и Claude Code CLI;
> - Git policy — `manual`;
> - для каждой платформы нужны выбранные вами model mappings для tiers `strong`, `balanced` и `fast`; для Codex также нужен reasoning effort.
>
> Подтверждаете эти настройки и выбранные model IDs?

> **Пользователь:** Да. Используй выбранные мной доступные модели для каждого tier. Git policy — `manual`.

**Внутреннее действие**

- Оркестратор не придумывает модели и не заменяет tier скрытно.
- Он записывает подтверждённые значения в `.ai/project.yaml`.
- Если файл уже существует, сначала показывает collision diff.

**Состояние после шага**

```text
.ai/project.yaml
  documentation_language: ru
  platforms.codex.enabled: true
  platforms.claude.enabled: true
  models: конкретные mappings, подтверждённые пользователем
  git.policy: manual
```

Product state ещё не создан. Текущий durable gate — начало Product Discovery.

### Шаг 2. Product Discovery → `SPEC.md`

Оркестратор читает `.ai/01-product-discovery.md` и начинает итеративное интервью.

> **Оркестратор:** Одним предложением: какую проблему решает TaskFlow и для кого?

> **Пользователь:** Это простое локальное приложение для личных задач. Я хочу быстро записывать задачи и не зависеть от облака.

> **Оркестратор:** Что обязательно должно войти в первую целевую версию: создание, редактирование, удаление, сроки, категории, синхронизация?

> **Пользователь:** Создание, список и завершение задачи. Редактирование и удаление тоже нужны, но позже. Синхронизация — будущая идея.

> **Оркестратор:** Должны ли задачи сохраняться после перезапуска? Есть ли ограничение на число задач? Нужна ли работа без сети?

> **Пользователь:** Да, сохраняться локально. До 10 000 задач. Всё основное должно работать без сети.

**Внутреннее действие**

1. Оркестратор формулирует наблюдаемые `FR-*`, измеримые `NFR-*` и бизнес-инварианты `BR-*`.
2. Не добавляет архитектуру, технологии, TASK, проценты готовности или implementation status.
3. Сохраняет draft в корневом `SPEC.md` на русском языке.
4. Показывает пользователю смысловой diff или краткую структуру документа.

Пример результата:

```text
FR-001 — пользователь может создать задачу с названием.
FR-002 — пользователь видит сохранённые задачи после перезапуска.
FR-003 — пользователь может отметить задачу выполненной.
NFR-001 — основные операции доступны без сети.
NFR-002 — поддерживается не менее 10 000 задач.
BR-001 — каждая задача имеет стабильный уникальный ID.
```

> **Оркестратор:** Draft `SPEC.md` создан. Синхронизация сохранена как будущая capability, но не включена в первый scope. Утверждаете SPEC?

> **Пользователь:** Добавь, что завершённая задача остаётся видимой в истории. После этого утверждаю.

**Внутреннее действие**

- Оркестратор изменяет тот же draft, повторно показывает поправку.
- Только после явного утверждения ставит `document_status: approved` и `approved_at`.
- Положительная фраза без явного утверждения не считается approval.

**Состояние после шага**

```text
SPEC.md
  document_status: approved
  language: ru
```

Единственным владельцем target product behavior теперь является `SPEC.md`.

### Шаг 3. System Design → `ARCHITECTURE.md`, ADR и `DECISIONS.md`

Оркестратор читает `.ai/02-system-design.md`, использует утверждённый SPEC как requirement driver и проводит архитектурное интервью.

> **Оркестратор:** Для локального хранения есть несколько подходов:
>
> 1. JSON-файл — минимальная сложность, но хуже масштабируется и сложнее безопасно обновлять;
> 2. SQLite — надёжные транзакции и удобная выборка, но появляется схема и миграции;
> 3. embedded key-value storage — простые операции, но меньше возможностей для будущих запросов.
>
> Для 10 000 задач и будущих фильтров рекомендую SQLite. Выбираем его?

> **Пользователь:** Да, SQLite подходит.

> **Оркестратор:** Это долгоживущее решение, влияющее на данные и миграции. Предлагаю оформить `ADR-001 — Use SQLite for local task storage`.

> **Пользователь:** Согласен.

**Внутреннее действие**

1. Создаётся `decisions/ADR-001-use-sqlite.md` со status `PROPOSED`.
2. Оркестратор показывает контекст, варианты, последствия и migration implications.
3. После отдельного ADR Approval status становится `ACCEPTED`.
4. `DECISIONS.md` генерируется как индекс из ADR frontmatter; он не дублирует решение.
5. `ARCHITECTURE.md` описывает компоненты, boundaries, data ownership, interfaces, trust boundaries, runtime, reliability, observability, testing и migration.

> **Оркестратор:** Архитектура разделена на UI, application service и repository boundary. SQLite принадлежит repository-компоненту. `ADR-001` принят. Утверждаете `ARCHITECTURE.md`?

> **Пользователь:** Да, утверждаю.

**Состояние после шага**

```text
ARCHITECTURE.md                    document_status: approved
decisions/ADR-001-use-sqlite.md   status: ACCEPTED
DECISIONS.md                      generated: true
```

### Шаг 4. Release Planning → `BACKLOG.md`

Оркестратор читает `.ai/03-release-planning.md` и превращает все сохранённые идеи в Epic Roadmap.

> **Оркестратор:** Предлагаю следующие Epic:
>
> - `EPIC-001` — базовое локальное создание и просмотр задач;
> - `EPIC-002` — завершение и история задач;
> - `EPIC-003` — редактирование и удаление;
> - `EPIC-004` — синхронизация между устройствами.
>
> `EPIC-004` пока `OUTLINE`, потому что требования к конфликтам и аккаунтам не определены. Назначьте приоритеты и желаемый порядок.

> **Пользователь:** EPIC-001 — P0, EPIC-002 — P0, EPIC-003 — P1, EPIC-004 — P2.

**Внутреннее действие**

1. Пользователь задаёт priority и порядок.
2. Оркестратор строит dependency graph.
3. Если поздний Epic блокирует ранний, оркестратор не переставляет строки сам.

Пример конфликта:

> **Оркестратор:** `EPIC-002` использует стабильную модель хранения из `EPIC-001`, поэтому текущий порядок допустим. Но если бы `EPIC-003` создавал обязательную migration infrastructure для `EPIC-002`, я бы показал блокировку и спросил, менять ли порядок. Без вашего подтверждения приоритет не меняется.

В новом проекте Defect Queue обычно пуст. Неподтверждённые опасения не превращаются в `BUG-*` автоматически.

> **Оркестратор:** `BACKLOG.md` содержит четыре Epic, пользовательский порядок и зависимости. Утверждаете Backlog?

> **Пользователь:** Да.

**Состояние после шага**

```text
BACKLOG.md
  document_status: approved
  Epic Roadmap: EPIC-001 ... EPIC-004
  Defect Queue: empty
```

`BACKLOG.md` владеет Epic priority, readiness, dependencies, blockers и status. TASK-списков в нём нет.

### Шаг 5. Prepare Workspace → Epic plan и TASK-файлы

Оркестратор выбирает `PLANNED + READY` Epic со стабильными requirements, boundaries и declarations зависимостей. Unsatisfied dependencies, blockers или другой active Epic не мешают планированию, но позже блокируют Epic Start. Допустим, выбран `EPIC-001`.

Он вызывает strong read-only `epic-planner`, передаёт approved canonical documents, repository/CI evidence, quality configuration, contracts и templates, затем независимо проверяет предложение. Planner не пишет plan/TASK-файлы и не утверждает их.

> **Оркестратор:** Для `EPIC-001` предлагаю три TASK:
>
> - `TASK-001` — создать domain-модель задачи и правила ID;
> - `TASK-002` — реализовать SQLite repository;
> - `TASK-003` — реализовать создание и список задач через application/UI boundary.
>
> Показываю полный plan, requirement coverage, quality profiles, Epic Verification Plan, acceptance criteria, зависимости, affected surfaces, risk flags, review focus и selected Task checks. Утверждаете определения plan и TASK?

> **Пользователь:** Для TASK-002 добавь проверку миграции пустой базы. Остальное принимаю.

**Внутреннее действие**

- Оркестратор обновляет proposed plan и TASK-002.
- До approval файлы остаются draft или ещё не создаются в execution workspace.
- После Plan Approval approved plan и все `TODO` TASK-файлы атомарно создаются в `execution/planned/EPIC-001-core/`; `BACKLOG.md` сохраняет `EPIC-001` в `PLANNED`.

> **Оркестратор:** Определения обновлены и сохранены в planned queue. Отдельный gate: активировать `EPIC-001` сейчас?

> **Пользователь:** Нет, оставь его спланированным в очереди.

**Внутреннее действие**

1. Epic Start не срабатывает; `EPIC-001` остаётся `PLANNED + READY`.
2. Approved workspace остаётся в `execution/planned/`.
3. Все три TASK имеют `definition_status: approved` и `status: TODO`.
4. Ни одна TASK не переходит в `IN PROGRESS`.

**Состояние после шага**

```text
execution/planned/EPIC-001-core/
├── plan.md
└── tasks/
    ├── TASK-001-domain-model.md    status: TODO
    ├── TASK-002-sqlite-repository.md
    └── TASK-003-create-and-list.md
```

Позже Epic Start повторно проверит dependencies, `Blocked by` и отсутствие другого active-work Epic, затем атомарно переместит каталог `execution/planned/ → execution/active/` вместе с переходом Backlog `PLANNED → ACTIVE`. Epic Start не является Task Start.

### Шаг 6. Создание Codex и Claude Code adapters

Оркестратор читает `.ai/05-create-platform-adapters.md`.

**Внутреннее действие**

1. Повторно проверяет model mappings в `.ai/project.yaml`.
2. Проверяет существующие `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.claude/`, `.agents/` на collision.
3. Показывает diff до перезаписи любых generated outputs.
4. Рендерит оба adapter-набора из одних neutral sources.
5. Проверяет parity: 7 агентов и 14 skills на каждой платформе.
6. Проверяет лимит root-router в 150 строк.
7. Создаёт `.ai/framework.lock` с hashes источников и outputs.
8. Создаёт или минимально дополняет project `README.md` после отдельного collision confirmation.

> **Оркестратор:** Collision не найден. Будут созданы оба router, 14 Codex skills, 14 Claude skills и по 7 agent-файлов. Подтверждаете генерацию?

> **Пользователь:** Да.

После генерации оркестратор показывает созданные пути, model mappings, router line counts, parity checks и hashes lock-файла.

> **Оркестратор:** Оба adapter-набора сгенерированы и прошли parity validation. Подтверждаете результат Step 05 и переход к Final Validation?

> **Пользователь:** Да, Step 05 принимаю.

**Состояние после шага**

```text
AGENTS.md
CLAUDE.md
.codex/agents/*.toml
.agents/skills/*/SKILL.md
.claude/agents/*.md
.claude/skills/*/SKILL.md
.ai/framework.lock
```

Generated adapters вручную не редактируются. Проектные дополнения хранятся в `.ai/custom/` и применяются через adapter sync.

### Шаг 7. Final Validation

Оркестратор читает `.ai/06-final-validation.md` и выполняет read-only проверку.

Проверяется:

- ownership и обязательные root-файлы;
- frontmatter и approval metadata;
- ссылки между requirements, architecture, ADR, Epic, plan и TASK;
- согласованность `BACKLOG.md` с ordered `execution/planned/` queue и `execution/active/`;
- отсутствие циклов TASK dependencies;
- parity двух adapters;
- отсутствие hooks, MCP, CLI dependency и report Markdown;
- восстановление текущего gate без истории чата.

> **Оркестратор:** Final Validation пройдена. `EPIC-001` находится в planned queue, все три TASK имеют status `TODO`, активного Epic нет. Следующий допустимый gate — Epic Start для `EPIC-001`. Подтверждаете результат Step 06 и завершение bootstrap?

> **Пользователь:** Да, Final Validation принимаю. Bootstrap можно завершить.

> **Оркестратор:** Bootstrap завершён. Отдельный следующий gate — Epic Start для `EPIC-001`; только после него можно запрашивать Task Start для `TASK-001`. Активировать EPIC-001?

На этом bootstrap заканчивается. Сам вопрос о запуске TASK не означает её запуск.

### Итог нового проекта

```text
TaskFlow initialized
├── canonical product and architecture: approved
├── Backlog: approved
├── EPIC-001: ACTIVE
├── TASK-001: TODO
├── Codex adapter: generated
├── Claude Code adapter: generated
└── current gate: task_start
```

---
