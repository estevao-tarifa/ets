import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def upsert_embedding(session: AsyncSession, node_id: int, vector: list[float]) -> None:
    """Insert or replace a 384-dim embedding in node_embeddings virtual table."""
    vec_json = json.dumps(vector)
    await session.execute(
        text("INSERT OR REPLACE INTO node_embeddings(node_id, embedding) VALUES(:node_id, :vec)"),
        {"node_id": node_id, "vec": vec_json},
    )
    await session.commit()

async def knn_search(
    session: AsyncSession, vector: list[float], k: int = 10
) -> list[tuple[int, float]]:
    """
    Return top-k (node_id, distance) pairs via sqlite-vec KNN.
    Lower distance = more similar.
    """
    vec_json = json.dumps(vector)
    result = await session.execute(
        text(
            "SELECT node_id, distance FROM node_embeddings "
            "WHERE embedding MATCH :vec AND k = :k "
            "ORDER BY distance"
        ),
        {"vec": vec_json, "k": k},
    )
    return [(row.node_id, row.distance) for row in result]
