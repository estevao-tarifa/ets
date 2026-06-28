import asyncio
import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# SSE broadcast: maps material_id -> list of queues waiting for progress
_sse_queues: dict[int, list[asyncio.Queue]] = {}

def register_sse_queue(material_id: int, q: asyncio.Queue) -> None:
    _sse_queues.setdefault(material_id, []).append(q)

def unregister_sse_queue(material_id: int, q: asyncio.Queue) -> None:
    if material_id in _sse_queues:
        _sse_queues[material_id] = [x for x in _sse_queues[material_id] if x is not q]

async def broadcast_progress(material_id: int, step: str, status: str = "running") -> None:
    for q in _sse_queues.get(material_id, []):
        await q.put({"step": step, "status": status})

async def claim_next_job(session: AsyncSession) -> int | None:
    """Atomically claim one queued job. Returns job id or None."""
    result = await session.execute(
        text(
            "UPDATE processing_jobs SET status='running', updated_at=:now "
            "WHERE id=(SELECT id FROM processing_jobs WHERE status='queued' ORDER BY created_at LIMIT 1) "
            "RETURNING id"
        ),
        {"now": datetime.utcnow().isoformat()},
    )
    await session.commit()
    row = result.fetchone()
    return row[0] if row else None

async def fail_job(session: AsyncSession, job_id: int, error: str) -> None:
    await session.execute(
        text(
            "UPDATE processing_jobs SET status='failed', error_msg=:err, updated_at=:now WHERE id=:id"
        ),
        {"err": error[:500], "now": datetime.utcnow().isoformat(), "id": job_id},
    )
    await session.commit()

async def done_job(session: AsyncSession, job_id: int) -> None:
    await session.execute(
        text("UPDATE processing_jobs SET status='done', updated_at=:now WHERE id=:id"),
        {"now": datetime.utcnow().isoformat(), "id": job_id},
    )
    await session.commit()

async def run_job(job_id: int) -> None:
    """Run one pipeline job with retry backoff (2s, 4s, 8s)."""
    from backend.services.ingestion import run_ingestion_pipeline  # late import to avoid circular

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT material_id, tentativas FROM processing_jobs WHERE id=:id"),
            {"id": job_id},
        )
        row = result.fetchone()
        if not row:
            return
        material_id, tentativas = row

    max_retries = 3
    backoff = [2, 4, 8]

    for attempt in range(max_retries):
        try:
            await run_ingestion_pipeline(job_id, material_id)
            async with AsyncSessionLocal() as session:
                await done_job(session, job_id)
            return
        except Exception as e:
            logger.warning(f"Job {job_id} attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(backoff[attempt])
            else:
                async with AsyncSessionLocal() as session:
                    await fail_job(session, job_id, str(e))

async def worker_loop() -> None:
    """Main worker loop — polls every 2 seconds for queued jobs."""
    logger.info("Worker loop started")
    while True:
        try:
            async with AsyncSessionLocal() as session:
                job_id = await claim_next_job(session)
            if job_id:
                asyncio.create_task(run_job(job_id))
            else:
                await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            await asyncio.sleep(5)
