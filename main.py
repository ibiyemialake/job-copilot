"""Usage:
    python main.py data/postings/sample_data_manager.txt
Writes outputs/<posting-name>.md and .json
"""
import json
import sys
from pathlib import Path

from copilot.tailor import tailor
from copilot.verify import verify

ICON = {"supported": "✅", "partial": "⚠️", "unsupported": "❌"}


def to_markdown(name: str, draft: dict, report: dict) -> str:
    lines = [f"# {name}", "", f"**Honesty score:** {report['honesty_score']}  ",
             f"{report['counts']}", "", "## Summary", draft["summary"], "", "## Bullets"]
    for c in report["claims"][1:]:
        lines.append(f"- {ICON[c['verdict']]} {c['claim']}  `{', '.join(c['evidence'])}`")
        if c.get("problem"):
            lines.append(f"  - _{c['problem']}_")
    lines += ["", "## Gaps (be honest about these)"]
    lines += [f"- **{g['requirement']}** — {g['note']}" for g in draft["gaps"]] or ["- none found"]
    return "\n".join(lines)


def main(path: str):
    posting = Path(path).read_text(encoding="utf-8")
    draft = tailor(posting)
    report = verify(draft)

    name = Path(path).stem
    out = Path("outputs")
    out.mkdir(exist_ok=True)
    (out / f"{name}.json").write_text(json.dumps({"draft": draft, "report": report}, indent=2))
    md = to_markdown(name, draft, report)
    (out / f"{name}.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main(sys.argv[1])
