from chess_zero.board.types import (
    Color,
    Piece,
    PieceType,
    Square,
    file_of,
    rank_of,
    square,
    square_name,
)


def test_color_opposite():
    assert Color.WHITE.opposite() == Color.BLACK
    assert Color.BLACK.opposite() == Color.WHITE


def test_piece_equality():
    a = Piece(PieceType.KNIGHT, Color.WHITE)
    b = Piece(PieceType.KNIGHT, Color.WHITE)
    c = Piece(PieceType.KNIGHT, Color.BLACK)
    assert a == b
    assert a != c


def test_piece_symbol():
    assert Piece(PieceType.KING, Color.WHITE).symbol() == "K"
    assert Piece(PieceType.KING, Color.BLACK).symbol() == "k"
    assert Piece(PieceType.PAWN, Color.WHITE).symbol() == "P"
    assert Piece(PieceType.PAWN, Color.BLACK).symbol() == "p"


def test_piece_from_symbol():
    assert Piece.from_symbol("Q") == Piece(PieceType.QUEEN, Color.WHITE)
    assert Piece.from_symbol("n") == Piece(PieceType.KNIGHT, Color.BLACK)


def test_square_from_coordinates():
    assert square(file=0, rank=0) == 0
    assert square(file=7, rank=0) == 7
    assert square(file=0, rank=7) == 56
    assert square(file=7, rank=7) == 63


def test_file_rank_of():
    assert file_of(0) == 0
    assert rank_of(0) == 0
    assert file_of(63) == 7
    assert rank_of(63) == 7
    assert file_of(28) == 4
    assert rank_of(28) == 3


def test_square_name():
    assert square_name(0) == "a1"
    assert square_name(63) == "h8"
    assert square_name(28) == "e4"


def test_square_from_name():
    assert Square.from_name("a1") == 0
    assert Square.from_name("e4") == 28
    assert Square.from_name("h8") == 63
