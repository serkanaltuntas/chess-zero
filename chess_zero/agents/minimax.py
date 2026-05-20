"""Minimax baseline with a handcrafted material-only evaluation.

Negamax formulation: every recursive call returns the score from the
side-to-move's perspective. Leaf scoring is material balance only —
no piece-square tables, no positional terms. Enough to beat random,
not enough to be interesting to a human; that's the point of a baseline.
"""

from __future__ import annotations

from chess_zero.agents.base import Agent
from chess_zero.board.board import Board
from chess_zero.board.draws import is_game_over
from chess_zero.board.legality import is_in_check, legal_moves
from chess_zero.board.move import Move
from chess_zero.board.types import Color, PieceType

PIECE_VALUE: dict[PieceType, int] = {
    PieceType.PAWN: 100,
    PieceType.KNIGHT: 320,
    PieceType.BISHOP: 330,
    PieceType.ROOK: 500,
    PieceType.QUEEN: 900,
    PieceType.KING: 0,
}

_MATE_SCORE = 1_000_000


class MinimaxAgent(Agent):
    def __init__(self, depth: int = 3) -> None:
        if depth < 1:
            raise ValueError("depth must be >= 1")
        self.depth = depth

    def select_move(self, board: Board) -> Move:
        moves = list(legal_moves(board))
        if not moves:
            raise ValueError("no legal moves available")

        best_score = -_MATE_SCORE - 1
        best_move = moves[0]
        for move in moves:
            board.apply_move(move)
            score = -self._negamax(board, self.depth - 1)
            board.undo_move()
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def _negamax(self, board: Board, depth: int) -> int:
        if is_game_over(board):
            return self._terminal_score(board, depth)
        if depth == 0:
            return self._material_score(board)

        best = -_MATE_SCORE - 1
        moves = list(legal_moves(board))
        if not moves:
            return self._terminal_score(board, depth)
        for move in moves:
            board.apply_move(move)
            score = -self._negamax(board, depth - 1)
            board.undo_move()
            best = max(best, score)
        return best

    @staticmethod
    def _terminal_score(board: Board, depth: int) -> int:
        # No legal moves: checkmate (lose) or stalemate (draw). Other draw
        # rules (50-move, 3-fold, insufficient material) also score zero.
        if is_in_check(board, board.side_to_move):
            # Prefer slower losses + faster wins: deeper search produces a
            # smaller magnitude score.
            return -_MATE_SCORE + (board.fullmove_number - depth)
        return 0

    @staticmethod
    def _material_score(board: Board) -> int:
        white = 0
        black = 0
        for piece in board.squares.values():
            value = PIECE_VALUE[piece.type]
            if piece.color is Color.WHITE:
                white += value
            else:
                black += value
        diff = white - black
        return diff if board.side_to_move is Color.WHITE else -diff
