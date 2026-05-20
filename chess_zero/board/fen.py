"""FEN (Forsyth-Edwards Notation) parse and serialize."""

from __future__ import annotations

from chess_zero.board.board import Board
from chess_zero.board.types import Color, Piece, Square, square, square_name

_FEN_FIELD_COUNT = 6
_BOARD_SIZE = 8
_CASTLING_ORDER = "KQkq"


def board_from_fen(fen: str) -> Board:
    parts = fen.split()
    if len(parts) != _FEN_FIELD_COUNT:
        raise ValueError(f"FEN must have {_FEN_FIELD_COUNT} fields, got {len(parts)}: {fen!r}")

    placement, active, castling, ep, halfmove, fullmove = parts

    squares: dict[int, Piece] = {}
    ranks = placement.split("/")
    if len(ranks) != _BOARD_SIZE:
        raise ValueError(f"FEN placement must have {_BOARD_SIZE} ranks: {placement!r}")
    for r_idx, rank_str in enumerate(ranks):
        rank = (_BOARD_SIZE - 1) - r_idx
        file = 0
        for ch in rank_str:
            if ch.isdigit():
                file += int(ch)
            else:
                squares[square(file, rank)] = Piece.from_symbol(ch)
                file += 1
        if file != _BOARD_SIZE:
            raise ValueError(f"FEN rank does not sum to {_BOARD_SIZE}: {rank_str!r}")

    side = Color.WHITE if active == "w" else Color.BLACK
    rights: set[str] = set() if castling == "-" else set(castling)
    ep_sq = None if ep == "-" else Square.from_name(ep)

    return Board(
        squares=squares,
        side_to_move=side,
        castling_rights=rights,
        en_passant_square=ep_sq,
        halfmove_clock=int(halfmove),
        fullmove_number=int(fullmove),
    )


def board_to_fen(board: Board) -> str:
    ranks: list[str] = []
    for r in range(_BOARD_SIZE - 1, -1, -1):
        empty = 0
        s = ""
        for f in range(_BOARD_SIZE):
            piece = board.piece_at(square(f, r))
            if piece is None:
                empty += 1
            else:
                if empty:
                    s += str(empty)
                    empty = 0
                s += piece.symbol()
        if empty:
            s += str(empty)
        ranks.append(s)
    placement = "/".join(ranks)

    active = "w" if board.side_to_move is Color.WHITE else "b"
    castling = "".join(sorted(board.castling_rights, key=_CASTLING_ORDER.index)) or "-"
    ep = "-" if board.en_passant_square is None else square_name(board.en_passant_square)

    return f"{placement} {active} {castling} {ep} {board.halfmove_clock} {board.fullmove_number}"
