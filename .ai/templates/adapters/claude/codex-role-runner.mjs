#!/usr/bin/env node
import { constants, existsSync, readFileSync, accessSync } from "node:fs";
import { delimiter, dirname, extname, isAbsolute, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const REQUIRED_NODE = [18, 18, 0];
const REQUIRED_MODEL = "gpt-5.6-sol";
const REQUIRED_EFFORT = "medium";
const REQUIRED_ROLES = new Set(["epic-planner", "reviewer"]);
const WINDOWS_EXTENSIONS = [".exe", ".cmd", ".bat", ""];

function json(value) {
  process.stdout.write(`${JSON.stringify(value)}\n`);
}

function versionAtLeast(actual, minimum) {
  const parts = String(actual).replace(/^v/, "").split(".").map((part) => Number.parseInt(part, 10) || 0);
  for (let index = 0; index < minimum.length; index += 1) {
    if ((parts[index] ?? 0) > minimum[index]) return true;
    if ((parts[index] ?? 0) < minimum[index]) return false;
  }
  return true;
}

function pathValue(env) {
  const key = Object.keys(env).find((candidate) => candidate.toLowerCase() === "path");
  return key ? env[key] ?? "" : "";
}

function uniquePaths(paths, platform) {
  const seen = new Set();
  const result = [];
  for (const value of paths) {
    if (!value) continue;
    const absolute = resolve(value);
    const key = platform === "win32" ? normalize(absolute).toLowerCase() : normalize(absolute);
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(absolute);
  }
  return result;
}

export function buildRuntimeEnv(env = process.env, platform = process.platform, execPath = process.execPath) {
  const runtimeEnv = { ...env };
  for (const key of ["BASH_ENV", "CLAUDE_PLUGIN_DATA", "CODEX_COMPANION_APP_SERVER_ENDPOINT", "CODEX_COMPANION_SESSION_ID"]) {
    delete runtimeEnv[key];
  }

  const preferred = [dirname(execPath)];
  if (platform === "win32" && env.APPDATA) preferred.unshift(join(env.APPDATA, "npm"));
  const merged = uniquePaths([...preferred, ...pathValue(env).split(delimiter)], platform).join(delimiter);
  const existingPathKey = Object.keys(runtimeEnv).find((candidate) => candidate.toLowerCase() === "path");
  runtimeEnv[existingPathKey ?? (platform === "win32" ? "Path" : "PATH")] = merged;
  return runtimeEnv;
}

function isUsableFile(path, platform) {
  try {
    accessSync(path, platform === "win32" ? constants.F_OK : constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

export function findCodexCandidates(env = process.env, platform = process.platform, execPath = process.execPath) {
  const explicit = env.FORGE_CODEX_BIN;
  if (explicit) {
    const candidate = isAbsolute(explicit) ? normalize(explicit) : resolve(explicit);
    return isUsableFile(candidate, platform) ? [candidate] : [];
  }

  const preferredDirs = [];
  if (platform === "win32" && env.APPDATA) preferredDirs.push(join(env.APPDATA, "npm"));
  preferredDirs.push(dirname(execPath));
  const searchDirs = uniquePaths([...preferredDirs, ...pathValue(env).split(delimiter)], platform);
  const extensions = platform === "win32" ? WINDOWS_EXTENSIONS : [""];
  const candidates = [];
  for (const directory of searchDirs) {
    for (const extension of extensions) {
      const candidate = join(directory, `codex${extension}`);
      if (isUsableFile(candidate, platform)) candidates.push(candidate);
    }
  }
  return uniquePaths(candidates, platform);
}

function run(command, args, options = {}) {
  const env = options.env ?? process.env;
  const common = {
    cwd: options.cwd,
    env,
    encoding: "utf8",
    input: options.input,
    maxBuffer: 16 * 1024 * 1024,
    timeout: options.timeout ?? 15000,
    windowsHide: true
  };
  if (process.platform === "win32" && [".cmd", ".bat"].includes(extname(command).toLowerCase())) {
    const npmEntrypoint = join(dirname(command), "node_modules", "@openai", "codex", "bin", "codex.js");
    if (!existsSync(npmEntrypoint)) {
      return {
        status: null,
        signal: null,
        stdout: "",
        stderr: "",
        error: new Error(`Rejected non-standard or broken Codex wrapper: ${command}`)
      };
    }
    return spawnSync(process.execPath, [npmEntrypoint, ...args], common);
  }
  return spawnSync(command, args, common);
}

function resultDetail(result) {
  return result.error?.message || result.stderr?.trim() || result.stdout?.trim() || `exit ${result.status ?? 1}`;
}

export function preflight(env = process.env, cwd = process.cwd(), nodeVersion = process.version) {
  if (!versionAtLeast(nodeVersion, REQUIRED_NODE)) return { available: false, reason: `Node.js ${REQUIRED_NODE.join(".")}+ is required.` };
  const runtimeEnv = buildRuntimeEnv(env);
  const candidates = findCodexCandidates(runtimeEnv);
  if (candidates.length === 0) {
    return {
      available: false,
      reason: "Codex CLI was not found. Install @openai/codex globally, restart Claude Code, or set FORGE_CODEX_BIN to the absolute codex executable path."
    };
  }

  const failures = [];
  for (const codexPath of candidates) {
    const version = run(codexPath, ["--version"], { cwd, env: runtimeEnv });
    if (version.error || version.status !== 0) {
      failures.push(`${codexPath}: ${resultDetail(version)}`);
      continue;
    }
    const execHelp = run(codexPath, ["exec", "--help"], { cwd, env: runtimeEnv });
    if (execHelp.error || execHelp.status !== 0) {
      failures.push(`${codexPath}: codex exec unavailable: ${resultDetail(execHelp)}`);
      continue;
    }
    const auth = run(codexPath, ["login", "status"], { cwd, env: runtimeEnv });
    if (auth.error || auth.status !== 0) {
      failures.push(`${codexPath}: not authenticated: ${resultDetail(auth)}`);
      continue;
    }
    return {
      available: true,
      codexPath,
      version: version.stdout.trim() || version.stderr.trim(),
      authentication: auth.stdout.trim() || auth.stderr.trim() || "authenticated"
    };
  }

  return { available: false, reason: "No usable authenticated Codex CLI was found.", diagnostics: failures };
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

export function main(argv = process.argv.slice(2), env = process.env, cwd = process.cwd()) {
  const options = parseArgs(argv);
  const check = preflight(env, cwd);
  if (options.preflight) { json({ provider: "codex-cli", transport: "exec", ...check }); return check.available ? 0 : 2; }
  if (!REQUIRED_ROLES.has(options.role)) throw new Error("--role must be epic-planner or reviewer.");
  if (!options["prompt-file"]) throw new Error("--prompt-file is required.");
  if (!check.available) { json({ provider: "codex-cli", transport: "exec", fallback: "forbidden", ...check }); return 2; }
  const promptFile = resolve(cwd, options["prompt-file"]);
  if (!existsSync(promptFile)) throw new Error(`Prompt file does not exist: ${promptFile}`);
  const prompt = readFileSync(promptFile, "utf8");
  const runtimeEnv = buildRuntimeEnv(env);
  const timeout = Number(env.FORGE_ROLE_TIMEOUT_MS || 900000);
  if (!Number.isFinite(timeout) || timeout <= 0) throw new Error("FORGE_ROLE_TIMEOUT_MS must be positive and finite.");
  const result = run(
    check.codexPath,
    ["exec", "--ephemeral", "--sandbox", "read-only", "--model", REQUIRED_MODEL, "--config", `model_reasoning_effort='${REQUIRED_EFFORT}'`, "--color", "never", "-"],
    { cwd, env: runtimeEnv, input: prompt, timeout }
  );
  const exitCode = result.error?.code === "ETIMEDOUT" ? 124 : result.error ? 1 : result.status === 0 && !result.stdout?.trim() ? 1 : result.status ?? 1;
  json({
    provider: "codex-cli",
    transport: "exec",
    role: options.role,
    model: REQUIRED_MODEL,
    reasoning_effort: REQUIRED_EFFORT,
    fresh: true,
    ephemeral: true,
    read_only: true,
    started: !result.error,
    exit_code: exitCode,
    stdout: result.stdout ?? "",
    stderr: result.error?.message || result.stderr || "",
    codexPath: check.codexPath
  });
  return exitCode;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { process.exitCode = main(); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
