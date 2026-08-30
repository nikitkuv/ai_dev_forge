# Миграция AI Development Forge

## Обновление до v4.7

v4.7 добавляет OpenCode как третий native adapter. Корневой `AGENTS.md` остаётся единым router для Codex и OpenCode, `.agents/skills/` переиспользуется обеими платформами, а одиннадцать OpenCode subagents генерируются под `.opencode/agents/`. `.opencode/skills/` и отдельный OpenCode router не создаются.

Enum `role_execution.mode` не меняется. Для OpenCode-led migration без утверждённого route предлагается существующий `native_subagents`; значение записывается только после явного approval. Уже утверждённый режим сохраняется, а несовпадение активного оркестратора блокирует planner/reviewer без fallback.

Включённый OpenCode требует три явно подтверждённых model ID в формате `provider/model-id`; provider-independent defaults нет. Migration не устанавливает и не авторизует OpenCode или provider. `opencode.json`, commands, plugins, skills и unlisted agents остаются project-owned. Все enabled adapters заменяются и откатываются атомарно; удалить можно только OpenCode-файлы, чья Forge ownership доказана старым lock.

## Обновление до v4.6

v4.6 вводит ровно два TASK delivery track: `fast` и `standard`. Migration не угадывает fast eligibility по старым risk flags и не синтезирует fast evidence. Любая legacy TASK без `delivery_track`, включая состояния `TODO`, `IN PROGRESS`, `IN REVIEW`, `IN TESTING` и `AWAITING USER ACCEPTANCE`, трактуется как `standard`; уже начатая standard TASK не понижается до fast.

После обновления новые планы и TASK definitions явно фиксируют track, rationale и verification. Fast TASK использует implementer и orchestrator assurance без reviewer/tester; при неопределённости или провале она повышается до standard. Model tier mapping, Task Acceptance, Epic Validation и fuzzing этой миграцией не меняются.

## Обновление до v4.4

v4.4 добавляет независимый `forge-mutation-test`, fast `mutation-runner`, strong `mutation-analyzer` и project-owned историю `quality/mutation-testing/`. Эти возможности не добавляют Epic/TASK transition или quality gate, не требуют mutation backend по умолчанию и не запускаются во время bootstrap, migration, adapter sync или обычной разработки.

Migration устанавливает новые manifest-declared agent/skill adapters, но не устанавливает `mutmut` или другой backend и не создаёт mutation registry. Существующий `quality/mutation-testing/` сохраняется byte-for-byte, не входит в managed-output hashes и восстанавливается при rollback. Отсутствие каталога — clean baseline и не является blocker.

Если старый проект уже имеет собственный файл или skill с ID `mutation-runner`, `mutation-analyzer` или `forge-mutation-test`, migration показывает same-ID collision и ждёт точного решения пользователя. Неизвестные mutation artifacts вне нового project-owned path остаются защищёнными как unrelated project state.

## Обновление до v4.2

v4.2 добавляет необязательный универсальный registry локальных интеграций и `work_source` intake. Чистый Forge по-прежнему не имеет `.ai/integrations/`, не требует connector runtime и проходит migration по прежнему основному пути.

Если `.ai/integrations/` существует, framework migration сканирует его только offline и сохраняет byte-for-byte. Current definitions продолжают работать; malformed, future-schema и неизвестные custom profiles блокируют только своих consumers. Framework replacement и integration-schema migration имеют разные preview, approval, backup и rollback.

Project-owned definitions/state не включаются в managed-output hashes. Изменение board, knowledge source, dataset или analysis service не считается framework drift и само по себе не требует adapter sync.

## Совместимость v4.1

v4.3 заменяет неявный preferred/fallback route явным `role_execution.mode` для обеих ролей. Доступны `claude_with_codex` (Claude Code + `openai/codex-plugin-cc` 1.0.6+), `codex_with_claude` (Codex + Claude Code CLI 2.1.203+ в headless plan mode) и `native_subagents` (внутренние агенты активной платформы).

Для проекта v4.2 миграция показывает прежнее эффективное поведение и предлагает `claude_with_codex` как совместимый вариант, но записывает его только после подтверждения. Она генерирует оба launcher и сохраняет native agents, не устанавливая и не авторизуя внешние runtimes. Недоступный выбранный route блокирует роль без fallback; откат восстанавливает прежнюю конфигурацию, adapters и lock одной транзакцией.

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

`AGENTS.md` получает новые framework-инструкции, сохраняя описание, карту и правила проекта; `CLAUDE.md` заменяется импортом `@AGENTS.md`. Старые Forge agents и skills заменяются новыми локальными версиями; посторонние пользовательские файлы сохраняются.

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
Preserve project-specific content from AGENTS.md and CLAUDE.md in one shared overlay rendered into AGENTS.md.
Reconcile it with canonical state from BACKLOG.md and report contradictions without editing BACKLOG.md.
Render the final AGENTS.md as the full router and CLAUDE.md as the exact `@AGENTS.md` import.
Replace legacy Forge agents and skills with the bundled local versions.
Show the complete migration diff before writing.
Communicate with me in Russian.
```

Сначала агент работает read-only и показывает полный diff: замену `.ai/`, объединение проектного содержимого routers и legacy platform-specific overlays в shared overlay, два идентичных итоговых router-файла, удаляемые старые Forge adapters, устанавливаемые локальные adapters, integration compatibility matrix, collisions и rollback source. Legacy `.ai/custom/codex-router.md` и `.ai/custom/claude-router.md` удаляются только после backup и явного подтверждения их merge. Противоречия с `BACKLOG.md` агент сообщает, но сам `BACKLOG.md` не изменяет. Ничего не подтверждайте, пока в framework diff присутствует canonical, integration или product path.

Для проекта со старым planned/active/paused Epic агент отдельно покажет compatibility findings: отсутствующие quality profiles, Epic Verification Plan, Epic Fuzzing Plan, Task fuzzing impact/smoke, Review Packets, planned-workspace mapping и Epic Validation evidence. Миграция не создаёт `execution/planned/` из строк Backlog и не перемещает execution-каталоги автоматически. После миграции findings исправляются через `forge-resume-development` и требуемые user gates. Старый Epic в `FUZZING` или `AWAITING EPIC ACCEPTANCE` нельзя завершить, пока полный Epic Validation не пройдёт на текущем aggregate fingerprint и fuzzing gate не получит актуальный outcome.

После подтверждения агент создаёт backup, применяет staged-кандидаты, проверяет защищённые пути и точное сохранение `.ai/integrations/`, и только затем создаёт `.ai/framework.lock`. При ошибке он восстанавливает старую `.ai/`, адаптеры и project-owned integration bytes. После успеха `.ai-next/` удаляется.

Старая поддерживаемая integration schema мигрируется только отдельным действием после framework upgrade: агент показывает exact diff всех definition/state/reference файлов, создаёт recoverable backup, просит отдельное подтверждение, валидирует staged result offline и применяет его атомарно. Ошибка откатывает только integration migration и не ломает установленный Forge. Framework rollback не удаляет external identities или canonical Epic/Task records.
