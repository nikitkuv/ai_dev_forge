"""Identifier allocation, evidence comparison, packet assembly, and approved
lifecycle mutations. Read-only commands never judge evidence; mutating
commands execute only explicitly requested transitions through preview/apply
and never authorize, infer, or decide anything."""
from __future__ import annotations

from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import re
import shutil

import yaml

from forge_core import (ARCHIVE_PATH, TERMINAL_BUG_STATUSES, TERMINAL_EPIC_STATUSES, ForgeError, Transaction,
                        archived_backlog_rows, archive_append, atomic_replace, backlog_rows, canonical, defect_rows,
                        digest, frontmatter, git_capture, inventory, load_yaml, sections, snapshot, table_rows, text,
                        within, workflow_state, yaml_value)

ID_FORMATS = {"task": ("TASK-", 3), "bug": ("BUG-", 3), "inv": ("INV-", 4), "int": ("INT-", 4),
              "epic": ("EPIC-", 3), "adr": ("ADR-", 3), "mut": ("MUT-", 4)}

# Values that mean "not recorded yet"; they never satisfy a mechanical comparison.
PLACEHOLDER = (r"^<[^>]*>$", r"^pending$", r"^[—–-]$", r"^\s*$")


def recorded(value):
    """Return the value when it is real evidence, else None."""
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if any(re.match(pattern, stripped) for pattern in PLACEHOLDER):
        return None
    return stripped


def _digits(identity, kind):
    match = re.fullmatch(re.escape(ID_FORMATS[kind][0]) + r"(\d+)", identity)
    return int(match.group(1)) if match else None


def next_id(root, kind):
    """Max-plus-one allocation over canonical declarations; never fills gaps."""
    if kind not in ID_FORMATS:
        raise ForgeError("Unsupported identifier kind")
    prefix, width = ID_FORMATS[kind]
    found, sources, declared_next = {}, [], [0]
    if kind == "task":
        sources = ["execution/"]
        items, errors = inventory(root, include_completed=True)
        if errors:
            raise ForgeError("Cannot allocate TASK ID from incomplete inventory: " + "; ".join(errors))
        for item in items:
            identity = item["metadata"].get("id")
            if identity and identity.startswith(prefix):
                found[identity] = item["path"]
    elif kind == "epic":
        sources = ["BACKLOG.md", ARCHIVE_PATH]
        for row in (backlog_rows(root) if within(root, "BACKLOG.md").exists() else []):
            identity = row["ID"].strip("`")
            if identity.startswith(prefix):
                found[identity] = "BACKLOG.md"
        for record in archived_backlog_rows(root, "Epic Roadmap"):
            identity = record["cells"].get("ID", "").strip("`")
            if identity.startswith(prefix):
                found[identity] = ARCHIVE_PATH
    elif kind == "bug":
        sources = ["BACKLOG.md", ARCHIVE_PATH]
        for row in (defect_rows(root) if within(root, "BACKLOG.md").exists() else []):
            identity = row["ID"].strip("`")
            if identity.startswith(prefix):
                found[identity] = "BACKLOG.md"
        for record in archived_backlog_rows(root, "Defect Queue"):
            identity = record["cells"].get("ID", "").strip("`")
            if identity.startswith(prefix):
                found[identity] = ARCHIVE_PATH
    elif kind == "inv":
        sources = ["investigations/"]
        base = within(root, "investigations")
        if base.exists():
            for path in sorted(base.glob("INV-*.md")):
                match = re.match(r"INV-\d+", path.stem)
                if match:
                    found[match.group(0)] = path.relative_to(Path(root).resolve()).as_posix()
    elif kind == "int":
        sources = ["intents/"]
        base = within(root, "intents")
        if base.exists():
            for path in sorted(base.glob("INT-*.md")):
                match = re.match(r"INT-\d+", path.stem)
                if match:
                    found[match.group(0)] = path.relative_to(Path(root).resolve()).as_posix()
    elif kind == "adr":
        sources = ["decisions/", "DECISIONS.md"]
        base = within(root, "decisions")
        if base.exists():
            for path in sorted(base.glob("ADR-*.md")):
                match = re.match(r"ADR-\d+", path.stem)
                if match:
                    found[match.group(0)] = path.relative_to(Path(root).resolve()).as_posix()
        index = within(root, "DECISIONS.md")
        if index.exists():
            for identity in re.findall(r"ADR-\d+", text(root, "DECISIONS.md")):
                found.setdefault(identity, "DECISIONS.md")
    elif kind == "mut":
        sources = ["quality/mutation-testing/registry.yaml"]
        registry = within(root, "quality/mutation-testing/registry.yaml")
        if registry.exists():
            data = load_yaml(root, "quality/mutation-testing/registry.yaml")
            for run in data.get("runs") or []:
                identity = run if isinstance(run, str) else run.get("id")
                if identity:
                    found[identity] = "quality/mutation-testing/registry.yaml"
            declared = data.get("next_id")
            if declared and _digits(str(declared), kind) is not None:
                # next_id names the next allocation, not an existing record.
                declared_next[0] = _digits(str(declared), kind)
    numbers = {number: identity for identity in found if (number := _digits(identity, kind)) is not None}
    if numbers:
        maximum = max(numbers)
        candidate = max(maximum + 1, declared_next[0])
        # Keep at least the digit width of the widest existing identifier (e.g. BUG-0010).
        widest = max(len(identity) - len(prefix) for identity in found if _digits(identity, kind) is not None)
        padding = max(width, len(str(max(numbers))), len(str(declared_next[0])), widest)
    else:
        candidate, padding = max(1, declared_next[0]), width
    return {"kind": kind, "next_id": f"{prefix}{candidate:0{padding}d}",
            "current_max": numbers.get(max(numbers)) if numbers else None,
            "current_max_number": max(numbers) if numbers else 0,
            "scanned": sources, "known": len(found)}


