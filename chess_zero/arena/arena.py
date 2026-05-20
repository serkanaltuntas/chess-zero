"""Arena: play one game between two agents; record + replay support.

The arena is the only thing that knows whose turn it is. Agents are
interchangeable — random, minimax, NN-backed later — because they share
the `Agent.select_move(board) -> Move` contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from chess_zero.agents.base import Agent
from chess_zero.board.board import Board
from chess_zero.board.draws import (
    game_result,
    is_fifty_move_draw,
    is_game_over,
    is_insufficient_material,
    is_threefold_repetition,
)
from chess_zero.board.fen import board_from_fen, board_to_fen
from chess_zero.board.legality import is_checkmate, is_stalemate
from chess_zero.board.move import Move
from chess_zero.board.pgn import move_to_san
from chess_zero.board.types import Color


@dataclass(frozen=True)
class GameRecord:
    white_name: str
    black_name: str
    initial_fen: str
    moves: list[Move] = field(default_factory=list)
    sans: list[str] = field(default_factory=list)
    result: str = "*"
    termination: str = "unknown"


def _termination_reason(board: Board, hit_max_plies: bool, no_legal: bool) -> str:
    if no_legal:
        # Agent raised ValueError on select_move — treat as game over due to
        # whichever terminal condition is now true.
        if is_checkmate(board):
            return "checkmate"
        if is_stalemate(board):
            return "stalemate"
        return "no_legal_moves"
    if is_checkmate(board):
        return "checkmate"
    if is_stalemate(board):
        return "stalemate"
    if is_fifty_move_draw(board):
        return "fifty_move"
    if is_threefold_repetition(board):
        return "threefold"
    if is_insufficient_material(board):
        return "insufficient_material"
    if hit_max_plies:
        return "max_plies"
    return "unknown"


def play_game(
    white: Agent,
    black: Agent,
    board: Board | None = None,
    max_plies: int = 1000,
) -> GameRecord:
    """Play a single game; return the move log, SAN log, result, termination."""
    play_board = board if board is not None else Board()
    initial_fen = board_to_fen(play_board)
    moves: list[Move] = []
    sans: list[str] = []
    no_legal = False

    while not is_game_over(play_board) and len(moves) < max_plies:
        agent = white if play_board.side_to_move is Color.WHITE else black
        try:
            move = agent.select_move(play_board)
        except ValueError:
            no_legal = True
            break
        sans.append(move_to_san(play_board, move))
        play_board.apply_move(move)
        moves.append(move)

    return GameRecord(
        white_name=type(white).__name__,
        black_name=type(black).__name__,
        initial_fen=initial_fen,
        moves=moves,
        sans=sans,
        result=game_result(play_board),
        termination=_termination_reason(
            play_board,
            hit_max_plies=len(moves) >= max_plies and not is_game_over(play_board),
            no_legal=no_legal,
        ),
    )


def replay(record: GameRecord) -> Board:
    """Replay `record.moves` from the initial FEN; return the final board."""
    board = board_from_fen(record.initial_fen)
    for move in record.moves:
        board.apply_move(move)
    return board
