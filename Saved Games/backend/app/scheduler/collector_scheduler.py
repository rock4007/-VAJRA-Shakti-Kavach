import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.registry import get_collectors
from app.core.config import get_settings
from app.core.platform_catalog import get_platform_catalog
from app.core.database import SessionLocal
from app.models.job import PlatformSetting
from app.schemas.job import BidSuggestion, JobOut, ScoreOut
from app.scoring.bid_engine import suggest_bid
from app.scoring.keyword_engine import (
    classify_cyber_category,
    compute_cybersecurity_score,
    compute_freelance_fit_score,
    compute_priority_tier,
)
from app.services.job_service import upsert_job_with_score
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)
settings = get_settings()
scheduler = AsyncIOScheduler()


async def run_collector(platform: str, db: AsyncSession) -> None:
    collector = get_collectors().get(platform)
    if collector is None:
        return

    jobs = await collector.collect()
    for item in jobs:
        try:
            job, score, is_new = await upsert_job_with_score(db, item)
            if is_new:
                cyber_score = compute_cybersecurity_score(job.title, job.description, job.tags)
                freelance_fit = compute_freelance_fit_score(
                    title=job.title,
                    description=job.description,
                    budget=job.budget,
                    platform=job.platform,
                    tags=job.tags,
                )
                category = classify_cyber_category(job.title, job.description, job.tags)
                priority = compute_priority_tier(score.final_score, cyber_score, freelance_fit, score.risk_score)
                bid = suggest_bid(job.budget, job.tags[0] if job.tags else "general")
                await ws_manager.publish(
                    "jobs",
                    {
                        "type": "new_job",
                        "payload": JobOut(
                            id=job.id,
                            title=job.title,
                            description=job.description,
                            platform=job.platform,
                            url=job.url,
                            budget=job.budget,
                            currency=job.currency,
                            region=job.region,
                            posted_at=job.posted_at,
                            tags=job.tags,
                            score=ScoreOut(
                                match_score=score.match_score,
                                risk_score=score.risk_score,
                                region_score=score.region_score,
                                final_score=score.final_score,
                            ),
                            suggested_bid=BidSuggestion(**bid),
                            cybersecurity_score=cyber_score,
                            freelance_fit_score=freelance_fit,
                            cyber_category=category,
                            priority_tier=priority,
                        ).model_dump(mode="json"),
                    },
                )
        except Exception as exc:
            await db.rollback()
            logger.exception("Collector persistence failed for %s: %s", platform, exc)


async def run_collector_once(platform: str) -> None:
    async with SessionLocal() as db:
        from sqlalchemy import select

        result = await db.execute(select(PlatformSetting).where(PlatformSetting.platform == platform))
        setting = result.scalar_one_or_none()
        if setting is not None and not setting.enabled:
            return
        await run_collector(platform, db)


def _safe_job(platform: str):
    async def _runner() -> None:
        try:
            await run_collector_once(platform)
        except Exception as exc:
            logger.exception("Collector %s failed: %s", platform, exc)

    return _runner


async def bootstrap_defaults() -> None:
    from sqlalchemy import select

    from app.models.job import Keyword

    async with SessionLocal() as db:
        for keyword in settings.default_keywords:
            result = await db.execute(select(Keyword).where(Keyword.keyword == keyword.lower()))
            if result.scalar_one_or_none() is None:
                db.add(Keyword(keyword=keyword.lower(), weight=10))

        catalog = get_platform_catalog()
        collectors = get_collectors()
        for platform in collectors.keys():
            interval = settings.source_intervals.get(platform, 300)
            enabled = bool(catalog.get(platform, {}).get("default_enabled", True))
            result = await db.execute(select(PlatformSetting).where(PlatformSetting.platform == platform))
            if result.scalar_one_or_none() is None:
                db.add(PlatformSetting(platform=platform, enabled=enabled, interval_seconds=interval))

        await db.commit()


def start_scheduler() -> None:
    if scheduler.running:
        return

    collectors = get_collectors()
    for platform in collectors.keys():
        interval = settings.source_intervals.get(platform, 180)
        scheduler.add_job(_safe_job(platform), "interval", seconds=interval, id=f"collector-{platform}", replace_existing=True)

    scheduler.start()


def update_platform_schedule(platform: str, enabled: bool, interval_seconds: int) -> None:
    if not scheduler.running:
        return

    job_id = f"collector-{platform}"
    runner = _safe_job(platform)
    existing = scheduler.get_job(job_id)

    if existing is None:
        scheduler.add_job(runner, "interval", seconds=interval_seconds, id=job_id, replace_existing=True)
        if not enabled:
            scheduler.pause_job(job_id)
        return

    scheduler.reschedule_job(job_id, trigger="interval", seconds=interval_seconds)
    if enabled:
        scheduler.resume_job(job_id)
    else:
        scheduler.pause_job(job_id)


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


async def warmup_run() -> None:
    tasks = [run_collector_once(platform) for platform in get_collectors().keys()]
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
