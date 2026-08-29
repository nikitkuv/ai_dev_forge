import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

function route(mode, active) {
  if (mode === "native_subagents" && ["codex", "claude"].includes(active)) return { provider: "native", blocked: false };
  if (mode === "claude_with_codex") return active === "claude" ? { provider: "codex-plugin-cc", blocked: false } : { blocked: true, reason: "active-orchestrator mismatch" };
  if (mode === "codex_with_claude") return active === "codex" ? { provider: "claude-code-cli", blocked: false } : { blocked: true, reason: "active-orchestrator mismatch" };
  return { blocked: true, reason: "invalid role_execution.mode" };
}

test("route matrix covers all supported mode and orchestrator combinations", () => {
  assert.deepEqual(route("claude_with_codex", "claude"), { provider: "codex-plugin-cc", blocked: false });
  assert.equal(route("claude_with_codex", "codex").blocked, true);
  assert.deepEqual(route("codex_with_claude", "codex"), { provider: "claude-code-cli", blocked: false });
  assert.equal(route("codex_with_claude", "claude").blocked, true);
  assert.deepEqual(route("native_subagents", "codex"), { provider: "native", blocked: false });
  assert.deepEqual(route("native_subagents", "claude"), { provider: "native", blocked: false });
  assert.equal(route(undefined, "codex").blocked, true);
  assert.equal(route("auto", "claude").blocked, true);
});

test("planner and reviewer use one exact assignment across every route", async () => {
  const [planner, reviewer, plannerRole, reviewerRole] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/framework/agents/epic-planner.yaml"),
    read(".ai/framework/agents/reviewer.yaml")
  ]);
  assert.match(planner, /one assignment from the complete neutral/i);
  assert.match(planner, /canonical, repository, CI, quality-configuration/);
  assert.match(reviewer, /one prompt from the complete neutral/i);
  assert.match(reviewer, /exact Review Packet/);
  assert.match(plannerRole, /spawn_policy: forbidden/);
  assert.match(reviewerRole, /spawn_policy: forbidden/);
});

test("generation and migration retain both launchers and all native agents", async () => {
  const [generation, sync, migration, validation] = await Promise.all([
    read(".ai/05-create-platform-adapters.md"),
    read(".ai/framework/skills/forge-sync-adapters/SKILL.md"),
    read(".ai/framework/skills/forge-migrate-framework/SKILL.md"),
    read(".ai/06-final-validation.md")
  ]);
  for (const source of [generation, sync, migration, validation]) {
    assert.match(source, /codex-role-runner\.mjs/);
    assert.match(source, /claude-role-runner\.mjs/);
    assert.match(source, /native/i);
  }
  assert.match(migration, /compatibility-preserving suggestion/);
  assert.match(migration, /never write it without approval/);
  assert.match(validation, /No route implicitly falls back/);
});

test("canonical router contains the complete no-fallback matrix and Claude imports it", async () => {
  const [codex, claude] = await Promise.all([
    read(".ai/templates/adapters/codex/AGENTS.md"),
    read(".ai/templates/adapters/claude/CLAUDE.md")
  ]);
  assert.equal(claude.trim(), "@AGENTS.md");
  for (const mode of ["claude_with_codex", "codex_with_claude", "native_subagents"]) assert.match(codex, new RegExp(mode));
  assert.match(codex, /There is no fallback/);
  assert.match(codex, /active-orchestrator mismatch/);
});
