from chess_zero.board.fen import board_from_fen
from chess_zero.board.legality import (
    is_checkmate,
    is_in_check,
    is_square_attacked_by,
    is_stalemate,
    legal_moves,
)
from chess_zero.board.types import Color, Square

# ---------- is_square_attacked_by ----------


def test_attacked_by_pawn():
    b = board_from_fen("8/8/8/8/8/4P3/8/8 w - - 0 1")
    assert is_square_attacked_by(b, Square.from_name("d4"), Color.WHITE)
    assert is_square_attacked_by(b, Square.from_name("f4"), Color.WHITE)
    assert not is_square_attacked_by(b, Square.from_name("e4"), Color.WHITE)


def test_attacked_by_black_pawn():
    b = board_from_fen("8/8/4p3/8/8/8/8/8 w - - 0 1")
    assert is_square_attacked_by(b, Square.from_name("d5"), Color.BLACK)
    assert is_square_attacked_by(b, Square.from_name("f5"), Color.BLACK)


def test_attacked_by_knight():
    b = board_from_fen("8/8/8/8/4N3/8/8/8 w - - 0 1")
    assert is_square_attacked_by(b, Square.from_name("f6"), Color.WHITE)
    assert is_square_attacked_by(b, Square.from_name("d6"), Color.WHITE)


def test_attacked_by_king():
    b = board_from_fen("8/8/8/4K3/8/8/8/8 w - - 0 1")
    assert is_square_attacked_by(b, Square.from_name("e6"), Color.WHITE)
    assert is_square_attacked_by(b, Square.from_name("d4"), Color.WHITE)
    assert not is_square_attacked_by(b, Square.from_name("e3"), Color.WHITE)


def test_attacked_by_bishop_diagonal():
    b = board_from_fen("8/8/8/4B3/8/8/8/8 w - - 0 1")
    assert is_square_attacked_by(b, Square.from_name("a1"), Color.WHITE)
    assert is_square_attacked_by(b, Square.from_name("h8"), Color.WHITE)


def test_sliding_attack_blocked_by_intervening_piece():
    # Rook on e4, white pawn on d4 — does NOT attack a4 (pawn blocks)
    b = board_from_fen("8/8/8/8/3PR3/8/8/8 w - - 0 1")
    assert not is_square_attacked_by(b, Square.from_name("a4"), Color.WHITE)
    assert is_square_attacked_by(b, Square.from_name("e8"), Color.WHITE)


def test_queen_attacks_diagonal_and_straight():
    b = board_from_fen("8/8/8/4Q3/8/8/8/8 w - - 0 1")
    assert is_square_attacked_by(b, Square.from_name("e1"), Color.WHITE)
    assert is_square_attacked_by(b, Square.from_name("a1"), Color.WHITE)
    assert is_square_attacked_by(b, Square.from_name("h8"), Color.WHITE)


# ---------- in_check / mate / stalemate ----------


def test_in_check_by_rook():
    b = board_from_fen("4k3/8/8/8/8/8/4R3/4K3 b - - 0 1")
    assert is_in_check(b, Color.BLACK)


def test_not_in_check_initial_position():
    from chess_zero.board.board import Board

    assert not is_in_check(Board(), Color.WHITE)
    assert not is_in_check(Board(), Color.BLACK)


def test_checkmate_fools_mate():
    b = board_from_fen(
        "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
    )
    assert is_in_check(b, Color.WHITE)
    assert is_checkmate(b)


def test_stalemate_classic():
    # Black king on h8, white king on f7, white queen on g6 — black to move,
    # no legal moves and not in check.
    b = board_from_fen("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1")
    assert not is_in_check(b, Color.BLACK)
    assert is_stalemate(b)
    assert not is_checkmate(b)


# ---------- legal_moves filter: pin and self-check ----------


def test_pinned_piece_cannot_move_off_pin_line():
    # Black king on e8, black bishop on e7 pinned by white rook on e1
    b = board_from_fen("4k3/4b3/8/8/8/8/8/4R2K b - - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    # Bishop cannot move off the e-file
    assert "e7d6" not in moves
    assert "e7f6" not in moves
    assert "e7d8" not in moves
    assert "e7f8" not in moves


def test_legal_moves_includes_king_evasion_under_check():
    # White king on e1, black rook on e2 (white in check)
    b = board_from_fen("4k3/8/8/8/8/8/4r3/4K3 w - - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    # King must escape check — staying on e-file is bad
    assert "e1d1" in moves or "e1f1" in moves or "e1e2" in moves


# ---------- castling legality guards (E3) ----------


def test_cannot_castle_while_in_check():
    # White king on e1, black rook on e8 puts white in check
    b = board_from_fen("4r3/8/8/8/8/8/8/4K2R w K - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert "e1g1" not in moves


def test_cannot_castle_through_attacked_square():
    # White king on e1, black rook on f8 attacks f1 (king path square)
    b = board_from_fen("5r2/8/8/8/8/8/8/4K2R w K - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert "e1g1" not in moves


def test_cannot_castle_into_check():
    # White king on e1, black rook on g8 attacks g1 (king destination)
    b = board_from_fen("6r1/8/8/8/8/8/8/4K2R w K - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert "e1g1" not in moves


def test_kingside_castle_legal_when_clear():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K2R w K - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert "e1g1" in moves


def test_queenside_castle_legal_when_clear():
    b = board_from_fen("4k3/8/8/8/8/8/8/R3K3 w Q - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert "e1c1" in moves


def test_queenside_castle_legal_when_b1_attacked_only():
    # The b1 square is NOT on king's path; only c1, d1, e1 matter.
    # Black knight on a3 attacks b1 but does not attack c1/d1/e1 — castle legal.
    b = board_from_fen("4k3/8/8/8/8/n7/8/R3K3 w Q - 0 1")
    moves = {m.uci() for m in legal_moves(b)}
    assert "e1c1" in moves
