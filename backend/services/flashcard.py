import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.domain.rules import sm2_update
from backend.infrastructure.llm import call_llm

logger = logging.getLogger(__name__)

async def generate_flashcard(
    session: AsyncSession, node_id: int, provider: str, api_key: str, model: str
) -> int:
    node_r = await session.execute(
        text("SELECT nome, descricao FROM knowledge_nodes WHERE id=:nid"), {"nid": node_id}
    )
    node = node_r.fetchone()
    if not node:
        raise ValueError(f"Node {node_id} not found")
    prompt = (
        f"Crie um flashcard de estudo para o conceito '{node.nome}'.\n"
        f"Descrição: {node.descricao or 'N/A'}\n"
        "Responda em JSON: {\"frente\": \"pergunta\", \"verso\": \"resposta\"}"
    )
    raw = await call_llm(prompt, provider, api_key, model, max_tokens=256, json_mode=True)
    import json
    data = json.loads(raw)
    r = await session.execute(
        text("INSERT INTO flashcards(node_id, frente, verso) VALUES(:nid,:f,:v) RETURNING id"),
        {"nid": node_id, "f": data["frente"], "v": data["verso"]},
    )
    await session.commit()
    return r.fetchone()[0]

async def review_flashcard(session: AsyncSession, flashcard_id: int, quality: int) -> dict:
    """quality 0-5. Updates SM-2 fields. Returns updated flashcard data."""
    r = await session.execute(
        text("SELECT ease_factor, interval_days FROM flashcards WHERE id=:fid"), {"fid": flashcard_id}
    )
    row = r.fetchone()
    if not row:
        raise ValueError(f"Flashcard {flashcard_id} not found")
    new_ef, new_interval = sm2_update(row.ease_factor, row.interval_days, quality)
    next_review = datetime.utcnow() + timedelta(days=new_interval)
    acerto_delta = 1 if quality >= 3 else 0
    erro_delta = 0 if quality >= 3 else 1
    await session.execute(
        text(
            "UPDATE flashcards SET ease_factor=:ef, interval_days=:iv, next_review=:nr, "
            "acertos=acertos+:ac, erros=erros+:er WHERE id=:fid"
        ),
        {"ef": new_ef, "iv": new_interval, "nr": next_review.isoformat(), "ac": acerto_delta, "er": erro_delta, "fid": flashcard_id},
    )
    await session.commit()
    return {"flashcard_id": flashcard_id, "ease_factor": new_ef, "interval_days": new_interval, "next_review": next_review.isoformat()}

async def get_due(session: AsyncSession) -> list[dict]:
    now = datetime.utcnow().isoformat()
    r = await session.execute(
        text("SELECT id, node_id, frente, verso, next_review FROM flashcards WHERE next_review <= :now ORDER BY next_review"),
        {"now": now},
    )
    return [dict(row._mapping) for row in r]
