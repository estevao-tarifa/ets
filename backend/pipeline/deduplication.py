import logging
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.dedup import find_candidates, score_pairs, classify
from backend.services.graph import add_node, merge_nodes
from backend.infrastructure.local_embeddings import encode_one

logger = logging.getLogger(__name__)

async def dedup_concepts(
    session: AsyncSession, concepts: list[dict], materia_id: int
) -> list[dict]:
    """
    For each concept:
    1. KNN search for similar existing nodes
    2. CrossEncoder scoring
    3. auto_merge (>0.95), review_queue (0.75-0.95), new_node (<0.75)
    Returns final list of dicts with 'node_id' set.
    """
    from sqlalchemy import text

    result = []
    for concept in concepts:
        nome = concept["nome"]
        vec = encode_one(nome)

        # Get existing nodes in this materia for candidate names
        from sqlalchemy import text as sql_text
        candidates_r = await session.execute(
            sql_text("SELECT id, nome FROM knowledge_nodes WHERE materia_id=:mid"),
            {"mid": materia_id},
        )
        existing = [(r.id, r.nome) for r in candidates_r]

        if not existing:
            # First concept — no dedup needed
            node_id = await add_node(session, materia_id, nome, concept.get("nivel", "conceito"), concept.get("descricao"))
            result.append({**concept, "node_id": node_id, "action": "new_node"})
            continue

        # Score against existing
        scored = score_pairs(nome, existing)
        if not scored:
            node_id = await add_node(session, materia_id, nome, concept.get("nivel", "conceito"), concept.get("descricao"))
            result.append({**concept, "node_id": node_id, "action": "new_node"})
            continue

        top_id, top_score = scored[0]
        action = classify(top_score)

        if action == "auto_merge":
            logger.info(f"Auto-merge '{nome}' → node {top_id} (score={top_score:.3f})")
            result.append({**concept, "node_id": top_id, "action": "auto_merge"})
        elif action == "review_queue":
            # ponytail: for MVP, treat review_queue as new_node; manual review UI is Phase FE
            node_id = await add_node(session, materia_id, nome, concept.get("nivel", "conceito"), concept.get("descricao"))
            logger.info(f"Review queue '{nome}' (score={top_score:.3f}) → created node {node_id}")
            result.append({**concept, "node_id": node_id, "action": "review_queue"})
        else:
            node_id = await add_node(session, materia_id, nome, concept.get("nivel", "conceito"), concept.get("descricao"))
            result.append({**concept, "node_id": node_id, "action": "new_node"})

    return result
