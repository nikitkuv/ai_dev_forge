"""Read-only structural checks for optional mutation campaigns; no backend calls."""
import re

from forge_core import ForgeError, canonical, digest, load_yaml, within


BASE = "quality/mutation-testing"
STATES = {"planned", "running", "awaiting_analysis", "awaiting_decision",
          "waiting_for_fixes", "verifying", "paused", "blocked", "completed", "cancelled"}


def mutation_plan(campaign, require_approval=False):
    """Project stable, user-visible plan fields; progress never changes the digest."""
    if campaign.get("schema_version") != 2:
        raise ForgeError("Use a schema-2 campaign plan before the next execution")
    if (not re.fullmatch(r"MTC-\d{4,}", str(campaign.get("id")))
            or campaign.get("objective") not in ("metrics_only", "audit", "hardening")
            or campaign.get("policy") not in ("audit_first", "batch_then_fix")):
        raise ForgeError("Plan requires a campaign identity, objective and policy")
    tool = campaign.get("tool")
    budget = campaign.get("budget")
    scope = campaign.get("scope")
    if not all(isinstance(value, dict) for value in (tool, budget, scope)):
        raise ForgeError("Plan requires tool, budget and scope mappings")
    for field in ("backend", "version", "baseline_command", "mutation_command"):
        if not isinstance(tool.get(field), str) or not tool[field].strip():
            raise ForgeError(f"Plan requires tool.{field}")
    def paths(record, field, required=True):
        value = record.get(field)
        if (not isinstance(value, list) or (required and not value)
                or any(not isinstance(p, str) or not p.strip() for p in value)):
            raise ForgeError(f"Invalid plan path list: {field}")
        return set(value)
    for field in ("production_paths", "test_paths", "dependency_inputs", "exclusions"):
        paths(scope, field, field in ("production_paths", "test_paths"))
    planned = []
    covered = set()
    batch_ids = set()
    batches = campaign.get("batches")
    if not isinstance(batches, list) or not batches:
        raise ForgeError("Plan requires ordered batch selections")
    for batch in batches:
        selection = batch.get("selection") if isinstance(batch, dict) else None
        if not isinstance(selection, dict) or not selection.get("backend_selector"):
            raise ForgeError("Plan requires a backend selector for each batch")
        identity = batch.get("id")
        if not isinstance(identity, str) or not re.fullmatch(r"B\d{3,}", identity) or identity in batch_ids:
            raise ForgeError("Plan requires unique batch identities")
        batch_ids.add(identity)
        covered.update(paths(selection, "production_paths"))
        if not paths(selection, "test_paths") <= set(scope["test_paths"]):
            raise ForgeError("Batch tests outside planned scope")
        planned.append({"id": batch.get("id"), "selection": selection})
    if covered != set(scope["production_paths"]):
        raise ForgeError("Batch selections must cover the planned production scope")
    limits = {}
    for field in ("execution_seconds", "per_run_timeout_seconds", "workers",
                  "analysis_candidates", "maximum_verification_rounds"):
        value = budget.get(field)
        if type(value) is not int or value < (0 if field == "analysis_candidates" else 1):
            raise ForgeError(f"Invalid plan budget: {field}")
        limits[field] = value
    plan = {key: campaign.get(key) for key in ("id", "objective", "policy", "scope", "tool")}
    plan.update(batches=planned, budget=limits)
    fingerprint = digest(canonical(plan).encode("utf-8"))
    if require_approval:
        auth = campaign.get("authorization")
        if (not isinstance(auth, dict) or not isinstance(auth.get("execution_ref"), str)
                or not auth["execution_ref"].strip() or auth.get("plan_hash") != fingerprint):
            raise ForgeError("Execution needs a user decision matching the current plan")
    return {"plan": plan, "plan_hash": fingerprint}


