"""
Platonic solids graph generators for chip firing and gonality studies.

This module provides functions to generate graphs corresponding to the five Platonic solids
as described in "Chip-firing on the Platonic solids" by Beougher et al.
"""
from __future__ import annotations
from typing import Dict
import networkx as nx
from .CFGraph import CFGraph


def tetrahedron() -> CFGraph:
    """
    Generate the complete graph K4 representing a tetrahedron.
    
    The tetrahedron has 4 vertices and 6 edges, with each vertex connected to every other.
    This is the complete graph K4.
    
    Returns:
        CFGraph: A CFGraph representing the tetrahedron (K4)
        
    Examples:
        >>> G = tetrahedron()
        >>> len(G.vertices)
        4
        >>> len(G.edges)
        6
    """
    # Create vertices - CFGraph expects vertex names as strings
    vertex_names = [str(i) for i in range(4)]
    
    # Create all edges for complete graph K4 - CFGraph expects tuples (v1_name, v2_name, valence)
    edges = []
    for i in range(4):
        for j in range(i + 1, 4):
            edges.append((str(i), str(j), 1))  # valence = 1 for single edge
    
    return CFGraph(vertex_names, edges)


def cube() -> CFGraph:
    """
    Generate the cube graph (octahedral graph).
    
    The cube has 8 vertices and 12 edges. Each vertex has degree 3.
    Vertices can be labeled by binary coordinates (x,y,z) where x,y,z ∈ {0,1}.
    Two vertices are adjacent if their coordinates differ in exactly one position.
    
    Returns:
        CFGraph: A CFGraph representing the cube
        
    Examples:
        >>> G = cube()
        >>> len(G.vertices)
        8
        >>> len(G.edges)
        12
    """
    # Create vertices with binary coordinates as labels
    vertex_names = []
    vertex_map = {}
    
    for x in [0, 1]:
        for y in [0, 1]:
            for z in [0, 1]:
                coord = (x, y, z)
                vertex_name = f"({x},{y},{z})"
                vertex_names.append(vertex_name)
                vertex_map[coord] = vertex_name
    
    edges = []
    
    # Connect vertices that differ in exactly one coordinate
    for x in [0, 1]:
        for y in [0, 1]:
            for z in [0, 1]:
                current = (x, y, z)
                
                # Check all three possible single-bit flips
                neighbors = [
                    (1-x, y, z),    # flip x
                    (x, 1-y, z),    # flip y
                    (x, y, 1-z)     # flip z
                ]
                
                for neighbor in neighbors:
                    if current < neighbor:  # Avoid duplicate edges
                        edges.append((vertex_map[current], vertex_map[neighbor], 1))
    
    return CFGraph(vertex_names, edges)


def octahedron() -> CFGraph:
    """
    Generate the octahedron graph (K_{2,2,2}).
    
    The octahedron has 6 vertices and 12 edges. It can be constructed as the complete
    tripartite graph K_{2,2,2}, or as the complement of 3K2 (three disjoint edges).
    
    Returns:
        CFGraph: A CFGraph representing the octahedron
        
    Examples:
        >>> G = octahedron()
        >>> len(G.vertices)
        6
        >>> len(G.edges)
        12
    """
    vertex_names = [f"v{i}" for i in range(6)]
    edges = []
    
    # The octahedron can be constructed as K_{2,2,2}
    # Partition vertices into three groups of 2
    groups = [
        [vertex_names[0], vertex_names[1]],  # Group 1
        [vertex_names[2], vertex_names[3]],  # Group 2
        [vertex_names[4], vertex_names[5]]   # Group 3
    ]
    
    # Connect every vertex in one group to every vertex in the other groups
    for i in range(3):
        for j in range(i + 1, 3):
            for v1 in groups[i]:
                for v2 in groups[j]:
                    edges.append((v1, v2, 1))
    
    return CFGraph(vertex_names, edges)


