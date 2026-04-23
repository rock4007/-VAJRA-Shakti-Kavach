from datetime import datetime

import pytest
import respx
from httpx import Response

from app.collectors.api_collectors import RemoteOKCollector


@pytest.mark.asyncio
@respx.mock
async def test_remoteok_collect() -> None:
    respx.get("https://remoteok.com/api").mock(
        return_value=Response(
            200,
            json=[
                {"id": 0},
                {
                    "id": 123,
                    "position": "Security Engineer",
                    "description": "Penetration testing work",
                    "url": "https://remoteok.com/remote-jobs/123",
                    "location": "Japan",
                    "epoch": int(datetime.now().timestamp()),
                    "tags": ["cybersecurity"],
                },
            ],
        )
    )

    collector = RemoteOKCollector()
    jobs = await collector.collect()

    assert len(jobs) == 1
    assert jobs[0].platform == "remoteok"
    assert jobs[0].title == "Security Engineer"
