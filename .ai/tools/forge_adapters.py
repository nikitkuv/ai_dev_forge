"""Deterministic rendering and compare-before-write adapter transactions."""
from __future__ import annotations

import difflib
import json
from pathlib import Path
import re
import tomllib

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

from forge_core import ForgeError, Transaction, atomic_replace, canonical, digest, frontmatter, load_yaml, text, within, yaml_value

_replace = atomic_replace


def render(bundle_root, root, config=None, overlay=None):
    """Render adapter outputs from one bundle directory against project state.

    Framework sources (manifest, templates, neutral agents, skills, launchers)
    are read from bundle_root (.ai or a staged .ai-next); project configuration
    and the router overlay come from root. Migration callers may pass the
    reconciled config dict and overlay content directly; the adapters command
    passes neither and keeps reading them from disk.
    """
    sources = []  # (label, absolute path) of every render input actually read

    def bundle_source(relative):
        label = f"{Path(bundle_root).name}/{relative}"
        sources.append((label, within(bundle_root, relative)))
        return text(bundle_root, relative)

    def project_source(name):
        sources.append((name, within(root, name)))
        return text(root, name)

    manifest = load_yaml(bundle_root, "framework/manifest.yaml")
    if config is None:
        config = yaml_value(project_source(".ai/project.yaml"))
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
    for name in ("tools/forge_adapters.py", "tools/forge_core.py", "tools/requirements.txt"):
        bundle_source(name)
    outputs = {}

    overlay_path = ".ai/custom/router-shared.md"
    if overlay is None:
        overlay = project_source(overlay_path) if within(root, overlay_path).exists() else ""
    router = env.from_string(bundle_source("templates/adapters/codex/AGENTS.md")).render(custom={"router_shared": overlay})
    if len(router.splitlines()) > 150 or "{{" in router:
        raise ForgeError("Router exceeds 150 lines or contains unresolved placeholders")
    outputs["AGENTS.md"] = router.encode()
    claude = bundle_source("templates/adapters/claude/CLAUDE.md")
    if claude.strip() != "@AGENTS.md":
        raise ForgeError("CLAUDE.md must import AGENTS.md exactly")
    outputs["CLAUDE.md"] = b"@AGENTS.md\n"
    for identity in manifest["subagents"]:
        if not re.fullmatch(r"[a-z0-9-]+", identity):
            raise ForgeError("Unsafe agent ID")
        relative = f"framework/agents/{identity}.yaml"
        agent = yaml_value(bundle_source(relative))
        if not isinstance(agent, dict):
            raise ForgeError(f"Expected mapping: {relative}")
        if agent["id"] != identity:
            raise ForgeError(f"Agent ID mismatch: {relative}")
        for platform in ("codex", "claude", "opencode"):
            if not platforms[platform]["enabled"]:
                continue
            extension = "toml" if platform == "codex" else "md"
            template = bundle_source(f"templates/adapters/{platform}/agent.{extension}")
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
        base = within(bundle_root, f"framework/skills/{identity}")
        for path in sorted(base.rglob("*")):
            within(bundle_root, path)
            if not path.is_file():
                continue
            relative = path.relative_to(base).as_posix()
            label = f"{Path(bundle_root).name}/framework/skills/{identity}/{relative}"
            sources.append((label, path))
            data = path.read_bytes()
            for directory in (".agents", ".claude"):
                outputs[f"{directory}/skills/{identity}/{relative}"] = data
    for platform, launcher in (("claude", "codex-role-runner.mjs"), ("codex", "claude-role-runner.mjs")):
        outputs[f".{platform}/forge/{launcher}"] = bundle_source(f"templates/adapters/{platform}/{launcher}").encode()
    return outputs, _input_state(sources)


def _input_state(sources):
    """Fingerprint every actually-read render input across bundle and project roots."""
    files = []
    for label, path in sources:
        data = path.read_bytes() if path.exists() else None
        files.append({"path": label, "sha256": digest(data) if data is not None else None,
                      "bytes": len(data) if data is not None else 0})
    files.sort(key=lambda item: item["path"])
    return {"algorithm": "forge-render-inputs-v1", "fingerprint": digest(canonical(files).encode()), "files": files}


def bundle_state(bundle_root, root):
    """Hash every file under the bundle manifest's declared framework-owned paths.

    Labels are project-relative `.ai/...` paths regardless of which bundle
    directory is read, so a staged bundle describes the state it will occupy
    after installation and an active bundle describes what is installed.
    """
    manifest = load_yaml(bundle_root, "framework/manifest.yaml")
    files = {}
    for declared in manifest["ownership"]["framework_owned_paths"]:
        relative = declared[len(".ai/"):] if declared.startswith(".ai/") else declared
        relative = relative.rstrip("/")
        base = within(bundle_root, relative)
        if not base.exists():
            continue
        if base.is_file():
            files[f".ai/{relative}"] = digest(base.read_bytes())
            continue
        for path in sorted(base.rglob("*")):
            within(bundle_root, path)
            if path.is_file() and "__pycache__" not in path.parts:
                files[f".ai/{relative}/{path.relative_to(base).as_posix()}"] = digest(path.read_bytes())
    return {"schema_version": 1, "files": files}


def preview(root, include_diff=False):
    outputs, inputs = render(within(root, ".ai"), root)
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
    return atomic_replace(path, data)


def apply(root, expected_token, approved_collisions=()):
    transaction = Transaction(root, "adapter").claim()
    success = False
    try:
        result, outputs, inputs, old_lock = preview(root)
        if result["preview_token"] != expected_token:
            raise ForgeError("Stale preview: inputs or outputs changed")
        if set(result["collisions"]) - set(approved_collisions):
            raise ForgeError("Unapproved collisions: " + ", ".join(result["collisions"]))
        lock = dict(old_lock)
        lock["python_adapter_state"] = {"schema_version": 1, "input_fingerprint": inputs["fingerprint"],
                                         "outputs": {p: digest(v) for p, v in outputs.items()}}
        lock["bundle_state"] = bundle_state(within(root, ".ai"), root)
        updates = {c["path"]: outputs[c["path"]] for c in result["changes"]}
        lock_bytes = (canonical(lock) + "\n").encode()
        lock_path = within(root, ".ai/framework.lock")
        if not lock_path.exists() or lock_path.read_bytes() != lock_bytes:
            updates[".ai/framework.lock"] = lock_bytes

        def recheck():
            if preview(root)[0]["preview_token"] != expected_token:
                raise ForgeError("Repository changed while preparing transaction")

        transaction.write(updates, recheck=recheck, replace=_replace)
        success = True
        return {"applied": list(updates), "preserved_retired": result["preserved_retired"]}
    finally:
        # Keep journals on failure for explicit recovery; never recursively remove user paths.
        transaction.finish(success)


def recover(root):
    allowed = set(render(within(root, ".ai"), root)[0]) | {".ai/framework.lock"}
    return Transaction(root, "adapter").restore(allowed)
