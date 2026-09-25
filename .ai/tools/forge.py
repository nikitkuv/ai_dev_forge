#!/usr/bin/env python3
"""Forge local automation. Run with --help; successful commands print compact JSON."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from forge_core import ForgeError, budget, canonical, context, frontmatter, load_yaml, section, snapshot, text, validate, within


def authorization(root, task_path):
    config = load_yaml(root, ".ai/project.yaml")
    policy = config.get("automation", {}).get("authorization", {})
    if policy.get("mode", "strict") != "bounded_task_starts":
        return {"authorized": False, "reason": "Separate Task Start required by strict policy"}
    if not policy.get("decision_ref") or not policy.get("approved_by"):
        raise ForgeError("Bounded authorization requires a recorded user decision and approver")
    try:
        expiry = datetime.fromisoformat(policy["expires_at"].replace("Z", "+00:00"))
        if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
            raise ForgeError("Bounded authorization expired or lacks timezone")
    except (KeyError, TypeError, ValueError) as exc:
        raise ForgeError("A future ISO expires_at with timezone is required") from exc
    task = frontmatter(text(root, task_path))
    if task.get("status") != "TODO" or task.get("definition_status") != "approved":
        return {"authorized": False, "reason": "Task is not approved TODO"}
    current = snapshot(root, [task_path])["fingerprint"]
    entries = policy.get("task_starts", [])
    match = next((e for e in entries if e.get("task_path") == task_path and e.get("definition_fingerprint") == current), None)
    return {"authorized": match is not None, "decision_ref": policy["decision_ref"],
            "reason": "Exact approved definition matches" if match else "Task absent or definition changed",
            "remaining_checks": ["dependencies", "blockers", "no other code-writing task", "delivery-track eligibility"],
            "grants": ["Task Start only"] if match else []}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".", help="Target project root; never bootstraps it")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("context", help="Compact metadata inventory; no model invocation")
    c.add_argument("--offset", type=int, default=0)
    c.add_argument("--limit", type=int, default=30)
    c.add_argument("--include-completed", action="store_true")
    c = sub.add_parser("section", help="List headings or extract exact ATX section(s)")
    c.add_argument("path")
    c.add_argument("--heading")
    c.add_argument("--offset", type=int, default=0)
    c.add_argument("--limit", type=int, default=12000)
    for name in ("fingerprint", "budget"):
        c = sub.add_parser(name)
        c.add_argument("paths", nargs="+")
    c = sub.add_parser("validate")
    c.add_argument("--project", action="store_true")
    c.add_argument("--adapters", action="store_true")
    c = sub.add_parser("adapters", help="Preview by default; apply exact reviewed preview token")
    c.add_argument("--diff", action="store_true")
    c.add_argument("--apply", metavar="PREVIEW_TOKEN")
    c.add_argument("--approve-collision", action="append", default=[])
    c.add_argument("--recover", action="store_true")
    migrate = sub.add_parser("migrate", help="Deterministic framework migration; stage .ai-next/ and run from the staged bundle")
    migrate.add_argument("--diff", action="store_true")
    migrate.add_argument("--apply", metavar="PREVIEW_TOKEN")
    migrate.add_argument("--set", dest="sets", action="append", default=[])
    migrate.add_argument("--router-shared")
    migrate.add_argument("--approve-collision", action="append", default=[])
    migrate.add_argument("--recover", action="store_true")
    c = sub.add_parser("checks", help="Execute only an approved JSON check packet")
    c.add_argument("packet")
    c.add_argument("--execute", action="store_true")
    c.add_argument("--reuse", action="store_true")
    c.add_argument("--task", help="Record observed check metrics for this canonical TASK")
    sub.add_parser("metrics")
    c = sub.add_parser("metrics-record")
    c.add_argument("packet")
    c = sub.add_parser("task-start-check")
    c.add_argument("task")
    c = sub.add_parser("next-id", help="Monotonic max-plus-one identifier allocation")
    c.add_argument("--kind", required=True, choices=["task", "bug", "inv", "int", "epic", "adr", "mut"])
    c = sub.add_parser("identity-check", help="Compact canonical identity and link diagnostics")
    c.add_argument("--path", action="append", default=[], help="Include hashes/declarations for these canonical files")
    c.add_argument("--details", action="store_true", help="Include the full declaration and file-hash maps")
    c = sub.add_parser("records-write", help="Render ID aliases and write a validated canonical batch")
    c.add_argument("packet")
    c.add_argument("--apply", metavar="PREVIEW_TOKEN")
    c = sub.add_parser("links-repair", help="Preview repairs of uniquely resolvable record links")
    c.add_argument("--apply", metavar="PREVIEW_TOKEN")
    sub.add_parser("records-recover", help="Recover the shared lifecycle record transaction")
    c = sub.add_parser("evidence-check", help="Recompute recorded evidence fingerprints; verdicts, not judgments")
    c.add_argument("task", nargs="?")
    c.add_argument("--epic")
    c = sub.add_parser("review-packet", help="Assemble the compact Review Packet from recorded TASK data")
    c.add_argument("path")
    c = sub.add_parser("checks-new", help="Write or extend an approved-checks packet; explicit argv only")
    c.add_argument("output")
    c.add_argument("--stage", required=True, choices=["task", "epic"])
    c.add_argument("--input", dest="inputs", action="append", default=[])
    c.add_argument("--cacheable", action="store_true")
    c.add_argument("--inputs-complete", action="store_true")
    c.add_argument("--id", required=True)
    c.add_argument("--timeout", type=float, default=60)
    c.add_argument("--cwd", default=".")
    c.add_argument("argv", nargs=argparse.REMAINDER)
    c = sub.add_parser("inv-create", help="Allocate the next INV and scaffold the canonical record")
    c.add_argument("--subject", required=True)
    c.add_argument("--area", required=True)
    c.add_argument("--paths", nargs="*", default=[])
    c.add_argument("--name")
    c.add_argument("--apply", metavar="PREVIEW_TOKEN")
    backlog = sub.add_parser("backlog", help="Exact-row Backlog edits through preview/apply")
    backlog_sub = backlog.add_subparsers(dest="backlog_command", required=True)
    add_bug = backlog_sub.add_parser("add-bug")
    add_bug.add_argument("--problem", required=True)
    add_bug.add_argument("--severity", required=True)
    add_bug.add_argument("--priority", required=True)
    add_bug.add_argument("--requirement", default="—")
    add_bug.add_argument("--sources", default="—")
    add_bug.add_argument("--research", default="—")
    add_bug.add_argument("--id")
    add_bug.add_argument("--apply", metavar="PREVIEW_TOKEN")
    update_row = backlog_sub.add_parser("update-row")
    update_row.add_argument("--id", required=True)
    update_row.add_argument("--set", dest="sets", action="append", required=True)
    update_row.add_argument("--move-before")
    update_row.add_argument("--apply", metavar="PREVIEW_TOKEN")
    archive_row = backlog_sub.add_parser("archive-row", help="Move one terminal row to BACKLOG-ARCHIVE.md")
    archive_row.add_argument("--id", required=True)
    archive_row.add_argument("--apply", metavar="PREVIEW_TOKEN")
    archive_all = backlog_sub.add_parser("archive-all", help="Backfill every legacy terminal row in one transaction")
    archive_all.add_argument("--apply", metavar="PREVIEW_TOKEN")
    stale_rows = backlog_sub.add_parser("stale-rows", help="Read-only staleness report from Git row history")
    stale_rows.add_argument("--older-than", type=int, default=90)
    c = sub.add_parser("query", help="Ranked record pointers from the derived local search index")
    c.add_argument("text")
    c.add_argument("--kind", help="Comma-separated filter: TASK,INV,INT,ADR,PLAN,EPIC,BUG")
    c.add_argument("--area")
    c.add_argument("--since", help="YYYY-MM or YYYY-MM-DD floor on recorded dates")
    c.add_argument("--limit", type=int, default=20)
    index = sub.add_parser("index", help="Derived search index maintenance")
    index_sub = index.add_subparsers(dest="index_command", required=True)
    index_sub.add_parser("rebuild")
    index_sub.add_parser("status")
    transition = sub.add_parser("transition", help="Execute one approved status transition")
    transition_sub = transition.add_subparsers(dest="transition_command", required=True)
    transition_task = transition_sub.add_parser("task")
    transition_task.add_argument("path")
    transition_task.add_argument("--to", required=True)
    transition_task.add_argument("--apply", metavar="PREVIEW_TOKEN")
    transition_epic = transition_sub.add_parser("epic")
    transition_epic.add_argument("epic_id")
    transition_epic.add_argument("--to", required=True)
    transition_epic.add_argument("--apply", metavar="PREVIEW_TOKEN")
    c = sub.add_parser("epic-start", help="Atomic planned-to-active workspace move plus Backlog transition")
    c.add_argument("epic_id")
    c.add_argument("--apply", metavar="PREVIEW_TOKEN")
    c = sub.add_parser("epic-complete", help="Atomic active-to-completed workspace move plus Backlog transition")
    c.add_argument("epic_id")
    c.add_argument("--apply", metavar="PREVIEW_TOKEN")
    c = sub.add_parser("accept-record", help="Record explicit acceptance facts and set one TASK DONE")
    c.add_argument("path")
    c.add_argument("--by", required=True)
    c.add_argument("--decision-ref", required=True)
    c.add_argument("--notes")
    c.add_argument("--resolve-bug")
    c.add_argument("--apply", metavar="PREVIEW_TOKEN")
    c = sub.add_parser("commit-scoped", help="Stage exactly the recorded TASK scope under the Git policy")
    c.add_argument("path")
    c.add_argument("--message")
    c.add_argument("--paths", nargs="*", default=[])
    c.add_argument("--authorized", action="store_true")
    c = sub.add_parser("role", help="Bounded external planner/reviewer transport; no automatic fallback")
    c.add_argument("--orchestrator", required=True, choices=["codex", "claude"])
    c.add_argument("--role", required=True, choices=["reviewer", "epic-planner"])
    c.add_argument("--prompt-file")
    c.add_argument("--assignment-file", help="Assignment only; the helper embeds the neutral contract itself")
    c.add_argument("--preflight", action="store_true")
    c.add_argument("--timeout", type=float, default=900)
    c.add_argument("--task", help="Record observed role duration, calls and available usage for this TASK")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    root = Path(args.root).resolve()
    metric_task = None
    if args.command in ("role", "checks") and args.task:
        metric_task = frontmatter(text(root, args.task))
        if metric_task.get("document_type") != "task" or not metric_task.get("id"):
            raise ForgeError("--task must identify a canonical TASK")
        if metric_task.get("delivery_track", "standard") not in ("fast", "standard"):
            raise ForgeError("Invalid metric TASK delivery track")
    if getattr(args, "offset", 0) < 0 or getattr(args, "limit", 1) <= 0:
        raise ForgeError("offset must be non-negative and limit positive")
    if args.command == "context":
        result = context(root, args.offset, args.limit, args.include_completed)
    elif args.command == "section":
        result = section(root, args.path, args.heading, args.offset, args.limit)
    elif args.command == "fingerprint":
        result = snapshot(root, args.paths)
    elif args.command == "budget":
        result = budget(root, args.paths)
    elif args.command == "task-start-check":
        result = authorization(root, args.task)
    elif args.command == "next-id":
        from forge_lifecycle import next_id
        result = next_id(root, args.kind)
    elif args.command == "identity-check":
        from forge_records import identity_check
        result = identity_check(root)
        result["identity_count"] = len(result["declarations"])
        if args.path:
            selected = {within(root, name).relative_to(root).as_posix() for name in args.path}
            unknown = selected - set(result["file_hashes"])
            if unknown:
                raise ForgeError("Not an existing canonical record: " + ", ".join(sorted(unknown)))
            result["file_hashes"] = {p: h for p, h in result["file_hashes"].items() if p in selected}
            result["declarations"] = {i: paths for i, paths in result["declarations"].items()
                                      if any(p in selected for p in paths)}
        elif not args.details:
            result.pop("file_hashes")
            result.pop("declarations")
    elif args.command == "records-write":
        from forge_records import records_write
        result = records_write(root, json.loads(text(root, args.packet)), args.apply)
    elif args.command == "links-repair":
        from forge_records import links_repair
        result = links_repair(root, args.apply)
    elif args.command == "records-recover":
        from forge_core import Transaction
        result = Transaction(root, "lifecycle").restore()
    elif args.command == "evidence-check":
        from forge_lifecycle import evidence_check, evidence_check_epic
        if bool(args.task) == bool(args.epic):
            raise ForgeError("Pass either a TASK path or --epic <EPIC-ID>")
        result = evidence_check_epic(root, args.epic) if args.epic else evidence_check(root, args.task)
    elif args.command == "review-packet":
        from forge_lifecycle import review_packet
        result = review_packet(root, args.path)
    elif args.command == "checks-new":
        from forge_runtime import checks_new
        argv = list(args.argv)
        if argv and argv[0] == "--":
            argv = argv[1:]
        result = checks_new(root, args.output, args.stage, args.inputs, args.id, argv, args.timeout,
                            args.cacheable, args.inputs_complete, args.cwd)
    elif args.command == "inv-create":
        from forge_lifecycle import inv_create
        result = inv_create(root, args.subject, args.area, args.paths, args.name, args.apply)
    elif args.command == "backlog":
        from forge_lifecycle import backlog_add_bug, backlog_update_row
        sets = {}
        for item in args.sets if args.backlog_command == "update-row" else []:
            if "=" not in item:
                raise ForgeError("--set expects Column=Value")
            column, value = item.split("=", 1)
            sets[column.strip()] = value
        if args.backlog_command == "add-bug":
            result = backlog_add_bug(root, args.problem, args.severity, args.priority, args.requirement,
                                     args.sources, args.research, args.id, args.apply)
        elif args.backlog_command == "archive-row":
            from forge_lifecycle import backlog_archive_row
            result = backlog_archive_row(root, args.id, args.apply)
        elif args.backlog_command == "archive-all":
            from forge_lifecycle import backlog_archive_all
            result = backlog_archive_all(root, args.apply)
        elif args.backlog_command == "stale-rows":
            from forge_lifecycle import backlog_stale_rows
            result = backlog_stale_rows(root, args.older_than)
        else:
            result = backlog_update_row(root, args.id, sets, args.move_before, args.apply)
    elif args.command == "transition":
        from forge_lifecycle import transition_epic, transition_task
        if args.transition_command == "task":
            result = transition_task(root, args.path, args.to, args.apply)
        else:
            result = transition_epic(root, args.epic_id, args.to, args.apply)
    elif args.command == "epic-start":
        from forge_lifecycle import epic_start
        result = epic_start(root, args.epic_id, args.apply)
    elif args.command == "epic-complete":
        from forge_lifecycle import epic_complete
        result = epic_complete(root, args.epic_id, args.apply)
    elif args.command == "accept-record":
        from forge_lifecycle import accept_record
        result = accept_record(root, args.path, args.by, args.decision_ref, args.notes, args.resolve_bug, args.apply)
    elif args.command == "commit-scoped":
        from forge_lifecycle import commit_scoped
        result = commit_scoped(root, args.path, args.message, args.paths, args.authorized)
    elif args.command == "query":
        from forge_index import query as index_query
        kinds = ([value.strip().upper() for value in args.kind.split(",") if value.strip()]
                 if args.kind else None)
        result = index_query(root, args.text, kinds, args.area, args.since, args.limit)
    elif args.command == "index":
        from forge_index import rebuild as index_rebuild, status as index_status
        result = index_rebuild(root) if args.index_command == "rebuild" else index_status(root)
    elif args.command == "validate":
        result = validate(root, args.project)
        if args.adapters:
            from forge_adapters import preview
            inspection = preview(root)[0]
            result["adapter_drift"] = [c["path"] for c in inspection["changes"]]
            result["passed"] = result["passed"] and not inspection["changes"]
    elif args.command == "adapters":
        from forge_adapters import apply, preview, recover
        if args.recover and args.apply:
            raise ForgeError("Choose apply or recovery")
        result = recover(root) if args.recover else apply(root, args.apply, args.approve_collision) if args.apply else preview(root, args.diff)[0]
    elif args.command == "migrate":
        from forge_migration import apply_migrate, preview_migrate, recover_migrate
        if args.recover and (args.apply or args.sets or args.router_shared):
            raise ForgeError("Choose recovery or a migration operation")
        sets = {}
        for item in args.sets:
            if "=" not in item:
                raise ForgeError("--set expects key=value")
            key, value = item.split("=", 1)
            sets[key.strip()] = value
        if args.recover:
            result = recover_migrate(root)
        elif args.apply:
            result = apply_migrate(root, args.apply, sets, args.router_shared, args.approve_collision)
        else:
            result = preview_migrate(root, args.router_shared, args.diff, sets)[0]
    elif args.command in ("checks", "metrics", "metrics-record"):
        from forge_runtime import checks, metrics, metrics_record
        if args.command == "metrics":
            result = metrics(root)
        else:
            packet = json.loads(text(root, args.packet))
            result = checks(root, packet, args.execute, args.reuse) if args.command == "checks" else metrics_record(root, packet)
    else:
        from forge_runtime import compose_role_prompt, role
        config = load_yaml(root, ".ai/project.yaml")
        mode = config.get("role_execution", {}).get("mode")
        expected = "claude_with_codex" if args.orchestrator == "claude" else "codex_with_claude"
        if mode != expected:
            raise ForgeError("Active-orchestrator/route mismatch; native mode must use native subagents")
        provider = "codex" if args.orchestrator == "claude" else "claude"
        mapping = {"model": "gpt-6-sol", "effort": "high"} if provider == "codex" else config["models"]["claude"]["strong"]
        transient = None
        if args.assignment_file:
            transient = compose_role_prompt(root, args.role, args.assignment_file)
        elif not args.prompt_file and not args.preflight:
            raise ForgeError("--prompt-file or --assignment-file required")
        try:
            source = args.prompt_file if args.prompt_file else transient
            prompt = text(root, source) if source else ""
            result = role(root, provider, args.role, prompt, mapping["model"], mapping["effort"], args.timeout, args.preflight)
        finally:
            if transient:
                within(root, transient).unlink(missing_ok=True)
    if metric_task and not getattr(args, "preflight", False):
        from forge_runtime import record_observation
        record_observation(root, metric_task, args.command, result)
    print(canonical(result))
    if result.get("errors") or result.get("passed") is False or result.get("authorized") is False:
        return 1
    return result.get("exit_code", 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except (ForgeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(canonical({"error": str(exc), "action": "Inspect the reported input; no model fallback or lifecycle transition was performed"}))
        sys.exit(2)
