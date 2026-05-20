"""Perft oracle: chess-zero board vs python-chess for canonical positions.

`python-chess` is allowed ONLY in this directory; the conftest.py guard
fails the suite if anything under `chess_zero/` ever imports it. Standard
positions covered:

- starting position
- Kiwipete (Steven Edwards' "every chess rule in one position")
- Position 3-6 from the Chess Programming Wiki perft suite

Depths 1-3 are exercised for all six positions. Depth 4 is enabled for the
starting position only — full depth-4 across all positions would push the
pure-Python board into multi-minute test runtimes, which is overkill for a
correctness gate that already finds rule-violation bugs at depth 3.
"""

from __future__ import annotations

import chess as oracle  # python-chess — allowed here only
import pytest

from chess_zero.board.fen import board_from_fen
from chess_zero.board.perft import perft

STARTING = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
KIWIPETE = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
POSITION_3 = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"
POSITION_4 = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2pP/R2Q1RK1 w kq - 0 1"
POSITION_5 = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"
POSITION_6 = "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10"

POSITIONS = [
    (STARTING, "starting"),
    (KIWIPETE, "kiwipete"),
    (POSITION_3, "position3"),
    (POSITION_4, "position4"),
    (POSITION_5, "position5"),
    (POSITION_6, "position6"),
]


def _oracle_perft(board: oracle.Board, depth: int) -> int:
    if depth == 0:
        return 1
    total = 0
    for move in board.legal_moves:
        board.push(move)
        total += _oracle_perft(board, depth - 1)
        board.pop()
    return total


@pytest.mark.parametrize("fen,name", POSITIONS, ids=[p[1] for p in POSITIONS])
@pytest.mark.parametrize("depth", [1, 2, 3])
def test_perft_matches_python_chess(fen: str, name: str, depth: int) -> None:
    ours = perft(board_from_fen(fen), depth)
    theirs = _oracle_perft(oracle.Board(fen), depth)
    assert ours == theirs, f"perft({name}, {depth}): ours={ours} theirs={theirs}"


def test_perft_starting_depth_4_matches_python_chess() -> None:
    ours = perft(board_from_fen(STARTING), 4)
    theirs = _oracle_perft(oracle.Board(STARTING), 4)
    assert ours == theirs
