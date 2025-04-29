from collections import defaultdict

class Laplacian:
    def __init__(self, graph):
        """
        Initialize the Laplacian with a graph.
        
        :param graph: A dictionary representing the adjacency list of the graph.
        """
        self.graph = graph

    def construct_matrix(self):
        """
        Construct the Laplacian matrix for the graph.
        
        :return laplacian: A dictionary where each key is a vertex, and the value is a dictionary representing the row of the Laplacian matrix.
        """
        laplacian = defaultdict(lambda: defaultdict(int))
        for v in self.graph:
            degree = sum(self.graph[v].values())
            laplacian[v][v] = degree
            for w, edge_count in self.graph[v].items():
                laplacian[v][w] -= edge_count
        return laplacian

    def apply(self, divisor, firing_script):
        """
        Apply the Laplacian matrix to a firing script to calculate the resulting divisor.
        
        :param divisor: Initial divisor dictionary representing wealth at each vertex.
        :param firing_script: The firing script dictionary where keys are vertices and values are the number of times they fired.
        :return resulting_divisor: A dictionary representing the resulting divisor after applying the Laplacian.
        """
        laplacian = self.construct_matrix()
        resulting_divisor = defaultdict(int, divisor)

        for v in self.graph:
            for w in self.graph:
                resulting_divisor[v] -= laplacian[v][w] * firing_script[w]
        
        return resulting_divisor