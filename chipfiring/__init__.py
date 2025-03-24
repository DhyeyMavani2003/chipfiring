"""
Chip firing package for simulating graph-based chip firing games.
"""

from .graph import Graph, Vertex, Edge
from .divisor import Divisor
from .dollar_game import DollarGame
from .dhar import (
    find_legal_firing_set,
    is_q_reduced,
    q_reduce,
    is_winnable_dhar,
    get_winning_strategy_dhar,
)
from .visualization import draw_graph, draw_game_state

__all__ = [
    "Graph",
    "Vertex",
    "Edge",
    "Divisor",
    "DollarGame",
    "find_legal_firing_set",
    "is_q_reduced",
    "q_reduce",
    "is_winnable_dhar",
    "get_winning_strategy_dhar",
    "draw_graph",
    "draw_game_state",
]
__version__ = "0.0.1"
