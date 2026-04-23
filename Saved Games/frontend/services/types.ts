export type Score = {
  match_score: number;
  risk_score: number;
  region_score: number;
  final_score: number;
};

export type BidSuggestion = {
  low: number;
  optimal: number;
  premium: number;
};

export type Job = {
  id: string;
  title: string;
  description: string;
  platform: string;
  url: string;
  budget: number | null;
  currency: string;
  region: string;
  posted_at: string;
  tags: string[];
  score: Score;
  suggested_bid: BidSuggestion;
  cybersecurity_score: number;
  freelance_fit_score: number;
  cyber_category: string;
  priority_tier: "critical" | "high" | "medium" | "low";
};

export type Keyword = {
  id: number;
  keyword: string;
  weight: number;
};

export type PlatformSetting = {
  platform: string;
  enabled: boolean;
  interval_seconds: number;
};

export type PlatformCatalog = {
  platform: string;
  label: string;
  category: string;
  tier: string;
  default_enabled: boolean;
};

export type StrategyMode = "fast_money" | "cyber_big_win" | "low_competition" | "direct_client";
