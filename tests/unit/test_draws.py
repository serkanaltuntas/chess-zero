from chess_zero.board.board import Board
from chess_zero.board.draws import (
    game_result,
    is_fifty_move_draw,
    is_game_over,
    is_insufficient_material,
    is_threefold_repetition,
)
from chess_zero.board.fen import board_from_fen
from chess_zero.board.move import Move
from chess_zero.board.types import Square

# ---------- 50-move ----------


def test_fifty_move_draw_at_100():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K3 w - - 100 60")
    assert is_fifty_move_draw(b)


def test_not_fifty_move_at_99():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K3 w - - 99 60")
    assert not is_fifty_move_draw(b)


# ---------- insufficient material ----------


def test_insufficient_kvk():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    assert is_insufficient_material(b)


def test_insufficient_kn_vs_k():
    b = board_from_fen("4k3/8/8/8/8/8/8/3NK3 w - - 0 1")
    assert is_insufficient_material(b)


def test_insufficient_kb_vs_k():
    b = board_from_fen("4k3/8/8/8/8/8/8/3BK3 w - - 0 1")
    assert is_insufficient_material(b)


def test_sufficient_with_pawn():
    b = board_from_fen("4k3/8/8/8/8/8/3P4/4K3 w - - 0 1")
    assert not is_insufficient_material(b)


def test_sufficient_with_rook():
    b = board_from_fen("4k3/8/8/8/8/8/8/3RK3 w - - 0 1")
    assert not is_insufficient_material(b)


def test_sufficient_with_two_knights_vs_lone_king():
    # Two minor pieces (even both knights) is treated as sufficient here —
    # KNN vs K is technically drawable in practice but not enforced by rule.
    b = board_from_fen("4k3/8/8/8/8/8/8/2N1KN2 w - - 0 1")
    assert not is_insufficient_material(b)


# ---------- threefold repetition ----------


def test_initial_position_in_history():
    b = Board()
    assert b.position_history == [b.position_key()]


def test_threefold_repetition_by_king_shuffle():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    moves = [
        Move(Square.from_name("e1"), Square.from_name("e2")),
        Move(Square.from_name("e8"), Square.from_name("e7")),
        Move(Square.from_name("e2"), Square.from_name("e1")),
        Move(Square.from_name("e7"), Square.from_name("e8")),
        Move(Square.from_name("e1"), Square.from_name("e2")),
        Move(Square.from_name("e8"), Square.from_name("e7")),
        Move(Square.from_name("e2"), Square.from_name("e1")),
        Move(Square.from_name("e7"), Square.from_name("e8")),
    ]
    for m in moves:
        b.apply_move(m)
    # Starting position has now occurred 3 times: at init, after 4 plies, after 8 plies.
    assert is_threefold_repetition(b)


def test_no_repetition_before_third_occurrence():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    moves = [
        Move(Square.from_name("e1"), Square.from_name("e2")),
        Move(Square.from_name("e8"), Square.from_name("e7")),
        Move(Square.from_name("e2"), Square.from_name("e1")),
        Move(Square.from_name("e7"), Square.from_name("e8")),
    ]
    for m in moves:
        b.apply_move(m)
    # Starting position now occurred 2 times only (init + after 4 plies).
    assert not is_threefold_repetition(b)


def test_undo_pops_position_history():
    b = Board()
    initial_len = len(b.position_history)
    b.apply_move(Move(Square.from_name("e2"), Square.from_name("e4")))
    assert len(b.position_history) == initial_len + 1
    b.undo_move()
    assert len(b.position_history) == initial_len


# ---------- is_game_over + game_result ----------


def test_game_over_checkmate_returns_winner_string():
    b = board_from_fen(
        "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
    )
    assert is_game_over(b)
    # White is in checkmate → black wins
    assert game_result(b) == "0-1"


def test_game_over_stalemate_is_draw():
    b = board_from_fen("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1")
    assert is_game_over(b)
    assert game_result(b) == "1/2-1/2"


def test_game_over_fifty_move_is_draw():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K3 w - - 100 60")
    assert is_game_over(b)
    assert game_result(b) == "1/2-1/2"


def test_game_over_insufficient_is_draw():
    b = board_from_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    assert is_game_over(b)
    assert game_result(b) == "1/2-1/2"


def test_game_not_over_initial_position():
    assert not is_game_over(Board())
    assert game_result(Board()) == "*"
