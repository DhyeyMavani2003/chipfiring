from __future__ import annotations
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
import typing
import itertools
import copy

class CFConfig:
    """
    Represents a configuration c with respect to a fixed vertex q, where c is an element of Z(V~),
    and V~ = V - {q}.
    Operations like lending/borrowing can still occur at q, affecting the underlying divisor,
    but the configuration's properties (degree, non-negativity) are defined over V~.

    Example:
        >>> vertices = {"A", "B", "C"}
        >>> edges = [("A", "B", 1), ("B", "C", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
        >>> config_respect_A = CFConfig(divisor, "A")
        >>> config_respect_A.get_degree_at("B")
        1
        >>> config_respect_A.get_degree_sum() # c(B) + c(C) = 1 + 0
        1
        >>> config_respect_A.is_non_negative()
        True
    """
    def __init__(self, divisor: CFDivisor, q_name: str):
        """
        Initializes a configuration.

        Args:
            divisor: The CFDivisor object (representing chip counts on all vertices V).
            q_name: The name of the vertex q to be excluded for configuration properties.

        Raises:
            ValueError: If q_name is not in the divisor's graph.
            
        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.get_degree_at("B")
            1
        """
        self.divisor: CFDivisor = divisor 
        self.graph: CFGraph = divisor.graph
        
        q_vertex_candidate = Vertex(q_name)
        if q_vertex_candidate not in self.graph.vertices:
            raise ValueError(f"Vertex q='{q_name}' not found in the graph of the divisor.")
        self.q_vertex: Vertex = q_vertex_candidate
        
        self.v_tilde_vertices: typing.Set[Vertex] = self.graph.vertices - {self.q_vertex}

    # --- Properties related to the configuration c on V~ ---
    def get_degree_at(self, vertex_name: str) -> int:
        """
        Returns c(v), the number of chips associated with vertex v in the configuration (v in V~).
        
        Args:
            vertex_name: The name of the vertex in V~.

        Returns:
            The number of chips c(v).

        Raises:
            ValueError: If vertex_name is q or not in V~.
            
        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.get_degree_at("B")
            1
        """
        v = Vertex(vertex_name)
        if v == self.q_vertex:
            raise ValueError(f"Configuration degree is not defined for q_vertex '{self.q_vertex.name}'. Use `get_q_underlying_degree()` for the underlying divisor's D(q).")
        if v not in self.v_tilde_vertices:
            raise ValueError(f"Vertex '{vertex_name}' not in V~ (= V - {{q}}).")
        return self.divisor.get_degree(vertex_name)

    def is_non_negative(self) -> bool:
        """
        Checks if the configuration c is non-negative (c(v) >= 0 for all v in V~).
        
        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.is_non_negative()
            True
        """
        for v_node in self.v_tilde_vertices:
            if self.get_degree_at(v_node.name) < 0:
                return False
        return True

    def get_degree_sum(self) -> int:
        """
        Calculates deg(c) = sum_{v in V~} c(v).
        
        Returns:
            The sum of the configuration degrees c(v) for v in V~.
        
        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.get_degree_sum()
            1
        """
        current_sum = 0
        for v_node in self.v_tilde_vertices:
            current_sum += self.get_degree_at(v_node.name)
        return current_sum

    # --- Comparison operators for configurations (on V~) ---
    
    def _is_comparable_to(self, other: "CFConfig") -> bool:
        """Checks if two configurations are defined on the same graph G and with the same q."""
        if self.q_vertex != other.q_vertex:
            return False
        # Structural graph equality check
        if set(self.graph.vertices) != set(other.graph.vertices):
            return False
        for v_node in self.graph.vertices:
            self_v_neighbors = self.graph.graph.get(v_node, {})
            other_v_neighbors = other.graph.graph.get(v_node, {})
            if self_v_neighbors != other_v_neighbors:
                return False
        return True

    def __eq__(self, other: "CFConfig") -> bool:
        if not self._is_comparable_to(other):
            return False
        
        for v_node in self.v_tilde_vertices:
            # get_degree_at will raise error if other.v_tilde_vertices is different due to different q/graph
            if self.get_degree_at(v_node.name) != other.get_degree_at(v_node.name):
                return False
        return True
    
    def __ge__(self, other: "CFConfig") -> bool:
        if not self._is_comparable_to(other):
            raise ValueError("Configurations must be on the same graph G and with the same q for comparison.")
        for v_node in self.v_tilde_vertices:
            if self.get_degree_at(v_node.name) < other.get_degree_at(v_node.name):
                return False
        return True

    def __le__(self, other: "CFConfig") -> bool:
        if not self._is_comparable_to(other):
            raise ValueError("Configurations must be on the same graph G and with the same q for comparison.")
        for v_node in self.v_tilde_vertices:
            if self.get_degree_at(v_node.name) > other.get_degree_at(v_node.name):
                return False
        return True

    def __lt__(self, other: "CFConfig") -> bool:
        # _is_comparable_to check is implicitly done by __le__ and __eq__
        return self <= other and not self == other

    def __gt__(self, other: "CFConfig") -> bool:
        # _is_comparable_to check is implicitly done by __ge__ and __eq__
        return self >= other and not self == other

    # --- Operations (modifying the underlying self.divisor) ---
    def lending_move(self, vertex_name: str) -> None:
        """Performs a lending move at vertex_name on the underlying divisor.
        This can change D(q) if q is involved, but deg(c) remains based on V~."""
        self.divisor.lending_move(vertex_name)

    def borrowing_move(self, vertex_name: str) -> None:
        """Performs a borrowing move at vertex_name on the underlying divisor.
        This can change D(q) if q is involved, but deg(c) remains based on V~."""
        self.divisor.borrowing_move(vertex_name)

    def set_fire(self, S_vertex_names: typing.Set[str]) -> None:
        """
        Performs a set firing on S_vertex_names (subset of V~) on the underlying divisor.
        Chips may be transferred to/from q if q is a neighbor of a vertex in S,
        affecting D(q), but configuration properties remain focused on V~.
        
        Args:
            S_vertex_names: A set of names of vertices in V~ to be fired.

        Raises:
            ValueError: If any name in S_vertex_names is q or not in V~.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.set_fire({"B", "C"})
            >>> config.get_degree_at("B")
            0
            >>> config.get_degree_at("C")
            0
        """
        for name in S_vertex_names:
            v = Vertex(name)
            if v == self.q_vertex:
                raise ValueError(f"Firing set S cannot include q_vertex '{self.q_vertex.name}'.")
            if v not in self.v_tilde_vertices:
                raise ValueError(f"Vertex '{name}' in firing set S not in V~ (= V - {{q}}).")
        
        self.divisor.set_fire(S_vertex_names)

    # --- Superstability related methods ---
    def get_out_degree_S(self, v_name_in_S: str, S_names: typing.Set[str]) -> int:
        """
        Calculates outdeg_S(v) for v in S, where S is a subset of V~ names.
        outdeg_S(v) is the sum of valencies of edges from v to vertices NOT in S (can include q).
        
        Args:
            v_name_in_S: Name of the vertex v in S.
            S_names: Set of names of vertices in the set S (subset of V~).

        Returns:
            The out-degree of v with respect to S.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.get_out_degree_S("B", {"B", "C"})
            1
        """
        v_in_S_obj = Vertex(v_name_in_S)
        if v_in_S_obj not in self.graph.vertices:
            raise ValueError(f"Vertex '{v_name_in_S}' not found in graph.")
        if v_in_S_obj == self.q_vertex:
             raise ValueError("out_degree_S is for v in S, and S must be a subset of V~.")
        if v_name_in_S not in S_names: # Ensures v_name_in_S is actually in the set S_names
            raise ValueError(f"Vertex '{v_name_in_S}' must be in the provided set S_names.")

        S_vertices_objs = {Vertex(name) for name in S_names}
        
        out_degree = 0
        if v_in_S_obj in self.graph.graph: 
            for neighbor_vertex, valence in self.graph.graph[v_in_S_obj].items():
                if neighbor_vertex not in S_vertices_objs: 
                    out_degree += valence
        return out_degree

    def is_legal_set_firing(self, S_names: typing.Set[str]) -> bool:
        """
        Checks if firing the non-empty set S_names (subset of V~) is legal.
        A firing c --S--> c' is legal if c'(v) >= 0 for all v in S.
        Args:
            S_names: A non-empty set of names of vertices in V~ to be fired.
        Returns:
            True if the set firing is legal, False otherwise.
        Raises:
            ValueError: If S_names contains q or vertices not in V~.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.is_legal_set_firing({"B", "C"})
            True
        """
        if not S_names: 
            return False 
        
        for name in S_names: # Validate S_names
            v = Vertex(name)
            if v == self.q_vertex:
                raise ValueError(f"Firing set S cannot include q_vertex '{self.q_vertex.name}'.")
            if v not in self.v_tilde_vertices:
                 raise ValueError(f"Vertex '{name}' in firing set S not in V~ (= V - {{q}}).")

        temp_config_copy = self.copy() # Use the copy method
        temp_config_copy.set_fire(S_names)

        for v_name_in_S in S_names:
            if temp_config_copy.get_degree_at(v_name_in_S) < 0: 
                return False
        return True

    def is_superstable(self) -> bool:
        """
        Checks if the configuration c is superstable.
        c is superstable if c >= 0 (non-negative) and has no legal nonempty set-firings within V~.
        Note: This method tries all possible nonempty subsets of V~ to check for legal set-firings.
        This is not efficient for large graphs, but is correct.
        
        Args:
            None
        Returns:
            True if the configuration is superstable, False otherwise.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.is_superstable()
            False
        """
        if not self.is_non_negative():
            return False

        v_tilde_node_names = {v.name for v in self.v_tilde_vertices}
        
        for i in range(1, len(v_tilde_node_names) + 1): 
            for s_tuple in itertools.combinations(v_tilde_node_names, i):
                S_names_subset = set(s_tuple)
                if self.is_legal_set_firing(S_names_subset):
                    return False 
        return True

    # --- Utility / Contextual methods ---
    def get_q_vertex_name(self) -> str:
        """
        Returns the name of the q vertex.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.get_q_vertex_name()
            "A"
        """
        return self.q_vertex.name
    def get_q_underlying_degree(self) -> int:
        """
        Returns D(q), the degree of q in the underlying divisor. 
        Note: This is not c(q), as configurations are not defined at q.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.get_q_underlying_degree()
            2
        """
        return self.divisor.get_degree(self.q_vertex.name)
        
    def get_v_tilde_names(self) -> typing.Set[str]:
        """
        Returns the set of names of vertices in V~ (= V - {q}).

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.get_v_tilde_names()
            {"B", "C"}
        """
        return {v.name for v in self.v_tilde_vertices}
    def get_config_degrees_as_dict(self) -> typing.Dict[str, int]:
        """
        Returns the configuration degrees c(v) for v in V~ as a dictionary {name: degree}.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config.get_config_degrees_as_dict()
            {"B": 1, "C": 0}
        """
        return {v.name: self.get_degree_at(v.name) for v in self.v_tilde_vertices}

    def __repr__(self) -> str:
        degrees_str = ", ".join(f"{name}:{deg}" for name, deg in sorted(self.get_config_degrees_as_dict().items()))
        return f"CFConfig(q='{self.q_vertex.name}', Config(V~)={{ {degrees_str} }})"
    
    def copy(self) -> "CFConfig":
        """
        Returns a deep copy of this CFConfig object, including a deep copy of the underlying divisor.

        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0)])
            >>> config = CFConfig(divisor, "A")
            >>> config_copy = config.copy()
            >>> config_copy.get_degree_at("B")
            1
        """
        return CFConfig(copy.deepcopy(self.divisor), self.q_vertex.name)
