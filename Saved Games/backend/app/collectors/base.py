from abc import ABC, abstractmethod
from typing import Any

from app.schemas.job import JobIn


class BaseCollector(ABC):
    platform: str

    @abstractmethod
    async def collect(self) -> list[JobIn]:
        raise NotImplementedError

    def normalize(
        self,
        *,
        source_id: str,
        title: str,
        description: str,
        url: str,
        budget: float | None,
        currency: str,
        region: str,
        posted_at,
        tags: list[str] | None = None,
    ) -> JobIn:
        return JobIn(
            id=f"{self.platform}:{source_id}",
            title=title.strip(),
            description=description.strip(),
            platform=self.platform,
            url=url,
            budget=budget,
            currency=currency or "USD",
            region=region or "global",
            posted_at=posted_at,
            tags=tags or [],
        )


def safe_text(value: Any) -> str:
    return str(value or "").strip()
