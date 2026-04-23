from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.job import BidSuggestion, JobOut, ScoreOut
from app.scoring.bid_engine import suggest_bid
from app.scoring.keyword_engine import (
    classify_cyber_category,
    compute_cybersecurity_score,
    compute_freelance_fit_score,
    compute_priority_tier,
)
from app.services.job_service import list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobOut])
async def get_jobs(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=200, ge=1, le=1000),
    platform: str | None = None,
    region: str | None = None,
    min_match: int = Query(default=0, ge=0, le=100),
    max_risk: int = Query(default=100, ge=0, le=100),
    security_only: bool = False,
    min_freelance_fit: int = Query(default=0, ge=0, le=100),
) -> list[JobOut]:
    jobs = await list_jobs(db, limit=limit)

    filtered: list[tuple] = []
    for job in jobs:
        if platform and job.platform.lower() != platform.lower():
            continue
        if region and region.lower() not in job.region.lower():
            continue
        if job.score.match_score < min_match:
            continue
        if job.score.risk_score > max_risk:
            continue

        cyber_score = compute_cybersecurity_score(job.title, job.description, job.tags)
        if security_only and cyber_score < 35:
            continue

        freelance_fit = compute_freelance_fit_score(
            title=job.title,
            description=job.description,
            budget=job.budget,
            platform=job.platform,
            tags=job.tags,
        )
        if freelance_fit < min_freelance_fit:
            continue

        category = classify_cyber_category(job.title, job.description, job.tags)
        priority = compute_priority_tier(job.score.final_score, cyber_score, freelance_fit, job.score.risk_score)
        filtered.append((job, cyber_score, freelance_fit, category, priority))

    result = []
    for item, cyber_score, freelance_fit, category, priority in filtered:
        hint = item.tags[0] if item.tags else "general"
        bid = suggest_bid(item.budget, hint)
        result.append(
            JobOut(
                id=item.id,
                title=item.title,
                description=item.description,
                platform=item.platform,
                url=item.url,
                budget=item.budget,
                currency=item.currency,
                region=item.region,
                posted_at=item.posted_at,
                tags=item.tags,
                score=ScoreOut(
                    match_score=item.score.match_score,
                    risk_score=item.score.risk_score,
                    region_score=item.score.region_score,
                    final_score=item.score.final_score,
                ),
                suggested_bid=BidSuggestion(**bid),
                cybersecurity_score=cyber_score,
                freelance_fit_score=freelance_fit,
                cyber_category=category,
                priority_tier=priority,
            )
        )
    return result


@router.get("/fresh-count")
async def fresh_jobs_count(db: AsyncSession = Depends(get_db)) -> dict[str, int]:
    jobs = await list_jobs(db, limit=500)
    now = datetime.now(timezone.utc)
    fresh = [j for j in jobs if (now - j.posted_at).total_seconds() <= 300]
    return {"fresh": len(fresh)}
