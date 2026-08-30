import assert from "node:assert/strict";
import test from "node:test";
import { readFile, readdir } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

const declaredIds = (manifest) => {
  const match = manifest.match(/subagents: \[([^\]]+)\]/);
  assert.ok(match, "manifest subagents list must exist");
  return match[1].split(",").map((id) => id.trim());
};

const validOpenCodeModel = (value) =>
  typeof value === "string" && /^[^/\s]+\/[^/\s]+$/.test(value);

test("manifest and project template declare OpenCode without adding a route mode", async () => {
  const [manifest, project] = await Promise.all([
    read(".ai/framework/manifest.yaml"),
    read(".ai/templates/project.yaml")
  ]);

  assert.match(manifest, /version: 4\.7\.0/);
  assert.match(manifest, /adapters: \[codex, claude, opencode\]/);
  assert.match(manifest, /- \.opencode\/agents\//);
  assert.match(manifest, /opencode_default_when_primary: true/);
  assert.match(project, /opencode:\n    enabled: true/);
  assert.match(project, /opencode:\n    strong: \{model: null\}\n    balanced: \{model: null\}\n    fast: \{model: null\}/);
  assert.match(project, /provider\/model-id form/);

  const modes = manifest.match(/supported_modes: \[([^\]]+)\]/)?.[1]
    .split(",").map((mode) => mode.trim());
  assert.deepEqual(modes, ["claude_with_codex", "codex_with_claude", "native_subagents"]);
  assert.equal(validOpenCodeModel("openai/gpt-5"), true);
  for (const invalid of [null, "", "gpt-5", "openai/", "/gpt-5", "a/b/c"]) {
    assert.equal(validOpenCodeModel(invalid), false);
  }
});

test("OpenCode template renders every neutral agent through deterministic boundaries", async () => {
  const [manifest, template] = await Promise.all([
    read(".ai/framework/manifest.yaml"),
    read(".ai/templates/adapters/opencode/agent.md")
  ]);
  const ids = declaredIds(manifest);
  const files = (await readdir(new URL("../.ai/framework/agents/", import.meta.url)))
    .filter((name) => name.endsWith(".yaml"));

  assert.equal(ids.length, 11);
  assert.deepEqual(files.map((name) => name.replace(/\.yaml$/, "")).sort(), [...ids].sort());
  assert.ok(template.startsWith("---\n"));
  assert.match(template, /mode: subagent/);
  assert.match(template, /models\.opencode\[agent\.model_tier\]\.model/);
  assert.match(template, /agent\.write_policy\.mode == 'assigned_scope'/);
  assert.match(template, /'Bash' in agent\.claude_tools/);
  assert.match(template, /'WebFetch' in agent\.claude_tools/);
  assert.match(template, /'WebSearch' in agent\.claude_tools/);
  for (const denied of ["external_directory", "task", "skill", "todowrite"]) {
    assert.match(template, new RegExp(`${denied}: deny`));
  }

  for (const id of ids) {
    const source = await read(`.ai/framework/agents/${id}.yaml`);
    const writeMode = source.match(/write_policy:\r?\n  mode: ([^\r\n]+)/)?.[1];
    const tools = source.match(/claude_tools: \[([^\]]*)\]/)?.[1] ?? "";
    assert.ok(writeMode, `${id} must declare a write mode`);
    assert.equal(writeMode === "assigned_scope", id === "implementer", `${id} edit boundary`);
    assert.equal(/WebFetch|WebSearch/.test(tools), id === "documentation-researcher", `${id} network boundary`);
    assert.match(source, /spawn_policy: forbidden/, `${id} must forbid spawning`);
  }
});

test("generation, validation, and migration preserve shared and project-owned OpenCode files", async () => {
  const [generation, sync, check, validation, migrate, conventions] = await Promise.all([
    read(".ai/05-create-platform-adapters.md"),
    read(".ai/framework/skills/forge-sync-adapters/SKILL.md"),
    read(".ai/framework/skills/forge-check-framework/SKILL.md"),
    read(".ai/06-final-validation.md"),
    read(".ai/MIGRATE.md"),
    read(".ai/CONVENTIONS.md")
  ]);

  for (const source of [generation, sync, check, validation, migrate, conventions]) {
    assert.match(source, /\.opencode\/agents\//);
    assert.match(source, /\.agents\/skills\//);
  }
  assert.match(generation, /Do not create an OpenCode-only router/);
  assert.match(generation, /copy skills into `\.opencode\/skills\/`/);
  assert.match(generation, /If any enabled platform fails, replace none/);
  assert.match(sync, /restore all adapter sets on failure/);
  assert.match(check, /only implementer permits edits/i);
  assert.match(validation, /provider-qualified `provider\/model-id`/i);
  assert.match(migrate, /Remove only OpenCode files proven by the prior lock to be Forge-managed/);
  for (const protectedName of ["opencode.json", "commands", "plugins", "skills", "unlisted"]) {
    assert.match(`${generation}\n${sync}\n${validation}\n${migrate}`, new RegExp(protectedName, "i"));
  }
});

test("OpenCode-led planning and review default to existing native_subagents with no fallback", async () => {
  const [router, bootstrap, planner, reviewer] = await Promise.all([
    read(".ai/templates/adapters/codex/AGENTS.md"),
    read(".ai/BOOTSTRAP.md"),
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/skills/forge-run-task/SKILL.md")
  ]);

  for (const source of [router, bootstrap, planner, reviewer]) {
    assert.match(source, /OpenCode/);
    assert.match(source, /native_subagents/);
  }
  assert.match(bootstrap, /without adding a mode/);
  assert.match(planner, /adds no mode/);
  assert.match(reviewer, /adds no mode/);
  assert.match(router, /There is no fallback/);
});
