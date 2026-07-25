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
├── .claude/agents/          # Субагенты (implementation, validation, review, fuzzing)
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
| .claude/agents/ | Субагенты (implementation, validation, review, fuzzing) | AI | Step 05 |
| docs/ | Документация | AI / documentation agent | Step 04 (пустая), наполняется по мере |
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
- создание субагентов в `.claude/agents/` (implementation, validation, review, fuzzing)
- поддержка опциональных `.ai/rules/`

⚠️ CLAUDE.md:

- ~90 строк
- навигация + orchestrator pattern + правила
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

# ⚙️ Workflow разработки (Orchestrator Pattern)

Главный агент — **оркестратор**. Он не пишет код, а делегирует субагентам.

## 1. Оркестратор читает контекст

- читает CLAUDE.md
- находит active Epic в BACKLOG.md
- открывает plan.md
- определяет текущую TASK (IN PROGRESS или первый TODO)

## 2. Оркестратор запускает implementation субагента

- передаёт субагенту файл таски + контекст (ARCHITECTURE.md, plan.md)
- субагент сам собирает контекст
- субагент реализует задачу и пишет тесты
- если задачи независимы (разные файлы) → несколько субагентов параллельно

## 3. Субагент отчитывается оркестратору

- статус: DONE / IN PROGRESS
- список файлов
- результаты тестов

## 4. Оркестратор запускает review субагента

- review проверяет код: архитектура, качество, баги, acceptance criteria
- если найдены критические проблемы → оркестратор запускает implementation для доработки
- если всё ок → таска остаётся DONE

## 5. Оркестратор переходит к следующей таске

- повторяет шаги 2-4 для каждой таски эпика

## 6. Завершение Epic

- когда все таски DONE → оркестратор запускает fuzzing субагента
- fuzzing тестирует функции на устойчивость
- если краши → создаёт Bug таски
- Epic → Completed, перенос в execution/completed/

---

# 🧠 Ключевые принципы системы

## 1. Separation of Concerns

- SPEC → WHAT
- ARCHITECTURE → HOW
- BACKLOG → WHAT WILL BE DONE
- execution → WHAT IS BEING DONE
- CLAUDE.md → HOW TO NAVIGATE

---

## 2. Orchestrator Delegation

- главный агент — оркестратор, не пишет код
- 1 задача = 1 субагент
- независимые задачи → параллельные субагенты
- зависимые задачи → последовательно

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

- ~90 строк
- навигация + orchestrator pattern + правила
- не содержит определений субагентов

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