def _task_state(root, task_path):
    content = text(root, task_path)
    return content, frontmatter(content), workflow_state(content)


def _fingerprint_report(root, paths):
    if not paths:
        return {"verdict": "insufficient", "reason": "No recorded paths"}
    snap = snapshot(root, [p for p in paths if isinstance(p, str)])
    missing = [f["path"] for f in snap["files"] if f["kind"] == "missing"]
    report = {"verdict": "current", "fingerprint": snap["fingerprint"], "paths": len(paths), "missing": missing}
    if missing:
        report["verdict"] = "missing_paths"
    return report


def _compare(label, recorded_value, current):
    """One recorded-vs-current fingerprint comparison."""
    value = recorded(recorded_value)
    entry = {"recorded": recorded_value if value else None, "current": current.get("fingerprint")}
    if value is None:
        entry["verdict"] = "insufficient"
    elif current["verdict"] == "insufficient":
        entry["verdict"] = "insufficient"
    elif value != current["fingerprint"]:
        entry["verdict"] = "stale"
        entry["reason"] = "Recorded fingerprint does not match the current file set"
    else:
        entry["verdict"] = "fresh"
    return entry


def evidence_check(root, task_path):
    """Recompute recorded evidence fingerprints and report mechanical verdicts.

    Never decides review protocol completeness, test integrity, or acceptance;
    those remain orchestrator judgments and are listed in requires_judgment."""
    content, meta, state = _task_state(root, task_path)
    packet = state.get("review_packet") or {}
    changed = [p for p in (packet.get("changed_paths") or []) if recorded(p)]
    production = [p for p in (packet.get("production_review_paths") or []) if recorded(p)]
    whole = _fingerprint_report(root, changed)
    production_now = _fingerprint_report(root, production)
    review = _compare("review", (state.get("review") or {}).get("production_fingerprint"), production_now)
    testing = _compare("testing", (state.get("testing") or {}).get("implementation_fingerprint"), whole)
    assurance = _compare("fast_assurance", (state.get("fast_assurance") or {}).get("implementation_fingerprint"), whole)
    track = meta.get("delivery_track", "standard")
    eligibility = {"status": meta.get("status"), "delivery_track": track}
    if meta.get("status") != "AWAITING USER ACCEPTANCE":
        eligibility["verdict"] = "not_eligible"
        eligibility["reason"] = "Task is not AWAITING USER ACCEPTANCE"
    elif track == "fast":
        outcome = recorded((state.get("fast_assurance") or {}).get("outcome"))
        if outcome == "PASSED" and assurance["verdict"] == "fresh":
            eligibility["verdict"] = "mechanically_eligible"
        else:
            eligibility["verdict"] = "not_eligible"
            eligibility["reason"] = "Fast assurance outcome/fingerprint does not match current evidence"
    else:
        if testing["verdict"] == "fresh" and review["verdict"] == "fresh":
            eligibility["verdict"] = "mechanically_eligible"
        else:
            eligibility["verdict"] = "not_eligible"
            eligibility["reason"] = "Testing or clean-review fingerprint does not match current evidence"
    return {"task": task_path, "status": meta.get("status"), "delivery_track": track,
            "current": {"whole_implementation": whole, "production_surface": production_now},
            "review_freshness": review, "testing_currency": testing, "fast_assurance": assurance,
            "acceptance_eligibility": eligibility,
            "requires_judgment": ["review protocol completeness", "test integrity and coverage quality",
                                  "explicit user acceptance", "verification-selection adequacy"]}


