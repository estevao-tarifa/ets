from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import get_session

router = APIRouter(tags=["materias"])


class MateriaIn(BaseModel):
    nome: str
    descricao: str | None = None


@router.get("/materias")
async def list_materias(session: AsyncSession = Depends(get_session)):
    r = await session.execute(text("SELECT id, nome, descricao, created_at FROM materias ORDER BY nome"))
    return [dict(row._mapping) for row in r]


@router.post("/materias", status_code=201)
async def create_materia(body: MateriaIn, session: AsyncSession = Depends(get_session)):
    try:
        r = await session.execute(
            text("INSERT INTO materias(nome, descricao) VALUES(:nome,:desc) RETURNING id, nome, descricao"),
            {"nome": body.nome, "desc": body.descricao},
        )
        await session.commit()
        return dict(r.fetchone()._mapping)
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=409, detail="Matéria já existe")
        raise
