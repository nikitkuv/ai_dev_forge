"""Derived, rebuildable full-text index over durable records.

A cache under `.ai/local/index.db`, always rebuildable from canonical files.
It never participates in gates, lifecycle transitions, or evidence: queries
return ranked pointers (identifier, kind, path, score, snippet), never record
bodies. Standard library only; no model calls, no network, no embeddings."""
from __future__ import annotations

import os
from pathlib import Path
import re
import sqlite3

from forge_core import (ARCHIVE_PATH, ForgeError, archived_backlog_rows, backlog_rows, canonical, defect_rows,
                        digest, frontmatter, text, within)

INDEX_PATH = ".ai/local/index.db"
SCHEMA_VERSION = 1
INVENTORY_ROOTS = ["execution/planned", "execution/active", "execution/paused", "execution/completed",
                   "investigations", "intents"]
KIND_BY_TYPE = {"task": "TASK", "investigation": "INV", "intent": "INT", "epic_plan": "PLAN"}


class _RebuildNeeded(Exception):
    pass


def _connect(root):
    path = within(root, INDEX_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(path))


def _open(root):
    """Connect and ensure the schema; raise _RebuildNeeded when the file is unusable."""
    conn = _connect(root)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
        stored = dict(conn.execute("SELECT key, value FROM meta").fetchall()).get("schema_version")
        if stored is not None and stored != str(SCHEMA_VERSION):
            raise _RebuildNeeded(f"index schema {stored} != {SCHEMA_VERSION}")
        conn.execute("""CREATE TABLE IF NOT EXISTS records(
            path TEXT PRIMARY KEY, id TEXT NOT NULL, kind TEXT NOT NULL, subject TEXT,
            area TEXT, status TEXT, outcome TEXT, created_at TEXT, updated_at TEXT,
            epic_id TEXT, refs TEXT, mtime REAL NOT NULL, sha256 TEXT NOT NULL, fts_rowid INTEGER NOT NULL)""")
        conn.execute("CREATE INDEX IF NOT EXISTS records_kind ON records(kind)")
        try:
            conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(text, id UNINDEXED)")
        except sqlite3.OperationalError as exc:
            raise ForgeError(f"Search index unavailable: this SQLite build lacks FTS5 ({exc}); "
                             "canonical files and workflows are unaffected") from exc
        conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES('schema_version', ?)", (str(SCHEMA_VERSION),))
        conn.execute("SELECT count(*) FROM records").fetchone()
        conn.commit()
        return conn
    except sqlite3.DatabaseError as exc:
        conn.close()
        raise _RebuildNeeded(f"index unreadable: {exc}") from exc
    except BaseException:
        conn.close()
        raise


def _first_heading(content):
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _record(path, ident, kind, body, subject=None, area=None, status=None, outcome=None,
            created_at=None, updated_at=None, epic_id=None, refs=None, mtime=0.0):
    fields = {"id": ident, "kind": kind, "subject": subject, "area": area, "status": status, "outcome": outcome,
              "created_at": created_at, "updated_at": updated_at, "epic_id": epic_id, "refs": refs, "body": body}
    sha = digest(canonical(fields).encode())
    return {"path": path, "mtime": float(mtime), "sha256": sha,
            "fts_rowid": int(sha[:15], 16), **{key: value for key, value in fields.items() if key != "body"},
            "text": f"{subject or ''}\n{body}".strip()}


def _frontmatter_record(path, content, mtime):
    meta = frontmatter(content)
    document = meta.get("document_type")
    kind = KIND_BY_TYPE.get(document)
    if kind is None:
        kind = next((candidate for prefix, candidate in (("TASK-", "TASK"), ("INV-", "INV"), ("INT-", "INT"), ("ADR-", "ADR"))
                     if str(meta.get("id", "")).startswith(prefix)), "TASK")
    ident = meta.get("id") or meta.get("epic_id")
    if not ident:
        raise ForgeError(f"Record lacks id/epic_id frontmatter: {path}")
    refs = {key: meta[key] for key in ("research_refs", "promoted_to", "sources") if meta.get(key)}
    return _record(path, str(ident), kind, content,
                   subject=(meta.get("subject") if isinstance(meta.get("subject"), str) else None) or _first_heading(content),
                   area=meta.get("area") if isinstance(meta.get("area"), str) else None,
                   status=meta.get("status") or meta.get("document_status"),
                   outcome=meta.get("outcome"), created_at=meta.get("created_at"), updated_at=meta.get("updated_at"),
                   epic_id=meta.get("epic_id"), refs=canonical(refs) if refs else None, mtime=mtime)


