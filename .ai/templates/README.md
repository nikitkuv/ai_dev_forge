# <Product Name>

<Briefly explain what the product does and who it is for. Keep detailed product behavior in `SPEC.md`.>

## Setup

### Prerequisites

- <Required runtime, tool, service, or account and its supported version.>

### Installation

```text
<Reproducible installation commands>
```

### Configuration

1. <Copy or create the local configuration file.>
2. <Set required environment variables or secrets without committing secret values.>

## Run

```text
<Command that starts the product locally>
```

## Test

```text
<Primary command that runs the project test suite>
```

## Project Documentation

- [Product specification](SPEC.md) — target product behavior.
- [Architecture](ARCHITECTURE.md) — target system architecture.
- [Backlog](BACKLOG.md) — Epic priority, readiness, lifecycle, and defects.
- [Decision index](DECISIONS.md) — navigation to authoritative ADR files.
- [Codex and OpenCode instructions](AGENTS.md) — shared project workflow.
- [Claude Code instructions](CLAUDE.md) — Claude Code project workflow.

When this project deliberately configures local capabilities, document the project-owned `.ai/integrations/` definitions and external connector setup here without copying credentials. Omit this guidance for a clean project with no integrations.

This README is operational orientation, not a canonical source for product requirements, architecture, execution status, or architectural decisions. Follow the linked canonical documents when information differs.
