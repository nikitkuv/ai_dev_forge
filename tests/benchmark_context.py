"""Reproducible synthetic context-size comparison, not a billed-token benchmark."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".ai/tools"))
from forge_core import canonical, inventory


def benchmark():
    with tempfile.TemporaryDirectory(prefix="forge-context-benchmark-") as temporary:
        root = Path(temporary)
        body = "Acceptance criterion and implementation evidence.\n" * 200
        total = 0
        for number in range(1, 101):
            path = root / f"execution/planned/EPIC-001-example/tasks/TASK-{number:03d}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            content = f"---\ndocument_type: task\nid: TASK-{number:03d}\nepic_id: EPIC-001\nstatus: TODO\ndefinition_status: approved\ndelivery_track: standard\n---\n## Plan\n{body}"
            path.write_text(content, encoding="utf-8")
            total += len(content.encode())
        records, errors = inventory(root)
        if errors or len(records) != 100:
            raise RuntimeError(errors)
        compact = len(canonical(records).encode())
        # Illustrative follow-up: load three relevant complete Task files too.
        selected = sum(p.stat().st_size for p in sorted(root.rglob("TASK-*.md"))[:3])
        return {"tasks": len(records), "all_bodies_bytes": total, "metadata_bytes": compact,
                "metadata_plus_three_tasks_bytes": compact + selected,
                "reduction_percent": round(100 * (1 - (compact + selected) / total), 2),
                "scope": "synthetic queued-task context only; no claim about total model usage or quality"}


if __name__ == "__main__":
    print(json.dumps(benchmark(), ensure_ascii=False))
