from __future__ import annotations
from typing import Set, Tuple
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
from .CFOrientation import CFOrientation, OrientationState
from .CFConfig import CFConfig

class DharAlgorithm:
    """Implements Dhar's algorithm for finding maximal legal firing sets on a graph.

    Dhar's algorithm uses a "burning process" to identify vertices that can be
    legally fired together. It starts a fire at a distinguished vertex q and
    determines which vertices burn based on chip configuration.

    Example:
        >>> # Create a simple graph
        >>> vertices = {"A", "B", "C", "D"}
        >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1), ("A", "C", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> # Create a chip configuration (as a CFDivisor)
        >>> divisor = CFDivisor(graph, [("A", 3), ("B", 2), ("C", 1), ("D", 2)])
        >>> # Initialize the algorithm with "A" as the distinguished vertex
        >>> dhar = DharAlgorithm(graph, divisor, "A")
        >>> # Run the algorithm to find maximal legal firing set
        >>> firing_set_names, orientation = dhar.run()
        >>> # Check which vertices are in the firing set (excluding A)
        >>> sorted(list(firing_set_names))
        ['B', 'C', 'D']
        >>> # Verify orientation is a CFOrientation object
        >>> isinstance(orientation, CFOrientation)
        True
    """

    def __init__(self, graph: CFGraph, initial_divisor: CFDivisor, q_name: str, visualizer=None):
        """Initialize Dhar's Algorithm for finding a maximal legal firing set.

        Args:
            graph: A CFGraph object representing the graph.
            initial_divisor: A CFDivisor object representing the initial chip configuration on G.
                             This divisor will be modified by the algorithm (e.g., by send_debt_to_q).
            q_name: The name of the distinguished vertex (fire source).
            visualizer: An optional EWDVisualizer instance for visualization.

        Raises:
            ValueError: If q_name is not found in the graph.

        Example:
            >>> # Create a simple graph
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> # Create a chip configuration
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
            >>> # Initialize the algorithm with "A" as the distinguished vertex
            >>> dhar = DharAlgorithm(graph, divisor, "A")
            >>> dhar.q_vertex.name # q_vertex is now part of CFConfig
            'A'
            >>> # Unburnt vertices initially (all except q from CFConfig)
            >>> sorted(list(dhar.configuration.get_v_tilde_names()))
            ['B', 'C', 'D']
            >>> # Invalid distinguished vertex
            >>> try:
            ...     DharAlgorithm(graph, divisor, "E")
            ... except ValueError as e:
            ...     print(str(e))
            Vertex q='E' not found in the graph of the divisor.
        """
        self.graph = graph # Kept for outdegree_S, though CFConfig also has it.
        
        # The configuration object will manage the state w.r.t q
        # The initial_divisor passed in IS the underlying divisor for the config.
        # Operations on self.configuration (like borrowing) will modify initial_divisor.
        self.configuration = CFConfig(initial_divisor, q_name)
        self.q_vertex = self.configuration.q_vertex # Convenience alias
        self.visualizer = visualizer

    def outdegree_S(self, vertex: Vertex, S: Set[Vertex]) -> int:
        """
        Calculate the number of edges from a vertex to vertices in set S.
        S can be any subset of V (including q). This is used for calculating edges to burnt set.
        
        Args:
            vertex: A Vertex object
            S: A set of Vertex objects

        Returns:
            The number of edges from vertex to vertices in S.
        
        Example:
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> dhar = DharAlgorithm(graph, divisor, "A")
            >>> dhar.outdegree_S(Vertex("A"), {Vertex("B"), Vertex("C")})
            1
            >>> dhar.outdegree_S(Vertex("A"), {Vertex("B"), Vertex("C"), Vertex("D")})
            2
            >>> dhar.outdegree_S(Vertex("A"), {Vertex("B"), Vertex("C"), Vertex("D"), Vertex("A")})
            2
            >>> dhar.outdegree_S(Vertex("A"), {Vertex("A")})
            0
        """
        # This method remains as is, as it might need to calculate outdegree towards q,
        # which is part of the burnt set but not V~.
        # CFConfig.get_out_degree_S is for S subset of V~ and outdegree to V\\S (which can include q).
        if vertex not in self.graph.graph: # Ensure vertex is in graph before accessing neighbors
             return 0
        return sum(
            self.graph.graph[vertex].get(neighbor, 0) # Use .get for safety
            for neighbor in self.graph.graph[vertex]
            if neighbor in S
        )

    def send_debt_to_q(self) -> None:
        """Concentrate all debt at the distinguished vertex q, making all non-q vertices out of debt.
        This method modifies self.configuration (and its underlying divisor)
        so all c(v) for v in V~ are non-negative.

        Example:
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 2), ("B", -1), ("C", -2), ("D", 1)])
            >>> dhar = DharAlgorithm(graph, divisor, "A") # dhar.configuration now wraps divisor
            >>> # Check initial configuration values in V~
            >>> dhar.configuration.get_degree_at("B")
            -1
            >>> dhar.configuration.get_degree_at("C")
            -2
            >>> initial_q_degree = dhar.configuration.get_q_underlying_degree() # D(A)
            >>> # Send debt to q (A)
            >>> dhar.send_debt_to_q()
            >>> # Verify all non-q vertices have non-negative values
            >>> dhar.configuration.get_degree_at("B") >= 0
            True
            >>> dhar.configuration.get_degree_at("C") >= 0
            True
            >>> dhar.configuration.get_degree_at("D") >= 0
            True
            >>> # The distinguished vertex q takes on the debt
            >>> dhar.configuration.get_q_underlying_degree() < initial_q_degree # D(A) should decrease
            True
        """
        # Sort vertices by distance from q (approximation using BFS)
        queue = [self.q_vertex]
        visited_bfs = {self.q_vertex}
        distance_ordering = [self.q_vertex] # distance_ordering stores Vertex objects
        
        v_tilde_vertices_set = self.configuration.v_tilde_vertices # More efficient lookup

        head = 0
        while head < len(queue):
            current_v_obj = queue[head]
            head += 1
            if current_v_obj in self.graph.graph: 
                for neighbor_v_obj in self.graph.graph[current_v_obj]:
                    if neighbor_v_obj not in visited_bfs and neighbor_v_obj in v_tilde_vertices_set:
                        visited_bfs.add(neighbor_v_obj)
                        queue.append(neighbor_v_obj)
                        distance_ordering.append(neighbor_v_obj)
        
        # Process vertices in V~ in reverse order of distance
        vertices_to_process_names = [
            v.name for v in reversed(distance_ordering) if v in v_tilde_vertices_set
        ]

        for v_name in vertices_to_process_names:
            while self.configuration.get_degree_at(v_name) < 0:
                self.configuration.borrowing_move(v_name)
                if self.visualizer:
                    self.visualizer.add_step(self.configuration.divisor, CFOrientation(self.graph, []), q=self.q_vertex.name, description=f"{v_name} performs a borrowing move.", source_function="Sending debt to q...")


    def run(self) -> Tuple[Set[str], CFOrientation]:
        """Run Dhar's Algorithm to find a maximal legal firing set.

        Returns:
            A tuple containing:
            - A set of names of unburnt vertices (V~_unburnt) representing the maximal legal firing set.
            - A CFOrientation object tracking the burning directions.
        
        Example:
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 3), ("B", 2), ("C", 1), ("D", 2)])
            >>> dhar = DharAlgorithm(graph, divisor, "A")
            >>> unburnt_names, orientation = dhar.run()
            >>> sorted(list(unburnt_names))
            ['B', 'C', 'D']
            >>> isinstance(orientation, CFOrientation)
            True
            >>> # Example with debt and burning
            >>> from chipfiring import CFOrientation, OrientationState # For doctest
            >>> divisor2 = CFDivisor(graph, [("A", 3), ("B", 0), ("C", 0), ("D", 2)])
            >>> dhar2 = DharAlgorithm(graph, divisor2, "A")
            >>> unburnt_names2, orientation2 = dhar2.run()
            >>> 'B' not in unburnt_names2 # B burns
            True
            >>> # Check orientation from A to B. Since B burns due to A, A is source, B is sink.
            >>> orientation2.get_orientation("A", "B") == ('A', 'B')
            True
        """
        self.send_debt_to_q()

        burnt_vertices = {self.q_vertex} # Set of Vertex objects
        unburnt_vertex_names = self.configuration.get_v_tilde_names().copy() 
                                                                    
        orientation = CFOrientation(self.graph, []) # Initialize with no specific orientations
        
        if self.visualizer:
            self.visualizer.add_step(self.configuration.divisor, orientation, set(v for v in unburnt_vertex_names), q=self.q_vertex.name, description="Starting burn process.", source_function="Dhar (run)")

        changed = True
        while changed:
            changed = False
            
            # Iterate over a copy of unburnt_vertex_names as it might be modified
            sorted_unburnt_names = sorted(list(unburnt_vertex_names))

            for v_name in sorted_unburnt_names:
                if v_name not in unburnt_vertex_names: # Already burned in this iteration
                    continue

                v_obj = Vertex(v_name) 
                
                edges_to_burnt = self.outdegree_S(v_obj, burnt_vertices)
                
                current_degree_v = self.configuration.get_degree_at(v_name)
                if current_degree_v < edges_to_burnt:
                    unburnt_vertex_names.remove(v_name)
                    burnt_vertices.add(v_obj)
                    changed = True
                        
                    if v_obj in self.graph.graph:
                        for neighbor_obj in self.graph.graph[v_obj]:
                            if neighbor_obj in burnt_vertices and neighbor_obj != v_obj: 
                                if v_obj in self.graph.graph.get(neighbor_obj, {}): 
                                     orientation.set_orientation(neighbor_obj, v_obj, OrientationState.SOURCE_TO_SINK)
                    
                    if self.visualizer:
                        self.visualizer.add_step(self.configuration.divisor, orientation, set(v for v in unburnt_vertex_names), q=self.q_vertex.name, description=f"Vertex {v_name} burns.", source_function="Dhar (run)")

        return unburnt_vertex_names, orientation

    def get_maximal_legal_firing_set(self) -> Set[str]:
        """
        Runs Dhar's algorithm and returns only the set of unburnt vertex names (maximal legal firing set).

        Returns:
            A set of names of unburnt vertices (V~_unburnt).
        
        Example:
            >>> vertices = {"A", "B", "C", "D"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 3), ("B", 2), ("C", 1), ("D", 2)])
            >>> dhar = DharAlgorithm(graph, divisor, "A")
            >>> dhar.get_maximal_legal_firing_set()
            {'B', 'C', 'D'}
        """
        unburnt_names, _ = self.run()
        return unburnt_names

    def legal_set_fire(self, unburnt_vertex_names: Set[str]):
        """
        Performs a set firing operation on the provided set of unburnt vertex names (from V~).
        This modifies the underlying divisor of the CFConfig object.

        Args:
            unburnt_vertex_names: A set of names of vertices in V~ (typically the result of self.run()).
        
        Example:
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 1), ("B", "C", 1), ("A", "C", 2)]
            >>> graph = CFGraph(vertices, edges)
            >>> divisor = CFDivisor(graph, [("A", 0), ("B", 2), ("C", 3)]) # q=A, c(B)=2, c(C)=3
            >>> dhar = DharAlgorithm(graph, divisor, "A")
            >>> # Assume run() determined {"B", "C"} as unburnt_vertex_names
            >>> unburnt_to_fire = {"B", "C"} 
            >>> dhar.legal_set_fire(unburnt_to_fire)
            >>> # B fires to A (q). C fires to A (q).
            >>> # Initial: D(A)=0, D(B)=2, D(C)=3
            >>> # B fires to A (1 chip): D(B) -> 2-1=1, D(A) -> 0+1=1
            >>> # C fires to A (2 chips): D(C) -> 3-2=1, D(A) -> 1+2=3
            >>> # Final configuration on V~ (B,C)
            >>> dhar.configuration.get_degree_at("B") # c(B)
            1
            >>> dhar.configuration.get_degree_at("C") # c(C)
            1
            >>> # Underlying degree of q
            >>> dhar.configuration.get_q_underlying_degree() # D(A)
            3
        """
        if not unburnt_vertex_names: 
            return
            
        self.configuration.set_fire(unburnt_vertex_names)