def _fuzz_evidence(content):
    """Final Fuzzing impact and Task fuzz smoke values from the Verification Plan."""
    found = [s for s in sections(content) if s["heading"] == "Verification Plan"]
    if not found:
        return None, None
    values = {}
    for line in found[0]["content"].splitlines():
        match = re.match(r"-\s+\*\*(Fuzzing impact|Task fuzz smoke):\*\*\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2)
    return values.get("Fuzzing impact"), values.get("Task fuzz smoke")


def evidence_check_epic(root, epic_id):
    """Mechanical Epic gate inputs: DONE coverage, fuzz evidence, aggregate fingerprint."""
    records = [r for r in inventory(root, include_completed=True)[0]
               if r["metadata"].get("epic_id") == epic_id and r["metadata"].get("document_type") == "task"]
    if not records:
        raise ForgeError(f"No TASK records found for {epic_id}")
    tasks, surface = [], []
    for item in records:
        content = text(root, item["path"])
        meta = item["metadata"]
        impact, smoke = _fuzz_evidence(content)
        state = None
        try:
            state = workflow_state(content)
        except ForgeError:
            pass
        packet = (state or {}).get("review_packet") or {}
        surface.extend(p for p in (packet.get("changed_paths") or []) if recorded(p) and p not in surface)
        tasks.append({"path": item["path"], "status": meta.get("status"),
                      "fuzzing_impact": impact if recorded(impact) else None,
                      "task_fuzz_smoke": smoke if recorded(smoke) else None})
    aggregate = _fingerprint_report(root, surface)
    return {"epic": epic_id, "tasks": tasks,
            "all_done": all(t["status"] == "DONE" for t in tasks),
            "fuzz_evidence_complete": all(t["fuzzing_impact"] and t["task_fuzz_smoke"] for t in tasks),
            "aggregate": aggregate,
            "requires_judgment": ["requirement and critical-path coverage", "profile gates",
                                  "applicability of the approved Epic Fuzzing Plan", "explicit Epic acceptance"]}


def _base_revision(content):
    found = [s for s in sections(content) if s["heading"] == "Implementation Summary"]
    if not found:
        raise ForgeError("Missing recorded input: Implementation Summary section")
    for line in found[0]["content"].splitlines():
        match = re.match(r"-\s+\*\*Base revision:\*\*\s*(.*)$", line)
        if match and recorded(match.group(1)):
            return match.group(1).strip()
    raise ForgeError("Missing recorded input: Base revision in Implementation Summary")


def _bounded_diff(root, base, paths, limit=65536):
    """Diff from the recorded base revision to the current working tree, scoped
    to explicit paths. Untracked additions are listed separately: Git cannot
    diff a path it does not track yet."""
    if not paths:
        return {"paths": 0, "diff": "", "truncated": False, "untracked": []}
    result = git_capture(root, ["diff", "--no-color", base, "--"] + paths, timeout=60)
    if result["exit_code"]:
        raise ForgeError(f"Git diff failed for base {base!r}: {result['stderr'].strip() or result['stdout'].strip()}")
    listing = git_capture(root, ["ls-files", "--others", "--exclude-standard", "--"] + paths, timeout=30)
    untracked = [line for line in listing["stdout"].splitlines() if line] if not listing["exit_code"] else []
    diff = result["stdout"]
    return {"paths": len(paths), "diff": diff[:limit], "truncated": len(diff) > limit,
            "untracked": untracked, "diff_sha256": digest(diff.encode())}


def review_packet(root, task_path):
    """Assemble the compact Review Packet JSON from recorded TASK data.

    Uses the recorded path classification as input; never classifies paths,
    judges review focus, or validates review protocol."""
    content, meta, state = _task_state(root, task_path)
    packet = state.get("review_packet") or {}
    missing = [field for field, value in (("review_packet.changed_paths", packet.get("changed_paths")),
                                          ("review_packet.production_review_paths", packet.get("production_review_paths")),
                                          ("review_packet.supporting_evidence_paths", packet.get("supporting_evidence_paths")))
               if not value]
    if missing:
        raise ForgeError("Missing recorded input: " + ", ".join(missing))
    changed = [p for p in packet["changed_paths"] if isinstance(p, str)]
    production = [p for p in packet["production_review_paths"] if isinstance(p, str)]
    supporting = [p for p in packet["supporting_evidence_paths"] if isinstance(p, str)]
    if not changed or not production:
        raise ForgeError("Missing recorded input: empty changed or production path list")
    base = _base_revision(content)
    whole = snapshot(root, changed)
    production_snap = snapshot(root, production)
    overlap = sorted(set(production) & set(supporting))
    ambiguous = packet.get("ambiguous_path_classification") or []
    result = {"task": task_path, "epic_id": meta.get("epic_id"), "base_revision": base,
              "implementation_revision": state.get("implementation_revision"),
              "fingerprints": {"whole_implementation": whole["fingerprint"],
                               "production_surface": production_snap["fingerprint"]},
              "surfaces": {"production_review_paths": production, "supporting_evidence_paths": supporting,
                           "ambiguous_path_classification": ambiguous},
              "missing_paths": sorted({f["path"] for f in whole["files"] + production_snap["files"]
                                       if f["kind"] == "missing"}),
              "classification_warnings": {"production_supporting_overlap": overlap,
                                          "ambiguous_without_rationale": len(ambiguous)},
              "diffs": {"whole_implementation": _bounded_diff(root, base, changed),
                        "production_surface": _bounded_diff(root, base, production)}}
    return result


# ---------------------------------------------------------------- mutations
# Every mutation follows one contract: preview shows the exact planned edits
# and a token bound to the current inputs; apply re-derives the plan, requires
# the same token, writes through the journaled transaction, revalidates
# structurally, and rolls back completely on any failure. Nothing here
# authorizes, infers, or decides a transition.


def _today():
    return datetime.now(timezone.utc).date().isoformat()


def _slug(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ForgeError("A short name requires ASCII letters or digits; pass --name explicitly")
    return slug[:48]


def _tree_digest(root, directory):
    """Digest of every file name and byte under one directory."""
    base = within(root, directory)
    entries = []
    if base.exists():
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            within(root, path)
            entries.append([path.relative_to(base).as_posix(), digest(path.read_bytes())])
    return digest(canonical(entries).encode())


def mutation_preview(root, operation, updates, moves=(), description=None):
    """Token-bound preview of exact file edits and directory moves."""
    observed = {}
    for relative in updates:
        path = within(root, relative)
        observed[relative] = digest(path.read_bytes()) if path.exists() else None
    move_state = [[source, destination, _tree_digest(root, source)] for source, destination in moves]
    state = {"operation": operation, "observed": observed,
             "candidate": {p: digest(d) for p, d in updates.items()}, "moves": move_state}
    token = digest(canonical(state).encode())
    changes = []
    for relative, data in updates.items():
        before = observed[relative]
        previous = within(root, relative).read_bytes().decode("utf-8", "replace").splitlines(True) if before else []
        changes.append({"path": relative, "before": before, "after": digest(data), "new_file": before is None,
                        "diff": "".join(difflib.unified_diff(previous, data.decode("utf-8", "replace").splitlines(True),
                                                             fromfile=relative, tofile=relative))})
    return {"operation": operation, "description": description or operation, "preview_token": token,
            "changes": changes, "moves": move_state}, updates


def mutation_apply(root, operation, updates, expected_token, moves=(), validator=None):
    """Execute one reviewed preview transactionally; full rollback on failure."""
    transaction = Transaction(root, "lifecycle").claim()
    moved, success = [], False
    try:
        current, _ = mutation_preview(root, operation, updates, moves)
        if current["preview_token"] != expected_token:
            raise ForgeError("Stale preview: inputs or planned outputs changed")

        def recheck():
            if mutation_preview(root, operation, updates, moves)[0]["preview_token"] != expected_token:
                raise ForgeError("Repository changed while preparing transaction")

        transaction.write(updates, recheck=recheck)
        for source, destination in moves:
            origin, target = within(root, source), within(root, destination)
            if not origin.exists():
                raise ForgeError(f"Move source missing: {source}")
            if target.exists():
                raise ForgeError(f"Move destination exists: {destination}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(origin), str(target))
            moved.append((source, destination))
        if validator is not None:
            errors = validator(root)
            if errors:
                raise ForgeError("Post-transition validation failed: " + "; ".join(errors[:5]))
        success = True
        return {"operation": operation, "applied": list(updates), "moved": [destination for _, destination in moved]}
    except BaseException:
        for source, destination in reversed(moved):
            shutil.move(str(within(root, destination)), str(within(root, source)))
        transaction.rollback()
        raise
    finally:
        transaction.finish(success)


def _validate_project(root):
    from forge_core import validate
    return validate(root, True)["errors"]


def _split_frontmatter(content):
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ForgeError("Missing YAML frontmatter")
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1:])
    raise ForgeError("Unclosed YAML frontmatter")


def _with_frontmatter(content, updates):
    head, body = _split_frontmatter(content)
    value = yaml_value(head)
    value.update(updates)
    return "---\n" + yaml.safe_dump(value, sort_keys=False, allow_unicode=True, default_flow_style=False) + "---\n" + body


def _with_workflow_state(content, updates):
    lines = content.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.rstrip() == "## Workflow State"), None)
    if start is None:
        raise ForgeError("Missing Workflow State section")
    opening = None
    for index in range(start + 1, len(lines)):
        if lines[index].lstrip().startswith("```"):
            if opening is None:
                opening = index
            else:
                state = workflow_state(content)
                state.update(updates)
                dumped = yaml.safe_dump(state, sort_keys=False, allow_unicode=True, default_flow_style=False)
                return "".join(lines[:opening + 1]) + dumped + "".join(lines[index:])
    raise ForgeError("Workflow State section lacks a YAML block")


