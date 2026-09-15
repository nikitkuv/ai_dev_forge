"""Read-only, deterministic repository operations. No model or network calls."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

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


def atomic_replace(path, data):
    """Durably replace one file's bytes via a same-directory temporary."""
    path = Path(path)
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


class Transaction:
    """One guarded multi-file write with a backup journal, rollback, and recovery.

    Never decides anything: callers preview changes, pass exact byte updates,
    and keep authorization. A claimed guard directory prevents concurrent
    transactions of the same kind; a caught failure restores journaled files;
    an interrupted operation leaves the journal for explicit recovery, which
    refuses to overwrite subsequent user edits.
    """

    def __init__(self, root, name):
        if not re.fullmatch(r"[a-z0-9-]+", name):
            raise ForgeError("Unsafe transaction name")
        self.root = Path(root).resolve()
        self.name = name
        self.guard = within(self.root, f".ai/local/{name}-transaction")
        self.journal_path = self.guard / "journal.json"

    def claim(self):
        self.guard.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.guard.mkdir()
        except FileExistsError as exc:
            raise ForgeError(f"{self.name} transaction exists; inspect/recover it before retrying") from exc
        return self

    def write(self, updates, recheck=None, replace=atomic_replace):
        """Back up, journal, recheck, then atomically write {relative_path: bytes}."""
        if not self.journal_path.parent.exists():
            raise ForgeError("Claim the transaction before writing")
        originals = {}
        for index, name in enumerate(updates):
            path = within(self.root, name)
            before = path.read_bytes() if path.exists() else None
            originals[name] = before
            if before is not None:
                (self.guard / f"{index}.bak").write_bytes(before)
        journal = {"files": [{"path": n, "backup": f"{i}.bak" if b is not None else None,
                              "after": digest(updates[n])} for i, (n, b) in enumerate(originals.items())]}
        self.journal_path.write_text(canonical(journal), encoding="utf-8")
        # Recheck the whole preview after preparing backups, before the first write.
        if recheck is not None:
            recheck()
        written = []
        try:
            for name, data in updates.items():
                path = within(self.root, name)
                if (path.read_bytes() if path.exists() else None) != originals[name]:
                    raise ForgeError(f"Concurrent edit: {name}")
                replace(path, data)
                written.append(name)
        except BaseException:
            self._restore(journal, replace)
            raise
        return list(updates)

    def _restore(self, journal, replace=atomic_replace):
        """Put every journaled file back to its backup, refusing concurrent edits."""
        for item in reversed(journal["files"]):
            path = within(self.root, item["path"])
            current = path.read_bytes() if path.exists() else None
            backup = (self.guard / item["backup"]).read_bytes() if item["backup"] else None
            if current is not None and current != backup and digest(current) != item["after"]:
                raise ForgeError(f"Concurrent edit during rollback: {item['path']}; backups retained at {self.guard}")
            if backup is not None:
                replace(path, backup)
            elif path.exists():
                path.unlink()

    def restore(self, allowed=None):
        """Explicitly recover an interrupted transaction from its journal."""
        journal = json.loads(self.journal_path.read_text(encoding="utf-8"))
        restored = []
        # Validate every target first so recovery cannot overwrite a later user edit.
        for item in journal["files"]:
            if allowed is not None and item["path"] not in allowed:
                raise ForgeError(f"Unmanaged target in recovery journal: {item['path']}")
            if item["backup"] is not None and not re.fullmatch(r"\d+\.bak", item["backup"]):
                raise ForgeError("Invalid backup name in recovery journal")
            path = within(self.root, item["path"])
            before = (self.guard / item["backup"]).read_bytes() if item["backup"] else None
            current = path.read_bytes() if path.exists() else None
            if current != before and (current is None or digest(current) != item["after"]):
                raise ForgeError(f"Recovery conflicts with later edit: {item['path']}")
        for item in reversed(journal["files"]):
            path = within(self.root, item["path"])
            if item["backup"]:
                atomic_replace(path, (self.guard / item["backup"]).read_bytes())
            elif path.exists():
                path.unlink()
            restored.append(item["path"])
        self._clear()
        return {"restored": restored}

    def rollback(self):
        """Restore all journaled files after a caught failure and clear the journal."""
        if not self.journal_path.exists():
            self._clear()
            return {"restored": []}
        journal = json.loads(self.journal_path.read_text(encoding="utf-8"))
        self._restore(journal)
        restored = [item["path"] for item in reversed(journal["files"])]
        self._clear()
        return {"restored": restored}

    def finish(self, success):
        """Clear the guard on success or when nothing was journaled; keep it otherwise."""
        if success or not self.journal_path.exists():
            self._clear()

    def _clear(self):
        if self.guard.exists():
            for path in self.guard.iterdir():
                path.unlink()
            self.guard.rmdir()



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
    roots = ["execution/planned", "execution/active", "execution/paused", "investigations", "intents"]
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
                              "delivery_track", "blocked_by", "research_refs", "outcome", "subject", "area",
                              "relevant_paths", "origin", "promoted_to", "sources")
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


