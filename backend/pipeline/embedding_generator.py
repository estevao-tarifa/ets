import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.local_embeddings import encode
from backend.infrastructure.vector_store import upsert_embedding

logger = logging.getLogger(__name__)

async def generate_embeddings(session: AsyncSession, node_ids: list[int]) -> None:
    """
    Generate local embeddings for all nodes and upsert into sqlite-vec.
    Uses node nome + descricao as the text to embed.
    """
    if not node_ids:
        return

    # Fetch node texts
    placeholders = ",".join(str(i) for i in node_ids)
    r = await session.execute(
        text(f"SELECT id, nome, descricao FROM knowledge_nodes WHERE id IN ({placeholders})")
    )
    nodes = list(r)
    if not nodes:
        return

    texts = [f"{n.nome}: {n.descricao or ''}" for n in nodes]
    vectors = encode(texts)  # list of 384-dim float lists

    for node, vec in zip(nodes, vectors):
        await upsert_embedding(session, node.id, vec)

    logger.info(f"Embeddings generated for {len(nodes)} nodes")
