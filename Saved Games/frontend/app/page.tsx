"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { FilterPanel } from "../components/FilterPanel";
import { JobCard } from "../components/JobCard";
import { SettingsPanel } from "../components/SettingsPanel";
import { useJobsSocket } from "../hooks/useJobsSocket";
import { fetchJobs, fetchKeywords, fetchPlatformCatalog, fetchPlatformSettings, savePlatformSetting } from "../services/api";
import { Job, Keyword, PlatformCatalog, PlatformSetting, StrategyMode } from "../services/types";

function useBeep() {
  return () => {
    const audioContext = new AudioContext();
    const oscillator = audioContext.createOscillator();
    oscillator.type = "triangle";
    oscillator.frequency.value = 660;
    oscillator.connect(audioContext.destination);
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.12);
  };
}

export default function HomePage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [platforms, setPlatforms] = useState<PlatformSetting[]>([]);
  const [platformCatalog, setPlatformCatalog] = useState<PlatformCatalog[]>([]);
  const [platform, setPlatform] = useState("");
  const [region, setRegion] = useState("");
  const [minMatch, setMinMatch] = useState(0);
  const [maxRisk, setMaxRisk] = useState(100);
  const [securityOnly, setSecurityOnly] = useState(true);
  const [minFreelanceFit, setMinFreelanceFit] = useState(30);
  const [applyingStrategy, setApplyingStrategy] = useState<StrategyMode | null>(null);

  const beep = useBeep();

  const loadJobs = useCallback(async () => {
    const data = await fetchJobs({
      platform,
      region,
      min_match: minMatch,
      max_risk: maxRisk,
      security_only: securityOnly,
      min_freelance_fit: minFreelanceFit
    });
    setJobs(data);
  }, [platform, region, minMatch, maxRisk, securityOnly, minFreelanceFit]);

  const loadKeywords = useCallback(async () => {
    setKeywords(await fetchKeywords());
  }, []);

  const loadPlatforms = useCallback(async () => {
    setPlatforms(await fetchPlatformSettings());
  }, []);

  const loadPlatformCatalog = useCallback(async () => {
    setPlatformCatalog(await fetchPlatformCatalog());
  }, []);

  useEffect(() => {
    void loadJobs();
  }, [loadJobs]);

  useEffect(() => {
    void loadKeywords();
    void loadPlatforms();
    void loadPlatformCatalog();
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      void Notification.requestPermission();
    }
  }, [loadKeywords, loadPlatforms, loadPlatformCatalog]);

  useJobsSocket(
    useCallback(
      (job: Job) => {
        setJobs((prev) => [job, ...prev.filter((j) => j.id !== job.id)].slice(0, 500));
        if (job.score.final_score >= 70) {
          beep();
          if (typeof Notification !== "undefined" && Notification.permission === "granted") {
            new Notification("High-value job", {
              body: `${job.title} (${job.platform}) final score ${job.score.final_score}`
            });
          }
        }
      },
      [beep]
    )
  );

  const highValueCount = useMemo(() => jobs.filter((j) => j.score.final_score >= 70).length, [jobs]);
  const cyberCriticalCount = useMemo(
    () => jobs.filter((j) => j.priority_tier === "critical" || j.priority_tier === "high").length,
    [jobs]
  );

  const applyStrategy = useCallback(
    async (mode: StrategyMode) => {
      if (platforms.length === 0 || platformCatalog.length === 0) return;
      setApplyingStrategy(mode);
      try {
        const activeTiers: Record<StrategyMode, Set<string>> = {
          fast_money: new Set(["fast_money"]),
          cyber_big_win: new Set(["cyber_big_win"]),
          low_competition: new Set(["low_competition"]),
          direct_client: new Set(["direct_client"])
        };

        const selectedTiers = activeTiers[mode];
        const catalogByPlatform = new Map(platformCatalog.map((item) => [item.platform, item]));

        const updates = platforms.map((p) => {
          const meta = catalogByPlatform.get(p.platform);
          const enabled = meta ? selectedTiers.has(meta.tier) : false;
          return savePlatformSetting({ ...p, enabled });
        });

        await Promise.all(updates);

        if (mode === "fast_money") {
          setSecurityOnly(false);
          setMinFreelanceFit(35);
          setMinMatch(20);
          setMaxRisk(60);
          setRegion("");
        }
        if (mode === "cyber_big_win") {
          setSecurityOnly(true);
          setMinFreelanceFit(30);
          setMinMatch(30);
          setMaxRisk(45);
          setRegion("");
        }
        if (mode === "low_competition") {
          setSecurityOnly(true);
          setMinFreelanceFit(25);
          setMinMatch(20);
          setMaxRisk(55);
          setRegion("japan");
        }
        if (mode === "direct_client") {
          setSecurityOnly(true);
          setMinFreelanceFit(40);
          setMinMatch(25);
          setMaxRisk(50);
          setRegion("");
        }

        await loadPlatforms();
        await loadJobs();
      } finally {
        setApplyingStrategy(null);
      }
    },
    [platforms, platformCatalog, loadPlatforms, loadJobs]
  );

  return (
    <main className="mx-auto max-w-7xl p-4 md:p-8">
      <header className="mb-6 rounded-3xl border border-black/10 bg-white/80 p-6 shadow-panel">
        <p className="font-mono text-xs uppercase tracking-widest text-ocean">Personal Freelance Intelligence Dashboard</p>
        <h1 className="mt-2 font-display text-3xl md:text-5xl">Live Intelligence Feed</h1>
        <div className="mt-3 flex flex-wrap gap-2 text-sm">
          <span className="rounded-full bg-ink px-3 py-1 text-sand">Total jobs: {jobs.length}</span>
          <span className="rounded-full bg-moss px-3 py-1 text-white">High value: {highValueCount}</span>
          <span className="rounded-full bg-ember px-3 py-1 text-white">Cyber priority: {cyberCriticalCount}</span>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-1">
          <FilterPanel
            platform={platform}
            region={region}
            minMatch={minMatch}
            maxRisk={maxRisk}
            securityOnly={securityOnly}
            minFreelanceFit={minFreelanceFit}
            onChange={(next) => {
              if (next.platform !== undefined) setPlatform(next.platform);
              if (next.region !== undefined) setRegion(next.region);
              if (next.minMatch !== undefined) setMinMatch(next.minMatch);
              if (next.maxRisk !== undefined) setMaxRisk(next.maxRisk);
              if (next.securityOnly !== undefined) setSecurityOnly(next.securityOnly);
              if (next.minFreelanceFit !== undefined) setMinFreelanceFit(next.minFreelanceFit);
            }}
          />
          <SettingsPanel
            keywords={keywords}
            platforms={platforms}
            catalog={platformCatalog}
            applyingStrategy={applyingStrategy}
            onApplyStrategy={applyStrategy}
            onKeywordsReload={loadKeywords}
            onPlatformsReload={loadPlatforms}
          />
          <button onClick={() => void loadJobs()} className="w-full rounded-xl bg-ember px-4 py-3 font-semibold text-white">
            Refresh Now
          </button>
        </div>

        <section className="space-y-3 lg:col-span-2">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
          {jobs.length === 0 && <div className="panel text-sm text-ink/70">No jobs yet. Collectors are warming up.</div>}
        </section>
      </div>
    </main>
  );
}
