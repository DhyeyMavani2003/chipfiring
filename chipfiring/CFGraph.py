from __future__ import annotations
import warnings
import typing

class Vertex:
    """Represents a vertex in the graph.

    Example:
        >>> v1 = Vertex("A")
        >>> v2 = Vertex("B")
        >>> v3 = Vertex("A")
        >>> v1 == v3  # Same name means equal vertices
        True
        >>> v1 != v2
        True
        >>> v1 < v2  # Ordering is based on name
        True
        >>> str(v1)
        'A'
        >>> vertex_set = {v1, v2, v3}  # v1 and v3 are considered equal
        >>> len(vertex_set)
        2
    """

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
    """Represents an edge in the graph.

    Example:
        >>> v1 = Vertex("A")
        >>> v2 = Vertex("B")
        >>> v3 = Vertex("C")
        >>> e1 = Edge(v1, v2)
        >>> e2 = Edge(v2, v1)  # Same edge, different order
        >>> e3 = Edge(v1, v3)
        >>> e1 == e2  # Edge equality ignores order of vertices
        True
        >>> e1 != e3
        False
        >>> str(e1)
        'A-B'
        >>> edge_set = {e1, e2, e3}  # e1 and e2 are considered equal
        >>> len(edge_set)
        2
    """

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


class CFGraph:
    """Represents a chip-firing graph with multiple edges possible between vertices.

    Example:
        >>> vertices = {"A", "B", "C"}
        >>> edges = [("A", "B", 2), ("B", "C", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> len(graph.vertices)
        3
        >>> graph.total_valence  # 2 edges A-B, 1 edge B-C
        3
        >>> graph.get_valence("A")
        2
        >>> graph.get_valence("B")  # 2 from A-B, 1 from B-C
        3
        >>> graph.get_valence("C")
        1
    """

    def __init__(
        self, vertices: typing.Set[str], edges: typing.List[typing.Tuple[str, str, int]]
    ):
        """Initialize the graph with a set of vertex names and a list of edge tuples.

        Args:
            vertices: Set of vertex names (strings)
            edges: List of tuples (v1_name, v2_name, valence) where v1_name and v2_name are strings
                  and valence is a positive integer representing the number of edges
                  between the vertices

        Raises:
            ValueError: If duplicate vertex names are provided

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Check we have the expected number of vertices
            >>> len(graph.vertices)
            3
            >>> # Check the total valence (number of edges)
            >>> graph.total_valence
            3
            >>> # With duplicate edges, valences are merged
            >>> edges_with_dup = [("A", "B", 2), ("A", "B", 3)]
            >>> with_dup_graph = CFGraph(vertices, edges_with_dup)  # Issues warning
            >>> with_dup_graph.graph[Vertex("A")][Vertex("B")]
            5
        """
        # Check for duplicate vertex names
        if len(vertices) != len(set(vertices)):
            raise ValueError("Duplicate vertex names are not allowed")

        # Create Vertex objects and initialize graph
        self.vertices = {Vertex(name) for name in vertices}
        self.graph: typing.Dict[Vertex, typing.Dict[Vertex, int]] = {}
        self.vertex_total_valence: typing.Dict[Vertex, int] = {}
        self.total_valence: int = 0

        # Add all vertices to the graph
        for vertex in self.vertices:
            self.graph[vertex] = {}
            self.vertex_total_valence[vertex] = 0

        # Add all edges
        if edges:
            self.add_edges(edges)

    def is_loopless(self, v1_name: str, v2_name: str) -> bool:
        """Check if an edge connects a vertex to itself.

        Args:
            v1_name: Name of first vertex
            v2_name: Name of second vertex

        Returns:
            True if v1_name != v2_name (not a self-loop), False otherwise

        Example:
            >>> vertices = {"A", "B"}
            >>> graph = CFGraph(vertices, [])
            >>> graph.is_loopless("A", "B")  # Different vertices
            True
            >>> graph.is_loopless("A", "A")  # Same vertex (self-loop)
            False
        """
        return v1_name != v2_name

    # TODO: If the user adds an edge and one or both vertices are not in the graph,
    # we should add them to the graph.
    def add_edges(self, edges: typing.List[typing.Tuple[str, str, int]]) -> None:
        """Add multiple edges to the graph.

        Args:
            edges: List of tuples (v1_name, v2_name, valence) where v1_name and v2_name are strings
                  and valence is a positive integer representing the number of edges
                  between the vertices

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> graph = CFGraph(vertices, [])
            >>> graph.add_edges([("A", "B", 2), ("B", "C", 1), ("A", "C", 3)])
            >>> graph.graph[Vertex("A")][Vertex("B")]
            2
            >>> graph.graph[Vertex("B")][Vertex("C")]
            1
            >>> graph.graph[Vertex("A")][Vertex("C")]
            3
            >>> # With duplicate edges, a warning is issued
            >>> graph.add_edges([("A", "B", 3)])  # Issues warning
            >>> graph.graph[Vertex("A")][Vertex("B")]  # 2 + 3 = 5
            5
        """
        seen_edges = set()
        for v1_name, v2_name, valence in edges:
            edge = tuple(sorted([v1_name, v2_name]))
            if edge in seen_edges:
                warnings.warn(
                    f"Duplicate edge {v1_name}-{v2_name} found in inputed edges. Merging valences."
                )
            seen_edges.add(edge)
            self.add_edge(v1_name, v2_name, valence)

    def add_edge(self, v1_name: str, v2_name: str, valence: int) -> None:
        """Add edges between vertices with names v1_name and v2_name.

        Args:
            v1_name: Name of first vertex
            v2_name: Name of second vertex
            valence: Number of edges to add between the vertices

        Raises:
            ValueError: If trying to add a self-loop
            ValueError: If valence is not positive
            ValueError: If either vertex is not in the graph

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> graph = CFGraph(vertices, [])
            >>> # Add a single edge with valence 2
            >>> graph.add_edge("A", "B", 2)
            >>> graph.graph[Vertex("A")][Vertex("B")]
            2
            >>> graph.graph[Vertex("B")][Vertex("A")]  # Undirected graph
            2
            >>> # Adding to an existing edge increases valence
            >>> graph.add_edge("A", "B", 3)
            >>> graph.graph[Vertex("A")][Vertex("B")]  # 2 + 3 = 5
            5
            >>> # Invalid operations
            >>> try:
            ...     graph.add_edge("A", "A", 1)  # Self-loop
            ... except ValueError:
            ...     print("Self-loops not allowed")
            Self-loops not allowed
            >>> try:
            ...     graph.add_edge("A", "D", 1)  # D not in graph
            ... except ValueError:
            ...     print("Vertex not in graph")
            Vertex not in graph
        """
        if not self.is_loopless(v1_name, v2_name):
            raise ValueError(
                f"Self-loops are not allowed: attempted to add edge {v1_name}-{v2_name}"
            )
        if valence <= 0:
            raise ValueError("Number of edges must be positive")

        v1, v2 = Vertex(v1_name), Vertex(v2_name)
        if v1 not in self.graph or v2 not in self.graph:
            raise ValueError("Both vertices must be in the graph before adding edges")

        # Add or update edges in both directions (undirected graph)
        if v2 in self.graph[v1]:
            # Edge exists, add to existing valence
            self.graph[v1][v2] += valence
            self.graph[v2][v1] += valence

            # Update vertex totals
            self.vertex_total_valence[v1] += valence
            self.vertex_total_valence[v2] += valence

            # Update total (only count each edge once)
            self.total_valence += valence
        else:
            # New edge
            self.graph[v1][v2] = valence
            self.graph[v2][v1] = valence

            # Update vertex totals
            self.vertex_total_valence[v1] += valence
            self.vertex_total_valence[v2] += valence

            # Update total (only count each edge once)
            self.total_valence += valence

    def get_valence(self, v_name: str) -> int:
        """Get the total valence (sum of all edge valences) for a vertex.

        Args:
            v_name: Name of the vertex

        Returns:
            The total valence of the vertex

        Raises:
            ValueError: If the vertex is not in the graph

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 3)]
            >>> graph = CFGraph(vertices, edges)
            >>> graph.get_valence("A")  # 2 from A-B, 3 from A-C
            5
            >>> graph.get_valence("B")  # 2 from A-B, 1 from B-C
            3
            >>> graph.get_valence("C")  # 1 from B-C, 3 from A-C
            4
            >>> try:
            ...     graph.get_valence("D")  # D not in graph
            ... except ValueError:
            ...     print("Vertex not in graph")
            Vertex not in graph
        """
        v = Vertex(v_name)
        if v not in self.vertex_total_valence:
            raise ValueError(f"Vertex {v_name} not in graph")
        return self.vertex_total_valence[v]

    def get_genus(self) -> int:
        """Get the genus of the graph, which is defined as |E| - |V| + 1.

        Returns:
            The genus of the graph

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Total edges = 4, Vertices = 3
            >>> # Genus = |E| - |V| + 1 = 4 - 3 + 1 = 2
            >>> graph.get_genus()
            2
        """
        return self.total_valence - len(self.graph) + 1

    def remove_vertex(self, vertex_name: str) -> "CFGraph":
        """Create a copy of the graph without the specified vertex.

        Args:
            vertex_name: The name of the vertex to remove

        Returns:
            A new CFGraph object without the specified vertex

        Raises:
            ValueError: If the vertex name is not found in the graph

        Example:
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("C", "D", 3), ("A", "D", 2)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Remove vertex C
            >>> new_graph = graph.remove_vertex("C")
            >>> # Check the new graph has the correct vertices
            >>> len(new_graph.vertices)
            3
            >>> # Check edges are preserved correctly
            >>> new_graph.graph[Vertex("A")][Vertex("B")]
            2
            >>> new_graph.graph[Vertex("A")][Vertex("D")]
            2
            >>> # Check valences
            >>> new_graph.get_valence("A")  # 2 from A-B, 2 from A-D
            4
            >>> new_graph.get_valence("B")  # 2 from A-B
            2
            >>> new_graph.get_valence("D")  # 2 from A-D
            2
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")

        # Create new vertex set without the removed vertex
        remaining_vertices = {v.name for v in self.vertices if v != vertex}

        # Collect edges between remaining vertices
        remaining_edges = []
        processed_edges = set()

        for v1 in self.vertices:
            if v1 != vertex:
                for v2, valence in self.graph[v1].items():
                    if v2 != vertex:
                        edge = tuple(sorted((v1.name, v2.name)))
                        if edge not in processed_edges:
                            remaining_edges.append((v1.name, v2.name, valence))
                            processed_edges.add(edge)

        # Create new graph with remaining vertices and edges
        return CFGraph(remaining_vertices, remaining_edges)

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> "CFGraph":
        """Creates a CFGraph instance from a dictionary representation.

        Args:
            data: A dictionary with 'vertices' (list of names) and 
                  'edges' (list of [v1_name, v2_name, valence] tuples).

        Returns:
            A CFGraph instance.
        """
        vertices = set(data.get("vertices", []))
        edges = data.get("edges", [])
        graph = cls(vertices, edges)

        return graph

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Converts the CFGraph instance to a dictionary representation.

        Returns:
            A dictionary with 'vertices' and 'edges'.
        """
        vertex_names = sorted([v.name for v in self.vertices]) # Sort for consistent output
        
        edge_list = []

        sorted_vertices = sorted(list(self.vertices), key=lambda v: v.name)

        for v1 in sorted_vertices:
            if v1 in self.graph:
                sorted_neighbors = sorted(self.graph[v1].keys(), key=lambda v: v.name)
                for v2 in sorted_neighbors:
                    if v1.name < v2.name:
                        valence = self.graph[v1][v2]
                        edge_list.append([v1.name, v2.name, valence])
                    elif v1.name == v2.name:
                        raise ValueError("Self-loops are not allowed")

        return {"vertices": vertex_names, "edges": edge_list}

    def get_vertex_by_name(self, name: str) -> typing.Optional[Vertex]:
        """Find a vertex in the graph by its name."""
        for vertex in self.vertices:
            if vertex.name == name:
                return vertex
        return None
