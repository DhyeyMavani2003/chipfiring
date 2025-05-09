from __future__ import annotations
from typing import Set
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor


class DharAlgorithm:
    def __init__(self, graph: CFGraph, configuration: CFDivisor, q_name: str):
        """
        Initialize Dhar's Algorithm for finding a maximal legal firing set.

        Args:
            graph: A CFGraph object representing the graph
            configuration: A CFDivisor object representing the chip configuration
            q_name: The name of the distinguished vertex (fire source)

        Raises:
            ValueError: If q_name is not found in the graph
        """
        self.graph = graph
        self.q = Vertex(q_name)
        if self.q not in self.graph.vertices:
            raise ValueError(f"Distinguished vertex {q_name} not found in graph")

        self.full_configuration = configuration
        # For convenience, store a separate configuration excluding q
        # NOTE: This creates a new CFGraph object internally in the remove_vertex method, which is wasteful
        self.configuration = configuration

        self.unburnt_vertices = set(self.graph.vertices) - {self.q}

    def outdegree_S(self, vertex: Vertex, S: Set[Vertex]) -> int:
        """
        Calculate the number of edges from a vertex to vertices in set S.

        Args:
            vertex: The vertex to calculate outdegree for
            S: Set of vertices to count edges to

        Returns:
            Sum of edge weights from vertex to vertices in S
        """
        return sum(
            self.graph.graph[vertex][neighbor]
            for neighbor in self.graph.graph[vertex]
            if neighbor in S
        )

    def send_debt_to_q(self) -> None:
        """
        Concentrate all debt at the distinguished vertex q, making all non-q vertices out of debt.
        This method modifies self.configuration so all non-q vertices have non-negative values.

        The algorithm works by performing borrowing moves at vertices in debt,
        working in reverse order of distance from q (approximated by BFS).
        """
        # Sort vertices by distance from q (approximation using BFS)
        queue = [self.q]
        visited = {self.q}
        distance_ordering = [self.q]

        while queue:
            current = queue.pop(0)
            for neighbor in self.graph.graph[current]:
                if neighbor not in visited and neighbor in self.unburnt_vertices:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    distance_ordering.append(neighbor)

        # Process vertices in reverse order of distance (excluding q)
        vertices_to_process = [
            v for v in reversed(distance_ordering) if v in self.unburnt_vertices
        ]

        for v in vertices_to_process:
            # While v is in debt, borrow
            while self.configuration.get_degree(v.name) < 0:
                # Perform a borrowing move at v
                vertex_degree = self.graph.get_valence(v.name)
                self.configuration.degrees[v] += vertex_degree

                # Update neighbors based on edge counts
                for neighbor, edge_count in self.graph.graph[v].items():
                    if neighbor in self.configuration.degrees.keys():
                        self.configuration.degrees[neighbor] -= edge_count

    def run(self) -> Set[Vertex]:
        """
        Run Dhar's Algorithm to find a maximal legal firing set.

        This implementation uses the "burning process" metaphor:
        1. Start a fire at the distinguished vertex q
        2. A vertex burns if it has fewer chips than edges to burnt vertices
        3. Vertices that never burn form a legal firing set

        Returns:
            A set of unburnt vertices (excluding q) representing the maximal legal firing set
        """
        # First, ensure all non-q vertices are out of debt
        self.send_debt_to_q()

        # Initialize burnt set with the distinguished vertex q
        burnt = {self.q}
        unburnt = set(self.graph.vertices) - burnt

        # Continue until no new vertices burn
        changed = True
        while changed:
            changed = False

            # Check each unburnt vertex to see if it should burn
            for v in list(unburnt):
                # Count edges from v to burnt vertices
                edges_to_burnt = sum(
                    self.graph.graph[v][neighbor]
                    for neighbor in self.graph.graph[v]
                    if neighbor in burnt
                )

                # A vertex burns if it has fewer chips than edges to burnt vertices
                if (
                    v in self.configuration.degrees.keys()
                    and self.configuration.get_degree(v.name) < edges_to_burnt
                ):
                    burnt.add(v)
                    unburnt.remove(v)
                    changed = True

        # Return unburnt vertices (excluding q) as the maximal firing set
        return unburnt - {self.q}

    def legal_set_fire(self, unburnt_vertices: Set[Vertex]):
        divisor = self.full_configuration
        for v in self.full_configuration.degrees.keys():
            if v == self.q:
                divisor.degrees[v] = self.full_configuration.get_total_degree() - (
                    self.configuration.get_total_degree()
                    - self.configuration.get_degree(self.q.name)
                )
            else:
                divisor.degrees[v] = self.configuration.get_degree(v.name)

        divisor.set_fire({v.name for v in unburnt_vertices})

        for v in self.configuration.degrees.keys():
            self.configuration.degrees[v] = divisor.get_degree(v.name)
