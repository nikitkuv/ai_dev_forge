"""Read-only structural checks for optional mutation campaigns; no backend calls."""
import re

from forge_core import ForgeError, load_yaml, within


BASE = "quality/mutation-testing"
STATES = {"planned", "running", "awaiting_analysis", "awaiting_decision",
          "waiting_for_fixes", "verifying", "paused", "blocked", "completed", "cancelled"}


def campaign_errors(root, registry):
    errors = []
    entries = registry.get("campaigns", [])
    if not isinstance(entries, list) or any(not isinstance(item, str) for item in entries):
        return ["Mutation campaigns must be a list of MTC identities"]
    valid = {item for item in entries if re.fullmatch(r"MTC-\d{4,}", item)}
    if len(valid) != len(entries):
        errors.append("Mutation campaigns require unique MTC identities")
    directory = within(root, f"{BASE}/campaigns")
    disk = {path.stem for path in directory.glob("MTC-*.yaml")} if directory.exists() else set()
    for identity in sorted(valid - disk):
        errors.append(f"Missing mutation campaign record: {identity}")
    for identity in sorted(disk - valid):
        errors.append(f"Unregistered mutation campaign record: {identity}")
    next_id = registry.get("next_campaign_id")
    if entries or next_id is not None:
        if not isinstance(next_id, str) or not re.fullmatch(r"MTC-\d{4,}", next_id):
            errors.append("Mutation next_campaign_id must be an MTC identity")
        elif valid and int(next_id[4:]) <= max(int(item[4:]) for item in valid):
            errors.append("Mutation next_campaign_id must exceed retained identities")
    raw_runs = registry.get("runs") or []
    run_ids = {item if isinstance(item, str) else item.get("id")
               for item in raw_runs if isinstance(item, (str, dict))}
    linked = {}
    for identity in sorted(valid & disk):
        try:
            campaign = load_yaml(root, f"{BASE}/campaigns/{identity}.yaml")
        except (OSError, ForgeError) as exc:
            errors.append(f"{identity}: {exc}")
            continue
        def fail(message):
            errors.append(f"{identity}: {message}")
        if campaign.get("schema_version") != 1 or campaign.get("id") != identity:
            fail("campaign schema or identity mismatch")
        if campaign.get("status") not in tuple(STATES):
            fail("invalid campaign status")
        if campaign.get("objective") not in ("metrics_only", "audit", "hardening"):
            fail("invalid campaign objective")
        if campaign.get("policy") not in ("audit_first", "batch_then_fix"):
            fail("invalid campaign policy")
        budget = campaign.get("budget") or {}
        if not isinstance(budget, dict):
            fail("budget must be a mapping")
            continue
        for limit, used in (("execution_seconds", "consumed_execution_seconds"),
                            ("analysis_candidates", "consumed_analysis_candidates")):
            cap, consumed = budget.get(limit), budget.get(used)
            if (type(cap) is not int or cap < 0 or type(consumed) is not int or consumed < 0):
                fail(f"finite nonnegative budget required: {limit}/{used}")
            elif consumed > cap and campaign.get("status") not in ("paused", "blocked", "cancelled"):
                fail(f"exhausted budget must pause: {limit}")
        for field in ("per_run_timeout_seconds", "workers", "maximum_verification_rounds"):
            value = budget.get(field)
            if type(value) is not int or value <= 0:
                fail(f"positive finite budget required: {field}")
        batches = campaign.get("batches")
        if not isinstance(batches, list) or not batches or any(not isinstance(b, dict) for b in batches):
            fail("nonempty ordered batch records required")
            continue
        batch_ids = [b.get("id") for b in batches]
        if any(not isinstance(b, str) or not re.fullmatch(r"B\d{3,}", b) for b in batch_ids):
            fail("invalid batch identity")
            continue
        if len(set(batch_ids)) != len(batch_ids):
            fail("duplicate batch identity")
        for batch in batches:
            attempts = batch.get("run_ids", [])
            current = batch.get("current_run_ids", [])
            if (not isinstance(attempts, list) or not isinstance(current, list)
                    or any(not isinstance(r, str) for r in attempts + current)):
                fail("batch run identities must be lists of strings")
                continue
            if len(set(attempts)) != len(attempts) or not set(current).issubset(attempts):
                fail("duplicate attempts or current evidence outside batch history")
            for run_id in attempts:
                if run_id in linked or run_id not in run_ids:
                    fail(f"duplicate or unregistered run link: {run_id}")
                linked[run_id] = (identity, batch["id"])
        checkpoint = campaign.get("checkpoint") or {}
        if not isinstance(checkpoint, dict):
            fail("checkpoint must be a mapping")
            continue
        if checkpoint.get("batch_id") is not None and checkpoint["batch_id"] not in batch_ids:
            fail("checkpoint references unknown batch")
        if campaign.get("status") == "completed":
            closure = campaign.get("closure") or {}
            if not isinstance(closure, dict):
                fail("closure must be a mapping")
                continue
            outcome = closure.get("outcome")
            expected = {"metrics_only": "metrics_collected", "audit": "analyzed", "hardening": "verified"}
            if not closure.get("completed_at") or not closure.get("evidence_refs"):
                fail("completed campaign requires timestamp and evidence")
            if outcome == "accepted_exceptions":
                if not closure.get("decision_ref") or not closure.get("exceptions"):
                    fail("accepted exceptions require explicit decision and residual exceptions")
            else:
                if outcome != expected.get(str(campaign.get("objective"))):
                    fail("closure outcome does not match objective")
                if closure.get("exceptions") or closure.get("remaining_work"):
                    fail("ordinary completion cannot hide remaining work or exceptions")
                if any(b.get("stale") is not False or b.get("status") != "closed"
                       or not b.get("current_run_ids") or b.get("remaining_selection") for b in batches):
                    fail("ordinary completion requires current closed batches with no remainder")
    for run_id in sorted(r for r in run_ids if isinstance(r, str) and re.fullmatch(r"MUT-\d{4,}", r)):
        path = within(root, f"{BASE}/runs/{run_id}.yaml")
        if not path.exists():
            continue # Existing registry validator reports missing runs.
        try:
            run = load_yaml(root, f"{BASE}/runs/{run_id}.yaml")
        except (OSError, ForgeError) as exc:
            errors.append(f"{run_id}: {exc}")
            continue
        link = run.get("campaign") or {}
        if not isinstance(link, dict):
            errors.append(f"{run_id}: campaign link must be a mapping")
            continue
        if not link.get("id") and run_id not in linked:
            continue # Legacy standalone history.
        if linked.get(run_id) != (link.get("id"), link.get("batch_id")):
            errors.append(f"{run_id}: nonreciprocal campaign/batch link")
        if link.get("purpose") not in ("initial", "retry", "verification", "refresh"):
            errors.append(f"{run_id}: invalid campaign run purpose")
        predecessors = link.get("predecessor_run_ids", [])
        if (not isinstance(predecessors, list) or any(not isinstance(p, str) or p == run_id
                or p not in run_ids for p in predecessors)):
            errors.append(f"{run_id}: invalid predecessor run")
        analysis = run.get("analysis") or {}
        if not isinstance(analysis, dict):
            errors.append(f"{run_id}: analysis must be a mapping")
            continue
        done = analysis.get("analyzed_candidate_ids", [])
        remaining = analysis.get("remaining_candidate_ids", [])
        if not isinstance(done, list) or not isinstance(remaining, list) or any(not isinstance(c, str) for c in done + remaining):
            errors.append(f"{run_id}: candidate IDs must be string lists")
        elif (len(set(done + remaining)) != len(done + remaining)
              or analysis.get("analyzed_candidates", 0) != len(done)
              or analysis.get("remaining_candidates", 0) != len(remaining)):
            errors.append(f"{run_id}: inconsistent candidate continuation ledger")
    return errors
