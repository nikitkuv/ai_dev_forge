"""Canonical identity diagnostics and token-bound record writes; no model calls."""
from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

from forge_core import (ForgeError, Transaction, archived_backlog_rows, backlog_rows, canonical,
                        defect_rows, digest, frontmatter, inventory, text, within)

IDENTITY = r"(?:TASK|EPIC|BUG|ADR|INV|INT|MUT)-\d+"
LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\((<?)([^\s)]+?)(>?)\)")


def metadata(content):
    # Root indexes and legacy ADRs may be plain Markdown; malformed YAML still fails.
    return frontmatter(content) if content.startswith("---\n") or content.startswith("---\r\n") else {}


def link_matches(content):
    """Ignore fenced examples when inspecting live Markdown navigation."""
    masked, fence = [], None
    for line in content.splitlines(keepends=True):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            masked.append(" " * len(line))
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
        elif marker:
            fence = marker[1]
            masked.append(" " * len(line))
        else:
            masked.append(line)
    return LINK.finditer("".join(masked))


def rewrite_links(content, replace):
    for match in reversed(list(link_matches(content))):
        content = content[:match.start()] + replace(match) + content[match.end():]
    return content


def replace_target(match, target):
    start, end = match.start(2) - match.start(), match.end(2) - match.start()
    return match[0][:start] + target + match[0][end:]


def target_identity(target):
    path = PurePosixPath(target)
    match = re.match(IDENTITY + r"(?=-|$)", path.stem)
    if not match and path.name == "plan.md":
        match = re.match(r"EPIC-\d+(?=-|$)", path.parent.name)
    return match[0] if match else None


def cell_id(value):
    """Accept plain IDs, code spans and Markdown links, never substring matches."""
    value = str(value).strip()
    match = re.fullmatch(r"`(" + IDENTITY + r")`", value)
    if match:
        return match[1]
    match = re.match(r"\[(`?)(" + IDENTITY + r")\1\]\(", value)
    if match:
        return match[2]
    match = re.match(r"^(" + IDENTITY + r")(?=$|\s)", value)
    return match[1] if match else None


def canonical_files(root):
    records, errors = inventory(root, include_completed=True)
    paths = {r["path"] for r in records}
    base = within(root, "decisions")
    if base.exists():
        paths.update(p.relative_to(root).as_posix() for p in base.glob("ADR-*.md"))
    for name in ("BACKLOG.md", "BACKLOG-ARCHIVE.md", "DECISIONS.md", "SPEC.md", "ARCHITECTURE.md"):
        if within(root, name).exists():
            paths.add(name)
    return sorted(paths), errors


def reference_target(source, target):
    """Resolve a local Markdown URL lexically; filesystem access still uses within()."""
    target = unquote(target.split("#", 1)[0])
    if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    # Forge root-relative canonical paths are common alongside normal relative links.
    if target.startswith(("execution/", "decisions/", "investigations/", "intents/")) or target in {
            "BACKLOG.md", "SPEC.md", "ARCHITECTURE.md", "DECISIONS.md"}:
        parts = []
    elif target.startswith("/"):
        return None
    else:
        parts = list(PurePosixPath(source).parent.parts)
    for part in target.replace("\\", "/").split("/"):
        if part == "..":
            if not parts:
                return None
            parts.pop()
        elif part not in ("", "."):
            parts.append(part)
    return "/".join(parts)


