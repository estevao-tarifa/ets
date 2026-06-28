from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.infrastructure.database import get_session

router = APIRouter(tags=["health"])

@router.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    await session.execute(text("SELECT 1"))
    # Check sqlite-vec
    try:
        await session.execute(text("SELECT count(*) FROM node_embeddings"))
        vec_ok = True
    except Exception:
        vec_ok = False
    return {"status": "ok", "db": "ok", "vec": "ok" if vec_ok else "unavailable"}
