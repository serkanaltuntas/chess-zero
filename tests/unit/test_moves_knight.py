from chess_zero.board.fen import board_from_fen
from chess_zero.board.moves import pseudo_legal_moves


def _moves(fen: str) -> set[str]:
    return {m.uci() for m in pseudo_legal_moves(board_from_fen(fen))}


def test_knight_center_eight_targets():
    moves = _moves("8/8/8/4N3/8/8/8/8 w - - 0 1")
    expected = {"e5d7", "e5f7", "e5c6", "e5g6", "e5c4", "e5g4", "e5d3", "e5f3"}
    assert expected == moves


def test_knight_corner_two_targets():
    moves = _moves("8/8/8/8/8/8/8/N7 w - - 0 1")
    assert moves == {"a1b3", "a1c2"}


def test_knight_blocked_by_own_piece():
    moves = _moves("8/8/8/8/8/8/3P4/1N6 w - - 0 1")
    assert "b1d2" not in moves
    assert "b1c3" in moves
    assert "b1a3" in moves


def test_knight_captures_enemy_on_target():
    moves = _moves("8/8/8/8/8/2p5/8/1N6 w - - 0 1")
    assert "b1c3" in moves  # captures pawn on c3
    assert "b1a3" in moves  # empty
    assert "b1d2" in moves  # empty
