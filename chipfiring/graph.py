"""
Implementation of the mathematical graph structure for the chip-firing game.
"""

from typing import Dict, Set, List
from collections import defaultdict
from enum import Enum
import numpy as np


class Direction(Enum):
    """Represents the direction of an edge between two vertices."""
    UNDIRECTED = 0
    OUTGOING = 1  # From key vertex to neighbor
    INCOMING = 2  # From neighbor to key vertex


class Vertex:
    """Represents a vertex in the graph."""

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __lt__(self, other):
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.name < other.name

    def __le__(self, other):
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.name <= other.name

    def __gt__(self, other):
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.name > other.name

    def __ge__(self, other):
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.name >= other.name


class Edge:
    """Represents an edge in the graph."""

    def __init__(self, v1: Vertex, v2: Vertex):
        # Ensure consistent ordering for undirected edges
        if v1.name <= v2.name:
            self.v1, self.v2 = v1, v2
        else:
            self.v1, self.v2 = v2, v1

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return NotImplemented
        return (self.v1 == other.v1 and self.v2 == other.v2) or (
            self.v1 == other.v2 and self.v2 == other.v1
        )

    def __hash__(self):
        return hash((self.v1, self.v2))

    def __str__(self):
        return f"{self.v1}-{self.v2}"

# TODO: Rename everything to CFGraph, CFOrientation, CFDivisor
class Graph:
    """
    Implementation of a finite, connected, undirected multigraph without loop edges.
    This graph is assumed to be connected if not empty.
    Vertices are added implicitly when edges are added.
    The graph can be partially oriented, where some edges are given directions.
    Core graph operations (like Laplacian) ignore orientation.
    """

    def __init__(self):
        self._adjacency: Dict[Vertex, Dict[Vertex, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        # Stores orientation information separately from the core graph structure
        self._orientation: Dict[Vertex, Dict[Vertex, Direction]] = defaultdict(
            lambda: defaultdict(lambda: Direction.UNDIRECTED)
        )


    def add_edge(self, v1: Vertex, v2: Vertex, count: int = 1) -> None:
        """
        Add an edge between v1 and v2 with multiplicity count.
        Raises ValueError if trying to add a loop edge.
        New edges are always undirected. Implicitly adds vertices if not present.
        """
        if v1 == v2:
            raise ValueError("Loop edges are not allowed")

        # edge = Edge(v1, v2) # No longer needed here
        # self.edges[edge] += count # Removed
        self._adjacency[v1][v2] += count
        self._adjacency[v2][v1] += count  # Undirected graph

    def get_edge_count(self, v1: Vertex, v2: Vertex) -> int:
        """Get the number of edges between v1 and v2."""
        # Handle cases where one or both vertices might not (yet) be in _adjacency keys
        return self._adjacency.get(v1, {}).get(v2, 0)

    # TODO: Rename to valence
    def vertex_degree(self, v: Vertex) -> int:
        """Get the degree (valence) of a vertex."""
        # Handle case where vertex might not be in _adjacency (degree 0)
        return sum(self._adjacency.get(v, {}).values())

    # TODO: This is valence; what laplacian
    def get_vertex_degree(self, v: Vertex) -> int:
        """Alias for vertex_degree for compatibility with tests."""
        return self.vertex_degree(v)

    def get_neighbors(self, v: Vertex) -> List[Vertex]:
        """Get all neighbors of a vertex."""
        return [neighbor for neighbor, count in self._adjacency[v].items() if count > 0]

    def get_outgoing_neighbors(self, v: Vertex) -> List[Vertex]:
        """Get neighbors connected by outgoing or undirected edges from v."""
        return [
            neighbor
            for neighbor in self.get_neighbors(v)
            if self._orientation[v][neighbor] in (Direction.OUTGOING, Direction.UNDIRECTED)
        ]

    def get_incoming_neighbors(self, v: Vertex) -> List[Vertex]:
        """Get neighbors connected by incoming or undirected edges to v."""
        return [
            neighbor
            for neighbor in self.get_neighbors(v)
            if self._orientation[v][neighbor] in (Direction.INCOMING, Direction.UNDIRECTED)
        ]

    def get_edge_direction(self, v1: Vertex, v2: Vertex) -> Direction:
        """Get the direction of edges between v1 and v2 from v1's perspective."""
        # Handle cases where vertices might not be in orientation keys yet
        return self._orientation.get(v1, {}).get(v2, Direction.UNDIRECTED)

    # NOTE: This is not currently used because you cannot add vertices to the graph (only edges)
    '''
    def is_connected(self) -> bool:
        """
        Check if the graph is connected. Assumes graph is connected if non-empty.
        Handles the empty graph case.
        """
        if not self._adjacency:
            return True # Empty graph is considered connected

        visited: set[Vertex] = set()
        # Get all vertices from the adjacency list keys
        all_vertices = set(self._adjacency.keys())
        start = next(iter(all_vertices)) # Pick an arbitrary start node

        def dfs(v: Vertex) -> None:
            visited.add(v)
            # Iterate through neighbors from adjacency list
            for neighbor in self._adjacency.get(v, {}):
                if neighbor not in visited:
                    dfs(neighbor)

        dfs(start)
        return len(visited) == len(all_vertices)
    '''

    def __str__(self) -> str:
        """String representation of the graph."""
        if not self._adjacency:
            return "Graph with 0 vertices and 0 edges"

        vertices_list = sorted(self._adjacency.keys())
        edges_str = []
        seen_edges: Set[Edge] = set() # Track canonical edges

        for v1 in vertices_list:
            for v2, count in self._adjacency.get(v1, {}).items():
                if v1 < v2: # Process each edge only once (using canonical order)
                    edge = Edge(v1, v2) # Create canonical edge for representation
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        direction = self.get_edge_direction(v1, v2) # Use safe getter
                        
                        # Determine string based on orientation from v1's perspective
                        if direction == Direction.UNDIRECTED:
                            edge_str_base = str(edge) # Uses Edge.__str__ (v1-v2)
                        elif direction == Direction.OUTGOING: # v1 -> v2
                            edge_str_base = f"{v1}->{v2}"
                        else: # INCOMING (v2 -> v1)
                            edge_str_base = f"{v2}->{v1}"

                        if count > 1:
                            edges_str.append(f"{edge_str_base} (x{count})")
                        else:
                            edges_str.append(edge_str_base)
        
        # Sort edges for consistent output
        edges_str.sort() 
        vertices_names = [str(v) for v in vertices_list]
        return f"Graph with vertices {vertices_names} and edges {edges_str}"
