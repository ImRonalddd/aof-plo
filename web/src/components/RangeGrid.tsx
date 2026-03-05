"use client";

import { useState, useMemo } from "react";
import GridCell from "./GridCell";
import { RANK_DISPLAY, getSuitStructure } from "@/lib/plo";
import { getStrategy, type RangesData } from "@/lib/ranges";

type SuitFilter = "all" | "double-suited" | "single-suited" | "rainbow";

interface RangeGridProps {
  history: string;
  data: RangesData;
}

// Build representative hands for a top-two rank pair (r1 >= r2)
// and optional side cards (r3 >= r4), filtered by suit structure.
// Returns average shove frequency or null if no data.
function avgShoveFreq(
  r1: number,
  r2: number,
  r3: number | null,
  r4: number | null,
  history: string,
  filter: SuitFilter,
  data: RangesData,
): number | null {
  // Generate a small set of representative 4-card hands
  const ranks = r3 !== null && r4 !== null
    ? [[r1, r2, r3, r4]]
    : generateSideRankPairs(r1, r2).slice(0, 8); // sample up to 8 side pairs

  let total = 0;
  let count = 0;

  for (const [a, b, c, d] of ranks) {
    // Try a few suit combos
    for (const suits of representativeSuits()) {
      const cards = [a * 4 + suits[0], b * 4 + suits[1], c * 4 + suits[2], d * 4 + suits[3]];
      if (new Set(cards).size !== 4) continue;

      const structure = getSuitStructure(cards);
      if (filter !== "all" && structure !== filter) continue;

      // Build canonical key: sort by card value desc (rank*4+suit desc)
      // to match Python's canonicalize output
      const canon = buildCanonicalKey(cards);
      const strat = getStrategy(data, canon, history);
      if (strat) {
        total += strat[0];
        count++;
        if (count >= 4) break; // enough samples per rank combo
      }
    }
    if (count >= 12) break;
  }

  return count > 0 ? total / count : null;
}

// Generate side rank pairs for a given top-two combo (r1, r2)
function generateSideRankPairs(r1: number, r2: number): [number, number, number, number][] {
  const pairs: [number, number, number, number][] = [];
  for (let r3 = 12; r3 >= 0; r3--) {
    for (let r4 = r3; r4 >= 0; r4--) {
      pairs.push([r1, r2, r3, r4]);
    }
  }
  return pairs;
}

// Representative suit combinations to sample
function representativeSuits(): number[][] {
  // [suit for card0, suit for card1, suit for card2, suit for card3]
  return [
    [0, 0, 1, 1], // double suited: top two same suit, bottom two same suit
    [0, 1, 0, 1], // double suited: alternating
    [0, 0, 1, 2], // single suited: top two same suit
    [0, 1, 2, 3], // rainbow
    [0, 1, 2, 0], // single suited: 3 of one suit isn't standard but include
  ];
}

// Build canonical key matching Python's canonicalize() output
// Python: sort by rank DESC (suit as tiebreaker), then relabel suits via S4 minimum
// For lookup purposes: just sort descending by card int and build the tuple string
function buildCanonicalKey(cards: number[]): string {
  // Try all 24 suit permutations, pick lex-min (matches Python implementation)
  const perms = generateSuitPerms();
  let best: number[] | null = null;
  for (const perm of perms) {
    const relabeled = cards.map(c => Math.floor(c / 4) * 4 + perm[c % 4]);
    const sorted = [...relabeled].sort((a, b) => b - a);
    if (best === null || lexLess(sorted, best)) best = sorted;
  }
  return `(${best!.join(", ")})`;
}

const SUIT_PERMS = (() => {
  const perms: number[][] = [];
  const arr = [0, 1, 2, 3];
  function permute(a: number[], l: number) {
    if (l === a.length) { perms.push([...a]); return; }
    for (let i = l; i < a.length; i++) {
      [a[l], a[i]] = [a[i], a[l]];
      permute(a, l + 1);
      [a[l], a[i]] = [a[i], a[l]];
    }
  }
  permute(arr, 0);
  return perms;
})();

function generateSuitPerms() { return SUIT_PERMS; }

function lexLess(a: number[], b: number[]): boolean {
  for (let i = 0; i < a.length; i++) {
    if (a[i] < b[i]) return true;
    if (a[i] > b[i]) return false;
  }
  return false;
}

