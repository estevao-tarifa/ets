import logging
from backend.infrastructure.local_embeddings import encode_one
from backend.infrastructure.vector_store import knn_search
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# ponytail: CrossEncoder loaded lazily, only when dedup runs (not on startup)
_cross_encoder = None

def _get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        from sentence_transformers.cross_encoder import CrossEncoder
        _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _cross_encoder

async def find_candidates(session: AsyncSession, text: str, k: int = 20) -> list[tuple[int, float]]:
    """KNN search: return (node_id, distance) pairs."""
    vec = encode_one(text)
    return await knn_search(session, vec, k=k)

def score_pairs(query: str, candidates: list[tuple[int, str]]) -> list[tuple[int, float]]:
    """
    Re-rank candidates with CrossEncoder.
    candidates: list of (node_id, node_nome)
    Returns list of (node_id, score) sorted desc.
    """
    if not candidates:
        return []
    ce = _get_cross_encoder()
    pairs = [[query, nome] for _, nome in candidates]
    scores = ce.predict(pairs)
    result = [(candidates[i][0], float(scores[i])) for i in range(len(candidates))]
    return sorted(result, key=lambda x: x[1], reverse=True)

def classify(score: float) -> str:
    """
    > 0.95 → auto_merge
    0.75 <= score <= 0.95 → review_queue
    < 0.75 → new_node
    """
    if score > 0.95:
        return "auto_merge"
    if score >= 0.75:
        return "review_queue"
    return "new_node"
