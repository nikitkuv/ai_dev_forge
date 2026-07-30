---
name: forge-migrate-framework
description: Migrate an initialized project to a newly copied AI Development Forge bundle while preserving project-owned files, previewing destructive changes, regenerating both adapters, validating the result, and rolling back on failure.
---

# Migrate the Framework

## Establish a recoverable baseline

1. Read the new `.ai/framework/manifest.yaml`, existing `.ai/framework.lock`, `.ai/project.yaml`, `.ai/custom/`, Git status, canonical documents, and generated adapter hashes.
2. Identify the prior framework version and a recoverable pre-copy baseline from Git or an explicit backup. If the old framework-owned content cannot be recovered, disclose the rollback limitation before any change.
3. Classify paths as framework-owned, project-owned, or generated adapter outputs.
4. Detect:
   - changed and obsolete framework-owned paths;
   - project changes that collide with the new bundle;
   - manual edits in generated adapters;
   - canonical schema changes requiring user action;
   - model mapping or platform compatibility gaps.

Never overwrite project-owned canonical documents, `.ai/project.yaml`, `.ai/framework.lock`, or `.ai/custom/` as framework content.

## Preview and authorize

1. Show a complete migration diff: replacements, deletions, adapter regeneration, collisions, canonical schema changes, and rollback source.
2. Separate required framework migration from optional canonical document edits.
3. Request explicit user confirmation before overwriting, deleting, moving, or regenerating files.
4. Require a separate diff and approval for canonical schema changes.

## Apply with backup

After approval:

1. create a temporary backup of every affected target, including recoverable prior framework files and current generated adapters;
2. apply only approved framework-owned replacements and obsolete-file removals;
3. preserve project-owned files and custom overlays;
4. invoke `forge-sync-adapters` to regenerate Codex and Claude outputs together;
5. apply separately approved canonical changes;
6. run `forge-check-framework`.

Update `.ai/framework.lock` only after every migration validation passes. Record framework version, source hashes, generated adapter hashes, and ownership data needed for later collision detection.

On any failure, restore the backup, restore the previous lock, and report the failed stage. Remove the temporary backup only after successful validation and user acknowledgement. Do not require a framework CLI, install tools, or create a migration report Markdown file.
