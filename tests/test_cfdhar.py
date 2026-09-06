import random

import pytest
from chipfiring.CFGraph import CFGraph, Vertex
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFDhar import DharAlgorithm
from chipfiring.CFOrientation import CFOrientation
from chipfiring.CFConfig import CFConfig


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

    def test_send_debt_to_q_revisits_vertices_made_negative_later(self):
        """A later borrowing move can put debt back on an earlier vertex."""
        graph = CFGraph(
            {"q", "a", "b"},
            [("q", "a", 1), ("a", "b", 1)],
        )
        divisor = CFDivisor(graph, [("q", 1), ("a", 0), ("b", -1)])
        initial_total = divisor.get_total_degree()

        dhar = DharAlgorithm(graph, divisor, "q")
        dhar.send_debt_to_q()

        working_divisor = dhar.configuration.divisor
        assert working_divisor.get_degree("a") >= 0
        assert working_divisor.get_degree("b") >= 0
        assert working_divisor.get_total_degree() == initial_total
        assert working_divisor.graph is graph
        # The caller's divisor is left untouched.
        assert divisor.get_degree("b") == -1
        assert divisor.get_total_degree() == initial_total

    def test_send_debt_to_q_property_on_connected_multigraphs(self):
        """Debt concentration terminates and is idempotent on varied connected inputs."""
        rng = random.Random(20260823)

        for case_number in range(150):
            vertex_count = rng.randint(1, 6)
            names = [f"v{i}" for i in range(vertex_count)]
            edge_multiplicities = {}

            # Start with a random spanning tree, then add optional parallel-edge
            # multiplicities and chords. This guarantees connected, loopless inputs.
            for i in range(1, vertex_count):
                parent = rng.randrange(i)
                edge_multiplicities[(parent, i)] = rng.randint(1, 4)
            for i in range(vertex_count):
                for j in range(i + 1, vertex_count):
                    if (i, j) not in edge_multiplicities and rng.random() < 0.35:
                        edge_multiplicities[(i, j)] = rng.randint(1, 4)

            edges = [
                (names[i], names[j], multiplicity)
                for (i, j), multiplicity in edge_multiplicities.items()
            ]
            graph = CFGraph(set(names), edges)
            q_name = rng.choice(names)
            degrees = [(name, rng.randint(-8, 8)) for name in names]
            divisor = CFDivisor(graph, degrees)
            initial_total = divisor.get_total_degree()
            initial_degrees = dict(divisor.degrees)
            dhar = DharAlgorithm(graph, divisor, q_name)

            dhar.send_debt_to_q()

            working_divisor = dhar.configuration.divisor
            assert all(
                dhar.configuration.get_degree_at(name) >= 0
                for name in dhar.configuration.get_v_tilde_names()
            ), f"failed generated case {case_number}"
            assert working_divisor.get_total_degree() == initial_total
            # The caller's divisor is never modified.
            assert divisor.degrees == initial_degrees

            once_reduced = working_divisor.degrees.copy()
            dhar.send_debt_to_q()
            assert working_divisor.degrees == once_reduced

    def test_send_debt_to_q_rejects_disconnected_graph(self):
        graph = CFGraph({"q", "a", "b"}, [("q", "a", 1)])
        divisor = CFDivisor(graph, [("q", 0), ("a", 0), ("b", -1)])
        dhar = DharAlgorithm(graph, divisor, "q")

        with pytest.raises(ValueError, match="connected graph"):
            dhar.send_debt_to_q()

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
        # After debt concentration at A the configuration is B=1, C=0, D=2
        # (D(A) = -1); only {D} can fire legally, and no superset of it can.
        divisor = CFDivisor(simple_graph, [("A", 0), ("B", -1), ("C", 1), ("D", 2)])
        dhar = DharAlgorithm(simple_graph, divisor, "A")
        unburnt_vertex_names, _ = dhar.run()

        assert unburnt_vertex_names == {"D"}

        # Legality and maximality are judged on the debt-concentrated working
        # configuration, which is a copy: the caller's divisor is unchanged.
        working = dhar.configuration
        assert isinstance(working, CFConfig)
        assert working.is_legal_set_firing(unburnt_vertex_names)
        for other in working.get_v_tilde_names() - unburnt_vertex_names:
            assert not working.is_legal_set_firing(unburnt_vertex_names | {other})
        assert divisor.get_degree("B") == -1

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
