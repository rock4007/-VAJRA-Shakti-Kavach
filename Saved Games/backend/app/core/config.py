from functools import lru_cache
from typing import Dict, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "PFID Backend"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"
    app_debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./pfid.db"
    redis_url: str = "redis://redis:6379/0"

    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    default_keywords: List[str] = Field(
        default_factory=lambda: [
            "cybersecurity",
            "penetration testing",
            "osint",
            "web development",
            "ui ux",
            "cryptography",
            "security audit",
            "compliance",
            "tool development",
            "bug bounty",
            "vulnerability assessment",
            "red team",
            "appsec",
            "incident response",
            "soc",
            "threat intelligence",
        ]
    )

    source_intervals: Dict[str, int] = Field(
        default_factory=lambda: {
            "upwork": 30,
            "freelancer": 45,
            "peopleperhour": 90,
            "guru": 120,
            "truelancer": 120,
            "worknhire": 180,

            "remoteok": 30,
            "weworkremotely": 90,
            "remotive": 90,
            "workingnomads": 120,

            "hackerone": 60,
            "bugcrowd": 90,
            "yeswehack": 120,
            "intigriti": 120,
            "synack": 300,

            "github": 60,
            "gitcoin": 180,
            "opencollective": 300,

            "wellfound": 120,
            "ycombinator": 180,
            "indiehackers": 120,

            "seek": 120,
            "crowdworks": 180,
            "lancers": 180,
            "nabbesh": 180,
            "ureed": 180,
            "bayt": 180,
            "gulftalent": 180,
            "malt": 150,
            "yunojuno": 180,
            "airtasker": 180,
            "trademe": 180,

            "toptal": 300,
            "braintrust": 180,
            "gunio": 300,
            "ateam": 300,
            "contra": 180,

            "topcoder": 180,
            "codeforces": 300,
            "leetcode": 300,
            "tryhackme": 360,
            "hackthebox": 360,

            "linkedin": 600,
            "reddit": 180,
        }
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        url = str(value)
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
