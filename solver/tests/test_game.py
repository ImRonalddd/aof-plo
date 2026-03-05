from game import (
    current_player, is_terminal, legal_actions,
    compute_payoffs, has_active_shove,
    SHOVE, FOLD, PLAYERS, BLINDS, STACK,
)
from cards import hand_from_str

CO, BTN, SB, BB = 0, 1, 2, 3


def test_player_order():
    assert current_player("") == CO
    assert current_player("S") == BTN
    assert current_player("SS") == SB
    assert current_player("SSS") == BB


def test_terminal_at_length_4():
    assert is_terminal("SSSS")
    assert is_terminal("FFFF")
    assert is_terminal("SFSF")


def test_not_terminal_less_than_4():
    assert not is_terminal("")
    assert not is_terminal("SSS")


def test_legal_actions_always_two():
    # Always exactly 2 actions regardless of history
    assert legal_actions("") == [SHOVE, FOLD]
    assert legal_actions("S") == [SHOVE, FOLD]
    assert legal_actions("FF") == [SHOVE, FOLD]
    assert legal_actions("SSS") == [SHOVE, FOLD]


def test_has_active_shove():
    assert not has_active_shove("")
    assert has_active_shove("S")
    assert has_active_shove("FS")
    assert not has_active_shove("FF")
    assert not has_active_shove("FFF")


def test_constants():
    assert SHOVE == 0
    assert FOLD == 1
    assert STACK == 5.0
    assert BLINDS[0] == 0.0  # CO no blind
    assert BLINDS[1] == 0.0  # BTN no blind
    assert BLINDS[2] == 0.5  # SB
    assert BLINDS[3] == 1.0  # BB


def test_payoffs_co_wins_uncontested():
    """CO shoves, BTN/SB/BB all fold."""
    history = "SFFF"  # CO=S, BTN=F, SB=F, BB=F
    hands = [
        list(hand_from_str("AcAdKcKd")),  # CO (shoves)
        list(hand_from_str("2c3d4h5s")),  # BTN (folds, no blind)
        list(hand_from_str("6c7d8h9s")),  # SB (folds, loses 0.5BB)
        list(hand_from_str("QcQdJcJd")),  # BB (folds, loses 1BB)
    ]
    payoffs = compute_payoffs(history, hands, n_equity_samples=100)
    # CO wins the pot = 5 + 0 + 0.5 + 1 = 6.5BB, net = 6.5 - 5 = +1.5BB
    assert abs(payoffs[0] - 1.5) < 0.01
    # BTN folded, no blind posted
    assert abs(payoffs[1] - 0.0) < 0.01
    # SB lost blind
    assert abs(payoffs[2] - (-0.5)) < 0.01
    # BB lost blind
    assert abs(payoffs[3] - (-1.0)) < 0.01


def test_payoffs_heads_up_co_vs_bb():
    """CO shoves, BTN folds, SB folds, BB calls."""
    history = "SFFS"  # CO=S, BTN=F, SB=F, BB=S(call)
    hands = [
        list(hand_from_str("AcAdKcKd")),  # CO: AAKK ds (strong)
        list(hand_from_str("2c3d4h5s")),  # BTN: folded
        list(hand_from_str("6c7d8h9s")),  # SB: folded
        list(hand_from_str("QcQdJcJd")),  # BB: QQJJ ds
    ]
    payoffs = compute_payoffs(history, hands, n_equity_samples=2000)
    # CO: 5BB in, BB: 5BB in. Pot = 10BB + 0.5BB SB dead = 10.5BB
    # BTN lost nothing (no blind posted, folded before shoving)
    assert abs(payoffs[1] - 0.0) < 0.01
    # SB lost their blind
    assert abs(payoffs[2] - (-0.5)) < 0.01
    # CO + BB payoffs sum to 0.5 (the SB dead money, net of their combined 10BB investment)
    assert abs(payoffs[0] + payoffs[3] - 0.5) < 0.5  # within Monte Carlo noise


def test_payoffs_nobody_shoves():
    """FFFF - nobody shoves, return negative blinds."""
    history = "FFFF"
    hands = [
        list(hand_from_str("AcAdKcKd")),
        list(hand_from_str("2c3d4h5s")),
        list(hand_from_str("6c7d8h9s")),
        list(hand_from_str("QcQdJcJd")),
    ]
    payoffs = compute_payoffs(history, hands, n_equity_samples=100)
    assert abs(payoffs[0] - 0.0) < 0.01   # CO: no blind
    assert abs(payoffs[1] - 0.0) < 0.01   # BTN: no blind
    assert abs(payoffs[2] - (-0.5)) < 0.01  # SB loses blind
    assert abs(payoffs[3] - (-1.0)) < 0.01  # BB loses blind
