"use client";

import { useState } from "react";

import { addKeyword, deleteKeyword, savePlatformSetting } from "../services/api";
import { Keyword, PlatformCatalog, PlatformSetting, StrategyMode } from "../services/types";

type Props = {
  keywords: Keyword[];
  platforms: PlatformSetting[];
  catalog: PlatformCatalog[];
  applyingStrategy: StrategyMode | null;
  onApplyStrategy: (mode: StrategyMode) => Promise<void>;
  onKeywordsReload: () => Promise<void>;
  onPlatformsReload: () => Promise<void>;
};

export function SettingsPanel({
  keywords,
  platforms,
  catalog,
  applyingStrategy,
  onApplyStrategy,
  onKeywordsReload,
  onPlatformsReload
}: Props) {
  const [keyword, setKeyword] = useState("");
  const [weight, setWeight] = useState(10);
  const groupedCatalog = catalog.reduce<Record<string, PlatformCatalog[]>>((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  }, {});

  return (
    <section className="panel">
      <h2 className="font-display text-xl">Settings Panel</h2>

      <div className="mt-3 space-y-2">
        <h3 className="text-sm font-semibold">Keywords</h3>
        <div className="flex flex-wrap gap-2">
          {keywords.map((k) => (
            <button
              key={k.id}
              onClick={async () => {
                await deleteKeyword(k.id);
                await onKeywordsReload();
              }}
              className="rounded-full border border-black/15 bg-white px-3 py-1 text-xs hover:border-ember"
            >
              {k.keyword} ({k.weight}) x
            </button>
          ))}
        </div>
        <div className="mt-2 flex gap-2">
          <input
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="new keyword"
            className="w-full rounded-lg border border-black/10 px-3 py-2"
          />
          <input
            type="number"
            value={weight}
            onChange={(e) => setWeight(Number(e.target.value))}
            className="w-24 rounded-lg border border-black/10 px-3 py-2"
          />
          <button
            onClick={async () => {
              if (!keyword.trim()) return;
              await addKeyword(keyword, weight);
              setKeyword("");
              await onKeywordsReload();
            }}
            className="rounded-lg bg-ocean px-3 py-2 text-white"
          >
            Add
          </button>
        </div>
      </div>

      <div className="mt-5 space-y-2">
        <h3 className="text-sm font-semibold">Strategy Mode</h3>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => void onApplyStrategy("fast_money")}
            disabled={applyingStrategy !== null}
            className="rounded-lg bg-ember px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
          >
            Fast Money
          </button>
          <button
            onClick={() => void onApplyStrategy("cyber_big_win")}
            disabled={applyingStrategy !== null}
            className="rounded-lg bg-ocean px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
          >
            Cyber Big Win
          </button>
          <button
            onClick={() => void onApplyStrategy("low_competition")}
            disabled={applyingStrategy !== null}
            className="rounded-lg bg-moss px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
          >
            Low Competition
          </button>
          <button
            onClick={() => void onApplyStrategy("direct_client")}
            disabled={applyingStrategy !== null}
            className="rounded-lg bg-ink px-3 py-2 text-xs font-semibold text-sand disabled:opacity-60"
          >
            Direct Client
          </button>
        </div>
        {applyingStrategy && (
          <div className="text-xs text-ink/70">Applying {applyingStrategy.replaceAll("_", " ")} strategy...</div>
        )}
      </div>

      <div className="mt-5 space-y-2">
        <h3 className="text-sm font-semibold">Platforms</h3>
        <div className="space-y-2">
          {platforms.map((p) => (
            <div key={p.platform} className="flex items-center justify-between rounded-lg border border-black/10 bg-white px-3 py-2">
              <div>
                <div className="font-mono text-xs">{p.platform}</div>
                <div className="text-xs text-ink/60">Every {p.interval_seconds}s</div>
              </div>
              <label className="flex items-center gap-2 text-xs">
                Enabled
                <input
                  type="checkbox"
                  checked={p.enabled}
                  onChange={async (e) => {
                    await savePlatformSetting({ ...p, enabled: e.target.checked });
                    await onPlatformsReload();
                  }}
                />
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-5 space-y-2">
        <h3 className="text-sm font-semibold">Global Opportunity Radar</h3>
        <div className="max-h-72 space-y-3 overflow-auto pr-1">
          {Object.entries(groupedCatalog).map(([category, items]) => (
            <div key={category} className="rounded-lg border border-black/10 bg-white p-2">
              <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-ocean">{category.replaceAll("_", " ")}</div>
              <div className="flex flex-wrap gap-1">
                {items.map((item) => (
                  <span
                    key={item.platform}
                    className="rounded-full border border-black/10 px-2 py-1 text-[11px]"
                    title={`tier: ${item.tier}`}
                  >
                    {item.label}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
