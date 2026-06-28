import logging
from dataclasses import dataclass
import networkx as nx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.domain.enums import NodeColor, RelationType
from backend.domain.rules import calculate_node_color, calculate_dominio_score

logger = logging.getLogger(__name__)

# ponytail: in-memory graph per-materia, rebuilt on demand. Fine for <500 nodes MVP.
_graphs: dict[int, nx.DiGraph] = {}

async def get_graph_data(session: AsyncSession, materia_id: int) -> dict:
    """Return nodes + edges with dominio_score and color for frontend."""
    nodes_r = await session.execute(
        text("SELECT id, nome, nivel, descricao FROM knowledge_nodes WHERE materia_id=:mid"),
        {"mid": materia_id},
    )
    edges_r = await session.execute(
        text("SELECT from_node_id, to_node_id, tipo FROM dependencies d "
             "JOIN knowledge_nodes n ON n.id=d.from_node_id WHERE n.materia_id=:mid"),
        {"mid": materia_id},
    )
    nodes = [dict(r._mapping) for r in nodes_r]
    edges = [dict(r._mapping) for r in edges_r]

    # Build in-memory graph to detect nodes with dependents
    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n["id"])
    for e in edges:
        G.add_edge(e["from_node_id"], e["to_node_id"])

    # Compute dominio + color per node
    for node in nodes:
        evid_r = await session.execute(
            text("SELECT resultado FROM evidencias WHERE node_id=:nid ORDER BY created_at"),
            {"nid": node["id"]},
        )
        resultados = [float(r[0]) for r in evid_r]
        dominio = calculate_dominio_score(resultados)
        tem_deps = G.out_degree(node["id"]) > 0
        node["dominio_score"] = dominio
        node["color"] = calculate_node_color(dominio, tem_deps).value

    return {"nodes": nodes, "edges": edges}

async def get_node(session: AsyncSession, node_id: int) -> dict | None:
    r = await session.execute(
        text("SELECT id, materia_id, nome, nivel, descricao FROM knowledge_nodes WHERE id=:nid"),
        {"nid": node_id},
    )
    row = r.fetchone()
    return dict(row._mapping) if row else None

async def add_node(session: AsyncSession, materia_id: int, nome: str, nivel: str, descricao: str | None = None) -> int:
    r = await session.execute(
        text("INSERT INTO knowledge_nodes(materia_id, nome, nivel, descricao) VALUES(:mid,:nome,:nivel,:desc) RETURNING id"),
        {"mid": materia_id, "nome": nome, "nivel": nivel, "desc": descricao},
    )
    await session.commit()
    return r.fetchone()[0]

async def add_dependency(session: AsyncSession, from_id: int, to_id: int, tipo: str = "hierarquica") -> None:
    if from_id == to_id:
        raise ValueError("Self-loops prohibited")
    await session.execute(
        text("INSERT OR IGNORE INTO dependencies(from_node_id, to_node_id, tipo) VALUES(:f,:t,:tipo)"),
        {"f": from_id, "t": to_id, "tipo": tipo},
    )
    await session.commit()

async def merge_nodes(session: AsyncSession, keep_id: int, discard_id: int) -> None:
    """Merge discard into keep: reassign evidencias, dependencies, flashcards, then delete discard."""
    for tbl in ("evidencias", "session_events", "flashcards", "material_nodes"):
        await session.execute(text(f"UPDATE {tbl} SET node_id=:keep WHERE node_id=:disc"), {"keep": keep_id, "disc": discard_id})
    await session.execute(
        text("UPDATE dependencies SET from_node_id=:keep WHERE from_node_id=:disc AND to_node_id!=:keep"),
        {"keep": keep_id, "disc": discard_id},
    )
    await session.execute(
        text("UPDATE dependencies SET to_node_id=:keep WHERE to_node_id=:disc AND from_node_id!=:keep"),
        {"keep": keep_id, "disc": discard_id},
    )
    await session.execute(text("DELETE FROM knowledge_nodes WHERE id=:disc"), {"disc": discard_id})
    await session.commit()
