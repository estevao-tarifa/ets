import os
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import MetaData, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite+aiosqlite:///./data/ets.db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
metadata = MetaData()


@event.listens_for(engine.sync_engine, "connect")
def _load_sqlite_vec(conn, _):
    conn.enable_load_extension(True)
    conn.load_extension("vec0")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    Path("data").mkdir(exist_ok=True)
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA foreign_keys=ON"))
