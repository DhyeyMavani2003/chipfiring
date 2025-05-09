from enum import Enum
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
import typing
from typing import Optional


class OrientationState(Enum):
    """Represents the possible states of an edge orientation."""

    NO_ORIENTATION = 0  # Edge exists but has no orientation
    SOURCE_TO_SINK = 1  # Edge is oriented from source to sink
    SINK_TO_SOURCE = 2  # Edge is oriented from sink to source


class CFOrientation:
    """Represents an orientation of edges in a chip-firing graph."""

    def __init__(
        self, graph: CFGraph, orientations: typing.List[typing.Tuple[str, str]]
    ):
        """Initialize the orientation with a graph and list of oriented edges.

        Args:
            graph: A CFGraph object representing the underlying graph
            orientations: List of tuples (source_name, sink_name) where source_name and sink_name
                        are strings representing vertex names. Each tuple indicates that the edge
                        is oriented from source to sink.

        Raises:
            ValueError: If an edge specified in orientations does not exist in the graph
            ValueError: If multiple orientations are specified for the same edge
        """
        self.graph = graph
        # Initialize orientation dictionary
        # First level keys are vertices
        # Second level keys are vertices
        # Value is an OrientationState enum indicating the orientation state
        self.orientation: typing.Dict[Vertex, typing.Dict[Vertex, OrientationState]] = {
            v: {} for v in graph.vertices
        }

        # Initialize in/out degree counters for each vertex
        self.in_degree: typing.Dict[Vertex, int] = {v: 0 for v in graph.vertices}
        self.out_degree: typing.Dict[Vertex, int] = {v: 0 for v in graph.vertices}

        # Flag to track if all edges have an orientation
        self.is_full: bool = False
        self.is_full_checked: bool = False  # Flag to track if is_full is up to date

        # Initialize all edges with NO_ORIENTATION
        for v1 in graph.vertices:
            for v2, _ in graph.graph[v1].items():
                if v2 not in self.orientation[v1]:
                    self.orientation[v1][v2] = OrientationState.NO_ORIENTATION
                    self.orientation[v2][v1] = OrientationState.NO_ORIENTATION

        # Process each orientation
        for source_name, sink_name in orientations:
            source = Vertex(source_name)
            sink = Vertex(sink_name)

            # Check if vertices exist in graph
            if source not in graph.graph or sink not in graph.graph:
                raise ValueError(f"Edge {source_name}-{sink_name} not found in graph")

            # Check if edge exists in graph
            if sink not in graph.graph[source]:
                raise ValueError(f"Edge {source_name}-{sink_name} not found in graph")

            # Check if edge already has an orientation (other than NO_ORIENTATION)
            if (
                self.orientation[source][sink] != OrientationState.NO_ORIENTATION
                or self.orientation[sink][source] != OrientationState.NO_ORIENTATION
            ):
                # Sort names for consistent error message
                v1_name, v2_name = sorted([source_name, sink_name])
                raise ValueError(
                    f"Multiple orientations specified for edge {v1_name}-{v2_name}"
                )

            # Store the orientation and update in/out degrees
            self._set_orientation(source, sink, OrientationState.SOURCE_TO_SINK)

        # Check if the orientation is full after initialization
        self._check_fullness()

    def _check_fullness(self) -> None:
        """Check if all edges have an orientation and update is_full."""
        for v1 in self.graph.vertices:
            for v2 in self.graph.graph[v1]:
                # Only check each edge once (where v1 < v2)
                if v1 < v2:
                    if self.orientation[v1][v2] == OrientationState.NO_ORIENTATION:
                        self.is_full = False
                        self.is_full_checked = True
                        return  # Found an unoriented edge
        self.is_full = True  # All edges checked and oriented
        self.is_full_checked = True

    def _set_orientation(
        self, source: Vertex, sink: Vertex, state: OrientationState
    ) -> None:
        """Helper method to set orientation and update in/out degrees.

        Args:
            source: Source vertex
            sink: Sink vertex
            state: New orientation state
        """
        old_state = self.orientation[source][sink]
        valence = self.graph.graph[source][sink]

        # Remove old orientation's effect on degrees (if any)
        if old_state == OrientationState.SOURCE_TO_SINK:
            self.out_degree[source] -= valence
            self.in_degree[sink] -= valence
        elif old_state == OrientationState.SINK_TO_SOURCE:
            self.in_degree[source] -= valence
            self.out_degree[sink] -= valence

        # Set new orientation
        self.orientation[source][sink] = state
        self.orientation[sink][source] = (
            OrientationState.NO_ORIENTATION
            if state == OrientationState.NO_ORIENTATION
            else (
                OrientationState.SINK_TO_SOURCE
                if state == OrientationState.SOURCE_TO_SINK
                else OrientationState.SOURCE_TO_SINK
            )
        )

        # Update degrees based on new orientation
        if state == OrientationState.SOURCE_TO_SINK:
            self.out_degree[source] += valence
            self.in_degree[sink] += valence
        elif state == OrientationState.SINK_TO_SOURCE:
            self.in_degree[source] += valence
            self.out_degree[sink] += valence

        # If we set an edge to NO_ORIENTATION, the orientation is no longer full
        if state == OrientationState.NO_ORIENTATION:
            self.is_full = False
            self.is_full_checked = True

        if (
            old_state == OrientationState.NO_ORIENTATION
            and state != OrientationState.NO_ORIENTATION
        ):
            self.is_full_checked = False

    def get_orientation(
        self, v1_name: str, v2_name: str
    ) -> typing.Optional[typing.Tuple[str, str]]:
        """Get the orientation of an edge between two vertices.

        Args:
            v1_name: Name of first vertex
            v2_name: Name of second vertex

        Returns:
            Tuple (source_name, sink_name) indicating the orientation,
            or None if the edge exists but has no orientation

        Raises:
            ValueError: If the edge does not exist
        """
        v1 = Vertex(v1_name)
        v2 = Vertex(v2_name)

        # Check if vertices exist in graph
        if v1 not in self.graph.graph or v2 not in self.graph.graph:
            raise ValueError(f"Edge {v1_name}-{v2_name} not found in graph")

        # Check if edge exists
        if v2 not in self.graph.graph[v1]:
            raise ValueError(f"Edge {v1_name}-{v2_name} not found in graph")

        state = self.orientation[v1][v2]
        if state == OrientationState.NO_ORIENTATION:
            return None
        elif state == OrientationState.SOURCE_TO_SINK:
            return v1_name, v2_name
        else:  # state == OrientationState.SINK_TO_SOURCE
            return v2_name, v1_name

    def is_source(self, vertex_name: str, neighbor_name: str) -> Optional[bool]:
        """Check if a vertex is the source of an oriented edge.

        Args:
            vertex_name: Name of the vertex to check
            neighbor_name: Name of the neighboring vertex

        Returns:
            True if the vertex is the source of the edge,
            False if the vertex is the sink of the edge,
            None if the edge exists but has no orientation

        Raises:
            ValueError: If the edge does not exist
        """
        vertex = Vertex(vertex_name)
        neighbor = Vertex(neighbor_name)

        # Check if vertices exist in graph
        if vertex not in self.graph.graph or neighbor not in self.graph.graph:
            raise ValueError(f"Edge {vertex_name}-{neighbor_name} not found in graph")

        # Check if edge exists
        if neighbor not in self.graph.graph[vertex]:
            raise ValueError(f"Edge {vertex_name}-{neighbor_name} not found in graph")

        state = self.orientation[vertex][neighbor]
        if state == OrientationState.NO_ORIENTATION:
            return None
        return state == OrientationState.SOURCE_TO_SINK

    def is_sink(self, vertex_name: str, neighbor_name: str) -> Optional[bool]:
        """Check if a vertex is the sink of an oriented edge.

        Args:
            vertex_name: Name of the vertex to check
            neighbor_name: Name of the neighboring vertex

        Returns:
            True if the vertex is the sink of the edge,
            False if the vertex is the source of the edge,
            None if the edge exists but has no orientation

        Raises:
            ValueError: If the edge does not exist
        """
        vertex = Vertex(vertex_name)
        neighbor = Vertex(neighbor_name)

        # Check if vertices exist in graph
        if vertex not in self.graph.graph or neighbor not in self.graph.graph:
            raise ValueError(f"Edge {vertex_name}-{neighbor_name} not found in graph")

        # Check if edge exists
        if neighbor not in self.graph.graph[vertex]:
            raise ValueError(f"Edge {vertex_name}-{neighbor_name} not found in graph")

        state = self.orientation[vertex][neighbor]
        if state == OrientationState.NO_ORIENTATION:
            return None
        return state == OrientationState.SINK_TO_SOURCE

    def get_in_degree(self, vertex_name: str) -> int:
        """Get the in-degree of a vertex, which is the sum of valences of edges oriented into the vertex.

        Args:
            vertex_name: Name of the vertex to get the in-degree for

        Returns:
            The in-degree of the vertex

        Raises:
            ValueError: If the vertex name is not found in the graph
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")
        return self.in_degree[vertex]

    def get_out_degree(self, vertex_name: str) -> int:
        """Get the out-degree of a vertex, which is the sum of valences of edges oriented out of the vertex.

        Args:
            vertex_name: Name of the vertex to get the out-degree for

        Returns:
            The out-degree of the vertex

        Raises:
            ValueError: If the vertex name is not found in the graph
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")
        return self.out_degree[vertex]

    def reverse(self) -> "CFOrientation":
        """Return a new CFOrientation object with all edge orientations reversed.

        Raises:
            RuntimeError: If the current orientation is not full (i.e., contains unoriented edges).

        Returns:
            A new CFOrientation object representing the reversed orientation.
        """
        # Ensure the fullness status is up-to-date
        if not self.is_full_checked:
            self._check_fullness()

        # Check if the orientation is full
        if not self.is_full:
            raise RuntimeError(
                "Cannot reverse a not full orientation. All edges must be oriented."
            )

        reversed_orientations = []
        processed_edges = set()

        for v1 in self.graph.vertices:
            for v2 in self.graph.graph[v1]:
                # Process each edge only once
                edge = tuple(sorted((v1, v2)))
                if edge not in processed_edges:
                    processed_edges.add(edge)

                    state = self.orientation[v1][v2]
                    if state == OrientationState.SOURCE_TO_SINK:  # v1 -> v2
                        reversed_orientations.append((v2.name, v1.name))
                    elif state == OrientationState.SINK_TO_SOURCE:  # v1 <- v2
                        reversed_orientations.append((v1.name, v2.name))
                    # No need to handle NO_ORIENTATION as we checked for fullness

        # Create and return the new orientation object
        return CFOrientation(self.graph, reversed_orientations)

    def divisor(self) -> CFDivisor:
        """Returns the divisor associated with the orientation; by definition, for each vertex v,
        the degree of v in the divisor is the in-degree of v in the orientation minus 1.

        Raises:
            RuntimeError: If the current orientation is not full (i.e., contains unoriented edges).

        Returns:
            A new CFDivisor object representing the calculated divisor.
        """
        # Ensure the fullness status is up-to-date
        if not self.is_full_checked:
            self._check_fullness()

        # Check if the orientation is full
        if not self.is_full:
            raise RuntimeError(
                "Cannot create divisor: Orientation is not full. All edges must be oriented."
            )

        divisor_degrees = []
        for vertex in self.graph.vertices:
            degree = self.in_degree[vertex] - 1
            divisor_degrees.append((vertex.name, degree))

        # Create and return the new divisor object
        return CFDivisor(self.graph, divisor_degrees)

    def canonical_divisor(self) -> CFDivisor:
        """Returns the canonical divisor associated with the graph; by definition, the canonical divisor of an orientation is
        equal to the divisor of the orientation plus the divisor of the reverse of the orientation. After simlifying, we get thatfor each vertex v,
        the degree of v in the canonical divisor is the valence of v minus 2.

        Returns:
            A new CFDivisor object representing the canonical divisor.
        """
        canonical_degrees = []
        for vertex in self.graph.vertices:
            valence = self.graph.get_valence(vertex.name)
            degree = valence - 2
            canonical_degrees.append((vertex.name, degree))

        # Create and return the new divisor object
        return CFDivisor(self.graph, canonical_degrees)
