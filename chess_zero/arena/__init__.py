"""Arena: two agents play one game; Elo update; replay from record."""

from chess_zero.arena.arena import GameRecord, play_game, replay
from chess_zero.arena.elo import expected_score, update_pair, update_rating
from chess_zero.arena.gauntlet import GauntletResult, elo_delta_from_score, run_gauntlet

__all__ = [
    "GameRecord",
    "GauntletResult",
    "elo_delta_from_score",
    "expected_score",
    "play_game",
    "replay",
    "run_gauntlet",
    "update_pair",
    "update_rating",
]