def verified_findings(root, campaign, batches):
    """Check repair claims against the current, successful full-batch attempt."""
    findings = campaign.get("findings")
    if not isinstance(findings, list):
        raise ForgeError("Hardening closure requires a findings ledger")
    by_id = {b["id"]: b for b in batches}
    recorded = {(str(f.get("run_id")), str(f.get("candidate_id"))) for f in findings
                if isinstance(f, dict) and f.get("classification") == "actionable_test_gap"}
    for batch in batches:
        attempts, current = batch.get("run_ids"), batch.get("current_run_ids")
        if not isinstance(attempts, list) or not isinstance(current, list):
            raise ForgeError("Invalid batch evidence lists")
        for ref in attempts:
            if not isinstance(ref, str) or not re.fullmatch(r"MUT-\d{4,}", ref):
                raise ForgeError("Invalid evidence reference")
            run = load_yaml(root, f"{BASE}/runs/{ref}.yaml")
            analysis = run.get("analysis", {})
            if not isinstance(analysis, dict) or not isinstance(analysis.get("findings", []), list):
                raise ForgeError("Invalid run analysis findings")
            for item in analysis.get("findings", []):
                if not isinstance(item, dict) or (item.get("classification") == "actionable_test_gap"
                        and (ref, str(item.get("candidate_id"))) not in recorded):
                    raise ForgeError("Missing campaign finding for analyzed test gap")
            if ref in current:
                result, baseline = run.get("run"), run.get("baseline")
                if (not isinstance(result, dict) or result.get("outcome") != "COMPLETED"
                        or not isinstance(baseline, dict) or baseline.get("outcome") != "passed"
                        or analysis.get("status") not in ("completed", "skipped_no_candidates")
                        or analysis.get("remaining_candidates", 0) != 0):
                    raise ForgeError("Hardening requires completed current measurements and analysis")
    for finding in findings:
        if not isinstance(finding, dict):
            raise ForgeError("Invalid finding record")
        if (finding.get("classification") != "actionable_test_gap" and not finding.get("work_refs")
                and finding.get("disposition") not in ("fix_requested", "verified")):
            continue
        batch = by_id.get(str(finding.get("batch_id")))
        refs = finding.get("verification_run_ids")
        if (not batch or finding.get("disposition") != "verified" or not finding.get("verification_mapping")
                or not isinstance(refs, list) or not refs or not finding.get("candidate_id")
                or finding.get("run_id") not in batch.get("run_ids", [])):
            raise ForgeError("Actionable finding lacks mapped verification evidence")
        for ref in refs:
            if not isinstance(ref, str) or not re.fullmatch(r"MUT-\d{4,}", ref) or ref not in batch.get("current_run_ids", []):
                raise ForgeError("Finding verification must reference current batch evidence")
            run = load_yaml(root, f"{BASE}/runs/{ref}.yaml")
            link = run.get("campaign")
            result, baseline = run.get("run"), run.get("baseline")
            if (not isinstance(link, dict) or link.get("purpose") not in ("verification", "refresh")
                    or link.get("id") != campaign["id"] or link.get("batch_id") != batch["id"]
                    or not isinstance(link.get("predecessor_run_ids"), list)
                    or finding["run_id"] not in link["predecessor_run_ids"]
                    or link.get("full_batch_selection") != batch.get("selection")
                    or not isinstance(result, dict) or result.get("outcome") != "COMPLETED"
                    or not isinstance(baseline, dict) or baseline.get("outcome") != "passed"):
                raise ForgeError("Finding requires successful full-batch verification")


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
        if campaign.get("schema_version") not in (1, 2) or campaign.get("id") != identity:
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
        if campaign.get("schema_version") == 2:
            started = any(b.get("run_ids") for b in batches)
            if campaign.get("status") in ("running", "verifying", "completed") or started:
                # An incomplete setup can be recorded while the plan awaits a decision.
                if campaign.get("status") not in ("planned", "awaiting_decision", "blocked", "cancelled"):
                    try:
                        mutation_plan(campaign, require_approval=True)
                    except ForgeError as exc:
                        fail(str(exc))
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
                if outcome == "verified" and campaign.get("schema_version") == 2:
                    try:
                        verified_findings(root, campaign, batches)
                    except (OSError, ForgeError) as exc:
                        fail(str(exc))
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
