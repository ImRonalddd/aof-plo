"use client";

import { useState, useEffect } from "react";
import ActionTree from "@/components/ActionTree";
import RangeGrid from "@/components/RangeGrid";
import { loadRanges, currentPosition, type RangesData } from "@/lib/ranges";

export default function Home() {
  const [history, setHistory] = useState<string>("");
  const [data, setData] = useState<RangesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRanges()
      .then(setData)
      .catch(e => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const handleAction = (action: "S" | "F") => {
    if (history.length < 4) setHistory(h => h + action);
  };

  const handleBack = () => setHistory(h => h.slice(0, -1));

  const displayPos = currentPosition(history);

  return (
    <main className="max-w-5xl mx-auto px-4 py-8 flex flex-col gap-8">
      {/* Header */}
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-xl font-bold tracking-tight">AOF PLO Range Viewer</h1>
        <p className="text-gray-500 text-sm mt-0.5">4-max · 5BB deep · All-In-Or-Fold · Preflop GTO</p>
        {data && (
          <p className="text-gray-700 text-xs mt-1">
            {data.meta.iterations.toLocaleString()} CFR+ iterations · {data.meta.n_infosets.toLocaleString()} infosets · {data.meta.elapsed_seconds}s solve time
          </p>
        )}
      </div>

      {/* Action Tree */}
      <section>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Action Sequence</h2>
        <ActionTree history={history} onAction={handleAction} onBack={handleBack} />
      </section>

      {/* Range Display */}
      {loading && (
        <div className="text-gray-500 text-sm">Loading ranges...</div>
      )}
      {error && (
        <div className="text-red-500 text-sm">Error: {error}</div>
      )}
      {data && history.length < 4 && (
        <section>
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-1">
            {displayPos} Strategy
          </h2>
          <p className="text-gray-600 text-xs mb-3">
            Showing shove frequency · Red = shove · Dark = fold
          </p>
          <RangeGrid history={history} data={data} />
        </section>
      )}
      {data && history.length === 4 && (
        <div className="text-gray-600 text-sm italic">Terminal node — all players have acted. Press ← Back to explore.</div>
      )}
    </main>
  );
}
