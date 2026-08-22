#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const REQUIRED_CLAUDE = [2, 1, 203];
const REQUIRED_ROLES = new Set(["epic-planner", "reviewer"]);
const ALLOWED_TOOLS = "Read,Grep,Glob,Bash";
const DISALLOWED_TOOLS = [
  "Edit", "Write", "NotebookEdit", "Agent", "Task", "TeamCreate",
  "TeamDelete", "SendMessage", "WebFetch", "WebSearch", "Chrome", "mcp__*"
].join(",");
const ALLOWED_EFFORTS = new Set(["low", "medium", "high", "xhigh", "max"]);

function json(value) {
  process.stdout.write(`${JSON.stringify(value)}\n`);
}

export function versionAtLeast(actual, minimum = REQUIRED_CLAUDE) {
  const match = String(actual).match(/(\d+)\.(\d+)\.(\d+)/);
  if (!match) return false;
  const parts = match.slice(1).map(Number);
  for (let index = 0; index < minimum.length; index += 1) {
    if (parts[index] > minimum[index]) return true;
    if (parts[index] < minimum[index]) return false;
  }
  return true;
}

export function claudeCommand(env = process.env, platform = process.platform) {
  const command = env.FORGE_CLAUDE_EXECUTABLE || (platform === "win32" ? "claude.cmd" : "claude");
  const prefixArgs = env.FORGE_CLAUDE_SCRIPT ? [resolve(env.FORGE_CLAUDE_SCRIPT)] : [];
  return { command, prefixArgs };
}

function runClaude(args, env, cwd, options = {}) {
  const { command, prefixArgs } = claudeCommand(env);
  return spawnSync(command, [...prefixArgs, ...args], {
    cwd,
    env,
    encoding: "utf8",
    windowsHide: true,
    ...options
  });
}

export function preflight(env = process.env, cwd = process.cwd()) {
  const version = runClaude(["--version"], env, cwd);
  if (version.error?.code === "ENOENT") return { available: false, reason: "Claude Code CLI is not installed or is not on PATH." };
  if (version.status !== 0) return { available: false, reason: version.stderr?.trim() || "Claude Code version check failed." };
  const versionText = version.stdout.trim();
  if (!versionAtLeast(versionText)) return { available: false, reason: `Claude Code ${REQUIRED_CLAUDE.join(".")}+ is required.`, version: versionText };

  const auth = runClaude(["auth", "status"], env, cwd);
  if (auth.status !== 0) return { available: false, reason: auth.stderr?.trim() || "Claude Code is not authenticated.", version: versionText };
  try {
    const authentication = JSON.parse(auth.stdout);
    return { available: true, version: versionText, authentication };
  } catch {
    return { available: false, reason: "Claude Code returned invalid authentication JSON.", version: versionText };
  }
}

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) throw new Error(`Unexpected argument: ${key}`);
    const name = key.slice(2);
    if (name === "preflight") { options.preflight = true; continue; }
    const value = argv[index + 1];
    if (value == null) throw new Error(`Missing value for ${key}`);
    options[name] = value;
    index += 1;
  }
  return options;
}

export function buildClaudeArgs(model, effort) {
  if (!model) throw new Error("--model is required.");
  if (!ALLOWED_EFFORTS.has(effort)) throw new Error("--effort must be low, medium, high, xhigh, or max.");
  return [
    "-p",
    "--output-format", "json",
    "--model", model,
    "--effort", effort,
    "--permission-mode", "plan",
    "--no-session-persistence",
    "--tools", ALLOWED_TOOLS,
    "--disallowedTools", DISALLOWED_TOOLS,
    "--no-chrome"
  ];
}

export function main(argv = process.argv.slice(2), env = process.env, cwd = process.cwd()) {
  const options = parseArgs(argv);
  const check = preflight(env, cwd);
  if (options.preflight) { json({ provider: "claude-code-cli", ...check }); return check.available ? 0 : 2; }
  if (!REQUIRED_ROLES.has(options.role)) throw new Error("--role must be epic-planner or reviewer.");
  if (!options["prompt-file"]) throw new Error("--prompt-file is required.");
  if (!check.available) { json({ provider: "claude-code-cli", fallback: "forbidden", ...check }); return 2; }

  const promptFile = resolve(cwd, options["prompt-file"]);
  if (!existsSync(promptFile)) throw new Error(`Prompt file does not exist: ${promptFile}`);
  const prompt = readFileSync(promptFile, "utf8");
  const timeout = Number.parseInt(env.FORGE_ROLE_TIMEOUT_MS || "900000", 10);
  const result = runClaude(buildClaudeArgs(options.model, options.effort), env, cwd, { input: prompt, timeout });
  const timedOut = result.error?.code === "ETIMEDOUT";
  let parsed = null;
  let validOutput = false;
  if (!timedOut && result.status === 0) {
    try { parsed = JSON.parse(result.stdout); validOutput = true; } catch { validOutput = false; }
  }
  const exitCode = timedOut ? 124 : (result.status ?? 1);
  json({
    provider: "claude-code-cli",
    role: options.role,
    model: options.model,
    effort: options.effort,
    permission_mode: "plan",
    allowed_tools: ALLOWED_TOOLS.split(","),
    disallowed_tools: DISALLOWED_TOOLS.split(","),
    fresh: true,
    session_persistence: false,
    read_only: true,
    nested_agents: false,
    started: true,
    timed_out: timedOut,
    valid_output: validOutput,
    exit_code: exitCode,
    result: parsed,
    stdout: validOutput ? undefined : result.stdout,
    stderr: result.stderr,
    claude_version: check.version
  });
  return exitCode === 0 && validOutput ? 0 : (exitCode || 1);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { process.exitCode = main(); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
