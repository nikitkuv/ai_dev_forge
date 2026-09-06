"""Bounded subprocesses, explicitly scoped check reuse, and local usage records."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

from forge_core import ForgeError, canonical, digest, load_yaml, snapshot, within


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ForgeError(f"{name} must be finite and positive")
    return value


def terminate(process):
    """Stop only the process group created by this helper."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True,
                       timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
        if process.poll() is None:
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=10)


def executable(command, env=None, cwd=None):
    env = os.environ if env is None else env
    if cwd is not None and not Path(command).is_absolute() and ("/" in command or "\\" in command):
        command = str(Path(cwd) / command)
    search_path = next((value for key, value in env.items() if key.lower() == "path"), "")
    found = shutil.which(command, path=search_path)
    if not found:
        raise ForgeError(f"Executable not found: {command}")
    path = Path(found).resolve()
    if path.suffix.lower() in (".cmd", ".bat"):
        # Avoid shell=True and shell interpolation of user prompts/arguments.
        entries = {"codex": "@openai/codex/bin/codex.js", "claude": "@anthropic-ai/claude-code/cli.js",
                   "npm": "npm/bin/npm-cli.js", "npx": "npm/bin/npx-cli.js"}
        entry = entries.get(path.stem.lower())
        script = path.parent / "node_modules" / entry if entry else None
        if script is None or not script.is_file():
            raise ForgeError(f"Unsupported command wrapper: {path}; configure a native executable")
        node = shutil.which("node", path=search_path)
        if not node:
            raise ForgeError("Node is required by this installed npm wrapper")
        return [str(Path(node).resolve()), str(script.resolve())]
    return [str(path)]


