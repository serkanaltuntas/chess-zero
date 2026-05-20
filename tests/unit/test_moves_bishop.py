from chess_zero.board.fen import board_from_fen
from chess_zero.board.moves import pseudo_legal_moves


def _moves(fen: str) -> set[str]:
    return {m.uci() for m in pseudo_legal_moves(board_from_fen(fen))}


def test_bishop_center_empty_board():
    moves = _moves("8/8/8/4B3/8/8/8/8 w - - 0 1")
    expected = {
        "e5d6", "e5c7", "e5b8",
        "e5f6", "e5g7", "e5h8",
        "e5d4", "e5c3", "e5b2", "e5a1",
        "e5f4", "e5g3", "e5h2",
    }
    assert moves == expected


def test_bishop_blocked_by_own_piece():
    moves = _moves("8/8/2P5/8/4B3/8/8/8 w - - 0 1")
    assert "e4d5" in moves
    assert "e4c6" not in moves


def test_bishop_captures_enemy_and_stops():
    moves = _moves("8/8/2p5/8/4B3/8/8/8 w - - 0 1")
    assert "e4d5" in moves
    assert "e4c6" in moves
    assert "e4b7" not in moves
