import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.infrastructure.database import init_db
from backend.jobs.worker import worker_loop

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    worker_task = asyncio.create_task(worker_loop())
    logger.info("ETS backend started")
    yield
    worker_task.cancel()

app = FastAPI(title="ETS API", version="0.1.0", lifespan=lifespan)

# Register all routers
from backend.api.routes import config, materials, graph, study, flashcards, exercises, exams, health
app.include_router(config.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(study.router, prefix="/api")
app.include_router(flashcards.router, prefix="/api")
app.include_router(exercises.router, prefix="/api")
app.include_router(exams.router, prefix="/api")
app.include_router(health.router, prefix="/api")

# Serve frontend SPA (must be last)
_frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="spa")
