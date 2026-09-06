---
name: forge-migrate-framework
description: Use when a consumer repository already contains an older AI Development Forge bundle and a newer release is staged at `.ai-next/`, including legacy installations without a lock.
---

# Migrate the Framework

The Python automation bundle `.ai/tools/` is framework-owned. Preserve project-owned `.ai/local/` caches/logs/metrics and unknown lock fields; exclude local artifacts from render inputs. Do not install Python, enable command reuse, or create bounded Task Start grants implicitly. Use the deterministic preview/apply flow after the framework replacement when available. Incompatible legacy fingerprints require fresh evidence, not relabeling. Preserve and report retired generated outputs for a separately reviewed removal. Keep existing runtime settings and manual workflow support.

## Establish a recoverable baseline

1. Read `.ai-next/MIGRATE.md` in full and verify that active `.ai/` and staged `.ai-next/` are distinct, complete bundles.
2. Inspect both manifests, investigation, integration and mutation-testing contracts, the optional old lock, project configuration, custom overlays, optional project-owned `investigations/`, `.ai/integrations/`, `quality/mutation-testing/`, project-owned consumers, Git state, root routers, local adapters, canonical documents, ADRs, and execution state.
3. Support a legacy installation without `.ai/framework.lock`. Use the old bundle, known legacy IDs, content comparison, Git history, and explicit user decisions as evidence.
4. Hash canonical, execution, product, and unrelated project paths before any write.
5. Identify a recoverable rollback source. Stop if the old bundle and affected adapters cannot be restored.
6. Classify integrations offline as absent, current-supported, older-migratable, malformed, unsupported-future, custom-profile, or ownership collision. Invoke no connector. Absence is the clean baseline; malformed/future/custom/offline entries block only their consumers, while ownership or safety collisions block migration.
7. For a pre-v4 project, inspect every planned/active/paused workspace, quality configuration, Epic Verification Plans, Epic Fuzzing Plans, Task affected/risk/verification fields including fuzzing impact and Task smoke, delivery track and matching assurance evidence, Review Packets, and Epic Validation fingerprints. Treat missing fields, an invalid `execution/planned/` mapping, and any Epic already in `FUZZING` or `AWAITING EPIC ACCEPTANCE` without current validation as compatibility findings. Missing legacy delivery track means standard; never synthesize fast eligibility or assurance for planned, active, reviewed, testing, or awaiting-acceptance TASKs.
8. Inspect `role_execution.mode`. If it is absent, show the old effective routing and require the user to choose one supported value. Offer `claude_with_codex` only as the compatibility-preserving suggestion for a 4.2 project; for an OpenCode-led project with no approved route, offer the existing `native_subagents` value by default. Never write a suggestion without approval, add a new mode, or silently replace an approved value.
9. Inspect `platforms.opencode.enabled`, explicit OpenCode tier mappings, `opencode.json`, and `.opencode/`. Preserve a disabled choice. Enabled OpenCode requires non-empty user-supplied or locally evidenced `provider/model-id` values for all three tiers; never invent, install, authenticate, or configure a provider.

Never modify canonical documents, canonical schema, ADRs, execution state, project investigations, project integrations, project mutation history, project code, tests, data, or unrelated configuration during the framework-upgrade transaction.

## Classify routers and adapters

1. Split `AGENTS.md` and `CLAUDE.md` into project-owned context and legacy Forge instructions. OpenCode shares `AGENTS.md`; do not invent an OpenCode-only router. Include any existing shared, Codex-only, and Claude-only custom router overlays as migration inputs. Check project-owned statements against canonical state, especially `BACKLOG.md`, and report contradictions without changing canonical files.
2. Merge the preserved project-owned context from both routers and all legacy overlays into one `.ai/custom/router-shared.md`. If any inputs disagree, show the conflict and require an explicit user decision; do not silently prefer either platform. Back up legacy platform-specific overlays and remove them only within the approved migration scope after their preserved content is present in the shared overlay.
3. Derive the new managed adapter membership from the staged manifest IDs.
4. Preserve native `epic-planner` and `reviewer` agents on Codex and Claude and, when enabled, OpenCode while adding both staged external launchers (`.claude/forge/codex-role-runner.mjs` and `.codex/forge/claude-role-runner.mjs`) and the unchanged three-mode route metadata. OpenCode reuses `.agents/skills/`; generate no `.opencode/skills/`. Do not install, authenticate, preflight, or invoke Codex, Claude, OpenCode, or a model provider during migration. External-mode unavailability is a runtime blocker, not a migration fallback; `native_subagents` is the explicit dependency-free choice and the default proposal for an OpenCode-led project with no approved route.
5. Recognize legacy Forge agents and skills from the old bundle, old hashes when present, known IDs, and content comparison.
6. Preserve unlisted agents, skills, platform configuration, settings, commands, hooks, `opencode.json`, OpenCode commands/plugins/skills/unlisted agents, and unknown files.
7. Preserve project-owned `investigations/`, integration consumer skills, and `quality/mutation-testing/` history as unlisted project state. Treat an incompatible investigation layout, ambiguous obsolete path, or same-ID custom entry as a collision; do not delete it by inference.