def identity_check(root):
    root = Path(root).resolve()
    paths, errors = canonical_files(root)
    declarations, findings, contents, advisory = {}, [], {}, []

    def report(code, path, field, actual, expected=None):
        findings.append(dict(code=code, path=path, field=field, actual=actual, expected=expected))

    def declare(identity, path):
        if identity:
            declarations.setdefault(identity, []).append(path)

    for path in paths:
        content = text(root, path)
        contents[path] = content
        meta = metadata(content)
        kind = meta.get("document_type")
        identity = meta.get("epic_id") if kind == "epic_plan" else meta.get("id")
        if not identity and path.startswith("decisions/"):
            identity = target_identity(path)
        expected_prefix = {"task": "TASK-", "epic_plan": "EPIC-", "intent": "INT-",
                           "investigation": "INV-"}.get(kind)
        if expected_prefix and (not isinstance(identity, str) or not identity.startswith(expected_prefix)):
            report("record_kind_id_mismatch", path, "id", identity, expected_prefix)
        if identity:
            if not isinstance(identity, str) or not re.fullmatch(IDENTITY, identity):
                report("invalid_id", path, "frontmatter", identity)
                continue
            declare(identity, path)
            filename = re.match(IDENTITY, PurePosixPath(path).stem)
            if filename and filename[0] != identity:
                report("filename_id_mismatch", path, "id", identity, filename[0])
            heading = re.search(r"^# (" + IDENTITY + r")(?=\s|$)", content, re.MULTILINE)
            if heading and heading[1] != identity:
                report("heading_id_mismatch", path, "heading", heading[1], identity)
        if path.startswith("execution/") and kind in ("task", "epic_plan"):
            workspace = re.match(r"EPIC-\d+(?=-|$)", path.split("/")[2])
            if workspace and meta.get("epic_id") != workspace[0]:
                report("workspace_id_mismatch", path, "epic_id", meta.get("epic_id"), workspace[0])
    rows = []
    if "BACKLOG.md" in contents:
        rows = [("BACKLOG.md", r) for r in backlog_rows(root) + defect_rows(root)]
    rows += [("BACKLOG-ARCHIVE.md", r["cells"]) for r in archived_backlog_rows(root)]
    row_ids = {}
    for path, row in rows:
        identity = cell_id(row.get("ID", ""))
        if not identity:
            report("invalid_row_id", path, "ID", row.get("ID"))
            continue
        row_ids.setdefault(identity, []).append(path)
    for identity, locations in row_ids.items():
        if len(locations) > 1:
            report("duplicate_row_id", locations[0], "ID", identity, locations)
    for identity, locations in declarations.items():
        if len(locations) > 1:
            report("duplicate_declaration", locations[0], "id", identity, locations)
    # Numeric aliases are ambiguous, not an instruction to renumber history.
    aliases = {}
    for identity in set(declarations) | set(row_ids):
        prefix, number = identity.rsplit("-", 1)
        aliases.setdefault((prefix, int(number)), []).append(identity)
    for values in aliases.values():
        if len(values) > 1:
            report("numeric_id_collision", "", "id", sorted(values))
    known = set(declarations) | set(row_ids)
    for path, row in rows:
        if path == "BACKLOG-ARCHIVE.md":
            continue  # retained historical references need not resolve in the live workspace
        for field in ("Dependencies", "Blocked by", "Scheduled TASK"):
            for ref in re.findall(IDENTITY, row.get(field, "")):
                if ref not in known:
                    report("missing_reference", path, field, ref)
    for path, content in contents.items():
        meta = metadata(content)
        for field in ("blocked_by", "research_refs", "promoted_to"):
            value = meta.get(field) or []
            for ref in value if isinstance(value, list) else [value]:
                if isinstance(ref, str) and re.fullmatch(IDENTITY, ref) and ref not in known:
                    report("missing_reference", path, field, ref)
        # Historical archive links are immutable evidence, not live navigation.
        if path == "BACKLOG-ARCHIVE.md":
            continue
        for match in link_matches(content):
            target = reference_target(path, match[2])
            if target and target.startswith(("execution/", "decisions/", "investigations/", "intents/")):
                if not within(root, target).exists():
                    if path.startswith("execution/completed/"):
                        advisory.append({"code": "historical_record_link", "path": path, "target": match[2]})
                    else:
                        report("broken_record_link", path, "markdown_link", match[2])
                else:
                    label = re.match(r"\[`?(" + IDENTITY + r")`?\]", match[0])
                    actual = target_identity(target)
                    if label and actual and label[1] != actual:
                        report("link_id_mismatch", path, "markdown_link", label[1], actual)
    return {"passed": not findings and not errors, "findings": findings, "errors": errors,
            "advisory": advisory,
            "declarations": declarations, "scanned_files": len(paths),
            "file_hashes": {p: digest(within(root, p).read_bytes()) for p in paths},
            "requires_judgment": ["Which identity is authoritative in a conflict", "Historical prose and external mappings"]}


