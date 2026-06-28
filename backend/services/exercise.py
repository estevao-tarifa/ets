import json, logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.llm import call_llm

logger = logging.getLogger(__name__)

async def generate_exercise(session: AsyncSession, node_id: int, provider: str, api_key: str, model: str) -> dict:
    node_r = await session.execute(text("SELECT nome, descricao FROM knowledge_nodes WHERE id=:nid"), {"nid": node_id})
    node = node_r.fetchone()
    if not node:
        raise ValueError(f"Node {node_id} not found")
    prompt = (
        f"Crie um exercício de múltipla escolha sobre '{node.nome}'.\n"
        f"Descrição: {node.descricao or 'N/A'}\n"
        'Responda JSON: {"enunciado":"...","alternativas":["A)...","B)...","C)...","D)..."],"gabarito":"A"}'
    )
    raw = await call_llm(prompt, provider, api_key, model, max_tokens=512, json_mode=True)
    return json.loads(raw)
