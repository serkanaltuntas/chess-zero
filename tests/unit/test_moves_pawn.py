from chess_zero.board.fen import board_from_fen
from chess_zero.board.moves import pseudo_legal_moves


def _moves(fen: str) -> set[str]:
    return {m.uci() for m in pseudo_legal_moves(board_from_fen(fen))}


def test_pawn_single_and_double_push_from_starting():
    moves = _moves("8/8/8/8/8/8/4P3/8 w - - 0 1")
    assert "e2e3" in moves
    assert "e2e4" in moves


def test_pawn_no_double_off_starting_rank():
    moves = _moves("8/8/8/8/8/4P3/8/8 w - - 0 1")
    assert "e3e4" in moves
    assert "e3e5" not in moves


def test_pawn_capture():
    moves = _moves("8/8/8/3p1p2/4P3/8/8/8 w - - 0 1")
    assert "e4d5" in moves
    assert "e4f5" in moves


def test_pawn_no_capture_empty_diagonal():
    moves = _moves("8/8/8/8/4P3/8/8/8 w - - 0 1")
    assert "e4d5" not in moves
    assert "e4f5" not in moves


def test_pawn_en_passant():
    fen = "8/8/8/3pP3/8/8/8/8 w - d6 0 1"
    moves = {m.uci(): m for m in pseudo_legal_moves(board_from_fen(fen))}
    assert "e5d6" in moves
    assert moves["e5d6"].is_en_passant()


def test_pawn_promotion_all_variants():
    moves = _moves("8/4P3/8/8/8/8/8/8 w - - 0 1")
    assert {"e7e8q", "e7e8r", "e7e8b", "e7e8n"}.issubset(moves)


def test_pawn_capture_with_promotion():
    moves = _moves("3r4/4P3/8/8/8/8/8/8 w - - 0 1")
    assert {"e7d8q", "e7d8r", "e7d8b", "e7d8n"}.issubset(moves)


def test_pawn_blocked_by_piece():
    moves = _moves("8/8/8/8/8/4n3/4P3/8 w - - 0 1")
    assert "e2e3" not in moves
    assert "e2e4" not in moves


def test_black_pawn_directions():
    moves = _moves("8/4p3/8/8/8/8/8/8 b - - 0 1")
    assert "e7e6" in moves
    assert "e7e5" in moves


def test_black_pawn_promotion():
    moves = _moves("8/8/8/8/8/8/4p3/8 b - - 0 1")
    assert {"e2e1q", "e2e1r", "e2e1b", "e2e1n"}.issubset(moves)
