from __future__ import annotations
from enum import Enum
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
import typing


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

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientations = [("A", "B"), ("B", "C")]
            >>> orientation = CFOrientation(graph, orientations)
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
            self.set_orientation(source, sink, OrientationState.SOURCE_TO_SINK)

        # Check if the orientation is full after initialization
        self.check_fullness()

    def check_fullness(self) -> bool:
        """Check if all edges have an orientation and update is_full.

        Returns:
            True if all edges have an orientation, False otherwise

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientation = CFOrientation(graph, [("v1", "v2")])
            >>> orientation.check_fullness()
            False
            >>> # Now complete the orientation
            >>> from chipfiring.CFOrientation import Vertex, OrientationState
            >>> v2, v3 = Vertex("v2"), Vertex("v3")
            >>> orientation.set_orientation(v2, v3, OrientationState.SOURCE_TO_SINK)
            >>> v1, v3 = Vertex("v1"), Vertex("v3")
            >>> orientation.set_orientation(v1, v3, OrientationState.SOURCE_TO_SINK)
            >>> orientation.check_fullness()
            True
        """
        for v1 in self.graph.vertices:
            for v2 in self.graph.graph[v1]:
                # Only check each edge once (where v1 < v2)
                if v1 < v2:
                    if self.orientation[v1][v2] == OrientationState.NO_ORIENTATION:
                        self.is_full = False
                        self.is_full_checked = True
                        return False  # Found an unoriented edge
        self.is_full = True  # All edges checked and oriented
        self.is_full_checked = True
        return True

    def set_orientation(
        self, source: Vertex, sink: Vertex, state: OrientationState
    ) -> None:
        """Helper method to set orientation and update in/out degrees.

        Args:
            source: Source vertex
            sink: Sink vertex
            state: New orientation state

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientation = CFOrientation(graph, [])
            >>> from chipfiring.CFOrientation import OrientationState, Vertex
            >>> v_a = Vertex("A")
            >>> v_b = Vertex("B")
            >>> orientation.set_orientation(v_a, v_b, OrientationState.SOURCE_TO_SINK)
            >>> orientation.get_out_degree("A")
            2  # A-B edge has valence 2
            >>> orientation.get_in_degree("B")
            2
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
            >>> orientation = CFOrientation(graph, orientations)
            >>> orientation.get_orientation("v1", "v2")
            ('v1', 'v2')
            >>> orientation.get_orientation("v2", "v1")  # Order doesn't matter
            ('v1', 'v2')
            >>> # For a partially oriented graph:
            >>> partial = CFOrientation(graph, [("v1", "v2")])
            >>> partial.get_orientation("v1", "v2")
            ('v1', 'v2')
            >>> partial.get_orientation("v2", "v3")
            None
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

    def is_source(self, vertex_name: str, neighbor_name: str) -> typing.Optional[bool]:
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
            >>> orientation = CFOrientation(graph, orientations)
            >>> orientation.is_source("v1", "v2")
            True
            >>> orientation.is_source("v2", "v1")
            False
            >>> # For an unoriented edge
            >>> partial = CFOrientation(graph, [("v1", "v2")])
            >>> partial.is_source("v2", "v3")
            None
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

    def is_sink(self, vertex_name: str, neighbor_name: str) -> typing.Optional[bool]:
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
            >>> orientation = CFOrientation(graph, orientations)
            >>> orientation.is_sink("v1", "v2")
            False
            >>> orientation.is_sink("v2", "v1")
            True
            >>> # For an unoriented edge
            >>> partial = CFOrientation(graph, [("v1", "v2")])
            >>> partial.is_sink("v2", "v3")
            None
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
            >>> orientation = CFOrientation(graph, orientations)
            >>> orientation.get_in_degree("v1")
            0
            >>> orientation.get_in_degree("v2")
            1  # from v1
            >>> orientation.get_in_degree("v3")
            2  # from v1, v2
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
            >>> orientation = CFOrientation(graph, orientations)
            >>> orientation.get_out_degree("v1")
            2
            >>> orientation.get_out_degree("v2")
            1  # to v3
            >>> orientation.get_out_degree("v3")
            0
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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
            >>> orientation = CFOrientation(graph, orientations)
            >>> reversed_orientation = orientation.reverse()
            >>> reversed_orientation.get_orientation("v1", "v2")
            ('v2', 'v1')
            >>> reversed_orientation.get_orientation("v2", "v3")
            ('v3', 'v2')
            >>> reversed_orientation.get_orientation("v1", "v3")
            ('v3', 'v1')
        """
        # Ensure the fullness status is up-to-date
        if not self.is_full_checked:
            self.check_fullness()

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

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
            >>> orientation = CFOrientation(graph, orientations)
            >>> div = orientation.divisor()
            >>> div.get_degree("v1")
            -1  # in-degree 0 - 1
            >>> div.get_degree("v2")
            0   # in-degree 1 - 1
            >>> div.get_degree("v3")
            1   # in-degree 2 - 1
        """
        # Ensure the fullness status is up-to-date
        if not self.is_full_checked:
            self.check_fullness()

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
        equal to the divisor of the orientation plus the divisor of the reverse of the orientation. After simplifying, we get that for each vertex v,
        the degree of v in the canonical divisor is the valence of v minus 2.

        Returns:
            A new CFDivisor object representing the canonical divisor.

        Example:
            >>> vertices = {"a", "b", "c"}
            >>> edges = [("a", "b", 2), ("b", "c", 3)]  # Multi-graph
            >>> graph = CFGraph(vertices, edges)
            >>> orientation = CFOrientation(graph, [])  # Orientation doesn't matter
            >>> canonical = orientation.canonical_divisor()
            >>> canonical.get_degree("a")
            0   # valence 2 - 2
            >>> canonical.get_degree("b")
            3   # valence 5 - 2
            >>> canonical.get_degree("c")
            1   # valence 3 - 2
        """
        canonical_degrees = []
        for vertex in self.graph.vertices:
            valence = self.graph.get_valence(vertex.name)
            degree = valence - 2
            canonical_degrees.append((vertex.name, degree))

        # Create and return the new divisor object
        return CFDivisor(self.graph, canonical_degrees)

    def is_partial(self) -> bool:
        """Check whether this orientation is partial (i.e. has at least one unoriented edge).

        Partial orientations are central to the framework of Backman,
        *Riemann–Roch theory for graph orientations* (arXiv:1401.3309), where
        edges may be left unoriented in addition to being oriented in either
        direction.

        Returns:
            True if at least one edge of the underlying graph has no
            orientation, False if the orientation is full.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> CFOrientation(graph, [("v1", "v2")]).is_partial()
            True
            >>> CFOrientation(graph, [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]).is_partial()
            False
        """
        if not self.is_full_checked:
            self.check_fullness()
        return not self.is_full

    def oriented_edge_count(self) -> int:
        """Return the total number of oriented edges (counted with multiplicity).

        Each edge of valence ``k`` contributes ``k`` to the count when oriented.

        Returns:
            Sum of valences over all oriented edges.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 2), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> CFOrientation(graph, [("v1", "v2")]).oriented_edge_count()
            2
        """
        # Each oriented edge is captured by exactly one in_degree entry.
        return sum(self.in_degree.values())

    def unoriented_edge_count(self) -> int:
        """Return the total number of unoriented edges (counted with multiplicity).

        Returns:
            Total valence minus the number of oriented edges.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 2), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> CFOrientation(graph, [("v1", "v2")]).unoriented_edge_count()
            2
        """
        return self.graph.total_valence - self.oriented_edge_count()

    def sources(self) -> typing.Set[str]:
        """Return the names of vertices that are sources of the (partial) orientation.

        Following Backman (arXiv:1401.3309), a vertex ``v`` is a source of a
        partial orientation ``O`` when no oriented edge points into ``v``
        (i.e. ``indeg_O(v) == 0``). Equivalently, every edge incident to ``v``
        that has been oriented points away from ``v``.

        Returns:
            The set of names of source vertices.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> sorted(CFOrientation(graph, [("v1", "v2"), ("v1", "v3"), ("v2", "v3")]).sources())
            ['v1']
        """
        return {v.name for v in self.graph.vertices if self.in_degree[v] == 0}

    def sinks(self) -> typing.Set[str]:
        """Return the names of vertices that are sinks of the (partial) orientation.

        A vertex ``v`` is a sink of a partial orientation ``O`` when no oriented
        edge points out of ``v`` (i.e. ``outdeg_O(v) == 0``).

        Returns:
            The set of names of sink vertices.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> sorted(CFOrientation(graph, [("v1", "v2"), ("v1", "v3"), ("v2", "v3")]).sinks())
            ['v3']
        """
        return {v.name for v in self.graph.vertices if self.out_degree[v] == 0}

    def is_acyclic(self) -> bool:
        """Check whether the (partial) orientation contains no directed cycle.

        Acyclicity is computed on the directed sub-orientation: only edges
        with state ``SOURCE_TO_SINK`` (or equivalently ``SINK_TO_SOURCE``)
        contribute. Unoriented edges are ignored, which matches the
        definition of an acyclic partial orientation used by Backman in
        *Riemann–Roch theory for graph orientations* (arXiv:1401.3309).

        Multi-edges between the same two endpoints in the same direction do
        not create a cycle, but a pair of opposite edges does not arise here
        because each edge is oriented in at most one direction.

        Returns:
            True if there is no directed cycle in the oriented sub-graph,
            False otherwise.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # v1 -> v2 -> v3, v1 -> v3 is a DAG
            >>> CFOrientation(graph, [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]).is_acyclic()
            True
            >>> # v1 -> v2 -> v3 -> v1 is a directed 3-cycle
            >>> CFOrientation(graph, [("v1", "v2"), ("v2", "v3"), ("v3", "v1")]).is_acyclic()
            False
        """
        # Iterative DFS with three-color marking on the oriented sub-graph.
        WHITE, GRAY, BLACK = 0, 1, 2
        color: typing.Dict[Vertex, int] = {v: WHITE for v in self.graph.vertices}

        for start in self.graph.vertices:
            if color[start] != WHITE:
                continue
            # Stack entries: (vertex, iterator over outgoing oriented neighbors)
            stack: typing.List[typing.Tuple[Vertex, typing.Iterator[Vertex]]] = [
                (start, iter(
                    n for n, st in self.orientation[start].items()
                    if st == OrientationState.SOURCE_TO_SINK
                ))
            ]
            color[start] = GRAY
            while stack:
                v, it = stack[-1]
                next_neighbor = next(it, None)
                if next_neighbor is None:
                    color[v] = BLACK
                    stack.pop()
                    continue
                c = color[next_neighbor]
                if c == GRAY:
                    return False  # back-edge -> cycle
                if c == WHITE:
                    color[next_neighbor] = GRAY
                    stack.append((
                        next_neighbor,
                        iter(
                            n for n, st in self.orientation[next_neighbor].items()
                            if st == OrientationState.SOURCE_TO_SINK
                        ),
                    ))
        return True

    def partial_divisor(self) -> CFDivisor:
        """Return the divisor associated with this (possibly partial) orientation.

        Following Backman (arXiv:1401.3309, Definition 3.1), the divisor of a
        partial orientation ``O`` is

            D_O(v) = indeg_O(v) - 1,

        counting only edges that have been oriented. For full orientations
        this coincides with :meth:`divisor`; unlike :meth:`divisor`, this
        method does not require the orientation to be full.

        Returns:
            A new :class:`CFDivisor` with degree ``indeg_O(v) - 1`` at each
            vertex ``v``.

        Example:
            >>> vertices = {"v1", "v2", "v3"}
            >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Only v1 -> v2 oriented; v2-v3 and v1-v3 unoriented
            >>> partial = CFOrientation(graph, [("v1", "v2")])
            >>> div = partial.partial_divisor()
            >>> div.get_degree("v1")
            -1
            >>> div.get_degree("v2")
            0
            >>> div.get_degree("v3")
            -1
        """
        divisor_degrees = [
            (v.name, self.in_degree[v] - 1) for v in self.graph.vertices
        ]
        return CFDivisor(self.graph, divisor_degrees)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Converts the CFOrientation instance to a dictionary representation.

        Returns:
            A dictionary with 'graph' and 'orientations'.
        """
        graph_dict = self.graph.to_dict()
        
        orientation_list = []
        
        sorted_vertices = sorted(list(self.graph.vertices), key=lambda v: v.name)

        for v1 in sorted_vertices:
            sorted_neighbors = sorted(self.graph.graph[v1].keys(), key=lambda v: v.name)
            for v2 in sorted_neighbors:
                if v1.name < v2.name:
                    state = self.orientation[v1].get(v2)
                    if state == OrientationState.SOURCE_TO_SINK:
                        orientation_list.append([v1.name, v2.name])
                    elif state == OrientationState.SINK_TO_SOURCE:
                        orientation_list.append([v2.name, v1.name])
        
        return {
            "graph": graph_dict,
            "orientations": orientation_list
        }

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> "CFOrientation":
        """Creates a CFOrientation instance from a dictionary representation.

        Args:
            data: A dictionary with 'graph' (CFGraph representation) 
                  and 'orientations' (list of [source_name, sink_name] tuples).

        Returns:
            A CFOrientation instance.
        """
        graph_data = data.get("graph")
        if not graph_data:
            raise ValueError("Graph data is missing in CFOrientation representation")
        
        graph = CFGraph.from_dict(graph_data)
        orientations_list = data.get("orientations", [])
        
        return cls(graph, orientations_list)
