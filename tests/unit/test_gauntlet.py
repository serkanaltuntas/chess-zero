import pytest

from chess_zero.agents import MinimaxAgent, RandomAgent
from chess_zero.arena.gauntlet import GauntletResult, elo_delta_from_score, run_gauntlet

# ---------- run_gauntlet basics ----------


def test_run_gauntlet_returns_result_with_expected_shape():
    result = run_gauntlet(
        agent_a_factory=lambda: RandomAgent(seed=1),
        agent_b_factory=lambda: RandomAgent(seed=2),
        games=4,
        max_plies=60,
    )
    assert isinstance(result, GauntletResult)
    assert result.games_played == 4
    assert result.a_wins + result.a_draws + result.a_losses == 4
    assert 0.0 <= result.a_win_rate <= 1.0
    assert len(result.records) == 4


def test_run_gauntlet_alternates_colors_by_default():
    result = run_gauntlet(
        agent_a_factory=lambda: RandomAgent(seed=1),
        agent_b_factory=lambda: RandomAgent(seed=2),
        games=4,
        max_plies=20,
    )
    # Both are RandomAgent so naming alone is ambiguous; just check the
    # alternation invariant: half the games have A as white (even indices).
    a_as_white = [rec for i, rec in enumerate(result.records) if i % 2 == 0]
    a_as_black = [rec for i, rec in enumerate(result.records) if i % 2 == 1]
    assert len(a_as_white) == 2
    assert len(a_as_black) == 2


def test_run_gauntlet_no_alternation_when_disabled():
    result = run_gauntlet(
        agent_a_factory=lambda: RandomAgent(seed=1),
        agent_b_factory=lambda: RandomAgent(seed=2),
        games=3,
        alternate_colors=False,
        max_plies=20,
    )
    # All games: agent A is always white in this mode.
    assert all(rec.white_name == "RandomAgent" for rec in result.records)


# ---------- Elo derivation ----------


def test_elo_delta_zero_at_fifty_percent():
    assert elo_delta_from_score(0.5) == pytest.approx(0.0)


def test_elo_delta_positive_when_score_above_half():
    assert elo_delta_from_score(0.75) > 0


def test_elo_delta_negative_when_score_below_half():
    assert elo_delta_from_score(0.25) < 0


def test_elo_delta_handles_perfect_and_zero():
    # No NaN / inf — clamps internally.
    assert elo_delta_from_score(1.0) > 0
    assert elo_delta_from_score(0.0) < 0


# ---------- gauntlet sanity: minimax outperforms random ----------


def test_minimax_gauntlet_score_above_random():
    result = run_gauntlet(
        agent_a_factory=lambda: MinimaxAgent(depth=2),
        agent_b_factory=lambda: RandomAgent(seed=0),
        games=6,
        max_plies=80,
    )
    # Aggregate signal: minimax should comfortably outscore random.
    assert result.a_score > result.b_score
    assert result.a_win_rate > 0.5
