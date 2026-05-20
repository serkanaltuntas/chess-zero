"""chess-zero command-line interface.

Two subcommands:

- `play`: run a game between two agents (default: both random). Optional
  `--human white|black` puts a human at the keyboard for that color;
  moves are entered as UCI ("e2e4", "e7e8q") or SAN ("e4", "Nf3", "O-O").
- `perft`: run a perft node count from a given position to a given depth.

The CLI is intentionally minimal — it exists so the board engine has a
working entry point for v0.1, not as a full UCI engine. Arena, NN agents,
and self-play orchestration come in later sprints.
"""

from __future__ import annotations

import argparse
import random
import sys
from collections.abc import Sequence

from chess_zero.board.board import Board
from chess_zero.board.draws import game_result, is_game_over
from chess_zero.board.fen import board_from_fen, board_to_fen
from chess_zero.board.legality import legal_moves
from chess_zero.board.move import Move
from chess_zero.board.perft import perft
from chess_zero.board.pgn import move_to_san, san_to_move
from chess_zero.board.types import Color, square


def display_board(board: Board) -> str:
    """ASCII grid view, files a..h across the bottom, ranks 1..8 on the left."""
    lines: list[str] = []
    for r in range(7, -1, -1):
        row = [f"{r + 1} "]
        for f in range(8):
            piece = board.piece_at(square(f, r))
            row.append(f" {piece.symbol() if piece else '.'} ")
        lines.append("".join(row))
    lines.append("   a  b  c  d  e  f  g  h")
    return "\n".join(lines)


def _random_choice(board: Board, rng: random.Random) -> Move | None:
    moves = list(legal_moves(board))
    if not moves:
        return None
    return rng.choice(moves)


def _prompt_human(board: Board, color: Color) -> Move:
    """Read a move from stdin, accepting UCI or SAN. Re-prompts on bad input."""
    while True:
        raw = input(f"{color.name} move> ").strip()
        if not raw:
            continue
        # Try UCI first (4-5 alphanumeric).
        try:
            move = Move.from_uci(raw)
            if any(_moves_equivalent(move, m) for m in legal_moves(board)):
                return next(m for m in legal_moves(board) if _moves_equivalent(move, m))
        except ValueError:
            pass
        # Fall back to SAN.
        try:
            return san_to_move(board, raw)
        except ValueError as exc:
            print(f"  invalid: {exc}", file=sys.stderr)


def _moves_equivalent(a: Move, b: Move) -> bool:
    return (
        a.from_sq == b.from_sq
        and a.to_sq == b.to_sq
        and a.promotion == b.promotion
    )


def cmd_play(args: argparse.Namespace) -> int:
    rng = random.Random(args.seed)
    board = board_from_fen(args.fen) if args.fen else Board()
    human_color: Color | None = None
    if args.human == "white":
        human_color = Color.WHITE
    elif args.human == "black":
        human_color = Color.BLACK

    plies = 0
    san_log: list[str] = []
    while not is_game_over(board) and plies < args.max_plies:
        if human_color is not None and board.side_to_move is human_color:
            print(display_board(board))
            move = _prompt_human(board, board.side_to_move)
        else:
            picked = _random_choice(board, rng)
            if picked is None:
                break
            move = picked

        # Generate SAN before applying so move_to_san sees pre-move state.
        san = move_to_san(board, move)
        board.apply_move(move)
        san_log.append(san)
        plies += 1

        if args.verbose:
            number = (plies + 1) // 2
            prefix = f"{number}." if board.side_to_move is Color.BLACK else f"{number}..."
            print(f"  {prefix} {san}  {board_to_fen(board)}")

    print(f"result: {game_result(board)} after {plies} plies")
    if san_log:
        # Render as "1. e4 e5 2. Nf3 Nc6 ..." pairs.
        pairs: list[str] = []
        for i in range(0, len(san_log), 2):
            number = (i // 2) + 1
            if i + 1 < len(san_log):
                pairs.append(f"{number}. {san_log[i]} {san_log[i + 1]}")
            else:
                pairs.append(f"{number}. {san_log[i]}")
        print("pgn: " + " ".join(pairs) + f" {game_result(board)}")

    return 0


def cmd_perft(args: argparse.Namespace) -> int:
    board = board_from_fen(args.fen) if args.fen else Board()
    n = perft(board, args.depth)
    print(f"perft({args.depth}) = {n}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="chess-zero")
    sub = parser.add_subparsers(dest="cmd", required=True)

    play = sub.add_parser("play", help="play a game (random vs random by default)")
    play.add_argument("--seed", type=int, default=0)
    play.add_argument("--fen", type=str, default=None)
    play.add_argument("--max-plies", type=int, default=1000)
    play.add_argument("--verbose", action="store_true")
    play.add_argument(
        "--human",
        choices=["white", "black"],
        default=None,
        help="play as the given color; opponent uses random moves",
    )
    play.set_defaults(func=cmd_play)

    pf = sub.add_parser("perft", help="count legal-move tree size")
    pf.add_argument("--depth", type=int, required=True)
    pf.add_argument("--fen", type=str, default=None)
    pf.set_defaults(func=cmd_perft)

    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
