import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import AsyncSessionLocal
from backend.jobs.worker import broadcast_progress

logger = logging.getLogger(__name__)

PIPELINE_STEPS = ["pdf_to_md", "extraction", "normalization", "deduplication", "graph", "embeddings"]

async def _update_step(session: AsyncSession, job_id: int, step: str) -> None:
    await session.execute(
        text("UPDATE processing_jobs SET current_step=:step, updated_at=:now WHERE id=:jid"),
        {"step": step, "now": datetime.utcnow().isoformat(), "jid": job_id},
    )
    await session.commit()

async def run_ingestion_pipeline(job_id: int, material_id: int) -> None:
    """
    Execute all 6 pipeline stages in order:
    pdf_to_md → extraction → normalization → deduplication → graph → embeddings

    Reports progress via broadcast_progress (SSE) at each step.
    """
    from backend.pipeline.pdf_to_markdown import pdf_to_md
    from backend.pipeline.concept_extraction import extract_concepts
    from backend.pipeline.normalization import normalize_concepts
    from backend.pipeline.deduplication import dedup_concepts
    from backend.pipeline.graph_builder import build_graph
    from backend.pipeline.embedding_generator import generate_embeddings
    from backend.infrastructure.config import get_settings

    settings = get_settings()

    async with AsyncSessionLocal() as session:
        # Get material info
        mat_r = await session.execute(
            text("SELECT path, materia_id FROM materials WHERE id=:mid"), {"mid": material_id}
        )
        mat = mat_r.fetchone()
        if not mat:
            raise ValueError(f"Material {material_id} not found")
        pdf_path, materia_id = mat.path, mat.materia_id

    # Step 1: PDF → Markdown
    await broadcast_progress(material_id, "pdf_to_md")
    async with AsyncSessionLocal() as session:
        await _update_step(session, job_id, "pdf_to_md")
    markdown = pdf_to_md(pdf_path)

    # Step 2: Extract concepts
    await broadcast_progress(material_id, "extraction")
    async with AsyncSessionLocal() as session:
        await _update_step(session, job_id, "extraction")
    raw_concepts = await extract_concepts(
        markdown, settings.LLM_PROVIDER, settings.LLM_API_KEY, settings.LLM_MODEL
    )

    # Step 3: Normalize
    await broadcast_progress(material_id, "normalization")
    async with AsyncSessionLocal() as session:
        await _update_step(session, job_id, "normalization")
    normalized = normalize_concepts(raw_concepts)

    # Step 4: Deduplicate
    await broadcast_progress(material_id, "deduplication")
    async with AsyncSessionLocal() as session:
        await _update_step(session, job_id, "deduplication")
        final_concepts = await dedup_concepts(session, normalized, materia_id)

    # Step 5: Build graph
    await broadcast_progress(material_id, "graph")
    async with AsyncSessionLocal() as session:
        await _update_step(session, job_id, "graph")
        node_ids = await build_graph(session, materia_id, material_id, final_concepts)

    # Step 6: Generate embeddings
    await broadcast_progress(material_id, "embeddings")
    async with AsyncSessionLocal() as session:
        await _update_step(session, job_id, "embeddings")
        await generate_embeddings(session, node_ids)

    await broadcast_progress(material_id, "done", status="done")
    logger.info(f"Pipeline complete for job {job_id}, material {material_id}")
