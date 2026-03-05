"""
CFR+ solver for 4-player AOF PLO.

Infoset key: "{canonical_hand}|{history}"
  - canonical_hand: tuple[int] from cards.canonicalize()
  - history: string of S/F chars representing all actions to date

CFR+ vs vanilla CFR:
  1. regret_sum floored at 0 after each iteration (never negative)
  2. strategy_sum accumulates with linear iteration weight t
"""

import random
import numpy as np

from cards import canonicalize
from game import (
    current_player, is_terminal, legal_actions,
    compute_payoffs, SHOVE, FOLD,
)


class InfoSet:
    def __init__(self, n_actions: int = 2):
        self.regret_sum = np.zeros(n_actions, dtype=np.float64)
        self.strategy_sum = np.zeros(n_actions, dtype=np.float64)

    def get_strategy(self, reach: float, iteration: int) -> np.ndarray:
        """
        Regret matching with CFR+ semantics.
        Uses positive regrets only. Updates strategy_sum with linear weight.
        """
        positive = np.maximum(self.regret_sum, 0.0)
        total = positive.sum()
        if total > 0:
            strategy = positive / total
        else:
            strategy = np.ones(len(positive)) / len(positive)
        # Linear weighting for CFR+ average
        self.strategy_sum += iteration * reach * strategy
        return strategy

    def get_average_strategy(self) -> np.ndarray:
        total = self.strategy_sum.sum()
        if total > 0:
            return self.strategy_sum / total
        return np.ones(len(self.strategy_sum)) / len(self.strategy_sum)


class CFRSolver:
    def __init__(self, n_players: int = 4, equity_samples: int = 500):
        self.n_players = n_players
        self.equity_samples = equity_samples
        self.infosets: dict[str, InfoSet] = {}

    def _get_infoset(self, key: str) -> InfoSet:
        if key not in self.infosets:
            self.infosets[key] = InfoSet(n_actions=2)
        return self.infosets[key]

    def _deal_hands(self, rng: random.Random) -> list[list[int]]:
        deck = list(range(52))
        rng.shuffle(deck)
        return [deck[i * 4:(i + 1) * 4] for i in range(self.n_players)]

    def _cfr(
        self,
        history: str,
        hands: list[list[int]],
        reach_probs: np.ndarray,
        iteration: int,
    ) -> np.ndarray:
        """
        Recursive CFR+ traversal.
        Returns array of shape (n_players,) with expected values from this node.
        """
        if is_terminal(history):
            payoffs = compute_payoffs(history, hands, n_equity_samples=self.equity_samples)
            return np.array(payoffs)

        player = current_player(history)
        actions = legal_actions(history)  # always [SHOVE, FOLD]
        n_actions = len(actions)

        canonical_hand = canonicalize(tuple(hands[player]))
        key = f"{canonical_hand}|{history}"
        infoset = self._get_infoset(key)

        strategy = infoset.get_strategy(reach_probs[player], iteration)

        # Recurse for each action, collecting per-player values
        action_values = np.zeros((n_actions, self.n_players))
        for i, action in enumerate(actions):
            next_history = history + ("S" if action == SHOVE else "F")
            new_reach = reach_probs.copy()
            new_reach[player] *= strategy[i]
            action_values[i] = self._cfr(next_history, hands, new_reach, iteration)

        # Expected node value under current strategy
        node_value = strategy @ action_values  # (n_players,)

        # Counterfactual reach: product of all OTHER players' reach probs
        total_reach = reach_probs.prod()
        player_reach = reach_probs[player]
        cf_reach = total_reach / (player_reach + 1e-300)

        # Update regrets for acting player
        for i in range(n_actions):
            instant_regret = action_values[i][player] - node_value[player]
            infoset.regret_sum[i] += cf_reach * instant_regret

        # CFR+: floor regrets at 0 after each full update
        np.maximum(infoset.regret_sum, 0.0, out=infoset.regret_sum)

        return node_value

    def train(self, n_iterations: int, seed: int | None = None) -> None:
        rng = random.Random(seed)
        reach = np.ones(self.n_players)

        for t in range(1, n_iterations + 1):
            hands = self._deal_hands(rng)
            self._cfr("", hands, reach.copy(), iteration=t)

    def get_average_strategies(self) -> dict[str, np.ndarray]:
        return {
            key: infoset.get_average_strategy()
            for key, infoset in self.infosets.items()
        }
