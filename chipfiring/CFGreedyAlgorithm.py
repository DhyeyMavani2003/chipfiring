from __future__ import annotations
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

        Example:
            >>> G = CFGraph({"A", "B", "C", "D"}, [])
            >>> G.add_edge("A", "B", 1)
            >>> G.add_edge("B", "C", 1)
            >>> G.add_edge("C", "D", 1)
            >>> G.add_edge("D", "A", 1)
            >>> G.add_edge("A", "C", 1)
            >>> divisor = CFDivisor(G, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
            >>> algorithm = GreedyAlgorithm(G, divisor)
            >>> algorithm.graph == G
            True
            >>> algorithm.divisor == divisor
            True
            >>> # The firing script is initialized with all zeros
            >>> all(algorithm.firing_script.get_firings(v) == 0 for v in "ABCD")
            True
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

        Example:
            >>> G = CFGraph({"A", "B", "C", "D"}, [])
            >>> G.add_edge("A", "B", 1)
            >>> G.add_edge("B", "C", 1)
            >>> G.add_edge("C", "D", 1)
            >>> G.add_edge("D", "A", 1)
            >>> G.add_edge("A", "C", 1)
            >>> # With all non-negative chips
            >>> divisor = CFDivisor(G, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
            >>> algorithm = GreedyAlgorithm(G, divisor)
            >>> algorithm.is_effective()
            True
            >>> # With one vertex having negative chips
            >>> divisor2 = CFDivisor(G, [("A", 2), ("B", -1), ("C", 0), ("D", 1)])
            >>> algorithm2 = GreedyAlgorithm(G, divisor2)
            >>> algorithm2.is_effective()
            False
        """
        return all(self.divisor.get_degree(v.name) >= 0 for v in self.graph.vertices)

    def borrowing_move(self, vertex_name: str) -> None:
        """
        Perform a borrowing move at the specified vertex.

        Args:
            vertex_name: The name of the vertex at which to perform the borrowing move.

        Example:
            >>> G = CFGraph({"A", "B", "C", "D"}, [])
            >>> G.add_edge("A", "B", 1)
            >>> G.add_edge("B", "C", 1)
            >>> G.add_edge("C", "D", 1)
            >>> G.add_edge("D", "A", 1)
            >>> G.add_edge("A", "C", 1)
            >>> divisor = CFDivisor(G, [("A", 2), ("B", -1), ("C", 0), ("D", 1)])
            >>> algorithm = GreedyAlgorithm(G, divisor)
            >>> # Initial state
            >>> algorithm.divisor.get_degree("B")
            -1
            >>> algorithm.firing_script.get_firings("B")
            0
            >>> # Perform a borrowing move at vertex B
            >>> algorithm.borrowing_move("B")
            >>> # After borrowing, B's wealth increases by its valence (2 in this graph)
            >>> algorithm.divisor.get_degree("B")  # -1 + 2 = 1
            1
            >>> # Firing script decrements for borrowing vertex
            >>> algorithm.firing_script.get_firings("B")
            -1
            >>> # Neighbors lose chips equal to edge weights
            >>> algorithm.divisor.get_degree("A")  # 2 - 1 = 1
            1
            >>> algorithm.divisor.get_degree("C")  # 0 - 1 = -1
            -1
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

        Example:
            >>> G = CFGraph({"A", "B", "C", "D"}, [])
            >>> G.add_edge("A", "B", 1)
            >>> G.add_edge("B", "C", 1)
            >>> G.add_edge("C", "D", 1)
            >>> G.add_edge("D", "A", 1)
            >>> G.add_edge("A", "C", 1)
            >>> # Create a divisor with some debt
            >>> divisor = CFDivisor(G, [("A", 2), ("B", -1), ("C", 0), ("D", 1)])
            >>> algorithm = GreedyAlgorithm(G, divisor)
            >>> # Play the game
            >>> winnable, firing_script = algorithm.play()
            >>> winnable  # The game should be winnable
            True
            >>> isinstance(firing_script, CFiringScript)
            True
            >>> # Check that the resulting divisor is effective
            >>> all(algorithm.divisor.get_degree(v) >= 0 for v in "ABCD")
            True
            >>>
            >>> # Example with an unwinnable configuration (too much debt)
            >>> divisor2 = CFDivisor(G, [("A", -100), ("B", -100), ("C", -100), ("D", -100)])
            >>> algorithm2 = GreedyAlgorithm(G, divisor2)
            >>> winnable2, firing_script2 = algorithm2.play()
            >>> winnable2  # Should exceed move limit and be unwinnable
            False
            >>> firing_script2 is None
            True
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
