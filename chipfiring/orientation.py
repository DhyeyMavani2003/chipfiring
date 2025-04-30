"""
Implementation of graph orientation functionality for the chip-firing game.
"""

from typing import List, Set, Tuple, Optional, Iterable
from .graph import Graph, Vertex, Direction, Edge


class Orientation:
    """
    Class for managing orientations of edges in a graph.
    An orientation specifies which edges should be directed and in what direction.
    """

    def __init__(self, graph: Graph):
        """Initialize with a reference to the graph to be oriented."""
        self.graph = graph

    def orient_edge(self, source: Vertex, target: Vertex) -> None:
        """
        Orient all edges between source and target to go from source to target.
        Raises ValueError if the vertices are not connected.
        """
        if self.graph.get_edge_count(source, target) == 0:
            raise ValueError(f"No edges exist between {source} and {target}")

        # Update orientation in both directions for consistency
        self.graph._orientation[source][target] = Direction.OUTGOING
        self.graph._orientation[target][source] = Direction.INCOMING

    # TODO: Throw error when the user tries to add in (a, b) then (b, a) (causes a loop)
    def orient_edges(self, orientations: List[Tuple[Vertex, Vertex]]) -> None:
        """
        Orient multiple edges at once.
        Each tuple in orientations specifies (source, target) for edge direction.
        """
        for source, target in orientations:
            self.orient_edge(source, target)

    def reset_orientation(self, vertices: Optional[Set[Vertex]] = None) -> None:
        """
        Reset orientation to undirected for all edges involving the specified vertices.
        If vertices is None, resets all orientations in the graph.
        """
        target_vertices: Iterable[Vertex]
        if vertices is None:
            # Get vertices from the graph's adjacency list keys
            target_vertices = self.graph._adjacency.keys()
        else:
            target_vertices = vertices

        for v1 in target_vertices:
            # Ensure we only iterate over actual neighbors present in adjacency
            for v2 in self.graph._adjacency.get(v1, {}).keys():
                self.graph._orientation[v1][v2] = Direction.UNDIRECTED
                self.graph._orientation[v2][v1] = Direction.UNDIRECTED

    def get_oriented_edges(self) -> List[Tuple[Vertex, Vertex]]:
        """
        Return a list of oriented edges as (source, target) tuples.
        Only includes edges that have been explicitly oriented (not undirected ones).
        """
        oriented_edges = []
        seen_edges = set()  # Track edges we've already processed

        # Iterate over vertices present in the graph's adjacency list
        for v1 in self.graph._adjacency.keys():
            for v2 in self.graph._adjacency.get(v1, {}).keys():
                # Create canonical edge representation for tracking
                # Use the Edge class for canonical representation
                canonical_edge = Edge(v1, v2)
                if canonical_edge in seen_edges:
                    continue
                seen_edges.add(canonical_edge)

                direction = self.graph.get_edge_direction(v1, v2)
                if direction == Direction.OUTGOING:
                    oriented_edges.append((v1, v2))
                elif direction == Direction.INCOMING:
                    oriented_edges.append((v2, v1))

        return oriented_edges 