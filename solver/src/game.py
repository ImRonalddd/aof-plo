"""
4-player AOF PLO game tree: CO -> BTN -> SB -> BB.

History: string of length 0-4. Each char: S (shove/call) or F (fold).
Position = len(history): 0=CO, 1=BTN, 2=SB, 3=BB.
Terminal: len(history) == 4.
"""

from equity import compute_equity

SHOVE = 0
FOLD = 1

PLAYERS = ["CO", "BTN", "SB", "BB"]

# How much each player loses if they fold (their blind posting)
BLINDS = [0.0, 0.0, 0.5, 1.0]
STACK = 5.0  # Total investment when a player shoves


def current_player(history: str) -> int:
    return len(history)


def is_terminal(history: str) -> bool:
    return len(history) == 4


def has_active_shove(history: str) -> bool:
    return "S" in history


def legal_actions(history: str) -> list[int]:
    """Always [SHOVE, FOLD] — meaning changes if facing a shove, but options don't."""
    return [SHOVE, FOLD]


def compute_payoffs(
    history: str,
    hands: list[list[int]],
    n_equity_samples: int = 5000,
) -> list[float]:
    """
    Compute each player's net EV at a terminal node.

    Returns list of 4 floats: net gain/loss in BB.
    """
    assert is_terminal(history), f"Not terminal: {history!r}"
    assert len(hands) == 4

    # Edge case: nobody shoved -> each player loses their blind
    if not has_active_shove(history):
        return [-BLINDS[i] for i in range(4)]

    # Determine each player's investment and showdown eligibility
    invested = [0.0] * 4
    in_showdown = [False] * 4

    for i, action in enumerate(history):
        if action == "S":
            invested[i] = STACK
            in_showdown[i] = True
        else:  # F
            invested[i] = BLINDS[i]

    total_pot = sum(invested)

    # Compute equity among showdown players
    showdown_indices = [i for i in range(4) if in_showdown[i]]
    showdown_hands = [hands[i] for i in showdown_indices]
    equities = compute_equity(showdown_hands, n_samples=n_equity_samples)

    # Net payoff = equity share of pot - what you put in
    payoffs = [-invested[i] for i in range(4)]
    for idx, equity in zip(showdown_indices, equities):
        payoffs[idx] += equity * total_pot

    return payoffs
