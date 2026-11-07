import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("project rules are declared with checkable patterns and human statements", async () => {
  const [contracts, template, conventions] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/templates/rules.yaml"),
    read(".ai/CONVENTIONS.md")
  ]);

  assert.match(contracts, /project_rules:/);
  assert.match(contracts, /rule_fields: \[id, statement, pattern, scope, exclusions, kind\]/);
  assert.match(contracts, /pattern_syntax: python_re/);
  assert.match(contracts, /statement_authorship: human_authored/);
  assert.match(contracts, /patterns_rendered_into_router: false/);
  assert.match(contracts, /unverifiable_rule: judgment/);
  assert.match(contracts, /drift_check: forge\.py rules/);
  assert.match(contracts, /drift_never_blocks_on_raw_matches: true/);
  assert.match(contracts, /violated_rule_dispositions: \[fix_code, amend_rule, narrow_scope\]/);
  assert.match(template, /\.ai\/custom\/rules\.yaml/);
  assert.match(template, /schema_version: 1/);
  assert.match(conventions, /\.ai\/custom\/rules\.yaml/);
  assert.match(conventions, /project-owned/i);
});

test("rule statements render into the router while patterns stay out", async () => {
  const [router, adapters, contracts] = await Promise.all([
    read(".ai/templates/adapters/codex/AGENTS.md"),
    read(".ai/tools/forge_adapters.py"),
    read(".ai/framework/contracts.yaml")
  ]);

  assert.match(router, /custom\.rules_block/);
  assert.match(adapters, /rules_block/);
  assert.match(adapters, /rules_statement_block/);
  assert.match(contracts, /statement_rendering: compact_Project_Rules_block_in_the_router/);
});

test("drift checking is deterministic, report-only, and keeps judgment fields", async () => {
  const [core, skill, cli] = await Promise.all([
    read(".ai/tools/forge_core.py"),
    read(".ai/framework/skills/forge-check-framework/SKILL.md"),
    read(".ai/tools/forge.py")
  ]);

  assert.match(core, /def rules_check\(/);
  assert.match(core, /def rules_statement_block\(/);
  assert.match(core, /def router_rule_statements\(/);
  assert.match(cli, /"rules"/);
  assert.match(skill, /drift/i);
  assert.match(skill, /judgment/i);
  assert.match(skill, /fix(?:ing)? the code or amend(?:ing)? the rule/i);
});
