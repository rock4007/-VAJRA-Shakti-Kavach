from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Keyword
from app.schemas.job import KeywordIn


async def list_keywords(db: AsyncSession) -> list[Keyword]:
    result = await db.execute(select(Keyword).order_by(Keyword.keyword.asc()))
    return list(result.scalars().all())


async def upsert_keyword(db: AsyncSession, payload: KeywordIn) -> Keyword:
    keyword = payload.keyword.strip().lower()
    result = await db.execute(select(Keyword).where(Keyword.keyword == keyword))
    existing = result.scalar_one_or_none()
    if existing:
        existing.weight = payload.weight
        await db.commit()
        await db.refresh(existing)
        return existing

    item = Keyword(keyword=keyword, weight=payload.weight)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def remove_keyword(db: AsyncSession, keyword_id: int) -> None:
    await db.execute(delete(Keyword).where(Keyword.id == keyword_id))
    await db.commit()
