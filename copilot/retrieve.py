"""RAG layer: find the evidence items most relevant to a job requirement."""
import chromadb

from .evidence import load_evidence

_client = chromadb.Client()  # in-memory; fine for a few hundred items


def build_index(bank: dict[str, dict] | None = None):
    bank = bank or load_evidence()
    try:
        _client.delete_collection("evidence")
    except Exception:
        pass
    col = _client.create_collection("evidence", metadata={"hnsw:space": "cosine"})
    col.add(
        ids=list(bank.keys()),
        documents=[f"{v['role']}. {v['text']}" for v in bank.values()],
    )
    return col


def search(col, query: str, k: int = 3, max_distance: float = 0.75) -> list[tuple[str, float]]:
    """Return (evidence_id, distance) pairs. Weak matches are dropped so the
    drafter sees 'no evidence' instead of a loosely related item."""
    res = col.query(query_texts=[query], n_results=k)
    pairs = zip(res["ids"][0], res["distances"][0])
    return [(i, round(d, 3)) for i, d in pairs if d <= max_distance]
