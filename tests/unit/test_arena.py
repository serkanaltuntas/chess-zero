from chess_zero.agents import MinimaxAgent, RandomAgent
from chess_zero.arena import GameRecord, play_game, replay
from chess_zero.board.board import Board
from chess_zero.board.fen import board_from_fen, board_to_fen

# ---------- GameRecord shape ----------


def test_play_game_returns_game_record():
    record = play_game(
        RandomAgent(seed=0),
        RandomAgent(seed=1),
        max_plies=20,
    )
    assert isinstance(record, GameRecord)
    assert record.white_name == "RandomAgent"
    assert record.black_name == "RandomAgent"
    assert len(record.moves) == len(record.sans)
    assert record.result in {"1-0", "0-1", "1/2-1/2", "*"}


def test_play_game_terminates_on_game_over():
    # Stalemate position: black to move with no legal moves and not in check.
    board = board_from_fen("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1")
    record = play_game(
        RandomAgent(seed=0),
        RandomAgent(seed=1),
        board=board,
        max_plies=10,
    )
    assert len(record.moves) == 0
    assert record.result == "1/2-1/2"
    assert record.termination == "stalemate"


def test_play_game_respects_max_plies():
    record = play_game(
        RandomAgent(seed=0),
        RandomAgent(seed=1),
        max_plies=4,
    )
    assert len(record.moves) <= 4


def test_play_game_initial_fen_recorded():
    board = Board()
    fen = board_to_fen(board)
    record = play_game(RandomAgent(seed=0), RandomAgent(seed=1), max_plies=5)
    assert record.initial_fen == fen


# ---------- replay ----------


def test_replay_reproduces_final_state():
    record = play_game(
        RandomAgent(seed=7),
        RandomAgent(seed=11),
        max_plies=40,
    )
    replayed = replay(record)
    # Re-play from initial_fen + record.moves should land at the same FEN
    # the live game ended at. We reconstruct the original final FEN by
    # re-running play and capturing the post-loop board.
    live_board = board_from_fen(record.initial_fen)
    for move in record.moves:
        live_board.apply_move(move)
    assert board_to_fen(replayed) == board_to_fen(live_board)


# ---------- minimax vs random gauntlet sanity ----------


def test_minimax_outperforms_random_in_short_gauntlet():
    """Minimax should win more often than random over a small gauntlet.

    Single-game variance is high, so this asserts an aggregate signal over
    a few games: minimax must score strictly above 1.0 (out of 4 games).
    """
    minimax = MinimaxAgent(depth=2)
    random_agent = RandomAgent(seed=0)
    minimax_score = 0.0
    for _ in range(4):
        record = play_game(minimax, random_agent, max_plies=80)
        if record.result == "1-0":
            minimax_score += 1.0
        elif record.result == "1/2-1/2":
            minimax_score += 0.5
    assert minimax_score > 1.0
