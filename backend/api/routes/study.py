from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import get_session
from backend.services import study as study_svc

router = APIRouter(tags=["study"])

@router.post("/sessions")
async def create_session(materia_id: int, session: AsyncSession = Depends(get_session)):
    sid = await study_svc.create_session(session, materia_id)
    return {"session_id": sid}

class EventIn(BaseModel):
    tipo: str  # acerto/erro/duvida
    node_id: int | None = None

@router.post("/sessions/{session_id}/events")
async def add_event(session_id: int, body: EventIn, session: AsyncSession = Depends(get_session)):
    eid = await study_svc.add_event(session, session_id, body.tipo, body.node_id)
    return {"event_id": eid}

class CloseIn(BaseModel):
    autoavaliacao: int  # 1-5, required
    pendente: str | None = None

@router.post("/sessions/{session_id}/close")
async def close_session(session_id: int, body: CloseIn, session: AsyncSession = Depends(get_session)):
    try:
        await study_svc.close_session(session, session_id, body.autoavaliacao, body.pendente)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"ok": True}
