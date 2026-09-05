# Scenario 05 — Ad hoc investigation

## Research only

> **Пользователь:** Исследуй, почему пакетный алгоритм расчёта работает медленно. Пока ничего не исправляй.

Оркестратор явно invokes `forge-investigate`, выделяет следующий `INV-NNNN`, создаёт `investigations/INV-NNNN-algorithm-latency.md` и фиксирует baseline, scope и `research_only` authorization. Generated subagents не вызываются.

Основной агент сам читает релевантный код и историю, воспроизводит workload, выполняет bounded benchmark и profiling, проверяет гипотезы и обновляет INV только material evidence. Он отделяет наблюдение «85% времени занимает повторный lookup» от вывода о причине.

После подтверждения причины пользователь решает ничего не менять. INV получает:

```yaml
outcome: no_action
```

`Next Action` описывает возможное кэширование lookup, затрагиваемые пути, риски и проверку производительности. Backlog и execution state не меняются.

## Promote to normal work

> **Пользователь:** Оформи результат INV-0004 отдельным Epic.

Оркестратор применяет обычный feature или bug intake и его approval. Только после утверждения Backlog Epic получает `Research: INV-0004`, а INV — `outcome: promoted` и ссылку `EPIC-NNN`.

При подготовке Epic planner читает INV, проверяет его baseline и изменения relevant paths. Если контекст актуален, planner использует уже установленную причину, риски и предложенные проверки вместо повторного полного profiling. Plan и TASK сохраняют `research_refs: [INV-0004]`.

## Investigate and fix directly

> **Пользователь:** Исследуй эту проблему и сам исправь её.

Этот запрос разрешает `research_and_fix` для исследуемой проблемы. После подтверждения причины основной агент сам меняет production code и tests, не создаёт TASK и не вызывает implementer, reviewer или tester. Он выполняет proportionate verification и заполняет `Direct Fix`:

- added, modified и removed paths;
- что и зачем изменено;
- material effects;
- точные команды и результаты;
- оставшиеся риски;
- final revision/commit или scoped-diff fingerprint.

Только полный проверенный результат получает `outcome: fixed_directly`. Частичное или непроверенное изменение остаётся явно неполным. INV не меняет lifecycle существующего Epic/TASK, не означает acceptance и не разрешает commit автоматически.
