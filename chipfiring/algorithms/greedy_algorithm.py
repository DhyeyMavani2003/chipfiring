class GreedyAlgorithm:
    def __init__(self, graph, divisor):
        """
        Initialize the greedy algorithm for the dollar game.
        
        :param graph: A dictionary representing the adjacency list of the graph.
        :param divisor: A dictionary representing the wealth at each vertex.
        """
        self.graph = graph
        self.divisor = divisor.copy()  # Make a copy to avoid modifying original
        self.marked_vertices = set()
        self.firing_script = {v: 0 for v in graph} # Initialize firing script with all vertices

    def is_effective(self):
        """
        Check if all vertices have non-negative wealth.
        
        :return: True if effective, otherwise False.
        """
        return all(wealth >= 0 for wealth in self.divisor.values())

    def borrowing_move(self, vertex):
        """
        Perform a borrowing move at the specified vertex.
        
        :param vertex: The vertex at which to perform the borrowing move.
        """
        # Decrement the borrowing vertex's firing script since it's receiving
        self.firing_script[vertex] -= 1
        
        # Update wealth based on the borrowing move
        for neighbor, edge_count in self.graph[vertex].items():
            total_borrowed = edge_count
            self.divisor[neighbor] -= total_borrowed
            self.divisor[vertex] += total_borrowed

    def play(self):
        """
        Execute the greedy algorithm to determine winnability.
        
        :return: Tuple (True, firing_script) if the game is winnable; otherwise (False, None).
        """
        moves = 0
        # Enforcing a Scalable and Reasonable upper bound
        max_moves = len(self.graph) * 10
        
        while not self.is_effective():
            moves += 1
            if moves > max_moves:
                return False, None
                
            in_debt_vertex = next((v for v in self.divisor if self.divisor[v] < 0), None)
            if in_debt_vertex is None:
                break
                
            self.borrowing_move(in_debt_vertex)
            
        return True, dict(self.firing_script)