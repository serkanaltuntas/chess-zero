"""Perft (performance test): count legal move trees to a given depth.

Used purely as a correctness gate against the canonical perft positions —
any mismatch with `python-chess` (in tests/oracles/) means there's a bug
in move generation, legality filtering, or apply/undo.
"""

from __future__ import annotations

from chess_zero.board.board import Board
from chess_zero.board.legality import legal_moves


def perft(board: Board, depth: int) -> int:
    if depth == 0:
        return 1
    total = 0
    # Materialise legal_moves: it's a generator that mutates the board mid-yield.
    for move in list(legal_moves(board)):
        board.apply_move(move)
        total += perft(board, depth - 1)
        board.undo_move()
    return total
