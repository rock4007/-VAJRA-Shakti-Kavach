from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import PlatformSetting
from app.schemas.job import PlatformSettingIn


async def list_platform_settings(db: AsyncSession) -> list[PlatformSetting]:
    result = await db.execute(select(PlatformSetting).order_by(PlatformSetting.platform.asc()))
    return list(result.scalars().all())


async def upsert_platform_setting(db: AsyncSession, payload: PlatformSettingIn) -> PlatformSetting:
    result = await db.execute(select(PlatformSetting).where(PlatformSetting.platform == payload.platform))
    item = result.scalar_one_or_none()
    if item:
        item.enabled = payload.enabled
        item.interval_seconds = payload.interval_seconds
        await db.commit()
        await db.refresh(item)
        return item

    item = PlatformSetting(
        platform=payload.platform,
        enabled=payload.enabled,
        interval_seconds=payload.interval_seconds,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
