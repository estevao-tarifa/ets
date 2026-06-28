import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.jobs.worker import claim_next_job, done_job


@pytest.fixture
async def engine():
    e = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with e.begin() as conn:
        await conn.execute(sa.text(
            "CREATE TABLE materias (id INTEGER PRIMARY KEY, nome TEXT NOT NULL UNIQUE)"
        ))
        await conn.execute(sa.text(
            "CREATE TABLE materials (id INTEGER PRIMARY KEY, materia_id INTEGER NOT NULL, "
            "filename TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE, path TEXT NOT NULL, "
            "status TEXT DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        ))
        await conn.execute(sa.text(
            "CREATE TABLE processing_jobs (id INTEGER PRIMARY KEY, material_id INTEGER NOT NULL, "
            "status TEXT DEFAULT 'queued', current_step TEXT, tentativas INTEGER DEFAULT 0, "
            "max_tentativas INTEGER DEFAULT 3, error_msg TEXT, "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        ))
        await conn.execute(sa.text("INSERT INTO materias (nome) VALUES ('Física')"))
        await conn.execute(sa.text(
            "INSERT INTO materials (materia_id, filename, sha256, path) "
            "VALUES (1, 'a.pdf', 'deadbeef', '/tmp/a.pdf')"
        ))
        await conn.execute(sa.text("INSERT INTO processing_jobs (material_id) VALUES (1)"))
    yield e
    await e.dispose()


@pytest.mark.asyncio
async def test_create_job_status_queued(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        row = (await session.execute(
            sa.text("SELECT status FROM processing_jobs WHERE id=1")
        )).fetchone()
    assert row.status == "queued"


@pytest.mark.asyncio
async def test_claim_next_job_sets_running(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        job_id = await claim_next_job(session)
    assert job_id == 1

    async with factory() as session:
        row = (await session.execute(
            sa.text("SELECT status FROM processing_jobs WHERE id=:id"), {"id": job_id}
        )).fetchone()
    assert row.status == "running"


@pytest.mark.asyncio
async def test_done_job_sets_done(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        job_id = await claim_next_job(session)
    async with factory() as session:
        await done_job(session, job_id)
    async with factory() as session:
        row = (await session.execute(
            sa.text("SELECT status FROM processing_jobs WHERE id=:id"), {"id": job_id}
        )).fetchone()
    assert row.status == "done"


@pytest.mark.asyncio
async def test_duplicate_sha256_rejected(engine):
    """Replicate the dedup check from the materials upload route handler."""
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _insert_material(session, sha: str) -> int:
        existing = (await session.execute(
            sa.text("SELECT id FROM materials WHERE sha256=:sha"), {"sha": sha}
        )).fetchone()
        if existing:
            raise ValueError("material já processado")  # mirrors HTTP 400
        r = await session.execute(
            sa.text(
                "INSERT INTO materials (materia_id, filename, sha256, path) "
                "VALUES (1, 'dup.pdf', :sha, '/tmp/dup.pdf') RETURNING id"
            ),
            {"sha": sha},
        )
        await session.commit()
        return r.fetchone()[0]

    # 'deadbeef' is already seeded — second insert must raise
    async with factory() as session:
        with pytest.raises(ValueError, match="já processado"):
            await _insert_material(session, "deadbeef")

    # A new sha goes through fine
    async with factory() as session:
        new_id = await _insert_material(session, "cafebabe")
    assert new_id is not None
