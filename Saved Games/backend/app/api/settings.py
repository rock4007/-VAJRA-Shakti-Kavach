from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.platform_catalog import get_platform_catalog
from app.core.database import get_db
from app.scheduler.collector_scheduler import update_platform_schedule
from app.schemas.job import PlatformCatalogOut, PlatformSettingIn, PlatformSettingOut
from app.services.settings_service import list_platform_settings, upsert_platform_setting

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/platforms", response_model=list[PlatformSettingOut])
async def get_platform_settings(db: AsyncSession = Depends(get_db)) -> list[PlatformSettingOut]:
    rows = await list_platform_settings(db)
    return [
        PlatformSettingOut(platform=row.platform, enabled=row.enabled, interval_seconds=row.interval_seconds)
        for row in rows
    ]


@router.get("/platform-catalog", response_model=list[PlatformCatalogOut])
async def get_platform_catalog_view() -> list[PlatformCatalogOut]:
    catalog = get_platform_catalog()
    return [
        PlatformCatalogOut(
            platform=name,
            label=str(meta.get("label", name)),
            category=str(meta.get("category", "other")),
            tier=str(meta.get("tier", "other")),
            default_enabled=bool(meta.get("default_enabled", False)),
        )
        for name, meta in sorted(catalog.items(), key=lambda pair: pair[0])
    ]


@router.put("/platforms", response_model=PlatformSettingOut)
async def set_platform_setting(payload: PlatformSettingIn, db: AsyncSession = Depends(get_db)) -> PlatformSettingOut:
    row = await upsert_platform_setting(db, payload)
    update_platform_schedule(row.platform, row.enabled, row.interval_seconds)
    return PlatformSettingOut(platform=row.platform, enabled=row.enabled, interval_seconds=row.interval_seconds)
