from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import get_session
from backend.infrastructure.config import get_settings
from backend.services import flashcard as fc_svc

router = APIRouter(tags=["flashcards"])

@router.get("/flashcards/due")
async def get_due(session: AsyncSession = Depends(get_session)):
    return await fc_svc.get_due(session)

@router.post("/flashcards/generate")
async def generate(node_id: int, session: AsyncSession = Depends(get_session)):
    s = get_settings()
    fid = await fc_svc.generate_flashcard(session, node_id, s.LLM_PROVIDER, s.LLM_API_KEY, s.LLM_MODEL)
    return {"flashcard_id": fid}

class ReviewIn(BaseModel):
    quality: int  # 0-5

@router.post("/flashcards/{flashcard_id}/review")
async def review(flashcard_id: int, body: ReviewIn, session: AsyncSession = Depends(get_session)):
    return await fc_svc.review_flashcard(session, flashcard_id, body.quality)