def run(argv, cwd, timeout=60, input_text=None, env=None, max_bytes=8 * 1024 * 1024):
    positive(timeout, "timeout")
    positive(max_bytes, "max_bytes")
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and "\0" not in a for a in argv):
        raise ForgeError("argv must be a non-empty string array")
    env = dict(os.environ if env is None else env)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    launch = executable(argv[0], env, cwd) + argv[1:]
    started = time.monotonic()
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as error, tempfile.TemporaryFile() as incoming:
        incoming.write((input_text or "").encode())
        incoming.seek(0)
        process = subprocess.Popen(launch, cwd=cwd, env=env, stdin=incoming, stdout=output, stderr=error,
                                   shell=False, start_new_session=os.name != "nt",
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        reason = None
        try:
            while process.poll() is None:
                if time.monotonic() - started > timeout:
                    reason = "timeout"
                elif os.fstat(output.fileno()).st_size + os.fstat(error.fileno()).st_size > max_bytes:
                    reason = "output_limit"
                if reason:
                    terminate(process)
                    break
                time.sleep(0.02)
        except BaseException:
            if process.poll() is None:
                terminate(process)
            raise
        output.seek(0)
        error.seek(0)
        stdout = output.read(max_bytes + 1)
        stderr = error.read(max_bytes + 1)
        if len(stdout) + len(stderr) > max_bytes:
            reason = reason or "output_limit"
        return {"exit_code": 124 if reason == "timeout" else 125 if reason else process.returncode,
                "failure": reason, "duration_seconds": round(time.monotonic() - started, 4),
                "stdout": stdout[:max_bytes].decode("utf-8", "replace").replace("\r\n", "\n"),
                "stderr": stderr[:max_bytes].decode("utf-8", "replace").replace("\r\n", "\n")}


def checks(root, packet, execute=False, reuse=False):
    if not execute:
        raise ForgeError("Use --execute only for commands already authorized in the Verification Plan")
    if packet.get("schema_version") != 1 or packet.get("stage") not in ("task", "epic"):
        raise ForgeError("Check packet requires schema_version: 1 and stage: task|epic")
    commands = packet.get("checks")
    if not isinstance(commands, list) or not commands:
        raise ForgeError("Non-empty checks required")
    scope = packet.get("inputs")
    if not isinstance(scope, list) or not all(isinstance(p, str) for p in scope):
        raise ForgeError("inputs must be explicit file paths, including dependencies and configuration")
    before = snapshot(root, scope)
    env = dict(os.environ)
    extra_env = packet.get("env", {})
    if not isinstance(extra_env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in extra_env.items()):
        raise ForgeError("env must map string names to string values")
    env.update(extra_env)
    keys = []
    for item in commands:
        positive(item.get("timeout_seconds"), "check timeout_seconds")
        argv = item.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(a, str) for a in argv):
            raise ForgeError("Each check needs argv")
        launch = executable(argv[0], env, within(root, item.get("cwd", ".")))
        keys.append([{ "path": p, "sha256": digest(Path(p).read_bytes())} for p in launch])
        within(root, item.get("cwd", "."))
    key = digest(canonical({"root": str(root), "packet": packet, "fingerprint": before["fingerprint"], "launchers": keys,
                            "environment_hash": digest(canonical(env).encode()), "python": sys.version,
                            "runner_hash": digest(Path(__file__).read_bytes()),
                            "core_hash": digest(Path(__file__).with_name("forge_core.py").read_bytes())}).encode())
    cache = within(root, f".ai/local/check-cache/{key}.json")
    eligible = packet.get("cacheable") is True and packet.get("inputs_complete") is True and packet["stage"] == "task"
    if reuse and eligible and cache.exists():
        saved = json.loads(cache.read_text(encoding="utf-8"))
        intact = all(within(root, r["log"]).is_file() and digest(within(root, r["log"]).read_bytes()) == r.get("log_sha256")
                     for r in saved.get("results", []))
        if saved.get("key") == key and saved.get("passed") is True and len(saved.get("results", [])) == len(commands) and intact:
            saved["reused"] = True
            return saved
    results = []
    for item in commands:
        result = run(item["argv"], within(root, item.get("cwd", ".")), item["timeout_seconds"], env=env)
        log_id = uuid.uuid4().hex
        log_path = within(root, f".ai/local/check-logs/{log_id}.json")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(canonical(result), encoding="utf-8")
        results.append({"id": item.get("id"), "argv": item["argv"], "cwd": item.get("cwd", "."),
                        "exit_code": result["exit_code"], "failure": result["failure"],
                        "duration_seconds": result["duration_seconds"], "log": log_path.relative_to(root).as_posix(),
                        "log_sha256": digest(log_path.read_bytes()),
                        "warning_tail": result["stderr"][-1500:] or None,
                        "output_tail": (result["stderr"] + result["stdout"])[-3000:] if result["exit_code"] else None})
        if result["exit_code"]:
            break  # no retry-until-green and no model invocation to interpret success
    after = snapshot(root, scope)
    report = {"key": key, "passed": len(results) == len(commands) and all(r["exit_code"] == 0 for r in results)
              and before["fingerprint"] == after["fingerprint"], "reused": False,
              "fingerprint": before["fingerprint"], "inputs_changed": before["fingerprint"] != after["fingerprint"],
              "results": results, "unrun": len(commands) - len(results)}
    if eligible and report["passed"]:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(canonical(report), encoding="utf-8")
    return report


