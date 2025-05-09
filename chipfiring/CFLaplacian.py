import typing
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
