"""
Tests for the Graph class using pytest.
"""

import pytest
from chipfiring.graph import Graph, Vertex, Edge


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


def test_vertex_creation():
    """Test vertex creation and equality."""
    v1 = Vertex("A")
    v2 = Vertex("A")
    v3 = Vertex("B")

    assert v1 == v2
    assert v1 != v3
    assert hash(v1) == hash(v2)
    assert hash(v1) != hash(v3)


def test_edge_creation():
    """Test edge creation and equality."""
    v1 = Vertex("A")
    v2 = Vertex("B")
    e1 = Edge(v1, v2)
    e2 = Edge(v2, v1)
    e3 = Edge(v1, Vertex("C"))

    assert e1 == e2  # Undirected edges
    assert e1 != e3
    assert hash(e1) == hash(e2)
    assert hash(e1) != hash(e3)


def test_graph_creation(example_graph):
    """Test basic graph creation and properties."""
    G, v1, v2, v3 = example_graph

    assert len(G.vertices) == 3
    assert v1 in G.vertices
    assert v2 in G.vertices
    assert v3 in G.vertices

    assert G.get_edge_count(v1, v2) == 1
    assert G.get_edge_count(v2, v1) == 1  # Undirected
    assert G.get_edge_count(v1, v3) == 1
    assert G.get_edge_count(v2, v3) == 1


def test_multigraph_support():
    """Test support for multiple edges between vertices."""
    G = Graph()
    v1 = Vertex("A")
    v2 = Vertex("B")

    G.add_vertex(v1)
    G.add_vertex(v2)

    G.add_edge(v1, v2)
    G.add_edge(v1, v2)

    assert G.get_edge_count(v1, v2) == 2
    assert G.get_edge_count(v2, v1) == 2  # Undirected


def test_loop_edges():
    """Test that loop edges are not allowed."""
    G = Graph()
    v = Vertex("A")
    G.add_vertex(v)

    with pytest.raises(ValueError):
        G.add_edge(v, v)


def test_vertex_degrees(example_graph):
    """Test vertex degree calculations."""
    G, v1, v2, v3 = example_graph

    assert G.vertex_degree(v1) == 2
    assert G.vertex_degree(v2) == 2
    assert G.vertex_degree(v3) == 2


def test_laplacian_matrix(example_graph):
    """Test Laplacian matrix construction."""
    G, v1, v2, v3 = example_graph
    L = G.get_laplacian_matrix()

    # Check matrix dimensions
    assert L.shape == (3, 3)

    # Check diagonal entries (degrees)
    assert L[0, 0] == 2  # degree of v1
    assert L[1, 1] == 2  # degree of v2
    assert L[2, 2] == 2  # degree of v3

    # Check off-diagonal entries
    assert L[0, 1] == -1  # edge v1-v2
    assert L[1, 0] == -1  # edge v2-v1
    assert L[0, 2] == -1  # edge v1-v3
    assert L[2, 0] == -1  # edge v3-v1
    assert L[1, 2] == -1  # edge v2-v3
    assert L[2, 1] == -1  # edge v3-v2


def test_reduced_laplacian(example_graph):
    """Test reduced Laplacian matrix construction."""
    G, v1, v2, v3 = example_graph
    L_reduced = G.get_reduced_laplacian(v1)

    # Check matrix dimensions (should be 2x2 after removing v1)
    assert L_reduced.shape == (2, 2)

    # Check diagonal entries (degrees)
    assert L_reduced[0, 0] == 2  # degree of v2
    assert L_reduced[1, 1] == 2  # degree of v3

    # Check off-diagonal entries
    assert L_reduced[0, 1] == -1  # edge v2-v3
    assert L_reduced[1, 0] == -1  # edge v3-v2


def test_connected_graph():
    """Test connected graph detection."""
    G = Graph()
    v1 = Vertex("A")
    v2 = Vertex("B")
    v3 = Vertex("C")

    G.add_vertex(v1)
    G.add_vertex(v2)
    G.add_vertex(v3)

    # Initially disconnected
    assert not G.is_connected()

    # Add edges to make it connected
    G.add_edge(v1, v2)
    G.add_edge(v2, v3)
    assert G.is_connected()

    # Remove an edge to make it disconnected
    G = Graph()  # Create new graph
    G.add_vertex(v1)
    G.add_vertex(v2)
    G.add_vertex(v3)
    G.add_edge(v1, v2)
