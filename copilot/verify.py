"""The honesty check: is every claim in the draft backed by real evidence?"""
import re

from .evidence import load_evidence
from .llm import ask_json

JUDGE_SYSTEM = """You audit CV claims. Given a CLAIM and the EVIDENCE it cites, decide:
- "supported": everything in the claim is stated or directly implied by the evidence
- "partial": the core is supported but something is stretched or added
- "unsupported": a key part (tool, number, scope, outcome, title) is not in the evidence
Return JSON: {"verdict": "...", "problem": "what was added or stretched, or empty"}"""

NUM = re.compile(r"\d+(?:\.\d+)?")


def numbers_ok(claim: str, evidence_text: str) -> list[str]:
    """Cheap deterministic check: every number in the claim must appear in the
    evidence. Returns the numbers that don't."""
    found = set(NUM.findall(evidence_text))
    return [n for n in NUM.findall(claim) if n not in found]


def check_claim(text: str, ids: list[str], bank: dict) -> dict:
    missing_ids = [i for i in ids if i not in bank]
    ev = "\n".join(bank[i]["text"] for i in ids if i in bank)

    result = {"claim": text, "evidence": ids, "missing_ids": missing_ids,
              "unbacked_numbers": numbers_ok(text, ev) if ev else []}

    if not ev:
        result.update(verdict="unsupported", problem="cites no valid evidence")
        return result

    judged = ask_json(JUDGE_SYSTEM, f"CLAIM: {text}\n\nEVIDENCE:\n{ev}", max_tokens=1000)
    result.update(judged)
    # A made-up number overrides a lenient judge.
    if result["unbacked_numbers"] and result["verdict"] == "supported":
        result.update(verdict="partial",
                      problem=f"numbers not in evidence: {result['unbacked_numbers']}")
    return result


def verify(draft: dict) -> dict:
    bank = load_evidence()
    claims = [(draft["summary"], draft.get("summary_evidence", []))]
    claims += [(b["text"], b["evidence"]) for b in draft["bullets"]]
    results = [check_claim(t, ids, bank) for t, ids in claims]

    counts = {v: sum(r["verdict"] == v for r in results)
              for v in ("supported", "partial", "unsupported")}
    return {"claims": results, "counts": counts,
            "honesty_score": round(counts["supported"] / len(results), 2)}
