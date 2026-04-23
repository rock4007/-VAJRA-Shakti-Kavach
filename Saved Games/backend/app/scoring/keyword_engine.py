import re
from dataclasses import dataclass


@dataclass
class WeightedKeyword:
    keyword: str
    weight: int


def tokenize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def compute_match_score(title: str, description: str, weighted_keywords: list[WeightedKeyword]) -> int:
    t = tokenize(title)
    d = tokenize(description)

    score = 0
    for item in weighted_keywords:
        key = tokenize(item.keyword)
        if not key:
            continue
        if key in t:
            score += item.weight * 3
        if key in d:
            score += item.weight

    return max(0, min(100, score))


def compute_risk_score(title: str, description: str, budget: float | None) -> int:
    body = f"{title} {description}".lower()
    risk = 0

    suspicious_markers = [
        "telegram",
        "whatsapp",
        "gmail",
        "urgent payment",
        "send sample before hire",
        "contact me directly",
    ]
    for marker in suspicious_markers:
        if marker in body:
            risk += 20

    if budget is not None and budget <= 20:
        risk += 20
    if budget is not None and budget > 100000:
        risk += 20

    return max(0, min(100, risk))


def compute_region_score(region: str) -> int:
    normalized = (region or "").lower()
    if "japan" in normalized:
        return 20
    if "uae" in normalized or "dubai" in normalized:
        return 15
    if "new zealand" in normalized or "nz" in normalized:
        return 20
    return 0


def final_score(match_score: int, region_score: int, risk_score: int) -> int:
    total = match_score + region_score - risk_score
    return max(0, min(100, total))


def compute_cybersecurity_score(title: str, description: str, tags: list[str]) -> int:
    body = tokenize(f"{title} {description} {' '.join(tags)}")
    signals = {
        "penetration": 16,
        "pentest": 16,
        "vulnerability": 14,
        "bug bounty": 14,
        "red team": 14,
        "threat": 10,
        "siem": 12,
        "soc": 10,
        "incident response": 12,
        "forensics": 12,
        "owasp": 12,
        "security audit": 14,
        "compliance": 8,
        "osint": 12,
        "malware": 12,
        "reverse engineering": 12,
        "application security": 12,
        "cloud security": 10,
        "cryptography": 10,
    }
    score = 0
    for term, weight in signals.items():
        if term in body:
            score += weight
    return max(0, min(100, score))


def classify_cyber_category(title: str, description: str, tags: list[str]) -> str:
    body = tokenize(f"{title} {description} {' '.join(tags)}")
    buckets = {
        "penetration testing": ["penetration", "pentest", "red team", "vulnerability"],
        "bug bounty": ["bug bounty", "hackerone", "disclosure"],
        "security audit": ["security audit", "compliance", "iso", "soc2", "owasp"],
        "osint": ["osint", "threat intel", "investigation"],
        "appsec": ["application security", "sast", "dast", "secure code"],
        "incident response": ["incident", "forensics", "malware", "soc"],
    }
    for category, terms in buckets.items():
        if any(term in body for term in terms):
            return category
    return "general security"


def compute_freelance_fit_score(
    *,
    title: str,
    description: str,
    budget: float | None,
    platform: str,
    tags: list[str],
) -> int:
    body = tokenize(f"{title} {description} {' '.join(tags)} {platform}")
    score = 35

    positive_terms = [
        "contract",
        "freelance",
        "remote",
        "part-time",
        "hourly",
        "fixed price",
        "statement of work",
        "scope",
    ]
    for term in positive_terms:
        if term in body:
            score += 8

    if budget is not None:
        if 200 <= budget <= 15000:
            score += 20
        elif budget > 15000:
            score += 12
        elif budget < 80:
            score -= 10

    if platform.lower() in {"upwork", "freelancer", "remoteok", "crowdworks", "lancers", "peopleperhour"}:
        score += 12

    if "full-time" in body and "contract" not in body:
        score -= 20

    return max(0, min(100, score))


def compute_priority_tier(final_score_value: int, cyber_score: int, freelance_fit: int, risk_score_value: int) -> str:
    weighted = final_score_value + (cyber_score // 2) + (freelance_fit // 3) - (risk_score_value // 3)
    if weighted >= 95:
        return "critical"
    if weighted >= 75:
        return "high"
    if weighted >= 55:
        return "medium"
    return "low"
