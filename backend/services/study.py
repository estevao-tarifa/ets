import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.domain.rules import calculate_dominio_score, calculate_node_color

logger = logging.getLogger(__name__)

async def create_session(session: AsyncSession, materia_id: int) -> int:
    r = await session.execute(
        text("INSERT INTO study_sessions(materia_id, status) VALUES(:mid,'ativa') RETURNING id"),
        {"mid": materia_id},
    )
    await session.commit()
    return r.fetchone()[0]

async def add_event(session: AsyncSession, session_id: int, tipo: str, node_id: int | None = None) -> int:
    """Record event (acerto/erro/duvida). Returns event id."""
    r = await session.execute(
        text("INSERT INTO session_events(session_id, node_id, tipo) VALUES(:sid,:nid,:tipo) RETURNING id"),
        {"sid": session_id, "nid": node_id, "tipo": tipo},
    )
    # If node_id given and tipo in (acerto, erro): append evidencia
    if node_id and tipo in ("acerto", "erro"):
        resultado = 1.0 if tipo == "acerto" else 0.0
        await session.execute(
            text("INSERT INTO evidencias(node_id, session_id, tipo, resultado) VALUES(:nid,:sid,'revisao',:res)"),
            {"nid": node_id, "sid": session_id, "res": resultado},
        )
    await session.commit()
    return r.fetchone()[0]

async def close_session(
    session: AsyncSession, session_id: int, autoavaliacao: int, pendente: str | None = None
) -> None:
    """Close session. autoavaliacao 1-5 is required."""
    if not (1 <= autoavaliacao <= 5):
        raise ValueError("autoavaliacao must be 1-5")
    await session.execute(
        text(
            "UPDATE study_sessions SET status='finalizada', finalizada_em=:now, "
            "autoavaliacao=:av, pendente=:pend WHERE id=:sid"
        ),
        {"now": datetime.utcnow().isoformat(), "av": autoavaliacao, "pend": pendente, "sid": session_id},
    )
    await session.commit()

async def get_dominio(session: AsyncSession, node_id: int) -> float | None:
    r = await session.execute(
        text("SELECT resultado FROM evidencias WHERE node_id=:nid ORDER BY created_at"),
        {"nid": node_id},
    )
    return calculate_dominio_score([float(row[0]) for row in r])
