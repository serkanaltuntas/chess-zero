"""SAN move conversion + simple PGN move-text parse/serialize.

Scope for v0.1:
- `move_to_san(board, move)` — produce SAN (e.g., "e4", "Nxd5", "O-O",
  "e8=Q+", "Re8#") given the board state *before* the move is applied.
- `san_to_move(board, san)` — find the unique legal move matching a SAN
  string in the current position.
- `game_san_moves(board)` — SAN list for a board's `history`, in order.
- `moves_from_san_text(board, text)` — apply a sequence of SAN tokens
  ("1. e4 e5 2. Nf3 Nc6" style); returns the list of `Move` objects and
  mutates the board through them.

Out of scope for v0.1: PGN tag pairs `[...]`, NAG annotations (`$1`),
inline comments `{...}`, variations `(...)`, multi-game PGN files. The
goal is "human-readable game record for self-play arena logs", not full
PGN compliance.
"""

from __future__ import annotations

import re

from chess_zero.board.board import Board
from chess_zero.board.legality import is_checkmate, is_in_check, legal_moves
from chess_zero.board.move import Move, MoveFlag
from chess_zero.board.types import PieceType, file_of, rank_of, square_name

_PROMOTION_TO_LETTER = {
    PieceType.QUEEN: "Q",
    PieceType.ROOK: "R",
    PieceType.BISHOP: "B",
    PieceType.KNIGHT: "N",
}

_LETTER_TO_PIECE = {
    "K": PieceType.KING,
    "Q": PieceType.QUEEN,
    "R": PieceType.ROOK,
    "B": PieceType.BISHOP,
    "N": PieceType.KNIGHT,
}

# Matches: piece letter, optional disambig file, optional disambig rank,
# optional capture, destination square, optional promotion.
_SAN_RE = re.compile(
    r"^(?P<piece>[KQRBN])?"
    r"(?P<from_file>[a-h])?"
    r"(?P<from_rank>[1-8])?"
    r"(?P<capture>x)?"
    r"(?P<to>[a-h][1-8])"
    r"(?:=(?P<promo>[QRBN]))?$"
)


def move_to_san(board: Board, move: Move) -> str:
    """SAN for `move` from `board` (state before the move is applied).

    The board is not mutated by the caller's perspective: this function
    applies the move temporarily to detect check/mate, then undoes it.
    """
    piece = board.piece_at(move.from_sq)
    if piece is None:
        raise ValueError(f"no piece on {square_name(move.from_sq)}")

    if move.is_castle():
        core = "O-O" if move.flags & MoveFlag.CASTLE_KINGSIDE else "O-O-O"
    else:
        core = _non_castle_san_core(board, move, piece.type)

    # Check / checkmate suffix.
    board.apply_move(move)
    try:
        suffix = ""
        if is_checkmate(board):
            suffix = "#"
        elif is_in_check(board, board.side_to_move):
            suffix = "+"
    finally:
        board.undo_move()

    return core + suffix


def _non_castle_san_core(board: Board, move: Move, piece_type: PieceType) -> str:
    is_capture = (
        board.piece_at(move.to_sq) is not None or move.is_en_passant()
    )

    if piece_type is PieceType.PAWN:
        piece_letter = ""
        disambig = (
            "abcdefgh"[file_of(move.from_sq)] if is_capture else ""
        )
    else:
        piece_letter = piece_type.value.upper()
        disambig = _piece_disambiguation(board, move, piece_type)

    promotion = (
        f"={_PROMOTION_TO_LETTER[move.promotion]}"
        if move.promotion is not None
        else ""
    )
    capture = "x" if is_capture else ""
    return f"{piece_letter}{disambig}{capture}{square_name(move.to_sq)}{promotion}"


