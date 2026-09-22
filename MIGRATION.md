# Миграция AI Development Forge

Эта инструкция обновляет проект, где уже используется старая версия Forge. Канонические документы, `.ai/integrations/`, `quality/mutation-testing/`, project-owned consumers, `decisions/`, `execution/`, код и тесты проекта не изменяются framework-транзакцией.

## Что получится

До запуска:

```text
.ai/       старая активная версия
.ai-next/  новая версия из этого репозитория
```

После успешной проверки:

```text
.ai/       новая активная версия
```

`AGENTS.md` рендерится из нового шаблона с существующим `.ai/custom/router-shared.md` байт-в-байт; `CLAUDE.md` заменяется импортом `@AGENTS.md`. Адаптеры Forge заменяются новыми локальными версиями; посторонние пользовательские файлы сохраняются. Устаревшие файлы bundle удаляются только при доказанном провенансе (hash в `bundle_state` lock); неизвестные файлы в framework-пространстве сохраняются и показываются advisory-находкой.

Для проекта с work-source links миграция отдельно проверяет совместимость Backlog `Sources`, TASK `external_sources`, Epic coverage matrix и reverse provenance, но не исправляет их без отдельного canonical/Replan или integration-schema approval.

## Рекомендуемый вариант: миграцией управляет агент

Команда миграции остаётся детерминированной и транзакционной, но работать с ней вручную не нужно. Клонируйте или обновите AI Development Forge, откройте **этот клон** в Codex, Claude Code или OpenCode и отправьте короткий запрос с путём к обновляемому проекту:

```text
Обнови AI Development Forge в проекте D:\work\my_project, используя текущий клон Forge.
Прочитай .ai\MIGRATE.md и сам проведи миграцию.
Сам подготовь и проверь .ai-next, спроси только необходимые решения и финальное подтверждение,
после подтверждения сам примени миграцию. Не проси меня переносить preview_token или собирать команды.
```

Для POSIX-систем укажите соответствующий путь к проекту. Можно работать и наоборот: открыть обновляемый проект, указать путь к клону Forge и попросить прочитать `<путь-к-клону>/.ai/MIGRATE.md`. Этого запроса достаточно, чтобы агент:

1. проверил версии активного bundle и указанного клона;
2. сам подготовил `.ai-next/`, не затрагивая активную `.ai/`;
3. запустил read-only preview и объяснил изменения обычным языком;
4. запросил только содержательные решения, если они действительно нужны;
5. показал итоговый scope для одного финального подтверждения;
6. сам передал сохранённый `preview_token` в apply, выполнил проверку и сообщил результат.

Пользователь не копирует token, не собирает `--set`/`--router-shared`/`--approve-collision` и не вычитывает JSON команды. Эти детали обслуживает агент. Ручной режим ниже нужен для CI, диагностики или осознанного самостоятельного запуска.

## Перед ручным запуском

Запускайте команды из корня мигрируемого проекта. Убедитесь, что старая `.ai/` существует, сохраните текущее состояние в Git или сделайте резервную копию. Если `.ai-next/` уже существует, не перезаписывайте её: удалите или переименуйте только после проверки её происхождения. Нужен Python 3.11+ с зависимостями из `.ai-next/tools/requirements.txt`; например, интерпретатор из `.forge-venv` проекта.

## Ручной вариант 1: копирование локальной версии

Скопируйте `.ai/` нового релиза в мигрируемый проект под именем `.ai-next/` (без `project.yaml`, `custom/`, `local/` и `framework.lock`, которых в релизном bundle нет). Старая `.ai/` должна остаться на месте. Затем запустите preview:

```text
python .ai-next/tools/forge.py migrate
```

## Ручной вариант 2: последняя версия из GitHub `main`

Скрипт клонирует bundle, кладёт его в `.ai-next/` и сразу запускает preview миграции.

### PowerShell

