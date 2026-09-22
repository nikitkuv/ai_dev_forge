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

## Рекомендуемый вариант: `.ai-next/` в проекте, миграцией управляет агент

Отдельный постоянный клон Forge не нужен. Из корня обновляемого проекта выполните подходящий PowerShell- или POSIX-блок из раздела [«Подготовить `.ai-next/`»](#подготовить-ai-next). Он создаёт временный sparse clone, копирует только release bundle в `.ai-next/` и удаляет временный клон.

После этого откройте обновляемый проект в Codex, Claude Code или OpenCode и отправьте:

```text
Прочитай .ai-next\MIGRATE.md и сам проведи миграцию Forge в этом проекте.
Сам запусти preview, спроси только необходимые решения и финальное подтверждение,
после подтверждения сам примени миграцию. Не проси меня переносить preview_token или собирать команды.
```

Этого запроса достаточно, чтобы агент:

1. проверил версии активного и staged bundle;
2. запустил read-only preview и объяснил изменения обычным языком;
3. запросил только содержательные решения, если они действительно нужны;
4. показал итоговый scope для одного финального подтверждения;
5. сам передал сохранённый `preview_token` в apply, выполнил проверку и сообщил результат.

Пользователь не копирует token, не собирает `--set`/`--router-shared`/`--approve-collision` и не вычитывает JSON команды. Эти детали обслуживает агент. Ручной режим ниже нужен для CI, диагностики или осознанного самостоятельного запуска.

## Подготовить `.ai-next/`

Запускайте команды из корня мигрируемого проекта. Убедитесь, что старая `.ai/` существует, сохраните текущее состояние в Git или сделайте резервную копию. Если `.ai-next/` уже существует, не перезаписывайте её: удалите или переименуйте только после проверки её происхождения. Нужен Python 3.11+ с зависимостями из `.ai-next/tools/requirements.txt`; например, интерпретатор из `.forge-venv` проекта.

### Из существующего локального клона

Скопируйте `.ai/` нового релиза в мигрируемый проект под именем `.ai-next/` (без `project.yaml`, `custom/`, `local/` и `framework.lock`, которых в релизном bundle нет). Старая `.ai/` должна остаться на месте. После копирования передайте работу агенту по сценарию выше.

### Напрямую из GitHub `main` без отдельного клона

Скрипт использует временный sparse clone и кладёт bundle в `.ai-next/` текущего проекта. После завершения отдельного клона на диске не остаётся; preview и apply выполнит агент.

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
```

Sparse checkout загружает рабочую копию только папки `.ai/`; временный Git-каталог создаётся за пределами проекта и удаляется после копирования. В проекте остаётся готовая `.ai-next/`, после чего можно сразу передавать миграцию агенту.

## Продолжение в ручном режиме

Этот раздел нужен только если вы сознательно не передали миграцию агенту. Запустите `python .ai-next/tools/forge.py migrate --diff`, затем:

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
