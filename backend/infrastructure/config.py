from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    LLM_PROVIDER: str = "groq"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "llama3-8b-8192"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ets.db"
    DATA_DIR: str = "./data"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
