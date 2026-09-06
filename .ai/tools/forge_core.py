"""Read-only, deterministic repository operations. No model or network calls."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import yaml


class ForgeError(ValueError):
    pass


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently changing a contract."""


def _mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ForgeError(f"Non-string or duplicate YAML key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def within(root, name):
    """Resolve only project paths, rejecting symlinks/junctions and traversal."""
    root = Path(root).resolve()
    path = Path(name)
    if not path.is_absolute():
        path = root / path
    # Do not normalize away '..' before checking the boundary.
    if ".." in path.parts:
        raise ForgeError(f"Parent traversal is not supported: {name}")
    try:
        relative = path.relative_to(root)
        current = root
        for part in relative.parts:
            current = current / part
            if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
                raise ForgeError(f"Linked path requires manual handling: {name}")
        path.resolve().relative_to(root)
    except ValueError as exc:
        raise ForgeError(f"Path outside project: {name}") from exc
    return path


def text(root, name):
    return within(root, name).read_text(encoding="utf-8-sig")


def yaml_value(content):
    try:
        return yaml.load(content, Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        raise ForgeError(f"Invalid YAML: {exc}") from exc


def load_yaml(root, name):
    value = yaml_value(text(root, name))
    if not isinstance(value, dict):
        raise ForgeError(f"Expected mapping: {name}")
    return value


def frontmatter(content):
    lines = content.splitlines()
    if not lines or lines[0] != "---":
        raise ForgeError("Missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ForgeError("Unclosed YAML frontmatter") from exc
    value = yaml_value("\n".join(lines[1:end]))
    if not isinstance(value, dict):
        raise ForgeError("Frontmatter must be a mapping")
    return value


def snapshot(root, paths):
    """Explicit current file set: content + name + executable bit + absence.

    Not a diff, dependency resolver, approval, or proof of a complete scope.
    Directories are deliberately refused; additions must enter the path set.
    """
    if not paths:
        raise ForgeError("Fingerprint requires an explicit non-empty path set")
    entries = {}
    for name in paths:
        path = within(root, name)
        relative = path.relative_to(Path(root).resolve()).as_posix()
        if path.exists() and not path.is_file():
            raise ForgeError(f"Expected regular file, not directory: {relative}")
        if path.exists():
            before = path.stat()
            hasher = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    hasher.update(block)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ForgeError(f"File changed during fingerprint: {relative}")
            entries[relative] = {"path": relative, "kind": "file", "sha256": hasher.hexdigest(),
                                 "executable": bool(after.st_mode & 0o111), "bytes": after.st_size}
        else:
            entries[relative] = {"path": relative, "kind": "missing"}
    files = [entries[key] for key in sorted(entries)]
    return {"algorithm": "forge-files-v1", "fingerprint": digest(canonical(files).encode()), "files": files}


def sections(content):
    """ATX sections, including subheadings; fenced code headings are ignored."""
    lines = content.splitlines(keepends=True)
    headings, fence = [], None
    for index, line in enumerate(lines):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, rest = marker.groups()
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not rest.strip():
                fence = None
            continue
        if fence:
            continue
        heading = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading:
            headings.append((index, len(heading[1]), heading[2]))
    result = []
    for position, (start, level, title) in enumerate(headings):
        end = next((i for i, depth, _ in headings[position + 1:] if depth <= level), len(lines))
        result.append({"heading": title, "level": level, "line": start + 1,
                       "end_line": end, "content": "".join(lines[start:end])})
    return result


def section(root, name, heading=None, offset=0, limit=12000):
    content = text(root, name)
    values = sections(content)
    if heading is None:
        return {"path": name, "sections": [{k: v for k, v in s.items() if k != "content"} for s in values]}
    matches = [s for s in values if s["heading"] == heading]
    if not matches:
        raise ForgeError(f"No heading {heading!r} in {name}")
    selected = "\n".join(s["content"] for s in matches)
    end = min(offset + limit, len(selected))
    return {"path": name, "heading": heading, "matches": len(matches), "source_sha256": digest(content.encode()),
            "content": selected[offset:end], "total_chars": len(selected), "offset": offset,
            "next_offset": end if end < len(selected) else None, "complete": end == len(selected)}


def inventory(root, include_completed=False):
    roots = ["execution/planned", "execution/active", "execution/paused", "investigations"]
    if include_completed:
        roots.append("execution/completed")
    records, errors = [], []
    for directory in roots:
        base = within(root, directory)
        if not base.exists():
            continue
        for walk_root, dirs, files in os.walk(base, followlinks=False):
            for entry in list(dirs):
                try:
                    within(root, Path(walk_root) / entry)
                except ForgeError as exc:
                    errors.append(str(exc))
                    dirs.remove(entry)
            for filename in sorted(files):
                if not filename.endswith(".md"):
                    continue
                path = (Path(walk_root) / filename).relative_to(root).as_posix()
                try:
                    content = text(root, path)
                    meta = frontmatter(content)
                    fields = ("id", "epic_id", "document_type", "document_status", "definition_status", "status",
                              "delivery_track", "blocked_by", "research_refs", "outcome", "subject", "area", "relevant_paths")
                    record = {"path": path, "sha256": digest(content.encode()),
                              "metadata": {key: meta[key] for key in fields if key in meta}}
                    records.append(record)
                except (ForgeError, OSError, UnicodeError) as exc:
                    errors.append(f"{path}: {exc}")
    return sorted(records, key=lambda r: r["path"]), errors


def git_status(root):
    try:
        result = subprocess.run(["git", "-c", f"safe.directory={Path(root).resolve().as_posix()}",
                                 "-c", "core.fsmonitor=false", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                                cwd=root, capture_output=True, timeout=15)
        if result.returncode:
            return {"available": False, "error": result.stderr.decode("utf-8", "replace").strip()}
        chunks = result.stdout.decode("utf-8", "replace").split("\0")
        changes, index = [], 0
        while index < len(chunks) and chunks[index]:
            value = chunks[index]
            item = {"status": value[:2], "path": value[3:]}
            if "R" in value[:2] or "C" in value[:2]:
                index += 1
                item["from"] = chunks[index]
            changes.append(item)
            index += 1
        return {"available": True, "changes": changes}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "error": str(exc)}


def backlog_rows(root):
    result, headers, in_roadmap = [], None, False
    for line in text(root, "BACKLOG.md").splitlines():
        if line.startswith("## "):
            in_roadmap = line.strip() == "## Epic Roadmap"
            continue
        if not in_roadmap or not line.strip().startswith("|"):
            continue
        cells = [v.strip().replace("\\|", "|") for v in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if headers is None:
            headers = cells
        elif not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in cells):
            if len(cells) != len(headers):
                raise ForgeError("Malformed Epic Roadmap row; inspect BACKLOG.md")
            result.append(dict(zip(headers, cells)))
    if headers is None or not {"ID", "Priority", "Readiness", "Status", "Dependencies", "Blocked by"}.issubset(headers):
        raise ForgeError("Missing Epic Roadmap columns; inspect BACKLOG.md")
    return result


def context(root, offset=0, limit=30, include_completed=False):
    records, errors = inventory(root, include_completed)
    git = git_status(root)
    if not git["available"]:
        errors.append("Git status unavailable: " + git["error"])
    page = records[offset:offset + limit]
    return {"schema_version": 1, "scope": "inventory, not lifecycle approval", "records": page,
            "inventory_fingerprint": digest(canonical(records).encode()),
            "total": len(records), "next_offset": offset + limit if offset + limit < len(records) else None,
            "errors": errors, "git": git,
            "read_next": ["BACKLOG.md"] + [r["path"] for r in page if r["path"].startswith(("execution/active/", "execution/paused/"))]}


def validate(root, project=False):
    errors = []
    manifest = load_yaml(root, ".ai/framework/manifest.yaml")
    contracts = load_yaml(root, ".ai/framework/contracts.yaml")
    for category, directory, suffix in (("subagents", "agents", ".yaml"), ("skills", "skills", "/SKILL.md")):
        ids = manifest[category]
        if len(ids) != len(set(ids)):
            errors.append(f"Duplicate {category} IDs")
        for identity in ids:
            path = f".ai/framework/{directory}/{identity}{suffix}"
            try:
                data = load_yaml(root, path) if category == "subagents" else frontmatter(text(root, path))
                if data.get("id" if category == "subagents" else "name") != identity:
                    errors.append(f"ID mismatch: {path}")
            except (OSError, ForgeError) as exc:
                errors.append(f"{path}: {exc}")
    if project:
        records, problems = inventory(root, include_completed=True)
        errors.extend(problems)
        rows = backlog_rows(root)
        roadmap = {}
        active = {"ACTIVE", "VALIDATING", "FUZZING", "AWAITING EPIC ACCEPTANCE"}
        for row in rows:
            identity = row["ID"].strip("`")
            if identity in roadmap:
                errors.append(f"Duplicate Backlog Epic: {identity}")
            roadmap[identity] = row
            if row["Status"] not in contracts["enums"]["epic_status"]:
                errors.append(f"Invalid Epic status: {identity}")
            if row["Readiness"] not in contracts["enums"]["epic_readiness"]:
                errors.append(f"Invalid Epic readiness: {identity}")
        if sum(row["Status"] in active for row in rows) > 1:
            errors.append("Multiple active-work Epics")
        ids, epics, writing = set(), set(), []
        for record in records:
            meta, path = record["metadata"], record["path"]
            identity = meta.get("id")
            if identity:
                if identity in ids:
                    errors.append(f"Duplicate ID: {identity}")
                ids.add(identity)
            if meta.get("document_type") == "epic_plan":
                epic = meta.get("epic_id")
                if epic in epics:
                    errors.append(f"Duplicate Epic workspace: {epic}")
                epics.add(epic)
                row = roadmap.get(epic)
                state = path.split("/")[1]
                if not row:
                    errors.append(f"Workspace missing from Backlog: {path}")
                elif (state == "planned" and (row["Status"] != "PLANNED" or row["Readiness"] != "READY"
                      or meta.get("document_status") != "approved")) or (state == "active" and row["Status"] not in active) or (state == "paused" and row["Status"] != "PAUSED") or (state == "completed" and row["Status"] != "COMPLETED"):
                    errors.append(f"Workspace/Backlog mismatch: {path}")
            if meta.get("document_type") == "task":
                if meta.get("status") not in contracts["enums"]["task_status"]:
                    errors.append(f"Invalid Task status: {path}")
                if meta.get("delivery_track", "standard") not in contracts["enums"]["delivery_tracks"]:
                    errors.append(f"Invalid delivery track: {path}")
                if path.startswith("execution/planned/") and (meta.get("status") != "TODO" or meta.get("definition_status") != "approved"):
                    errors.append(f"Planned Task must be approved TODO: {path}")
                if meta.get("status") == "IN PROGRESS":
                    writing.append(path)
                workspace_id = re.match(r"^(EPIC-\d+)(?:-|$)", path.split("/")[2])
                if not identity or not workspace_id or meta.get("epic_id") != workspace_id[1]:
                    errors.append(f"Task identity/workspace mismatch: {path}")
            if meta.get("document_type") == "investigation" and meta.get("outcome") not in contracts["enums"]["investigation_outcomes"]:
                errors.append(f"Invalid investigation outcome: {path}")
        if len(writing) > 1:
            errors.append("Multiple code-writing Tasks")
        for epic, row in roadmap.items():
            if row["Status"] in active | {"PAUSED", "COMPLETED"} and epic not in epics:
                errors.append(f"Missing Epic workspace: {epic}")
    return {"passed": not errors, "errors": errors,
            "coverage": "manifest IDs and source syntax" + (", lifecycle inventory and Backlog consistency" if project else ""),
            "requires_judgment": ["scope and permissions", "test integrity and coverage", "review protocol and evidence freshness", "integration and mutation semantics"]}


def budget(root, paths):
    rows = []
    for path in paths:
        content = text(root, path)
        rows.append({"path": path, "bytes": len(content.encode()), "chars": len(content),
                     "lines": len(content.splitlines()), "estimated_tokens": (len(content) + 3) // 4})
    return {"files": rows, "estimated_tokens": sum(r["estimated_tokens"] for r in rows),
            "estimate_method": "ceil(characters / 4); heuristic, not model tokenizer or billed usage"}
