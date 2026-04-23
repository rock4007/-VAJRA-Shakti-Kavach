from app.collectors.api_collectors import (
    FreelancerCollector,
    GitHubIssuesCollector,
    HackerOneCollector,
    RemoteOKCollector,
    UpworkCollector,
)
from app.collectors.base import BaseCollector
from app.collectors.scraping_collectors import (
    BaytCollector,
    CrowdWorksCollector,
    DynamicPassiveCollector,
    IndieHackersCollector,
    LancersCollector,
    LinkedInPlaceholderCollector,
    MaltCollector,
    ManualPlatformCollector,
    PeoplePerHourCollector,
    SeekCollector,
    TradeMeJobsCollector,
    WellfoundCollector,
)


def get_collectors() -> dict[str, BaseCollector]:
    return {
        # Core freelance marketplaces
        "upwork": UpworkCollector(),
        "freelancer": FreelancerCollector(),
        "peopleperhour": PeoplePerHourCollector(),
        "guru": DynamicPassiveCollector("guru", "https://www.guru.com/d/jobs/"),
        "truelancer": DynamicPassiveCollector("truelancer", "https://www.truelancer.com/freelance-jobs"),
        "worknhire": DynamicPassiveCollector("worknhire", "https://worknhire.com/job"),

        # Remote and startup
        "remoteok": RemoteOKCollector(),
        "wellfound": WellfoundCollector(),
        "ycombinator": DynamicPassiveCollector("ycombinator", "https://www.ycombinator.com/jobs"),
        "indiehackers": IndieHackersCollector(),
        "weworkremotely": DynamicPassiveCollector("weworkremotely", "https://weworkremotely.com/remote-jobs"),
        "remotive": DynamicPassiveCollector("remotive", "https://remotive.com/remote-jobs/software-dev"),
        "workingnomads": DynamicPassiveCollector("workingnomads", "https://www.workingnomads.com/jobs"),

        # Cybersecurity and bug bounty
        "hackerone": HackerOneCollector(),
        "bugcrowd": DynamicPassiveCollector("bugcrowd", "https://bugcrowd.com/programs"),
        "yeswehack": DynamicPassiveCollector("yeswehack", "https://yeswehack.com/programs"),
        "intigriti": DynamicPassiveCollector("intigriti", "https://www.intigriti.com/programs"),
        "synack": ManualPlatformCollector("synack"),

        # Open source money
        "github": GitHubIssuesCollector(),
        "gitcoin": DynamicPassiveCollector("gitcoin", "https://explorer.gitcoin.co"),
        "opencollective": DynamicPassiveCollector("opencollective", "https://opencollective.com/discover"),

        # Regional platforms
        "malt": MaltCollector(),
        "yunojuno": DynamicPassiveCollector("yunojuno", "https://www.yunojuno.com/freelancer-jobs"),
        "crowdworks": CrowdWorksCollector(),
        "lancers": LancersCollector(),
        "nabbesh": DynamicPassiveCollector("nabbesh", "https://www.nabbesh.com", "uae"),
        "ureed": DynamicPassiveCollector("ureed", "https://ureed.com/en/projects", "uae"),
        "bayt": BaytCollector(),
        "gulftalent": DynamicPassiveCollector("gulftalent", "https://www.gulftalent.com/jobs", "uae"),
        "seek": SeekCollector(),
        "airtasker": DynamicPassiveCollector("airtasker", "https://www.airtasker.com/jobs", "new zealand"),
        "trademe": TradeMeJobsCollector(),

        # High-end networks and direct channels
        "toptal": ManualPlatformCollector("toptal"),
        "braintrust": DynamicPassiveCollector("braintrust", "https://www.usebraintrust.com/jobs"),
        "gunio": ManualPlatformCollector("gunio"),
        "ateam": DynamicPassiveCollector("ateam", "https://www.a.team"),
        "contra": DynamicPassiveCollector("contra", "https://contra.com/opportunities"),

        # Skill based and learning pipeline
        "topcoder": DynamicPassiveCollector("topcoder", "https://www.topcoder.com/challenges"),
        "codeforces": DynamicPassiveCollector("codeforces", "https://codeforces.com/contests"),
        "leetcode": DynamicPassiveCollector("leetcode", "https://leetcode.com/contest/"),
        "tryhackme": DynamicPassiveCollector("tryhackme", "https://tryhackme.com/hacktivities"),
        "hackthebox": DynamicPassiveCollector("hackthebox", "https://www.hackthebox.com"),

        # Direct client sources
        "linkedin": LinkedInPlaceholderCollector(),
        "reddit": DynamicPassiveCollector("reddit", "https://www.reddit.com/r/forhire/"),
    }
