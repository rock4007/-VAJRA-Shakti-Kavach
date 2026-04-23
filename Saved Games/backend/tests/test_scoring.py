from app.scoring.keyword_engine import (
    WeightedKeyword,
    compute_match_score,
    compute_region_score,
    compute_risk_score,
    final_score,
)


def test_match_score_weighted_keywords() -> None:
    keywords = [
        WeightedKeyword(keyword="cybersecurity", weight=20),
        WeightedKeyword(keyword="osint", weight=15),
    ]
    score = compute_match_score(
        "Senior Cybersecurity Consultant",
        "Need osint and cybersecurity support for audit",
        keywords,
    )
    assert score >= 80


def test_risk_score_markers() -> None:
    risk = compute_risk_score(
        "Urgent project",
        "Contact me directly on telegram with your gmail",
        budget=10,
    )
    assert risk >= 60


def test_region_and_final_score() -> None:
    region = compute_region_score("Japan")
    total = final_score(match_score=70, region_score=region, risk_score=10)
    assert region == 20
    assert total == 80
