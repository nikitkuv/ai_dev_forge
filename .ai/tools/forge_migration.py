"""Deterministic one-command framework migration: preview, apply, recover.

The command runs from the staged new bundle (`.ai-next/tools/`) against the
active `.ai/` bundle. Preview is a pure function of repository state; apply is
one guarded transaction that replaces framework-owned paths, applies explicit
configuration decisions, renders routers and adapters, validates, and writes
the lock last. No model calls, no network, no connector invocation.
"""
from __future__ import annotations

import difflib
import json
from pathlib import Path
import re
import shutil

from forge_adapters import bundle_state, preview as adapter_preview, render
from forge_core import (ForgeError, Transaction, backlog_rows, canonical, defect_rows, digest, git_status,
                        load_yaml, snapshot, text, within, yaml_value)

ACTIVE = ".ai"
STAGED = ".ai-next"
LOCK = ".ai/framework.lock"
CONFIG = ".ai/project.yaml"
OVERLAY = ".ai/custom/router-shared.md"
MIGRATIONS = "framework/migrations.yaml"
INTEGRATIONS = ".ai/integrations"
SAFE_SET_KEYS = {"documentation_language"}
TERMINAL_EPIC = {"COMPLETED", "CANCELLED"}
TERMINAL_BUG = {"RESOLVED", "REJECTED", "DUPLICATE", "WONT_FIX"}

_MISSING = object()


def version_tuple(value):
    parts = str(value).split(".")
    if not parts or not all(part.isdigit() for part in parts):
        raise ForgeError(f"Invalid framework version: {value!r}")
    return tuple(int(part) for part in parts)


def migration_entries(bundle_root, old_version, new_version):
    """Contract entries strictly within (old_version, new_version]."""
    if not within(bundle_root, MIGRATIONS).exists():
        raise ForgeError("Staged bundle lacks framework/migrations.yaml")
    data = yaml_value(text(bundle_root, MIGRATIONS))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ForgeError("Unsupported migrations contract schema_version")
    low, high = version_tuple(old_version), version_tuple(new_version)
    selected = []
    for name, entry in sorted((data.get("versions") or {}).items(), key=lambda item: version_tuple(item[0])):
        if low < version_tuple(name) <= high and isinstance(entry, dict):
            selected.append((name, entry))
    return selected


