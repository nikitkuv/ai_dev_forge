# AI Dev Forge

---

# 🧠 Структура проекта

```text
project/
│
├── README.md                  # Введение для человека
├── CLAUDE.md                  # Навигация и входная точка для AI (≤100 строк)
│
├── SPEC.md                   # Что представляет продукт (WHAT)
├── ARCHITECTURE.md          # Как система устроена (HOW)
├── BACKLOG.md               # Глобальный список Epics (WHAT WILL BE DONE)
├── DECISIONS.md             # ADR индекс — навигация по решениям
├── decisions/               # Атомарные ADR-записи (ADR-NNN-name.md)
│
├── execution/               # Runtime слой (текущее выполнение)
│   ├── active/
│   │    ├── EPIC-001-short-name/
│   │    │      ├── plan.md
│   │    │      └── tasks/
│   │    │            ├── TASK-001-short-name.md
│   │    │            ├── TASK-002-short-name.md
│   │    │            └── ...
│   │
│   └── completed/
│
├── .claude/agents/          # Субагенты (Implementation, Validation, ...)
├── docs/                    # Документация (knowledge layer)
├── references/              # Внешние материалы, исследования
├── tests/                   # Тесты
├── src/                     # Кодовая база
```

---

# 📄 Назначение документов

| Файл | Назначение | Кто создает | Когда |
|------|-----------|-------------|-------|
| README.md | Введение для человека | AI + человек | Сразу |
| CLAUDE.md | Карта проекта + AI навигация | AI | После bootstrap |
| SPEC.md | Описание продукта (WHAT) | AI + человек | Step 01 |
| ARCHITECTURE.md | Архитектура (HOW) | AI + человек | Step 02 |
| BACKLOG.md | Список Epics (WHAT WILL BE DONE) | AI + человек | Step 03 |
| DECISIONS.md | ADR индекс (навигация) | AI + человек | Step 02 |
| decisions/ | Атомарные ADR-записи | AI + человек | Step 02, далее по мере решений |
| execution/ | Runtime слой разработки | AI | Step 04 |
| plan.md | План Epic | AI | Step 04 |
| TASK-NNN-name.md | Атомарные задачи | AI | Step 04 |
| .claude/agents/ | Субагенты (Implementation, Validation, ...) | AI | Step 05 |
| docs/ | Документация | Documentation Agent | Step 04 (пустая), наполняется по мере |
| references/ | Внешние материалы | Человек | Step 04 (пустая), наполняется по мере |

---

# 🚀 Bootstrap процесс (как создается проект)

## STEP 01 — Product Discovery → SPEC.md

- совместно формируется понимание продукта
- задаются вопросы
- уточняются требования
- создается SPEC.md

👉 SPEC = WHAT is the product

---

## STEP 02 — System Design → ARCHITECTURE.md

- анализ SPEC.md
- проектирование системы
- определение компонентов и взаимодействий
- создание ARCHITECTURE.md
- инициализация журнала решений (DECISIONS.md + decisions/)

👉 ARCHITECTURE = HOW system works
👉 DECISIONS = принятые архитектурные компромиссы

---

## STEP 03 — Release Planning → BACKLOG.md

- анализ SPEC + ARCHITECTURE
- выделение Epics
- формирование roadmap
- определение приоритетов

⚠️ BACKLOG содержит только Epics (без задач и прогресса)

👉 BACKLOG = WHAT will be built

---

## STEP 04 — Prepare Workspace → execution/

- выбор активного Epic
- создание execution/active/EPIC-NNN-name
- создание plan.md
- разбиение на TASK-NNN-name.md
- создание пустых docs/ и references/

👉 execution = WHAT is being built

---

## STEP 05 — Create AI Environment → CLAUDE.md + .claude/agents/

- создание карты проекта
- описание AI workflow
- определение правил работы AI
- создание субагентов в `.claude/agents/` (Implementation, Validation, ...)
- поддержка опциональных `.ai/rules/`

⚠️ CLAUDE.md:

- ≤ 100 строк
- только навигация
- не содержит знаний
- не содержит определений субагентов (они в `.claude/agents/`)

👉 CLAUDE.md = AI router

---

## STEP 06 — Final Validation

- проверка структуры
- проверка навигации
- проверка consistency
- проверка workflow
- исправление минимальных несоответствий

👉 система готова к разработке

---

# 🧭 Навигация AI (runtime workflow)

Каждая новая сессия следует фиксированному пути:

```text
CLAUDE.md
&#x20;   ↓
BACKLOG.md
&#x20;   ↓
Active Epic
&#x20;   ↓
execution/active/EPIC/plan.md
&#x20;   ↓
TASK-NNN-name.md
&#x20;   ↓
Codebase
```

---

# ⚙️ Workflow разработки

## 1. Контекстная инициализация

AI:

- читает CLAUDE.md
- находит active Epic
- открывает plan.md
- определяет текущую TASK

---

## 2. Анализ кода (при необходимости)

- отдельный контекстный агент
- использует MCP / code search
- возвращает summary

---

## 3. Реализация

AI:

- реализует одну задачу
- не выходит за её рамки
- пишет тесты

---

## 4. Проверка

- запуск тестов
- lint (ruff, mypy и т.д.)
- проверка качества

AI не чинит результаты сам — только анализирует

---

## 5. Обновление состояния

AI:

- переводит задачу в `IN PROGRESS` перед стартом и в `DONE` по завершении
- обновляет TASK-NNN-name.md
- обновляет plan.md
- обновляет Epic progress
- при необходимости обновляет BACKLOG.md
- фиксирует значимые решения как ADR в `decisions/` и обновляет индекс `DECISIONS.md`

⚠️ одновременно активна только одна задача (`IN PROGRESS`) — это и есть «текущая задача»

---

## 6. Завершение Epic

Если Epic завершён:

- перенос в execution/completed/
- активация следующего Epic
- создание нового plan.md
- генерация TASK-NNN-name.md

---

# 🧠 Ключевые принципы системы

## 1. Separation of Concerns

- SPEC → WHAT
- ARCHITECTURE → HOW
- BACKLOG → WHAT WILL BE DONE
- execution → WHAT IS BEING DONE
- CLAUDE.md → HOW TO NAVIGATE

---

## 2. Single Task Execution

- всегда 1 задача за раз
- последовательное выполнение
- без параллельной разработки

---

## 3. Deterministic AI Behavior

При одинаковом состоянии:

- AI всегда находит один и тот же Epic
- всегда одну и ту же TASK
- всегда один и тот же workflow

---

## 4. Minimal Context Principle

AI никогда не читает весь проект:

- только путь выполнения
- только необходимый контекст

---

## 5. CLAUDE.md Constraint

- ≤ 100 строк
- не содержит знаний
- только навигация
- только routing

---

## 6. Rule Delegation

Если правил становится много:

```text
.ai/rules/
```

CLAUDE.md не расширяется.

---

# 📌 Итог

Эта система превращает разработку в:

> deterministic execution pipeline for AI coding agents

---

# 🟢 Результат

После bootstrap:

- проект полностью описан
- структура готова
- AI может работать без внешней памяти
- контекст всегда локализован
- выполнение строго детерминировано
