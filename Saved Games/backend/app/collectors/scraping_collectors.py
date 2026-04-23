from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector
from app.schemas.job import JobIn


class PassiveScrapingCollector(BaseCollector):
    source_url: str
    default_region: str = "global"

    async def collect(self) -> list[JobIn]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.source_url, headers={"User-Agent": "pfid-bot/1.0"})
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("title")
            if not title_tag:
                return []

            return [
                self.normalize(
                    source_id="index",
                    title=f"{self.platform.title()} opportunities",
                    description=title_tag.text.strip(),
                    url=self.source_url,
                    budget=None,
                    currency="USD",
                    region=self.default_region,
                    posted_at=datetime.now(timezone.utc),
                    tags=[self.platform],
                )
            ]
        except Exception:
            return []


class DynamicPassiveCollector(PassiveScrapingCollector):
    def __init__(self, platform: str, source_url: str, default_region: str = "global") -> None:
        self.platform = platform
        self.source_url = source_url
        self.default_region = default_region


class WellfoundCollector(PassiveScrapingCollector):
    platform = "wellfound"
    source_url = "https://wellfound.com/jobs"


class PeoplePerHourCollector(PassiveScrapingCollector):
    platform = "peopleperhour"
    source_url = "https://www.peopleperhour.com/freelance-jobs"


class MaltCollector(PassiveScrapingCollector):
    platform = "malt"
    source_url = "https://www.malt.com/en/projects"


class CrowdWorksCollector(PassiveScrapingCollector):
    platform = "crowdworks"
    source_url = "https://crowdworks.jp/public/jobs"
    default_region = "japan"


class LancersCollector(PassiveScrapingCollector):
    platform = "lancers"
    source_url = "https://www.lancers.jp/work/search"
    default_region = "japan"


class BaytCollector(PassiveScrapingCollector):
    platform = "bayt"
    source_url = "https://www.bayt.com/en/jobs/"
    default_region = "uae"


class SeekCollector(PassiveScrapingCollector):
    platform = "seek"
    source_url = "https://www.seek.co.nz/jobs"
    default_region = "new zealand"


class TradeMeJobsCollector(PassiveScrapingCollector):
    platform = "trademe"
    source_url = "https://www.trademe.co.nz/a/jobs"
    default_region = "new zealand"


class IndieHackersCollector(PassiveScrapingCollector):
    platform = "indiehackers"
    source_url = "https://www.indiehackers.com/jobs"


class LinkedInPlaceholderCollector(BaseCollector):
    platform = "linkedin"

    async def collect(self) -> list[JobIn]:
        return []


class ManualPlatformCollector(BaseCollector):
    def __init__(self, platform: str) -> None:
        self.platform = platform

    async def collect(self) -> list[JobIn]:
        return []
