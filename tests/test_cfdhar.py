import pytest
from chipfiring.CFGraph import CFGraph, Vertex
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFDhar import DharAlgorithm
from chipfiring.CFOrientation import CFOrientation
from chipfiring.CFConfig import CFConfig
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
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
        dhar = DharAlgorithm(simple_graph, divisor, "A")
        assert dhar.q_vertex == Vertex("A")
        assert dhar.graph == simple_graph
        assert dhar.configuration.get_v_tilde_names() == {"B", "C", "D"}

    def test_init_invalid_q(self, simple_graph):
        """Test initialization with invalid distinguished vertex."""
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
        with pytest.raises(
            ValueError, match="Vertex q='E' not found in the graph of the divisor."
        ):
            DharAlgorithm(simple_graph, divisor, "E")

    def test_outdegree_S(self, simple_graph):
        """Test outdegree_S method."""
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", 1), ("C", 0), ("D", 1)])
        dhar = DharAlgorithm(simple_graph, divisor, "A")

        S = {Vertex("B"), Vertex("C")}
        assert dhar.outdegree_S(Vertex("A"), S) == 2
        assert dhar.outdegree_S(Vertex("D"), S) == 1
        assert dhar.outdegree_S(Vertex("B"), {Vertex("C")}) == 1

    def test_send_debt_to_q(self, simple_graph):
        """Test send_debt_to_q method."""
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", -1), ("C", -2), ("D", 1)])
        dhar = DharAlgorithm(simple_graph, divisor, "A")
        dhar.send_debt_to_q()
        for v_name in dhar.configuration.get_v_tilde_names():
            assert dhar.configuration.get_degree_at(v_name) >= 0

    def test_run_simple(self, simple_graph):
        """Test run method on a simple graph."""
        divisor = CFDivisor(simple_graph, [("A", 3), ("B", 2), ("C", 1), ("D", 2)])
        dhar = DharAlgorithm(simple_graph, divisor, "A")
        unburnt_vertex_names, orientation = dhar.run()

        assert isinstance(unburnt_vertex_names, set)
        assert isinstance(orientation, CFOrientation)
        expected_unburnt_names = {"B", "C", "D"}
        assert unburnt_vertex_names == expected_unburnt_names

    def test_run_with_debt(self, simple_graph):
        """Test run method with debt in the configuration."""
        divisor = CFDivisor(simple_graph, [("A", 3), ("B", -1), ("C", 1), ("D", 2)])
        dhar = DharAlgorithm(simple_graph, divisor, "A")
        unburnt_vertex_names, orientation = dhar.run()

        for v_name in dhar.configuration.get_v_tilde_names():
            assert dhar.configuration.get_degree_at(v_name) >= 0
        assert isinstance(unburnt_vertex_names, set)
        assert isinstance(orientation, CFOrientation)

    def test_run_cycle(self, cycle_graph):
        """Test the Dhar algorithm on a cycle graph."""
        divisor = CFDivisor(cycle_graph, [("A", 2), ("B", 0), ("C", 1), ("D", 0)])
        dhar = DharAlgorithm(cycle_graph, divisor, "A")
        unburnt_vertex_names, orientation = dhar.run()

        assert isinstance(unburnt_vertex_names, set)
        assert isinstance(orientation, CFOrientation)
        assert unburnt_vertex_names == set()

    def test_run_weighted(self, weighted_graph):
        """Test the Dhar algorithm on a weighted graph."""
        divisor = CFDivisor(weighted_graph, [("A", 4), ("B", 3), ("C", 2), ("D", 3)])
        dhar = DharAlgorithm(weighted_graph, divisor, "A")
        unburnt_vertex_names, orientation = dhar.run()

        assert isinstance(unburnt_vertex_names, set)
        assert isinstance(orientation, CFOrientation)
        assert all(isinstance(name, str) for name in unburnt_vertex_names)
        assert len(unburnt_vertex_names) <= 3

    def test_maximal_firing_set(self, simple_graph):
        """Test that the algorithm produces a maximal legal firing set."""
        divisor = CFDivisor(simple_graph, [("A", 2), ("B", 2), ("C", 2), ("D", 2)])
        dhar = DharAlgorithm(simple_graph, divisor, "A")
        unburnt_vertex_names, _ = dhar.run()

        test_config_obj = CFConfig(copy.deepcopy(divisor), "A")
        if unburnt_vertex_names:
            test_config_obj.set_fire(unburnt_vertex_names)

        for v_name in test_config_obj.get_v_tilde_names():
            assert test_config_obj.get_degree_at(v_name) >= 0

    def test_debt_concentration_with_bob_as_q(self, sequence_test_graph):
        """Test the debt concentration with Bob as distinguished vertex."""
        divisor = CFDivisor(
            sequence_test_graph,
            [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)],
        )
        dhar = DharAlgorithm(sequence_test_graph, divisor, "Bob")
        unburnt_vertex_names, orientation = dhar.run()

        for v_name in dhar.configuration.get_v_tilde_names():
            assert dhar.configuration.get_degree_at(v_name) >= 0

        assert isinstance(unburnt_vertex_names, set)
        assert isinstance(orientation, CFOrientation)
        assert unburnt_vertex_names == {"Charlie", "Elise"}

    def test_debt_concentration_with_bob_as_q_alt(self, sequence_test_graph):
        """Test the debt concentration with Bob as distinguished vertex, alternate initial."""
        divisor = CFDivisor(
            sequence_test_graph,
            [("Alice", 3), ("Bob", -2), ("Charlie", 1), ("Elise", 0)],
        )
        dhar = DharAlgorithm(sequence_test_graph, divisor, "Bob")
        unburnt_vertex_names, orientation = dhar.run()

        for v_name in dhar.configuration.get_v_tilde_names():
            assert dhar.configuration.get_degree_at(v_name) >= 0

        assert isinstance(unburnt_vertex_names, set)
        assert isinstance(orientation, CFOrientation)
        assert unburnt_vertex_names == {"Alice", "Charlie", "Elise"}
