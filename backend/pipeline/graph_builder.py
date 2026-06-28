import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def build_graph(
    session: AsyncSession,
    materia_id: int,
    material_id: int,
    concepts: list[dict],
) -> list[int]:
    """
    Insert nodes and dependencies into DB + link material_nodes.
    concepts: list of dicts with 'node_id', 'nome', 'relacoes' (list of related concept names), 'nivel'.
    Returns list of node_ids that need embeddings.
    """
    # Build nome→node_id map for relation linking
    nome_to_id: dict[str, int] = {}
    for c in concepts:
        nome_to_id[c["nome"]] = c["node_id"]
        # Link material → node
        await session.execute(
            text("INSERT OR IGNORE INTO material_nodes(material_id, node_id, relevancia) VALUES(:mid,:nid,1.0)"),
            {"mid": material_id, "nid": c["node_id"]},
        )

    # Add dependencies (relations)
    for c in concepts:
        from_id = c["node_id"]
        for rel_nome in c.get("relacoes", []):
            to_id = nome_to_id.get(rel_nome)
            if to_id and to_id != from_id:
                await session.execute(
                    text("INSERT OR IGNORE INTO dependencies(from_node_id, to_node_id, tipo) VALUES(:f,:t,'hierarquica')"),
                    {"f": from_id, "t": to_id},
                )

    await session.commit()
    node_ids = [c["node_id"] for c in concepts]
    logger.info(f"Graph built: {len(node_ids)} nodes, material {material_id}")
    return node_ids
