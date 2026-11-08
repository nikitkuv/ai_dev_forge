"""Prepare fresh-session inputs, run mechanical oracles, validate measured trial records.

No model invocation or synthetic agent scores. See scenarios/06-agent-knowledge.md.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".ai/tools"))
import forge_core as core
import forge_index as index
import forge_knowledge as knowledge
import forge_records as records

FIXTURE = ROOT / "tests/fixtures/agent-knowledge.json"
NUMBERS = ("repeated_mistakes", "unnecessary_investigations", "foreground_seconds", "consolidation_seconds",
           "input_tokens", "output_tokens", "consolidation_input_tokens", "consolidation_output_tokens")


def write(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def record(root, path, meta, body):
    write(root, path, "---\n" + core.canonical(meta) + "\n---\n" + body)


def prepare(root, case, variant):
    """Each caller supplies a new empty project root; never reuse a trial workspace."""
    if root.exists() and any(root.iterdir()):
        raise ValueError("Trial workspace must be empty")
    root.mkdir(parents=True, exist_ok=True)
    write(root, "src/config.txt", "version two" if case.get("change_dependency") else "version one")
    source = None
    if not case.get("empty"):
        finding = dict(id="RF-01", claim="config accepts version one", applicability="config version one only",
                       status=case["status"], evidence_refs=["evidence/config-check.txt"] if case["status"] == "verified" else [],
                       verified_at="2026-11-09" if case["status"] == "verified" else None,
                       verified_revision="fixture-v1" if case["status"] == "verified" else None,
                       recheck_when="config or current contract changes",
                       dependencies=[dict(kind="file", path="src/config.txt", sha256=core.digest(b"version one"))])
        write(root, "evidence/config-check.txt", "Fixture observation: config version one was accepted at fixture-v1. No renderer behavior was tested.")
        source = "investigations/INV-0001-config.md"
        record(root, source, dict(document_type="investigation", id="INV-0001", area="config", reusable_findings=[finding]),
               "# INV-0001\n## Evidence\nconfig constraint. See evidence/config-check.txt.\n")
        if case.get("repeat"):
            record(root, "investigations/INV-0002-config.md", dict(document_type="investigation", id="INV-0002", reusable_findings=[finding]), "# INV-0002\nSame untested config explanation.\n")
        if case.get("moved"):
            source = "execution/completed/EPIC-001-config/tasks/TASK-001.md"
            record(root, source, dict(document_type="task", id="TASK-001", epic_id="EPIC-001", status="DONE", reusable_findings=[finding]), "# TASK-001\nconfig constraint\n")
            record(root, "intents/INT-0001-config.md", dict(document_type="intent", id="INT-0001", knowledge_refs=[dict(ref="TASK-001#RF-01", rationale="reuse", checked_revision="fixture-v1")]), "# INT-0001\n")
    if case.get("conflict"):
        record(root, "decisions/ADR-001-config.md", dict(id="ADR-001", status="accepted"), "# ADR-001\nThe current contract rejects version one; this accepted decision supersedes old config behavior.\n")
    write(root, "ASSIGNMENT.md", case["prompt"] + "\nWork only in this project; do not change lifecycle state.\n")
    manifest = dict(case=case["id"], variant=variant, fixture_sha256=core.digest(FIXTURE.read_bytes()),
                    baseline_revision=json.loads(FIXTURE.read_text())["baseline_revision"],
                    agent_outcome="unmeasured", model=None, settings=None, trial=None, retrieved_sources=None,
                    used_sources=None, quality_pass=None, harmful_reuse=None, fresh_session=None,
                    evidence_ref=None, **{name: None for name in NUMBERS})
    # Outside the agent workspace in normal trial preparation; rubrics are not prompts.
    return source, manifest


def mechanical():
    outcomes = []
    for case in json.loads(FIXTURE.read_text())["cases"]:
        with tempfile.TemporaryDirectory(prefix="forge-knowledge-eval-") as directory:
            root = Path(directory)
            source, _ = prepare(root, case, "B")
            matches = index.query(root, case["query"], match="any")
            if case.get("empty") or case["id"] == "irrelevant-history":
                assert matches["returned"] == 0, case["id"]
            else:
                assert matches["returned"] > 0, case["id"]
            if source:
                finding = knowledge.knowledge_check(root, source, "RF-01")["findings"][0]
                assert finding["verdict"] == case["expected_verdict"], case["id"]
                if case["status"] == "hypothesis":
                    assert not finding["factual_reuse_candidate"]
            if case.get("moved"):
                assert not records.identity_check(root)["advisory"]
            outcomes.append(dict(case=case["id"], mechanical="passed", agent_outcome="unmeasured"))
    return dict(cases=outcomes, note="Mechanical checks only; A/B/C agent comparisons and costs remain unmeasured.")


def validate_trial(trial):
    fixture = json.loads(FIXTURE.read_text())
    if trial.get("case") not in {c["id"] for c in fixture["cases"]} or trial.get("variant") not in ("A", "B", "C"):
        raise ValueError("Unknown case or variant")
    if trial.get("fixture_sha256") != core.digest(FIXTURE.read_bytes()) or trial.get("baseline_revision") != fixture["baseline_revision"]:
        raise ValueError("Trial fixture/baseline mismatch")
    for name in NUMBERS:
        value = trial.get(name)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
            raise ValueError("Invalid metric: " + name)
    if trial.get("agent_outcome") not in ("measured", "unmeasured"):
        raise ValueError("Agent outcome must be measured or unmeasured")
    if trial["agent_outcome"] == "measured":
        if trial.get("fresh_session") is not True or not all(trial.get(k) for k in ("model", "settings", "trial", "evidence_ref")):
            raise ValueError("Measured trial requires fresh-session and runtime evidence")
        if any(not isinstance(trial.get(k), bool) for k in ("quality_pass", "harmful_reuse")):
            raise ValueError("Measured quality requires independent boolean judgments")
        if any(not isinstance(trial.get(k), list) for k in ("retrieved_sources", "used_sources")):
            raise ValueError("Measured trial requires observed source lists")
    elif any(trial.get(k) is not None for k in ("quality_pass", "harmful_reuse", *NUMBERS)):
        raise ValueError("Unmeasured agent outcomes cannot carry invented results")
    return trial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", type=Path)
    parser.add_argument("--case")
    parser.add_argument("--variant", choices=["A", "B", "C"], default="B")
    parser.add_argument("--trial", type=Path, help="Validate an independently recorded trial JSON")
    args = parser.parse_args()
    if args.trial:
        print(json.dumps(validate_trial(json.loads(args.trial.read_text(encoding="utf-8"))), indent=2))
    elif args.prepare:
        cases = json.loads(FIXTURE.read_text())["cases"]
        case = next(c for c in cases if c["id"] == args.case)
        _, manifest = prepare(args.prepare, case, args.variant)
        print(json.dumps(manifest, indent=2))
    else:
        print(json.dumps(mechanical(), indent=2))


if __name__ == "__main__":
    main()
