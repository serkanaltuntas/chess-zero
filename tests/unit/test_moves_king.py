from chess_zero.board.fen import board_from_fen
from chess_zero.board.moves import pseudo_legal_moves


def _moves(fen: str) -> set[str]:
    return {m.uci() for m in pseudo_legal_moves(board_from_fen(fen))}


def test_king_center_eight_targets():
    moves = _moves("8/8/8/4K3/8/8/8/8 w - - 0 1")
    expected = {
        "e5d6", "e5e6", "e5f6",
        "e5d5", "e5f5",
        "e5d4", "e5e4", "e5f4",
    }
    assert moves == expected


def test_king_corner_three_targets():
    moves = _moves("8/8/8/8/8/8/8/K7 w - - 0 1")
    assert moves == {"a1a2", "a1b2", "a1b1"}


def test_king_does_not_capture_own_piece():
    moves = _moves("8/8/8/8/8/8/4P3/4K3 w - - 0 1")
    assert "e1e2" not in moves


def test_king_captures_enemy_piece():
    moves = _moves("8/8/8/8/8/8/4p3/4K3 w - - 0 1")
    assert "e1e2" in moves
