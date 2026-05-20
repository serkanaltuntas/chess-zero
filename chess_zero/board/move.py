"""Move dataclass with UCI parse/serialize and flag helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntFlag

from chess_zero.board.types import PieceType, Square, square_name


class MoveFlag(IntFlag):
    NONE = 0
    DOUBLE_PUSH = 1
    EN_PASSANT = 2
    CASTLE_KINGSIDE = 4
    CASTLE_QUEENSIDE = 8
    PROMOTION = 16


@dataclass(frozen=True, slots=True)
class Move:
    from_sq: int
    to_sq: int
    promotion: PieceType | None = None
    flags: MoveFlag = field(default=MoveFlag.NONE)

    def is_double_push(self) -> bool:
        return bool(self.flags & MoveFlag.DOUBLE_PUSH)

    def is_en_passant(self) -> bool:
        return bool(self.flags & MoveFlag.EN_PASSANT)

    def is_castle(self) -> bool:
        return bool(self.flags & (MoveFlag.CASTLE_KINGSIDE | MoveFlag.CASTLE_QUEENSIDE))

    def is_promotion(self) -> bool:
        return self.promotion is not None

    def uci(self) -> str:
        s = square_name(self.from_sq) + square_name(self.to_sq)
        if self.promotion is not None:
            s += self.promotion.value
        return s

    @classmethod
    def from_uci(cls, uci: str) -> Move:
        if len(uci) not in (4, 5):
            raise ValueError(f"invalid uci: {uci!r}")
        promotion = PieceType(uci[4]) if len(uci) == 5 else None
        return cls(
            Square.from_name(uci[0:2]),
            Square.from_name(uci[2:4]),
            promotion=promotion,
            flags=MoveFlag.PROMOTION if promotion is not None else MoveFlag.NONE,
        )
