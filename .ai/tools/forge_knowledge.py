"""Optional source-backed knowledge. Read-only checks, never lifecycle authority."""
from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
import re

from forge_core import ForgeError, digest, frontmatter, text, within

FINDING_ID = r"RF-[0-9]{2,}"
REFERENCE = rf"(?:TASK|INV)-[0-9]+#{FINDING_ID}"


def finding_errors(value):
    if not isinstance(value, dict):
        return ["Finding must be a mapping"]
    errors = []
    for field in ("verified_at", "verified_revision"):
        if field not in value:
            errors.append(f"Missing {field}; use null for an unverified finding")
    for field in ("id", "claim", "applicability", "recheck_when"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append(f"Missing or invalid {field}")
    if not re.fullmatch(FINDING_ID, str(value.get("id", ""))):
        errors.append("Invalid finding ID")
    if value.get("status") not in ("hypothesis", "verified", "obsolete"):
        errors.append("Invalid finding status")
    evidence = value.get("evidence_refs")
    if not isinstance(evidence, list) or any(not isinstance(v, str) or not v.strip() for v in evidence):
        errors.append("evidence_refs must be a list of source references")
    if value.get("status") == "verified":
        if not evidence or not isinstance(value.get("verified_revision"), str) or not value["verified_revision"].strip():
            errors.append("Verified finding requires evidence, date and revision")
        try:
            date.fromisoformat(str(value.get("verified_at")))
        except ValueError:
            errors.append("Verified finding requires an ISO verification date")
    if not isinstance(value.get("dependencies"), list):
        errors.append("dependencies must be a list")
    if "correction_of" in value and not re.fullmatch(REFERENCE, str(value["correction_of"])):
        errors.append("Invalid correction_of reference")
    return errors


def finding_summary(meta):
    """Do not inject claims, evidence or dependency bodies into routine inventory."""
    values = meta.get("reusable_findings", [])
    if not isinstance(values, list):
        return {"count": None, "ids": [], "malformed": True}
    return {"count": len(values), "ids": [v["id"] for v in values
            if isinstance(v, dict) and isinstance(v.get("id"), str)]}


def knowledge_advisories(contents, declarations):
    """Optional knowledge errors stay outside blocking identity findings."""
    issues, sources, references = [], {}, []
    for path, content in contents.items():
        meta = frontmatter(content) if content.startswith("---") else {}
        values = meta.get("reusable_findings", [])
        if not isinstance(values, list):
            issues.append(dict(code="knowledge_schema", path=path, reason="reusable_findings must be a list"))
            values = []
        counts = Counter(v.get("id") for v in values if isinstance(v, dict) and isinstance(v.get("id"), str))
        for value in values:
            errors = finding_errors(value)
            if meta.get("document_type") not in ("task", "investigation"):
                errors.append("Findings belong to TASK or INV")
            if isinstance(value, dict):
                ident = value.get("id")
                if isinstance(ident, str) and counts[ident] > 1:
                    errors.append("Duplicate finding ID")
                if not errors:
                    sources.setdefault(f'{meta.get("id")}#{ident}', []).append(path)
                if value.get("correction_of"):
                    references.append((path, value["correction_of"]))
            for error in errors:
                issues.append(dict(code="knowledge_schema", path=path, reason=error))
        refs = meta.get("knowledge_refs", [])
        if not isinstance(refs, list):
            issues.append(dict(code="knowledge_schema", path=path, reason="knowledge_refs must be a list"))
            continue
        for ref in refs:
            if not isinstance(ref, dict) or any(not isinstance(ref.get(k), str) or not ref[k].strip()
                                              for k in ("ref", "rationale", "checked_revision")):
                issues.append(dict(code="knowledge_schema", path=path, reason="Invalid knowledge reference"))
            else:
                references.append((path, ref["ref"]))
    for path, ref in references:
        if not isinstance(ref, str) or not re.fullmatch(REFERENCE, ref) or len(sources.get(ref, [])) != 1 or len(declarations.get(ref.split("#")[0], [])) != 1:
            issues.append(dict(code="knowledge_reference", path=path, reason="Missing, invalid or ambiguous finding", ref=ref))
    return issues


def dependency_check(root, dependency):
    result = {"verdict": "unknown"}
    if not isinstance(dependency, dict):
        return dict(result, reason="Dependency must be a mapping")
    if dependency.get("kind", "file") != "file":
        return dict(result, reason="Environment or unsupported input needs a current independent observation")
    name, expected = dependency.get("path"), dependency.get("sha256")
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        return dict(result, reason="Dependency must use a project-relative file path")
    if expected != "absent" and not (isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected)):
        return dict(result, path=name, reason="Missing or invalid expected hash/absence")
    try:
        path = within(root, name)
        # stat, unlike exists on newer Python, does not swallow permission failures.
        try:
            path.stat()
        except FileNotFoundError:
            actual = "absent"
        else:
            actual = digest(path.read_bytes())
        return dict(path=name, verdict="unchanged" if expected == actual else "changed",
                    expected=expected, actual=actual)
    except (ForgeError, OSError, ValueError):
        return dict(result, path=name, reason="Unsafe, unreadable or non-file dependency")