def _backlog_unit(root, name, section_rows, kind, subject_column):
    """Records for one Backlog file: one synthetic path per row, one mtime per file."""
    source = within(root, name)
    if not source.exists():
        return {}, []
    mtime = source.stat().st_mtime
    prefix = f"{name}#"
    records, errors = {}, []
    try:
        for row in section_rows(root):
            ident = str(row.get("ID", "")).strip("`")
            if not ident:
                continue
            body = " ".join(f"{key}: {value}" for key, value in row.items())
            records[prefix + ident] = _record(prefix + ident, ident, kind, body,
                                              subject=row.get(subject_column) or ident,
                                              status=row.get("Status"), epic_id=ident if kind == "EPIC" else None,
                                              mtime=mtime)
    except (ForgeError, OSError) as exc:
        errors.append(f"{name}: {exc}")
    return records, errors


def _archive_unit(root):
    source = within(root, ARCHIVE_PATH)
    if not source.exists():
        return {}, []
    mtime = source.stat().st_mtime
    prefix = f"{ARCHIVE_PATH}#"
    records, errors = {}, []
    try:
        for entry in archived_backlog_rows(root):
            cells = entry["cells"]
            ident = str(cells.get("ID", "")).strip("`")
            if not ident:
                continue
            kind = "EPIC" if entry["section"] == "Epic Roadmap" else "BUG"
            subject_column = "Epic and intended outcome" if kind == "EPIC" else "Problem"
            body = f"{entry['year']} " + " ".join(f"{key}: {value}" for key, value in cells.items())
            records[f"{prefix}{entry['year']}#{ident}"] = _record(
                f"{prefix}{entry['year']}#{ident}", ident, kind, body,
                subject=cells.get(subject_column) or ident, status=cells.get("Status"),
                epic_id=ident if kind == "EPIC" else None, mtime=mtime)
    except (ForgeError, OSError) as exc:
        errors.append(f"{ARCHIVE_PATH}: {exc}")
    return records, errors


def _discover(root):
    """{unit: mtime} for every indexable source; Backlog files are row-unit prefixes ending in '#'."""
    found = {}
    resolved = Path(root).resolve()
    for directory in INVENTORY_ROOTS:
        base = within(root, directory)
        if not base.exists():
            continue
        for walk_root, dirs, files in os.walk(base, followlinks=False):
            dirs.sort()
            for filename in sorted(files):
                if filename.endswith(".md"):
                    path = Path(walk_root) / filename
                    found[path.relative_to(resolved).as_posix()] = path.stat().st_mtime
    decisions = within(root, "decisions")
    if decisions.exists():
        for path in sorted(decisions.glob("ADR-*.md")):
            found[path.relative_to(resolved).as_posix()] = path.stat().st_mtime
    for name in ("BACKLOG.md", ARCHIVE_PATH):
        source = within(root, name)
        if source.exists():
            found[name + "#"] = source.stat().st_mtime
    return found


def _collect(root, discover, cached):
    """Split sources into (fresh records to parse, unchanged record paths, errors).

    A stored mtime that still matches the file skips re-parsing; anything else is
    re-read from the canonical file. Units absent from discovery are removals."""
    fresh, unchanged, errors = {}, set(), []
    for unit, mtime in discover.items():
        if unit.endswith("#"):
            prefix = unit
            rows = {path: value for path, value in cached.items() if path.startswith(prefix)}
            if rows and all(value[0] == mtime for value in rows.values()):
                unchanged.update(rows)
            else:
                if prefix == "BACKLOG.md#":
                    for section_rows, kind, column in ((backlog_rows, "EPIC", "Epic and intended outcome"),
                                                       (defect_rows, "BUG", "Problem")):
                        records, problems = _backlog_unit(root, "BACKLOG.md", section_rows, kind, column)
                        fresh.update(records)
                        errors.extend(problems)
                else:
                    records, problems = _archive_unit(root)
                    fresh.update(records)
                    errors.extend(problems)
            continue
        if cached.get(unit) and cached[unit][0] == mtime:
            unchanged.add(unit)
            continue
        try:
            content = within(root, unit).read_text(encoding="utf-8-sig")
            fresh[unit] = _frontmatter_record(unit, content, mtime)
        except (ForgeError, OSError, UnicodeError) as exc:
            errors.append(f"{unit}: {exc}")
    return fresh, unchanged, errors


def _read_cached(conn):
    return {path: (mtime, sha) for path, mtime, sha in
            conn.execute("SELECT path, mtime, sha256 FROM records").fetchall()}


def _plan(root, conn):
    cached = _read_cached(conn)
    discover = _discover(root)
    fresh, unchanged, errors = _collect(root, discover, cached)
    removed = set(cached) - set(fresh) - unchanged
    return fresh, unchanged, removed, errors


