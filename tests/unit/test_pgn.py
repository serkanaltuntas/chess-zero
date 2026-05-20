import pytest

from chess_zero.board.board import Board
from chess_zero.board.fen import board_from_fen
from chess_zero.board.move import Move, MoveFlag
from chess_zero.board.pgn import (
    game_san_moves,
    move_to_san,
    moves_from_san_text,
    san_to_move,
)
from chess_zero.board.types import PieceType, Square

# ---------- move_to_san ----------


def test_san_pawn_push():
    b = Board()
    m = Move(
        Square.from_name("e2"),
        Square.from_name("e4"),
        flags=MoveFlag.DOUBLE_PUSH,
    )
    assert move_to_san(b, m) == "e4"


def test_san_pawn_single_push():
    b = Board()
    m = Move(Square.from_name("e2"), Square.from_name("e3"))
    assert move_to_san(b, m) == "e3"


def test_san_knight_move():
    b = Board()
    m = Move(Square.from_name("g1"), Square.from_name("f3"))
    assert move_to_san(b, m) == "Nf3"


def test_san_pawn_capture_uses_file():
    b = board_from_fen("8/8/8/3p4/4P3/8/8/4K2k w - - 0 1")
    m = Move(Square.from_name("e4"), Square.from_name("d5"))
    assert move_to_san(b, m) == "exd5"


def test_san_piece_capture():
    b = board_from_fen("8/8/8/3p4/8/4N3/8/4K2k w - - 0 1")
    m = Move(Square.from_name("e3"), Square.from_name("d5"))
    assert move_to_san(b, m) == "Nxd5"


def test_san_kingside_castle():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K2R w K - 0 1")
    m = Move(
        Square.from_name("e1"),
        Square.from_name("g1"),
        flags=MoveFlag.CASTLE_KINGSIDE,
    )
    assert move_to_san(b, m) == "O-O"


def test_san_queenside_castle():
    b = board_from_fen("4k3/8/8/8/8/8/8/R3K3 w Q - 0 1")
    m = Move(
        Square.from_name("e1"),
        Square.from_name("c1"),
        flags=MoveFlag.CASTLE_QUEENSIDE,
    )
    assert move_to_san(b, m) == "O-O-O"


def test_san_promotion():
    # Black king on h8 so the e8 square is empty for promotion push.
    # The promoted queen on e8 attacks h8 along rank 8 → check marker added.
    b = board_from_fen("7k/4P3/8/8/8/8/8/4K3 w - - 0 1")
    m = Move(
        Square.from_name("e7"),
        Square.from_name("e8"),
        promotion=PieceType.QUEEN,
        flags=MoveFlag.PROMOTION,
    )
    assert move_to_san(b, m) == "e8=Q+"


def test_san_check_marker():
    # Black king on h8, white rook on e1 → Re8 attacks rank 8 = check on h8.
    b = board_from_fen("7k/8/8/8/8/8/8/4R2K w - - 0 1")
    m = Move(Square.from_name("e1"), Square.from_name("e8"))
    assert move_to_san(b, m) == "Re8+"


def test_san_checkmate_marker():
    # Back-rank mate: black king h8 boxed in by own pawns f7/g7/h7, white rook
    # delivers Re8 sealing rank 8 → mate.
    b = board_from_fen("7k/5ppp/8/8/8/8/8/4R2K w - - 0 1")
    m = Move(Square.from_name("e1"), Square.from_name("e8"))
    assert move_to_san(b, m) == "Re8#"


def test_san_disambiguation_by_file():
    # Two knights both attacking the same square
    b = board_from_fen("8/8/8/8/3N1N2/8/8/4K2k w - - 0 1")
    m = Move(Square.from_name("d4"), Square.from_name("e6"))
    assert move_to_san(b, m) == "Nde6"


def test_san_disambiguation_by_rank():
    # Two rooks on the same file, both can move to e5
    b = board_from_fen("8/8/8/4R3/8/8/4R3/4K2k w - - 0 1")
    m = Move(Square.from_name("e2"), Square.from_name("e4"))
    assert move_to_san(b, m) == "R2e4"


# ---------- san_to_move ----------


def test_san_to_move_pawn_push():
    b = Board()
    m = san_to_move(b, "e4")
    assert m.from_sq == Square.from_name("e2")
    assert m.to_sq == Square.from_name("e4")


def test_san_to_move_knight():
    b = Board()
    m = san_to_move(b, "Nf3")
    assert m.from_sq == Square.from_name("g1")
    assert m.to_sq == Square.from_name("f3")


def test_san_to_move_castle():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K2R w K - 0 1")
    m = san_to_move(b, "O-O")
    assert m.is_castle()


def test_san_to_move_promotion():
    # Black king on h8 so e8 is empty for the promotion push.
    b = board_from_fen("7k/4P3/8/8/8/8/8/4K3 w - - 0 1")
    m = san_to_move(b, "e8=Q")
    assert m.promotion is PieceType.QUEEN


def test_san_to_move_strips_check_marker():
    # Black king on h8 so the rook's e-file path to e8 is unblocked.
    b = board_from_fen("7k/8/8/8/8/8/8/4R2K w - - 0 1")
    m = san_to_move(b, "Re8+")
    assert m.to_sq == Square.from_name("e8")


def test_san_to_move_raises_on_illegal():
    b = Board()
    with pytest.raises(ValueError):
        san_to_move(b, "e5")  # not legal from starting position


def test_san_to_move_raises_on_unparseable():
    b = Board()
    with pytest.raises(ValueError):
        san_to_move(b, "garbage")


# ---------- roundtrip game-level ----------


def test_game_san_moves_records_history():
    b = Board()
    b.apply_move(
        Move(
            Square.from_name("e2"),
            Square.from_name("e4"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    b.apply_move(
        Move(
            Square.from_name("e7"),
            Square.from_name("e5"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    b.apply_move(Move(Square.from_name("g1"), Square.from_name("f3")))
    sans = game_san_moves(b)
    assert sans == ["e4", "e5", "Nf3"]


def test_moves_from_san_text_applies_to_board():
    b = Board()
    moves = moves_from_san_text(b, "1. e4 e5 2. Nf3 Nc6")
    assert len(moves) == 4
    # Board has been advanced by the parsed moves
    assert b.piece_at(Square.from_name("e4")) is not None
    assert b.piece_at(Square.from_name("f3")) is not None


def test_roundtrip_short_game():
    b = Board()
    b.apply_move(
        Move(
            Square.from_name("e2"),
            Square.from_name("e4"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    b.apply_move(
        Move(
            Square.from_name("e7"),
            Square.from_name("e5"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    b.apply_move(Move(Square.from_name("g1"), Square.from_name("f3")))
    sans = game_san_moves(b)

    # Replay from start using parsed SAN — should reach the same FEN
    fresh = Board()
    moves_from_san_text(fresh, " ".join(sans))
    from chess_zero.board.fen import board_to_fen

    assert board_to_fen(fresh) == board_to_fen(b)
