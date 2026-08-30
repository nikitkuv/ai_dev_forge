import assert from "node:assert/strict";
import test from "node:test";
import { chmodSync, copyFileSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { delimiter, join } from "node:path";
import { buildRuntimeEnv, findCodexCandidates, main, preflight } from "../.ai/templates/adapters/claude/codex-role-runner.mjs";

function fixture(options = {}) {
  const root = mkdtempSync(join(tmpdir(), "forge-codex-cli-"));
  const script = join(root, "fake-codex.mjs");
  writeFileSync(script, `
const args = process.argv.slice(2);
if (args[0] === "--version") { console.log("codex-cli 1.2.3"); process.exit(0); }
if (args[0] === "exec" && args[1] === "--help") { console.log("Usage: codex exec"); process.exit(${options.execAvailable === false ? 7 : 0}); }
if (args[0] === "login" && args[1] === "status") { console.log("Logged in using ChatGPT"); process.exit(${options.authenticated === false ? 1 : 0}); }
if (args[0] === "exec") {
  let prompt = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => { prompt += chunk; });
  process.stdin.on("end", () => {
    const required = ["--ephemeral", "--sandbox", "read-only", "--model", "gpt-5.6-sol", "--config", "model_reasoning_effort='medium'", "--color", "never", "-"];
    if (!required.every((value) => args.includes(value))) process.exit(8);
    if (process.env.FAKE_EXPECT_PROMPT && prompt !== process.env.FAKE_EXPECT_PROMPT) process.exit(9);
    if (process.env.BASH_ENV || process.env.CLAUDE_PLUGIN_DATA || process.env.CODEX_COMPANION_APP_SERVER_ENDPOINT) process.exit(10);
    console.log("Codex result");
    process.exit(Number(process.env.FAKE_TASK_EXIT || 0));
  });
}
`);

  let command;
  if (process.platform === "win32") {
    command = join(root, "codex.cmd");
    const npmEntrypoint = join(root, "node_modules", "@openai", "codex", "bin", "codex.js");
    mkdirSync(join(root, "node_modules", "@openai", "codex", "bin"), { recursive: true });
    copyFileSync(script, npmEntrypoint);
    writeFileSync(command, "@echo off\r\n");
  } else {
    command = join(root, "codex");
    writeFileSync(command, `#!/bin/sh\nexec "${process.execPath}" "${script}" "$@"\n`);
    chmodSync(command, 0o755);
  }
  return { root, command };
}

test("candidate discovery honors an explicit absolute Codex path", () => {
  const { command } = fixture();
  assert.deepEqual(findCodexCandidates({ FORGE_CODEX_BIN: command }), [command]);
});

test("candidate discovery prioritizes the Windows npm-global directory over PATH", { skip: process.platform !== "win32" }, () => {
  const preferred = fixture();
  const stale = fixture();
  const env = { APPDATA: preferred.root, Path: stale.root };
  const npmCommand = join(preferred.root, "npm", "codex.cmd");
  mkdirSync(join(preferred.root, "npm"));
  copyFileSync(preferred.command, npmCommand);
  assert.equal(findCodexCandidates(env)[0], npmCommand);
});

test("runtime environment exposes Node/npm paths and removes broker and shell injection state", () => {
  const env = buildRuntimeEnv({
    APPDATA: "C:\\Users\\example\\AppData\\Roaming",
    Path: `C:\\stale${delimiter}C:\\tools`,
    BASH_ENV: "unsafe.sh",
    CLAUDE_PLUGIN_DATA: "shared-state",
    CODEX_COMPANION_APP_SERVER_ENDPOINT: "pipe:stale"
  }, "win32", "D:\\nodejs\\node.exe");
  assert.match(env.Path, /AppData\\Roaming\\npm/i);
  assert.match(env.Path, /D:\\nodejs/i);
  assert.equal(env.BASH_ENV, undefined);
  assert.equal(env.CLAUDE_PLUGIN_DATA, undefined);
  assert.equal(env.CODEX_COMPANION_APP_SERVER_ENDPOINT, undefined);
});

test("preflight validates exec support and authentication", () => {
  const ready = fixture();
  assert.equal(preflight({ FORGE_CODEX_BIN: ready.command }).available, true);
  const unauthenticated = fixture({ authenticated: false });
  const result = preflight({ FORGE_CODEX_BIN: unauthenticated.command });
  assert.equal(result.available, false);
  assert.match(result.diagnostics.join("\n"), /not authenticated/i);
});

test("preflight skips a broken wrapper and uses the next real Codex installation", { skip: process.platform !== "win32" }, () => {
  const brokenRoot = mkdtempSync(join(tmpdir(), "forge-codex-broken-"));
  writeFileSync(join(brokenRoot, "codex.cmd"), "@echo off\r\nexit /b 1\r\n");
  const ready = fixture();
  const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => key.toLowerCase() !== "path"));
  env.APPDATA = "";
  env.Path = `${brokenRoot}${delimiter}${ready.root}`;
  const result = preflight(env);
  assert.equal(result.available, true);
  assert.equal(result.codexPath, ready.command);
});

test("preflight rejects an unavailable Node.js runtime", () => {
  const { command } = fixture();
  const result = preflight({ FORGE_CODEX_BIN: command }, process.cwd(), "v18.17.0");
  assert.equal(result.available, false);
  assert.match(result.reason, /Node\.js 18\.18\.0\+/);
});

test("successful planner and reviewer calls pass the exact prompt through stdin", () => {
  const { command } = fixture();
  const work = mkdtempSync(join(tmpdir(), "forge-codex-success-"));
  writeFileSync(join(work, "planner.md"), "Epic assignment");
  writeFileSync(join(work, "reviewer.md"), "Review Packet with \"quoted\"\nmultiline content");
  assert.equal(main(["--role", "epic-planner", "--prompt-file", "planner.md"], { FORGE_CODEX_BIN: command }, work), 0);
  assert.equal(main(["--role", "reviewer", "--prompt-file", "reviewer.md"], {
    FORGE_CODEX_BIN: command,
    FAKE_EXPECT_PROMPT: "Review Packet with \"quoted\"\nmultiline content",
    BASH_ENV: "must-not-leak",
    CLAUDE_PLUGIN_DATA: "must-not-leak",
    CODEX_COMPANION_APP_SERVER_ENDPOINT: "pipe:must-not-leak"
  }, work), 0);
});

test("a started task failure is returned as a Codex failure, not a fallback", () => {
  const { command } = fixture();
  const work = mkdtempSync(join(tmpdir(), "forge-codex-work-"));
  writeFileSync(join(work, "prompt.md"), "Review Packet");
  const status = main(["--role", "reviewer", "--prompt-file", "prompt.md"], {
    FORGE_CODEX_BIN: command,
    FAKE_TASK_EXIT: "7"
  }, work);
  assert.equal(status, 7);
});

test("runner source pins stable fresh read-only Codex exec settings", async () => {
  const source = await import("node:fs/promises").then(({ readFile }) => readFile(new URL("../.ai/templates/adapters/claude/codex-role-runner.mjs", import.meta.url), "utf8"));
  assert.match(source, /\["exec", "--ephemeral", "--sandbox", "read-only"/);
  assert.match(source, /model_reasoning_effort='\$\{REQUIRED_EFFORT\}'/);
  assert.match(source, /REQUIRED_EFFORT = "medium"/);
  assert.doesNotMatch(source, /codex-companion|app-server|CLAUDE_PLUGIN_DATA.*=/);
  assert.doesNotMatch(source, /--resume|--background|--write/);
  assert.match(source, /fallback: "forbidden"/);
});