def table_rows(content, heading, required, optional=False):
    """Parse one Markdown table under `## <heading>` into row dicts."""
    result, headers, active = [], None, False
    for line in content.splitlines():
        if line.startswith("## "):
            active = line.strip() == f"## {heading}"
            continue
        if not active or not line.strip().startswith("|"):
            continue
        cells = [v.strip().replace("\\|", "|") for v in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if headers is None:
            headers = cells
        elif not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in cells):
            if len(cells) != len(headers):
                raise ForgeError(f"Malformed {heading} row; inspect BACKLOG.md")
            result.append(dict(zip(headers, cells)))
    if headers is None:
        if optional:
            return []
        raise ForgeError(f"Missing {heading} table; inspect BACKLOG.md")
    if not set(required).issubset(headers):
        raise ForgeError(f"Missing {heading} columns; inspect BACKLOG.md")
    return result


def backlog_rows(root):
    return table_rows(text(root, "BACKLOG.md"), "Epic Roadmap",
                      {"ID", "Priority", "Readiness", "Status", "Dependencies", "Blocked by"})


def defect_rows(root):
    return table_rows(text(root, "BACKLOG.md"), "Defect Queue", {"ID", "Status"}, optional=True)


ARCHIVE_PATH = "BACKLOG-ARCHIVE.md"
ARCHIVE_HEADER = ("# Backlog Archive\n\n"
                  "Append-only archive of terminal Backlog rows. Rows move here verbatim from `BACKLOG.md`; "
                  "they are never edited or deleted.\n")
TERMINAL_EPIC_STATUSES = {"COMPLETED", "CANCELLED"}
TERMINAL_BUG_STATUSES = {"RESOLVED", "REJECTED", "DUPLICATE", "WONT_FIX"}
ARCHIVE_SECTIONS = {"Epic Roadmap": {"ID", "Status"}, "Defect Queue": {"ID", "Status"}}


def archive_records(content):
    """Parse archived rows: one `## <year>` section per year, `### <table>` subsections."""
    records, year, section, headers = [], None, None, None
    for line in content.splitlines():
        if line.startswith("## "):
            year, section, headers = line[3:].strip(), None, None
            continue
        if line.startswith("### "):
            section, headers = line[4:].strip(), None
            continue
        if year is None or section is None or not line.strip().startswith("|"):
            continue
        cells = [v.strip().replace("\\|", "|") for v in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if headers is None:
            headers = cells
        elif not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in cells):
            if len(cells) != len(headers):
                raise ForgeError(f"Malformed archived {section} row; inspect {ARCHIVE_PATH}")
            records.append({"year": year, "section": section, "cells": dict(zip(headers, cells))})
    return records


