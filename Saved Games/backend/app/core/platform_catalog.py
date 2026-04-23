PLATFORM_CATALOG: dict[str, dict[str, str | bool]] = {
    # Core freelancing marketplaces
    "upwork": {"category": "core_freelance", "label": "Upwork", "default_enabled": True, "tier": "fast_money"},
    "freelancer": {"category": "core_freelance", "label": "Freelancer", "default_enabled": True, "tier": "fast_money"},
    "peopleperhour": {"category": "core_freelance", "label": "PeoplePerHour", "default_enabled": True, "tier": "fast_money"},
    "guru": {"category": "core_freelance", "label": "Guru", "default_enabled": True, "tier": "fast_money"},
    "truelancer": {"category": "core_freelance", "label": "Truelancer", "default_enabled": True, "tier": "fast_money"},
    "worknhire": {"category": "core_freelance", "label": "WorkNHire", "default_enabled": False, "tier": "fast_money"},

    # High-end low competition
    "toptal": {"category": "high_end_network", "label": "Toptal", "default_enabled": False, "tier": "high_value"},
    "braintrust": {"category": "high_end_network", "label": "Braintrust", "default_enabled": True, "tier": "high_value"},
    "gunio": {"category": "high_end_network", "label": "Gun.io", "default_enabled": False, "tier": "high_value"},
    "ateam": {"category": "high_end_network", "label": "A.Team", "default_enabled": False, "tier": "high_value"},
    "contra": {"category": "high_end_network", "label": "Contra", "default_enabled": True, "tier": "high_value"},

    # Cybersecurity bug bounty
    "hackerone": {"category": "cyber_bounty", "label": "HackerOne", "default_enabled": True, "tier": "cyber_big_win"},
    "bugcrowd": {"category": "cyber_bounty", "label": "Bugcrowd", "default_enabled": True, "tier": "cyber_big_win"},
    "synack": {"category": "cyber_bounty", "label": "Synack", "default_enabled": False, "tier": "cyber_big_win"},
    "yeswehack": {"category": "cyber_bounty", "label": "YesWeHack", "default_enabled": True, "tier": "cyber_big_win"},
    "intigriti": {"category": "cyber_bounty", "label": "Intigriti", "default_enabled": True, "tier": "cyber_big_win"},

    # Open source money
    "github": {"category": "open_source_money", "label": "GitHub", "default_enabled": True, "tier": "direct_client"},
    "gitcoin": {"category": "open_source_money", "label": "Gitcoin", "default_enabled": True, "tier": "high_value"},
    "opencollective": {"category": "open_source_money", "label": "Open Collective", "default_enabled": True, "tier": "high_value"},

    # Startup and direct client
    "wellfound": {"category": "startup_direct", "label": "Wellfound", "default_enabled": True, "tier": "direct_client"},
    "ycombinator": {"category": "startup_direct", "label": "Y Combinator Jobs", "default_enabled": True, "tier": "direct_client"},
    "indiehackers": {"category": "startup_direct", "label": "Indie Hackers", "default_enabled": True, "tier": "direct_client"},

    # Remote job boards
    "remoteok": {"category": "remote_boards", "label": "Remote OK", "default_enabled": True, "tier": "fast_money"},
    "weworkremotely": {"category": "remote_boards", "label": "We Work Remotely", "default_enabled": True, "tier": "fast_money"},
    "remotive": {"category": "remote_boards", "label": "Remotive", "default_enabled": True, "tier": "fast_money"},
    "workingnomads": {"category": "remote_boards", "label": "Working Nomads", "default_enabled": True, "tier": "fast_money"},

    # Japan
    "crowdworks": {"category": "region_japan", "label": "CrowdWorks", "default_enabled": True, "tier": "low_competition"},
    "lancers": {"category": "region_japan", "label": "Lancers", "default_enabled": True, "tier": "low_competition"},

    # UAE and Middle East
    "nabbesh": {"category": "region_uae", "label": "Nabbesh", "default_enabled": True, "tier": "low_competition"},
    "ureed": {"category": "region_uae", "label": "Ureed", "default_enabled": True, "tier": "low_competition"},
    "bayt": {"category": "region_uae", "label": "Bayt", "default_enabled": True, "tier": "low_competition"},
    "gulftalent": {"category": "region_uae", "label": "GulfTalent", "default_enabled": True, "tier": "low_competition"},

    # Europe UK
    "malt": {"category": "region_europe", "label": "Malt", "default_enabled": True, "tier": "high_value"},
    "yunojuno": {"category": "region_europe", "label": "YunoJuno", "default_enabled": True, "tier": "high_value"},

    # Australia New Zealand
    "seek": {"category": "region_anz", "label": "Seek", "default_enabled": True, "tier": "low_competition"},
    "airtasker": {"category": "region_anz", "label": "Airtasker", "default_enabled": True, "tier": "low_competition"},
    "trademe": {"category": "region_anz", "label": "Trade Me Jobs", "default_enabled": True, "tier": "low_competition"},

    # Competitions and pipeline
    "topcoder": {"category": "skill_money", "label": "Topcoder", "default_enabled": True, "tier": "high_value"},
    "codeforces": {"category": "skill_money", "label": "Codeforces", "default_enabled": False, "tier": "pipeline"},
    "leetcode": {"category": "skill_money", "label": "LeetCode", "default_enabled": False, "tier": "pipeline"},
    "tryhackme": {"category": "pipeline_learning", "label": "TryHackMe", "default_enabled": False, "tier": "pipeline"},
    "hackthebox": {"category": "pipeline_learning", "label": "Hack The Box", "default_enabled": False, "tier": "pipeline"},

    # Direct client channels
    "linkedin": {"category": "direct_client", "label": "LinkedIn", "default_enabled": False, "tier": "direct_client"},
    "reddit": {"category": "direct_client", "label": "Reddit", "default_enabled": True, "tier": "direct_client"},
}


def get_platform_catalog() -> dict[str, dict[str, str | bool]]:
    return PLATFORM_CATALOG
