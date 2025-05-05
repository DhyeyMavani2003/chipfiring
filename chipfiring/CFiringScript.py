from __future__ import annotations
import typing
from chipfiring.CFGraph import CFGraph, Vertex

class CFiringScript:
    """Represents a chip-firing script for a given graph.

    A firing script specifies a net number of times each vertex fires.
    Positive values indicate lending (firing), while negative values
    indicate borrowing.
    """

    def __init__(self, graph: CFGraph, script: typing.Dict[str, int]):
        """Initialize the firing script.

        Args:
            graph: The CFGraph object the script applies to.
            script: A dictionary mapping vertex names (strings) to integers.
                    Positive integers represent lending moves (firings).
                    Negative integers represent borrowing moves.
                    Vertices not included in the script are assumed to have 0 net firings.

        Raises:
            ValueError: If any vertex name in the script is not present in the graph.
        """
        self.graph = graph
        self._script: typing.Dict[Vertex, int] = {}

        # Validate and store the script using Vertex objects
        for vertex_name, firings in script.items():
            vertex = Vertex(vertex_name)
            if vertex not in self.graph.vertices:
                raise ValueError(f"Vertex '{vertex_name}' in the script is not present in the graph.")
            self._script[vertex] = firings

    def get_firings(self, vertex_name: str) -> int:
        """Get the number of firings for a given vertex.

        Returns 0 if the vertex is not explicitly mentioned in the script.

        Args:
            vertex_name: The name of the vertex.

        Returns:
            The net number of firings for the vertex.

        Raises:
            ValueError: If the vertex name is not present in the graph.
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.vertices:
            raise ValueError(f"Vertex '{vertex_name}' is not present in the graph.")
        return self._script.get(vertex, 0)

    @property
    def script(self) -> typing.Dict[str, int]:
        """Return the script as a dictionary mapping vertex names to firings."""
        return {vertex.name: firings for vertex, firings in self._script.items()}