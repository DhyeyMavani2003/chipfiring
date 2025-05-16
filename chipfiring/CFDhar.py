from __future__ import annotations
from typing import Set, Tuple
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
from .CFOrientation import CFOrientation, OrientationState


class DharAlgorithm:
    """Implements Dhar's algorithm for finding maximal legal firing sets on a graph.

    Dhar's algorithm uses a "burning process" to identify vertices that can be
    legally fired together. It starts a fire at a distinguished vertex and
    determines which vertices burn based on chip configuration.

    Example:
        >>> # Create a simple graph
        >>> vertices = {"A", "B", "C", "D"}
        >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1), ("A", "C", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> # Create a chip configuration
        >>> config = CFDivisor(graph, [("A", 3), ("B", 2), ("C", 1), ("D", 2)])
        >>> # Initialize the algorithm with "A" as the distinguished vertex
        >>> dhar = DharAlgorithm(graph, config, "A")
        >>> # Run the algorithm to find maximal legal firing set
        >>> firing_set, orientation = dhar.run()
        >>> # Check which vertices are in the firing set (excluding A)
        >>> sorted([v.name for v in firing_set])
        ['B', 'C', 'D']
        >>> # Verify orientation is a CFOrientation object
        >>> isinstance(orientation, CFOrientation)
        True
    """

    def __init__(self, graph: CFGraph, configuration: CFDivisor, q_name: str):
        """Initialize Dhar's Algorithm for finding a maximal legal firing set.

        Args:
            graph: A CFGraph object representing the graph
            configuration: A CFDivisor object representing the chip configuration
            q_name: The name of the distinguished vertex (fire source)

        Raises:
            ValueError: If q_name is not found in the graph
            
        Example:
            >>> # Create a simple graph
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create a chip configuration
            >>> config = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
            >>> # Initialize the algorithm with "A" as the distinguished vertex
            >>> dhar = DharAlgorithm(graph, config, "A")
            >>> dhar.q.name
            'A'
            >>> # Unburnt vertices initially (all except q)
            >>> sorted([v.name for v in dhar.unburnt_vertices])
            ['B', 'C', 'D']
            >>> # Invalid distinguished vertex
            >>> try:
            ...     DharAlgorithm(graph, config, "E")
            ... except ValueError as e:
            ...     print(str(e))
            Distinguished vertex E not found in graph
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
        """Calculate the number of edges from a vertex to vertices in set S.

        Args:
            vertex: The vertex to calculate outdegree for
            S: Set of vertices to count edges to

        Returns:
            Sum of edge weights from vertex to vertices in S
            
        Example:
            >>> # Create a simple graph
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), 
            ...          ("D", "A", 1), ("A", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> config = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
            >>> dhar = DharAlgorithm(graph, config, "A")
            >>> # Calculate outdegree to a set of vertices
            >>> S = {Vertex("B"), Vertex("C")}
            >>> dhar.outdegree_S(Vertex("A"), S)  # A has edges to both B and C
            2
            >>> dhar.outdegree_S(Vertex("D"), S)  # D has no edges to B or C
            0
            >>> # With weighted edges
            >>> graph.add_edge("D", "C", 2)  # Add weighted edge from D to C
            >>> dhar.outdegree_S(Vertex("D"), S)  # D now has 2-weighted edge to C
            2
        """
        return sum(
            self.graph.graph[vertex][neighbor]
            for neighbor in self.graph.graph[vertex]
            if neighbor in S
        )

    def send_debt_to_q(self) -> None:
        """Concentrate all debt at the distinguished vertex q, making all non-q vertices out of debt.
        This method modifies self.configuration so all non-q vertices have non-negative values.

        The algorithm works by performing borrowing moves at vertices in debt,
        working in reverse order of distance from q (approximated by BFS).
        
        Example:
            >>> # Create a graph with some debt in the configuration
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> config = CFDivisor(graph, [("A", 2), ("B", -1), ("C", -2), ("D", 1)])
            >>> dhar = DharAlgorithm(graph, config, "A")
            >>> # Check initial configuration
            >>> config.get_degree("B")
            -1
            >>> config.get_degree("C")
            -2
            >>> # Send debt to q (A)
            >>> dhar.send_debt_to_q()
            >>> # Verify all non-q vertices have non-negative values
            >>> dhar.configuration.get_degree("B") >= 0
            True
            >>> dhar.configuration.get_degree("C") >= 0
            True
            >>> dhar.configuration.get_degree("D") >= 0
            True
            >>> # The distinguished vertex q takes on the debt
            >>> dhar.configuration.get_degree("A") <= 2  # Less than or equal to initial value
            True
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

    def run(self) -> Tuple[Set[Vertex], CFOrientation]:
        """Run Dhar's Algorithm to find a maximal legal firing set.

        This implementation uses the "burning process" metaphor:
        1. Start a fire at the distinguished vertex q
        2. A vertex burns if it has fewer chips than edges to burnt vertices
        3. Vertices that never burn form a legal firing set

        Returns:
            A tuple containing:
            - A set of unburnt vertices (excluding q) representing the maximal legal firing set
            - A CFOrientation object tracking the burning directions
            
        Example:
            >>> # Create a simple graph
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create a configuration
            >>> config = CFDivisor(graph, [("A", 3), ("B", 2), ("C", 1), ("D", 2)])
            >>> dhar = DharAlgorithm(graph, config, "A")
            >>> # Run the algorithm
            >>> unburnt_vertices, orientation = dhar.run()
            >>> # All vertices remain unburnt in this example
            >>> sorted([v.name for v in unburnt_vertices])
            ['B', 'C', 'D']
            >>> isinstance(orientation, CFOrientation)
            True
            >>> # Example with debt and burning
            >>> config2 = CFDivisor(graph, [("A", 3), ("B", 0), ("C", 0), ("D", 2)])
            >>> dhar2 = DharAlgorithm(graph, config2, "A")
            >>> unburnt2, orientation2 = dhar2.run()
            >>> # B burns because it has 0 chips but an edge to burnt vertex A
            >>> 'B' not in [v.name for v in unburnt2]
            True
            >>> # Test orientation - B should be oriented from A
            >>> orientation2.get_orientation("A", "B") is not None
            True
        """
        # First, ensure all non-q vertices are out of debt
        self.send_debt_to_q()

        # Initialize burnt set with the distinguished vertex q
        burnt = {self.q}
        unburnt = set(self.graph.vertices) - burnt

        # Initialize a new orientation object
        orientation = CFOrientation(self.graph, [])

        # Continue until no new vertices burn
        changed = True
        while changed:
            changed = False

            # Check each unburnt vertex to see if it should burn;
            # Sort unburnt vertices by name to ensure consistent behavior
            for v in sorted(list(unburnt), key=lambda x: x.name):
                # Count edges from v to burnt vertices
                edges_to_burnt = 0
                burnt_neighbors = []

                for neighbor in self.graph.graph[v]:
                    if neighbor in burnt:
                        edges_to_burnt += self.graph.graph[v][neighbor]
                        burnt_neighbors.append(neighbor)

                # A vertex burns if it has fewer chips than edges to burnt vertices
                if (
                    v in self.configuration.degrees.keys()
                    and self.configuration.get_degree(v.name) < edges_to_burnt
                ):
                    # Record orientations from burnt neighbors to the newly burning vertex
                    for burnt_neighbor in burnt_neighbors:
                        # Add orientation from burnt neighbor (source) to v (sink)
                        current = orientation.get_orientation(
                            burnt_neighbor.name, v.name
                        )
                        if current is None:
                            # Orientation doesn't exist yet, add it
                            orientation.set_orientation(
                                Vertex(burnt_neighbor.name),
                                Vertex(v.name),
                                OrientationState.SOURCE_TO_SINK,
                            )
                        else:
                            # If orientation exists, raise error
                            raise ValueError(
                                f"Conflicting orientation for edge {burnt_neighbor.name}-{v.name}"
                            )

                    burnt.add(v)
                    unburnt.remove(v)
                    changed = True

        # Return unburnt vertices (excluding q) as the maximal firing set, along with the orientation
        return unburnt - {self.q}, orientation

    def legal_set_fire(self, unburnt_vertices: Set[Vertex]):
        """Perform a firing of the legal set of unburnt vertices.
        
        This method updates the divisor by firing all vertices in the unburnt set.
        
        Args:
            unburnt_vertices: A set of vertices to fire
            
        Example:
            >>> # Create a simple graph
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create a configuration
            >>> config = CFDivisor(graph, [("A", 3), ("B", 2), ("C", 1), ("D", 2)])
            >>> dhar = DharAlgorithm(graph, config, "A")
            >>> # Run the algorithm
            >>> unburnt_vertices, _ = dhar.run()
            >>> # Store initial degrees
            >>> initial_b = config.get_degree("B")
            >>> initial_c = config.get_degree("C")
            >>> initial_d = config.get_degree("D")
            >>> # Fire the legal set
            >>> dhar.legal_set_fire(unburnt_vertices)
            >>> # Degrees should change according to firing rules
            >>> config.get_degree("B") != initial_b
            True
            >>> config.get_degree("C") != initial_c
            True
            >>> config.get_degree("D") != initial_d
            True
            >>> # Total degree remains the same
            >>> config.get_total_degree() == 8  # 3 + 2 + 1 + 2 = 8
            True
        """
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
