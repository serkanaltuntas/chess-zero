"""Pseudo-legal move generation per piece type.

Pseudo-legal = generated per piece movement rules, without checking whether
the moving side's king ends up in check. The legality filter (in legality.py)
removes self-checks. Castling is also emitted here based on `castling_rights`
and clear-path conditions; the "king passes through attacked square" check
lives in the legality filter (it needs attack detection, which depends on
board state, not piece kind).
"""

from __future__ import annotations

from collections.abc import Iterator

from chess_zero.board.board import Board
from chess_zero.board.move import Move, MoveFlag
from chess_zero.board.types import Color, PieceType, file_of, rank_of, square

PROMOTION_PIECES = (
    PieceType.QUEEN,
    PieceType.ROOK,
    PieceType.BISHOP,
    PieceType.KNIGHT,
)

KNIGHT_OFFSETS = (
    (1, 2), (2, 1), (-1, 2), (-2, 1),
    (1, -2), (2, -1), (-1, -2), (-2, -1),
)

KING_OFFSETS = (
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
)

BISHOP_DIRECTIONS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ROOK_DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))


def pseudo_legal_moves(board: Board) -> Iterator[Move]:
    for sq, piece in list(board.squares.items()):
        if piece.color is not board.side_to_move:
            continue
        match piece.type:
            case PieceType.PAWN:
                yield from _pawn_moves(board, sq, piece.color)
            case PieceType.KNIGHT:
                yield from _knight_moves(board, sq, piece.color)
            case PieceType.BISHOP:
                yield from _sliding_moves(board, sq, piece.color, BISHOP_DIRECTIONS)
            case PieceType.ROOK:
                yield from _sliding_moves(board, sq, piece.color, ROOK_DIRECTIONS)
            case PieceType.QUEEN:
                yield from _sliding_moves(
                    board, sq, piece.color, BISHOP_DIRECTIONS + ROOK_DIRECTIONS
                )
            case PieceType.KING:
                yield from _king_moves(board, sq, piece.color)


def _pawn_moves(board: Board, sq: int, color: Color) -> Iterator[Move]:
    direction = 1 if color is Color.WHITE else -1
    start_rank = 1 if color is Color.WHITE else 6
    promotion_rank = 7 if color is Color.WHITE else 0
    f, r = file_of(sq), rank_of(sq)

    # Single push (always within the board because pawns promote on rank 0/7).
    one = square(f, r + direction)
    if board.piece_at(one) is None:
        if r + direction == promotion_rank:
            for promo in PROMOTION_PIECES:
                yield Move(sq, one, promotion=promo, flags=MoveFlag.PROMOTION)
        else:
            yield Move(sq, one)
            # Double push from starting rank.
            if r == start_rank:
                two = square(f, r + 2 * direction)
                if board.piece_at(two) is None:
                    yield Move(sq, two, flags=MoveFlag.DOUBLE_PUSH)

    # Diagonal captures (including en passant).
    for df in (-1, 1):
        nf = f + df
        if not 0 <= nf < 8:
            continue
        target = square(nf, r + direction)
        target_piece = board.piece_at(target)
        if target_piece is not None and target_piece.color is not color:
            if r + direction == promotion_rank:
                for promo in PROMOTION_PIECES:
                    yield Move(sq, target, promotion=promo, flags=MoveFlag.PROMOTION)
            else:
                yield Move(sq, target)
        elif target == board.en_passant_square:
            yield Move(sq, target, flags=MoveFlag.EN_PASSANT)


def _knight_moves(board: Board, sq: int, color: Color) -> Iterator[Move]:
    f, r = file_of(sq), rank_of(sq)
    for df, dr in KNIGHT_OFFSETS:
        nf, nr = f + df, r + dr
        if not (0 <= nf < 8 and 0 <= nr < 8):
            continue
        target = square(nf, nr)
        target_piece = board.piece_at(target)
        if target_piece is None or target_piece.color is not color:
            yield Move(sq, target)


def _sliding_moves(
    board: Board,
    sq: int,
    color: Color,
    directions: tuple[tuple[int, int], ...],
) -> Iterator[Move]:
    f, r = file_of(sq), rank_of(sq)
    for df, dr in directions:
        nf, nr = f + df, r + dr
        while 0 <= nf < 8 and 0 <= nr < 8:
            target = square(nf, nr)
            target_piece = board.piece_at(target)
            if target_piece is None:
                yield Move(sq, target)
            else:
                if target_piece.color is not color:
                    yield Move(sq, target)
                break
            nf += df
            nr += dr


def _king_moves(board: Board, sq: int, color: Color) -> Iterator[Move]:
    f, r = file_of(sq), rank_of(sq)
    for df, dr in KING_OFFSETS:
        nf, nr = f + df, r + dr
        if not (0 <= nf < 8 and 0 <= nr < 8):
            continue
        target = square(nf, nr)
        target_piece = board.piece_at(target)
        if target_piece is None or target_piece.color is not color:
            yield Move(sq, target)

    # Castling: emit only if rights and path clear. The "king must not be in
    # check, must not pass through attacked squares" guards belong in the
    # legality filter — those depend on attack detection which is not in
    # scope here.
    #
    # IMPORTANT: we re-read `board.castling_rights` on each check rather
    # than alias it. As a generator, this function may be suspended between
    # yields while a caller applies and undoes other king moves; those
    # operations rebind `board.castling_rights` to a fresh set, and any
    # stored alias would point to a stale, mutated copy.
    rank0 = 0 if color is Color.WHITE else 7
    if sq != square(4, rank0):
        return
    ks = "K" if color is Color.WHITE else "k"
    qs = "Q" if color is Color.WHITE else "q"
    if (
        ks in board.castling_rights
        and board.piece_at(square(5, rank0)) is None
        and board.piece_at(square(6, rank0)) is None
    ):
        yield Move(sq, square(6, rank0), flags=MoveFlag.CASTLE_KINGSIDE)
    if (
        qs in board.castling_rights
        and board.piece_at(square(1, rank0)) is None
        and board.piece_at(square(2, rank0)) is None
        and board.piece_at(square(3, rank0)) is None
    ):
        yield Move(sq, square(2, rank0), flags=MoveFlag.CASTLE_QUEENSIDE)
