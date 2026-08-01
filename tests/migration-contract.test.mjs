import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";


const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(resolve(ROOT, path), "utf8");
}

test("repository has one payload and both migration entrypoints", () => {
  assert.equal(existsSync(resolve(ROOT, ".ai/MIGRATE.md")), true);
  assert.equal(existsSync(resolve(ROOT, "MIGRATION.md")), true);
  assert.equal(existsSync(resolve(ROOT, ".ai-next")), false);
  assert.equal(existsSync(resolve(ROOT, ".ai-migration")), false);
});

test("migration contract freezes project state", () => {
  const text = read(".ai/MIGRATE.md");
  for (const value of [
    "SPEC.md",
    "ARCHITECTURE.md",
    "BACKLOG.md",
    "DECISIONS.md",
    "decisions/",
    "execution/",
    "project source code",
    "tests",
    "canonical schema",
  ]) {
    assert.match(text, new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(text, /read-only/);
  assert.match(text, /rollback/);
});

test("user guide stages GitHub main as .ai-next", () => {
  const text = read("MIGRATION.md");
  assert.match(text, /https:\/\/github\.com\/nikitkuv\/ai_dev_forge\.git/);
  assert.match(text, /--branch main/);
  assert.match(text, /sparse-checkout set \.ai/);
  assert.match(text, /\.ai-next/);
  assert.match(text, /Read \.ai-next\/MIGRATE\.md/);
});

test("router templates consume durable project overlays", () => {
  const codex = read(".ai/templates/adapters/codex/AGENTS.md");
  const claude = read(".ai/templates/adapters/claude/CLAUDE.md");
  assert.match(codex, /\{\{ custom\.router_shared \}\}/);
  assert.match(claude, /\{\{ custom\.router_shared \}\}/);
  assert.match(codex, /\{\{ custom\.codex_router \}\}/);
  assert.match(claude, /\{\{ custom\.claude_router \}\}/);
});

test("adapter contract is ID-scoped and local", () => {
  const combined = [
    ".ai/framework/manifest.yaml",
    ".ai/05-create-platform-adapters.md",
    ".ai/framework/skills/forge-sync-adapters/SKILL.md",
  ].map(read).join("\n");

  for (const value of [
    ".codex/agents/",
    ".agents/skills/",
    ".claude/agents/",
    ".claude/skills/",
  ]) {
    assert.match(combined, new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }

  assert.match(combined, /preserve/i);
  assert.match(combined, /unlisted/i);
  assert.doesNotMatch(combined, /exactly seven/i);
  assert.doesNotMatch(combined, /exactly fourteen/i);
});

test("legacy migration uses .ai-next and never edits canonical schema", () => {
  const text = read(".ai/framework/skills/forge-migrate-framework/SKILL.md");
  assert.match(text, /\.ai-next\//);
  assert.match(text, /without `\.ai\/framework\.lock`/);
  assert.match(text, /Never modify canonical/);
  assert.doesNotMatch(text, /apply separately approved canonical changes/);
});

test("conformance allows project-owned adapter extensions", () => {
  const combined = [
    ".ai/framework/skills/forge-check-framework/SKILL.md",
    ".ai/06-final-validation.md",
  ].map(read).join("\n").toLowerCase();

  assert.match(combined, /manifest-declared/);
  assert.match(combined, /additional project-owned/);
  assert.doesNotMatch(combined, /seven `\.codex/);
  assert.doesNotMatch(combined, /fourteen `\.agents/);
});
