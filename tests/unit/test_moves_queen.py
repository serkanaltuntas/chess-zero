from chess_zero.board.fen import board_from_fen
from chess_zero.board.moves import pseudo_legal_moves


def _moves(fen: str) -> set[str]:
    return {m.uci() for m in pseudo_legal_moves(board_from_fen(fen))}


def test_queen_combines_rook_and_bishop_moves():
    moves = _moves("8/8/8/8/3Q4/8/8/8 w - - 0 1")
    rook_targets = {
        "d4d1", "d4d2", "d4d3", "d4d5", "d4d6", "d4d7", "d4d8",
        "d4a4", "d4b4", "d4c4", "d4e4", "d4f4", "d4g4", "d4h4",
    }
    bishop_targets = {
        "d4a1", "d4b2", "d4c3", "d4e5", "d4f6", "d4g7", "d4h8",
        "d4a7", "d4b6", "d4c5", "d4e3", "d4f2", "d4g1",
    }
    assert moves == rook_targets | bishop_targets