def metrics_record(root, event):
    allowed = {"task", "track", "stage", "model", "duration_seconds", "input_tokens", "output_tokens",
               "cached_input_tokens", "reused_checks", "review_iterations", "escalation_reason", "post_acceptance_fix"}
    if set(event) - allowed or event.get("track") not in ("fast", "standard"):
        raise ForgeError("Unknown metrics fields or invalid track")
    for key in ("duration_seconds", "input_tokens", "output_tokens", "cached_input_tokens", "reused_checks", "review_iterations"):
        value = event.get(key)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
            raise ForgeError(f"Invalid metric: {key}")
    event = dict(event, recorded_at=time.time())
    path = within(root, f".ai/local/metrics/{uuid.uuid4().hex}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(event), encoding="utf-8")
    return {"recorded": path.relative_to(root).as_posix()}


def metrics(root):
    groups = {}
    for path in sorted(within(root, ".ai/local/metrics").glob("*.json")):
        event = json.loads(within(root, path).read_text(encoding="utf-8"))
        key = event["track"] + ":" + str(event.get("stage", "unknown"))
        group = groups.setdefault(key, {"events": 0, "known_input_tokens": 0, "known_output_tokens": 0,
                                        "events_missing_usage": 0, "duration_seconds": 0})
        group["events"] += 1
        group["known_input_tokens"] += event.get("input_tokens") or 0
        group["known_output_tokens"] += event.get("output_tokens") or 0
        group["duration_seconds"] += event.get("duration_seconds") or 0
        group["events_missing_usage"] += event.get("input_tokens") is None or event.get("output_tokens") is None
    return {"groups": groups, "note": "Observed usage only; missing usage is unknown, not zero cost. Compare similar tasks."}


def role(root, provider, role_name, prompt, model, effort, timeout=900, preflight_only=False):
    if role_name not in ("epic-planner", "reviewer") or provider not in ("codex", "claude"):
        raise ForgeError("Unsupported role/provider")
    if effort not in ("low", "medium", "high", "xhigh", "max") or not model:
        raise ForgeError("Explicit model and supported effort required")
    env = {k: v for k, v in os.environ.items() if k.upper() not in
           {"BASH_ENV", "CLAUDE_PLUGIN_DATA", "CODEX_COMPANION_APP_SERVER_ENDPOINT", "CODEX_COMPANION_SESSION_ID"}}
    override = env.get("FORGE_CODEX_BIN" if provider == "codex" else "FORGE_CLAUDE_EXECUTABLE")
    command = override or (shutil.which(provider + ".exe") if os.name == "nt" else None) or provider
    version = run([command, "--version"], root, 15, env=env)
    if version["exit_code"]:
        raise ForgeError(f"{provider} version preflight failed: {version['failure'] or version['stderr']}")
    if provider == "claude":
        import re
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", version["stdout"])
        if not match or tuple(map(int, match.groups())) < (2, 1, 203):
            raise ForgeError("Claude Code 2.1.203+ required")
        auth = run([command, "auth", "status"], root, 15, env=env)
        try:
            authenticated = json.loads(auth["stdout"]).get("loggedIn") is True
        except (ValueError, AttributeError):
            authenticated = False
    else:
        if model != "gpt-5.6-sol" or effort != "medium":
            raise ForgeError("Configured claude_with_codex route requires gpt-5.6-sol/medium")
        help_result = run([command, "exec", "--help"], root, 15, env=env)
        if help_result["exit_code"]:
            raise ForgeError("codex exec unavailable")
        auth = run([command, "login", "status"], root, 15, env=env)
        authenticated = auth["exit_code"] == 0
    if auth["exit_code"] or not authenticated:
        raise ForgeError(f"{provider} authentication preflight failed")
    if preflight_only:
        return {"available": True, "provider": provider, "version": version["stdout"].strip()}
    if not prompt.strip():
        raise ForgeError("Empty assignment")
    if provider == "codex":
        args = ["exec", "--ephemeral", "--sandbox", "read-only", "--model", model, "--config",
                f"model_reasoning_effort='{effort}'", "--color", "never", "-"]
    else:
        args = ["-p", "--output-format", "json", "--model", model, "--effort", effort, "--permission-mode", "plan",
                "--no-session-persistence", "--tools", "Read,Grep,Glob,Bash", "--no-chrome", "--disallowedTools",
                "Edit,Write,NotebookEdit,Agent,Task,TeamCreate,TeamDelete,SendMessage,WebFetch,WebSearch,Chrome,mcp__*"]
    result = run([command] + args, root, timeout, input_text=prompt, env=env)
    valid = bool(result["stdout"].strip()) and result["exit_code"] == 0
    if provider == "claude" and valid:
        try:
            parsed = json.loads(result["stdout"])
            valid = isinstance(parsed, dict) and parsed.get("is_error") is not True and isinstance(parsed.get("result"), str) and bool(parsed["result"].strip())
        except ValueError:
            valid = False
    return {"provider": provider, "role": role_name, "model": model, "effort": effort,
            "valid_output": valid, "fallback": "forbidden", **result,
            "exit_code": result["exit_code"] or (0 if valid else 1)}
