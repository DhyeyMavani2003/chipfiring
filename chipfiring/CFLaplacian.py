import typing
import math
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
from .CFiringScript import CFiringScript
from collections import defaultdict


class CFLaplacian:
    """Represents the Laplacian operator for a chip-firing graph."""

    def __init__(self, graph: CFGraph):
        """
        Initialize the Laplacian with a CFGraph.

        Args:
            graph: A CFGraph object representing the graph.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> laplacian = CFLaplacian(graph)
        """
        self.graph = graph

    def _construct_matrix(self) -> typing.Dict[Vertex, typing.Dict[Vertex, int]]:
        """
        Construct the Laplacian matrix representation for the graph.

        Returns:
            A dictionary where each key is a Vertex, and the value is another
            dictionary representing the row of the Laplacian matrix for that vertex.
            The inner dictionary maps neighboring Vertices to their corresponding
            negative edge valence, and the vertex itself maps to its total valence.

        Example:
            >>> vertices = {"a", "b", "c"}
            >>> edges = [("a", "b", 2), ("b", "c", 3)]
            >>> graph = CFGraph(vertices, edges)
            >>> laplacian = CFLaplacian(graph)
            >>> matrix = laplacian._construct_matrix()
            >>> # The matrix would look like:
            >>> #    a  b  c
            >>> # a [2 -2  0]
            >>> # b [-2 5 -3]
            >>> # c [0 -3  3]
        """

        laplacian: typing.Dict[Vertex, typing.Dict[Vertex, int]] = {}
        vertices = self.graph.vertices

        for v in vertices:
            laplacian[v] = defaultdict(int)  # Initialize row for vertex v
            # Diagonal entry: total valence of vertex v
            degree = self.graph.get_valence(v.name)
            laplacian[v][v] = degree
            # Off-diagonal entries: negative valence for neighbors
            if v in self.graph.graph:  # Check if vertex has neighbors
                for w, valence in self.graph.graph[v].items():
                    laplacian[v][w] = -valence

        return laplacian

    def apply(self, divisor: CFDivisor, firing_script: CFiringScript) -> CFDivisor:
        """
        Apply the Laplacian to a firing script and add the result to an initial divisor.

        Calculates D' = D - L * s, where D is the initial divisor, L is the Laplacian,
        s is the firing script vector, and D' is the resulting divisor.

        Args:
            divisor: The initial CFDivisor object representing chip counts.
            firing_script: The CFiringScript object representing the net firings.

        Returns:
            A new CFDivisor object representing the chip configuration after applying
            the firing script via the Laplacian.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> degrees = [("v1", 5), ("v2", 0), ("v3", -2)]
            >>> divisor = CFDivisor(graph, degrees)
            >>> script = {"v1": 1, "v2": -1}  # v1 fires once, v2 borrows once
            >>> firing_script = CFiringScript(graph, script)
            >>> laplacian = CFLaplacian(graph)
            >>> result = laplacian.apply(divisor, firing_script)
            >>> result.get_degree("v1")
            2  # 5 - 3
            >>> result.get_degree("v2")
            3  # 0 - (-3)
            >>> result.get_degree("v3")
            -2  # -2 - 0
        """
        laplacian = self._construct_matrix()
        # Start with the initial chip counts from the divisor
        resulting_degrees: typing.Dict[Vertex, int] = divisor.degrees.copy()
        vertices = self.graph.vertices

        # Calculate the change in chips: -L * s
        # Iterate through each row v of the Laplacian
        for v in vertices:
            change_at_v = 0
            # Iterate through each column w of the Laplacian row for v
            for w in vertices:
                laplacian_vw = laplacian[v][w]
                firings_w = firing_script.get_firings(w.name)  # s[w]
                change_at_v += laplacian_vw * firings_w

            # Update the degree at vertex v: D'[v] = D[v] - change_at_v
            resulting_degrees[v] -= change_at_v

        # Convert the resulting degrees dict back to the list format for CFDivisor constructor
        final_degrees_list = [
            (vertex.name, degree) for vertex, degree in resulting_degrees.items()
        ]

        # Create and return the new divisor
        return CFDivisor(self.graph, final_degrees_list)

    def get_matrix_entry(self, v_name: str, w_name: str) -> int:
        """
        Get the value of the Laplacian matrix at entry (v, w).

        Args:
            v_name: The name of the row vertex.
            w_name: The name of the column vertex.

        Returns:
            The integer value of the Laplacian matrix L[v][w].

        Raises:
            ValueError: If v_name or w_name are not in the graph.

        Example:
            >>> vertices = {"a", "b", "c"}
            >>> edges = [("a", "b", 2), ("b", "c", 3)]
            >>> graph = CFGraph(vertices, edges)
            >>> laplacian = CFLaplacian(graph)
            >>> laplacian.get_matrix_entry("a", "a")
            2  # Diagonal entry: valence of vertex a
            >>> laplacian.get_matrix_entry("b", "b")
            5  # Diagonal entry: valence of vertex b (2+3)
            >>> laplacian.get_matrix_entry("a", "b")
            -2  # Off-diagonal: negative valence between a and b
            >>> laplacian.get_matrix_entry("a", "c")
            0   # Off-diagonal: a and c are not neighbors
        """
        v = Vertex(v_name)
        w = Vertex(w_name)
        if v not in self.graph.vertices or w not in self.graph.vertices:
            raise ValueError(
                "Both vertex names must correspond to vertices in the graph."
            )

        matrix = self._construct_matrix()
        # Return L[v][w], defaulting to 0 if w is not a neighbor of v (or if v=w and v has no neighbors)
        return matrix.get(v, {}).get(w, 0)

    def get_reduced_matrix(
        self, q: Vertex
    ) -> typing.Dict[Vertex, typing.Dict[Vertex, int]]:
        """
        Get the reduced Laplacian matrix for a given vertex q.

        Args:
            q: The vertex to reduce the matrix with respect to.

        Returns:
            A dictionary representing the reduced Laplacian matrix.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
            >>> # The full Laplacian matrix is:
            >>> #    A  B  C
            >>> # A [3 -2 -1]
            >>> # B [-2 3 -1]
            >>> # C [-1 -1 2]
            >>> # Reducing with respect to B, we get:
            >>> #    A  C
            >>> # A [3 -1]
            >>> # C [-1 2]
        """
        laplacian = self._construct_matrix()
        vertices = self.graph.vertices

        # Create a new dictionary for the reduced matrix
        reduced_matrix: typing.Dict[Vertex, typing.Dict[Vertex, int]] = {}

        # For each vertex except q, create a row in the reduced matrix
        for v in vertices:
            if v != q:
                reduced_matrix[v] = {}
                # For each vertex except q, add an entry to the row
                for w in vertices:
                    if w != q:
                        reduced_matrix[v][w] = laplacian[v][w]

        return reduced_matrix

    def apply_reduced_matrix(
        self,
        divisor: CFDivisor,
        reduced_matrix: typing.Dict[Vertex, typing.Dict[Vertex, int]],
        q: Vertex,
    ) -> typing.List[typing.Tuple[str, int]]:
        """
        Apply the reduced Laplacian matrix to a divisor.

        Args:
            divisor: The initial CFDivisor object representing chip counts.
            reduced_matrix: The reduced Laplacian matrix to apply.
            q: The vertex to reduce the matrix with respect to.

        Returns:
            A list of tuples representing the new divisor after applying the reduced matrix.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> laplacian = CFLaplacian(graph)
            >>> reduced_matrix = laplacian.get_reduced_matrix(Vertex("B"))
            >>> # The reduced matrix is:
            >>> #    A  C
            >>> # A [3 -1]
            >>> # C [-1 2]
            >>> # The initial divisor is:
            >>> # [(A, 3), (B, 0), (C, 0)]
            >>> # Applying the reduced matrix to the divisor with respect to B, we get:
            >>> # [(A, -6), (C, 3)]
        """
        # Get the initial chip counts from the divisor
        initial_degrees = divisor.degrees

        # Create a new dictionary for the resulting degrees
        resulting_degrees = {}

        # For each vertex in the reduced matrix, calculate the new degree
        for v in reduced_matrix:
            new_degree = initial_degrees[v]
            for w in reduced_matrix[v]:
                new_degree -= reduced_matrix[v][w] * initial_degrees[w]
            resulting_degrees[v] = math.floor(new_degree)

        # Create a new list of tuples for the resulting degrees
        final_degrees_list = [
            (vertex.name, degree) for vertex, degree in resulting_degrees.items()
        ]

        # Return the new list of degrees
        return final_degrees_list
