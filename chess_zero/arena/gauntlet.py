"""Batch-of-games gauntlet runner with alternating colors + Elo derivation.

`run_gauntlet(agent_a_factory, agent_b_factory, games=100, ...)` plays N
games between A and B. With `alternate_colors=True` (default) A plays
white in even-indexed games and black in odd-indexed games, halving the
first-move bias.

`elo_delta_from_score(score)` inverts the Elo expected-score formula:
the rating difference implied by an observed score over many games.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

from chess_zero.agents.base import Agent
from chess_zero.arena.arena import GameRecord, play_game

AgentFactory = Callable[[], Agent]


@dataclass(frozen=True)
class GauntletResult:
    games_played: int
    a_wins: int
    a_draws: int
    a_losses: int
    a_score: float
    b_score: float
    a_win_rate: float
    elo_delta_a: float
    records: list[GameRecord] = field(default_factory=list)


def elo_delta_from_score(score: float) -> float:
    """Implied rating difference of A over B given A's per-game score in [0,1].

    Inverse of `expected_score`. Clamps boundary scores so log10 doesn't blow up.
    """
    # Cap at the equivalent of "won 1 of N+1 games" / "lost 1 of N+1 games".
    bounded = min(max(score, 1e-3), 1.0 - 1e-3)
    return -400.0 * math.log10(1.0 / bounded - 1.0)


def run_gauntlet(
    agent_a_factory: AgentFactory,
    agent_b_factory: AgentFactory,
    games: int = 100,
    *,
    alternate_colors: bool = True,
    max_plies: int = 200,
) -> GauntletResult:
    """Play `games` games between fresh A/B instances per game."""
    if games <= 0:
        raise ValueError("games must be positive")

    records: list[GameRecord] = []
    a_wins = 0
    a_draws = 0
    a_losses = 0

    for i in range(games):
        a = agent_a_factory()
        b = agent_b_factory()

        # Even index → A plays white. Odd index → A plays black (when alternation enabled).
        a_is_white = (not alternate_colors) or (i % 2 == 0)
        if a_is_white:
            record = play_game(a, b, max_plies=max_plies)
        else:
            record = play_game(b, a, max_plies=max_plies)
        records.append(record)

        if record.result in {"1/2-1/2", "*"}:
            # Treat "*" (unfinished by max_plies) as half-point each.
            a_draws += 1
            continue

        white_won = record.result == "1-0"
        if (white_won and a_is_white) or (not white_won and not a_is_white):
            a_wins += 1
        else:
            a_losses += 1

    a_score = a_wins + 0.5 * a_draws
    b_score = games - a_score
    a_win_rate = a_score / games
    return GauntletResult(
        games_played=games,
        a_wins=a_wins,
        a_draws=a_draws,
        a_losses=a_losses,
        a_score=a_score,
        b_score=b_score,
        a_win_rate=a_win_rate,
        elo_delta_a=elo_delta_from_score(a_win_rate),
        records=records,
    )
