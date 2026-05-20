"""Abstract `Agent` protocol — the only arena contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from chess_zero.board.board import Board
from chess_zero.board.move import Move


class Agent(ABC):
    """Anything that picks a move from a board position."""

    @abstractmethod
    def select_move(self, board: Board) -> Move:
        """Return a legal move for the side to move.

        Implementations should raise `ValueError` when no legal moves exist
        (the arena will treat that as game over for the side to move).
        """
