"""Deterministic rendering and compare-before-write adapter transactions."""
from __future__ import annotations

import difflib
import json
import os
from pathlib import Path
import re
import tempfile
import tomllib

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

from forge_core import ForgeError, canonical, digest, frontmatter, load_yaml, snapshot, text, within


def render(root):
    manifest = load_yaml(root, ".ai/framework/manifest.yaml")
    config = load_yaml(root, ".ai/project.yaml")
    if config.get("version") != manifest["framework"]["version"]:
        raise ForgeError("Project/framework versions differ; reconcile migration first")
    mode = config.get("role_execution", {}).get("mode")
    if mode not in manifest["role_execution"]["supported_modes"]:
        raise ForgeError("An approved role_execution.mode is required")
    platforms = config.get("platforms", {})
    for name in ("codex", "claude", "opencode"):
        if type(platforms.get(name, {}).get("enabled")) is not bool:
            raise ForgeError(f"Explicit platform enabled flag required: {name}")
        if name != "opencode" and not platforms[name]["enabled"]:
            raise ForgeError("Codex and Claude must remain enabled")
    for platform in platforms:
        if not platforms[platform].get("enabled"):
            continue
        for tier in ("strong", "balanced", "fast"):
            mapping = config.get("models", {}).get(platform, {}).get(tier, {})
            model = mapping.get("model")
            if not isinstance(model, str) or not model.strip() or any(c in model for c in "<>\n\r"):
                raise ForgeError(f"Unresolved model: {platform}.{tier}")
            if platform == "opencode" and not re.fullmatch(r"[^/\s]+/[^\s]+", model):
                raise ForgeError(f"OpenCode model must be provider-qualified: {tier}")
            if platform in ("codex", "claude"):
                effort = mapping.get("reasoning_effort" if platform == "codex" else "effort")
                if effort not in ("low", "medium", "high", "xhigh", "max"):
                    raise ForgeError(f"Unresolved effort: {platform}.{tier}")
    for legacy in ("codex-router", "claude-router"):
        if within(root, f".ai/custom/{legacy}.md").exists():
            raise ForgeError("Reconcile legacy overlays into router-shared.md first")
    env = SandboxedEnvironment(undefined=StrictUndefined, keep_trailing_newline=True)
    env.filters["tojson"] = lambda value: json.dumps(value, ensure_ascii=False)
    inputs = [".ai/framework/manifest.yaml", ".ai/project.yaml", ".ai/tools/forge_adapters.py",
              ".ai/tools/forge_core.py", ".ai/tools/requirements.txt"]
    outputs = {}

    def source(path):
        inputs.append(path)
        return text(root, path)

    overlay_path = ".ai/custom/router-shared.md"
    inputs.append(overlay_path)
    overlay = text(root, overlay_path) if within(root, overlay_path).exists() else ""
    router = env.from_string(source(".ai/templates/adapters/codex/AGENTS.md")).render(custom={"router_shared": overlay})
    if len(router.splitlines()) > 150 or "{{" in router:
        raise ForgeError("Router exceeds 150 lines or contains unresolved placeholders")
    outputs["AGENTS.md"] = router.encode()
    claude = source(".ai/templates/adapters/claude/CLAUDE.md")
    if claude.strip() != "@AGENTS.md":
        raise ForgeError("CLAUDE.md must import AGENTS.md exactly")
    outputs["CLAUDE.md"] = b"@AGENTS.md\n"
    for identity in manifest["subagents"]:
        if not re.fullmatch(r"[a-z0-9-]+", identity):
            raise ForgeError("Unsafe agent ID")
        path = f".ai/framework/agents/{identity}.yaml"
        inputs.append(path)
        agent = load_yaml(root, path)
        if agent["id"] != identity:
            raise ForgeError(f"Agent ID mismatch: {path}")
        for platform in ("codex", "claude", "opencode"):
            if not platforms[platform]["enabled"]:
                continue
            extension = "toml" if platform == "codex" else "md"
            template = source(f".ai/templates/adapters/{platform}/agent.{extension}")
            rendered = env.from_string(template).render(agent=agent, **config)
            if platform == "codex":
                parsed = tomllib.loads(rendered)
                if parsed["developer_instructions"] != agent["instructions"]:
                    raise ForgeError("Rendered role instructions changed")
            else:
                frontmatter(rendered)
                if not rendered.startswith("---\n") or agent["instructions"] not in rendered:
                    raise ForgeError("Invalid role frontmatter/instruction parity")
            outputs[f".{platform}/agents/{identity}.{extension}"] = rendered.encode()
    for identity in manifest["skills"]:
        if not re.fullmatch(r"[a-z0-9-]+", identity):
            raise ForgeError("Unsafe skill ID")
        # Copy supporting resources too: skills may disclose detail progressively.
        base = within(root, f".ai/framework/skills/{identity}")
        for path in sorted(base.rglob("*")):
            within(root, path)
            if not path.is_file():
                continue
            relative = path.relative_to(base).as_posix()
            original = path.relative_to(root).as_posix()
            inputs.append(original)
            data = path.read_bytes()
            for directory in (".agents", ".claude"):
                outputs[f"{directory}/skills/{identity}/{relative}"] = data
    for platform, launcher in (("claude", "codex-role-runner.mjs"), ("codex", "claude-role-runner.mjs")):
        outputs[f".{platform}/forge/{launcher}"] = source(f".ai/templates/adapters/{platform}/{launcher}").encode()
    return outputs, snapshot(root, inputs)


