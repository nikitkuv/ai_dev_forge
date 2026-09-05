## Why

Forge currently routes investigation and remediation through Backlog, Epic, and TASK workflows. Users need a simpler ad hoc path where the main agent can investigate a concrete codebase problem freely, preserve the result, and then either create normal planned work or fix the problem directly.

## What Changes

- Add a portable `forge-investigate` workflow that runs outside the standard Epic/TASK lifecycle and is performed directly by the main agent without invoking subagents.
- Store every material investigation as one lightweight canonical document under `investigations/` containing the question, scope, evidence, cause, conclusions, and suggested next action.
- Record one simple outcome: `no_action`, `promoted`, `fixed_directly`, or `unresolved`. A promoted result links to normal Bug/Epic work; a direct fix stays inside the investigation when the user authorizes it.
- When the agent fixes the problem directly, require the investigation document to record what was added, modified, or removed, the purpose of each change, commands and checks run, results, limitations, and the final Git/diff reference when available.
- Keep investigation history reusable: later intake or Epic planning can read a referenced or relevant investigation instead of repeating completed research, while still checking that its code context remains applicable.
- Keep existing authority boundaries for product decisions, destructive/external actions, lifecycle state, and commits. An investigation does not automatically create or advance a Bug, Epic, or TASK, and commits still require the project's existing explicit authorization.

## Capabilities

### New Capabilities

- `ad-hoc-investigations`: Defines standalone main-agent investigation, lightweight canonical records, direct fixes, promotion to planned work, and later reuse of research.

### Modified Capabilities

- None.

## Impact

- Adds `investigations/INV-NNNN-<short-name>.md`, an investigation template, and `forge-investigate` to generated Forge projects.
- Extends framework contracts, conventions, manifest ownership, router guidance, bootstrap/migration/validation instructions, intake and planning guidance, maintained documentation, scenarios, and contract tests.
- Does not add a new delivery track, require a subagent, create a parallel TASK lifecycle, or automatically change Backlog state.
