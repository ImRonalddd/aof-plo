"""
Monte Carlo PLO equity calculator using phevaluator.

PLO rules: each player must use exactly 2 of their 4 hole cards
and exactly 3 of the 5 board cards. phevaluator handles this
automatically when given 4 hole cards + 5 board cards.
"""

import random
from phevaluator import evaluate_omaha_cards
from cards import card_to_str


def compute_equity(
    hands: list[list[int]],
    n_samples: int = 5000,
    seed: int | None = None,
) -> list[float]:
    """
    Monte Carlo equity for 2-4 PLO hands (no board cards known).

    Args:
        hands: List of hands, each a list of 4 card ints.
        n_samples: Number of random 5-card boards to simulate.
        seed: Optional RNG seed for reproducibility.

    Returns:
        List of equity fractions (sums to 1.0).

    Raises:
        ValueError: If any two hands share a card.
    """
    if seed is not None:
        random.seed(seed)

    all_hole_cards: list[int] = []
    for hand in hands:
        all_hole_cards.extend(hand)

    if len(all_hole_cards) != len(set(all_hole_cards)):
        raise ValueError("Hands have duplicate cards")

    deck = [c for c in range(52) if c not in all_hole_cards]

    wins = [0.0] * len(hands)

    for _ in range(n_samples):
        board = random.sample(deck, 5)
        board_strs = [card_to_str(c) for c in board]

        hand_ranks = []
        for hand in hands:
            hole_strs = [card_to_str(c) for c in hand]
            # evaluate_omaha_cards(h0, h1, h2, h3, b0, b1, b2, b3, b4)
            # Lower rank = stronger hand in phevaluator
            r = evaluate_omaha_cards(
                hole_strs[0], hole_strs[1], hole_strs[2], hole_strs[3],
                board_strs[0], board_strs[1], board_strs[2], board_strs[3], board_strs[4],
            )
            hand_ranks.append(r)

        best = min(hand_ranks)
        winners = [i for i, r in enumerate(hand_ranks) if r == best]
        share = 1.0 / len(winners)
        for w in winners:
            wins[w] += share

    return [w / n_samples for w in wins]
