# Миграция AI Development Forge

## Обновление до v4.2

v4.2 добавляет необязательный универсальный registry локальных интеграций и `work_source` intake. Чистый Forge по-прежнему не имеет `.ai/integrations/`, не требует connector runtime и проходит migration по прежнему основному пути.

Если `.ai/integrations/` существует, framework migration сканирует его только offline и сохраняет byte-for-byte. Current definitions продолжают работать; malformed, future-schema и неизвестные custom profiles блокируют только своих consumers. Framework replacement и integration-schema migration имеют разные preview, approval, backup и rollback.

Project-owned definitions/state не включаются в managed-output hashes. Изменение board, knowledge source, dataset или analysis service не считается framework drift и само по себе не требует adapter sync.

## Совместимость v4.1

v4.1 добавляет необязательный preferred route для Claude Code: `epic-planner` и `reviewer` могут выполняться через установленный `openai/codex-plugin-cc` с `gpt-5.6-sol/high`. Миграция сохраняет оба native Claude agent-файла как fallback, не устанавливает плагин и не выполняет login автоматически. После adapter sync проверьте `/codex:setup`; при недоступности runtime workflow продолжит работу через текущих Claude subagents.

Минимальная проверенная версия плагина — `1.0.6`. Для отката удалите managed launcher и preferred-route metadata при следующем adapter sync; native Claude agents остаются рабочими без плагина.

Эта инструкция обновляет проект, где уже используется старая версия Forge. Канонические документы, `.ai/integrations/`, project-owned consumers, `decisions/`, `execution/`, код и тесты проекта не изменяются framework-транзакцией.

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

`AGENTS.md` и `CLAUDE.md` получают новые framework-инструкции, сохраняя описание, карту и правила проекта. Старые Forge agents и skills заменяются новыми локальными версиями; посторонние пользовательские файлы сохраняются.

При переходе на v4 добавляются `epic-planner`, `epic-validator`, lifecycle state `VALIDATING`, selective Task testing, обязательный Review Packet, quality profiles и полный Epic Validation перед fuzzing. Миграция фреймворка не переписывает существующие plan/TASK-файлы автоматически.

Для проекта с work-source links она отдельно проверяет совместимость Backlog `Sources`, TASK `external_sources`, Epic coverage matrix и reverse provenance, но не исправляет их без отдельного canonical/Replan или integration-schema approval.

## Перед началом

Запускайте команды из корня мигрируемого проекта. Убедитесь, что старая `.ai/` существует, сохраните текущее состояние в Git или сделайте резервную копию. Если `.ai-next/` уже существует, не перезаписывайте её: удалите или переименуйте только после проверки её происхождения.

## Вариант 1: копирование локальной версии

Скопируйте `.ai/` нового релиза в мигрируемый проект под именем `.ai-next/`. Старая `.ai/` должна остаться на месте.

## Вариант 2: последняя версия из GitHub `main`

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

Sparse checkout загружает рабочую копию только папки `.ai/`; временный Git-каталог создаётся за пределами проекта и удаляется после копирования.

## Запуск

Откройте мигрируемый проект в Codex или Claude Code и отправьте:

```text
Read .ai-next/MIGRATE.md and migrate the framework from .ai/ to .ai-next/.
The legacy project may not have .ai/framework.lock.
Do not modify canonical documents, decisions/, execution/, project code, or tests.
Preserve optional .ai/integrations/ and project-owned integration consumers byte-for-byte.
Classify integration compatibility offline and do not invoke connectors.
Preserve project-specific content from AGENTS.md and CLAUDE.md in one shared overlay.
Reconcile it with canonical state from BACKLOG.md and report contradictions without editing BACKLOG.md.
Render final AGENTS.md and CLAUDE.md with byte-identical content.
Replace legacy Forge agents and skills with the bundled local versions.
Show the complete migration diff before writing.
Communicate with me in Russian.
```

Сначала агент работает read-only и показывает полный diff: замену `.ai/`, объединение проектного содержимого routers и legacy platform-specific overlays в shared overlay, два идентичных итоговых router-файла, удаляемые старые Forge adapters, устанавливаемые локальные adapters, integration compatibility matrix, collisions и rollback source. Legacy `.ai/custom/codex-router.md` и `.ai/custom/claude-router.md` удаляются только после backup и явного подтверждения их merge. Противоречия с `BACKLOG.md` агент сообщает, но сам `BACKLOG.md` не изменяет. Ничего не подтверждайте, пока в framework diff присутствует canonical, integration или product path.

Для проекта со старым planned/active/paused Epic агент отдельно покажет compatibility findings: отсутствующие quality profiles, Verification Plans, Review Packets, planned-workspace mapping и Epic Validation evidence. Миграция не создаёт `execution/planned/` из строк Backlog и не перемещает execution-каталоги автоматически. После миграции findings исправляются через `forge-resume-development` и требуемые user gates. Старый Epic в `FUZZING` или `AWAITING EPIC ACCEPTANCE` нельзя завершить, пока полный Epic Validation не пройдёт на текущем aggregate fingerprint.

После подтверждения агент создаёт backup, применяет staged-кандидаты, проверяет защищённые пути и точное сохранение `.ai/integrations/`, и только затем создаёт `.ai/framework.lock`. При ошибке он восстанавливает старую `.ai/`, адаптеры и project-owned integration bytes. После успеха `.ai-next/` удаляется.

Старая поддерживаемая integration schema мигрируется только отдельным действием после framework upgrade: агент показывает exact diff всех definition/state/reference файлов, создаёт recoverable backup, просит отдельное подтверждение, валидирует staged result offline и применяет его атомарно. Ошибка откатывает только integration migration и не ломает установленный Forge. Framework rollback не удаляет external identities или canonical Epic/Task records.
