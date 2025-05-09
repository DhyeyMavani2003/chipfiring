import pytest
import copy
from chipfiring.CFGraph import CFGraph
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFGreedyAlgorithm import GreedyAlgorithm
from chipfiring.CFiringScript import CFiringScript


@pytest.fixture
def simple_graph():
    """Create a simple graph for testing GreedyAlgorithm."""
    G = CFGraph({"A", "B", "C", "D"}, [])
    G.add_edge("A", "B", 1)
    G.add_edge("B", "C", 1)
    G.add_edge("C", "D", 1)
    G.add_edge("D", "A", 1)
    G.add_edge("A", "C", 1)
    return G


@pytest.fixture
def path_graph():
    """Create a path graph for testing."""
    G = CFGraph({"A", "B", "C", "D"}, [])
    G.add_edge("A", "B", 1)
    G.add_edge("B", "C", 1)
    G.add_edge("C", "D", 1)
    return G


@pytest.fixture
def weighted_graph():
    """Create a graph with weighted edges for testing."""
    G = CFGraph({"A", "B", "C", "D"}, [])
    G.add_edge("A", "B", 2)
    G.add_edge("B", "C", 3)
    G.add_edge("C", "D", 1)
    G.add_edge("D", "A", 2)
    return G


@pytest.fixture
def sequence_test_graph():
    """Graph used in the set_fire and laplacian sequence tests."""
    vertices = {"Alice", "Bob", "Charlie", "Elise"}
    edges = [
        ("Alice", "Bob", 1),
        ("Bob", "Charlie", 1),
        ("Charlie", "Elise", 1),
        ("Alice", "Elise", 2),
        ("Alice", "Charlie", 1),
    ]
    return CFGraph(vertices, edges)


@pytest.fixture
def sequence_test_initial_divisor(sequence_test_graph):
    """Initial divisor for the sequence tests."""
    # A=2, B=-3, C=4, E=-1 (Total=2)
    initial_degrees = [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)]
    return CFDivisor(sequence_test_graph, initial_degrees)


