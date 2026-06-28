import asyncio

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


async def claim_next_job(session: AsyncSession) -> int | None:
    result = await session.execute(
        sa.text(
            "UPDATE processing_jobs SET status='running', updated_at=datetime('now')"
            " WHERE id=("
            "  SELECT id FROM processing_jobs WHERE status='queued'"
            "  ORDER BY created_at LIMIT 1"
            ") RETURNING id"
        )
    )
    await session.commit()
    row = result.fetchone()
    return row[0] if row else None


@pytest.fixture
async def engine():
    e = create_async_engine("sqlite+aiosqlite:///:memory:", isolation_level="SERIALIZABLE")
    async with e.begin() as conn:
        await conn.execute(sa.text("PRAGMA foreign_keys=ON"))
        await conn.execute(
            sa.text(
                "CREATE TABLE materias (id INTEGER PRIMARY KEY,"
                " nome TEXT NOT NULL UNIQUE, descricao TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        await conn.execute(
            sa.text(
                "CREATE TABLE materials (id INTEGER PRIMARY KEY,"
                " materia_id INTEGER NOT NULL REFERENCES materias(id),"
                " filename TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE,"
                " path TEXT NOT NULL, status TEXT DEFAULT 'pending',"
                " created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        await conn.execute(
            sa.text(
                "CREATE TABLE processing_jobs (id INTEGER PRIMARY KEY,"
                " material_id INTEGER NOT NULL REFERENCES materials(id),"
                " status TEXT DEFAULT 'queued', current_step TEXT,"
                " tentativas INTEGER DEFAULT 0, max_tentativas INTEGER DEFAULT 3,"
                " error_msg TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,"
                " updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        # seed: 1 materia → 1 material → 2 jobs
        await conn.execute(sa.text("INSERT INTO materias (nome) VALUES ('Test')"))
        await conn.execute(
            sa.text(
                "INSERT INTO materials (materia_id, filename, sha256, path)"
                " VALUES (1, 'f.pdf', 'abc', '/tmp/f.pdf')"
            )
        )
        await conn.execute(sa.text("INSERT INTO processing_jobs (material_id) VALUES (1)"))
        await conn.execute(sa.text("INSERT INTO processing_jobs (material_id) VALUES (1)"))
    yield e
    await e.dispose()


@pytest.mark.asyncio
async def test_concurrent_claim_no_duplicate(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def worker():
        async with factory() as session:
            return await claim_next_job(session)

    ids = await asyncio.gather(worker(), worker())
    claimed = [i for i in ids if i is not None]
    # both jobs claimed, no duplicates
    assert len(claimed) == 2
    assert claimed[0] != claimed[1]
