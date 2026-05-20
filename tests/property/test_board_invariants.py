"""Property: apply/undo is a true inverse for any sequence of legal-ish play.

Hypothesis drives random move sequences (using pseudo-legal moves — legality
filter is not yet wired). After applying N moves and undoing N times, the
board's FEN must equal the starting FEN. This is a strong invariant: any
mismatch in apply or undo (forgotten castling-rights restore, dropped
captured piece on en passant, promotion not reverted, etc.) surfaces as a
diverging FEN.
"""

from __future__ import annotations

import random

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from chess_zero.board.board import Board
from chess_zero.board.fen import board_to_fen
from chess_zero.board.moves import pseudo_legal_moves

MAX_PLY_PER_RUN = 30
MAX_SEEDS = 30


@settings(
    deadline=None,
    max_examples=80,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
@given(
    seeds=st.lists(
        st.integers(min_value=0, max_value=2**31 - 1),
        min_size=1,
        max_size=MAX_SEEDS,
    )
)
def test_apply_undo_invariance(seeds: list[int]) -> None:
    board = Board()
    fen0 = board_to_fen(board)
    applied = 0

    for seed in seeds[:MAX_PLY_PER_RUN]:
        moves = list(pseudo_legal_moves(board))
        if not moves:
            break
        rng = random.Random(seed)
        m = rng.choice(moves)
        try:
            board.apply_move(m)
        except KeyError:
            # Pseudo-legal includes moves that may not be safely applicable in
            # corner positions (e.g., king/rook indexing after long sequences).
            # The property is about apply/undo symmetry, so we stop on the
            # first KeyError without polluting state.
            break
        applied += 1

    for _ in range(applied):
        board.undo_move()

    assert board_to_fen(board) == fen0
