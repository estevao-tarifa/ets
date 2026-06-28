from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import get_session
from backend.services import graph as graph_svc

router = APIRouter(tags=["graph"])

@router.get("/graph")
async def get_graph(materia_id: int, session: AsyncSession = Depends(get_session)):
    return await graph_svc.get_graph_data(session, materia_id)

@router.get("/nodes/{node_id}")
async def get_node(node_id: int, session: AsyncSession = Depends(get_session)):
    node = await graph_svc.get_node(session, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

class MergeIn(BaseModel):
    keep_id: int
    discard_id: int

@router.post("/nodes/merge")
async def merge_nodes(body: MergeIn, session: AsyncSession = Depends(get_session)):
    await graph_svc.merge_nodes(session, body.keep_id, body.discard_id)
    return {"ok": True}
