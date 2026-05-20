import pytest

from chess_zero.agents import Agent, MinimaxAgent, RandomAgent
from chess_zero.board.board import Board
from chess_zero.board.fen import board_from_fen
from chess_zero.board.legality import legal_moves
from chess_zero.board.types import PieceType

# ---------- Agent ABC contract ----------


def test_agent_abc_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Agent()  # type: ignore[abstract]


# ---------- RandomAgent ----------


def test_random_agent_picks_legal_move():
    agent = RandomAgent(seed=0)
    board = Board()
    move = agent.select_move(board)
    assert move in list(legal_moves(board))


def test_random_agent_deterministic_with_seed():
    a = RandomAgent(seed=42)
    b = RandomAgent(seed=42)
    board = Board()
    assert a.select_move(board) == b.select_move(board)


def test_random_agent_different_seeds_diverge():
    a = RandomAgent(seed=0)
    b = RandomAgent(seed=999)
    # Not guaranteed, but extremely likely given 20 legal opening moves.
    a_choices = [a.select_move(Board()) for _ in range(5)]
    b_choices = [b.select_move(Board()) for _ in range(5)]
    assert a_choices != b_choices


def test_random_agent_raises_when_no_legal_moves():
    # Stalemate position — side to move has no legal moves.
    board = board_from_fen("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1")
    agent = RandomAgent(seed=0)
    with pytest.raises(ValueError):
        agent.select_move(board)


# ---------- MinimaxAgent ----------


def test_minimax_agent_picks_legal_move():
    agent = MinimaxAgent(depth=2)
    board = Board()
    move = agent.select_move(board)
    assert move in list(legal_moves(board))


def test_minimax_prefers_free_capture():
    # White queen on d4 can capture a hanging black queen on d8 for free.
    # A correct minimax at depth ≥ 2 must take it; material eval drives the choice.
    board = board_from_fen("3q3k/8/8/8/3Q4/8/8/4K3 w - - 0 1")
    agent = MinimaxAgent(depth=2)
    move = agent.select_move(board)
    piece = board.piece_at(move.from_sq)
    assert piece is not None and piece.type is PieceType.QUEEN
    from chess_zero.board.types import Square

    assert move.to_sq == Square.from_name("d8")


def test_minimax_finds_mate_in_one():
    # Back-rank mate setup: black king h8 boxed in by own pawns g7/h7,
    # white rook on a1 has an open a-file to deliver Ra8#.
    board = board_from_fen("7k/6pp/8/8/8/8/8/R3K3 w - - 0 1")
    agent = MinimaxAgent(depth=3)
    move = agent.select_move(board)
    board.apply_move(move)
    from chess_zero.board.draws import is_game_over
    from chess_zero.board.legality import is_checkmate

    assert is_game_over(board) and is_checkmate(board)


def test_minimax_handles_no_legal_moves():
    board = board_from_fen("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1")
    agent = MinimaxAgent(depth=2)
    with pytest.raises(ValueError):
        agent.select_move(board)
