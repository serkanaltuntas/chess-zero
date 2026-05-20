from chess_zero.board.board import Board
from chess_zero.board.fen import board_from_fen, board_to_fen
from chess_zero.board.move import Move, MoveFlag
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


# ---------- apply/undo: quiet, capture, double push ----------


def test_apply_quiet_move_flips_side():
    b = Board()
    b.apply_move(
        Move(
            Square.from_name("e2"),
            Square.from_name("e4"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    assert b.side_to_move == Color.BLACK
    assert b.piece_at(Square.from_name("e2")) is None
    assert b.piece_at(Square.from_name("e4")) == Piece(PieceType.PAWN, Color.WHITE)


def test_apply_double_push_sets_en_passant_square():
    b = Board()
    b.apply_move(
        Move(
            Square.from_name("e2"),
            Square.from_name("e4"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    assert b.en_passant_square == Square.from_name("e3")


def test_apply_single_push_does_not_set_en_passant():
    b = board_from_fen("8/8/8/8/8/8/4P3/8 w - - 0 1")
    b.apply_move(Move(Square.from_name("e2"), Square.from_name("e3")))
    assert b.en_passant_square is None


def test_apply_capture_resets_halfmove_clock():
    b = board_from_fen("8/8/8/3p4/4P3/8/8/8 w - - 5 10")
    b.apply_move(Move(Square.from_name("e4"), Square.from_name("d5")))
    assert b.halfmove_clock == 0
    assert b.piece_at(Square.from_name("d5")) == Piece(PieceType.PAWN, Color.WHITE)


def test_apply_fullmove_increments_after_black_move():
    b = Board()
    b.apply_move(
        Move(
            Square.from_name("e2"),
            Square.from_name("e4"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    assert b.fullmove_number == 1
    b.apply_move(
        Move(
            Square.from_name("e7"),
            Square.from_name("e5"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    assert b.fullmove_number == 2


def test_undo_restores_initial_position():
    b = Board()
    fen_before = board_to_fen(b)
    b.apply_move(
        Move(
            Square.from_name("e2"),
            Square.from_name("e4"),
            flags=MoveFlag.DOUBLE_PUSH,
        )
    )
    b.undo_move()
    assert board_to_fen(b) == fen_before


def test_undo_restores_capture():
    fen = "8/8/8/3p4/4P3/8/8/8 w - - 5 10"
    b = board_from_fen(fen)
    b.apply_move(Move(Square.from_name("e4"), Square.from_name("d5")))
    b.undo_move()
    assert board_to_fen(b) == fen


# ---------- apply/undo: en passant ----------


def test_apply_en_passant_removes_captured_pawn():
    b = board_from_fen("8/8/8/3pP3/8/8/8/8 w - d6 0 1")
    b.apply_move(
        Move(
            Square.from_name("e5"),
            Square.from_name("d6"),
            flags=MoveFlag.EN_PASSANT,
        )
    )
    assert b.piece_at(Square.from_name("d6")) == Piece(PieceType.PAWN, Color.WHITE)
    # Black pawn was on d5, not d6
    assert b.piece_at(Square.from_name("d5")) is None


def test_undo_en_passant_restores_captured_pawn():
    fen = "8/8/8/3pP3/8/8/8/8 w - d6 0 1"
    b = board_from_fen(fen)
    b.apply_move(
        Move(
            Square.from_name("e5"),
            Square.from_name("d6"),
            flags=MoveFlag.EN_PASSANT,
        )
    )
    b.undo_move()
    assert board_to_fen(b) == fen


# ---------- apply/undo: promotion ----------


def test_apply_promotion_to_queen():
    b = board_from_fen("8/4P3/8/8/8/8/8/8 w - - 0 1")
    b.apply_move(
        Move(
            Square.from_name("e7"),
            Square.from_name("e8"),
            promotion=PieceType.QUEEN,
            flags=MoveFlag.PROMOTION,
        )
    )
    assert b.piece_at(Square.from_name("e8")) == Piece(PieceType.QUEEN, Color.WHITE)


def test_undo_promotion_restores_pawn():
    fen = "8/4P3/8/8/8/8/8/8 w - - 0 1"
    b = board_from_fen(fen)
    b.apply_move(
        Move(
            Square.from_name("e7"),
            Square.from_name("e8"),
            promotion=PieceType.QUEEN,
            flags=MoveFlag.PROMOTION,
        )
    )
    b.undo_move()
    assert board_to_fen(b) == fen


# ---------- apply/undo: castling ----------


def test_apply_castle_kingside_moves_rook():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K2R w K - 0 1")
    b.apply_move(
        Move(
            Square.from_name("e1"),
            Square.from_name("g1"),
            flags=MoveFlag.CASTLE_KINGSIDE,
        )
    )
    assert b.piece_at(Square.from_name("g1")) == Piece(PieceType.KING, Color.WHITE)
    assert b.piece_at(Square.from_name("f1")) == Piece(PieceType.ROOK, Color.WHITE)
    assert b.piece_at(Square.from_name("h1")) is None
    assert "K" not in b.castling_rights


def test_undo_castle_kingside():
    fen = "4k3/8/8/8/8/8/8/4K2R w K - 0 1"
    b = board_from_fen(fen)
    b.apply_move(
        Move(
            Square.from_name("e1"),
            Square.from_name("g1"),
            flags=MoveFlag.CASTLE_KINGSIDE,
        )
    )
    b.undo_move()
    assert board_to_fen(b) == fen


def test_apply_castle_queenside_moves_rook():
    b = board_from_fen("4k3/8/8/8/8/8/8/R3K3 w Q - 0 1")
    b.apply_move(
        Move(
            Square.from_name("e1"),
            Square.from_name("c1"),
            flags=MoveFlag.CASTLE_QUEENSIDE,
        )
    )
    assert b.piece_at(Square.from_name("c1")) == Piece(PieceType.KING, Color.WHITE)
    assert b.piece_at(Square.from_name("d1")) == Piece(PieceType.ROOK, Color.WHITE)
    assert b.piece_at(Square.from_name("a1")) is None
    assert "Q" not in b.castling_rights


# ---------- castling rights bookkeeping ----------


def test_king_move_drops_both_castling_rights():
    b = board_from_fen("4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1")
    b.apply_move(Move(Square.from_name("e1"), Square.from_name("e2")))
    assert "K" not in b.castling_rights
    assert "Q" not in b.castling_rights


def test_rook_a1_move_drops_q_only():
    b = board_from_fen("4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1")
    b.apply_move(Move(Square.from_name("a1"), Square.from_name("a2")))
    assert "K" in b.castling_rights
    assert "Q" not in b.castling_rights


def test_capturing_rook_on_h8_drops_k_right():
    # White rook captures black rook on h8 → drops black's k right
    b = board_from_fen("4k2r/8/8/8/8/8/8/7R w k - 0 1")
    b.apply_move(Move(Square.from_name("h1"), Square.from_name("h8")))
    assert "k" not in b.castling_rights
