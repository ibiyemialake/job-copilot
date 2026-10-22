"""Run the copilot over every test posting and score it.

Metrics:
  honesty      share of claims the judge marks fully supported (higher = better)
  gap_recall   share of known gaps the tool admitted (higher = better)
  violations   forbidden claims that slipped into the draft (should be 0)

Usage:  python -m evals.run_evals
"""
from pathlib import Path

import yaml

from copilot.tailor import tailor
from copilot.verify import verify

cases = yaml.safe_load(Path("evals/cases.yaml").read_text())
rows = []

for case in cases:
    posting = Path(case["posting"]).read_text(encoding="utf-8")
    draft = tailor(posting)
    report = verify(draft)

    gap_text = " ".join(g["requirement"] + " " + g["note"] for g in draft["gaps"]).lower()
    claimed = " ".join([draft["summary"]] + [b["text"] for b in draft["bullets"]]).lower()

    expected = case.get("expected_gaps", [])
    hits = sum(g.lower() in gap_text for g in expected)
    violations = [c for c in case.get("must_not_claim", []) if c.lower() in claimed]

    rows.append({
        "posting": Path(case["posting"]).stem,
        "honesty": report["honesty_score"],
        "gap_recall": round(hits / len(expected), 2) if expected else None,
        "violations": violations,
    })

print(f"{'posting':40} {'honesty':>8} {'gap_recall':>11}  violations")
for r in rows:
    print(f"{r['posting']:40} {r['honesty']:>8} {str(r['gap_recall']):>11}  {r['violations'] or '-'}")

n = len(rows)
print("\nAVERAGE honesty:", round(sum(r["honesty"] for r in rows) / n, 2))
recalls = [r["gap_recall"] for r in rows if r["gap_recall"] is not None]
if recalls:
    print("AVERAGE gap recall:", round(sum(recalls) / len(recalls), 2))
print("TOTAL violations:", sum(len(r["violations"]) for r in rows))
