from fastapi import APIRouter
from pydantic import BaseModel
from backend.infrastructure.llm import test_connection
from backend.infrastructure.config import get_settings

router = APIRouter(tags=["config"])

class ConfigIn(BaseModel):
    provider: str
    api_key: str
    model: str

class ConfigOut(BaseModel):
    provider: str
    model: str
    api_key_hint: str  # last 4 chars only

@router.get("/config", response_model=ConfigOut)
async def get_config():
    s = get_settings()
    return ConfigOut(
        provider=s.LLM_PROVIDER,
        model=s.LLM_MODEL,
        api_key_hint=("..." + s.LLM_API_KEY[-4:]) if len(s.LLM_API_KEY) >= 4 else "****",
    )

@router.post("/config/test")
async def test_config(body: ConfigIn):
    # NEVER return api_key in response
    result = await test_connection(body.provider, body.api_key, body.model)
    return result  # {"ok": bool, "error": str | None}