```powershell
if (Test-Path -LiteralPath ".ai-next") {
    throw ".ai-next already exists; inspect it before staging another release."
}

$forgeStage = Join-Path $env:TEMP ("ai-dev-forge-" + [guid]::NewGuid())

try {
    git clone `
      --depth 1 `
      --filter=blob:none `
      --sparse `
      --branch main `
      https://github.com/nikitkuv/ai_dev_forge.git `
      $forgeStage

    git -C $forgeStage sparse-checkout set .ai
    Copy-Item -LiteralPath (Join-Path $forgeStage ".ai") -Destination ".ai-next" -Recurse
    python .ai-next/tools/forge.py migrate
}
finally {
    if (Test-Path -LiteralPath $forgeStage) {
        Remove-Item -LiteralPath $forgeStage -Recurse -Force
    }
}
```

### POSIX shell

```sh
test ! -e .ai-next || {
  echo '.ai-next already exists; inspect it before staging another release.' >&2
  exit 1
}

forge_stage="$(mktemp -d)"
trap 'rm -rf -- "$forge_stage"' EXIT

git clone \
  --depth 1 \
  --filter=blob:none \
  --sparse \
  --branch main \
  https://github.com/nikitkuv/ai_dev_forge.git \
  "$forge_stage"

git -C "$forge_stage" sparse-checkout set .ai
cp -R "$forge_stage/.ai" .ai-next
python .ai-next/tools/forge.py migrate
```

Sparse checkout загружает рабочую копию только папки `.ai/`; временный Git-каталог создаётся за пределами проекта и удаляется после копирования. Preview не изменяет репозиторий: он лишь печатает полный план миграции в компактном JSON с `preview_token`.

## Продолжение в ручном режиме

Этот раздел нужен только если вы сознательно не передали миграцию агенту. Preview уже запущен одним из вариантов выше (или повторите `python .ai-next/tools/forge.py migrate --diff`). Дальше:

1. Разберите findings. Блокирующие (`router_extraction_required`, `legacy_overlay_present`, `config_decision_required`, `unexpected_staged_file`, `downgrade_refused`, `already_current`, `render_validation`, `integration_ownership_collision`) требуют решения до apply; глоссарий — в `.ai/tools/USAGE.md`.
2. Для legacy-проекта без `.ai/custom/router-shared.md` один раз вычлените сохраняемый проектный контент старых роутеров в файл и передайте его: `--router-shared <path>`. Альтернатива всему циклу — вызвать скилл `forge-migrate-framework`: он прогонит команды и соберёт решения.
3. Явные решения конфигурации передавайте по одному: `--set role_execution.mode=native_subagents`. Утверждённые значения никогда не перезаписываются молча.
4. Утвердите точный preview и примените тот же токен:

```text
python .ai-next/tools/forge.py migrate --apply PREVIEW_TOKEN \
  [--set key=value ...] [--router-shared path] [--approve-collision path ...]
```

Apply выполняет одну охраняемую транзакцию: backup-журнал, атомарные записи с lock последним, валидация, повторное хэширование защищённых путей и удаление `.ai-next/` только после успеха. Любой провал полностью откатывает репозиторий и сохраняет staged bundle; прерванная транзакция восстанавливается только через `migrate --recover`. Dirty Git tree — warning: recoverable baseline остаётся ответственностью пользователя.

После миграции advisory-находки (например, терминальные строки живого Backlog) исправляются отдельными командами backfill по явному решению. Для проекта со старым planned/active/paused Epic команда отдельно покажет compatibility findings: отсутствующие quality profiles, Epic Verification/Fuzzing Plans, Review Packets, planned-workspace mapping и Epic Validation evidence. Они исправляются через `forge-resume-development` и требуемые user gates; миграция не создаёт `execution/planned/` из строк Backlog и не перемещает execution-каталоги. Старый Epic в `FUZZING` или `AWAITING EPIC ACCEPTANCE` нельзя завершить, пока полный Epic Validation не пройдёт на текущем aggregate fingerprint.

Старая поддерживаемая integration schema мигрируется только отдельным действием после framework upgrade: `older_migratable` classification показывает точный diff, recoverable backup и отдельное подтверждение; ошибка откатывает только integration migration. Framework rollback не удаляет external identities или canonical Epic/Task records.
