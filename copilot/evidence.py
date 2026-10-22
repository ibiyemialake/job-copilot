"""Load the evidence bank: the only source of truth about your experience."""
from pathlib import Path

import yaml

EVIDENCE_FILE = Path(__file__).parent.parent / "data" / "evidence.yaml"


def load_evidence(path: Path = EVIDENCE_FILE) -> dict[str, dict]:
    items = yaml.safe_load(path.read_text(encoding="utf-8"))
    bank = {}
    for item in items:
        if item["id"] in bank:
            raise ValueError(f"Duplicate evidence id: {item['id']}")
        bank[item["id"]] = item
    return bank


def as_text(item: dict) -> str:
    return f"[{item['id']}] ({item['role']}) {item['text']}"