## Preview and authorize

Show one complete diff containing framework replacements, recognized obsolete Forge paths, shared-overlay extraction, final `AGENTS.md` rendering, the exact `CLAUDE.md` import, adapter additions/replacements including `forge-investigate`, `mutation-runner`, `mutation-analyzer`, and `forge-mutation-test`, preserved investigations, files and mutation history, collisions, protected hashes, the explicit role-execution choice, default or overridden model/configuration decisions, rollback source, and the offline integration compatibility matrix.

Framework upgrade and project integration-schema migration are separate gates. A supported framework upgrade may proceed while an older integration remains unmigrated or a malformed/future/custom integration is preserved but unavailable to core consumers. Do not include any project-owned integration rewrite in the framework diff.

Report canonical schema differences only as compatibility findings outside migration scope. Do not infer approved planning from a `PLANNED` Backlog row, create `execution/planned/`, or move any existing execution workspace during migration. A pre-v4 planned, active, or paused plan requires a later explicit compatibility diff through `forge-resume-development`; an Epic may not continue through fuzzing or Epic Acceptance without current v4 Epic Validation evidence. Request explicit approval for the exact framework, router, managed-adapter, and project quality-configuration changes. Approval does not authorize canonical or execution edits, product changes, commits, or pushes.

An already-started legacy TASK remains standard. A pre-start standard-to-fast change requires Replan and complete fast evidence; standard-to-fast after Task Start is forbidden. Do not convert standard review/testing evidence into a Fast Assurance Summary.

## Apply with backup

After approval:

1. back up active `.ai/`, root routers, every affected adapter entry, the old lock, exact optional `investigations/`, integration, and `quality/mutation-testing/` bytes;
2. build a candidate `.ai/` from the staged release plus approved project configuration, including `role_execution.mode`, and the shared overlay while preserving `investigations/`, `.ai/integrations/`, and `quality/mutation-testing/` byte-for-byte; do not create investigation or mutation history when absent and do not install a mutation backend;
3. render the full root `AGENTS.md` from its current template plus the shared overlay, and render root `CLAUDE.md` exactly as `@AGENTS.md`;
4. invoke `forge-sync-adapters` to replace recognized Forge IDs and install the manifest-declared local set on every enabled platform while preserving unlisted files;
5. replace the active bundle and every enabled staged adapter output as one logical operation;
6. run `forge-check-framework`, compare all protected-path hashes, and verify investigation, integration, and mutation history are unchanged and not included in managed-output lock hashes;
7. create or update `.ai/framework.lock` only after every check passes;
8. remove `.ai-next/` only after success and retain the backup until user acknowledgement.

On any failure, restore the old bundle, project configuration including its prior role-execution and OpenCode model representation, routers, all adapter sets, both launchers, lock, exact project-owned investigation and integration state, and exact mutation history, then verify protected hashes again and report the failed stage. Remove only OpenCode files proven by the prior lock to be Forge-managed. Create no report Markdown file and require no framework CLI.

## Migrate an integration schema separately

Only after the framework transaction is valid, offer deterministic `older_migratable` transformations as a separate project-owned change. Show the exact definition/state/canonical-reference diff, supported version transition, consumer impact, backup and rollback source. After explicit approval, stage all related files, validate schemas and bidirectional references offline, and apply atomically. On failure restore the complete pre-migration representation without disturbing the installed framework.

Never downgrade `unsupported_future` content. Framework rollback retains integrations and chooses a mutually supported saved representation before re-enabling affected consumers; otherwise report a scoped compatibility blocker. Never delete external identities or canonical work as rollback cleanup.
