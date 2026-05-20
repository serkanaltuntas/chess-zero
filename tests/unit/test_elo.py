import pytest

from chess_zero.arena import expected_score, update_pair, update_rating


def test_expected_score_equal_ratings_is_half():
    assert expected_score(1500, 1500) == pytest.approx(0.5)


def test_expected_score_higher_rating_above_half():
    assert expected_score(1600, 1500) > 0.5
    assert expected_score(1500, 1600) < 0.5


def test_expected_score_400_diff_is_91_percent():
    # Standard Elo: 400-point gap → ~91% expected score for the favourite
    assert expected_score(1900, 1500) == pytest.approx(10 / 11, rel=1e-3)


def test_update_rating_win_against_equal_increases_rating():
    new_rating = update_rating(rating=1500, expected=0.5, actual=1.0, k=32)
    assert new_rating == pytest.approx(1516)


def test_update_rating_loss_against_equal_decreases_rating():
    new_rating = update_rating(rating=1500, expected=0.5, actual=0.0, k=32)
    assert new_rating == pytest.approx(1484)


def test_update_rating_draw_against_equal_unchanged():
    new_rating = update_rating(rating=1500, expected=0.5, actual=0.5, k=32)
    assert new_rating == pytest.approx(1500)


def test_update_pair_conserves_total_rating_change():
    """A and B's total rating change must sum to zero in any single update."""
    new_a, new_b = update_pair(1500, 1500, result_a=1.0, k=32)
    # Sum of changes is zero (one's gain = other's loss)
    assert (new_a - 1500) + (new_b - 1500) == pytest.approx(0.0)


def test_update_pair_winner_gains_loser_loses():
    new_a, new_b = update_pair(1500, 1500, result_a=1.0, k=32)
    assert new_a > 1500
    assert new_b < 1500


def test_update_pair_draw_between_equals_no_change():
    new_a, new_b = update_pair(1500, 1500, result_a=0.5, k=32)
    assert new_a == pytest.approx(1500)
    assert new_b == pytest.approx(1500)
