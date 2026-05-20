"""Random-move baseline. Useful as the trivial opponent in any gauntlet."""

from __future__ import annotations

import random

from chess_zero.agents.base import Agent
from chess_zero.board.board import Board
from chess_zero.board.legality import legal_moves
from chess_zero.board.move import Move


class RandomAgent(Agent):
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def select_move(self, board: Board) -> Move:
        moves = list(legal_moves(board))
        if not moves:
            raise ValueError("no legal moves available")
        return self._rng.choice(moves)
