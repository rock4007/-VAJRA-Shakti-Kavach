import { Job, Keyword, PlatformCatalog, PlatformSetting } from "./types";

const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function fetchJobs(params: {
  platform?: string;
  region?: string;
  min_match?: number;
  max_risk?: number;
  security_only?: boolean;
  min_freelance_fit?: number;
} = {}): Promise<Job[]> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, String(value));
    }
  });

  const response = await fetch(`${base}/api/jobs/?${query.toString()}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch jobs");
  return response.json();
}

export async function fetchKeywords(): Promise<Keyword[]> {
  const response = await fetch(`${base}/api/keywords/`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch keywords");
  return response.json();
}

export async function addKeyword(keyword: string, weight: number): Promise<Keyword> {
  const response = await fetch(`${base}/api/keywords/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keyword, weight })
  });
  if (!response.ok) throw new Error("Failed to add keyword");
  return response.json();
}

export async function deleteKeyword(id: number): Promise<void> {
  const response = await fetch(`${base}/api/keywords/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete keyword");
}

export async function fetchPlatformSettings(): Promise<PlatformSetting[]> {
  const response = await fetch(`${base}/api/settings/platforms`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch platform settings");
  return response.json();
}

export async function fetchPlatformCatalog(): Promise<PlatformCatalog[]> {
  const response = await fetch(`${base}/api/settings/platform-catalog`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch platform catalog");
  return response.json();
}

export async function savePlatformSetting(payload: PlatformSetting): Promise<PlatformSetting> {
  const response = await fetch(`${base}/api/settings/platforms`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error("Failed to save platform setting");
  return response.json();
}
