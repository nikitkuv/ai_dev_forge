## Сценарий 2. Инициализация существующего проекта

> Bootstrap существующего проекта сохраняет native agents обеих платформ и требует явный `role_execution.mode`. Cross-provider runtime используется только в выбранном режиме и не имеет fallback.

### Исходное состояние

В существующем TaskFlow уже есть код и документы:

```text
taskflow/
├── src/
├── tests/
├── README.md
├── docs/legacy-requirements.md
├── package.json
└── .git/
```

Предположим, что:

- код хранит задачи только в памяти;
- один тест ожидает сохранение после перезапуска;
- README утверждает, что persistent storage уже готов;
- пользователь хочет SQLite и offline-first behavior;
- в Git есть незакоммиченные пользовательские изменения.

Пользователь копирует `.ai/` в корень, не удаляя существующие файлы.

### Шаг 0. Стартовый запрос

> **Пользователь:**
>
> Read .ai/BOOTSTRAP.md and initialize this existing repository.  
> Analyze the current code and documentation before starting the interview.  
> Create both Codex and Claude Code adapters.  
> Communicate with me in Russian.

**Внутреннее действие**

Оркестратор выбирает `forge-bootstrap-existing`. В отличие от нового проекта, он не начинает с вопроса «какой продукт вы хотите?». Сначала собирается repository evidence.

### Шаг 1. Read-only discovery существующего состояния

Оркестратор вызывает `context-collector` с tier `fast`.

Контекст-субагент читает локально и без изменений:

- source code и package boundaries;
- тесты и fixtures;
- README и legacy-документы;
- конфигурацию, deployment и migrations;
- Git status, diff и недавнюю историю;
- существующие agent instructions;
- потенциальные дефекты, debt и architecture violations.

Субагент возвращает evidence оркестратору, а не пишет отдельный report-файл.

> **Оркестратор:** Я нашёл несколько несовпадений:
>
> | Источник | Утверждение |
> | --- | --- |
> | Код | задачи существуют только в памяти |
> | Тест | после перезапуска задача должна сохраниться |
> | README | persistent storage уже реализован |
> | Ваш запрос | целевое хранение — SQLite и offline-first |
>
> Код показывает текущее поведение, но не определяет автоматически target behavior. Что считать целевым: тест и ваш запрос, либо текущее in-memory поведение?

> **Пользователь:** Целевое поведение — сохранение в SQLite. README устарел, а тест описывает желаемое поведение.

**Внутреннее действие**

Оркестратор классифицирует каждое утверждение:

- code evidence;
- test evidence;
- documentation claim;
- user-confirmed intent;
- inference.

Ни один вывод не становится requirement, Bug или Epic без решения пользователя.

### Шаг 2. Защита существующей работы

До записи framework-файлов оркестратор показывает collisions и unrelated Git changes.

> **Оркестратор:** В рабочем дереве изменён `src/ui.ts`, но изменение не относится к bootstrap. Я сохраню его без изменений и не включу в framework commit. Корневой README уже существует, поэтому позже покажу только минимальный diff со ссылками на canonical документы. Подтверждаете продолжение?

> **Пользователь:** Да, `src/ui.ts` не трогай.

**Состояние после шага**

- существующий код не изменён;
- незакоммиченный diff пользователя сохранён;
- collision decisions пока находятся в текущем gate;
- режим `existing` подтверждён пользователем и восстанавливается вместе с repository evidence и состоянием numbered workflows;
- `.ai/project.yaml` фиксирует язык, модели, `role_execution.mode`, integrations и Git policy.

### Шаг 3. Existing-project Product Discovery

Интервью начинается уже с собранным evidence.

> **Оркестратор:** Подтверждённый target behavior включает SQLite persistence. Нужно ли сохранять совместимость с текущим форматом in-memory export, если он используется пользователями?

> **Пользователь:** Да, импорт старого JSON нужен, но экспорт можно сделать отдельным будущим Epic.

> **Оркестратор:** Тогда предлагаю:
>
> - добавить migration/import requirement в SPEC;
> - старый экспорт сохранить как будущий `PLANNED/OUTLINE` Epic;
> - несоответствие текущего кода target behavior пока считать implementation gap, а не Bug.
>
> Подтверждаете?

> **Пользователь:** Да.

**Внутреннее действие**

- `SPEC.md` описывает утверждённый target state, а не копию текущего поведения.
- Нереализованное target behavior не помечается как «готовое».
- Случайные особенности старого кода не становятся требованиями.
- Документ утверждается отдельным approval так же, как в новом проекте.

### Шаг 4. Existing-project architecture reconciliation

> **Оркестратор:** Текущий код связывает UI напрямую с in-memory store. Для target architecture предлагаю repository boundary и SQLite adapter. Это изменяет dependency direction и требует ADR. Возможны два пути:
>
> 1. постепенная замена за interface boundary;
> 2. полная переработка storage слоя одной большой TASK.
>
> Рекомендую постепенную замену, чтобы сохранить работающий UI и упростить review. Выбираем её?

