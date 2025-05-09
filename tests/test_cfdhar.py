import pytest
from chipfiring.CFGraph import CFGraph, Vertex
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFDhar import DharAlgorithm
import copy


@pytest.fixture
def simple_graph():
    """Create a simple graph for testing DharAlgorithm."""
    G = CFGraph({"A", "B", "C", "D"}, [])
    G.add_edge("A", "B", 1)
    G.add_edge("B", "C", 1)
    G.add_edge("C", "D", 1)
    G.add_edge("D", "A", 1)
    G.add_edge("A", "C", 1)
    return G


@pytest.fixture
def cycle_graph():
    """Create a cycle graph for testing."""
    G = CFGraph({"A", "B", "C", "D"}, [])
    G.add_edge("A", "B", 1)
    G.add_edge("B", "C", 1)
    G.add_edge("C", "D", 1)
    G.add_edge("D", "A", 1)
    return G


@pytest.fixture
def weighted_graph():
    """Create a graph with weighted edges for testing."""
    G = CFGraph({"A", "B", "C", "D"}, [])
    G.add_edge("A", "B", 2)
    G.add_edge("B", "C", 3)
    G.add_edge("C", "D", 1)
    G.add_edge("D", "A", 2)
    G.add_edge("A", "C", 1)
    return G


@pytest.fixture
def sequence_test_graph():
    """Graph used for debt concentration test."""
    vertices = {"Alice", "Bob", "Charlie", "Elise"}
    edges = [
        ("Alice", "Bob", 1),
        ("Bob", "Charlie", 1),
        ("Charlie", "Elise", 1),
        ("Alice", "Elise", 2),
        ("Alice", "Charlie", 1),
    ]
    return CFGraph(vertices, edges)


