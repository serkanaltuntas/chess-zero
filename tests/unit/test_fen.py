import pytest

from chess_zero.board.fen import board_from_fen, board_to_fen
from chess_zero.board.types import Color, Piece, PieceType, Square

INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
KIWIPETE = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
AFTER_E4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
ENDGAME = "8/8/8/3k4/8/3K4/8/8 w - - 5 60"


def test_fen_initial_position():
    b = board_from_fen(INITIAL_FEN)
    assert b.side_to_move == Color.WHITE
    assert b.castling_rights == {"K", "Q", "k", "q"}
    assert b.en_passant_square is None
    assert b.halfmove_clock == 0
    assert b.fullmove_number == 1
    assert b.piece_at(Square.from_name("a1")) == Piece(PieceType.ROOK, Color.WHITE)


def test_fen_kiwipete():
    b = board_from_fen(KIWIPETE)
    assert b.side_to_move == Color.WHITE
    assert b.piece_at(Square.from_name("d5")) == Piece(PieceType.PAWN, Color.WHITE)
    assert b.piece_at(Square.from_name("e5")) == Piece(PieceType.KNIGHT, Color.WHITE)


def test_fen_en_passant_field():
    b = board_from_fen(AFTER_E4)
    assert b.en_passant_square == Square.from_name("e3")
    assert b.side_to_move == Color.BLACK


def test_fen_no_castling_rights():
    b = board_from_fen(ENDGAME)
    assert b.castling_rights == set()
    assert b.halfmove_clock == 5
    assert b.fullmove_number == 60


def test_fen_roundtrip_initial():
    assert board_to_fen(board_from_fen(INITIAL_FEN)) == INITIAL_FEN


def test_fen_roundtrip_kiwipete():
    assert board_to_fen(board_from_fen(KIWIPETE)) == KIWIPETE


def test_fen_roundtrip_after_e4():
    assert board_to_fen(board_from_fen(AFTER_E4)) == AFTER_E4


def test_fen_roundtrip_endgame():
    assert board_to_fen(board_from_fen(ENDGAME)) == ENDGAME


def test_fen_malformed_field_count():
    with pytest.raises(ValueError):
        board_from_fen("not a real fen string")


def test_fen_malformed_rank_count():
    with pytest.raises(ValueError):
        board_from_fen("rnbqkbnr/pppppppp/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
