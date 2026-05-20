from chess_zero.board.fen import board_from_fen
from chess_zero.board.moves import pseudo_legal_moves


def _moves(fen: str) -> set[str]:
    return {m.uci() for m in pseudo_legal_moves(board_from_fen(fen))}


def test_rook_center_empty_board():
    moves = _moves("8/8/8/8/3R4/8/8/8 w - - 0 1")
    expected = {
        "d4d1", "d4d2", "d4d3", "d4d5", "d4d6", "d4d7", "d4d8",
        "d4a4", "d4b4", "d4c4", "d4e4", "d4f4", "d4g4", "d4h4",
    }
    assert moves == expected


def test_rook_captures_enemy_then_stops():
    moves = _moves("8/8/8/3r4/8/3R4/8/8 w - - 0 1")
    assert "d3d5" in moves
    assert "d3d6" not in moves


def test_rook_blocked_by_own_piece():
    moves = _moves("8/8/8/3R4/3P4/8/8/8 w - - 0 1")
    assert "d5d4" not in moves
    assert "d5d3" not in moves
