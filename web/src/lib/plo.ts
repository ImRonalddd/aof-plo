// Card encoding mirrors solver/src/cards.py
export const RANKS = "23456789TJQKA";
export const SUITS = "cdhs";
export const RANK_DISPLAY = ["2","3","4","5","6","7","8","9","T","J","Q","K","A"];

export type Card = number; // 0-51
export type Hand = [Card, Card, Card, Card];

export function cardRank(card: Card): number { return Math.floor(card / 4); }
export function cardSuit(card: Card): number { return card % 4; }
export function cardToStr(card: Card): string {
  return RANKS[cardRank(card)] + SUITS[cardSuit(card)];
}

export type SuitStructure = "double-suited" | "single-suited" | "rainbow";

export function getSuitStructure(cards: number[]): SuitStructure {
  const suitCounts = new Map<number, number>();
  for (const c of cards) {
    const s = cardSuit(c);
    suitCounts.set(s, (suitCounts.get(s) ?? 0) + 1);
  }
  const counts = [...suitCounts.values()].sort((a, b) => b - a);
  if (counts[0] === 2 && (counts[1] ?? 0) === 2) return "double-suited";
  if (counts[0] >= 2) return "single-suited";
  return "rainbow";
}
