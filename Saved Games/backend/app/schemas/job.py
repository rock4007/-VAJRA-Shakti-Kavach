from datetime import datetime

from pydantic import BaseModel, Field


class JobIn(BaseModel):
    id: str
    title: str
    description: str
    platform: str
    url: str
    budget: float | None = None
    currency: str = "USD"
    region: str = "global"
    posted_at: datetime
    tags: list[str] = Field(default_factory=list)


class ScoreOut(BaseModel):
    match_score: int
    risk_score: int
    region_score: int
    final_score: int


class BidSuggestion(BaseModel):
    low: float
    optimal: float
    premium: float


class JobOut(BaseModel):
    id: str
    title: str
    description: str
    platform: str
    url: str
    budget: float | None
    currency: str
    region: str
    posted_at: datetime
    tags: list[str]
    score: ScoreOut
    suggested_bid: BidSuggestion
    cybersecurity_score: int = 0
    freelance_fit_score: int = 0
    cyber_category: str = "general security"
    priority_tier: str = "low"


class KeywordIn(BaseModel):
    keyword: str
    weight: int = 10


class KeywordOut(BaseModel):
    id: int
    keyword: str
    weight: int


class PlatformSettingOut(BaseModel):
    platform: str
    enabled: bool
    interval_seconds: int


class PlatformSettingIn(BaseModel):
    platform: str
    enabled: bool
    interval_seconds: int


class PlatformCatalogOut(BaseModel):
    platform: str
    label: str
    category: str
    tier: str
    default_enabled: bool
