export type ActionFrequency = [number, number]; // [shove_prob, fold_prob]

export interface RangesMeta {
  iterations: number;
  equity_samples: number;
  n_infosets: number;
  elapsed_seconds: number;
}

export interface RangesData {
  meta: RangesMeta;
  strategies: Record<string, ActionFrequency>;
}

// Singleton cache
let cachedData: RangesData | null = null;

export async function loadRanges(): Promise<RangesData> {
  if (cachedData) return cachedData;
  const res = await fetch("/ranges.json");
  if (!res.ok) throw new Error(`Failed to load ranges.json: ${res.status}`);
  cachedData = await res.json() as RangesData;
  return cachedData;
}

export function getStrategy(
  data: RangesData,
  canonicalHand: string,
  history: string,
): ActionFrequency | null {
  return data.strategies[`${canonicalHand}|${history}`] ?? null;
}

export const POSITION_NAMES = ["CO", "BTN", "SB", "BB"];
export const ALL_HISTORIES = [
  "", "S", "F",
  "SS", "SF", "FS", "FF",
  "SSS", "SSF", "SFS", "SFF", "FSS", "FSF", "FFS", "FFF",
];

export function currentPosition(history: string): string {
  return POSITION_NAMES[history.length] ?? "—";
}
