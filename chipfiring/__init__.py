"""
Chip firing package for simulating graph-based chip firing games.
"""
from __future__ import annotations
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
from .CFEWDVisualizer import EWDVisualizer
from .CFVisualizer import visualize
from .CFGonality import gonality, play_gonality_game, CFGonality, GonalityGameResult, GonalityResult
from .CFPlatonicSolids import (
    tetrahedron, cube, octahedron, dodecahedron, icosahedron,
    complete_graph, platonic_solid_gonality_bounds, complete_graph_gonality
)
from .CFGonalityDhar import GonalityDharAlgorithm, enhanced_dhar_gonality_test, batch_gonality_analysis

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
    "EWDVisualizer",
    "visualize",
    "gonality",
    "play_gonality_game",
    "CFGonality",
    "GonalityGameResult",
    "GonalityResult",
    "tetrahedron",
    "cube",
    "octahedron",
    "dodecahedron",
    "icosahedron",
    "complete_graph",
    "platonic_solid_gonality_bounds",
    "complete_graph_gonality",
    "GonalityDharAlgorithm",
    "enhanced_dhar_gonality_test",
    "batch_gonality_analysis",
]

__version__ = "1.0.0"
