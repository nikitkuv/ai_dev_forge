import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { findPluginRoots, main, preflight } from "../.ai/templates/adapters/claude/codex-role-runner.mjs";

function fixture(version = "1.0.6", ready = true, base = mkdtempSync(join(tmpdir(), "forge-codex-plugin-"))) {
  const root = join(base, "cache", "openai-codex", "codex", version);
  mkdirSync(join(root, ".claude-plugin"), { recursive: true });
  mkdirSync(join(root, "scripts"), { recursive: true });
  writeFileSync(join(root, ".claude-plugin", "plugin.json"), JSON.stringify({ name: "codex", version }));
  writeFileSync(join(root, "scripts", "codex-companion.mjs"), `import { readFileSync } from 'node:fs'; if (process.argv[2] === 'setup') console.log(JSON.stringify({ ready: ${ready} })); else { const prompt = readFileSync(process.argv[process.argv.indexOf('--prompt-file') + 1], 'utf8'); if (process.env.FAKE_EXPECT_PROMPT && prompt !== process.env.FAKE_EXPECT_PROMPT) process.exit(9); process.exit(Number(process.env.FAKE_TASK_EXIT || 0)); }`);
  return { base, root };
}

test("findPluginRoots uses Claude's configurable cache root", () => {
  const { base, root } = fixture();
  assert.deepEqual(findPluginRoots({ CLAUDE_CODE_PLUGIN_CACHE_DIR: base }), [root]);
});

test("findPluginRoots accepts slash-separated cache paths", () => {
  const { base, root } = fixture();
  assert.deepEqual(findPluginRoots({ CLAUDE_CODE_PLUGIN_CACHE_DIR: base.replaceAll("\\", "/") }), [root]);
});

test("findPluginRoots supports an explicit plugin root and rejects absent caches", () => {
  const { root } = fixture();
  assert.deepEqual(findPluginRoots({ FORGE_CODEX_PLUGIN_ROOT: root }), [root]);
  assert.deepEqual(findPluginRoots({ CLAUDE_CODE_PLUGIN_CACHE_DIR: join(tmpdir(), "not-a-plugin-cache") }), []);
});

test("findPluginRoots treats a disabled or invalid plugin as unavailable", () => {
  const base = mkdtempSync(join(tmpdir(), "forge-codex-disabled-"));
  const root = join(base, "cache", "openai-codex", "codex", "1.0.6");
  mkdirSync(join(root, ".claude-plugin"), { recursive: true });
  mkdirSync(join(root, "scripts"), { recursive: true });
  writeFileSync(join(root, ".claude-plugin", "plugin.json"), JSON.stringify({ name: "disabled", version: "1.0.6" }));
  writeFileSync(join(root, "scripts", "codex-companion.mjs"), "");
  assert.deepEqual(findPluginRoots({ CLAUDE_CODE_PLUGIN_CACHE_DIR: base }), []);
});

test("preflight distinguishes a ready plugin from unavailable authentication", () => {
  const ready = fixture();
  assert.equal(preflight({ FORGE_CODEX_PLUGIN_ROOT: ready.root }).available, true);
  const unavailable = fixture("1.0.7", false);
  assert.equal(preflight({ FORGE_CODEX_PLUGIN_ROOT: unavailable.root }).available, false);
});

test("preflight rejects an outdated codex-plugin-cc installation", () => {
  const { root } = fixture("1.0.5");
  const result = preflight({ FORGE_CODEX_PLUGIN_ROOT: root });
  assert.equal(result.available, false);
  assert.match(result.reason, /1\.0\.6\+/);
});

test("preflight rejects an unavailable Node.js runtime", () => {
  const { root } = fixture();
  const result = preflight({ FORGE_CODEX_PLUGIN_ROOT: root }, process.cwd(), "v18.17.0");
  assert.equal(result.available, false);
  assert.match(result.reason, /Node\.js 18\.18\.0\+/);
});

test("preflight rejects ambiguous plugin versions before starting a task", () => {
  const first = fixture();
  fixture("1.0.7", true, first.base);
  const result = preflight({ CLAUDE_CODE_PLUGIN_CACHE_DIR: first.base });
  assert.equal(result.available, false);
  assert.match(result.reason, /Multiple usable/);
});

test("successful planner and reviewer transport preserve provider selection", () => {
  const { root } = fixture();
  const work = mkdtempSync(join(tmpdir(), "forge-codex-success-"));
  writeFileSync(join(work, "planner.md"), "Epic assignment");
  writeFileSync(join(work, "reviewer.md"), "Review Packet with \"quoted\"\nmultiline content");
  assert.equal(main(["--role", "epic-planner", "--prompt-file", "planner.md"], { FORGE_CODEX_PLUGIN_ROOT: root }, work), 0);
  assert.equal(main(["--role", "reviewer", "--prompt-file", "reviewer.md"], { FORGE_CODEX_PLUGIN_ROOT: root, FAKE_EXPECT_PROMPT: "Review Packet with \"quoted\"\nmultiline content" }, work), 0);
});

test("a started task failure is returned as a Codex failure, not a fallback", () => {
  const { root } = fixture();
  const work = mkdtempSync(join(tmpdir(), "forge-codex-work-"));
  writeFileSync(join(work, "prompt.md"), "quoted \"Review Packet\"\nmultiline");
  const status = main(["--role", "reviewer", "--prompt-file", "prompt.md"], { FORGE_CODEX_PLUGIN_ROOT: root, FAKE_TASK_EXIT: "7" }, work);
  assert.equal(status, 7);
});

test("runner source pins read-only fresh Codex task settings", async () => {
  const source = await import("node:fs/promises").then(({ readFile }) => readFile(new URL("../.ai/templates/adapters/claude/codex-role-runner.mjs", import.meta.url), "utf8"));
  assert.match(source, /"task", "--fresh", "--model", REQUIRED_MODEL/);
  assert.match(source, /"--effort", REQUIRED_EFFORT/);
  assert.doesNotMatch(source, /"--write"/);
  assert.doesNotMatch(source, /"--resume/);
  assert.doesNotMatch(source, /"--background"/);
  assert.doesNotMatch(source, /claude-subagent|fallback_agent/);
  assert.match(source, /fallback: "forbidden"/);
});
