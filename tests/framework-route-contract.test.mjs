import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("manifest declares fixed Codex routes with native fallback agents", async () => {
  const manifest = await read(".ai/framework/manifest.yaml");
  assert.match(manifest, /version: 4\.1\.0/);
  for (const role of ["epic-planner", "reviewer"]) {
    assert.match(manifest, new RegExp(`${role}:\\n    provider: codex-plugin-cc[\\s\\S]*?minimum_plugin_version: 1\\.0\\.6[\\s\\S]*?model: gpt-5\\.6-sol[\\s\\S]*?reasoning_effort: high[\\s\\S]*?fallback_agent: ${role}`));
  }
});

test("root routers remain byte-identical and document both provider paths", async () => {
  const [claude, codex] = await Promise.all([
    read(".ai/templates/adapters/claude/CLAUDE.md"),
    read(".ai/templates/adapters/codex/AGENTS.md")
  ]);
  assert.equal(claude, codex);
  assert.match(claude, /codex@openai-codex/);
  assert.match(claude, /never switch providers mid-attempt/);
});

test("workflow skills preserve native fallback and post-start fail-closed handling", async () => {
  const [planner, reviewer, preparation] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/04-prepare-workspace.md")
  ]);
  for (const source of [planner, reviewer, preparation]) {
    assert.match(source, /preflight/i);
  }
  assert.match(planner, /fallback/i);
  assert.match(reviewer, /fallback/i);
  assert.match(preparation, /falling back/i);
  assert.match(planner, /never falls back/);
  assert.match(reviewer, /never falls back/);
});

test("workflow contracts gate planner and reviewer results before lifecycle changes", async () => {
  const [planner, reviewer] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/skills/forge-run-task/SKILL.md")
  ]);
  assert.match(planner, /malformed result blocks planning/i);
  assert.match(planner, /independently verify the proposal/i);
  assert.match(reviewer, /malformed output.*blocks review/i);
  assert.match(reviewer, /If review finds anything actionable/i);
});
