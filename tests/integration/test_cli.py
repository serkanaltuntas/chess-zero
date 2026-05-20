"""End-to-end smoke tests for the chess-zero CLI."""

from __future__ import annotations

import random

from chess_zero.board.board import Board
from chess_zero.board.draws import game_result, is_game_over
from chess_zero.board.legality import legal_moves
from chess_zero.cli import display_board, main


def test_random_game_terminates_with_legal_result():
    rng = random.Random(42)
    board = Board()
    max_plies = 1000
    plies = 0
    while not is_game_over(board) and plies < max_plies:
        moves = list(legal_moves(board))
        if not moves:
            break
        board.apply_move(rng.choice(moves))
        plies += 1
    assert plies <= max_plies
    if is_game_over(board):
        assert game_result(board) in {"1-0", "0-1", "1/2-1/2"}


def test_cli_perft_subcommand_prints_count(capsys):
    exit_code = main(["perft", "--depth", "1"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "20" in captured.out  # perft(1) of starting position


def test_cli_perft_with_custom_fen(capsys):
    # Two kings only — perft(1) for white king on e1 = 5 legal moves
    # (e1d1, e1d2, e1e2, e1f1, e1f2 — none into attack from a8 black king)
    exit_code = main(
        [
            "perft",
            "--depth",
            "1",
            "--fen",
            "k7/8/8/8/8/8/8/4K3 w - - 0 1",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "= 5" in captured.out


def test_cli_play_random_vs_random_runs(capsys):
    exit_code = main(
        ["play", "--seed", "0", "--max-plies", "60"]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "result:" in captured.out


def test_cli_play_emits_pgn_with_verbose(capsys):
    exit_code = main(
        ["play", "--seed", "0", "--max-plies", "6", "--verbose"]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    # Verbose stream should mention move numbers
    assert "1." in captured.out


def test_display_board_renders_grid():
    out = display_board(Board())
    # File legend across the bottom (rendered with 2-space padding between letters).
    assert "a" in out and "h" in out
    assert out.splitlines()[-1].strip().startswith("a")
    # White rook on a1 should appear on the bottom rank row, starts with "1".
    rows = out.splitlines()
    assert rows[-2].startswith("1 ")
    assert "R" in rows[-2]
