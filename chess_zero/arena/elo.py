"""Standard Elo rating math.

`expected_score(R_A, R_B)` is the canonical logistic:

    E_A = 1 / (1 + 10^((R_B - R_A) / 400))

`update_rating(rating, expected, actual, k)` applies one game's update:

    R' = R + k * (S - E)

where S is the actual score (1 = win, 0.5 = draw, 0 = loss) and E is the
expected score from `expected_score`. K controls volatility — 32 for
casual use, 16 for established players, 10 for masters. Default 32.
"""

from __future__ import annotations

DEFAULT_K = 32.0


def expected_score(rating_a: float, rating_b: float) -> float:
    return float(1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0)))


def update_rating(
    rating: float,
    expected: float,
    actual: float,
    k: float = DEFAULT_K,
) -> float:
    return rating + k * (actual - expected)


def update_pair(
    rating_a: float,
    rating_b: float,
    result_a: float,
    k: float = DEFAULT_K,
) -> tuple[float, float]:
    """Symmetric update for both players given player A's score (1/0.5/0)."""
    expected_a = expected_score(rating_a, rating_b)
    expected_b = 1.0 - expected_a
    new_a = update_rating(rating_a, expected_a, result_a, k)
    new_b = update_rating(rating_b, expected_b, 1.0 - result_a, k)
    return new_a, new_b