def dodecahedron() -> CFGraph:
    """
    Generate the dodecahedron graph.
    
    The dodecahedron has 20 vertices and 30 edges. Each vertex has degree 3.
    This implementation creates the standard dodecahedral graph structure.
    
    Returns:
        CFGraph: A CFGraph representing the dodecahedron
        
    Examples:
        >>> G = dodecahedron()
        >>> len(G.vertices)
        20
        >>> len(G.edges)
        30
    """
    # Use NetworkX to generate the dodecahedral graph, then convert to CFGraph
    nx_graph = nx.dodecahedral_graph()
    
    # Create vertices
    vertex_names = [f"v{i}" for i in range(20)]
    
    # Create edges based on NetworkX graph
    edges = []
    for u, v in nx_graph.edges():
        edges.append((f"v{u}", f"v{v}", 1))
    
    return CFGraph(vertex_names, edges)


def icosahedron() -> CFGraph:
    """
    Generate the icosahedron graph.
    
    The icosahedron has 12 vertices and 30 edges. Each vertex has degree 5.
    This implementation creates the standard icosahedral graph structure.
    
    Returns:
        CFGraph: A CFGraph representing the icosahedron
        
    Examples:
        >>> G = icosahedron()
        >>> len(G.vertices)
        12
        >>> len(G.edges)
        30
    """
    # Use NetworkX to generate the icosahedral graph, then convert to CFGraph
    nx_graph = nx.icosahedral_graph()
    
    # Create vertices
    vertex_names = [f"v{i}" for i in range(12)]
    
    # Create edges based on NetworkX graph
    edges = []
    for u, v in nx_graph.edges():
        edges.append((f"v{u}", f"v{v}", 1))
    
    return CFGraph(vertex_names, edges)


def complete_graph(n: int) -> CFGraph:
    """
    Generate the complete graph Kn.
    
    The complete graph Kn has n vertices and n(n-1)/2 edges.
    Every vertex is connected to every other vertex.
    
    Args:
        n: Number of vertices
        
    Returns:
        CFGraph: A CFGraph representing Kn
        
    Examples:
        >>> G = complete_graph(5)
        >>> len(G.vertices)
        5
        >>> len(G.edges)
        10
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    
    vertex_names = [f"v{i}" for i in range(n)]
    edges = []
    
    # Connect every pair of vertices
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((f"v{i}", f"v{j}", 1))
    
    return CFGraph(vertex_names, edges)


def platonic_solid_gonality_bounds() -> Dict[str, Dict[str, int]]:
    """
    Return known gonality bounds for Platonic solids.
    
    Based on the paper "Chip-firing on the Platonic solids" by Beougher et al.,
    this function returns theoretical bounds and exact values where known.
    The gonality of K_n is n-1. Tetrahedron is K4, so its gonality is 3.
    
    Returns:
        Dict[str, Dict[str, int]]: Dictionary mapping solid names to their gonality bounds
        
    Examples:
        >>> bounds = platonic_solid_gonality_bounds()
        >>> bounds['tetrahedron']['exact']
        3
    """
    return {
        'tetrahedron': {
            'exact': 3,  # K4 has gonality 3 (n-1 for K_n)
            'lower_bound': 3,
            'upper_bound': 3,
            'vertices': 4,
            'edges': 6
        },
        'cube': {
            'exact': 4,  # Computed result for cube graph
            'lower_bound': 4,
            'upper_bound': 4,
            'vertices': 8,
            'edges': 12
        },
        'octahedron': {
            'exact': 3,  # K_{2,2,2} has gonality 3
            'lower_bound': 3,
            'upper_bound': 3,
            'vertices': 6,
            'edges': 12
        },
        'dodecahedron': {
            'lower_bound': 4,  # Theoretical lower bound
            'upper_bound': 6,  # Theoretical upper bound
            'vertices': 20,
            'edges': 30
        },
        'icosahedron': {
            'lower_bound': 3,  # Theoretical lower bound
            'upper_bound': 5,  # Theoretical upper bound
            'vertices': 12,
            'edges': 30
        }
    }


def complete_graph_gonality(n: int) -> int:
    """
    Return the exact gonality of the complete graph Kn.
    
    For complete graphs, the gonality is known to be n-1.
    
    Args:
        n: Number of vertices in Kn
        
    Returns:
        int: The gonality of Kn
        
    Examples:
        >>> complete_graph_gonality(4)
        3
        >>> complete_graph_gonality(5)
        4
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    return n - 1
