from __future__ import annotations
from typing import List, Tuple, Dict, Set
from .CFGraph import CFGraph, Vertex

# TODO: Implement 0-divisors and 1-divisors
class CFDivisor:
    """Represents a divisor (chip configuration) on a chip-firing graph.

    Example:
        >>> vertices = {"A", "B", "C"}
        >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> degrees = [("A", 2), ("B", -1), ("C", 0)]
        >>> divisor = CFDivisor(graph, degrees)
        >>> divisor.get_degree("A")
        2
        >>> divisor.get_degree("B")
        -1
        >>> divisor.get_total_degree()  # 2 + (-1) + 0 = 1
        1
    """

    def __init__(self, graph: CFGraph, degrees: List[Tuple[str, int]]):
        """Initialize the divisor with a graph and list of vertex degrees.

        Args:
            graph: A CFGraph object representing the underlying graph
            degrees: List of tuples (vertex_name, degree) where degree is the number
                    of chips at the vertex with the given name

        Raises:
            ValueError: If a vertex name appears multiple times in degrees
            ValueError: If a vertex name is not found in the graph

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create a divisor with specified degrees
            >>> degrees = [("v1", 10), ("v2", -5)]  # v3 defaults to 0
            >>> divisor = CFDivisor(graph, degrees)
            >>> divisor.get_degree("v1")
            10
            >>> divisor.get_degree("v2")
            -5
            >>> divisor.get_degree("v3")  # Default degree
            0
            >>> # Empty degrees list makes all vertices have 0 chips
            >>> zero_divisor = CFDivisor(graph, [])
            >>> zero_divisor.get_degree("v1")
            0
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

    def to_dict(self) -> Dict[str, any]:
        """Converts the CFDivisor instance to a dictionary representation.

        Returns:
            A dictionary with 'graph' and 'degrees'.
        """
        graph_dict = self.graph.to_dict()
        degrees_dict = {v.name: deg for v, deg in self.degrees.items()}
        return {
            "graph": graph_dict,
            "degrees": degrees_dict
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "CFDivisor":
        """Creates a CFDivisor instance from a dictionary representation.

        Args:
            data: A dictionary with 'graph' (CFGraph representation) 
                  and 'degrees' (dictionary mapping vertex names to degrees).

        Returns:
            A CFDivisor instance.
        """
        graph_data = data.get("graph")
        if not graph_data:
            raise ValueError("Graph data is missing in CFDivisor representation")
        
        graph = CFGraph.from_dict(graph_data)
        
        degrees_dict = data.get("degrees", {})
        degrees_list = list(degrees_dict.items()) # Convert dict to list of tuples for constructor
        
        return cls(graph, degrees_list)

    def is_effective(self) -> bool:
        """Check if the divisor is effective.

        A divisor is effective if all its degrees are non-negative.

        Returns:
            True if the divisor is effective, False otherwise

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Effective divisor (all non-negative)
            >>> effective = CFDivisor(graph, [("v1", 1), ("v2", 0), ("v3", 3)])
            >>> effective.is_effective()
            True
            >>> # Not effective (has negative degree)
            >>> not_effective = CFDivisor(graph, [("v1", 1), ("v2", 2), ("v3", -3)])
            >>> not_effective.is_effective()
            False
            >>> # Zero degrees are considered effective
            >>> zero = CFDivisor(graph, [("v1", 0), ("v2", 0), ("v3", 0)])
            >>> zero.is_effective()
            True
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> degrees = [("v1", 5), ("v2", 0), ("v3", -2)]
            >>> divisor = CFDivisor(graph, degrees)
            >>> divisor.get_degree("v1")
            5
            >>> divisor.get_degree("v2")
            0
            >>> divisor.get_degree("v3")
            -2
            >>> try:
            ...     divisor.get_degree("v4")  # Non-existent vertex
            ... except ValueError as e:
            ...     print(str(e))
            Vertex v4 not in divisor
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.degrees:
            raise ValueError(f"Vertex {vertex_name} not in divisor")
        return self.degrees[vertex]

    def get_total_degree(self) -> int:
        """Get the total number of chips in the divisor.

        Returns:
            The total number of chips in the divisor

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Test positive total
            >>> divisor1 = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> divisor1.get_total_degree()  # 2 + 1 + 0 = 3
            3
            >>> # Test negative total
            >>> divisor2 = CFDivisor(graph, [("A", -2), ("B", -1), ("C", 0)])
            >>> divisor2.get_total_degree()  # -2 + (-1) + 0 = -3
            -3
            >>> # Test zero total
            >>> divisor3 = CFDivisor(graph, [("A", 1), ("B", -1), ("C", 0)])
            >>> divisor3.get_total_degree()  # 1 + (-1) + 0 = 0
            0
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create a divisor
            >>> divisor = CFDivisor(graph, [("v1", 3), ("v2", 1), ("v3", 0)])
            >>> # K3 graph: each vertex has valence 2
            >>> initial_total = divisor.get_total_degree()  # 4
            >>> # Lend from v1 (valence 2)
            >>> divisor.lending_move("v1")
            >>> divisor.get_degree("v1")  # 3 - 2 = 1
            1
            >>> divisor.get_degree("v2")  # 1 + 1 = 2
            2
            >>> divisor.get_degree("v3")  # 0 + 1 = 1
            1
            >>> divisor.get_total_degree() == initial_total  # Total preserved
            True
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create a divisor
            >>> divisor = CFDivisor(graph, [("v1", 3), ("v2", 1), ("v3", 0)])
            >>> initial_total = divisor.get_total_degree()  # 4
            >>> # Borrow at v2 (valence 2)
            >>> divisor.borrowing_move("v2")
            >>> divisor.get_degree("v2")  # 1 + 2 = 3
            3
            >>> divisor.get_degree("v1")  # 3 - 1 = 2
            2
            >>> divisor.get_degree("v3")  # 0 - 1 = -1
            -1
            >>> divisor.get_total_degree() == initial_total  # Total preserved
            True
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("v1", 5), ("v2", 0), ("v3", -2)])
            >>> initial_total = divisor.get_total_degree()  # 3
            >>> # Transfer 1 chip v1 -> v2
            >>> divisor.chip_transfer("v1", "v2")
            >>> divisor.get_degree("v1")  # 5 - 1 = 4
            4
            >>> divisor.get_degree("v2")  # 0 + 1 = 1
            1
            >>> # Transfer multiple chips
            >>> divisor.chip_transfer("v2", "v3", amount=3)
            >>> divisor.get_degree("v2")  # 1 - 3 = -2
            -2
            >>> divisor.get_degree("v3")  # -2 + 3 = 1
            1
            >>> divisor.get_total_degree() == initial_total  # Total preserved
            True
            >>> # Invalid operations
            >>> try:
            ...     divisor.chip_transfer("v1", "v2", amount=0)  # Zero amount
            ... except ValueError as e:
            ...     print(str(e))
            Amount must be positive for chip transfer
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

        Example:
            >>> vertices = {"a", "b", "c"}
            >>> edges = [("a", "b", 2), ("b", "c", 3)]  # Multi-graph
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("a", 10), ("b", 5), ("c", 0)])
            >>> initial_total = divisor.get_total_degree()  # 15
            >>> # Fire single vertex
            >>> divisor.set_fire({"a"})  # Transfers 2 chips from a to b
            >>> divisor.get_degree("a")  # 10 - 2 = 8
            8
            >>> divisor.get_degree("b")  # 5 + 2 = 7
            7
            >>> divisor.get_degree("c")  # Unchanged
            0
            >>> # Fire multiple vertices
            >>> divisor.set_fire({"a", "b"})  # a->b (in set, no transfer), b->c (3 chips)
            >>> divisor.get_degree("a")  # 8 (unchanged)
            8
            >>> divisor.get_degree("b")  # 7 - 3 = 4
            4
            >>> divisor.get_degree("c")  # 0 + 3 = 3
            3
            >>> divisor.get_total_degree() == initial_total  # Total preserved
            True
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

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 3), ("B", -1), ("C", 2)])
            >>> # Remove vertex B
            >>> new_divisor = divisor.remove_vertex("B")
            >>> # Check the new divisor has one fewer vertex
            >>> "B" in [v.name for v in new_divisor.graph.vertices]
            False
            >>> len(new_divisor.graph.vertices)
            2
            >>> # Check degrees are preserved for remaining vertices
            >>> new_divisor.get_degree("A")
            3
            >>> new_divisor.get_degree("C")
            2
            >>> new_divisor.get_total_degree()  # 3 + 2 = 5
            5
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")

        # Create new graph without the vertex
        new_graph = self.graph.remove_vertex(vertex_name)

        # Create new divisor with remaining vertices and their degrees
        remaining_degrees = [(v.name, self.degrees[v]) for v in new_graph.vertices]

        return CFDivisor(new_graph, remaining_degrees)

    def degrees_to_str(self) -> str:
        """Return a string representation of the degrees.
        
        Returns:
            A string showing vertex names and their degrees in alphabetical order.
            
        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", -1), ("C", 0)])
            >>> divisor.degrees_to_str()
            'A:2, B:-1, C:0'
        """
        degrees_str = ", ".join(
            f"{v.name}:{self.degrees[v]}" 
            for v in sorted(self.graph.vertices, key=lambda v: v.name)
        )
        return degrees_str

    def __eq__(self, other) -> bool:
        """Check if two divisors are equal.

        Two divisors are equal if they have the same underlying graph structure and
        the same distribution of chips across vertices.

        Args:
            other: Another object to compare with

        Returns:
            True if the divisors are equal, False otherwise

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Two identical divisors
            >>> div1 = CFDivisor(graph, [("v1", 1), ("v2", 2), ("v3", 3)])
            >>> div2 = CFDivisor(graph, [("v1", 1), ("v2", 2), ("v3", 3)])
            >>> div1 == div2
            True
            >>> # Different degree at one vertex
            >>> div3 = CFDivisor(graph, [("v1", 5), ("v2", 2), ("v3", 3)])
            >>> div1 == div3
            False
            >>> # Different underlying graph
            >>> different_graph = CFGraph({"v1", "v2", "v3"}, [("v1", "v2", 2)])
            >>> div4 = CFDivisor(different_graph, [("v1", 1), ("v2", 2), ("v3", 3)])
            >>> div1 == div4
            False
            >>> # Comparison with non-CFDivisor object
            >>> div1 == "not a divisor"
            False
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create two divisors
            >>> degrees1 = [("v1", 1), ("v2", 2), ("v3", 3)]
            >>> divisor1 = CFDivisor(graph, degrees1)
            >>> degrees2 = [("v1", 4), ("v2", 5), ("v3", 0)]
            >>> divisor2 = CFDivisor(graph, degrees2)
            >>> # Add them
            >>> sum_divisor = divisor1 + divisor2
            >>> sum_divisor.get_degree("v1")  # 1 + 4 = 5
            5
            >>> sum_divisor.get_degree("v2")  # 2 + 5 = 7
            7
            >>> sum_divisor.get_degree("v3")  # 3 + 0 = 3
            3
            >>> sum_divisor.get_total_degree()  # (1+2+3) + (4+5+0) = 15
            15
            >>> # With unspecified degrees (defaulting to 0)
            >>> div_a = CFDivisor(graph, [("v1", 10)])  # v2, v3 are 0
            >>> div_b = CFDivisor(graph, [("v2", 5)])   # v1, v3 are 0
            >>> sum_div = div_a + div_b
            >>> sum_div.get_degree("v1")  # 10 + 0 = 10
            10
            >>> sum_div.get_degree("v2")  # 0 + 5 = 5
            5
            >>> sum_div.get_degree("v3")  # 0 + 0 = 0
            0
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create two divisors
            >>> divisor1 = CFDivisor(graph, [("v1", 5), ("v2", 0), ("v3", -2)])
            >>> divisor2 = CFDivisor(graph, [("v1", 1), ("v2", -1), ("v3", 3)])
            >>> # Subtract them
            >>> diff_divisor = divisor1 - divisor2
            >>> diff_divisor.get_degree("v1")  # 5 - 1 = 4
            4
            >>> diff_divisor.get_degree("v2")  # 0 - (-1) = 1
            1
            >>> diff_divisor.get_degree("v3")  # -2 - 3 = -5
            -5
            >>> diff_divisor.get_total_degree()  # (5+0-2) - (1-1+3) = 3 - 3 = 0
            0
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