def _scalar(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    raw = str(value)
    if raw == "" or raw != raw.strip() or re.search(r"[\n:#[\]{}&*!|>'\"%@`,]", raw):
        return json.dumps(raw, ensure_ascii=False)
    return raw


def _indent_of(line):
    return len(line) - len(line.lstrip(" "))


def _block_end(lines, start, indent):
    """First line at or after `start` whose content dedents below `indent`."""
    for position in range(start, len(lines)):
        line = lines[position]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if _indent_of(line) < indent:
            return position
    return len(lines)


def _insert_position(lines, start, end):
    for position in range(end - 1, start - 1, -1):
        if lines[position].strip() and not lines[position].lstrip().startswith("#"):
            return position + 1
    return start


def _new_block(segments, value, indent):
    lines = [" " * (indent + 2 * depth) + segment + ":" for depth, segment in enumerate(segments)]
    lines[-1] = lines[-1] + " " + _scalar(value)
    return lines


def _set_flow_value(line, leaf, value):
    pattern = re.compile(r"(" + re.escape(leaf) + r":)(\s*)([^,}]*)([},])")
    replaced, count = pattern.subn(lambda match: match.group(1) + " " + _scalar(value) + match.group(4), line, count=1)
    if count != 1:
        raise ForgeError(f"Key {leaf!r} not found inside the flow mapping")
    return replaced


def _edit(lines, segments, value, indent, start, end):
    key = segments[0]
    pattern = re.compile(r"^ {" + str(indent) + r"}" + re.escape(key) + r":(.*)$")
    found = None
    for position in range(start, end):
        line = lines[position]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if _indent_of(line) == indent and pattern.match(line):
            found = position
            break
    if found is None:
        lines[_insert_position(lines, start, end):_insert_position(lines, start, end)] = _new_block(segments, value, indent)
        return
    if len(segments) == 1:
        lines[found] = " " * indent + key + ": " + _scalar(value)
        return
    rest = pattern.match(lines[found]).group(1)
    if rest.strip() == "":
        child_end = _block_end(lines, found + 1, indent + 1)
        _edit(lines, segments[1:], value, indent + 2, found + 1, child_end)
    elif rest.strip().startswith("{") and len(segments) == 2:
        lines[found] = _set_flow_value(lines[found], segments[1], value)
    else:
        raise ForgeError(f"Cannot set {'.'.join(segments)}: {key} holds a non-block value")


def update_yaml_text(content, dotted, value):
    """Set one dotted value in simply-indented YAML text, preserving comments and layout."""
    segments = dotted.split(".")
    lines = content.split("\n")
    trailing = content.endswith("\n")
    if lines and lines[-1] == "":
        lines.pop()
    _edit(lines, segments, value, 0, 0, len(lines))
    result = "\n".join(lines)
    return result + "\n" if trailing else result


def _config_value(data, dotted):
    current = data
    for segment in dotted.split("."):
        if not isinstance(current, dict) or segment not in current:
            return _MISSING
        current = current[segment]
    return current


def _staged_stray_files(staged, manifest):
    owned = []
    for declared in manifest["ownership"]["framework_owned_paths"]:
        relative = declared[len(".ai/"):] if declared.startswith(".ai/") else declared
        owned.append(relative.rstrip("/"))
    stray = []
    for path in sorted(staged.rglob("*")):
        within(staged, path)
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(staged).as_posix()
        if not any(relative == entry or relative.startswith(entry + "/") for entry in owned):
            stray.append(f"{STAGED}/{relative}")
    return stray


def _bundle_files(bundle_root, manifest):
    """Enumerate {'.ai/<relative>': sha256} under the manifest's framework-owned paths."""
    files = {}
    for declared in manifest["ownership"]["framework_owned_paths"]:
        relative = declared[len(".ai/"):] if declared.startswith(".ai/") else declared
        relative = relative.rstrip("/")
        base = within(bundle_root, relative)
        if not base.exists():
            continue
        if base.is_file():
            files[f"{ACTIVE}/{relative}"] = digest(base.read_bytes())
            continue
        for path in sorted(base.rglob("*")):
            within(bundle_root, path)
            if path.is_file() and "__pycache__" not in path.parts:
                files[f"{ACTIVE}/{relative}/{path.relative_to(base).as_posix()}"] = digest(path.read_bytes())
    return files


def _classify_integrations(root, staged):
    results = []
    base = within(root, INTEGRATIONS)
    if not base.exists():
        return results
    contracts_path = within(staged, "framework/integrations/contracts.yaml")
    if not contracts_path.exists():
        raise ForgeError("Staged bundle lacks framework/integrations/contracts.yaml while .ai/integrations/ exists")
    contracts = load_yaml(staged, "framework/integrations/contracts.yaml")
    current_definition = contracts.get("definition", {}).get("current_schema_version")
    current_state = (contracts.get("work_items") or {}).get("schema_version")
    built_in = set((contracts.get("profiles") or {}).get("built_in") or {})
    reserved = set((contracts.get("registry") or {}).get("reserved_state_files") or [])
    identities = {}
    for path in sorted(base.rglob("*")):
        within(root, path)
        if not path.is_file():
            continue
        relative = path.relative_to(base).as_posix()
        if path.suffix != ".yaml":
            classification = "malformed"
        else:
            try:
                data = yaml_value(path.read_text(encoding="utf-8-sig"))
            except Exception:
                data = None
            schema = data.get("schema_version") if isinstance(data, dict) else None
            identity = data.get("id") if isinstance(data, dict) else None
            if relative not in reserved and isinstance(identity, str) and identity:
                identities.setdefault(identity, []).append(relative)
            if not isinstance(schema, int):
                classification = "malformed"
            elif relative in reserved:
                if schema == current_state:
                    classification = "current_supported"
                elif isinstance(current_state, int) and schema < current_state:
                    classification = "older_migratable"
                else:
                    classification = "unsupported_future"
            elif not isinstance(current_definition, int):
                classification = "custom_profile"
            elif schema > current_definition:
                classification = "unsupported_future"
            elif schema < current_definition:
                classification = "older_migratable"
            elif data.get("profile") not in built_in:
                classification = "custom_profile"
            else:
                classification = "current_supported"
        results.append({"path": f"{INTEGRATIONS}/{relative}", "classification": classification})
    duplicates = {identity for identity, paths in identities.items() if len(paths) > 1}
    for item in results:
        if duplicates and item["classification"] == "current_supported":
            source = yaml_value(within(root, item["path"]).read_text(encoding="utf-8-sig"))
            if isinstance(source, dict) and source.get("id") in duplicates:
                item["classification"] = "ownership_collision"
    return results


def _protected_labels(root, manifests):
    labels = set()
    for manifest in manifests:
        for declared in manifest["ownership"]["project_owned_paths"]:
            base = within(root, declared.rstrip("/"))
            if not base.exists():
                continue
            if base.is_file():
                labels.add(declared)
            else:
                for path in base.rglob("*"):
                    within(root, path)
                    if path.is_file() and "__pycache__" not in path.parts:
                        labels.add(path.relative_to(root).as_posix())
    return {label for label in labels if not label.startswith(f"{ACTIVE}/local/")}


def preview_migrate(root, router_shared=None, include_diff=False, sets=None):
    """Compute the complete migration result without writing anything."""
    root = Path(root).resolve()
    active = within(root, ACTIVE)
    staged = within(root, STAGED)
    blocking, advisory = [], []

    def block(finding_id, detail, **extra):
        item = {"id": finding_id, "detail": detail}
        item.update(extra)
        blocking.append(item)

    def note(finding_id, detail, **extra):
        item = {"id": finding_id, "detail": detail}
        item.update(extra)
        advisory.append(item)

    if not within(active, "framework/manifest.yaml").exists():
        raise ForgeError("Active .ai bundle with framework/manifest.yaml is required")
    if not within(staged, "framework/manifest.yaml").exists():
        raise ForgeError("Staged .ai-next bundle with framework/manifest.yaml is required")
    if active.resolve() == staged.resolve():
        raise ForgeError("Active and staged bundles resolve to the same path")
    old_manifest = load_yaml(active, "framework/manifest.yaml")
    new_manifest = load_yaml(staged, "framework/manifest.yaml")
    old_version = str(old_manifest["framework"]["version"])
    new_version = str(new_manifest["framework"]["version"])
    if version_tuple(new_version) == version_tuple(old_version):
        block("already_current", f"Active framework version {old_version} equals the staged version; nothing to migrate")
    elif version_tuple(new_version) < version_tuple(old_version):
        block("downgrade_refused", f"Staged version {new_version} is older than active {old_version}; downgrades are refused")
    stray = _staged_stray_files(staged, new_manifest)
    if stray:
        block("unexpected_staged_file", "Staged bundle contains files outside its declared framework-owned paths", paths=stray)

    active_owned = _bundle_files(active, old_manifest)
    staged_files = _bundle_files(staged, new_manifest)
    replacements = {}
    for label, staged_hash in sorted(staged_files.items()):
        if active_owned.get(label) != staged_hash:
            source = within(staged, label[len(f"{ACTIVE}/"):])
            replacements[label] = source.read_bytes()
    prior_bundle = {}
    lock_bytes = None
    old_lock = {}
    if within(root, LOCK).exists():
        lock_bytes = within(root, LOCK).read_bytes()
        old_lock = yaml_value(lock_bytes.decode("utf-8-sig"))
        if not isinstance(old_lock, dict):
            raise ForgeError("Existing .ai/framework.lock must be a mapping")
        prior_bundle = (old_lock.get("bundle_state") or {}).get("files") or {}
    deletions, preserved = [], []
    for label, current_hash in sorted(active_owned.items()):
        if label in staged_files:
            continue
        if prior_bundle.get(label) == current_hash:
            deletions.append(label)
        else:
            preserved.append(label)

    known_outputs = (old_lock.get("python_adapter_state") or {}).get("outputs") or {}
    legacy = [name for name in ("codex-router", "claude-router") if within(root, f"{ACTIVE}/custom/{name}.md").exists()]
    if legacy:
        block("legacy_overlay_present", "Reconcile legacy platform-specific overlays into router-shared.md first",
              paths=[f"{ACTIVE}/custom/{name}.md" for name in legacy])
    overlay_bytes = None
    overlay_source = None
    if router_shared is not None:
        overlay_source = within(root, router_shared)
        if not overlay_source.is_file():
            raise ForgeError(f"Router overlay file is missing: {router_shared}")
        overlay_bytes = overlay_source.read_bytes()
        if not overlay_bytes.strip():
            raise ForgeError("Router overlay file is empty")
        if b"{{" in overlay_bytes:
            raise ForgeError("Router overlay file contains unresolved template markers")
    elif within(root, OVERLAY).exists():
        overlay_bytes = within(root, OVERLAY).read_bytes()
    else:
        block("router_extraction_required",
              "Extract preserved project router content into .ai/custom/router-shared.md and pass it via --router-shared",
              sources=["AGENTS.md", "CLAUDE.md"])

    if not within(root, CONFIG).exists():
        raise ForgeError("Active project requires .ai/project.yaml; use bootstrap instead")
    config_text = text(root, CONFIG)
    entries = migration_entries(staged, old_version, new_version)
    additions = {}
    decisions = []
    for _, entry in entries:
        additions.update(entry.get("config_additions") or {})
        decisions.extend(entry.get("config_decisions") or [])
    sets = dict(sets or {})
    allowed_keys = {decision["key"] for decision in decisions} | SAFE_SET_KEYS
    unknown = sorted(set(sets) - allowed_keys)
    if unknown:
        raise ForgeError("--set refuses keys outside the declared migration decisions: " + ", ".join(unknown))
    new_config_text = update_yaml_text(config_text, "version", new_version)
    parsed = yaml_value(new_config_text)
    applied_additions = []
    for key in sorted(additions):
        if _config_value(parsed, key) is _MISSING:
            new_config_text = update_yaml_text(new_config_text, key, additions[key])
            applied_additions.append(key)
    for key in sorted(sets):
        new_config_text = update_yaml_text(new_config_text, key, yaml_value(sets[key]))
    new_config = yaml_value(new_config_text)
    if not isinstance(new_config, dict):
        raise ForgeError("Reconciled .ai/project.yaml must remain a mapping")

    outputs = {}
    render_inputs = None
    if not blocking:
        overlay_text = None
        if overlay_bytes is not None:
            overlay_text = overlay_bytes.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        try:
            outputs, render_inputs = render(staged, root, config=new_config, overlay=overlay_text)
        except ForgeError as exc:
            unresolved = [decision for decision in decisions
                          if _config_value(new_config, decision["key"]) in (None, "", _MISSING)]
            if unresolved:
                block("config_decision_required", str(exc),
                      suggestions=[{"key": decision["key"], "suggest": decision.get("suggest", ""),
                                    "note": decision.get("note", "")} for decision in unresolved])
            else:
                block("render_validation", str(exc))

    integrations = _classify_integrations(root, staged)
    for item in integrations:
        if item["classification"] == "ownership_collision":
            block("integration_ownership_collision",
                  "Staged bundle ships a file at an existing project-owned integration path", paths=[item["path"]])
        elif item["classification"] == "older_migratable":
            note("integration_older_migratable",
                 "Older integration schema is preserved byte-for-byte; schema migration is a separate approval",
                 paths=[item["path"]])
        elif item["classification"] in ("malformed", "unsupported_future", "custom_profile"):
            note(f"integration_{item['classification']}",
                 "Integration file blocks only its consumers; the framework migration is unaffected",
                 paths=[item["path"]])

    for name, entry in entries:
        for message in entry.get("breaking") or []:
            note("breaking_change", message, version=name)
        for message in entry.get("notes") or []:
            note("version_note", message, version=name)
        for command in entry.get("backfill_commands") or []:
            note("backfill_available", command.get("description", ""), command=command.get("command", ""), version=name)

    if within(root, "BACKLOG.md").exists():
        terminal = [row["ID"].strip("`") for row in backlog_rows(root) if row["Status"] in TERMINAL_EPIC]
        terminal += [row["ID"].strip("`") for row in defect_rows(root) if row["Status"] in TERMINAL_BUG]
        if terminal:
            note("terminal_backlog_rows",
                 "Legacy terminal rows remain valid in the live Backlog until a one-time backfill",
                 paths=terminal, command=f"python {ACTIVE}/tools/forge.py backlog archive-all")

    git = git_status(root)
    dirty = [change["path"] for change in git.get("changes", [])
             if not change["path"].startswith(STAGED)] if git.get("available") else []
    if git.get("available") and dirty:
        note("dirty_git_tree",
             "Working tree is not clean; the recoverable baseline remains the user's responsibility", paths=dirty[:20])

    updates = dict(replacements)
    updates.update(outputs)
    if router_shared is not None and overlay_bytes is not None:
        updates[OVERLAY] = overlay_bytes
    if new_config_text != config_text:
        updates[CONFIG] = new_config_text.encode()
    collisions = []
    observed = {}
    changes = []
    for name in sorted(updates):
        path = within(root, name)
        before = path.read_bytes() if path.exists() else None
        observed[name] = digest(before) if before is not None else None
        data = updates[name]
        if before == data:
            continue
        if before is not None and name in outputs and name in known_outputs and observed[name] != known_outputs[name]:
            collisions.append(name)
        item = {"path": name, "before": observed[name], "after": digest(data), "bytes": len(data)}
        if include_diff:
            try:
                item["diff"] = "".join(difflib.unified_diff((before or b"").decode("utf-8").splitlines(True),
                                                            data.decode("utf-8").splitlines(True),
                                                            fromfile=name, tofile=name))
            except UnicodeDecodeError:
                item["diff"] = None
        changes.append(item)

    protected_labels = sorted(_protected_labels(root, (old_manifest, new_manifest))
                              - set(updates) - set(deletions) - {LOCK, CONFIG, OVERLAY})
    protected = snapshot(root, protected_labels)

    state = {"old_version": old_version, "new_version": new_version,
             "updates": {name: digest(updates[name]) for name in sorted(updates)},
             "observed": observed, "deletions": sorted(deletions),
             "protected": protected["fingerprint"], "old_lock": digest(lock_bytes) if lock_bytes else None,
             "config_before": digest(config_text.encode()),
             "router_shared": digest(overlay_bytes) if overlay_bytes is not None else None,
             "staged": staged_files, "active_owned": active_owned,
             "integrations": integrations, "collisions": sorted(collisions)}
    token = None if blocking else digest(canonical(state).encode())
    result = {"schema_version": 1, "command": "migrate",
              "old_version": old_version, "new_version": new_version,
              "changes": changes, "deletions": deletions, "preserved_unknown": preserved,
              "collisions": collisions,
              "config": {"version": new_version, "sets_applied": sets, "additions_applied": applied_additions},
              "integrations": integrations,
              "findings": {"blocking": blocking, "advisory": advisory},
              "protected_fingerprint": protected["fingerprint"],
              "git_clean": (not dirty) if git.get("available") else None,
              "rollback": "journal at .ai/local/migrate-transaction; .ai-next retained on failure",
              "preview_token": token, "passed": not blocking}
    context = {"updates": updates, "protected": protected, "protected_labels": protected_labels,
               "old_lock": old_lock, "render_inputs": render_inputs, "render_outputs": outputs,
               "lock_bytes": lock_bytes, "staged_root": staged, "new_version": new_version}
    return result, context


def apply_migrate(root, expected_token, sets=None, router_shared=None, approved_collisions=()):
    """Apply one approved migration preview as a single guarded transaction."""
    root = Path(root).resolve()
    result, context = preview_migrate(root, router_shared=router_shared, sets=sets)
    if result["preview_token"] is None:
        raise ForgeError("Blocking findings prevent apply: " +
                         ", ".join(finding["id"] for finding in result["findings"]["blocking"]))
    if result["preview_token"] != expected_token:
        raise ForgeError("Stale preview: inputs or outputs changed")
    approved = set(approved_collisions)
    unapproved = [name for name in result["collisions"] if name not in approved]
    if unapproved:
        raise ForgeError("Unapproved collisions: " + ", ".join(unapproved))
    invalid = sorted(approved - set(result["collisions"]) - set(result["preserved_unknown"]))
    if invalid:
        raise ForgeError("--approve-collision names files that are neither collisions nor preserved unknowns: "
                         + ", ".join(invalid))
    updates = dict(context["updates"])
    for label in result["deletions"]:
        updates[label] = None
    approved_deletions = []
    for label in result["preserved_unknown"]:
        if label in approved:
            updates[label] = None
            approved_deletions.append(label)
    lock = dict(context["old_lock"])
    lock["bundle_state"] = bundle_state(context["staged_root"], root)
    if context["render_inputs"] is not None:
        lock["python_adapter_state"] = {
            "schema_version": 1,
            "input_fingerprint": context["render_inputs"]["fingerprint"],
            "outputs": {name: digest(data) for name, data in sorted(context["render_outputs"].items())}}
    updates[LOCK] = (canonical(lock) + "\n").encode()

    transaction = Transaction(root, "migrate").claim()
    success = False
    try:
        def recheck():
            fresh, _ = preview_migrate(root, router_shared=router_shared, sets=sets)
            if fresh["preview_token"] != expected_token:
                raise ForgeError("Repository changed while preparing transaction")

        transaction.write(updates, recheck=recheck)
        from forge_core import validate
        validation = validate(root)
        if not validation["passed"]:
            raise ForgeError("Post-migration validation failed: " + "; ".join(validation["errors"]))
        drift = [change["path"] for change in adapter_preview(root)[0]["changes"]]
        if drift:
            raise ForgeError("Generated adapter drift after migration: " + ", ".join(drift))
        after = snapshot(root, context["protected_labels"])
        if after["fingerprint"] != context["protected"]["fingerprint"]:
            raise ForgeError("Protected paths changed during the migration")
        removed = True
        try:
            shutil.rmtree(within(root, STAGED))
        except OSError:
            removed = False
        success = True
        return {"applied": sorted(name for name, data in updates.items() if data is not None),
                "deleted": sorted(name for name, data in updates.items() if data is None),
                "staging_removed": removed,
                "new_version": result["new_version"],
                "rollout": "backup journal retained at .ai/local/migrate-transaction until this command succeeds"}
    except BaseException:
        if transaction.journal_path.exists():
            transaction.rollback()
        raise
    finally:
        transaction.finish(success)


def recover_migrate(root):
    """Explicitly recover an interrupted migration from its journal.

    Managed targets are the exact framework-owned files that still exist plus
    anything under a manifest-declared framework-owned directory (a journaled
    deletion may reference a file that no longer exists), the generated adapter
    outputs, the lock, the project configuration, and the router overlay.
    """
    root = Path(root).resolve()
    allowed = {LOCK, CONFIG, OVERLAY}
    owned_directories = []
    for bundle in (within(root, ACTIVE), within(root, STAGED)):
        if not (bundle / "framework/manifest.yaml").exists():
            continue
        manifest = load_yaml(bundle, "framework/manifest.yaml")
        allowed |= set(_bundle_files(bundle, manifest))
        owned_directories.extend(path.rstrip("/") for path in manifest["ownership"]["framework_owned_paths"])
        for declared in manifest["ownership"]["generated_adapter_outputs"]:
            base = within(root, declared.rstrip("/"))
            if not base.exists():
                continue
            for path in base.rglob("*"):
                within(root, path)
                if path.is_file():
                    allowed.add(path.relative_to(root).as_posix())
    transaction = Transaction(root, "migrate")
    journal = json.loads(transaction.journal_path.read_text(encoding="utf-8"))
    for item in journal["files"]:
        name = item["path"]
        if name not in allowed and not any(name == prefix or name.startswith(prefix + "/") for prefix in owned_directories):
            raise ForgeError(f"Unmanaged target in recovery journal: {name}")
    return transaction.restore(None)