def _baseline_revision(root):
    head = git_capture(root, ["rev-parse", "HEAD"])
    if head["exit_code"]:
        return "no Git repository; working tree only"
    status = git_capture(root, ["status", "--porcelain=v1", "--untracked-files=all"])
    changes = len([line for line in status["stdout"].splitlines() if line.strip()])
    return head["stdout"].strip() + (f" (dirty working tree, {changes} changes)"
                                     if changes else " (clean working tree)")


def inv_create(root, subject, area, paths=(), name=None, apply_token=None):
    """Allocate the next INV identity and scaffold the canonical record."""
    identity = next_id(root, "inv")["next_id"]
    short_name = _slug(name or subject)
    relative = f"investigations/{identity}-{short_name}.md"
    if within(root, relative).exists():
        raise ForgeError(f"Investigation path already exists: {relative}; pass a different --name")
    template = text(root, ".ai/templates/INVESTIGATION.md")
    today = _today()
    filled = (template
              .replace("INV-NNNN", identity)
              .replace('subject: "<Short investigation subject>"', f'subject: "{subject}"')
              .replace('area: "<Component or product area>"', f'area: "{area}"')
              .replace('created_at: "<YYYY-MM-DD>"', f'created_at: "{today}"')
              .replace('updated_at: "<YYYY-MM-DD>"', f'updated_at: "{today}"')
              .replace('baseline_revision: "<Git revision or explicit working-tree description>"',
                       f'baseline_revision: "{_baseline_revision(root)}"')
              .replace("relevant_paths: []", "relevant_paths: [" + ", ".join(paths) + "]")
              .replace("# INV-NNNN — <Investigation Subject>", f"# {identity} — {subject}"))
    updates = {relative: filled.encode()}
    if apply_token is None:
        return mutation_preview(root, "inv-create", updates,
                                description=f"Create {relative} from the canonical template")[0]
    return mutation_apply(root, "inv-create", updates, apply_token)


BUG_COLUMNS = {"ID": None, "Problem": None, "Severity": None, "User priority": None,
               "Related requirement": "—", "Sources": "—", "Research": "—", "Status": "OPEN", "Scheduled TASK": "—"}


def _escape_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table_bounds(lines, heading):
    """Locate header, separator, and last data row of one Backlog table."""
    in_section, header, separator, last_row = False, None, None, None
    for index, line in enumerate(lines):
        if line.startswith("## "):
            in_section = line.strip() == f"## {heading}"
            continue
        if not in_section or not line.strip().startswith("|"):
            continue
        if header is None:
            header = index
        elif separator is None and all(re.fullmatch(r":?-+:?", c.replace(" ", ""))
                                       for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]):
            separator = index
        else:
            last_row = index
    return header, separator, last_row


def backlog_add_bug(root, problem, severity, priority, requirement="—", sources="—", research="—",
                    identity=None, apply_token=None):
    """Insert exactly one OPEN Defect Queue row from explicit user-approved fields."""
    content = text(root, "BACKLOG.md")
    lines = content.splitlines(keepends=True)
    header, separator, _ = _table_bounds(lines, "Defect Queue")
    if header is None or separator is None:
        raise ForgeError("Defect Queue table missing; create the section before adding bugs")
    columns = [cell.strip() for cell in re.split(r"(?<!\\)\|", lines[header].strip())[1:-1]]
    unknown = [c for c in columns if c not in BUG_COLUMNS]
    if unknown:
        raise ForgeError("Unsupported Defect Queue columns: " + ", ".join(unknown))
    identity = identity or next_id(root, "bug")["next_id"]
    values = dict(BUG_COLUMNS, **{"ID": identity, "Problem": problem, "Severity": severity,
                                  "User priority": priority, "Related requirement": requirement,
                                  "Sources": sources, "Research": research})
    row = "| " + " | ".join(_escape_cell(values[c]) for c in columns) + " |\n"
    if not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    insert_at = len(lines)
    for index in range(separator + 1, len(lines)):
        if lines[index].strip().startswith("|"):
            insert_at = index + 1
        else:
            break
    updated = "".join(lines[:insert_at]) + row + "".join(lines[insert_at:])
    updates = {"BACKLOG.md": updated.encode()}
    if apply_token is None:
        return mutation_preview(root, "backlog-add-bug", updates,
                                description=f"Insert {identity} as OPEN in the Defect Queue")[0]
    return mutation_apply(root, "backlog-add-bug", updates, apply_token, validator=_validate_project)


