import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.domain.rules import calculate_dominio_score
from backend.infrastructure.llm import call_llm

logger = logging.getLogger(__name__)

async def get_diagnostic(session: AsyncSession, materia_id: int) -> list[dict]:
    """Return nodes ranked by risk score (low dominio = high risk)."""
    nodes_r = await session.execute(
        text("SELECT id, nome FROM knowledge_nodes WHERE materia_id=:mid"), {"mid": materia_id}
    )
    nodes = list(nodes_r)
    result = []
    for node in nodes:
        evid_r = await session.execute(
            text("SELECT resultado FROM evidencias WHERE node_id=:nid ORDER BY created_at"), {"nid": node.id}
        )
        dominio = calculate_dominio_score([float(r[0]) for r in evid_r])
        risco = 1.0 - (dominio or 0.0)
        result.append({"node_id": node.id, "nome": node.nome, "dominio": dominio, "risco_score": risco})
    return sorted(result, key=lambda x: x["risco_score"], reverse=True)

async def generate_revision_plan(session: AsyncSession, materia_id: int, provider: str, api_key: str, model: str, days_until_exam: int) -> str:
    diagnostic = await get_diagnostic(session, materia_id)
    top_nodes = [f"{d['nome']} (domínio={d['dominio']:.0%})" for d in diagnostic[:10]]
    prompt = (
        f"Crie um plano de revisão para os próximos {days_until_exam} dias cobrindo os tópicos mais críticos:\n"
        + "\n".join(f"- {n}" for n in top_nodes)
        + "\nFormate como cronograma dia a dia em português."
    )
    return await call_llm(prompt, provider, api_key, model, max_tokens=1024)
