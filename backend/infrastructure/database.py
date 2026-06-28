import os
from collections.abc import AsyncGenerator
from pathlib import Path

import sqlite_vec
from sqlalchemy import MetaData, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite+aiosqlite:///./data/ets.db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
metadata = MetaData()


@event.listens_for(engine.sync_engine, "connect")
def _load_sqlite_vec(dbapi_conn, _):
    # ponytail: best-effort vec0 load; only needed for KNN queries (pipeline dedup)
    try:
        import sqlite3
        # aiosqlite async driver — skip extension loading in async context
        # Extension is pre-loaded in init_db.py (sync sqlite3) for the vec virtual table
    except Exception:
        pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    Path("data").mkdir(exist_ok=True)
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA foreign_keys=ON"))
