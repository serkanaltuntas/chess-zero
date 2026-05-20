"""Draw rules: 50-move, threefold repetition, insufficient material.

Plus `is_game_over` and `game_result` wrappers that combine these with the
mate/stalemate signals from `legality`. The threefold-repetition check
relies on `Board.position_history`, which is maintained by `Board.apply_move`
and `Board.undo_move` (a canonical key per game state — placement + side +
castling + en passant — is pushed and popped symmetrically).
"""

from __future__ import annotations

from collections import Counter

from chess_zero.board.board import Board
from chess_zero.board.legality import is_checkmate, is_stalemate
from chess_zero.board.types import Color, PieceType

_FIFTY_MOVE_HALFMOVES = 100  # 50 moves by each side
_THREEFOLD_THRESHOLD = 3


def is_fifty_move_draw(board: Board) -> bool:
    return board.halfmove_clock >= _FIFTY_MOVE_HALFMOVES


def is_insufficient_material(board: Board) -> bool:
    """K vs K, K+N vs K, K+B vs K are draws by FIDE insufficient-material.

    K+B vs K+B (same-color bishops) is also a draw by some interpretations;
    not enforced here to keep the rule conservative.
    """
    counts: dict[Color, Counter[PieceType]] = {
        Color.WHITE: Counter(),
        Color.BLACK: Counter(),
    }
    for piece in board.squares.values():
        counts[piece.color][piece.type] += 1

    # Any pawn, rook, or queen on the board → sufficient material.
    for cs in counts.values():
        if cs[PieceType.PAWN] or cs[PieceType.ROOK] or cs[PieceType.QUEEN]:
            return False

    w_minors = counts[Color.WHITE][PieceType.KNIGHT] + counts[Color.WHITE][PieceType.BISHOP]
    b_minors = counts[Color.BLACK][PieceType.KNIGHT] + counts[Color.BLACK][PieceType.BISHOP]

    if w_minors == 0 and b_minors == 0:
        return True  # K vs K
    # K+N vs K or K+B vs K (exactly one minor piece on one side)
    return w_minors + b_minors == 1


def is_threefold_repetition(board: Board) -> bool:
    if not board.position_history:
        return False
    current = board.position_history[-1]
    return board.position_history.count(current) >= _THREEFOLD_THRESHOLD


def is_game_over(board: Board) -> bool:
    return (
        is_checkmate(board)
        or is_stalemate(board)
        or is_fifty_move_draw(board)
        or is_insufficient_material(board)
        or is_threefold_repetition(board)
    )


def game_result(board: Board) -> str:
    """PGN-style result: '1-0', '0-1', '1/2-1/2', or '*' if game not over."""
    if is_checkmate(board):
        return "0-1" if board.side_to_move is Color.WHITE else "1-0"
    if (
        is_stalemate(board)
        or is_fifty_move_draw(board)
        or is_insufficient_material(board)
        or is_threefold_repetition(board)
    ):
        return "1/2-1/2"
    return "*"
