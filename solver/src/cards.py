"""
Card representation for PLO solver.

Encoding: card = rank * 4 + suit
  rank: 0=2, 1=3, ..., 11=K, 12=A
  suit: 0=c, 1=d, 2=h, 3=s
"""

from itertools import permutations

RANKS = "23456789TJQKA"
SUITS = "cdhs"


def card_from_str(s: str) -> int:
    return RANKS.index(s[0]) * 4 + SUITS.index(s[1])


def card_to_str(card: int) -> str:
    return RANKS[card // 4] + SUITS[card % 4]


def rank(card: int) -> int:
    return card // 4


def suit(card: int) -> int:
    return card % 4


def hand_from_str(s: str) -> tuple[int, ...]:
    """Parse 'AcKsQhJd' into (card_int, ...). Pairs of chars."""
    return tuple(card_from_str(s[i:i+2]) for i in range(0, len(s), 2))


def canonicalize(cards: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    """
    Return suit-isomorphic canonical form of a 4-card PLO hand.

    Algorithm:
      1. Try all 24 suit relabelings (permutations of the 4 suits).
      2. For each relabeling, sort the resulting card integers descending
         (this preserves rank-descending order since card = rank*4 + suit).
      3. Return the lexicographically smallest such tuple.

    Two hands are strategically equivalent preflop iff they share
    a canonical form. This correctly identifies 16,432 distinct PLO4
    hand types from the full 52-card deck.
    """
    best: tuple[int, ...] | None = None
    for perm in permutations(range(4)):
        candidate = tuple(
            sorted(
                (rank(c) * 4 + perm[suit(c)] for c in cards),
                reverse=True,
            )
        )
        if best is None or candidate < best:
            best = candidate
    return best  # type: ignore[return-value]
