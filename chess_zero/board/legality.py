"""Attack detection + legal-move filter + mate/stalemate.

Pseudo-legal moves come from `moves.pseudo_legal_moves`. A pseudo-legal move
is "legal" iff applying it does not leave the moving side's king in check.
Castling has an additional guard (king-not-in-check, king path not attacked).

`is_square_attacked_by(board, sq, color)` asks: does `color` attack `sq`
right now? It scans piece-type-by-piece-type from the target square outward,
matching the same patterns the move generator uses but in reverse.
"""

from __future__ import annotations

from collections.abc import Iterator

from chess_zero.board.board import Board
from chess_zero.board.move import Move
from chess_zero.board.moves import (
    BISHOP_DIRECTIONS,
    KING_OFFSETS,
    KNIGHT_OFFSETS,
    ROOK_DIRECTIONS,
    pseudo_legal_moves,
)
from chess_zero.board.types import Color, PieceType, file_of, rank_of, square


def is_square_attacked_by(board: Board, sq: int, by_color: Color) -> bool:
    f, r = file_of(sq), rank_of(sq)

    # Pawn attacks. Attacker sits "behind" the target square from its own
    # marching direction — i.e. one rank toward the attacker's home rank.
    pawn_direction = -1 if by_color is Color.WHITE else 1
    for df in (-1, 1):
        nf, nr = f + df, r + pawn_direction
        if 0 <= nf < 8 and 0 <= nr < 8:
            p = board.piece_at(square(nf, nr))
            if p is not None and p.color is by_color and p.type is PieceType.PAWN:
                return True

    # Knight attacks.
    for df, dr in KNIGHT_OFFSETS:
        nf, nr = f + df, r + dr
        if 0 <= nf < 8 and 0 <= nr < 8:
            p = board.piece_at(square(nf, nr))
            if p is not None and p.color is by_color and p.type is PieceType.KNIGHT:
                return True

    # King attacks (adjacent).
    for df, dr in KING_OFFSETS:
        nf, nr = f + df, r + dr
        if 0 <= nf < 8 and 0 <= nr < 8:
            p = board.piece_at(square(nf, nr))
            if p is not None and p.color is by_color and p.type is PieceType.KING:
                return True

    # Sliding attacks.
    if _slider_attack(
        board, f, r, by_color, BISHOP_DIRECTIONS, (PieceType.BISHOP, PieceType.QUEEN)
    ):
        return True
    return _slider_attack(
        board, f, r, by_color, ROOK_DIRECTIONS, (PieceType.ROOK, PieceType.QUEEN)
    )


def _slider_attack(
    board: Board,
    f: int,
    r: int,
    by_color: Color,
    directions: tuple[tuple[int, int], ...],
    piece_types: tuple[PieceType, ...],
) -> bool:
    for df, dr in directions:
        nf, nr = f + df, r + dr
        while 0 <= nf < 8 and 0 <= nr < 8:
            p = board.piece_at(square(nf, nr))
            if p is not None:
                if p.color is by_color and p.type in piece_types:
                    return True
                break
            nf += df
            nr += dr
    return False


def find_king(board: Board, color: Color) -> int:
    for sq, piece in board.squares.items():
        if piece.color is color and piece.type is PieceType.KING:
            return sq
    raise ValueError(f"no {color} king on board")


def is_in_check(board: Board, color: Color) -> bool:
    return is_square_attacked_by(board, find_king(board, color), color.opposite())


def legal_moves(board: Board) -> Iterator[Move]:
    """Yield pseudo-legal moves that don't leave own king in check.

    Castling carries an extra guard: the king must not be in check now, and
    must not pass through or land on a square attacked by the opponent.
    """
    color = board.side_to_move
    enemy = color.opposite()
    for move in pseudo_legal_moves(board):
        if move.is_castle() and not _castle_path_safe(board, move, color, enemy):
            continue
        board.apply_move(move)
        try:
            if not is_in_check(board, color):
                yield move
        finally:
            board.undo_move()


def _castle_path_safe(board: Board, move: Move, color: Color, enemy: Color) -> bool:
    # The king must not start in check.
    if is_in_check(board, color):
        return False
    # King path: from_sq, midpoint, to_sq — none may be attacked.
    step = 1 if move.to_sq > move.from_sq else -1
    mid_sq = move.from_sq + step
    return not (
        is_square_attacked_by(board, mid_sq, enemy)
        or is_square_attacked_by(board, move.to_sq, enemy)
    )


def is_checkmate(board: Board) -> bool:
    if not is_in_check(board, board.side_to_move):
        return False
    return next(iter(legal_moves(board)), None) is None


def is_stalemate(board: Board) -> bool:
    if is_in_check(board, board.side_to_move):
        return False
    return next(iter(legal_moves(board)), None) is None
