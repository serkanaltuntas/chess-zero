"""Core board types: Color, PieceType, Piece, Square helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

_FILES = "abcdefgh"


class Color(Enum):
    WHITE = "w"
    BLACK = "b"

    def opposite(self) -> Color:
        return Color.BLACK if self is Color.WHITE else Color.WHITE


class PieceType(Enum):
    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"
    KING = "k"


@dataclass(frozen=True, slots=True)
class Piece:
    type: PieceType
    color: Color

    def symbol(self) -> str:
        s = self.type.value
        return s.upper() if self.color is Color.WHITE else s

    @classmethod
    def from_symbol(cls, symbol: str) -> Piece:
        color = Color.WHITE if symbol.isupper() else Color.BLACK
        return cls(PieceType(symbol.lower()), color)


def square(file: int, rank: int) -> int:
    """Build a square index 0..63 from (file 0..7, rank 0..7)."""
    return rank * 8 + file


def file_of(sq: int) -> int:
    return sq & 7


def rank_of(sq: int) -> int:
    return sq >> 3


def square_name(sq: int) -> str:
    return f"{_FILES[file_of(sq)]}{rank_of(sq) + 1}"


class Square:
    """Namespace for square index helpers. Square indices are plain `int` in [0, 64)."""

    @staticmethod
    def from_name(name: str) -> int:
        if len(name) != 2:
            raise ValueError(f"invalid square name: {name}")
        f = _FILES.index(name[0])
        r = int(name[1]) - 1
        return square(f, r)
