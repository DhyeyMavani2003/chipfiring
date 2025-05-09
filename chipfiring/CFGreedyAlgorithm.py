from .CFGraph import CFGraph
from .CFDivisor import CFDivisor
from .CFiringScript import CFiringScript
from typing import Optional, Tuple
import copy


class GreedyAlgorithm:
    def __init__(self, graph: CFGraph, divisor: CFDivisor):
        """
        Initialize the greedy algorithm for the dollar game.

        Args:
            graph: A CFGraph object representing the graph.
            divisor: A CFDivisor object representing the initial chip configuration.
        """
        self.graph = graph
        self.divisor = copy.deepcopy(divisor)
        # Initialize firing script with all vertices at 0
        self.firing_script = CFiringScript(graph)

    def is_effective(self) -> bool:
        """
        Check if all vertices have non-negative wealth.

        Returns:
            True if effective (all vertices have non-negative chips), otherwise False.
        """
        return all(self.divisor.get_degree(v.name) >= 0 for v in self.graph.vertices)

    def borrowing_move(self, vertex_name: str) -> None:
        """
        Perform a borrowing move at the specified vertex.

        Args:
            vertex_name: The name of the vertex at which to perform the borrowing move.
        """
        # Decrement the borrowing vertex's firing script since it's receiving
        self.firing_script.update_firings(vertex_name, -1)

        # Update wealth based on the borrowing move
        self.divisor.borrowing_move(vertex_name)

    def play(self) -> Tuple[bool, Optional[CFiringScript]]:
        """
        Execute the greedy algorithm to determine winnability.

        Returns:
            Tuple (True, firing_script) if the game is winnable; otherwise (False, None).
            The firing script is a dictionary mapping vertex names to their net number of firings.
        """
        moves = 0
        # Enforcing a Scalable and Reasonable upper bound
        max_moves = len(self.graph.vertices) * 10

        while not self.is_effective():
            moves += 1
            if moves > max_moves:
                return False, None

            # Find a vertex with negative chips
            in_debt_vertex = None
            for vertex in self.graph.vertices:
                if self.divisor.get_degree(vertex.name) < 0:
                    in_debt_vertex = vertex.name
                    break

            if in_debt_vertex is None:
                break

            self.borrowing_move(in_debt_vertex)

        return True, self.firing_script