def _write(conn, fresh, removed):
    for path in removed:
        row = conn.execute("SELECT fts_rowid FROM records WHERE path = ?", (path,)).fetchone()
        if row:
            conn.execute("DELETE FROM records_fts WHERE rowid = ?", (row[0],))
        conn.execute("DELETE FROM records WHERE path = ?", (path,))
    for record in fresh.values():
        conn.execute("""INSERT OR REPLACE INTO records(path, id, kind, subject, area, status, outcome,
                        created_at, updated_at, epic_id, refs, mtime, sha256, fts_rowid)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (record["path"], record["id"], record["kind"], record["subject"], record["area"],
                      record["status"], record["outcome"], record["created_at"], record["updated_at"],
                      record["epic_id"], record["refs"], record["mtime"], record["sha256"], record["fts_rowid"]))
        conn.execute("DELETE FROM records_fts WHERE rowid = ?", (record["fts_rowid"],))
        conn.execute("INSERT INTO records_fts(rowid, text, id) VALUES(?,?,?)",
                     (record["fts_rowid"], record["text"], record["id"]))
    conn.commit()


def reconcile(root):
    """Bring the index in line with canonical files; rebuild deterministically when unusable."""
    try:
        conn = _open(root)
    except _RebuildNeeded:
        within(root, INDEX_PATH).unlink(missing_ok=True)
        conn = _open(root)
    try:
        fresh, unchanged, removed, errors = _plan(root, conn)
        if fresh or removed:
            _write(conn, fresh, removed)
        total = conn.execute("SELECT count(*) FROM records").fetchone()[0]
        return {"status": "current", "total": total, "updated": len(fresh), "removed": len(removed),
                "reused_unchanged": len(unchanged), "errors": errors}
    finally:
        conn.close()


def rebuild(root):
    """Discard the cache and rebuild it fully from canonical files."""
    within(root, INDEX_PATH).unlink(missing_ok=True)
    return reconcile(root)


def status(root):
    """Index shape and freshness without writing."""
    try:
        conn = _open(root)
    except _RebuildNeeded as exc:
        return {"index_exists": within(root, INDEX_PATH).exists(), "fresh": False, "reason": str(exc),
                "records": 0, "errors": []}
    try:
        fresh, unchanged, removed, errors = _plan(root, conn)
        return {"index_exists": True, "records": _read_cached(conn) and len(_read_cached(conn)),
                "fresh": not fresh and not removed, "pending_updates": len(fresh),
                "pending_removals": len(removed), "errors": errors}
    finally:
        conn.close()


def _match_expression(query_text):
    """Quote every term so user text can never inject FTS operators."""
    tokens = []
    for token in query_text.split():
        tokens.extend(part for part in token.replace('"', " ").split() if part)
    if not tokens:
        raise ForgeError("Query needs at least one non-empty term")
    return " ".join(f'"{token}"' for token in tokens)


def query(root, query_text, kinds=None, area=None, since=None, limit=20):
    """Ranked pointers into canonical files; never bodies, never a judgment."""
    if kinds is not None and not kinds:
        raise ForgeError("Empty --kind filter")
    freshness = reconcile(root)
    conn = _connect(root)
    try:
        expression = _match_expression(query_text)
        matches = conn.execute("SELECT id, bm25(records_fts) FROM records_fts WHERE records_fts MATCH ? LIMIT 500",
                               (expression,)).fetchall()
        catalog = conn.execute("""SELECT path, id, kind, subject, area, status, outcome, created_at, updated_at,
                                  fts_rowid FROM records""").fetchall()
        by_id = {}
        for row in catalog:
            by_id.setdefault(row[1], []).append(row)
        results = []
        for ident, score in matches:
            for (path, _, kind, subject, row_area, row_status, outcome, created_at, updated_at, fts_rowid) in by_id.get(ident, ()):
                if kinds is not None and kind not in kinds:
                    continue
                if area is not None and (row_area or "") != area:
                    continue
                if since is not None:
                    date = created_at or updated_at
                    if not date or str(date) < since:
                        continue
                snippet = conn.execute(
                    "SELECT snippet(records_fts, 0, '', '', '…', 16) FROM records_fts WHERE rowid = ?",
                    (fts_rowid,)).fetchone()
                results.append({"id": ident, "kind": kind, "path": path, "score": round(score, 4) + 0.0,
                                "subject": subject, "status": row_status, "outcome": outcome,
                                "snippet": snippet[0] if snippet else None})
        results.sort(key=lambda item: (item["score"], item["id"], item["path"]))
        return {"query": query_text, "filters": {"kind": kinds, "area": area, "since": since},
                "freshness": freshness, "results": results[:limit], "returned": min(len(results), limit),
                "note": "Ranked pointers only; read the canonical file before relying on any record"}
    finally:
        conn.close()
