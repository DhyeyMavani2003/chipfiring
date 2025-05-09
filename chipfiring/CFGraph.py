import warnings
import typing


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


class CFGraph:
    """Represents a chip-firing graph with multiple edges possible between vertices."""

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
        """Check if an edge connects a vertex to itself."""
        return v1_name != v2_name

    # TODO: If the user adds an edge and one or both vertices are not in the graph,
    # we should add them to the graph.
    def add_edges(self, edges: typing.List[typing.Tuple[str, str, int]]) -> None:
        """Add multiple edges to the graph.

        Args:
            edges: List of tuples (v1_name, v2_name, valence) where v1_name and v2_name are strings
                  and valence is a positive integer representing the number of edges
                  between the vertices
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
        """Get the total valence (sum of all edge valences) for a vertex."""
        v = Vertex(v_name)
        if v not in self.vertex_total_valence:
            raise ValueError(f"Vertex {v_name} not in graph")
        return self.vertex_total_valence[v]

    def get_genus(self) -> int:
        """Get the genus of the graph, which is defined as |E| - |V| + 1."""
        return self.total_valence - len(self.graph) + 1

    def remove_vertex(self, vertex_name: str) -> "CFGraph":
        """Create a copy of the graph without the specified vertex.

        Args:
            vertex_name: The name of the vertex to remove

        Returns:
            A new CFGraph object without the specified vertex

        Raises:
            ValueError: If the vertex name is not found in the graph
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
