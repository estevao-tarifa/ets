from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import get_session
from backend.infrastructure.config import get_settings
from backend.services import exercise as ex_svc

router = APIRouter(tags=["exercises"])

@router.post("/exercises/generate")
async def generate_exercise(node_id: int, session: AsyncSession = Depends(get_session)):
    s = get_settings()
    return await ex_svc.generate_exercise(session, node_id, s.LLM_PROVIDER, s.LLM_API_KEY, s.LLM_MODEL)
