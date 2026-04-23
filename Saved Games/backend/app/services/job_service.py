from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job import Job, Keyword, Score
from app.scoring.keyword_engine import (
    WeightedKeyword,
    compute_match_score,
    compute_region_score,
    compute_risk_score,
    final_score,
)
from app.schemas.job import JobIn


async def list_jobs(db: AsyncSession, limit: int = 200) -> list[Job]:
    result = await db.execute(
        select(Job).options(selectinload(Job.score)).order_by(Job.posted_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def get_weighted_keywords(db: AsyncSession) -> list[WeightedKeyword]:
    result = await db.execute(select(Keyword))
    return [WeightedKeyword(keyword=k.keyword, weight=k.weight) for k in result.scalars().all()]


async def upsert_job_with_score(db: AsyncSession, item: JobIn) -> tuple[Job, Score, bool]:
    result = await db.execute(select(Job).options(selectinload(Job.score)).where(Job.id == item.id))
    existing = result.scalar_one_or_none()

    weighted = await get_weighted_keywords(db)
    match = compute_match_score(item.title, item.description, weighted)
    risk = compute_risk_score(item.title, item.description, item.budget)
    region = compute_region_score(item.region)
    total = final_score(match, region, risk)

    if existing:
        existing.title = item.title
        existing.description = item.description
        existing.url = item.url
        existing.budget = item.budget
        existing.currency = item.currency
        existing.region = item.region
        existing.posted_at = item.posted_at
        existing.tags = item.tags
        if existing.score is None:
            existing.score = Score(
                job_id=existing.id,
                match_score=match,
                risk_score=risk,
                region_score=region,
                final_score=total,
            )
        else:
            existing.score.match_score = match
            existing.score.risk_score = risk
            existing.score.region_score = region
            existing.score.final_score = total
        await db.commit()
        await db.refresh(existing)
        await db.refresh(existing, attribute_names=["score"])
        return existing, existing.score, False

    new_job = Job(
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
    )
    new_score = Score(
        job_id=item.id,
        match_score=match,
        risk_score=risk,
        region_score=region,
        final_score=total,
    )
    new_job.score = new_score
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    await db.refresh(new_job, attribute_names=["score"])
    return new_job, new_score, True
