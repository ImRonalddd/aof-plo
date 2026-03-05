from cards import (
    card_from_str, card_to_str, rank, suit,
    canonicalize, hand_from_str, RANKS, SUITS
)


def test_card_encoding():
    # 2c = rank 0, suit 0 → card 0
    assert card_from_str("2c") == 0
    # Ac = rank 12, suit 0 → card 48
    assert card_from_str("Ac") == 48
    # As = rank 12, suit 3 → card 51
    assert card_from_str("As") == 51


def test_card_to_str_roundtrip():
    for c in range(52):
        assert card_from_str(card_to_str(c)) == c


def test_rank_suit():
    assert rank(card_from_str("Kh")) == 11   # K = rank 11
    assert suit(card_from_str("Kh")) == 2    # h = suit 2


def test_hand_from_str():
    hand = hand_from_str("AcKcQhJh")
    assert len(hand) == 4
    assert card_from_str("Ac") in hand


def test_canonicalize_suit_isomorphism():
    # AsKsQhJh and AdKdQcJc should be the same canonical hand
    hand1 = hand_from_str("AsKsQhJh")
    hand2 = hand_from_str("AdKdQcJc")
    assert canonicalize(hand1) == canonicalize(hand2)


def test_canonicalize_rainbow_distinct_from_suited():
    hand_ds = hand_from_str("AsKsQhJh")   # double suited
    hand_rb = hand_from_str("AsKdQhJc")   # rainbow
    assert canonicalize(hand_ds) != canonicalize(hand_rb)


def test_canonicalize_sorted_by_rank_desc():
    # Input in any order → canonical is rank-descending
    hand = hand_from_str("JhAsQhKs")  # scrambled order
    canon = canonicalize(hand)
    ranks = [c // 4 for c in canon]
    assert ranks == sorted(ranks, reverse=True)


def test_canonicalize_count():
    """Verify exactly 16432 unique canonical PLO4 hands from full deck."""
    from itertools import combinations
    canon_set = set()
    for combo in combinations(range(52), 4):
        canon_set.add(canonicalize(combo))
    assert len(canon_set) == 16432
