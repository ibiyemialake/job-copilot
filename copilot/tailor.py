"""Read a posting, retrieve evidence per requirement, draft cited content."""
import json

from .evidence import as_text, load_evidence
from .llm import ask_json
from .retrieve import build_index, search

EXTRACT_SYSTEM = """You read job postings. Extract the distinct requirements a hiring
manager would screen on (skills, tools, years, team size, domain, credentials).
Return a JSON list of short strings, most important first, at most 12."""

DRAFT_SYSTEM = """You tailor a CV to a job posting using ONLY the evidence provided.
Rules:
- Every bullet must cite the evidence ids it relies on, e.g. ["CA-01","MP-02"].
- Never add tools, numbers, years, titles or outcomes that are not in the cited evidence.
- Rephrasing is fine; inventing is not. If evidence is weak, say less.
- Any requirement with no supporting evidence goes in "gaps", stated plainly.
Return JSON: {"summary": str, "summary_evidence": [ids],
              "bullets": [{"text": str, "evidence": [ids]}],
              "gaps": [{"requirement": str, "note": str}]}"""


def tailor(posting: str) -> dict:
    bank = load_evidence()
    col = build_index(bank)

    requirements = ask_json(EXTRACT_SYSTEM, posting)

    matches = {}
    for req in requirements:
        matches[req] = [{"id": i, "distance": d} for i, d in search(col, req)]

    used_ids = {m["id"] for ms in matches.values() for m in ms}
    evidence_block = "\n".join(as_text(bank[i]) for i in sorted(used_ids))
    req_block = json.dumps(matches, indent=2)

    draft = ask_json(
        DRAFT_SYSTEM,
        f"JOB POSTING:\n{posting}\n\nREQUIREMENTS AND RETRIEVED EVIDENCE IDS:\n{req_block}"
        f"\n\nEVIDENCE:\n{evidence_block or '(none retrieved)'}",
        max_tokens=3000,
    )
    draft["requirements"] = matches
    return draft
