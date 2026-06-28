from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


async def seed_db(session: AsyncSession) -> dict:
    now = datetime.utcnow()

    # materias
    result = await session.execute(
        sa.text("INSERT INTO materias (nome) VALUES (:n) RETURNING id"),
        {"n": "Cálculo I"},
    )
    calculo_id = result.scalar_one()

    r2 = await session.execute(
        sa.text("INSERT INTO materias (nome) VALUES (:n) RETURNING id"),
        {"n": "Álgebra Linear"},
    )
    algebra_id = r2.scalar_one()

    r3 = await session.execute(
        sa.text("INSERT INTO materias (nome) VALUES (:n) RETURNING id"),
        {"n": "Física I"},
    )
    fisica_id = r3.scalar_one()

    # knowledge_nodes under Cálculo I
    nodes_data = [
        ("Limite", "conceito"),
        ("Continuidade", "conceito"),
        ("Derivada", "topico"),
        ("Regra da Cadeia", "subtopico"),
        ("Integral Definida", "topico"),
        ("Integral Indefinida", "subtopico"),
        ("Teorema Fundamental do Cálculo", "topico"),
        ("Séries de Taylor", "area"),
        ("Cálculo Diferencial", "area"),
        ("Máximos e Mínimos", "subtopico"),
    ]
    node_ids = []
    for nome, nivel in nodes_data:
        r = await session.execute(
            sa.text(
                "INSERT INTO knowledge_nodes (materia_id, nome, nivel)"
                " VALUES (:m, :n, :l) RETURNING id"
            ),
            {"m": calculo_id, "n": nome, "l": nivel},
        )
        node_ids.append(r.scalar_one())

    # study_sessions for Cálculo I
    session_ids = []
    for _ in range(2):
        r = await session.execute(
            sa.text(
                "INSERT INTO study_sessions (materia_id, status)"
                " VALUES (:m, 'finalizada') RETURNING id"
            ),
            {"m": calculo_id},
        )
        session_ids.append(r.scalar_one())

    # evidencias: cycle through resultado values across nodes
    resultados = [0.2, 0.5, 0.7, 0.9]
    evidencia_ids = []
    for i, node_id in enumerate(node_ids):
        r = await session.execute(
            sa.text(
                "INSERT INTO evidencias (node_id, session_id, tipo, resultado)"
                " VALUES (:n, :s, 'quiz', :res) RETURNING id"
            ),
            {
                "n": node_id,
                "s": session_ids[i % len(session_ids)],
                "res": resultados[i % len(resultados)],
            },
        )
        evidencia_ids.append(r.scalar_one())

    await session.commit()

    return {
        "materia_ids": {"calculo": calculo_id, "algebra": algebra_id, "fisica": fisica_id},
        "node_ids": node_ids,
        "session_ids": session_ids,
        "evidencia_ids": evidencia_ids,
    }
