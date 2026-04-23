import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, jobs, keywords, settings, ws
from app.core.config import get_settings
from app.core.database import Base, engine
from app.scheduler.collector_scheduler import bootstrap_defaults, start_scheduler, stop_scheduler, warmup_run

logging.basicConfig(level=logging.INFO)
settings_obj = get_settings()

app = FastAPI(title=settings_obj.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings_obj.cors_origins,
    allow_origin_regex=r"https?://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(keywords.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(ws.router)


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await bootstrap_defaults()
    start_scheduler()
    await warmup_run()


@app.on_event("shutdown")
async def shutdown() -> None:
    stop_scheduler()
    await engine.dispose()
