from .algorithms.greedy_algorithm import GreedyAlgorithm
from .algorithms.dhar_algorithm import DharAlgorithm
from .laplacian import Laplacian
from .graph import Graph
from .divisor import Divisor

class DollarGame:
    def __init__(self, graph: Graph, divisor: Divisor):
        """
        Initialize the dollar game.
        
        :param graph: A Graph object.
        :param divisor: A Divisor object representing the initial state.
        """
        if divisor.graph is not graph:
             raise ValueError("Divisor must be defined on the provided graph.")
        self.graph = graph
        self.current_divisor = divisor
        self.laplacian = Laplacian(graph)

    def play_game(self, strategy="greedy", q=None):
        """
        Play the game using the specified strategy.
        
        :param strategy: "greedy" or "dhar" to choose the algorithm.
        :param q: The distinguished vertex for Dhar's algorithm.
        :return: Tuple (True, result) if the game is winnable; otherwise (False, None).
        """
        if strategy == "greedy":
            greedy_algo = GreedyAlgorithm(self.graph, self.current_divisor)
            return greedy_algo.play()

        elif strategy == "dhar":
            if q is not None and not isinstance(q, Vertex):
                try:
                    q_vertex = next(v for v in self.graph._adjacency.keys() if v.name == str(q))
                except StopIteration:
                    raise ValueError(f"Distinguished vertex '{q}' not found in graph.")
            else:
                q_vertex = q
            
            dhar_algo = DharAlgorithm(self.graph, self.current_divisor, q_vertex)
            legal_firing_set = dhar_algo.run()
            if legal_firing_set:
                return True, legal_firing_set
            else:
                return False, None

    def apply_laplacian(self, firing_script):
        """
        Apply the Laplacian matrix to the firing script to get the resulting divisor.
        
        :param firing_script: The firing script dictionary.
        :return: The resulting divisor after applying the Laplacian.
        """
        return self.laplacian.apply(self.current_divisor.values, firing_script)