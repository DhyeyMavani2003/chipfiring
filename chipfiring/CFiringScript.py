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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 2)]
            >>> graph = CFGraph(vertices, edges)
            >>> script_dict = {"v1": 2, "v3": -1}  # v1 fires twice, v3 borrows once
            >>> firing_script = CFiringScript(graph, script_dict)
            >>> firing_script.script
            {'v1': 2, 'v3': -1, 'v2': 0}  # v2 has 0 firings by default

            >>> # Empty script
            >>> empty_script = CFiringScript(graph, {})
            >>> empty_script.script
            {'v1': 0, 'v2': 0, 'v3': 0}
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 2)]
            >>> graph = CFGraph(vertices, edges)
            >>> script_dict = {"v1": 5, "v2": -3}
            >>> firing_script = CFiringScript(graph, script_dict)
            >>> firing_script.get_firings("v1")
            5
            >>> firing_script.get_firings("v2")
            -3
            >>> firing_script.get_firings("v3")  # Not explicitly in script
            0
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 2)]
            >>> graph = CFGraph(vertices, edges)
            >>> firing_script = CFiringScript(graph, {})
            >>> firing_script.set_firings("v1", 3)
            >>> firing_script.get_firings("v1")
            3
            >>> firing_script.set_firings("v2", -2)
            >>> firing_script.script
            {'v1': 3, 'v2': -2, 'v3': 0}
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 2)]
            >>> graph = CFGraph(vertices, edges)
            >>> script_dict = {"v1": 1}
            >>> firing_script = CFiringScript(graph, script_dict)
            >>> firing_script.update_firings("v1", 2)  # Add 2 more firings
            >>> firing_script.get_firings("v1")
            3  # 1 + 2
            >>> firing_script.update_firings("v2", -1)  # Add -1 (borrow once)
            >>> firing_script.get_firings("v2")
            -1  # 0 + (-1)
        """
        current_firings = self.get_firings(vertex_name)
        self.set_firings(vertex_name, current_firings + additional_firings)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Converts the CFiringScript instance to a dictionary representation.

        Returns:
            A dictionary with 'graph' and 'script' (mapping vertex names to firings).
        """
        graph_dict = self.graph.to_dict()
        
        script_to_store = {v.name: f for v, f in self._script.items()} # Use internal _script

        return {
            "graph": graph_dict,
            "script": script_to_store
        }

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> "CFiringScript":
        """Creates a CFiringScript instance from a dictionary representation.

        Args:
            data: A dictionary with 'graph' (CFGraph representation) 
                  and 'script' (dictionary mapping vertex names to firings).

        Returns:
            A CFiringScript instance.
        """
        graph_data = data.get("graph")
        if not graph_data:
            raise ValueError("Graph data is missing in CFiringScript representation")
        
        graph = CFGraph.from_dict(graph_data)
        script_dict = data.get("script", {}) # Script can be empty, defaults to {} in constructor
        
        return cls(graph, script_dict)

    @property
    def script(self) -> typing.Dict[str, int]:
        """Return the script as a dictionary mapping vertex names to firings.

        Returns:
            A dictionary where keys are vertex names and values are the number of firings.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 2)]
            >>> graph = CFGraph(vertices, edges)
            >>> script_dict = {"v2": 10, "v3": -5}
            >>> firing_script = CFiringScript(graph, script_dict)
            >>> firing_script.script
            {'v1': 0, 'v2': 10, 'v3': -5}
        """
        to_return = {}
        for vertex in self.graph.vertices:
            to_return[vertex.name] = self.get_firings(vertex.name)
        return to_return
