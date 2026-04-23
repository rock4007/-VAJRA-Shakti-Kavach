def suggest_bid(budget: float | None, category_hint: str = "general") -> dict[str, float]:
    if budget is not None and budget > 0:
        return {
            "low": round(budget * 0.7, 2),
            "optimal": round(budget, 2),
            "premium": round(budget * 1.3, 2),
        }

    category_defaults = {
        "cybersecurity": 1200.0,
        "penetration testing": 1800.0,
        "osint": 1000.0,
        "web development": 1500.0,
        "ui ux": 1300.0,
        "cryptography": 2200.0,
        "security audit": 2000.0,
        "compliance": 1700.0,
        "tool development": 1600.0,
        "general": 1200.0,
    }
    base = category_defaults.get(category_hint.lower(), category_defaults["general"])
    return {
        "low": round(base * 0.7, 2),
        "optimal": round(base, 2),
        "premium": round(base * 1.3, 2),
    }
