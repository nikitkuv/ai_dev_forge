import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

function analysisDecision({ run, analysisAuthorized, analysisBudget }) {
  if (!analysisAuthorized) return "not_requested";
  if (!run.fingerprintCurrent) return "stale";
  if (run.baseline !== "passed" || ["SETUP REQUIRED", "BLOCKED", "CANCELLED", "INCONCLUSIVE"].includes(run.outcome) || !run.artifactsCurrent) return "blocked";
  const candidates = run.survived + run.noCoverage;
  if (candidates === 0) return "skipped_no_candidates";
  if (analysisBudget <= 0) return "blocked";
  if (run.existingRunId) return "invoke_without_rerun";
  return candidates > analysisBudget ? "invoke_partial" : "invoke";
}

function validateRecord(record) {
  const required = ["schema_version", "id", "started_at", "run", "scope", "fingerprint", "tool", "budget", "baseline", "results", "artifacts", "analysis", "disposition"];
  if (required.some((field) => !(field in record))) return false;
  if (!/^MUT-\d{4,}$/.test(record.id)) return false;
  if (!Array.isArray(record.scope.production_paths) || !Array.isArray(record.scope.test_paths)) return false;
  if (!record.fingerprint.base_revision || !record.fingerprint.scoped_diff_hash) return false;
  for (const key of ["generated", "killed", "survived", "no_coverage", "timeout", "invalid_or_error"]) {
    if (!Number.isInteger(record.results[key]) || record.results[key] < 0) return false;
  }
  if (!record.analysis.authorized && record.analysis.status !== "not_requested") return false;
  if (["completed", "partial"].includes(record.analysis.status) && (!record.analysis.authorized || !record.analysis.source_fingerprint || record.analysis.budget <= 0)) return false;
  if (record.analysis.status === "partial" && record.analysis.remaining_candidates <= 0) return false;
  return true;
}