def record_snapshot(root):
    paths, errors = canonical_files(root)
    if errors:
        raise ForgeError("Cannot inspect record state: " + "; ".join(errors))
    return digest(canonical({p: digest(within(root, p).read_bytes()) for p in paths}).encode())


def records_write(root, packet, apply_token=None):
    """Render symbolic IDs once across an explicitly supplied canonical file batch.

    Existing files require their exact SHA256. New IDs are assigned only to aliases
    requested in allocations; no lifecycle decision or document content is inferred.
    """
    from forge_lifecycle import ID_FORMATS, next_id, mutation_preview
    from forge_core import validate
    inspection = identity_check(root)
    if inspection["errors"] or any(f["code"] in {"duplicate_declaration", "duplicate_row_id", "numeric_id_collision"}
                                   for f in inspection["findings"]):
        raise ForgeError("Ambiguous record identities must be resolved before allocating or writing")
    if set(packet) - {"schema_version", "allocations", "files"} or packet.get("schema_version") != 1:
        raise ForgeError("Expected records-write packet schema_version 1")
    allocations = packet.get("allocations", {})
    files = packet.get("files")
    if not isinstance(allocations, dict) or not isinstance(files, list) or not files:
        raise ForgeError("allocations must be a mapping and files a non-empty list")
    mapping, counters = {}, {}
    for alias, kind in allocations.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", alias) or kind not in ID_FORMATS or kind == "mut":
            raise ForgeError("Invalid allocation alias or kind")
        if kind not in counters:
            counters[kind] = next_id(root, kind)["next_id"]
        mapping[alias] = counters[kind]
        prefix, digits = counters[kind].rsplit("-", 1)
        counters[kind] = f"{prefix}-{int(digits) + 1:0{len(digits)}d}"

    def render(value):
        if not isinstance(value, str):
            raise ForgeError("Record paths and content must be strings")
        def replace(match):
            if match[1] not in mapping:
                raise ForgeError(f"Unknown ID alias: {match[1]}")
            return mapping[match[1]]
        return re.sub(r"\{\{id:([a-z][a-z0-9_]*)\}\}", replace, value)

    updates = {}
    for item in files:
        if not isinstance(item, dict) or set(item) - {"path", "content", "source", "expected_sha256"}:
            raise ForgeError("Record file requires path/content and optional expected_sha256")
        if ("content" in item) == ("source" in item):
            raise ForgeError("Provide exactly one of content or source for each output")
        raw = text(root, item["source"]) if "source" in item else item["content"]
        name, content = render(item["path"]), render(raw)
        path = within(root, name)
        name = path.relative_to(Path(root).resolve()).as_posix()
        if name not in ("BACKLOG.md", "DECISIONS.md", "SPEC.md", "ARCHITECTURE.md") and not (
                name.startswith(("execution/", "intents/", "investigations/", "decisions/")) and name.endswith(".md")):
            raise ForgeError(f"Not a mutable canonical record path: {name}")
        if name.startswith("execution/completed/"):
            raise ForgeError("Completed history cannot be rewritten by records-write")
        if name in updates:
            raise ForgeError(f"Duplicate output path: {name}")
        current = digest(path.read_bytes()) if path.exists() else None
        if current != item.get("expected_sha256"):
            raise ForgeError(f"Existing record requires matching expected_sha256: {name}")
        after_meta = metadata(content)
        if path.exists():
            before_meta = metadata(text(root, name))
            for field in ("document_type", "id", "epic_id", "status"):
                if before_meta.get(field) != after_meta.get(field):
                    raise ForgeError(f"records-write cannot change existing {field}: {name}; use lifecycle or explicit conflict resolution")
        elif after_meta.get("document_type") == "task" and after_meta.get("status") != "TODO":
            raise ForgeError("New TASK records must remain TODO")
        if name == "BACKLOG.md" and path.exists():
            from forge_core import table_rows
            old_rows = backlog_rows(root) + defect_rows(root)
            new_rows = table_rows(content, "Epic Roadmap", {"ID", "Status"}) + table_rows(
                content, "Defect Queue", {"ID", "Status"}, optional=True)
            after_rows = {cell_id(r["ID"]): r for r in new_rows}
            for row in old_rows:
                replacement = after_rows.get(cell_id(row["ID"]))
                if replacement is None or replacement["Status"] != row["Status"]:
                    raise ForgeError("records-write cannot remove rows or change lifecycle status; use lifecycle helpers")
        updates[name] = content.encode("utf-8")
    baseline = record_snapshot(root)
    preview, _ = mutation_preview(root, "records-write", updates)
    token = digest(canonical([preview["preview_token"], baseline, mapping]).encode())
    preview.update(preview_token=token, identities=mapping, record_fingerprint=baseline)
    if apply_token is None:
        return preview
    if token != apply_token:
        raise ForgeError("Stale record preview: canonical records or allocation changed")
    transaction = Transaction(root, "lifecycle").claim()
    success = False
    try:
        def recheck():
            if record_snapshot(root) != baseline:
                raise ForgeError("Records changed before write; regenerate preview")
        transaction.write(updates, recheck=recheck)
        result = validate(root, True)
        if not result["passed"]:
            raise ForgeError("Record validation failed: " + "; ".join(result["errors"][:8]))
        declared = identity_check(root)["declarations"]
        rows = {cell_id(r["ID"]) for r in backlog_rows(root) + defect_rows(root)}
        for identity in mapping.values():
            if identity not in declared and identity not in rows:
                raise ForgeError(f"Allocated ID was not declared: {identity}")
        success = True
        return {"applied": list(updates), "identities": mapping, "passed": True}
    except BaseException:
        transaction.rollback()
        raise
    finally:
        transaction.finish(success)


