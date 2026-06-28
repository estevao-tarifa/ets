import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.services.flashcard import generate_flashcard, get_due, review_flashcard


@pytest.fixture
async def engine():
    e = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with e.begin() as conn:
        await conn.execute(sa.text(
            "CREATE TABLE materias (id INTEGER PRIMARY KEY, nome TEXT NOT NULL UNIQUE)"
        ))
        await conn.execute(sa.text(
            "CREATE TABLE knowledge_nodes (id INTEGER PRIMARY KEY, materia_id INTEGER NOT NULL, "
            "nome TEXT NOT NULL, descricao TEXT, nivel TEXT NOT NULL)"
        ))
        await conn.execute(sa.text(
            "CREATE TABLE flashcards (id INTEGER PRIMARY KEY, node_id INTEGER NOT NULL, "
            "frente TEXT NOT NULL, verso TEXT NOT NULL, ease_factor REAL DEFAULT 2.5, "
            "interval_days INTEGER DEFAULT 1, next_review DATETIME DEFAULT CURRENT_TIMESTAMP, "
            "acertos INTEGER DEFAULT 0, erros INTEGER DEFAULT 0, "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        ))
        await conn.execute(sa.text("INSERT INTO materias (nome) VALUES ('Matemática')"))
        await conn.execute(sa.text(
            "INSERT INTO knowledge_nodes (materia_id, nome, nivel) VALUES (1, 'Derivada', 'intermediario')"
        ))
    yield e
    await e.dispose()


@pytest.fixture
async def db(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.mark.asyncio
async def test_generate_flashcard_mocked_llm(db):
    mock_json = json.dumps({"frente": "Q", "verso": "A"})
    with patch("backend.infrastructure.llm.litellm.acompletion", new_callable=AsyncMock) as m:
        m.return_value.choices[0].message.content = mock_json
        fc_id = await generate_flashcard(db, node_id=1, provider="groq", api_key="key", model="llama3")

    assert fc_id is not None
    row = (await db.execute(
        sa.text("SELECT frente, verso FROM flashcards WHERE id=:id"), {"id": fc_id}
    )).fetchone()
    assert row.frente == "Q"
    assert row.verso == "A"


@pytest.mark.asyncio
async def test_review_3x_interval_grows(db):
    await db.execute(sa.text(
        "INSERT INTO flashcards (node_id, frente, verso) VALUES (1, 'Q', 'A')"
    ))
    await db.commit()
    fc_id = (await db.execute(sa.text("SELECT id FROM flashcards"))).scalar()

    r1 = await review_flashcard(db, fc_id, quality=5)
    r2 = await review_flashcard(db, fc_id, quality=5)
    r3 = await review_flashcard(db, fc_id, quality=5)

    assert r2["interval_days"] > r1["interval_days"]
    assert r3["interval_days"] > r2["interval_days"]
    assert r3["next_review"] > datetime.utcnow().isoformat()


@pytest.mark.asyncio
async def test_get_due_returns_past_not_future(db):
    past = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    future = (datetime.utcnow() + timedelta(days=7)).isoformat()

    await db.execute(sa.text(
        "INSERT INTO flashcards (node_id, frente, verso, next_review) VALUES (1, 'Q1', 'A1', :nr)"
    ), {"nr": past})
    await db.execute(sa.text(
        "INSERT INTO flashcards (node_id, frente, verso, next_review) VALUES (1, 'Q2', 'A2', :nr)"
    ), {"nr": future})
    await db.commit()

    due = await get_due(db)
    assert len(due) == 1
    assert due[0]["frente"] == "Q1"
