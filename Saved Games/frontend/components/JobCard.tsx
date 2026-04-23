"use client";

import clsx from "clsx";

import { Job } from "../services/types";

export function JobCard({ job }: { job: Job }) {
  const ageSeconds = Math.floor((Date.now() - new Date(job.posted_at).getTime()) / 1000);
  const isFresh = ageSeconds <= 300;
  const priorityStyle: Record<Job["priority_tier"], string> = {
    critical: "bg-red-600 text-white",
    high: "bg-ember text-white",
    medium: "bg-ocean text-white",
    low: "bg-black/10 text-ink"
  };

  return (
    <article className={clsx("panel transition", isFresh && "flash border-ember/60")}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-display text-lg font-bold">{job.title}</h3>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-ink px-3 py-1 font-mono text-xs text-sand">{job.platform}</span>
          <span className={clsx("rounded-full px-3 py-1 font-mono text-xs", priorityStyle[job.priority_tier])}>
            {job.priority_tier}
          </span>
        </div>
      </div>

      <div className="mt-2 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full bg-ocean/15 px-2 py-1 font-medium text-ocean">{job.cyber_category}</span>
        <span className="rounded-full bg-moss/20 px-2 py-1 font-medium text-moss">Cyber score {job.cybersecurity_score}</span>
        <span className="rounded-full bg-ink/10 px-2 py-1 font-medium text-ink">Freelance fit {job.freelance_fit_score}</span>
      </div>

      <p className="mt-2 line-clamp-3 text-sm text-ink/80">{job.description}</p>

      <div className="mt-3 grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
        <div>
          <div className="font-mono text-xs text-ink/60">Budget</div>
          <div>{job.budget ? `${job.currency} ${job.budget}` : "Not listed"}</div>
        </div>
        <div>
          <div className="font-mono text-xs text-ink/60">Match</div>
          <div className="font-semibold text-ocean">{job.score.match_score}</div>
        </div>
        <div>
          <div className="font-mono text-xs text-ink/60">Risk</div>
          <div className="font-semibold text-ember">{job.score.risk_score}</div>
        </div>
        <div>
          <div className="font-mono text-xs text-ink/60">Final</div>
          <div className="font-semibold text-moss">{job.score.final_score}</div>
        </div>
      </div>

      <div className="mt-3 text-xs text-ink/70">
        Suggested bid: {job.currency} {job.suggested_bid.low} / {job.suggested_bid.optimal} / {job.suggested_bid.premium}
      </div>

      <div className="mt-3 flex items-center justify-between text-xs">
        <span className="font-mono text-ink/60">{new Date(job.posted_at).toLocaleString()}</span>
        <a
          href={job.url}
          target="_blank"
          rel="noreferrer"
          className="rounded-lg bg-ember px-3 py-2 font-medium text-white transition hover:bg-ink"
        >
          Apply Link
        </a>
      </div>
    </article>
  );
}
