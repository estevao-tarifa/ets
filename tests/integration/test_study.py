import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.services.study import add_event, close_session, create_session, get_dominio


@pytest.fixture
async def engine():
    e = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with e.begin() as conn:
        await conn.execute(sa.text(
            "CREATE TABLE materias (id INTEGER PRIMARY KEY, nome TEXT NOT NULL UNIQUE, "
            "descricao TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        ))
        await conn.execute(sa.text(
            "CREATE TABLE knowledge_nodes (id INTEGER PRIMARY KEY, materia_id INTEGER NOT NULL, "
            "nome TEXT NOT NULL, descricao TEXT, nivel TEXT NOT NULL, "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        ))
        await conn.execute(sa.text(
            "CREATE TABLE study_sessions (id INTEGER PRIMARY KEY, materia_id INTEGER NOT NULL, "
            "iniciada_em DATETIME DEFAULT CURRENT_TIMESTAMP, finalizada_em DATETIME, "
            "autoavaliacao INTEGER, pendente TEXT, status TEXT DEFAULT 'ativa')"
        ))
        await conn.execute(sa.text(
            "CREATE TABLE session_events (id INTEGER PRIMARY KEY, session_id INTEGER NOT NULL, "
            "node_id INTEGER, tipo TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        ))
        await conn.execute(sa.text(
            "CREATE TABLE evidencias (id INTEGER PRIMARY KEY, node_id INTEGER NOT NULL, "
            "session_id INTEGER, tipo TEXT NOT NULL, resultado REAL NOT NULL, "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        ))
        await conn.execute(sa.text("INSERT INTO materias (nome) VALUES ('Direito Civil')"))
        await conn.execute(sa.text(
            "INSERT INTO knowledge_nodes (materia_id, nome, nivel) VALUES (1, 'Contratos', 'basico')"
        ))
    yield e
    await e.dispose()


@pytest.fixture
async def db(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.mark.asyncio
async def test_full_session_flow(db):
    session_id = await create_session(db, materia_id=1)
    assert session_id is not None

    e1 = await add_event(db, session_id, "acerto", node_id=1)
    e2 = await add_event(db, session_id, "erro", node_id=1)
    e3 = await add_event(db, session_id, "duvida", node_id=1)
    assert len({e1, e2, e3}) == 3  # all distinct ids

    await close_session(db, session_id, autoavaliacao=4)

    row = (await db.execute(
        sa.text("SELECT status, autoavaliacao FROM study_sessions WHERE id=:sid"),
        {"sid": session_id},
    )).fetchone()
    assert row.status == "finalizada"
    assert row.autoavaliacao == 4


@pytest.mark.asyncio
async def test_evidencias_append_only(db):
    session_id = await create_session(db, materia_id=1)

    await add_event(db, session_id, "acerto", node_id=1)
    count1 = (await db.execute(sa.text("SELECT COUNT(*) FROM evidencias"))).scalar()
    assert count1 == 1

    await add_event(db, session_id, "acerto", node_id=1)
    count2 = (await db.execute(sa.text("SELECT COUNT(*) FROM evidencias"))).scalar()
    assert count2 == 2  # appended, not updated

    # Both original rows are intact with their original values
    rows = (await db.execute(sa.text("SELECT resultado FROM evidencias ORDER BY id"))).fetchall()
    assert rows[0][0] == 1.0
    assert rows[1][0] == 1.0


@pytest.mark.asyncio
async def test_close_requires_valid_autoavaliacao(db):
    session_id = await create_session(db, materia_id=1)

    with pytest.raises(ValueError):
        await close_session(db, session_id, autoavaliacao=0)
    with pytest.raises(ValueError):
        await close_session(db, session_id, autoavaliacao=6)


@pytest.mark.asyncio
async def test_dominio_score_changes_after_acerto(db):
    session_id = await create_session(db, materia_id=1)

    before = await get_dominio(db, node_id=1)
    assert before is None  # no evidence yet

    await add_event(db, session_id, "acerto", node_id=1)
    after = await get_dominio(db, node_id=1)
    assert after is not None
    assert after > 0.0
