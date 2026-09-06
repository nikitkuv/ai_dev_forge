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
    c = sub.add_parser("checks", help="Execute only an approved JSON check packet")
    c.add_argument("packet")
    c.add_argument("--execute", action="store_true")
    c.add_argument("--reuse", action="store_true")
    sub.add_parser("metrics")
    c = sub.add_parser("metrics-record")
    c.add_argument("packet")
    c = sub.add_parser("task-start-check")
    c.add_argument("task")
    c = sub.add_parser("role", help="Bounded external planner/reviewer transport; no automatic fallback")
    c.add_argument("--orchestrator", required=True, choices=["codex", "claude"])
    c.add_argument("--role", required=True, choices=["reviewer", "epic-planner"])
    c.add_argument("--prompt-file")
    c.add_argument("--preflight", action="store_true")
    c.add_argument("--timeout", type=float, default=900)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    root = Path(args.root).resolve()
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
    elif args.command in ("checks", "metrics", "metrics-record"):
        from forge_runtime import checks, metrics, metrics_record
        if args.command == "metrics":
            result = metrics(root)
        else:
            packet = json.loads(text(root, args.packet))
            result = checks(root, packet, args.execute, args.reuse) if args.command == "checks" else metrics_record(root, packet)
    else:
        from forge_runtime import role
        config = load_yaml(root, ".ai/project.yaml")
        mode = config.get("role_execution", {}).get("mode")
        expected = "claude_with_codex" if args.orchestrator == "claude" else "codex_with_claude"
        if mode != expected:
            raise ForgeError("Active-orchestrator/route mismatch; native mode must use native subagents")
        provider = "codex" if args.orchestrator == "claude" else "claude"
        mapping = {"model": "gpt-5.6-sol", "effort": "medium"} if provider == "codex" else config["models"]["claude"]["strong"]
        if not args.preflight and not args.prompt_file:
            raise ForgeError("--prompt-file required")
        prompt = text(root, args.prompt_file) if args.prompt_file else ""
        result = role(root, provider, args.role, prompt, mapping["model"], mapping["effort"], args.timeout, args.preflight)
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
