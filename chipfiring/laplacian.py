from collections import defaultdict
from typing import Dict
from .graph import Graph, Vertex

class Laplacian:
    def __init__(self, graph: Graph):
        """
        Initialize the Laplacian with a graph object.
        
        :param graph: A Graph object.
        """
        self.graph = graph
        self._laplacian_matrix: Dict[Vertex, Dict[Vertex, int]] | None = None

    def get_matrix(self) -> Dict[Vertex, Dict[Vertex, int]]:
        """Construct the Laplacian matrix using graph methods."""
        matrix = defaultdict(lambda: defaultdict(int))
        vertices = list(self.graph._adjacency.keys())
        for v in vertices:
            # TODO: Should instead by degree, which is stored in divisor
            degree = self.graph.vertex_degree(v)
            matrix[v][v] = degree
            for w, edge_count in self.graph._adjacency.get(v, {}).items():
                matrix[v][w] -= edge_count
        self._laplacian_matrix = matrix
        return self._laplacian_matrix

    def apply(self, divisor: Dict[Vertex, int], firing_script: Dict[Vertex, int]) -> Dict[Vertex, int]:
        """
        Apply the Laplacian matrix to a firing script to calculate the resulting divisor.
        Uses the formula: D_new = D_initial - L * S
        where L is the Laplacian and S is the firing script vector.

        :param divisor: Initial divisor dictionary (chips at each vertex).
        :param firing_script: The firing script dictionary (times each vertex fired).
        :return resulting_divisor: A dictionary representing the resulting divisor.
        """
        laplacian = self.get_matrix()
        resulting_divisor = defaultdict(int, divisor)
        vertices = list(self.graph._adjacency.keys())

        laplacian_effect = defaultdict(int)
        for v in vertices:
            for w in vertices:
                laplacian_effect[v] += laplacian[v][w] * firing_script.get(w, 0)
        
        for v in vertices:
            resulting_divisor[v] -= laplacian_effect[v]
        
        for v in vertices:
            if v not in resulting_divisor:
                resulting_divisor[v] = 0
        
        return dict(resulting_divisor)