class TestGreedyAlgorithm:
    def test_init(self, simple_graph):
        """Test initialization of the GreedyAlgorithm."""
        # Create a divisor for the graph
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])

        # Initialize the algorithm
        algorithm = GreedyAlgorithm(simple_graph, divisor)

        # Check that the graph and divisor were properly stored
        assert algorithm.graph == simple_graph
        assert algorithm.divisor == divisor

        # Check that the firing script is initialized with all zeros
        assert isinstance(algorithm.firing_script, CFiringScript)
        assert all(
            algorithm.firing_script.get_firings(v.name) == 0
            for v in simple_graph.vertices
        )

    def test_is_effective_true(self, simple_graph):
        """Test is_effective method when all vertices have non-negative wealth."""
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
        algorithm = GreedyAlgorithm(simple_graph, divisor)

        # All vertices have non-negative wealth, so is_effective should return True
        assert algorithm.is_effective() is True

    def test_is_effective_false(self, simple_graph):
        """Test is_effective method when some vertex has negative wealth."""
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", -1), ("C", 0), ("D", 1)])
        algorithm = GreedyAlgorithm(simple_graph, divisor)

        # Vertex B has negative wealth, so is_effective should return False
        assert algorithm.is_effective() is False

    def test_borrowing_move(self, simple_graph):
        """Test the borrowing_move method."""
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", -1), ("C", 0), ("D", 1)])
        algorithm = GreedyAlgorithm(simple_graph, divisor)

        # Initial state
        assert algorithm.divisor.get_degree("B") == -1
        assert algorithm.firing_script.get_firings("B") == 0

        # Perform a borrowing move at vertex B
        algorithm.borrowing_move("B")

        # After borrowing, B's wealth should be increased by its valence (3 in this graph)
        # and its firing script value should be decreased by 1
        assert algorithm.divisor.get_degree("B") == 1  # -1 + 2 = 1
        assert algorithm.firing_script.get_firings("B") == -1

        # Neighbors should have lost chips equal to edge weights
        assert algorithm.divisor.get_degree("A") == 1  # 2 - 1 = 1
        assert algorithm.divisor.get_degree("C") == -1  # 0 - 1 = -1

    def test_play_winnable(self, simple_graph):
        """Test the play method when the game is winnable."""
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", -1), ("C", 0), ("D", 1)])
        algorithm = GreedyAlgorithm(simple_graph, divisor)

        # Play the game
        winnable, firing_script = algorithm.play()

        # The game should be winnable
        assert winnable is True
        assert isinstance(firing_script, CFiringScript)

        # Check that the resulting divisor is effective (all vertices have non-negative wealth)
        assert all(
            algorithm.divisor.get_degree(v.name) >= 0 for v in simple_graph.vertices
        )

    def test_play_path_graph(self, path_graph):
        """Test the play method on a path graph."""
        divisor = CFDivisor(path_graph, [("A", -1), ("B", 0), ("C", 0), ("D", 3)])
        algorithm = GreedyAlgorithm(path_graph, divisor)

        # Play the game
        winnable, firing_script = algorithm.play()

        # The game should be winnable for this path graph
        assert winnable is True
        assert isinstance(firing_script, CFiringScript)

        # Verify the final divisor is effective
        assert all(
            algorithm.divisor.get_degree(v.name) >= 0 for v in path_graph.vertices
        )

    def test_play_weighted_graph(self, weighted_graph):
        """Test the play method on a weighted graph."""
        divisor = CFDivisor(weighted_graph, [("A", -2), ("B", 0), ("C", 0), ("D", 6)])
        algorithm = GreedyAlgorithm(weighted_graph, divisor)

        # Play the game
        winnable, firing_script = algorithm.play()

        # This should be winnable
        assert winnable is True
        assert isinstance(firing_script, CFiringScript)

        # Verify final divisor is effective
        assert all(
            algorithm.divisor.get_degree(v.name) >= 0 for v in weighted_graph.vertices
        )

    def test_play_unwinnable(self, simple_graph):
        """Test the play method when the game is unwinnable due to too much debt."""
        # Create a divisor with extreme debt that can't be resolved within move limit
        divisor = CFDivisor(
            simple_graph, [("A", -100), ("B", -100), ("C", -100), ("D", -100)]
        )
        algorithm = GreedyAlgorithm(simple_graph, divisor)

        # The algorithm has a limit on the number of moves, and this should exceed it
        winnable, firing_script = algorithm.play()

        assert winnable is False
        assert firing_script is None

    def test_complete_execution(self, simple_graph):
        """Test complete execution and verify firing script correctness."""
        divisor = CFDivisor(simple_graph, [("A", 1), ("B", -2), ("C", 0), ("D", 2)])
        algorithm = GreedyAlgorithm(simple_graph, divisor)

        # Play the game
        winnable, firing_script = algorithm.play()

        assert winnable is True

        # Apply the firing script to the original divisor and verify it creates an effective divisor
        original_divisor = copy.deepcopy(divisor)

        # Create a copy of the original divisor
        test_divisor = copy.deepcopy(original_divisor)

        # Apply the firing script (firing_script contains net firings, so we need to adjust)
        for vertex, count in firing_script.script.items():
            if count < 0:  # Borrowing
                for _ in range(-count):
                    test_divisor.borrowing_move(vertex)

        # Check that the result is effective
        assert all(test_divisor.get_degree(v.name) >= 0 for v in simple_graph.vertices)

    def test_play_with_sequence_test_graph(
        self, sequence_test_graph, sequence_test_initial_divisor
    ):
        """Test the play method on the sequence test graph from the laplacian tests."""
        # Initial divisor has A=2, B=-3, C=4, E=-1 (Total=2)
        algorithm = GreedyAlgorithm(sequence_test_graph, sequence_test_initial_divisor)

        # Play the game
        winnable, firing_script = algorithm.play()

        # The game should be winnable
        assert winnable is True
        assert isinstance(firing_script, CFiringScript)

        # Check that the resulting divisor is effective
        for vertex in sequence_test_graph.vertices:
            assert algorithm.divisor.get_degree(vertex.name) >= 0

        # Verify the total degree remains the same
        assert (
            algorithm.divisor.get_total_degree()
            == sequence_test_initial_divisor.get_total_degree()
        )