def backlog_update_row(root, identity, sets, move_before=None, apply_token=None):
    """Change only the named cells of one row; all other bytes stay identical."""
    content = text(root, "BACKLOG.md")
    lines = content.splitlines(keepends=True)
    for heading in ("Defect Queue", "Epic Roadmap"):
        header, separator, _ = _table_bounds(lines, heading)
        if header is None:
            continue
        columns = [cell.strip() for cell in re.split(r"(?<!\\)\|", lines[header].strip())[1:-1]]
        target = None
        for index in range(separator + 1, len(lines)):
            if not lines[index].strip().startswith("|"):
                break
            cells = [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", lines[index].strip())[1:-1]]
            if cells and cells[columns.index("ID")] == identity:
                target = (index, cells)
                break
        if target is None:
            continue
        index, cells = target
        unknown = [column for column in sets if column not in columns]
        if unknown:
            raise ForgeError("Unknown columns for this table: " + ", ".join(unknown))
        if _terminal_target(heading, sets):
            if len(sets) > 1 or move_before:
                raise ForgeError("A terminal Status edit archives the row; apply other cell edits first, "
                                 "then set the terminal Status alone")
            backlog_bytes, archive_bytes = _archive_move(root, lines, heading, identity, sets["Status"])
            updates = {"BACKLOG.md": backlog_bytes, ARCHIVE_PATH: archive_bytes}
            if apply_token is None:
                return mutation_preview(root, "backlog-update-row", updates,
                                        description=f"Update {identity}: Status={sets['Status']} and archive")[0]
            return mutation_apply(root, "backlog-update-row", updates, apply_token, validator=_validate_project)
        cells = list(cells)
        for column, value in sets.items():
            cells[columns.index(column)] = _escape_cell(value)
        lines[index] = "| " + " | ".join(cells) + " |\n"
        if move_before:
            other = None
            for scan in range(separator + 1, len(lines)):
                if not lines[scan].strip().startswith("|"):
                    break
                scan_cells = re.split(r"(?<!\\)\|", lines[scan].strip())[1:-1]
                if scan_cells and scan_cells[columns.index("ID")].strip() == move_before:
                    other = scan
                    break
            if other is None:
                raise ForgeError(f"Move-before target not found: {move_before}")
            row_line = lines.pop(index)
            lines.insert(other - 1 if other > index else other, row_line)
        updates = {"BACKLOG.md": "".join(lines).encode()}
        if apply_token is None:
            return mutation_preview(root, "backlog-update-row", updates,
                                    description=f"Update {identity}: " + ", ".join(sets))[0]
        return mutation_apply(root, "backlog-update-row", updates, apply_token, validator=_validate_project)
    raise ForgeError(f"Row not found: {identity}")


GATE_BY_STATUS = {"TODO": "task_start", "IN PROGRESS": "implementation", "IN REVIEW": "review",
                  "IN TESTING": "testing", "AWAITING USER ACCEPTANCE": "user_acceptance",
                  "DONE": "done", "PAUSED": "paused", "CANCELLED": "cancelled"}


def _contracts(root):
    return load_yaml(root, ".ai/framework/contracts.yaml")


def transition_task(root, task_path, target, apply_token=None):
    """Mechanically transition one TASK; authorization and evidence stay outside."""
    contracts = _contracts(root)
    if target not in contracts["enums"]["task_status"]:
        raise ForgeError(f"Invalid target status: {target}")
    if target == "DONE":
        raise ForgeError("Use accept-record for AWAITING USER ACCEPTANCE -> DONE")
    content = text(root, task_path)
    meta = frontmatter(content)
    source = meta.get("status")
    if target not in contracts["transitions"]["task_status"].get(source, []):
        raise ForgeError(f"Forbidden transition {source!r} -> {target!r} per contracts.yaml")
    if target == "IN PROGRESS":
        for record in inventory(root, True)[0]:
            other = record["metadata"]
            if (other.get("document_type") == "task" and other.get("status") == "IN PROGRESS"
                    and record["path"] != task_path):
                raise ForgeError(f"Single-writer invariant: {record['path']} is already IN PROGRESS")
    fields = {"status": target}
    if target == "IN PROGRESS":
        fields["started_at"] = _today()
    updated = _with_workflow_state(_with_frontmatter(content, fields),
                                   {"current_gate": GATE_BY_STATUS[target]})
    updates = {task_path: updated.encode()}
    if apply_token is None:
        return mutation_preview(root, "transition-task", updates,
                                description=f"{task_path}: {source} -> {target}")[0]
    return mutation_apply(root, "transition-task", updates, apply_token, validator=_validate_project)


def _epic_row(root, epic_id):
    for row in backlog_rows(root):
        if row["ID"].strip("`") == epic_id:
            return row
    raise ForgeError(f"Epic not found in Backlog: {epic_id}")


def _edit_backlog_status(root, lines, epic_id, target):
    header, separator, _ = _table_bounds(lines, "Epic Roadmap")
    if header is None:
        raise ForgeError("Epic Roadmap table missing")
    columns = [cell.strip() for cell in re.split(r"(?<!\\)\|", lines[header].strip())[1:-1]]
    for index in range(separator + 1, len(lines)):
        if not lines[index].strip().startswith("|"):
            break
        cells = [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", lines[index].strip())[1:-1]]
        if cells and cells[columns.index("ID")] == epic_id:
            cells[columns.index("Status")] = _escape_cell(target)
            lines[index] = "| " + " | ".join(cells) + " |\n"
            return
    raise ForgeError(f"Epic row not found: {epic_id}")


_ARCHIVE_FROM_DISK = object()


def _archive_move(root, lines, heading, identity, status=None, archive_content=_ARCHIVE_FROM_DISK):
    """Set one row's Status (optional), then move the raw row line to the archive.

    Returns (backlog_bytes, archive_bytes). Raw cells keep their escapes, so the
    archived row matches the prior live row column-for-column. Batch callers pass
    the running archive content so sequential moves compose into one update."""
    header, separator, _ = _table_bounds(lines, heading)
    if header is None:
        raise ForgeError(f"{heading} table missing; inspect BACKLOG.md")
    columns = [cell.strip() for cell in re.split(r"(?<!\\)\|", lines[header].strip())[1:-1]]
    for index in range(separator + 1, len(lines)):
        if not lines[index].strip().startswith("|"):
            break
        raw_cells = re.split(r"(?<!\\)\|", lines[index].strip())[1:-1]
        if raw_cells and raw_cells[columns.index("ID")].strip().strip("`") == identity:
            if status is not None:
                raw_cells[columns.index("Status")] = f" {status} "
            row_line = "|" + "|".join(cell.strip() for cell in raw_cells) + "|"
            del lines[index]
            if archive_content is _ARCHIVE_FROM_DISK:
                archive_content = text(root, ARCHIVE_PATH) if within(root, ARCHIVE_PATH).exists() else None
            archive_bytes = archive_append(archive_content, _today()[:4], heading,
                                           lines[header], lines[separator], row_line).encode()
            return "".join(lines).encode(), archive_bytes
    raise ForgeError(f"Row not found in {heading}: {identity}")


def _terminal_target(heading, sets):
    """True when applying `sets` would leave the row in a terminal status."""
    terminal = TERMINAL_EPIC_STATUSES if heading == "Epic Roadmap" else TERMINAL_BUG_STATUSES
    return "Status" in sets and sets["Status"] in terminal


def backlog_archive_row(root, identity, apply_token=None):
    """Move one terminal live Backlog row verbatim to the append-only archive."""
    lines = text(root, "BACKLOG.md").splitlines(keepends=True)
    for heading, terminal in (("Epic Roadmap", TERMINAL_EPIC_STATUSES), ("Defect Queue", TERMINAL_BUG_STATUSES)):
        header, separator, _ = _table_bounds(lines, heading)
        if header is None:
            continue
        columns = [cell.strip() for cell in re.split(r"(?<!\\)\|", lines[header].strip())[1:-1]]
        for index in range(separator + 1, len(lines)):
            if not lines[index].strip().startswith("|"):
                break
            cells = [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", lines[index].strip())[1:-1]]
            if cells and cells[columns.index("ID")] == identity:
                if cells[columns.index("Status")] not in terminal:
                    raise ForgeError(f"Only terminal rows can be archived: {identity} is {cells[columns.index('Status')]}")
                backlog_bytes, archive_bytes = _archive_move(root, lines, heading, identity)
                updates = {"BACKLOG.md": backlog_bytes, ARCHIVE_PATH: archive_bytes}
                if apply_token is None:
                    return mutation_preview(root, "backlog-archive-row", updates,
                                            description=f"Move {identity} to {ARCHIVE_PATH}")[0]
                return mutation_apply(root, "backlog-archive-row", updates, apply_token, validator=_validate_project)
    raise ForgeError(f"Row not found: {identity}")


def _terminal_targets(root):
    """Every terminal live row as (heading, identity), using the validate classification."""
    targets = []
    for heading, terminal, rows in (("Epic Roadmap", TERMINAL_EPIC_STATUSES, backlog_rows(root)),
                                     ("Defect Queue", TERMINAL_BUG_STATUSES, defect_rows(root))):
        for row in rows:
            if row["Status"] in terminal:
                targets.append((heading, row["ID"].strip("`")))
    return targets


def backlog_archive_all(root, apply_token=None):
    """Backfill every legacy terminal live row to the archive in one transaction."""
    targets = _terminal_targets(root)
    if not targets:
        return {"operation": "backlog-archive-all", "terminal_rows": [], "archived": [],
                "note": "No terminal rows in the live Backlog; nothing to archive"}
    lines = text(root, "BACKLOG.md").splitlines(keepends=True)
    archive_content = text(root, ARCHIVE_PATH) if within(root, ARCHIVE_PATH).exists() else None
    for heading, identity in targets:
        _, archive_bytes = _archive_move(root, lines, heading, identity, archive_content=archive_content)
        archive_content = archive_bytes.decode()
    updates = {"BACKLOG.md": "".join(lines).encode(), ARCHIVE_PATH: archive_content.encode()}
    description = "Archive " + ", ".join(f"{identity} ({heading})" for heading, identity in targets)
    if apply_token is None:
        return mutation_preview(root, "backlog-archive-all", updates, description=description)[0]
    return mutation_apply(root, "backlog-archive-all", updates, apply_token, validator=_validate_project)


def backlog_stale_rows(root, older_than=90):
    """Read-only staleness report from Git row history; changes nothing."""
    if older_than < 0:
        raise ForgeError("--older-than must be non-negative")
    today = datetime.now(timezone.utc).date()
    stale, unknown, fresh = [], [], 0
    for heading, terminal, rows in (("Epic Roadmap", TERMINAL_EPIC_STATUSES, backlog_rows(root)),
                                     ("Defect Queue", TERMINAL_BUG_STATUSES, defect_rows(root))):
        for row in rows:
            identity = row["ID"].strip("`")
            if row["Status"] in terminal:
                continue  # terminal rows are archived by their transition; staleness is moot
            # Exact padded cell as the pickaxe key: EPIC-001 never matches EPIC-0010 history.
            result = git_capture(root, ["log", "-S", f"| {identity} |", "--format=%cI",
                                        "--max-count=1", "--", "BACKLOG.md"])
            stamp = result["stdout"].strip().splitlines()[-1].strip() if result["stdout"].strip() else ""
            if result["exit_code"] or not stamp:
                unknown.append({"id": identity, "section": heading, "status": row["Status"],
                                "reason": "no Git history for this row"})
                continue
            try:
                changed = datetime.fromisoformat(stamp).date()
            except ValueError:
                unknown.append({"id": identity, "section": heading, "status": row["Status"],
                                "reason": f"unparseable commit date: {stamp!r}"})
                continue
            age = (today - changed).days
            if age >= older_than:
                stale.append({"id": identity, "section": heading, "status": row["Status"],
                              "last_changed": changed.isoformat(), "age_days": age})
            else:
                fresh += 1
    return {"older_than_days": older_than, "stale": stale, "unknown": unknown, "fresh": fresh,
            "note": "Suggestion-only mechanical report; closing any row stays an explicit approved user transition"}


def _epic_status(root, epic_id):
    """Live status first, then archived: completed dependencies live in the archive."""
    for row in backlog_rows(root):
        if row["ID"].strip("`") == epic_id:
            return row["Status"]
    for record in archived_backlog_rows(root, "Epic Roadmap"):
        if record["cells"].get("ID", "").strip("`") == epic_id:
            return record["cells"].get("Status")
    return None


def transition_epic(root, epic_id, target, apply_token=None):
    """Transition one Epic's Backlog row through the exact approved status."""
    contracts = _contracts(root)
    if target not in contracts["enums"]["epic_status"]:
        raise ForgeError(f"Invalid target status: {target}")
    row = _epic_row(root, epic_id)
    source = row["Status"]
    if target not in contracts["transitions"]["epic_status"].get(source, []):
        raise ForgeError(f"Forbidden transition {source!r} -> {target!r} per contracts.yaml")
    lines = text(root, "BACKLOG.md").splitlines(keepends=True)
    if target in TERMINAL_EPIC_STATUSES:
        backlog_bytes, archive_bytes = _archive_move(root, lines, "Epic Roadmap", epic_id, target)
        updates = {"BACKLOG.md": backlog_bytes, ARCHIVE_PATH: archive_bytes}
    else:
        _edit_backlog_status(root, lines, epic_id, target)
        updates = {"BACKLOG.md": "".join(lines).encode()}
    if apply_token is None:
        return mutation_preview(root, "transition-epic", updates,
                                description=f"{epic_id}: {source} -> {target}")[0]
    return mutation_apply(root, "transition-epic", updates, apply_token, validator=_validate_project)


ACTIVE_STATES = {"ACTIVE", "VALIDATING", "FUZZING", "AWAITING EPIC ACCEPTANCE"}


def _workspace_directory(root, state, epic_id):
    base = within(root, state)
    matches = sorted(path for path in base.glob(f"{epic_id}-*")) if base.exists() else []
    matches = [path for path in matches if path.is_dir()]
    if len(matches) != 1:
        raise ForgeError(f"Expected exactly one {state} workspace for {epic_id}, found {len(matches)}")
    return matches[0].relative_to(Path(root).resolve()).as_posix()


def epic_start(root, epic_id, apply_token=None):
    """Atomically move one approved planned workspace to active and update the Backlog."""
    row = _epic_row(root, epic_id)
    if row["Status"] != "PLANNED" or row["Readiness"] != "READY":
        raise ForgeError("Epic Start requires PLANNED + READY")
    if row["Blocked by"].strip("`") not in ("", "—", "–", "-"):
        raise ForgeError(f"Epic Start blocked by: {row['Blocked by']}")
    dependencies = [value.strip() for value in row["Dependencies"].replace("`", "").split(",") if value.strip() not in ("", "—", "–", "-")]
    for dependency in dependencies:
        status = _epic_status(root, dependency)
        if status != "COMPLETED":
            raise ForgeError(f"Dependency not satisfied: {dependency} is {status or 'not in Backlog or archive'}")
    if any(other["ID"].strip("`") != epic_id and other["Status"] in ACTIVE_STATES for other in backlog_rows(root)):
        raise ForgeError("Another nonterminal active-work Epic exists")
    planned = _workspace_directory(root, "execution/planned", epic_id)
    name = planned.split("/")[-1]
    moves = [(planned, f"execution/active/{name}")]
    from forge_records import relocation_links
    updates = relocation_links(root, *moves[0])
    lines = updates.get("BACKLOG.md", text(root, "BACKLOG.md").encode()).decode().splitlines(keepends=True)
    _edit_backlog_status(root, lines, epic_id, "ACTIVE")
    updates["BACKLOG.md"] = "".join(lines).encode()
    if apply_token is None:
        return mutation_preview(root, "epic-start", updates, moves,
                                description=f"Move {planned} to active and set {epic_id} ACTIVE")[0]
    return mutation_apply(root, "epic-start", updates, apply_token, moves, validator=_validate_project)


def epic_complete(root, epic_id, apply_token=None):
    """Atomically move an accepted Epic's workspace to completed and archive its Backlog row."""
    row = _epic_row(root, epic_id)
    if row["Status"] != "AWAITING EPIC ACCEPTANCE":
        raise ForgeError("Epic completion requires AWAITING EPIC ACCEPTANCE")
    active = _workspace_directory(root, "execution/active", epic_id)
    name = active.split("/")[-1]
    moves = [(active, f"execution/completed/{name}")]
    from forge_records import relocation_links
    updates = relocation_links(root, *moves[0])
    lines = updates.get("BACKLOG.md", text(root, "BACKLOG.md").encode()).decode().splitlines(keepends=True)
    backlog_bytes, archive_bytes = _archive_move(root, lines, "Epic Roadmap", epic_id, "COMPLETED")
    updates.update({"BACKLOG.md": backlog_bytes, ARCHIVE_PATH: archive_bytes})
    if apply_token is None:
        return mutation_preview(root, "epic-complete", updates, moves,
                                description=f"Move {active} to completed and archive {epic_id} COMPLETED")[0]
    return mutation_apply(root, "epic-complete", updates, apply_token, moves, validator=_validate_project)


def _section_range(lines, heading):
    start = next((i for i, line in enumerate(lines) if line.rstrip() == f"## {heading}"), None)
    if start is None:
        raise ForgeError(f"Missing section: {heading}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return start, end


def _replace_bullet(content, heading, key, value):
    lines = content.splitlines(keepends=True)
    start, end = _section_range(lines, heading)
    pattern = re.compile(r"^(\s*-\s+\*\*" + re.escape(key) + r":\*\*)\s*(.*)$")
    for index in range(start, end):
        match = pattern.match(lines[index].rstrip("\r\n"))
        if match:
            lines[index] = f"{match.group(1)} {value}\n"
            return "".join(lines)
    raise ForgeError(f"Missing bullet {key!r} in section {heading}")


def _append_table_row(content, heading, row):
    lines = content.splitlines(keepends=True)
    start, end = _section_range(lines, heading)
    insert_at = end
    for index in range(end - 1, start, -1):
        if lines[index].strip():
            insert_at = index + 1
            break
    if insert_at > 0 and not lines[insert_at - 1].endswith("\n"):
        lines[insert_at - 1] += "\n"
    lines.insert(insert_at, row.rstrip("\n") + "\n")
    return "".join(lines)


def accept_record(root, task_path, accepted_by, decision_ref, notes=None, resolve_bug=None, apply_token=None):
    """Record explicit user acceptance facts and transition only this TASK to DONE."""
    if not accepted_by or not decision_ref:
        raise ForgeError("Acceptance requires an accepting user/role and a decision reference")
    content = text(root, task_path)
    meta = frontmatter(content)
    if meta.get("status") != "AWAITING USER ACCEPTANCE":
        raise ForgeError(f"Acceptance requires AWAITING USER ACCEPTANCE, found {meta.get('status')!r}")
    state = workflow_state(content)
    note = decision_ref + (f"; {notes}" if notes else "")
    updated = _replace_bullet(content, "User Acceptance", "Decision", "accepted")
    updated = _replace_bullet(updated, "User Acceptance", "Accepted by", accepted_by)
    updated = _replace_bullet(updated, "User Acceptance", "Accepted at", _today())
    updated = _replace_bullet(updated, "User Acceptance", "Notes", note)
    revision = state.get("implementation_revision") or 0
    updated = _append_table_row(updated, "Iteration History",
                                f"| {revision} | {_today()} | Task acceptance | "
                                f"accepted by {accepted_by} ({decision_ref}) | track evidence retained |")
    updated = _with_frontmatter(updated, {"status": "DONE", "completed_at": _today()})
    updated = _with_workflow_state(updated, {"current_gate": "done"})
    updates = {task_path: updated.encode()}
    if resolve_bug:
        row = next((r for r in defect_rows(root) if r["ID"].strip("`") == resolve_bug), None)
        if row is None:
            raise ForgeError(f"Bug not found: {resolve_bug}")
        if row["Status"] != "SCHEDULED":
            raise ForgeError(f"Only a SCHEDULED Bug can be RESOLVED, found {row['Status']}")
        bug_lines = text(root, "BACKLOG.md").splitlines(keepends=True)
        backlog_bytes, archive_bytes = _archive_move(root, bug_lines, "Defect Queue", resolve_bug, "RESOLVED")
        updates["BACKLOG.md"] = backlog_bytes
        updates[ARCHIVE_PATH] = archive_bytes
    if apply_token is None:
        return mutation_preview(root, "accept-record", updates,
                                description=f"Record acceptance and set {task_path} DONE")[0]
    return mutation_apply(root, "accept-record", updates, apply_token, validator=_validate_project)


def commit_scoped(root, task_path, message=None, paths=None, authorized=False):
    """Stage exactly the recorded scope; commit only under the configured policy."""
    config = within(root, ".ai/project.yaml")
    policy = load_yaml(root, ".ai/project.yaml").get("git", {}).get("policy", "manual") if config.exists() else "manual"
    content = text(root, task_path)
    meta = frontmatter(content)
    state = workflow_state(content)
    recorded_paths = [p for p in ((state.get("review_packet") or {}).get("changed_paths") or []) if recorded(p)]
    scoped = [task_path] + list(paths or recorded_paths)
    scoped = list(dict.fromkeys(scoped))
    missing = [p for p in scoped if not within(root, p).exists()]
    if missing:
        raise ForgeError("Scoped paths missing from disk: " + ", ".join(missing))
    title = next((line[2:].strip() for line in content.splitlines() if line.startswith("# ")), meta.get("id", "task"))
    proposed = message or f"{meta.get('id', 'TASK')}: {title}"
    status = git_capture(root, ["status", "--porcelain=v1", "--untracked-files=all"])
    changed = [line[3:].strip('"') for line in status["stdout"].splitlines() if line.strip()]
    excluded = sorted(set(changed) - set(scoped))
    report = {"policy": policy, "authorized": authorized, "scoped": scoped, "excluded_unrelated": excluded,
              "proposed_message": proposed, "committed": False}
    if policy != "auto_commit_after_acceptance" or not authorized:
        report["reason"] = ("manual policy; obtain separate commit authorization" if policy == "manual"
                            else "authorization flag required")
        return report
    if meta.get("status") != "DONE":
        raise ForgeError("The auto-commit policy requires the TASK to be DONE after explicit acceptance")
    staged = git_capture(root, ["add", "--"] + scoped)
    if staged["exit_code"]:
        raise ForgeError("git add failed: " + staged["stderr"].strip())
    committed = git_capture(root, ["commit", "-m", proposed], timeout=120)
    if committed["exit_code"]:
        raise ForgeError("git commit failed: " + committed["stderr"].strip())
    revision = git_capture(root, ["rev-parse", "HEAD"])
    report.update({"committed": True, "commit": revision["stdout"].strip()})
    return report