def preview(root, include_diff=False):
    outputs, inputs = render(root)
    lock_path = within(root, ".ai/framework.lock")
    old_lock = load_yaml(root, ".ai/framework.lock") if lock_path.exists() else {}
    known = old_lock.get("python_adapter_state", {}).get("outputs", {})
    changes, collisions, observed = [], [], {}
    for name, data in sorted(outputs.items()):
        path = within(root, name)
        before = path.read_bytes() if path.exists() else None
        current_hash = digest(before) if before is not None else None
        observed[name] = current_hash
        if before == data:
            continue
        if before is not None and current_hash != known.get(name):
            collisions.append(name)
        item = {"path": name, "before": current_hash, "after": digest(data), "bytes": len(data)}
        if include_diff:
            item["diff"] = "".join(difflib.unified_diff((before or b"").decode("utf-8").splitlines(True),
                                                        data.decode().splitlines(True), fromfile=name, tofile=name))
        changes.append(item)
    # Retired/disabled outputs are preserved; removal is a separate reviewed migration.
    retired = sorted(set(known) - set(outputs))
    state = {"inputs": inputs, "observed": observed, "candidate": {p: digest(v) for p, v in outputs.items()},
             "lock": digest(lock_path.read_bytes()) if lock_path.exists() else None}
    token = digest(canonical(state).encode())
    return {"preview_token": token, "changes": changes, "collisions": collisions, "preserved_retired": retired,
            "input_fingerprint": inputs["fingerprint"]}, outputs, inputs, old_lock


def _replace(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".forge-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(root, expected_token, approved_collisions=()):
    guard = within(root, ".ai/local/adapter-transaction")
    guard.parent.mkdir(parents=True, exist_ok=True)
    try:
        guard.mkdir()
    except FileExistsError as exc:
        raise ForgeError("Adapter transaction exists; inspect/recover it before retrying") from exc
    success = False
    originals = {}
    try:
        result, outputs, inputs, old_lock = preview(root)
        if result["preview_token"] != expected_token:
            raise ForgeError("Stale preview: inputs or outputs changed")
        if set(result["collisions"]) - set(approved_collisions):
            raise ForgeError("Unapproved collisions: " + ", ".join(result["collisions"]))
        lock = dict(old_lock)
        lock["python_adapter_state"] = {"schema_version": 1, "input_fingerprint": inputs["fingerprint"],
                                         "outputs": {p: digest(v) for p, v in outputs.items()}}
        updates = {c["path"]: outputs[c["path"]] for c in result["changes"]}
        lock_bytes = (canonical(lock) + "\n").encode()
        lock_path = within(root, ".ai/framework.lock")
        if not lock_path.exists() or lock_path.read_bytes() != lock_bytes:
            updates[".ai/framework.lock"] = lock_bytes
        for index, name in enumerate(updates):
            path = within(root, name)
            before = path.read_bytes() if path.exists() else None
            originals[name] = before
            if before is not None:
                (guard / f"{index}.bak").write_bytes(before)
        journal = {"files": [{"path": n, "backup": f"{i}.bak" if b is not None else None,
                               "after": digest(updates[n])} for i, (n, b) in enumerate(originals.items())]}
        (guard / "journal.json").write_text(canonical(journal), encoding="utf-8")
        # Recheck the entire preview after preparing backups, before the first write.
        if preview(root)[0]["preview_token"] != expected_token:
            raise ForgeError("Repository changed while preparing transaction")
        written = []
        try:
            for name, data in updates.items():
                path = within(root, name)
                if (path.read_bytes() if path.exists() else None) != originals[name]:
                    raise ForgeError(f"Concurrent edit: {name}")
                _replace(path, data)
                written.append(name)
        except BaseException:
            for name in reversed(written):
                path = within(root, name)
                if path.read_bytes() != updates[name]:
                    raise ForgeError(f"Concurrent edit during rollback: {name}; backups retained at {guard}")
                if originals[name] is None:
                    path.unlink()
                else:
                    _replace(path, originals[name])
            raise
        success = True
        return {"applied": list(updates), "preserved_retired": result["preserved_retired"]}
    finally:
        # Keep journals on failure for explicit recovery; never recursively remove user paths.
        if success or not (guard / "journal.json").exists():
            for path in guard.iterdir():
                path.unlink()
            guard.rmdir()


def recover(root):
    guard = within(root, ".ai/local/adapter-transaction")
    journal = json.loads((guard / "journal.json").read_text(encoding="utf-8"))
    restored = []
    allowed = set(render(root)[0]) | {".ai/framework.lock"}
    # Validate all targets first so recovery cannot overwrite a subsequent user edit.
    for item in journal["files"]:
        if item["path"] not in allowed:
            raise ForgeError(f"Unmanaged target in recovery journal: {item['path']}")
        if item["backup"] is not None and not re.fullmatch(r"\d+\.bak", item["backup"]):
            raise ForgeError("Invalid backup name in recovery journal")
        path = within(root, item["path"])
        before = (guard / item["backup"]).read_bytes() if item["backup"] else None
        current = path.read_bytes() if path.exists() else None
        if current != before and (current is None or digest(current) != item["after"]):
            raise ForgeError(f"Recovery conflicts with later edit: {item['path']}")
    for item in reversed(journal["files"]):
        path = within(root, item["path"])
        if item["backup"]:
            _replace(path, (guard / item["backup"]).read_bytes())
        elif path.exists():
            path.unlink()
        restored.append(item["path"])
    for path in guard.iterdir():
        path.unlink()
    guard.rmdir()
    return {"restored": restored}