def _piece_disambiguation(board: Board, move: Move, piece_type: PieceType) -> str:
    """Minimal disambiguation needed (file → rank → both)."""
    color = board.side_to_move

    # Snapshot piece positions: legal_moves mutates board.squares via apply/undo
    # below, so we can't iterate the live dict.
    same_type_squares = [
        sq
        for sq, p in board.squares.items()
        if p.type is piece_type and p.color is color and sq != move.from_sq
    ]
    if not same_type_squares:
        return ""

    legal_to_target = [
        m for m in legal_moves(board) if m.to_sq == move.to_sq
    ]
    rivals = [
        sq
        for sq in same_type_squares
        if any(m.from_sq == sq for m in legal_to_target)
    ]
    if not rivals:
        return ""

    from_file = file_of(move.from_sq)
    from_rank = rank_of(move.from_sq)
    if all(file_of(r) != from_file for r in rivals):
        return "abcdefgh"[from_file]
    if all(rank_of(r) != from_rank for r in rivals):
        return str(from_rank + 1)
    return f"{'abcdefgh'[from_file]}{from_rank + 1}"


def _moves_equivalent(a: Move, b: Move) -> bool:
    return (
        a.from_sq == b.from_sq
        and a.to_sq == b.to_sq
        and a.promotion == b.promotion
    )


def san_to_move(board: Board, san: str) -> Move:
    """Return the unique legal move matching `san` from the current board."""
    raw = san.rstrip("+#!?")

    if raw in ("O-O", "0-0"):
        for m in legal_moves(board):
            if m.flags & MoveFlag.CASTLE_KINGSIDE:
                return m
        raise ValueError(f"no legal kingside castle: {san!r}")
    if raw in ("O-O-O", "0-0-0"):
        for m in legal_moves(board):
            if m.flags & MoveFlag.CASTLE_QUEENSIDE:
                return m
        raise ValueError(f"no legal queenside castle: {san!r}")

    match = _SAN_RE.match(raw)
    if match is None:
        raise ValueError(f"unparseable SAN: {san!r}")

    piece_letter = match.group("piece")
    from_file_letter = match.group("from_file")
    from_rank_letter = match.group("from_rank")
    to_square = match.group("to")
    promo_letter = match.group("promo")

    target_type = (
        _LETTER_TO_PIECE[piece_letter] if piece_letter else PieceType.PAWN
    )
    from chess_zero.board.types import Square  # local import to avoid cycle noise

    target_sq = Square.from_name(to_square)
    target_promotion = (
        _LETTER_TO_PIECE[promo_letter] if promo_letter else None
    )
    target_from_file = (
        "abcdefgh".index(from_file_letter) if from_file_letter else None
    )
    target_from_rank = int(from_rank_letter) - 1 if from_rank_letter else None

    # Materialise legal_moves so the board returns to pre-move state before
    # we inspect piece types at the source squares.
    legal = list(legal_moves(board))
    candidates: list[Move] = []
    for m in legal:
        if m.to_sq != target_sq:
            continue
        if m.promotion != target_promotion:
            continue
        piece = board.piece_at(m.from_sq)
        if piece is None or piece.type is not target_type:
            continue
        if target_from_file is not None and file_of(m.from_sq) != target_from_file:
            continue
        if target_from_rank is not None and rank_of(m.from_sq) != target_from_rank:
            continue
        candidates.append(m)

    if not candidates:
        raise ValueError(f"no legal move matches SAN: {san!r}")
    if len(candidates) > 1:
        raise ValueError(f"ambiguous SAN, {len(candidates)} matches: {san!r}")
    return candidates[0]


def game_san_moves(board: Board) -> list[str]:
    """SAN strings for every move in `board.history`, in order.

    Mutates `board` transiently (undoes all and reapplies) but leaves the
    final state identical to the input.
    """
    move_list = [info.move for info in board.history]
    for _ in move_list:
        board.undo_move()

    sans: list[str] = []
    for move in move_list:
        sans.append(move_to_san(board, move))
        board.apply_move(move)
    return sans


_MOVE_NUMBER_RE = re.compile(r"\d+\.+")


def moves_from_san_text(board: Board, text: str) -> list[Move]:
    """Apply a whitespace-separated SAN sequence to `board`.

    Handles tokens like "1.", "1...", "2." (move numbers) and the result
    markers "1-0", "0-1", "1/2-1/2", "*". Returns the list of `Move`
    objects in order.
    """
    cleaned = _MOVE_NUMBER_RE.sub(" ", text)
    tokens = [t for t in cleaned.split() if t and t not in {"1-0", "0-1", "1/2-1/2", "*"}]

    applied: list[Move] = []
    for tok in tokens:
        move = san_to_move(board, tok)
        board.apply_move(move)
        applied.append(move)
    return applied
