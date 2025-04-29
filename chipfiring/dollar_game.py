from algorithms.greedy_algorithm import GreedyAlgorithm
from algorithms.dhar_algorithm import DharAlgorithm
from utils.laplacian import Laplacian

class DollarGame:
    def __init__(self, graph, divisor):
        """
        Initialize the dollar game with a choice of algorithms.
        
        :param graph: A dictionary representing the adjacency list of the graph.
        :param divisor: A dictionary representing the wealth at each vertex.
        """
        self.graph = graph
        self.divisor = divisor
        self.laplacian = Laplacian(graph)

    def play_game(self, strategy="greedy", q=None):
        """
        Play the game using the specified strategy.
        
        :param strategy: "greedy" or "dhar" to choose the algorithm.
        :param q: The distinguished vertex for Dhar's algorithm.
        :return: Tuple (True, result) if the game is winnable; otherwise (False, None).
        """
        if strategy == "greedy":
            greedy_algo = GreedyAlgorithm(self.graph, self.divisor)
            return greedy_algo.play()

        elif strategy == "dhar":
            dhar_algo = DharAlgorithm(self.graph, self.divisor, q)
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
        return self.laplacian.apply(self.divisor, firing_script)