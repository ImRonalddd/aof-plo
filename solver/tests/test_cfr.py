import numpy as np
from cfr import InfoSet, CFRSolver


def test_infoset_uniform_when_no_regret():
    infoset = InfoSet(n_actions=2)
    strategy = infoset.get_strategy(reach=1.0, iteration=1)
    assert abs(strategy[0] - 0.5) < 1e-9
    assert abs(strategy[1] - 0.5) < 1e-9


def test_infoset_follows_positive_regret():
    infoset = InfoSet(n_actions=2)
    infoset.regret_sum[0] = 10.0
    infoset.regret_sum[1] = 0.0
    strategy = infoset.get_strategy(reach=1.0, iteration=1)
    assert strategy[0] > 0.99


def test_infoset_cfr_plus_floors_at_zero():
    """CFR+: negative regrets are treated as zero in strategy computation."""
    infoset = InfoSet(n_actions=2)
    infoset.regret_sum[0] = -100.0
    infoset.regret_sum[1] = 1.0
    strategy = infoset.get_strategy(reach=1.0, iteration=1)
    assert strategy[1] > 0.99


def test_infoset_average_strategy():
    infoset = InfoSet(n_actions=2)
    infoset.strategy_sum[0] = 8.0
    infoset.strategy_sum[1] = 2.0
    avg = infoset.get_average_strategy()
    assert abs(avg[0] - 0.8) < 1e-9
    assert abs(avg[1] - 0.2) < 1e-9


def test_infoset_strategy_sum_updates():
    """get_strategy accumulates into strategy_sum with linear iteration weighting."""
    infoset = InfoSet(n_actions=2)
    # Uniform strategy, reach=1.0, iteration=3 -> adds 3 * 1.0 * [0.5, 0.5] = [1.5, 1.5]
    infoset.get_strategy(reach=1.0, iteration=3)
    assert abs(infoset.strategy_sum[0] - 1.5) < 1e-9
    assert abs(infoset.strategy_sum[1] - 1.5) < 1e-9


def test_solver_initializes():
    solver = CFRSolver(n_players=4)
    assert solver.infosets == {}


def test_solver_trains_smoke():
    """Solver runs 10 iterations without error."""
    solver = CFRSolver(n_players=4, equity_samples=20)
    solver.train(n_iterations=10, seed=42)
    assert len(solver.infosets) > 0


def test_solver_strategies_are_valid():
    """After training, all average strategies sum to 1.0."""
    solver = CFRSolver(n_players=4, equity_samples=50)
    solver.train(n_iterations=50, seed=42)
    for key, infoset in solver.infosets.items():
        avg = infoset.get_average_strategy()
        assert abs(sum(avg) - 1.0) < 1e-6, f"Invalid strategy at {key}: {avg}"


def test_solver_infoset_keys_format():
    """Infoset keys must be in format 'tuple|history'."""
    solver = CFRSolver(n_players=4, equity_samples=20)
    solver.train(n_iterations=5, seed=1)
    for key in solver.infosets.keys():
        assert "|" in key, f"Missing pipe in key: {key}"
        hand_part, history_part = key.split("|", 1)
        assert history_part in ["", "S", "F", "SS", "SF", "FS", "FF",
                                  "SSS", "SSF", "SFS", "SFF", "FSS", "FSF", "FFS", "FFF"]


def test_solver_bb_shoves_premium_vs_no_action():
    """
    After training, BB facing FFF (nobody acted) should shove premium hands often.
    Run more iterations so it has a chance to learn.
    """
    solver = CFRSolver(n_players=4, equity_samples=100)
    solver.train(n_iterations=300, seed=42)
    strategies = solver.get_average_strategies()

    from cards import hand_from_str, canonicalize
    premium = canonicalize(hand_from_str("AcAdKcKd"))
    key = f"{premium}|FFF"

    if key in strategies:
        shove_freq = strategies[key][0]
        # BB should shove AAKK when it gets to act after FFF -- at 5BB it's a clear shove
        assert shove_freq > 0.5, f"BB should shove AAKK often vs FFF, got {shove_freq:.2f}"
