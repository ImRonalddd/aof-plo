import pytest
from cards import hand_from_str
from equity import compute_equity


def test_equity_sums_to_one():
    h1 = hand_from_str("AcAdAhAs")  # Quad aces... wait, 4 aces impossible in one hand
    # Use a valid hand
    h1 = hand_from_str("AcAdKcKd")  # AAKK ds
    h2 = hand_from_str("2c3d4h5s")
    equities = compute_equity([list(h1), list(h2)], n_samples=500)
    assert abs(sum(equities) - 1.0) < 0.001


def test_equity_nonnegative():
    h1 = hand_from_str("AcAdKcKd")
    h2 = hand_from_str("2c3d4h5s")
    equities = compute_equity([list(h1), list(h2)], n_samples=500)
    assert all(e >= 0 for e in equities)


def test_strong_hand_favored():
    """AAKK double suited should be a significant favorite vs 2345 rainbow."""
    h1 = hand_from_str("AcAdKcKd")  # AAKK double suited
    h2 = hand_from_str("2c3d4h5s")  # wheel cards rainbow
    # True equity ~54-56%. Threshold 0.52 avoids Monte Carlo variance failures
    # at n_samples=2000 (2-sigma range ≈ 0.528-0.572).
    equities = compute_equity([list(h1), list(h2)], n_samples=2000, seed=42)
    assert equities[0] > 0.52


def test_three_way_equity():
    h1 = hand_from_str("AcAdKcKd")
    h2 = hand_from_str("QcQdJcJd")
    h3 = hand_from_str("TcTd9c9d")
    equities = compute_equity([list(h1), list(h2), list(h3)], n_samples=1000)
    assert abs(sum(equities) - 1.0) < 0.01
    assert equities[0] > equities[2]  # AAKK > TT99


def test_no_card_overlap():
    """Should raise if two hands share cards."""
    h1 = hand_from_str("AcAdKcKd")
    h2 = hand_from_str("AcKsQsJs")  # Ac appears in both
    with pytest.raises(ValueError, match="duplicate"):
        compute_equity([list(h1), list(h2)], n_samples=100)
