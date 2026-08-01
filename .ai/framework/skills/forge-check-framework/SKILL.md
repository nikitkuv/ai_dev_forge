---
name: forge-check-framework
description: Use after bootstrap, resume, adapter synchronization, framework upgrade, or suspected lifecycle and ownership inconsistencies in an initialized Forge project.
---

# Check Framework Conformance

## Read authoritative inputs

Read the manifest, contracts, project configuration, framework lock, custom overlays, canonical documents, ADRs, execution tree, neutral agent and skill sources, generated adapters, and Git state.

Do not repair files during this check.

## Validate structure and ownership

- Verify required framework-owned files and project-owned state exist.
- Detect obsolete framework-owned paths, unexpected overwrites, generated adapter edits, and ownership collisions.
- Verify both platform adapters were generated from the same source hashes and project configuration.
- Verify every manifest-declared agent and skill exists on both platforms with matching IDs, tiers, role boundaries, and concrete model mappings.
- Permit additional project-owned agents and skills; verify they and other unlisted platform files are excluded from Forge ownership and remain unchanged.
- Verify structured router overlays render into their intended routers without copying legacy framework instructions.
- Verify root `AGENTS.md` and `CLAUDE.md` are each no more than 150 lines.
- Verify the framework did not create default hooks, MCP configuration, or CLI dependencies.

## Validate canonical and lifecycle state

- Check required frontmatter, approved-document placeholders, global unique IDs, max-plus-one allocation, links, and ADR index parity.
- Check all enum values and transitions against `.ai/framework/contracts.yaml`.
- Check at most one `ACTIVE` Epic and one code-writing TASK in progress.
- Check Backlog Epic state matches `execution/active`, `paused`, or `completed`.
- Check Task state exists only in its TASK file and Epic priority/readiness/status only in `BACKLOG.md`.
- Check plan Task order matches existing TASK files without storing Task status.
- Check SPEC and ARCHITECTURE contain target state, not execution tracking.
- Check review/testing fingerprints match current implementation and fuzzing evidence is current after code changes.
- Check the current gate can be reconstructed without session history.

## Report

Return a concise pass/fail summary and actionable findings with severity, exact paths, violated invariant, and safe next gate. Distinguish blockers from warnings.

Create no conformance or validation report file, change no status, regenerate no adapter, and delete nothing. Route repairs through the relevant skill and explicit user approval.