class TestDharAlgorithm:
    def test_init_valid(self, simple_graph):
        """Test initialization with valid parameters."""
        config = CFDivisor(simple_graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
        dhar = DharAlgorithm(simple_graph, config, "A")
        assert dhar.q == Vertex("A")
        assert dhar.graph == simple_graph
        assert set(dhar.unburnt_vertices) == {Vertex("B"), Vertex("C"), Vertex("D")}

    def test_init_invalid_q(self, simple_graph):
        """Test initialization with invalid distinguished vertex."""
        config = CFDivisor(simple_graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
        with pytest.raises(
            ValueError, match="Distinguished vertex E not found in graph"
        ):
            DharAlgorithm(simple_graph, config, "E")

    def test_outdegree_S(self, simple_graph):
        """Test outdegree_S method."""
        config = CFDivisor(simple_graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
        dhar = DharAlgorithm(simple_graph, config, "A")

        # Test outdegree to a set of vertices
        S = {Vertex("B"), Vertex("C")}
        assert dhar.outdegree_S(Vertex("A"), S) == 2  # A has edges to both B and C
        assert dhar.outdegree_S(Vertex("D"), S) == 1  # D has one edge to C
        assert dhar.outdegree_S(Vertex("B"), {Vertex("C")}) == 1  # B has one edge to C

    def test_send_debt_to_q(self, simple_graph):
        """Test send_debt_to_q method."""
        # Create a configuration with debt
        config = CFDivisor(simple_graph, [("A", 2), ("B", -1), ("C", -2), ("D", 1)])
        dhar = DharAlgorithm(simple_graph, config, "A")

        # Run the method to send debt to q
        dhar.send_debt_to_q()

        # All non-q vertices should now have non-negative values
        for v in dhar.configuration.degrees.keys():
            assert dhar.configuration.get_degree(v.name) >= 0

    def test_run_simple(self, simple_graph):
        """Test run method on a simple graph."""
        # Configuration with no debt
        config = CFDivisor(simple_graph, [("A", 3), ("B", 2), ("C", 1), ("D", 2)])
        dhar = DharAlgorithm(simple_graph, config, "A")

        unburnt_vertices = dhar.run()

        # Verify the result is a set of vertices
        assert isinstance(unburnt_vertices, set)

        # In this case, some vertices should remain unburnt
        # Convert to vertex names for easier checking
        unburnt_names = {v.name for v in unburnt_vertices}
        expected_vertices = {"B", "C", "D"}
        assert unburnt_names.issubset(expected_vertices)

    def test_run_with_debt(self, simple_graph):
        """Test run method with debt in the configuration."""
        # Configuration with debt
        config = CFDivisor(simple_graph, [("A", 3), ("B", -1), ("C", 1), ("D", 2)])
        dhar = DharAlgorithm(simple_graph, config, "A")

        unburnt_vertices = dhar.run()

        # Verify debt has been removed
        assert all(
            dhar.configuration.get_degree(v.name) >= 0
            for v in dhar.configuration.degrees.keys()
        )

        # Check if the result is valid
        assert isinstance(unburnt_vertices, set)

    def test_run_cycle(self, cycle_graph):
        """Test the Dhar algorithm on a cycle graph."""
        # In a cycle graph with these specific values, we expect certain burning behavior
        config = CFDivisor(cycle_graph, [("A", 2), ("B", 0), ("C", 1), ("D", 0)])
        dhar = DharAlgorithm(cycle_graph, config, "A")

        unburnt_vertices = dhar.run()

        # In this configuration, B should burn (0 chips, 1 edge to burnt A)
        # Then C might burn depending on the burning propagation
        # Verify the result is a set of vertices
        assert isinstance(unburnt_vertices, set)

    def test_run_weighted(self, weighted_graph):
        """Test the Dhar algorithm on a weighted graph."""
        # Test with weighted edges
        config = CFDivisor(weighted_graph, [("A", 4), ("B", 3), ("C", 2), ("D", 3)])
        dhar = DharAlgorithm(weighted_graph, config, "A")

        unburnt_vertices = dhar.run()

        # Verify the result is a set of vertices
        assert isinstance(unburnt_vertices, set)

        # Convert unburnt vertices to a firing script for comparison
        firing_script = {v.name: 1 for v in unburnt_vertices}
        assert len(firing_script) <= 3  # A is excluded as distinguished vertex

    def test_maximal_firing_set(self, simple_graph):
        """Test that the algorithm produces a maximal legal firing set."""
        # Create a configuration where some vertices should remain unburnt
        config = CFDivisor(simple_graph, [("A", 2), ("B", 2), ("C", 2), ("D", 2)])
        dhar = DharAlgorithm(simple_graph, config, "A")

        unburnt_vertices = dhar.run()

        # Create a firing script from unburnt vertices
        firing_script = {v.name: 1 for v in unburnt_vertices}

        # Verify that firing all vertices in the script doesn't create debt
        # (This is the definition of a legal firing set)
        test_config = copy.deepcopy(config)
        for vertex, count in firing_script.items():
            # Simulate firing vertex 'count' times
            for _ in range(count):
                test_config.firing_move(vertex)

        # Check no vertex is in debt after firing
        for v in simple_graph.vertices:
            if v.name != "A":  # Exclude q
                assert test_config.get_degree(v.name) >= 0

    def test_debt_concentration_with_bob_as_q(self, sequence_test_graph):
        """Test the debt concentration with Bob as distinguished vertex."""
        # Config with debt at multiple vertices: Alice=2, Bob=-3, Charlie=4, Elise=-1
        divisor = CFDivisor(
            sequence_test_graph,
            [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)],
        )

        # Initialize with Bob as the distinguished vertex
        dhar = DharAlgorithm(sequence_test_graph, divisor, "Bob")

        # Run the algorithm
        unburnt_vertices = dhar.run()

        # Check that debt has been properly concentrated at q (Bob)
        for v in dhar.configuration.degrees.keys():
            if v.name != "Bob":
                assert dhar.configuration.get_degree(v.name) >= 0

        # Verify the result is a set of vertices
        assert isinstance(unburnt_vertices, set)

        assert unburnt_vertices == {Vertex("Charlie"), Vertex("Elise")}

    def test_debt_concentration_with_bob_as_q_alt(self, sequence_test_graph):
        """Test the debt concentration with Bob as distinguished vertex."""
        # Config with debt at multiple vertices: Alice=2, Bob=-3, Charlie=4, Elise=-1
        divisor = CFDivisor(
            sequence_test_graph,
            [("Alice", 3), ("Bob", -2), ("Charlie", 1), ("Elise", 0)],
        )

        # Initialize with Bob as the distinguished vertex
        dhar = DharAlgorithm(sequence_test_graph, divisor, "Bob")

        # Run the algorithm
        unburnt_vertices = dhar.run()

        # Check that debt has been properly concentrated at q (Bob)
        for v in dhar.configuration.degrees.keys():
            if v.name != "Bob":
                assert dhar.configuration.get_degree(v.name) >= 0

        # Verify the result is a set of vertices
        assert isinstance(unburnt_vertices, set)

        assert unburnt_vertices == {Vertex("Alice"), Vertex("Charlie"), Vertex("Elise")}
