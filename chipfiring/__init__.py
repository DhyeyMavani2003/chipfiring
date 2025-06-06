"""
Chip firing package for simulating graph-based chip firing games.
"""

from .CFGraph import CFGraph, Vertex, Edge
from .CFDivisor import CFDivisor
from .CFConfig import CFConfig
from .CFLaplacian import CFLaplacian
from .CFOrientation import CFOrientation, OrientationState
from .CFiringScript import CFiringScript
from .CFGreedyAlgorithm import GreedyAlgorithm
from .CFDhar import DharAlgorithm
from .algo import EWD, linear_equivalence, is_winnable, q_reduction, is_q_reduced
from .CFRank import rank
from .CFDataProcessor import CFDataProcessor

__all__ = [
    "CFGraph",
    "Vertex",
    "Edge",
    "CFDivisor",
    "CFConfig",
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
    "rank",
    "CFDataProcessor",
    "visualize"
]

__version__ = "0.1.2"