> **Пользователь:** Да.

**Внутреннее действие**

- `ARCHITECTURE.md` явно различает current и target architecture.
- ADR фиксирует repository boundary и migration strategy.
- Technical debt, который не нужен для target behavior, не добавляется автоматически.

### Шаг 5. Кандидаты в Backlog

После discovery оркестратор показывает, но не сохраняет автоматически:

- новые capabilities;
- implementation gaps;
- подтверждённые дефекты;
- technical debt;
- architecture risks;
- missing test coverage.

> **Оркестратор:** Найдены четыре кандидата:
>
> 1. Epic миграции на SQLite;
> 2. будущий Epic JSON export;
> 3. возможный Bug: README сообщает о несуществующей persistence;
> 4. debt: UI напрямую зависит от store.
>
> Предлагаю пункт 1 оформить как `READY` Epic, пункт 2 как `OUTLINE` Epic, пункт 3 исправить в рамках bootstrap README без Bug ID, пункт 4 включить в scope миграционного Epic. Подтверждаете?

> **Пользователь:** Да. Отдельный Bug для README не нужен.

**Внутреннее действие**

- В `BACKLOG.md` появляются только одобренные Epic.
- `BUG-*` не создаётся для отклонённого кандидата.
- Пользователь назначает priority и порядок.
- Оркестратор анализирует dependency conflict и спрашивает перед перестановкой.

### Шаг 6. Workspace и решение об активации Epic

Инициализация существующего проекта не обязана сразу активировать Epic.

> **Оркестратор:** Backlog готов. Можно закончить bootstrap без detailed workspace, подготовить migration Epic в planned queue либо отдельно подготовить и активировать его. Что выбираете?

> **Пользователь:** Подготовь migration Epic в очереди, но пока не активируй его и не запускай TASK.

Далее происходят те же отдельные gates:

1. strong read-only `epic-planner` формирует проверяемое предложение с requirement coverage, quality profiles, risk map и Epic/Task verification;
2. orchestrator независимо проверяет proposal, затем запрашивает Plan Approval для Epic plan и всех TASK definitions;
3. Plan Approval создаёт `execution/planned/EPIC-*`, оставляет Backlog status `PLANNED`, а все TASK создаёт как `TODO`;
4. отдельный Epic Start остаётся pending и позже переместит approved workspace в `execution/active/` только после повторной проверки eligibility;
5. Task Start не подразумевается ни Plan Approval, ни Epic Start.

### Шаг 7. Adapter collisions в существующем проекте

В проекте уже может быть `AGENTS.md`, `CLAUDE.md` или platform-specific agent configuration.

> **Оркестратор:** Существующий `CLAUDE.md` не был сгенерирован Forge и содержит проектные команды. Я не буду перезаписывать его молча. Предлагаю перенести уникальные project instructions в `.ai/custom/`, показать итоговый diff и затем сгенерировать оба router. Подтверждаете этот collision resolution?

> **Пользователь:** Да, но сохрани команды запуска без изменений.

**Внутреннее действие**

- Пользовательские инструкции переносятся только после подтверждения.
- Оба adapters генерируются одной логической операцией.
- При ошибке одного adapter второй тоже не заменяется.
- `.ai/framework.lock` записывается только после parity validation.

### Шаг 8. Прерывание и восстановление bootstrap

Предположим, сессия завершилась после утверждения `SPEC.md`, но до approval архитектуры.

В новой сессии пользователь пишет:

> **Пользователь:** Продолжи инициализацию фреймворка с места остановки.

**Внутреннее действие**

Новый оркестратор не полагается на память предыдущего чата. Он читает:

1. `.ai/project.yaml` — язык, модели, режим planner/reviewer, integrations и Git policy;
2. frontmatter `SPEC.md` — документ уже approved;
3. frontmatter `ARCHITECTURE.md` — draft или отсутствует;
4. ADR и `DECISIONS.md`;
5. `BACKLOG.md` и execution tree;
6. `.ai/framework.lock` и generated adapters;
7. Git status и diff;
8. признаки existing-project mode из repository evidence и уже выполненных numbered workflows.

> **Оркестратор:** Product Discovery завершён: `SPEC.md` approved. System Design не завершён: `ARCHITECTURE.md` draft, `ADR-001` ещё `PROPOSED`. Текущий gate — продолжить архитектурное интервью и запросить отдельный ADR Approval. Продолжаем?

Оркестратор не пересоздаёт approved SPEC и не объявляет bootstrap завершённым по истории чата.

### Итог существующего проекта

```text
Existing TaskFlow adopted
├── current implementation preserved as evidence
├── target behavior captured in approved SPEC
├── current/target architecture differences explicit
├── only approved candidates added to Backlog
├── unrelated Git changes preserved
├── both adapters generated after collision approval
└── next gate recovered from files, not conversation history
```

---
