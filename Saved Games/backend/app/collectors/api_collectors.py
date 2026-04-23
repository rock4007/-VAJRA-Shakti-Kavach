from datetime import datetime, timezone
from xml.etree import ElementTree

import httpx

from app.collectors.base import BaseCollector, safe_text
from app.schemas.job import JobIn


class UpworkCollector(BaseCollector):
    platform = "upwork"
    url = "https://www.upwork.com/ab/feed/jobs/rss"

    async def collect(self) -> list[JobIn]:
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(self.url)
                response.raise_for_status()

            root = ElementTree.fromstring(response.text)
            channel = root.find("channel")
            if channel is None:
                return []

            jobs: list[JobIn] = []
            for item in channel.findall("item")[:25]:
                link = safe_text(item.findtext("link"))
                guid = safe_text(item.findtext("guid")) or link
                title = safe_text(item.findtext("title"))
                description = safe_text(item.findtext("description"))
                pub_date = safe_text(item.findtext("pubDate"))
                posted_at = datetime.now(timezone.utc)
                if pub_date:
                    try:
                        posted_at = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                    except ValueError:
                        posted_at = datetime.now(timezone.utc)

                jobs.append(
                    self.normalize(
                        source_id=guid,
                        title=title,
                        description=description,
                        url=link,
                        budget=None,
                        currency="USD",
                        region="global",
                        posted_at=posted_at,
                        tags=[],
                    )
                )
            return jobs
        except Exception:
            return []


class RemoteOKCollector(BaseCollector):
    platform = "remoteok"
    url = "https://remoteok.com/api"

    async def collect(self) -> list[JobIn]:
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(self.url, headers={"User-Agent": "pfid-bot/1.0"})
                response.raise_for_status()
                payload = response.json()

            jobs: list[JobIn] = []
            for item in payload[1:30]:
                source_id = str(item.get("id") or item.get("slug") or item.get("url"))
                jobs.append(
                    self.normalize(
                        source_id=source_id,
                        title=safe_text(item.get("position") or item.get("title")),
                        description=safe_text(item.get("description") or ""),
                        url=safe_text(item.get("url") or "https://remoteok.com"),
                        budget=None,
                        currency="USD",
                        region=safe_text(item.get("location") or "remote"),
                        posted_at=datetime.fromtimestamp(int(item.get("epoch") or 0), tz=timezone.utc)
                        if item.get("epoch")
                        else datetime.now(timezone.utc),
                        tags=item.get("tags") or [],
                    )
                )
            return jobs
        except Exception:
            return []


class FreelancerCollector(BaseCollector):
    platform = "freelancer"
    url = "https://www.freelancer.com/api/projects/0.1/projects/active/"

    async def collect(self) -> list[JobIn]:
        params = {
            "limit": 25,
            "full_description": True,
            "sort_field": "time_updated",
            "sort_direction": "desc",
        }
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(self.url, params=params)
                response.raise_for_status()
                payload = response.json()

            projects = payload.get("result", {}).get("projects", [])
            jobs: list[JobIn] = []
            for project in projects:
                budget = None
                currency = "USD"
                budget_data = project.get("budget", {})
                if budget_data:
                    currency = safe_text(budget_data.get("currency", {}).get("code") or "USD")
                    minimum = budget_data.get("minimum")
                    maximum = budget_data.get("maximum")
                    if minimum and maximum:
                        budget = (float(minimum) + float(maximum)) / 2

                jobs.append(
                    self.normalize(
                        source_id=str(project.get("id")),
                        title=safe_text(project.get("title")),
                        description=safe_text(project.get("preview_description") or project.get("description")),
                        url=f"https://www.freelancer.com/projects/{project.get('seo_url', '')}",
                        budget=budget,
                        currency=currency,
                        region="global",
                        posted_at=datetime.fromtimestamp(int(project.get("time_submitted") or 0), timezone.utc)
                        if project.get("time_submitted")
                        else datetime.now(timezone.utc),
                        tags=[safe_text(tag.get("name")) for tag in project.get("jobs", []) if tag.get("name")],
                    )
                )
            return jobs
        except Exception:
            return []


class HackerOneCollector(BaseCollector):
    platform = "hackerone"
    url = "https://api.hackerone.com/v1/hackers/programs"

    async def collect(self) -> list[JobIn]:
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(self.url)
                response.raise_for_status()
                payload = response.json()

            jobs: list[JobIn] = []
            for program in payload.get("data", [])[:25]:
                attr = program.get("attributes", {})
                pid = str(program.get("id"))
                handle = safe_text(attr.get("handle"))
                jobs.append(
                    self.normalize(
                        source_id=pid,
                        title=f"Bug Bounty Program: {safe_text(attr.get('name'))}",
                        description=safe_text(attr.get("submission_state") or "Public bug bounty program"),
                        url=f"https://hackerone.com/{handle}" if handle else "https://hackerone.com/hacktivity",
                        budget=None,
                        currency="USD",
                        region="global",
                        posted_at=datetime.now(timezone.utc),
                        tags=["bug bounty", "security"],
                    )
                )
            return jobs
        except Exception:
            return []


class GitHubIssuesCollector(BaseCollector):
    platform = "github"

    def __init__(self, search_query: str = "security audit") -> None:
        self.search_query = search_query

    async def collect(self) -> list[JobIn]:
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(
                    "https://api.github.com/search/issues",
                    params={"q": f"{self.search_query} type:issue state:open", "sort": "updated"},
                    headers={"Accept": "application/vnd.github+json"},
                )
                response.raise_for_status()
                payload = response.json()

            jobs: list[JobIn] = []
            for item in payload.get("items", [])[:25]:
                jobs.append(
                    self.normalize(
                        source_id=str(item.get("id")),
                        title=safe_text(item.get("title")),
                        description=safe_text(item.get("body") or "Open issue that may map to contract work"),
                        url=safe_text(item.get("html_url")),
                        budget=None,
                        currency="USD",
                        region="global",
                        posted_at=datetime.strptime(item.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").replace(
                            tzinfo=timezone.utc
                        )
                        if item.get("created_at")
                        else datetime.now(timezone.utc),
                        tags=[
                            safe_text(label.get("name"))
                            for label in item.get("labels", [])
                            if isinstance(label, dict) and label.get("name")
                        ],
                    )
                )
            return jobs
        except Exception:
            return []
