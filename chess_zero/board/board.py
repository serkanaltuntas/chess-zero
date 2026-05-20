"""Board state + apply/undo with full chess rules.

Move application handles the four "non-quiet" cases — en passant, promotion,
castling, and double push — through `MoveFlag` markers and the `promotion`
field on `Move`. `undo_move` is the inverse; together they let the legality
filter speculatively try moves without permanently mutating state.

Castling rights bookkeeping covers three triggers: king move (drop both for
that color), rook move off its corner (drop the matching right), and capture
of a rook on its corner (drop opponent's right). All three are needed for
perft correctness.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from chess_zero.board.move import Move, MoveFlag
from chess_zero.board.types import Color, Piece, PieceType, square


def _initial_squares() -> dict[int, Piece]:
    """Standard chess starting position."""
    back_rank = [
        PieceType.ROOK,
        PieceType.KNIGHT,
        PieceType.BISHOP,
        PieceType.QUEEN,
        PieceType.KING,
        PieceType.BISHOP,
        PieceType.KNIGHT,
        PieceType.ROOK,
    ]
    squares: dict[int, Piece] = {}
    for file, ptype in enumerate(back_rank):
        squares[square(file, 0)] = Piece(ptype, Color.WHITE)
        squares[square(file, 7)] = Piece(ptype, Color.BLACK)
        squares[square(file, 1)] = Piece(PieceType.PAWN, Color.WHITE)
        squares[square(file, 6)] = Piece(PieceType.PAWN, Color.BLACK)
    return squares


@dataclass(frozen=True, slots=True)
class UndoInfo:
    move: Move
    captured: Piece | None
    captured_square: int | None  # differs from move.to_sq for en passant
    prev_castling: frozenset[str]
    prev_ep: int | None
    prev_halfmove: int
    prev_fullmove: int


# Castling-rights bookkeeping: when a king moves, drop these rights; when a
# rook moves from (or is captured on) one of these squares, drop the matching
# right.
_CORNER_RIGHT = {
    square(0, 0): "Q",  # a1
    square(7, 0): "K",  # h1
    square(0, 7): "q",  # a8
    square(7, 7): "k",  # k8
}


@dataclass
class Board:
    squares: dict[int, Piece] = field(default_factory=_initial_squares)
    side_to_move: Color = Color.WHITE
    castling_rights: set[str] = field(default_factory=lambda: {"K", "Q", "k", "q"})
    en_passant_square: int | None = None
    halfmove_clock: int = 0
    fullmove_number: int = 1
    history: list[UndoInfo] = field(default_factory=list)

    def piece_at(self, sq: int) -> Piece | None:
        return self.squares.get(sq)

    def set_piece_at(self, sq: int, piece: Piece) -> None:
        self.squares[sq] = piece

    def remove_piece(self, sq: int) -> Piece | None:
        return self.squares.pop(sq, None)

    # ------------------------------------------------------------------ apply

    def apply_move(self, move: Move) -> None:
        piece = self.squares[move.from_sq]
        captured: Piece | None = self.squares.get(move.to_sq)
        captured_sq: int | None = move.to_sq if captured is not None else None

        # En passant: the captured pawn sits behind the destination square.
        if move.is_en_passant():
            ep_capture_sq = (
                move.to_sq - 8 if piece.color is Color.WHITE else move.to_sq + 8
            )
            captured = self.squares.get(ep_capture_sq)
            captured_sq = ep_capture_sq

        info = UndoInfo(
            move=move,
            captured=captured,
            captured_square=captured_sq,
            prev_castling=frozenset(self.castling_rights),
            prev_ep=self.en_passant_square,
            prev_halfmove=self.halfmove_clock,
            prev_fullmove=self.fullmove_number,
        )

        # Halfmove clock: reset on pawn move or any capture.
        if piece.type is PieceType.PAWN or captured is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # En passant target: clear, then set if this is a double push.
        self.en_passant_square = None
        if move.is_double_push():
            self.en_passant_square = (move.from_sq + move.to_sq) // 2

        # Remove the moving piece from origin.
        del self.squares[move.from_sq]

        # Remove any captured piece (regular or en passant).
        if captured is not None and captured_sq is not None:
            self.squares.pop(captured_sq, None)

        # Place the destination piece — promoted type or original.
        if move.promotion is not None:
            self.squares[move.to_sq] = Piece(move.promotion, piece.color)
        else:
            self.squares[move.to_sq] = piece

        # Castling: also move the rook.
        if move.is_castle():
            self._apply_castle_rook(move, piece.color)

        # Update castling rights from king/rook movement.
        self._update_castling_rights_after(move, piece)
        # Capturing a rook on its starting square drops the matching right.
        if captured is not None and captured_sq is not None:
            opp_right = _CORNER_RIGHT.get(captured_sq)
            if opp_right is not None and captured.type is PieceType.ROOK:
                self.castling_rights.discard(opp_right)

        # Side flip and fullmove increment.
        if self.side_to_move is Color.BLACK:
            self.fullmove_number += 1
        self.side_to_move = self.side_to_move.opposite()

        self.history.append(info)

    def _apply_castle_rook(self, move: Move, color: Color) -> None:
        rank = 0 if color is Color.WHITE else 7
        if move.flags & MoveFlag.CASTLE_KINGSIDE:
            rook_from = square(7, rank)
            rook_to = square(5, rank)
        else:
            rook_from = square(0, rank)
            rook_to = square(3, rank)
        rook = self.squares.pop(rook_from)
        self.squares[rook_to] = rook

    def _update_castling_rights_after(self, move: Move, piece: Piece) -> None:
        if piece.type is PieceType.KING:
            if piece.color is Color.WHITE:
                self.castling_rights -= {"K", "Q"}
            else:
                self.castling_rights -= {"k", "q"}
        elif piece.type is PieceType.ROOK:
            right = _CORNER_RIGHT.get(move.from_sq)
            if right is not None:
                self.castling_rights.discard(right)

    # ------------------------------------------------------------------- undo

    def undo_move(self) -> None:
        if not self.history:
            raise IndexError("no moves to undo")
        info = self.history.pop()
        move = info.move

        # Flip side back first so we know whose piece moved.
        self.side_to_move = self.side_to_move.opposite()
        self.fullmove_number = info.prev_fullmove
        self.castling_rights = set(info.prev_castling)
        self.en_passant_square = info.prev_ep
        self.halfmove_clock = info.prev_halfmove

        moved_piece = self.squares.pop(move.to_sq)
        # If this was a promotion, the original piece on from_sq was a pawn.
        if move.promotion is not None:
            moved_piece = Piece(PieceType.PAWN, moved_piece.color)
        self.squares[move.from_sq] = moved_piece

        # Restore captured piece (regular or en passant).
        if info.captured is not None and info.captured_square is not None:
            self.squares[info.captured_square] = info.captured

        # Undo castling rook move.
        if move.is_castle():
            color = moved_piece.color
            rank = 0 if color is Color.WHITE else 7
            if move.flags & MoveFlag.CASTLE_KINGSIDE:
                rook_from = square(7, rank)
                rook_to = square(5, rank)
            else:
                rook_from = square(0, rank)
                rook_to = square(3, rank)
            rook = self.squares.pop(rook_to)
            self.squares[rook_from] = rook