def knowledge_check(root, record_path, finding=None):
    from forge_records import canonical_files, metadata
    path = within(root, record_path)
    name = path.relative_to(Path(root).resolve()).as_posix()
    paths, discovery_errors = canonical_files(root)
    if name not in paths:
        raise ForgeError("knowledge-check requires a canonical TASK or INV record")
    meta = frontmatter(text(root, name))
    if meta.get("document_type") not in ("task", "investigation"):
        raise ForgeError("knowledge-check requires a TASK or INV")
    values = meta.get("reusable_findings", [])
    malformed = not isinstance(values, list)
    if malformed:
        values = []
    counts = Counter(v.get("id") for v in values if isinstance(v, dict) and isinstance(v.get("id"), str))
    selected = [v for v in values if finding is None or isinstance(v, dict) and v.get("id") == finding]
    if finding and not selected:
        raise ForgeError("Finding not found in selected record")
    # Find additive corrections in canonical records without rewriting their sources.
    corrections, source_count = {}, 0
    for candidate in paths:
        try:
            other = metadata(text(root, candidate))
            source_count += other.get("id") == meta.get("id")
            items = other.get("reusable_findings", [])
            for item in items if isinstance(items, list) else []:
                if isinstance(item, dict) and isinstance(item.get("correction_of"), str):
                    corrections.setdefault(item["correction_of"], []).append(candidate)
        except (ForgeError, OSError, UnicodeError):
            discovery_errors.append("Correction source unavailable")
    results = []
    for value in selected:
        errors = finding_errors(value)
        value = value if isinstance(value, dict) else {}
        ident = value.get("id")
        if isinstance(ident, str) and counts[ident] > 1:
            errors.append("Duplicate finding ID")
        if source_count != 1:
            errors.append("Ambiguous source identity")
        deps = value.get("dependencies", [])
        checks = [dependency_check(root, d) for d in deps] if isinstance(deps, list) else []
        if not checks:
            checks = [{"verdict": "unknown", "reason": "No declared dependencies"}]
        correction_paths = corrections.get(f'{meta.get("id")}#{ident}', [])
        if correction_paths:
            checks.append({"verdict": "unknown", "reason": "Additive correction requires review"})
        if discovery_errors:
            checks.append({"verdict": "unknown", "reason": "Correction discovery incomplete"})
        verdicts = {c["verdict"] for c in checks}
        verdict = "unknown" if errors else "changed" if "changed" in verdicts else "unknown" if "unknown" in verdicts else "unchanged"
        results.append(dict(id=ident, status=value.get("status"), claim=value.get("claim"),
                            applicability=value.get("applicability"), evidence_refs=value.get("evidence_refs"),
                            recheck_when=value.get("recheck_when"), verdict=verdict,
                            dependencies=checks, problems=errors, correction_paths=correction_paths,
                            requires_judgment=True, factual_reuse_candidate=not errors and verdict == "unchanged" and value.get("status") == "verified"))
    return {"source": name, "id": meta.get("id"), "findings": results,
            "advisory": ["Malformed reusable_findings"] if malformed else [],
            "requires_judgment": "Declared input freshness is not truth, complete dependency coverage, or lifecycle evidence"}