def links_repair(root, apply_token=None):
    """Repair only missing Markdown file targets with a unique, verified ID match."""
    inspection = identity_check(root)
    if inspection["errors"] or any(f["code"] != "broken_record_link" for f in inspection["findings"]):
        raise ForgeError("Resolve identity conflicts before automatic link repair")
    files = []
    for path in sorted({f["path"] for f in inspection["findings"]}):
        before = text(root, path)
        def replace(match):
            target = reference_target(path, match[2])
            if not target or within(root, target).exists():
                return match[0]
            identity = target_identity(target)
            if not identity:
                return match[0]
            choices = inspection["declarations"].get(identity, [])
            if len(choices) != 1:
                return match[0]
            suffix = "#" + match[2].split("#", 1)[1] if "#" in match[2] else ""
            return replace_target(match, choices[0] + suffix)
        after = rewrite_links(before, replace)
        if after != before:
            files.append({"path": path, "content": after, "expected_sha256": digest(within(root, path).read_bytes())})
    if not files:
        return {"applied": [], "passed": inspection["passed"], "findings": inspection["findings"]}
    return records_write(root, {"schema_version": 1, "files": files}, apply_token)


def relocation_links(root, source, destination):
    """Rewrite exact Markdown record targets as part of the workspace transaction."""
    updates = {}
    for path in canonical_files(root)[0]:
        if path == "BACKLOG-ARCHIVE.md" or path.startswith("execution/completed/"):
            continue
        before = text(root, path)
        def replace(match):
            target = reference_target(path, match[2])
            if target and (target == source or target.startswith(source + "/")):
                suffix = "#" + match[2].split("#", 1)[1] if "#" in match[2] else ""
                return replace_target(match, destination + target[len(source):] + suffix)
            return match[0]
        after = rewrite_links(before, replace)
        if after != before:
            updates[path] = after.encode("utf-8")
    return updates
