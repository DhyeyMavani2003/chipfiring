from __future__ import annotations
from typing import List, Tuple, Dict, Set
from .CFGraph import CFGraph, Vertex


# TODO: Implement 0-divisors and 1-divisors
class CFDivisor:
    """Represents a divisor (chip configuration) on a chip-firing graph."""

    def __init__(self, graph: CFGraph, degrees: List[Tuple[str, int]]):
        """Initialize the divisor with a graph and list of vertex degrees.

        Args:
            graph: A CFGraph object representing the underlying graph
            degrees: List of tuples (vertex_name, degree) where degree is the number
                    of chips at the vertex with the given name

        Raises:
            ValueError: If a vertex name appears multiple times in degrees
            ValueError: If a vertex name is not found in the graph
        """
        self.graph = graph
        # Initialize the degrees dictionary with all vertices having degree 0
        self.degrees: Dict[Vertex, int] = {v: 0 for v in graph.vertices}
        self.total_degree: int = 0

        # Check for duplicate vertex names in degrees
        vertex_names = [name for name, _ in degrees]
        if len(vertex_names) != len(set(vertex_names)):
            raise ValueError("Duplicate vertex names are not allowed in degrees")

        # Update degrees (number of chips) for specified vertices
        for vertex_name, degree in degrees:
            vertex = Vertex(vertex_name)
            if vertex not in graph.graph:
                raise ValueError(f"Vertex {vertex_name} not found in graph")
            self.degrees[vertex] = degree
            self.total_degree += degree

    def is_effective(self) -> bool:
        """Check if the divisor is effective.

        A divisor is effective if all its degrees are non-negative.

        Returns:
            True if the divisor is effective, False otherwise
        """
        for _, degree in self.degrees.items():
            if degree < 0:
                return False
        return True

    def get_degree(self, vertex_name: str) -> int:
        """Get the number of chips at a vertex.

        Args:
            vertex_name: The name of the vertex to get the number of chips for

        Returns:
            The number of chips at the vertex

        Raises:
            ValueError: If the vertex name is not found in the divisor
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.degrees:
            raise ValueError(f"Vertex {vertex_name} not in divisor")
        return self.degrees[vertex]

    def get_total_degree(self) -> int:
        """Get the total number of chips in the divisor.

        Returns:
            The total number of chips in the divisor
        """
        return self.total_degree

    def lending_move(self, vertex_name: str) -> None:
        """Perform a lending move at the specified vertex.

        Decreases the degree of the vertex by its valence and increases the
        degree of each of its neighbors by 1.

        Args:
            vertex_name: The name of the vertex to perform the lending move at.

        Raises:
            ValueError: If the vertex name is not found in the graph.
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")

        neighbors = self.graph.graph[vertex]

        for neighbor in neighbors:
            valence = neighbors[neighbor]
            self.degrees[neighbor] += valence
            self.degrees[vertex] -= valence

        # Total degree remains unchanged: -valence + len(neighbors) = -valence + valence = 0

    firing_move = lending_move

    def borrowing_move(self, vertex_name: str) -> None:
        """Perform a borrowing move at the specified vertex.

        Increases the degree of the vertex by its valence and decreases the
        degree of each of its neighbors by 1.

        Args:
            vertex_name: The name of the vertex to perform the borrowing move at.

        Raises:
            ValueError: If the vertex name is not found in the graph.
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")

        neighbors = self.graph.graph[vertex]

        for neighbor in neighbors:
            valence = neighbors[neighbor]
            self.degrees[neighbor] -= valence
            self.degrees[vertex] += valence

        # Total degree remains unchanged: +valence - len(neighbors) = +valence - valence = 0

    def chip_transfer(
        self, vertex_from_name: str, vertex_to_name: str, amount: int = 1
    ) -> None:
        """Transfer a specified number of chips from one vertex to another.

        Decreases the degree of vertex_from_name by `amount` and increases the
        degree of vertex_to_name by `amount`.

        Args:
            vertex_from_name: The name of the vertex to transfer chips from.
            vertex_to_name: The name of the vertex to transfer chips to.
            amount: The number of chips to transfer (defaults to 1).

        Raises:
            ValueError: If either vertex name is not found in the divisor.
            ValueError: If the amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive for chip transfer")

        vertex_from = Vertex(vertex_from_name)
        vertex_to = Vertex(vertex_to_name)

        if vertex_from not in self.degrees:
            raise ValueError(f"Vertex {vertex_from_name} not in divisor")
        if vertex_to not in self.degrees:
            raise ValueError(f"Vertex {vertex_to_name} not in divisor")

        self.degrees[vertex_from] -= amount
        self.degrees[vertex_to] += amount

        # Total degree remains unchanged: -amount + amount = 0

    def set_fire(self, vertex_names: Set[str]) -> None:
        """Perform a set firing operation.

        For each vertex v in the specified set `vertex_names`, and for each
        neighbor w of v such that w is not in `vertex_names`, transfer chips
        from v to w equal to the number of edges between v and w.

        Args:
            vertex_names: A set of names of vertices in the firing set.

        Raises:
            ValueError: If any vertex name in the set is not found in the graph.
        """
        firing_set_vertices = set()
        # Validate vertex names and convert to Vertex objects
        for name in vertex_names:
            vertex = Vertex(name)
            if vertex not in self.graph.graph:
                raise ValueError(f"Vertex {name} not found in graph")
            firing_set_vertices.add(vertex)

        # Perform the chip transfers
        for vertex in firing_set_vertices:
            neighbors = self.graph.graph[vertex]  # {neighbor_vertex: valence}
            for neighbor_vertex, valence in neighbors.items():
                if neighbor_vertex not in firing_set_vertices:
                    # Transfer 'valence' chips from vertex to neighbor_vertex
                    self.chip_transfer(
                        vertex.name, neighbor_vertex.name, amount=valence
                    )

    def remove_vertex(self, vertex_name: str) -> "CFDivisor":
        """Create a copy of the divisor without the specified vertex.

        Creates a new graph without the specified vertex and returns a new divisor
        with the remaining vertices and their degrees.

        Args:
            vertex_name: The name of the vertex to remove

        Returns:
            A new CFDivisor object without the specified vertex

        Raises:
            ValueError: If the vertex name is not found in the graph
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")

        # Create new graph without the vertex
        new_graph = self.graph.remove_vertex(vertex_name)

        # Create new divisor with remaining vertices and their degrees
        remaining_degrees = [(v.name, self.degrees[v]) for v in new_graph.vertices]

        return CFDivisor(new_graph, remaining_degrees)

    def __eq__(self, other) -> bool:
        """Check if two divisors are equal.

        Two divisors are equal if they have the same underlying graph structure and
        the same distribution of chips across vertices.

        Args:
            other: Another object to compare with

        Returns:
            True if the divisors are equal, False otherwise
        """
        if not isinstance(other, CFDivisor):
            return False

        # Check if the vertex sets are the same
        if set(self.degrees.keys()) != set(other.degrees.keys()):
            return False

        # Check if all vertex degrees match
        for vertex, degree in self.degrees.items():
            if other.degrees[vertex] != degree:
                return False

        # Check if the graph structures are identical (vertices and edges)
        if set(self.graph.vertices) != set(other.graph.vertices):
            return False

        # Compare edges and their weights
        for v in self.graph.vertices:
            if v not in other.graph.graph:
                return False
            if set(self.graph.graph[v].keys()) != set(other.graph.graph[v].keys()):
                return False
            for neighbor, weight in self.graph.graph[v].items():
                if other.graph.graph[v][neighbor] != weight:
                    return False

        return True

    def __add__(self, other: "CFDivisor") -> "CFDivisor":
        """Perform vertex-wise addition of two divisors.

        Both divisors must be defined on graphs with the same set of vertices.
        The resulting divisor will be on the graph of the left operand (self).

        Args:
            other: Another CFDivisor object to add.

        Returns:
            A new CFDivisor representing the sum.

        Raises:
            TypeError: If 'other' is not a CFDivisor.
            ValueError: If the divisors are not on compatible graphs (different vertex sets).
        """
        if self.graph.vertices != other.graph.vertices:
            raise ValueError(
                "Divisors must be on graphs with the same set of vertices for addition."
            )

        new_degrees_list = []
        for v_obj in self.graph.vertices:  # Iterate over vertices of self.graph
            deg1 = self.degrees.get(v_obj, 0)
            deg2 = other.degrees.get(
                v_obj, 0
            )  # other.degrees also uses Vertex objects keyed by name
            new_degrees_list.append((v_obj.name, deg1 + deg2))

        return CFDivisor(self.graph, new_degrees_list)

    def __sub__(self, other: "CFDivisor") -> "CFDivisor":
        """Perform vertex-wise subtraction of two divisors.

        Both divisors must be defined on graphs with the same set of vertices.
        The resulting divisor will be on the graph of the left operand (self).

        Args:
            other: Another CFDivisor object to subtract.

        Returns:
            A new CFDivisor representing the difference.

        Raises:
            TypeError: If 'other' is not a CFDivisor.
            ValueError: If the divisors are not on compatible graphs (different vertex sets).
        """
        if self.graph.vertices != other.graph.vertices:
            raise ValueError(
                "Divisors must be on graphs with the same set of vertices for subtraction."
            )

        new_degrees_list = []
        for v_obj in self.graph.vertices:  # Iterate over vertices of self.graph
            deg1 = self.degrees.get(v_obj, 0)
            deg2 = other.degrees.get(v_obj, 0)
            new_degrees_list.append((v_obj.name, deg1 - deg2))

        return CFDivisor(self.graph, new_degrees_list)
