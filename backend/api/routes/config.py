from pathlib import Path
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

@router.post("/config", status_code=204)
async def save_config(body: ConfigIn):
    env_path = Path(".env")
    updates = {"LLM_PROVIDER": body.provider, "LLM_API_KEY": body.api_key, "LLM_MODEL": body.model}
    lines = env_path.read_text().splitlines() if env_path.exists() else []
    seen: set[str] = set()
    new_lines: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0].strip()
        if key in updates:
            new_lines.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            new_lines.append(line)
    for k, v in updates.items():
        if k not in seen:
            new_lines.append(f"{k}={v}")
    env_path.write_text("\n".join(new_lines) + "\n")
    get_settings.cache_clear()

@router.post("/config/test")
async def test_config(body: ConfigIn):
    result = await test_connection(body.provider, body.api_key, body.model)
    return result  # {"ok": bool, "error": str | None}