export default function RangeGrid({ history, data }: RangeGridProps) {
  const [selectedCell, setSelectedCell] = useState<[number, number] | null>(null);
  const [suitFilter, setSuitFilter] = useState<SuitFilter>("all");

  const filters: { key: SuitFilter; label: string }[] = [
    { key: "all", label: "All" },
    { key: "double-suited", label: "DS" },
    { key: "single-suited", label: "SS" },
    { key: "rainbow", label: "Rainbow" },
  ];

  // Pre-compute outer grid frequencies
  const outerFreqs = useMemo(() => {
    const grid: (number | null)[][] = [];
    for (let ri = 0; ri < 13; ri++) {
      grid[ri] = [];
      for (let ci = 0; ci < 13; ci++) {
        const r1 = 12 - ri;
        const r2 = 12 - ci;
        if (r2 > r1) { grid[ri][ci] = null; continue; }
        grid[ri][ci] = avgShoveFreq(r1, r2, null, null, history, suitFilter, data);
      }
    }
    return grid;
  }, [history, suitFilter, data]);

  return (
    <div className="flex flex-col gap-4">
      {/* Suit filter */}
      <div className="flex gap-2">
        {filters.map(f => (
          <button
            key={f.key}
            onClick={() => setSuitFilter(f.key)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              suitFilter === f.key
                ? "bg-yellow-500 text-black"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Legend */}
      <div className="flex gap-6 text-xs text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className="w-4 h-3 rounded-sm bg-red-600 inline-block" />Shove 100%
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-4 h-3 rounded-sm bg-gray-900 border border-gray-700 inline-block" />Fold 100%
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-4 h-3 rounded-sm inline-block" style={{ background: "linear-gradient(to right,#dc2626 60%,#111827 60%)" }} />Mixed
        </span>
      </div>

      {/* Outer 13x13 grid */}
      <div>
        <p className="text-gray-600 text-xs mb-2">Click a cell to drill down into side cards</p>
        <div className="inline-grid gap-px" style={{ gridTemplateColumns: "auto repeat(13, auto)" }}>
          <div className="w-5" />
          {Array.from({ length: 13 }, (_, ci) => (
            <div key={ci} className="w-9 h-5 flex items-center justify-center text-[10px] text-gray-500 font-mono">
              {RANK_DISPLAY[12 - ci]}
            </div>
          ))}
          {Array.from({ length: 13 }, (_, ri) => {
            const r1 = 12 - ri;
            return (
              <div key={ri} className="contents">
                <div className="w-5 flex items-center justify-center text-[10px] text-gray-500 font-mono">
                  {RANK_DISPLAY[r1]}
                </div>
                {Array.from({ length: 13 }, (_, ci) => {
                  const r2 = 12 - ci;
                  if (r2 > r1) return <div key={ci} className="w-9 h-9" />;
                  const freq = outerFreqs[ri]?.[ci] ?? null;
                  const isSelected = selectedCell?.[0] === r1 && selectedCell?.[1] === r2;
                  return (
                    <GridCell
                      key={ci}
                      shoveFreq={freq}
                      label={r1 === r2 ? `${RANK_DISPLAY[r1]}${RANK_DISPLAY[r1]}` : `${RANK_DISPLAY[r1]}${RANK_DISPLAY[r2]}`}
                      isSelected={isSelected}
                      onClick={() => setSelectedCell(isSelected ? null : [r1, r2])}
                    />
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>

      {/* Inner grid for selected top-two ranks */}
      {selectedCell && (
        <InnerGrid
          r1={selectedCell[0]}
          r2={selectedCell[1]}
          history={history}
          suitFilter={suitFilter}
          data={data}
        />
      )}
    </div>
  );
}

function InnerGrid({
  r1, r2, history, suitFilter, data,
}: {
  r1: number;
  r2: number;
  history: string;
  suitFilter: SuitFilter;
  data: RangesData;
}) {
  return (
    <div>
      <p className="text-gray-500 text-xs mb-2">
        Side cards for <span className="text-white font-mono">{RANK_DISPLAY[r1]}{RANK_DISPLAY[r2]}</span> — select which two remaining cards complete the hand
      </p>
      <div className="inline-grid gap-px" style={{ gridTemplateColumns: "auto repeat(13, auto)" }}>
        <div className="w-5" />
        {Array.from({ length: 13 }, (_, ci) => (
          <div key={ci} className="w-7 h-5 flex items-center justify-center text-[9px] text-gray-500 font-mono">
            {RANK_DISPLAY[12 - ci]}
          </div>
        ))}
        {Array.from({ length: 13 }, (_, ri) => {
          const r3 = 12 - ri;
          return (
            <div key={ri} className="contents">
              <div className="w-5 flex items-center justify-center text-[9px] text-gray-500 font-mono">
                {RANK_DISPLAY[r3]}
              </div>
              {Array.from({ length: 13 }, (_, ci) => {
                const r4 = 12 - ci;
                if (r4 > r3) return <div key={ci} className="w-7 h-7" />;
                const freq = avgShoveFreq(r1, r2, r3, r4, history, suitFilter, data);
                return (
                  <GridCell
                    key={ci}
                    shoveFreq={freq}
                    label={`${RANK_DISPLAY[r3]}${RANK_DISPLAY[r4]}`}
                    size="sm"
                  />
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}
