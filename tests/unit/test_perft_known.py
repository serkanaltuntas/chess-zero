"""Spot-check perft against well-known starting-position values.

These constants are documented across every chess programming reference; if
they don't pass, the oracle suite (tests/oracles/test_perft.py) will reveal
where the discrepancy lies.
"""

from chess_zero.board.board import Board
from chess_zero.board.perft import perft


def test_perft_initial_depth_1():
    assert perft(Board(), 1) == 20


def test_perft_initial_depth_2():
    assert perft(Board(), 2) == 400


def test_perft_initial_depth_3():
    assert perft(Board(), 3) == 8902
