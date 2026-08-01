# Миграция AI Development Forge

Эта инструкция обновляет проект, где уже используется старая версия Forge. Канонические документы, `decisions/`, `execution/`, код и тесты проекта не изменяются.

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
Preserve project-specific content in AGENTS.md and CLAUDE.md.
Replace legacy Forge agents and skills with the bundled local versions.
Show the complete migration diff before writing.
Communicate with me in Russian.
```

Сначала агент работает read-only и показывает полный diff: замену `.ai/`, merge routers, удаляемые старые Forge adapters, устанавливаемые локальные adapters, collisions и rollback source. Ничего не подтверждайте, пока в списке изменений присутствует canonical или product path.

После подтверждения агент создаёт backup, применяет staged-кандидаты, проверяет защищённые пути и только затем создаёт `.ai/framework.lock`. При ошибке он восстанавливает старую `.ai/` и адаптеры. После успеха `.ai-next/` удаляется.
