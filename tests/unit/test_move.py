from chess_zero.board.move import Move, MoveFlag
from chess_zero.board.types import PieceType, Square


def test_move_equality():
    a = Move(Square.from_name("e2"), Square.from_name("e4"))
    b = Move(Square.from_name("e2"), Square.from_name("e4"))
    assert a == b


def test_move_uci_quiet():
    m = Move(Square.from_name("e2"), Square.from_name("e4"))
    assert m.uci() == "e2e4"


def test_move_uci_promotion():
    m = Move(
        Square.from_name("e7"),
        Square.from_name("e8"),
        promotion=PieceType.QUEEN,
        flags=MoveFlag.PROMOTION,
    )
    assert m.uci() == "e7e8q"


def test_move_from_uci_quiet():
    assert Move.from_uci("e2e4") == Move(
        Square.from_name("e2"), Square.from_name("e4")
    )


def test_move_from_uci_promotion():
    m = Move.from_uci("e7e8q")
    assert m.from_sq == Square.from_name("e7")
    assert m.to_sq == Square.from_name("e8")
    assert m.promotion is PieceType.QUEEN
    assert m.is_promotion()


def test_move_flag_helpers():
    m = Move(0, 16, flags=MoveFlag.DOUBLE_PUSH)
    assert m.is_double_push()
    assert not m.is_en_passant()
    assert not m.is_castle()


def test_move_castle_flags():
    ks = Move(0, 0, flags=MoveFlag.CASTLE_KINGSIDE)
    qs = Move(0, 0, flags=MoveFlag.CASTLE_QUEENSIDE)
    assert ks.is_castle()
    assert qs.is_castle()


def test_move_from_uci_invalid_length():
    import pytest

    with pytest.raises(ValueError):
        Move.from_uci("e2")
