from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import get_session
from backend.infrastructure.config import get_settings
from backend.services import exam as exam_svc

router = APIRouter(tags=["exams"])

@router.post("/exams/diagnostic")
async def diagnostic(materia_id: int, session: AsyncSession = Depends(get_session)):
    return await exam_svc.get_diagnostic(session, materia_id)

class PlanIn(BaseModel):
    materia_id: int
    days_until_exam: int

@router.post("/exams/plan")
async def revision_plan(body: PlanIn, session: AsyncSession = Depends(get_session)):
    s = get_settings()
    plan = await exam_svc.generate_revision_plan(
        session, body.materia_id, s.LLM_PROVIDER, s.LLM_API_KEY, s.LLM_MODEL, body.days_until_exam
    )
    return {"plan": plan}