def archive_append(content, year, section, header_line, separator_line, row_line):
    """Append one verbatim row to a year/section table, creating structure as needed."""
    if section not in ARCHIVE_SECTIONS:
        raise ForgeError(f"Unsupported archive section: {section}")
    lines = (content or ARCHIVE_HEADER).splitlines(keepends=True)
    if not lines or not lines[-1].endswith("\n"):
        lines = [line + "\n" for line in (content.rstrip("\n").splitlines() if content else [ARCHIVE_HEADER.rstrip("\n")])]
    block = [f"### {section}\n", header_line.rstrip("\n") + "\n", separator_line.rstrip("\n") + "\n",
             row_line.rstrip("\n") + "\n", "\n"]
    # Locate the year section, then the table subsection, then the table's last row.
    year_start = next((i for i, line in enumerate(lines) if line.rstrip() == f"## {year}"), None)
    if year_start is None:
        return "".join(lines).rstrip("\n") + "\n\n" + f"## {year}\n\n" + "".join(block)
    year_end = next((i for i in range(year_start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    section_start = next((i for i in range(year_start + 1, year_end) if lines[i].rstrip() == f"### {section}"), None)
    if section_start is None:
        insert_at = year_end
        for index in range(year_end - 1, year_start, -1):
            if lines[index].strip():
                insert_at = index + 1
                break
        return "".join(lines[:insert_at]).rstrip("\n") + "\n\n" + "".join(block) + "".join(lines[insert_at:]).lstrip("\n")
    section_end = next((i for i in range(section_start + 1, year_end) if lines[i].startswith("### ")), year_end)
    last_row = None
    for index in range(section_end - 1, section_start, -1):
        if lines[index].strip().startswith("|"):
            last_row = index
            break
        if lines[index].strip():
            break
    if last_row is None:  # Heading exists without a table yet.
        return "".join(lines[:section_start + 1]) + "\n" + "".join(block[1:]) + "".join(lines[section_start + 1:]).lstrip("\n")
    insert_at = last_row + 1
    return "".join(lines[:insert_at]) + row_line.rstrip("\n") + "\n" + "".join(lines[insert_at:])


def archived_backlog_rows(root, section=None):
    """Archived rows as [{year, section, cells}], optionally filtered by section."""
    archive = within(root, ARCHIVE_PATH)
    if not archive.exists():
        return []
    records = archive_records(text(root, ARCHIVE_PATH))
    return [record for record in records if section is None or record["section"] == section]


def workflow_state(content):
    """Parse the YAML block of the Workflow State section; never guesses legacy layouts."""
    values = [s for s in sections(content) if s["heading"] == "Workflow State"]
    if not values:
        raise ForgeError("Missing Workflow State section")
    block, collecting = [], False
    for line in values[0]["content"].splitlines():
        if line.lstrip().startswith("```"):
            if not collecting:
                collecting = True
                continue
            break
        if collecting:
            block.append(line)
    if not collecting or not block:
        raise ForgeError("Workflow State section lacks a YAML block")
    value = yaml_value("\n".join(block))
    if not isinstance(value, dict):
        raise ForgeError("Workflow State block must be a mapping")
    return value


def git_capture(root, arguments, timeout=30):
    """Run one read-only Git command with the same safety options as git_status."""
    try:
        result = subprocess.run(["git", "-c", f"safe.directory={Path(root).resolve().as_posix()}",
                                 "-c", "core.fsmonitor=false"] + arguments,
                                cwd=root, capture_output=True, timeout=timeout)
        return {"exit_code": result.returncode,
                "stdout": result.stdout.decode("utf-8", "replace"),
                "stderr": result.stderr.decode("utf-8", "replace")}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": -1, "stdout": "", "stderr": str(ex)}



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


def conformance_errors(root, contracts):
    """Mechanical shape checks that do not need the record inventory."""
    errors = []
    if within(root, "AGENTS.md").exists() and len(text(root, "AGENTS.md").splitlines()) > 150:
        errors.append("AGENTS.md exceeds the 150-line router budget")
    if within(root, "CLAUDE.md").exists() and text(root, "CLAUDE.md").strip() != "@AGENTS.md":
        errors.append("CLAUDE.md must contain exactly @AGENTS.md")
    for pattern in (".claude/agents", ".opencode/agents"):
        base = within(root, pattern)
        if not base.exists():
            continue
        for path in sorted(base.glob("*.md")):
            relative = path.relative_to(Path(root).resolve()).as_posix()
            data = path.read_bytes()
            if data.startswith(b"\xef\xbb\xbf"):
                errors.append(f"Generated agent file has a UTF-8 BOM: {relative}")
            elif not data.startswith(b"---"):
                errors.append(f"Generated agent file lacks frontmatter at byte zero: {relative}")
    decisions = within(root, "decisions")
    indexed = set(re.findall(r"ADR-\d+", text(root, "DECISIONS.md"))) if within(root, "DECISIONS.md").exists() else set()
    if decisions.exists():
        files = {}
        for path in sorted(decisions.glob("ADR-*.md")):
            match = re.match(r"ADR-\d+", path.stem)
            if match:
                files[match.group(0)] = path
        for identity, path in files.items():
            if identity not in indexed:
                errors.append(f"Unindexed ADR: {path.relative_to(Path(root).resolve()).as_posix()}")
        for identity in sorted(indexed - set(files)):
            errors.append(f"Dangling ADR index entry: {identity}")
    if within(root, "BACKLOG.md").exists():
        for row in backlog_rows(root):
            identity = row["ID"].strip("`")
            if row["Status"] in TERMINAL_EPIC_STATUSES:
                errors.append(f"Terminal Epic row in live Backlog: {identity}; "
                              f"archive it via `backlog archive-all` or `backlog archive-row --id {identity}`")
        for row in defect_rows(root):
            identity = row["ID"].strip("`")
            if row["Status"] in TERMINAL_BUG_STATUSES:
                errors.append(f"Terminal Bug row in live Backlog: {identity}; "
                              f"archive it via `backlog archive-all` or `backlog archive-row --id {identity}`")
    archive = within(root, ARCHIVE_PATH)
    if archive.exists():
        content = text(root, ARCHIVE_PATH)
        for line in content.splitlines():
            if line.startswith("## ") and not re.fullmatch(r"## \d{4}", line.strip()):
                errors.append(f"Archive year section must be `## <YYYY>`: {line.strip()!r} in {ARCHIVE_PATH}")
        for record in archive_records(content):
            identity = record["cells"].get("ID", "").strip("`")
            terminal = TERMINAL_EPIC_STATUSES if record["section"] == "Epic Roadmap" else TERMINAL_BUG_STATUSES
            required = ARCHIVE_SECTIONS.get(record["section"])
            if required is None:
                errors.append(f"Unsupported archive table: {record['section']} for {identity} in {ARCHIVE_PATH}")
            elif not set(required).issubset(record["cells"]):
                errors.append(f"Archived {record['section']} row lacks ID/Status columns: {identity} in {ARCHIVE_PATH}")
            elif record["cells"]["Status"] not in terminal:
                errors.append(f"Non-terminal archived row: {identity} is {record['cells']['Status']} in {ARCHIVE_PATH}")
    registry = within(root, "quality/mutation-testing/registry.yaml")
    if registry.exists():
        data = load_yaml(root, "quality/mutation-testing/registry.yaml")
        if data.get("schema_version") != 1:
            errors.append("Mutation registry schema_version must be 1")
        runs = data.get("runs") or []
        identities = [run if isinstance(run, str) else run.get("id") for run in runs]
        if any(not identity for identity in identities) or len(identities) != len(set(identities)):
            errors.append("Mutation registry requires unique non-empty MUT identities")
        numbers = [int(re.search(r"(\d+)$", identity).group(1)) for identity in identities if identity]
        next_id = data.get("next_id")
        if next_id:
            if not re.fullmatch(r"MUT-\d+", str(next_id)):
                errors.append("Mutation registry next_id must be a MUT identity")
            elif numbers and int(re.search(r"(\d+)$", next_id).group(1)) <= max(numbers):
                errors.append("Mutation registry next_id must exceed every retained identity")
        run_dir = within(root, "quality/mutation-testing/runs")
        on_disk = {path.stem for path in run_dir.glob("MUT-*.yaml")} if run_dir.exists() else set()
        for identity in sorted(set(identities) - on_disk):
            if identity:
                errors.append(f"Missing mutation run record: {identity}")
        for identity in sorted(on_disk - set(identities)):
            errors.append(f"Unregistered mutation run record: {identity}")
    return errors


def record_structure_errors(root, record, contracts):
    """Mechanical per-record checks: plan order, Workflow State, investigation shape."""
    errors = []
    meta, path = record["metadata"], record["path"]
    if meta.get("document_type") == "epic_plan":
        content = text(root, path)
        if any(value["heading"] == "Ordered Task Sequence" for value in sections(content)):
            planned = [re.match(r"TASK-\d+", cell.get("Task", "")).group(0)
                       for cell in table_rows(content, "Ordered Task Sequence", {"Order", "Task"})
                       if re.match(r"TASK-\d+", cell.get("Task", ""))]
            task_dir = within(root, str(Path(path).parent / "tasks"))
            if task_dir.exists():
                on_disk = set()
                for item in sorted(task_dir.glob("*.md")):
                    relative = item.relative_to(Path(root).resolve()).as_posix()
                    on_disk.add(frontmatter(text(root, relative)).get("id"))
                for identity in [i for i in planned if i not in on_disk]:
                    errors.append(f"Plan Task missing from workspace: {identity} in {path}")
                for identity in sorted(i for i in on_disk if i and i not in planned):
                    errors.append(f"Task absent from plan order: {identity}")
    if meta.get("document_type") == "task" and meta.get("status") in {
            "IN PROGRESS", "IN REVIEW", "IN TESTING", "AWAITING USER ACCEPTANCE", "DONE"}:
        try:
            workflow_state(text(root, path))
        except ForgeError as exc:
            errors.append(f"{path}: {exc}; record the Workflow State block first")
    if meta.get("document_type") == "investigation":
        record_contract = contracts["ad_hoc_investigations"]["record"]
        content = text(root, path)
        full = frontmatter(content)
        for field in record_contract["required_frontmatter"]:
            if field not in full:
                errors.append(f"Investigation missing frontmatter field {field}: {path}")
        headings = {value["heading"] for value in sections(content)}
        for heading in record_contract["required_sections"]:
            if heading not in headings:
                errors.append(f"Investigation missing section {heading}: {path}")
    if meta.get("document_type") == "intent":
        record_contract = contracts["intent_records"]["record"]
        content = text(root, path)
        full = frontmatter(content)
        for field in record_contract["required_frontmatter"]:
            if field not in full:
                errors.append(f"Intent missing frontmatter field {field}: {path}")
        headings = {value["heading"] for value in sections(content)}
        for heading in record_contract["required_sections"]:
            if heading not in headings:
                errors.append(f"Intent missing section {heading}: {path}")
    return errors


def validate(root, project=False):
    errors = []
    advisory = []
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
        errors.extend(conformance_errors(root, contracts))
        rows = backlog_rows(root)
        roadmap = {}
        archived = {}
        for record in archived_backlog_rows(root):
            identity = record["cells"].get("ID", "").strip("`")
            if identity:
                if identity in archived:
                    errors.append(f"Duplicate archived row: {identity}")
                archived[identity] = record["cells"]
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
                row = roadmap.get(epic) or (archived.get(epic) if path.split("/")[1] == "completed" else None)
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
            if meta.get("document_type") == "intent":
                if meta.get("outcome") not in contracts["enums"]["intent_outcomes"]:
                    errors.append(f"Invalid intent outcome: {path}")
                if meta.get("origin") not in contracts["enums"]["intent_origins"]:
                    errors.append(f"Invalid intent origin: {path}")
            try:
                errors.extend(record_structure_errors(root, record, contracts))
            except (OSError, ForgeError) as exc:
                errors.append(f"{path}: {exc}")
        if len(writing) > 1:
            errors.append("Multiple code-writing Tasks")
        for epic, row in roadmap.items():
            if row["Status"] in active | {"PAUSED", "COMPLETED"} and epic not in epics:
                errors.append(f"Missing Epic workspace: {epic}")
        bug_ids = {row["ID"].strip("`") for row in defect_rows(root)}
        investigation_base = within(root, "investigations")
        for record in records:
            meta, path = record["metadata"], record["path"]
            if meta.get("document_type") != "intent":
                continue
            target = meta.get("promoted_to")
            if isinstance(target, str) and target.strip() and target not in roadmap and target not in bug_ids and target not in archived:
                errors.append(f"Intent promoted_to target missing: {path}")
            for ref in meta.get("research_refs") or []:
                if not isinstance(ref, str) or not ref.startswith("INV-"):
                    continue
                known = investigation_base.exists() and any(investigation_base.glob(f"{ref}-*.md"))
                if not known:
                    errors.append(f"Intent research_refs target missing: {ref} in {path}")
            try:
                if len(text(root, path)) > 6000:
                    advisory.append(f"Intent record exceeds the one-page bound: {path}")
            except (OSError, ForgeError):
                pass
    return {"passed": not errors, "errors": errors, "advisory": advisory,
            "coverage": "manifest IDs and source syntax" + (", lifecycle inventory, Backlog consistency, and structural conformance" if project else ""),
            "requires_judgment": ["scope and permissions", "test integrity and coverage", "review protocol and evidence freshness", "integration and mutation semantics"]}


def budget(root, paths):
    rows = []
    for path in paths:
        content = text(root, path)
        rows.append({"path": path, "bytes": len(content.encode()), "chars": len(content),
                     "lines": len(content.splitlines()), "estimated_tokens": (len(content) + 3) // 4})
    return {"files": rows, "estimated_tokens": sum(r["estimated_tokens"] for r in rows),
            "estimate_method": "ceil(characters / 4); heuristic, not model tokenizer or billed usage"}
