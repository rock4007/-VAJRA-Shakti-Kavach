"use client";

type FilterProps = {
  platform: string;
  region: string;
  minMatch: number;
  maxRisk: number;
  securityOnly: boolean;
  minFreelanceFit: number;
  onChange: (next: Partial<{ platform: string; region: string; minMatch: number; maxRisk: number; securityOnly: boolean; minFreelanceFit: number }>) => void;
};

export function FilterPanel({ platform, region, minMatch, maxRisk, securityOnly, minFreelanceFit, onChange }: FilterProps) {
  return (
    <section className="panel">
      <h2 className="font-display text-xl">Filter Panel</h2>
      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
        <label className="text-sm">
          Platform
          <input
            value={platform}
            onChange={(e) => onChange({ platform: e.target.value })}
            placeholder="upwork / remoteok"
            className="mt-1 w-full rounded-lg border border-black/10 bg-white px-3 py-2"
          />
        </label>
        <label className="text-sm">
          Region
          <input
            value={region}
            onChange={(e) => onChange({ region: e.target.value })}
            placeholder="japan / uae / new zealand"
            className="mt-1 w-full rounded-lg border border-black/10 bg-white px-3 py-2"
          />
        </label>
      </div>
      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
        <label className="text-sm">
          Minimum Match: {minMatch}
          <input
            type="range"
            min={0}
            max={100}
            value={minMatch}
            onChange={(e) => onChange({ minMatch: Number(e.target.value) })}
            className="mt-1 w-full"
          />
        </label>
        <label className="text-sm">
          Maximum Risk: {maxRisk}
          <input
            type="range"
            min={0}
            max={100}
            value={maxRisk}
            onChange={(e) => onChange({ maxRisk: Number(e.target.value) })}
            className="mt-1 w-full"
          />
        </label>
      </div>
      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
        <label className="text-sm">
          Minimum Freelance Fit: {minFreelanceFit}
          <input
            type="range"
            min={0}
            max={100}
            value={minFreelanceFit}
            onChange={(e) => onChange({ minFreelanceFit: Number(e.target.value) })}
            className="mt-1 w-full"
          />
        </label>
        <label className="mt-6 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={securityOnly}
            onChange={(e) => onChange({ securityOnly: e.target.checked })}
          />
          Cybersecurity jobs only
        </label>
      </div>
    </section>
  );
}
