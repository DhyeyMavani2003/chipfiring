"""
Implementation of the mathematical graph structure for the chip-firing game.
"""

from typing import Dict, Set, List
from collections import defaultdict
import numpy as np


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


class Graph:
    """
    Implementation of a finite, connected, undirected multigraph without loop edges.
    This matches the mathematical definition from the LaTeX writeup.
    """

    def __init__(self):
        self.vertices: Set[Vertex] = set()
        self.edges: Dict[Edge, int] = defaultdict(int)  # Multiset of edges
        self._adjacency: Dict[Vertex, Dict[Vertex, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def add_vertex(self, vertex: Vertex) -> None:
        """Add a vertex to the graph."""
        self.vertices.add(vertex)

    def add_edge(self, v1: Vertex, v2: Vertex, count: int = 1) -> None:
        """
        Add an edge between v1 and v2 with multiplicity count.
        Raises ValueError if trying to add a loop edge.
        """
        if v1 == v2:
            raise ValueError("Loop edges are not allowed")

        edge = Edge(v1, v2)
        self.edges[edge] += count
        self._adjacency[v1][v2] += count
        self._adjacency[v2][v1] += count  # Undirected graph

    def get_edge_count(self, v1: Vertex, v2: Vertex) -> int:
        """Get the number of edges between v1 and v2."""
        return self._adjacency[v1][v2]

    def vertex_degree(self, v: Vertex) -> int:
        """Get the degree (valence) of a vertex."""
        return sum(self._adjacency[v].values())

    def get_vertex_degree(self, v: Vertex) -> int:
        """Alias for vertex_degree for compatibility with tests."""
        return self.vertex_degree(v)

    def get_neighbors(self, v: Vertex) -> List[Vertex]:
        """Get all neighbors of a vertex."""
        return [neighbor for neighbor, count in self._adjacency[v].items() if count > 0]

    def is_connected(self) -> bool:
        """Check if the graph is connected."""
        if not self.vertices:
            return True

        visited: set[Vertex] = set()
        start = next(iter(self.vertices))

        def dfs(v: Vertex) -> None:
            visited.add(v)
            for neighbor in self._adjacency[v]:
                if neighbor not in visited:
                    dfs(neighbor)

        dfs(start)
        return len(visited) == len(self.vertices)

    def get_laplacian_matrix(self) -> np.ndarray:
        """
        Get the Laplacian matrix L where:
        L[i,j] = degree(v_i) if i=j
        L[i,j] = -(# of edges between v_i and v_j) if i≠j
        """
        vertices_list = sorted(self.vertices)
        n = len(vertices_list)
        L = np.zeros((n, n), dtype=int)

        for i, v1 in enumerate(vertices_list):
            for j, v2 in enumerate(vertices_list):
                if i == j:
                    L[i, j] = self.vertex_degree(v1)
                else:
                    L[i, j] = -self.get_edge_count(v1, v2)

        return L

    def get_reduced_laplacian(self, q: Vertex) -> np.ndarray:
        """
        Get the reduced Laplacian matrix by removing the row and column
        corresponding to the distinguished vertex q.
        """
        vertices_list = sorted(v for v in self.vertices if v != q)
        n = len(vertices_list)
        L = np.zeros((n, n), dtype=int)

        for i, v1 in enumerate(vertices_list):
            for j, v2 in enumerate(vertices_list):
                if i == j:
                    L[i, j] = self.vertex_degree(v1)
                else:
                    L[i, j] = -self.get_edge_count(v1, v2)

        return L

    def __str__(self) -> str:
        """String representation of the graph."""
        edges_str = []
        for edge, count in self.edges.items():
            if count > 1:
                edges_str.append(f"{edge} (x{count})")
            else:
                edges_str.append(str(edge))
        return f"Graph with vertices {list(self.vertices)} and edges {edges_str}"
