from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.job import KeywordIn, KeywordOut
from app.services.keyword_service import list_keywords, remove_keyword, upsert_keyword

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.get("/", response_model=list[KeywordOut])
async def get_keywords(db: AsyncSession = Depends(get_db)) -> list[KeywordOut]:
    records = await list_keywords(db)
    return [KeywordOut(id=k.id, keyword=k.keyword, weight=k.weight) for k in records]


@router.post("/", response_model=KeywordOut)
async def create_keyword(payload: KeywordIn, db: AsyncSession = Depends(get_db)) -> KeywordOut:
    item = await upsert_keyword(db, payload)
    return KeywordOut(id=item.id, keyword=item.keyword, weight=item.weight)


@router.delete("/{keyword_id}")
async def delete_keyword(keyword_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    await remove_keyword(db, keyword_id)
    return {"ok": True}
