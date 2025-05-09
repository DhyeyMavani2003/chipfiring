from __future__ import annotations
import typing
from typing import Optional
from chipfiring.CFGraph import CFGraph, Vertex


class CFiringScript:
    """Represents a chip-firing script for a given graph.

    A firing script specifies a net number of times each vertex fires.
    Positive values indicate lending (firing), while negative values
    indicate borrowing.
    """

    def __init__(self, graph: CFGraph, script: Optional[typing.Dict[str, int]] = None):
        """Initialize the firing script.

        Args:
            graph: The CFGraph object the script applies to.
            script: A dictionary mapping vertex names (strings) to integers.
                    Positive integers represent lending moves (firings).
                    Negative integers represent borrowing moves.
                    Vertices not included in the script are assumed to have 0 net firings.
                    If None, an empty script will be created (default: None).

        Raises:
            ValueError: If any vertex name in the script is not present in the graph.
        """
        self.graph = graph
        self._script = {}

        # Validate and store the script using Vertex objects
        if script is not None:
            for vertex_name, firings in script.items():
                vertex = Vertex(vertex_name)
                if vertex not in self.graph.vertices:
                    raise ValueError(
                        f"Vertex '{vertex_name}' in the script is not present in the graph."
                    )
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

    def set_firings(self, vertex_name: str, firings: int) -> None:
        """Set the number of firings for a given vertex.

        Args:
            vertex_name: The name of the vertex.
            firings: The net number of firings to set for the vertex.

        Raises:
            ValueError: If the vertex name is not present in the graph.
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.vertices:
            raise ValueError(f"Vertex '{vertex_name}' is not present in the graph.")
        self._script[vertex] = firings

    def update_firings(self, vertex_name: str, additional_firings: int) -> None:
        """Update the number of firings for a given vertex by adding to the current value.

        Args:
            vertex_name: The name of the vertex.
            additional_firings: The number of firings to add (can be negative to reduce firings).

        Raises:
            ValueError: If the vertex name is not present in the graph.
        """
        current_firings = self.get_firings(vertex_name)
        self.set_firings(vertex_name, current_firings + additional_firings)

    @property
    def script(self) -> typing.Dict[str, int]:
        """Return the script as a dictionary mapping vertex names to firings."""
        to_return = {}
        for vertex in self.graph.vertices:
            to_return[vertex.name] = self.get_firings(vertex.name)
        return to_return
