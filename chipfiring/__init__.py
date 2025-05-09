"""
Chip firing package for simulating graph-based chip firing games.
"""

from .CFGraph import CFGraph, Vertex, Edge
from .CFDivisor import CFDivisor
from .CFLaplacian import CFLaplacian
from .CFOrientation import CFOrientation, OrientationState
from .CFiringScript import CFiringScript
from .CFGreedyAlgorithm import GreedyAlgorithm
from .CFDhar import DharAlgorithm
from .algo import EWD, linear_equivalence, is_winnable, q_reduction, is_q_reduced

__all__ = [
    "CFGraph",
    "Vertex",
    "Edge",
    "CFDivisor",
    "CFLaplacian",
    "CFOrientation",
    "OrientationState",
    "CFiringScript",
    "DharAlgorithm",
    "GreedyAlgorithm",
    "EWD",
    "linear_equivalence",
    "is_winnable",
    "q_reduction",
    "is_q_reduced",
]

__version__ = "0.1.1"
