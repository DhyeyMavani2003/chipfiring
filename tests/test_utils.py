"""
Tests for the utility functions used in the Dollar Game.
"""

import pytest
import numpy as np
from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor
from chipfiring.dhar import (
    outdegree_to_set,
    find_legal_firing_set,
    is_q_reduced,
    q_reduce,
)


@pytest.fixture
def example_graph():
    """Create an example graph for testing."""
    G = Graph()
    v_a = Vertex("A")
    v_b = Vertex("B")
    v_c = Vertex("C")
    v_e = Vertex("E")

    G.add_vertex(v_a)
    G.add_vertex(v_b)
    G.add_vertex(v_c)
    G.add_vertex(v_e)

    G.add_edge(v_a, v_b)
    G.add_edge(v_a, v_c)
    G.add_edge(v_a, v_e)
    G.add_edge(v_a, v_e)  # Double edge
    G.add_edge(v_b, v_c)
    G.add_edge(v_c, v_e)

    return G, v_a, v_b, v_c, v_e


@pytest.fixture
def example_divisor(example_graph):
    """Create an example divisor for testing."""
    G, v_a, v_b, v_c, v_e = example_graph
    return Divisor(G, {v_a: 2, v_b: -3, v_c: 4, v_e: -1})


def test_vertex_mappings(example_graph):
    """Test vertex mapping functions."""
    G, v_a, v_b, v_c, v_e = example_graph

    # Test that vertex degrees are correctly calculated
    assert G.vertex_degree(v_a) == 4
    assert G.vertex_degree(v_b) == 2
    assert G.vertex_degree(v_c) == 3
    assert G.vertex_degree(v_e) == 3


def test_matrix_to_map(example_graph):
    """Test matrix to map conversion."""
    G, v_a, v_b, v_c, v_e = example_graph

    # Create a matrix representing firing counts
    firing_counts = np.array([1, 2, 0, 1])
    vertices = [v_a, v_b, v_c, v_e]

    # Convert to dictionary mapping
    mapping = {v: count for v, count in zip(vertices, firing_counts)}

    assert mapping[v_a] == 1
    assert mapping[v_b] == 2
    assert mapping[v_c] == 0
    assert mapping[v_e] == 1


def test_is_effective(example_divisor):
    """Test effectiveness check."""
    # The example divisor is not effective
    assert not example_divisor.is_effective()

    # Make it effective and check again
    example_divisor[Vertex("B")] = 0
    example_divisor[Vertex("E")] = 0
    assert example_divisor.is_effective()


def test_borrowing_move(example_graph, example_divisor):
    """Test borrowing move implementation."""
    G, v_a, v_b, v_c, v_e = example_graph

    # Initial values: A=2, B=-3, C=4, E=-1

    # Borrowing at B should add its degree (2) to B and subtract 1 from each neighbor (A and C)
    example_divisor[v_b] += G.vertex_degree(v_b)  # B += 2 => -1
    example_divisor[v_a] -= G.get_edge_count(v_a, v_b)  # A -= 1 => 1
    example_divisor[v_c] -= G.get_edge_count(v_c, v_b)  # C -= 1 => 3

    assert example_divisor[v_a] == 1
    assert example_divisor[v_b] == -1
    assert example_divisor[v_c] == 3
    assert example_divisor[v_e] == -1  # Unchanged


def test_outdegree_S(example_graph):
    """Test the outdegree_S function."""
    G, v_a, v_b, v_c, v_e = example_graph

    # Test outdegree of vertex A with respect to subset {A, B}
    subset = {v_a, v_b}
    outdegree = outdegree_to_set(G, v_a, subset)

    # A has edges to C and E (2 to E), so outdegree should be 3
    assert outdegree == 3


def test_greedy_debt_accumulation(example_graph, example_divisor):
    """Test the greedy debt accumulation strategy."""
    G, v_a, v_b, v_c, v_e = example_graph
    divisor = example_divisor

    # Initial values: A=2, B=-3, C=4, E=-1

    # Fire vertex C (degree 3)
    divisor[v_c] -= G.vertex_degree(v_c)  # C -= 3 => 1
    divisor[v_a] += G.get_edge_count(v_a, v_c)  # A += 1 => 3
    divisor[v_b] += G.get_edge_count(v_b, v_c)  # B += 1 => -2
    divisor[v_e] += G.get_edge_count(v_e, v_c)  # E += 1 => 0

    assert divisor[v_a] == 3
    assert divisor[v_b] == -2
    assert divisor[v_c] == 1
    assert divisor[v_e] == 0


def test_dhar_run(example_graph, example_divisor):
    """Test Dhar's algorithm functions."""
    G, v_a, v_b, v_c, v_e = example_graph
    divisor = example_divisor

    # Find a legal firing set with q = vertex A
    legal_set = find_legal_firing_set(G, divisor, v_a)

    # Vertices in the legal set should be non-negatively valued except possibly q
    for v in legal_set:
        if v != v_a:
            assert divisor[v] >= 0

    # Test q-reduction
    q_reduced = q_reduce(G, divisor, v_a)

    # A q-reduced divisor should not have any legal firing sets
    assert is_q_reduced(G, q_reduced, v_a)
