import hashlib
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.infrastructure.database import get_session
from backend.infrastructure.storage import save_pdf
from backend.jobs.worker import register_sse_queue, unregister_sse_queue
import asyncio, json

router = APIRouter(tags=["materials"])

@router.post("/materials/upload")
async def upload_material(
    materia_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()
    sha256 = hashlib.sha256(content).hexdigest()

    # Reject duplicate
    existing = await session.execute(text("SELECT id FROM materials WHERE sha256=:sha"), {"sha": sha256})
    if existing.fetchone():
        raise HTTPException(status_code=400, detail="material já processado")

    # Save to DB
    r = await session.execute(
        text("INSERT INTO materials(materia_id, filename, sha256, path, status) VALUES(:mid,:fn,:sha,:path,'pending') RETURNING id"),
        {"mid": materia_id, "fn": file.filename, "sha": sha256, "path": ""},
    )
    await session.commit()
    material_id = r.fetchone()[0]

    # Save to disk
    path = save_pdf(content, material_id)
    await session.execute(text("UPDATE materials SET path=:p WHERE id=:id"), {"p": path, "id": material_id})

    # Create processing job
    await session.execute(
        text("INSERT INTO processing_jobs(material_id) VALUES(:mid)"), {"mid": material_id}
    )
    await session.commit()
    return {"material_id": material_id}

@router.get("/materials/{material_id}/progress")
async def material_progress(material_id: int):
    """SSE endpoint for pipeline progress."""
    q: asyncio.Queue = asyncio.Queue()
    register_sse_queue(material_id, q)

    async def event_generator():
        try:
            while True:
                event = await asyncio.wait_for(q.get(), timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("status") in ("done", "failed"):
                    break
        except asyncio.TimeoutError:
            yield "data: {\"status\": \"timeout\"}\n\n"
        finally:
            unregister_sse_queue(material_id, q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
