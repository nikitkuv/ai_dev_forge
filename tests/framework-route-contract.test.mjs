import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("manifest declares the three role-execution modes and both external routes", async () => {
  const manifest = await read(".ai/framework/manifest.yaml");
  assert.match(manifest, /version: 4\.9\.0/);
  assert.match(manifest, /roles: \[epic-planner, reviewer\]/);
  assert.match(manifest, /supported_modes: \[claude_with_codex, codex_with_claude, native_subagents\]/);
  assert.match(manifest, /fallback: forbidden/);
  assert.match(manifest, /claude_with_codex:[\s\S]*?orchestrator: claude[\s\S]*?provider: codex-cli[\s\S]*?transport: exec[\s\S]*?model: gpt-5\.6-sol[\s\S]*?reasoning_effort: medium/);
  assert.match(manifest, /codex_with_claude:[\s\S]*?orchestrator: codex[\s\S]*?provider: claude-code-cli[\s\S]*?minimum_cli_version: 2\.1\.203[\s\S]*?permission_mode: plan/);
  assert.match(manifest, /native_subagents:[\s\S]*?orchestrator: active_platform[\s\S]*?external_preflight: false[\s\S]*?claude_reasoning_effort: high/);
  assert.match(manifest, /opencode_default_when_primary: true/);
});

test("project template requires an explicit valid role mode", async () => {
  const project = await read(".ai/templates/project.yaml");
  assert.match(project, /schema_version: 2/);
  assert.match(project, /role_execution:\n  mode: null/);
  assert.doesNotMatch(project, /(?:reasoning_effort|effort): high/);
  const valid = new Set(["claude_with_codex", "codex_with_claude", "native_subagents"]);
  for (const mode of valid) assert.equal(valid.has(mode), true);
  for (const mode of [undefined, null, "auto", "claude", "reviewer:codex"]) assert.equal(valid.has(mode), false);
});

test("Claude native subagents use high effort without changing other route defaults", async () => {
  const [agent, project, generation] = await Promise.all([
    read(".ai/templates/adapters/claude/agent.md"),
    read(".ai/templates/project.yaml"),
    read(".ai/05-create-platform-adapters.md")
  ]);
  assert.match(agent, /'high' if role_execution\.mode == 'native_subagents' else/);
  assert.match(project, /claude:\n    strong: \{model: opus, effort: medium\}/);
  assert.match(generation, /`effort: high` for every generated Claude agent when `role_execution\.mode` is `native_subagents`/);
  assert.match(generation, /native-only override does not change the managed `codex_with_claude` route/);
});

test("AGENTS.md is canonical and CLAUDE.md imports it without duplication", async () => {
  const [claude, codex, collector] = await Promise.all([
    read(".ai/templates/adapters/claude/CLAUDE.md"),
    read(".ai/templates/adapters/codex/AGENTS.md"),
    read(".ai/framework/agents/context-collector.yaml")
  ]);
  assert.equal(claude.trim(), "@AGENTS.md");
  assert.match(codex, /codex exec/);
  assert.match(codex, /never copy wrappers into user directories/);
  assert.match(codex, /claude-code-cli|Claude Code 2\.1\.203/);
  assert.match(codex, /There is no fallback/);
  assert.match(codex, /Codex, Claude Code, or OpenCode platform's matching generated agent/);
  assert.match(codex, /OpenCode-led setup[\s\S]*?proposes this existing mode/);
  assert.match(collector, /`AGENTS\.md` as the single complete generated router/);
  assert.match(collector, /`CLAUDE\.md`.*exactly `@AGENTS\.md`/);
  assert.match(collector, /do not require or report byte-for-byte identity between the two files/i);
});

test("workflow skills require explicit routing and prohibit fallback", async () => {
  const [planner, reviewer, preparation] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/04-prepare-workspace.md")
  ]);
  for (const source of [planner, reviewer, preparation]) {
    assert.match(source, /preflight/i);
  }
  for (const source of [planner, reviewer, preparation]) {
    assert.match(source, /role_execution\.mode/);
    assert.match(source, /claude_with_codex/);
    assert.match(source, /codex_with_claude/);
    assert.match(source, /native_subagents/);
    assert.match(source, /no fallback|never fall(?:s)? back/i);
  }
});

test("workflow contracts gate planner and reviewer results before lifecycle changes", async () => {
  const [planner, reviewer] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/skills/forge-run-task/SKILL.md")
  ]);
  assert.match(planner, /malformed result blocks planning/i);
  assert.match(planner, /independently verify the proposal/i);
  assert.match(reviewer, /malformed output.*blocks review/i);
  assert.match(reviewer, /If review finds any production finding/i);
});

test("task review findings are limited to the production surface", async () => {
  const [role, workflow, taskTemplate] = await Promise.all([
    read(".ai/framework/agents/reviewer.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/templates/TASK.md")
  ]);

  assert.match(role, /canonical documents.*reference inputs.*not review targets/is);
  assert.match(role, /must not become an actionable finding.*final outcome/is);
  assert.match(role, /production review paths.*executable production code/is);
  assert.match(role, /supporting evidence, not blocking review targets/i);
  assert.match(workflow, /production_review_paths/);
  assert.match(workflow, /supporting_evidence_paths/);
  assert.match(workflow, /canonical-only issue remains out of contract/i);
  assert.match(taskTemplate, /production_review_paths: \[\]/);
  assert.match(taskTemplate, /supporting_evidence_paths: \[\]/);
});
