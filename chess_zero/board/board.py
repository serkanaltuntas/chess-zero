"""Board state: piece placement, side to move, castling rights, en passant, clocks."""

from __future__ import annotations

from dataclasses import dataclass, field

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


@dataclass
class Board:
    squares: dict[int, Piece] = field(default_factory=_initial_squares)
    side_to_move: Color = Color.WHITE
    castling_rights: set[str] = field(default_factory=lambda: {"K", "Q", "k", "q"})
    en_passant_square: int | None = None
    halfmove_clock: int = 0
    fullmove_number: int = 1

    def piece_at(self, sq: int) -> Piece | None:
        return self.squares.get(sq)

    def set_piece_at(self, sq: int, piece: Piece) -> None:
        self.squares[sq] = piece

    def remove_piece(self, sq: int) -> Piece | None:
        return self.squares.pop(sq, None)
