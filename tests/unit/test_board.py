from chess_zero.board.board import Board
from chess_zero.board.types import Color, Piece, PieceType, Square


def test_initial_position_corners():
    b = Board()
    assert b.piece_at(Square.from_name("a1")) == Piece(PieceType.ROOK, Color.WHITE)
    assert b.piece_at(Square.from_name("h1")) == Piece(PieceType.ROOK, Color.WHITE)
    assert b.piece_at(Square.from_name("a8")) == Piece(PieceType.ROOK, Color.BLACK)
    assert b.piece_at(Square.from_name("h8")) == Piece(PieceType.ROOK, Color.BLACK)


def test_initial_position_kings_queens():
    b = Board()
    assert b.piece_at(Square.from_name("e1")) == Piece(PieceType.KING, Color.WHITE)
    assert b.piece_at(Square.from_name("d1")) == Piece(PieceType.QUEEN, Color.WHITE)
    assert b.piece_at(Square.from_name("e8")) == Piece(PieceType.KING, Color.BLACK)
    assert b.piece_at(Square.from_name("d8")) == Piece(PieceType.QUEEN, Color.BLACK)


def test_initial_position_pawns():
    b = Board()
    for f in range(8):
        assert b.piece_at(Square.from_name("abcdefgh"[f] + "2")) == Piece(
            PieceType.PAWN, Color.WHITE
        )
        assert b.piece_at(Square.from_name("abcdefgh"[f] + "7")) == Piece(
            PieceType.PAWN, Color.BLACK
        )


def test_initial_position_empty_middle():
    b = Board()
    assert b.piece_at(Square.from_name("e4")) is None
    assert b.piece_at(Square.from_name("d5")) is None


def test_initial_position_metadata():
    b = Board()
    assert b.side_to_move == Color.WHITE
    assert b.castling_rights == {"K", "Q", "k", "q"}
    assert b.en_passant_square is None
    assert b.halfmove_clock == 0
    assert b.fullmove_number == 1


def test_set_remove_piece():
    b = Board()
    sq = Square.from_name("e4")
    p = Piece(PieceType.PAWN, Color.WHITE)
    b.set_piece_at(sq, p)
    assert b.piece_at(sq) == p
    b.remove_piece(sq)
    assert b.piece_at(sq) is None