test("manifest exposes optional mutation capability without a lifecycle route", async () => {
  const [manifest, contracts] = await Promise.all([
    read(".ai/framework/manifest.yaml"),
    read(".ai/framework/contracts.yaml")
  ]);
  assert.match(manifest, /version: 4\.7\.0/);
  assert.match(manifest, /- quality\/mutation-testing\//);
  assert.match(manifest, /- forge-mutation-test/);
  assert.match(manifest, /mutation-runner, mutation-analyzer/);
  assert.match(manifest, /mutation_testing:[\s\S]*?generated_by_default: false[\s\S]*?backend_required_by_default: false/);
  assert.match(contracts, /mutation_testing:[\s\S]*?lifecycle_coupling: forbidden/);
  assert.match(contracts, /default_mode: metrics_only/);
  assert.match(contracts, /automatic_bug_task_epic_or_replan: forbidden/);
  assert.doesNotMatch(contracts, /gates:[\s\S]*?mutation_(?:test|testing|analysis):/);
});

test("project configuration is backend-neutral and creates no default history", async () => {
  const [project, manifest, bootstrap] = await Promise.all([
    read(".ai/templates/project.yaml"),
    read(".ai/framework/manifest.yaml"),
    read(".ai/BOOTSTRAP.md")
  ]);
  assert.match(project, /mutation_testing:\n  backend: null/);
  assert.match(project, /result_adapter: null/);
  assert.match(project, /artifact_policy: compact_only/);
  assert.match(manifest, /backend_required_by_default: false/);
  assert.doesNotMatch(bootstrap, /install (?:mutmut|cosmic-ray)/i);
});

test("mutation registry and run templates preserve reproducible independent history", async () => {
  const [registry, run, conventions] = await Promise.all([
    read(".ai/templates/mutation-registry.yaml"),
    read(".ai/templates/mutation-run.yaml"),
    read(".ai/CONVENTIONS.md")
  ]);
  assert.match(registry, /next_id: MUT-0001/);
  for (const field of ["run:", "scope:", "fingerprint:", "tool:", "budget:", "baseline:", "results:", "artifacts:", "analysis:", "disposition:"]) assert.match(run, new RegExp(field));
  assert.match(run, /status: not_requested/);
  assert.match(run, /scoped_diff_hash:/);
  assert.match(conventions, /MUT-/);
});

test("record validation accepts reproducible metrics-only history and rejects malformed analysis", async () => {
  const valid = {
    schema_version: 1,
    id: "MUT-0001",
    started_at: "2026-08-24T00:00:00Z",
    run: { outcome: "COMPLETED" },
    scope: { production_paths: ["src/"], test_paths: ["tests/"] },
    fingerprint: { base_revision: "abc", scoped_diff_hash: "def" },
    tool: { backend: "fake", version: "1" },
    budget: { timeout_seconds: 60 },
    baseline: { outcome: "passed" },
    results: { generated: 2, killed: 1, survived: 1, no_coverage: 0, timeout: 0, invalid_or_error: 0 },
    artifacts: { retained: false },
    analysis: { authorized: false, status: "not_requested", remaining_candidates: 0 },
    disposition: { status: "none", references: [] }
  };
  assert.equal(validateRecord(valid), true);
  assert.equal(validateRecord({ ...valid, id: "TASK-001" }), false);
  assert.equal(validateRecord({ ...valid, results: { ...valid.results, survived: -1 } }), false);
  assert.equal(validateRecord({ ...valid, analysis: { authorized: false, status: "completed", source_fingerprint: "def", budget: 1, remaining_candidates: 0 } }), false);
  assert.equal(validateRecord({ ...valid, analysis: { authorized: true, status: "partial", source_fingerprint: "def", budget: 1, remaining_candidates: 0 } }), false);
  const check = await read(".ai/framework/skills/forge-check-framework/SKILL.md");
  assert.match(check, /Reject reused, duplicate, path-mismatched, or dangling identities/);
  assert.match(check, /Counts must be non-negative/);
  assert.match(check, /Reject analysis after baseline failure/);
});

test("runner is fast, baseline-first, bounded, and cannot mutate tracked state", async () => {
  const runner = await read(".ai/framework/agents/mutation-runner.yaml");
  assert.match(runner, /model_tier: fast/);
  assert.match(runner, /mode: runtime_artifacts_only/);
  assert.match(runner, /before the baseline, before mutation execution, and after mutation execution/i);
  assert.match(runner, /SETUP REQUIRED/);
  assert.match(runner, /never install or configure a tool/i);
  assert.match(runner, /Do not edit tracked production code, tests, dependencies, configuration/i);
  assert.match(runner, /spawn_policy: forbidden/);
});

test("analyzer is strong, explicitly authorized, bounded, and never remediates", async () => {
  const analyzer = await read(".ai/framework/agents/mutation-analyzer.yaml");
  assert.match(analyzer, /model_tier: strong/);
  assert.match(analyzer, /explicit immediate or deferred analysis authorization/i);
  assert.match(analyzer, /positive candidate budget/i);
  assert.match(analyzer, /actionable_test_gap/);
  assert.match(analyzer, /likely_equivalent/);
  assert.match(analyzer, /Do not edit source or tests/);
  assert.match(analyzer, /spawn_policy: forbidden/);
});

test("skill defaults to metrics-only and invokes strong analysis only on current candidates", async () => {
  const skill = await read(".ai/framework/skills/forge-mutation-test/SKILL.md");
  assert.match(skill, /Metrics-only is the default/);
  assert.match(skill, /Without explicit analysis authorization[\s\S]*stop without invoking a strong model/);
  assert.match(skill, /skip the analyzer[\s\S]*all mutants are killed/i);
  assert.match(skill, /deferred analysis[\s\S]*never repeat the mutation campaign/i);
  assert.match(skill, /must not create or change a Bug, Epic, TASK, Replan/i);
});

test("dual-platform generation declares both mutation roles and portable skill", async () => {
  const [manifest, generation, codexRouter, claudeRouter, sync] = await Promise.all([
    read(".ai/framework/manifest.yaml"),
    read(".ai/05-create-platform-adapters.md"),
    read(".ai/templates/adapters/codex/AGENTS.md"),
    read(".ai/templates/adapters/claude/CLAUDE.md"),
    read(".ai/framework/skills/forge-sync-adapters/SKILL.md")
  ]);
  assert.equal(claudeRouter.trim(), "@AGENTS.md");
  assert.ok(codexRouter.split(/\r?\n/).length <= 150);
  for (const id of ["mutation-runner", "mutation-analyzer"]) {
    assert.match(manifest, new RegExp(id));
    assert.match(generation, new RegExp(`\\.codex/agents/${id}\\.toml`));
    assert.match(generation, new RegExp(`\\.claude/agents/${id}\\.md`));
    assert.match(codexRouter, new RegExp(id));
  }
  assert.match(generation, /sixteen portable `SKILL\.md` files/);
  assert.match(sync, /Generate no `\.ai\/integrations\/` or `quality\/mutation-testing\/` content/);
});

test("migration preserves project-owned mutation history and installs new managed IDs", async () => {
  const [migration, skill] = await Promise.all([
    read(".ai/MIGRATE.md"),
    read(".ai/framework/skills/forge-migrate-framework/SKILL.md")
  ]);
  for (const source of [migration, skill]) {
    assert.match(source, /quality\/mutation-testing\//);
    assert.match(source, /mutation-runner/);
    assert.match(source, /mutation-analyzer/);
    assert.match(source, /preserv/i);
    assert.match(source, /byte-for-byte|exact mutation history/i);
  }
});

test("conformance treats mutation records as independent project-owned state", async () => {
  const [check, validation, contracts] = await Promise.all([
    read(".ai/framework/skills/forge-check-framework/SKILL.md"),
    read(".ai/06-final-validation.md"),
    read(".ai/framework/contracts.yaml")
  ]);
  for (const source of [check, validation]) {
    assert.match(source, /quality\/mutation-testing\//);
    assert.match(source, /metrics-only/i);
    assert.match(source, /explicit authorization/i);
    assert.match(source, /lifecycle/i);
  }
  assert.match(contracts, /gate_satisfaction: forbidden/);
  assert.match(contracts, /evidence_invalidation: forbidden/);
});

test("maintained documentation explains cost-controlled standalone mutation testing", async () => {
  const paths = ["FRAMEWORK.md", "README.md", "RUNBOOK.md", "MIGRATION.md"];
  const sources = await Promise.all(paths.map(read));
  const combined = sources.join("\n");
  for (const term of ["forge-mutation-test", "mutation-runner", "mutation-analyzer", "MUT-NNNN", "quality/mutation-testing/"]) assert.match(combined, new RegExp(term));
  assert.match(combined, /metrics-only/i);
  assert.match(combined, /strong[^\n]*analysis[^\n]*separate|strong `mutation-analyzer`[^\n]*отдельн/i);
  assert.match(combined, /не меняет Backlog|never change development lifecycle state/i);
  assert.match(combined, /не устанавливает `mutmut`|не устанавливает backend|does not install/i);
});

test("fixture scenarios route analysis without a real mutation backend", async () => {
  const scenarios = JSON.parse(await read("tests/fixtures/mutation-testing.json"));
  for (const scenario of scenarios) {
    assert.equal(analysisDecision(scenario), scenario.expectedAnalysis, scenario.name);
  }
  const disposition = scenarios.at(-1).run.disposition;
  assert.deepEqual(disposition.references, ["EPIC-014", "TASK-031"]);
  assert.equal(scenarios.at(-1).expectedAnalysis, "not_requested");
});
