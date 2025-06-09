from __future__ import annotations
from typing import Dict
import typing
import numpy as np
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
        self.laplacian = self._construct_matrix()

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
            2
            >>> result.get_degree("v2")
            3
            >>> result.get_degree("v3")
            -2
        """
        resulting_degrees: typing.Dict[Vertex, int] = divisor.degrees.copy()
        
        # Establish a consistent, sorted order for vertices for matrix/vector operations
        ordered_vertices = sorted(list(self.graph.vertices), key=lambda v: v.name)
        num_vertices = len(ordered_vertices)

        if num_vertices == 0:
            # If there are no vertices, return the original divisor unchanged
            final_degrees_list = [
                (vertex.name, degree) for vertex, degree in resulting_degrees.items()
            ]
            return CFDivisor(self.graph, final_degrees_list)

        # 1. Convert self.laplacian (Dict[Vertex, defaultdict(int)]) to a numerical matrix L_matrix
        L_matrix: typing.List[typing.List[int]] = [
            [0] * num_vertices for _ in range(num_vertices)
        ]
        for r_idx, v_row in enumerate(ordered_vertices):
            for c_idx, v_col in enumerate(ordered_vertices):
                # self.laplacian[v_row] is a defaultdict(int), so access is safe
                L_matrix[r_idx][c_idx] = self.laplacian[v_row][v_col]

        # 2. Convert firing_script to a numerical vector s_vector
        s_vector: typing.List[int] = [0] * num_vertices
        for idx, v_obj in enumerate(ordered_vertices):
            s_vector[idx] = firing_script.get_firings(v_obj.name)

        # 3. Calculate Ls_vector using NumPy
        L_np = np.array(L_matrix)
        s_np = np.array(s_vector)
        Ls_vector = L_np.dot(s_np)  # Or L_np @ s_np

        # 4. Update resulting_degrees: D'[v_obj] = D[v_obj] - (Ls_vector)_idx
        for idx, v_obj in enumerate(ordered_vertices):
            # It's assumed v_obj from ordered_vertices (derived from self.graph.vertices)
            # will be a key in resulting_degrees (derived from divisor.degrees,
            # which should be for the same graph).
            if v_obj in resulting_degrees:
                resulting_degrees[v_obj] -= Ls_vector[idx]
            # else:
                # This case implies inconsistency between divisor's graph and CFLaplacian's graph.
                # Current CFDivisor structure ensures degrees are for vertices in its graph.
                # If graphs match, v_obj should be in resulting_degrees.
                # If not, an error might be more appropriate, or ensure keys align.
                # For now, we rely on the input divisor being correctly associated with the graph.


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

        matrix = self.laplacian
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
        laplacian = self.laplacian
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

    def solve_partial_system(self, degrees_at_v_tilde: Dict[Vertex, int], q_vertex: Vertex) -> Dict[Vertex, int]:
        """
        Solve the system L_q * x = b_q for a chip-firing context.
        
        Args:
            degrees_at_v_tilde: Dictionary of degrees at non-q vertices
            q_vertex: The q-vertex (excluded from the system)
            
        Returns:
            Dictionary of resulting degrees at non-q vertices after solving
        """
        if not self.graph.vertices:
            return {}

        # Get reduced Laplacian L_q
        reduced_L = self.get_reduced_matrix(q_vertex)
        
        # Construct vector b_q (degrees at non-q vertices)
        # Order must match the rows/cols of reduced_L
        v_tilde_ordered = [v for v in sorted(self.graph.vertices, key=lambda x: x.name) if v != q_vertex]
        
        b_vector = np.array([degrees_at_v_tilde.get(v, 0) for v in v_tilde_ordered], dtype=float)

        if reduced_L.size == 0 and b_vector.size == 0: # Graph with only q_vertex or no vertices
             return {}
        if reduced_L.shape[0] != b_vector.shape[0]:
            raise ValueError("Shape mismatch between reduced Laplacian and b_vector")

        # Solve L_q * x = b_q
        solution_vector = np.linalg.solve(reduced_L, b_vector)
        
        # Map solution back to Vertex objects
        # Create a mapping from original Vertex object to its index in the solution_vector
        new_idx_map = {v: i for i, v in enumerate(v_tilde_ordered)}

        return {
            v: int(np.rint(solution_vector[new_idx_map[v]]))
            for v in v_tilde_ordered
        }

    def apply_reduced_matrix_inv_floor_optimization(
        self,
        divisor: CFDivisor,
        reduced_matrix: typing.Dict[Vertex, typing.Dict[Vertex, int]],
        q: Vertex,
    ) -> typing.List[typing.Tuple[str, int]]:
        """
        Apply the reduced Laplacian matrix to a divisor according to the formula:
        c' = c - floor(inv(L_q) @ c)
        where L_q is the reduced Laplacian with respect to q, and c is the
        part of the divisor not on q.

        Args:
            divisor: The initial CFDivisor object representing chip counts.
            reduced_matrix: The reduced Laplacian matrix (L_q) to apply.
                            Keys are Vertex objects (all vertices except q).
            q: The vertex the matrix was reduced with respect to.

        Returns:
            A list of tuples representing the new divisor (c') for vertices not equal to q.

        Raises:
            ValueError: If the reduced_matrix is empty or not invertible.

        Example: # NOTE: This example might need updating based on the new formula.
            >>> vertices = {"A", "B", "C"}
            >>> edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
            >>> graph = CFGraph(vertices, edges)
            >>> laplacian = CFLaplacian(graph)
            >>> q_vertex = Vertex("B")
            >>> reduced_lap_dict = laplacian.get_reduced_matrix(q_vertex)
            >>> # Reduced Laplacian L_B (for A, C):
            >>> #    A  C
            >>> # A [3 -1]
            >>> # C [-1 2]
            >>> # inv(L_B) = [[2/5, 1/5], [1/5, 3/5]]
            >>> initial_degrees_dict = {"A": 3, "C": 0} # Divisor c, on vertices not B
            >>> divisor_obj = CFDivisor(graph, [("A", 3), ("B", 10), ("C", 0)]) # Full divisor D
            >>> # c = [3, 0] for A, C
            >>> # inv(L_B) @ c = [2/5*3 + 1/5*0, 1/5*3 + 3/5*0] = [6/5, 3/5] = [1.2, 0.6]
            >>> # floor(inv(L_B) @ c) = [1, 0]
            >>> # c' = c - floor(inv(L_B) @ c) = [3-1, 0-0] = [2, 0]
            >>> # result = laplacian.apply_reduced_matrix_inv_floor_optimization(divisor_obj, reduced_lap_dict, q_vertex)
            >>> # dict(result)
            {'A': 2, 'C': 0}
        """
        initial_degrees_on_reduced_vertices = divisor.degrees

        # Establish an ordered list of vertices in the reduced matrix (all graph vertices except q)
        # The keys of reduced_matrix are Vertex objects, which are the ones we care about.
        ordered_reduced_vertices = sorted(list(reduced_matrix.keys()), key=lambda v: v.name)

        if not ordered_reduced_vertices:
            # This case should ideally not happen if graph has >1 vertex and q is one of them.
            # Or if it does, perhaps an empty list is the right return.
            return []

        num_reduced_vertices = len(ordered_reduced_vertices)

        # 1. Convert reduced_matrix (L_q) to a NumPy 2D array
        Lq_np = np.zeros((num_reduced_vertices, num_reduced_vertices), dtype=float) # Use float for inverse
        for r_idx, v_row in enumerate(ordered_reduced_vertices):
            for c_idx, v_col in enumerate(ordered_reduced_vertices):
                # reduced_matrix[v_row] is a Dict[Vertex, int]
                Lq_np[r_idx, c_idx] = reduced_matrix[v_row].get(v_col, 0)

        # 2. Create vector c_np from divisor.degrees for ordered_reduced_vertices
        c_np = np.zeros(num_reduced_vertices, dtype=float)
        for idx, v_obj in enumerate(ordered_reduced_vertices):
            # initial_degrees_on_reduced_vertices is Dict[Vertex, int]
            c_np[idx] = initial_degrees_on_reduced_vertices.get(v_obj, 0)

        # 3. Calculate inv(L_q)
        try:
            inv_Lq_np = np.linalg.inv(Lq_np)
        except np.linalg.LinAlgError:
            raise ValueError("Reduced Laplacian matrix is singular and cannot be inverted.")

        # 4. Calculate inv(L_q) @ c
        invLq_c_np = inv_Lq_np @ c_np

        # 5. Floor the result: floor(inv(L_q) @ c)
        sigma_np = np.floor(invLq_c_np)

        # 6. Calculate L_q @ sigma
        Lq_sigma_np = Lq_np @ sigma_np

        # 7. Calculate c' = c - (L_q @ sigma)
        c_prime_np = c_np - Lq_sigma_np

        # 8. Convert c_prime_np back to list of tuples
        final_degrees_list: typing.List[typing.Tuple[str, int]] = []
        for idx, v_obj in enumerate(ordered_reduced_vertices):
            # Convert float result to int, consistent with chip counts
            # The values in c_prime_np should be integers after subtraction if c_np and Lq_sigma_np are.
            final_degrees_list.append((v_obj.name, int(np.rint(c_prime_np[idx]))))
            # Using int(np.rint()) for robustness with potential floating point inaccuracies.
            # CFDivisor degrees are int, so result should be int.
            # An alternative is int(c_prime_np[idx]) if precise integer arithmetic is expected.

        return final_degrees_list
