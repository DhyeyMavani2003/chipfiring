"""
Tests for the Divisor class using pytest.
"""

import pytest
from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor


@pytest.fixture
def example_graph():
    """Create an example graph for testing."""
    G = Graph()
    v1 = Vertex("A")
    v2 = Vertex("B")
    v3 = Vertex("C")

    G.add_vertex(v1)
    G.add_vertex(v2)
    G.add_vertex(v3)

    G.add_edge(v1, v2)
    G.add_edge(v2, v3)
    G.add_edge(v1, v3)

    return G, v1, v2, v3


def test_divisor_creation(example_graph):
    """Test basic divisor creation and properties."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G)

    # Test initial values
    assert D[v1] == 0
    assert D[v2] == 0
    assert D[v3] == 0

    # Test setting values
    D[v1] = 2
    D[v2] = -1
    assert D[v1] == 2
    assert D[v2] == -1
    assert D[v3] == 0


def test_divisor_equality(example_graph):
    """Test divisor equality."""
    G, v1, v2, v3 = example_graph
    D1 = Divisor(G)
    D2 = Divisor(G)

    # Initially equal
    assert D1 == D2

    # Different values
    D1[v1] = 1
    assert D1 != D2

    # Same values
    D2[v1] = 1
    assert D1 == D2


def test_divisor_addition(example_graph):
    """Test divisor addition."""
    G, v1, v2, v3 = example_graph
    D1 = Divisor(G)
    D2 = Divisor(G)

    D1[v1] = 2
    D1[v2] = -1

    D2[v1] = 1
    D2[v3] = 1

    D_sum = D1 + D2

    assert D_sum[v1] == 3
    assert D_sum[v2] == -1
    assert D_sum[v3] == 1


def test_divisor_scalar_multiplication(example_graph):
    """Test scalar multiplication of divisors."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G)

    D[v1] = 2
    D[v2] = -1

    D_scaled = 2 * D

    assert D_scaled[v1] == 4
    assert D_scaled[v2] == -2
    assert D_scaled[v3] == 0


def test_divisor_degree(example_graph):
    """Test divisor degree calculation."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G)

    D[v1] = 2
    D[v2] = -1
    D[v3] = 0

    assert D.degree() == 1  # 2 + (-1) + 0 = 1


def test_divisor_effective(example_graph):
    """Test effective divisor detection."""
    G, v1, v2, v3 = example_graph
    D1 = Divisor(G)
    D2 = Divisor(G)

    # Effective divisor
    D1[v1] = 2
    D1[v2] = 1
    D1[v3] = 0
    assert D1.is_effective()

    # Non-effective divisor
    D2[v1] = -1
    D2[v2] = 1
    D2[v3] = 0
    assert not D2.is_effective()


def test_divisor_principal(example_graph):
    """Test principal divisor detection."""
    G, v1, v2, v3 = example_graph

    # Create a principal divisor (degree 0)
    D = Divisor(G)
    D[v1] = 1
    D[v2] = -1
    D[v3] = 0
    assert D.degree() == 0

    # Test that it's not principal (should be equivalent to 0)
    assert not D.is_principal()


def test_divisor_linear_equivalence(example_graph):
    """Test linear equivalence of divisors."""
    G, v1, v2, v3 = example_graph
    D1 = Divisor(G)
    D2 = Divisor(G)

    # Create linearly equivalent divisors
    D1[v1] = 2
    D1[v2] = 0
    D1[v3] = 0

    D2[v1] = 1
    D2[v2] = 1
    D2[v3] = 0

    # These divisors should be linearly equivalent
    assert D1.is_linearly_equivalent(D2)


def test_divisor_rank(example_graph):
    """Test divisor rank calculation."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G)

    # Create a divisor with rank 1
    D[v1] = 2
    D[v2] = 0
    D[v3] = 0

    assert D.rank() == 1


def test_divisor_serialization(example_graph):
    """Test divisor serialization and deserialization."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G)

    D[v1] = 2
    D[v2] = -1
    D[v3] = 0

    # Test serialization
    serialized = D.to_dict()
    assert serialized == {v1: 2, v2: -1, v3: 0}

    # Test deserialization
    D_new = Divisor.from_dict(G, serialized)
    assert D_new == D
