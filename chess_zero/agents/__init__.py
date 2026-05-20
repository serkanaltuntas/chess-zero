"""Agent protocol + baseline implementations.

`Agent.select_move(board) -> Move` is the single arena contract. Every
agent (random, handcrafted minimax, neural-net-based later) implements
it; the arena never knows which kind it is playing.
"""

from chess_zero.agents.base import Agent
from chess_zero.agents.minimax import MinimaxAgent
from chess_zero.agents.random_agent import RandomAgent

__all__ = ["Agent", "MinimaxAgent", "RandomAgent"]
