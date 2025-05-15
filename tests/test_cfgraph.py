import pytest
from chipfiring.CFGraph import CFGraph, Vertex, Edge


def test_vertex_creation_and_comparison():
    """Test Vertex class creation and comparison operations."""
    v1 = Vertex("A")
    v2 = Vertex("B")
    v3 = Vertex("A")

    # Test equality
    assert v1 == v3
    assert v1 != v2

    # Test ordering
    assert v1 < v2
    assert v1 <= v2
    assert v2 > v1
    assert v2 >= v1

    # Test string representation
    assert str(v1) == "A"

    # Test hashing
    vertex_set = {v1, v2, v3}
    assert len(vertex_set) == 2  # v1 and v3 are equal


def test_edge_creation_and_comparison():
    """Test Edge class creation and comparison operations."""
    v1 = Vertex("A")
    v2 = Vertex("B")
    v3 = Vertex("C")

    e1 = Edge(v1, v2)
    e2 = Edge(v2, v1)  # Same edge, different order
    e3 = Edge(v1, v3)

    # Test equality
    assert e1 == e2
    assert e1 != e3

    # Test string representation
    assert str(e1) == "A-B"

    # Test hashing
    edge_set = {e1, e2, e3}
    assert len(edge_set) == 2  # e1 and e2 are equal


def test_graph_creation():
    """Test basic graph creation."""
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1)]

    graph = CFGraph(vertices, edges)

    # Test vertices were added
    assert len(graph.vertices) == 3
    assert all(isinstance(v, Vertex) for v in graph.vertices)

    # Test edges were added
    assert graph.total_valence == 3  # 2 edges between A-B, 1 edge between B-C

    # Test vertex valences
    assert graph.get_valence("A") == 2
    assert graph.get_valence("B") == 3  # 2 from A-B, 1 from B-C
    assert graph.get_valence("C") == 1


def test_graph_duplicate_vertices():
    """Test that duplicate vertices are not allowed."""
    vertices = {"A", "A", "B"}  # Duplicate vertex
    edges = [("A", "B", 1)]

    # Should not raise error since set removes duplicates
    graph = CFGraph(vertices, edges)
    assert len(graph.vertices) == 2


def test_graph_add_edges():
    """Test adding edges to the graph."""
    vertices = {"A", "B", "C"}
    graph = CFGraph(vertices, [])

    # Add single edge
    graph.add_edge("A", "B", 2)
    assert graph.graph[Vertex("A")][Vertex("B")] == 2
    assert graph.graph[Vertex("B")][Vertex("A")] == 2  # Undirected

    # Add multiple edges
    graph.add_edges([("B", "C", 1), ("A", "C", 3)])
    assert graph.graph[Vertex("B")][Vertex("C")] == 1
    assert graph.graph[Vertex("A")][Vertex("C")] == 3


def test_graph_invalid_operations():
    """Test invalid graph operations raise appropriate errors."""
    vertices = {"A", "B"}
    graph = CFGraph(vertices, [])

    # Test adding edge with invalid valence
    with pytest.raises(ValueError):
        graph.add_edge("A", "B", 0)

    with pytest.raises(ValueError):
        graph.add_edge("A", "B", -1)

    # Test adding edge with non-existent vertex
    with pytest.raises(ValueError):
        graph.add_edge("A", "C", 1)

    # Test getting valence of non-existent vertex
    with pytest.raises(ValueError):
        graph.get_valence("C")


def test_graph_genus():
    """Test genus calculation."""
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]

    graph = CFGraph(vertices, edges)
    # Total edges = 4, Vertices = 3
    # Genus = |E| - |V| + 1 = 4 - 3 + 1 = 2
    assert graph.get_genus() == 2


def test_graph_merge_duplicate_edges():
    """Test that duplicate edges are merged by adding valences."""
    vertices = {"A", "B"}
    edges = [("A", "B", 2), ("A", "B", 3)]  # Duplicate edge

    # Should merge valences
    with pytest.warns(UserWarning):
        graph = CFGraph(vertices, edges)

    assert graph.graph[Vertex("A")][Vertex("B")] == 5


def test_is_loopless():
    """Test the is_loopless method."""
    vertices = {"A", "B"}
    graph = CFGraph(vertices, [])

    # Test non-loop edge
    assert graph.is_loopless("A", "B")

    # Test loop edge
    assert not graph.is_loopless("A", "A")


def test_remove_vertex():
    """Test removing a vertex from the graph."""
    vertices = {"A", "B", "C", "D"}
    edges = [("A", "B", 2), ("B", "C", 1), ("C", "D", 3), ("A", "D", 2)]

    graph = CFGraph(vertices, edges)

    # Remove vertex C
    new_graph = graph.remove_vertex("C")

    # Check that the new graph has the correct vertices
    assert len(new_graph.vertices) == 3
    assert all(v.name in {"A", "B", "D"} for v in new_graph.vertices)
    assert all(v.name != "C" for v in new_graph.vertices)

    # Check that edges are preserved correctly
    assert new_graph.graph[Vertex("A")][Vertex("B")] == 2
    assert new_graph.graph[Vertex("A")][Vertex("D")] == 2
    assert Vertex("C") not in new_graph.graph

    # Check valences
    assert new_graph.get_valence("A") == 4  # 2 from A-B, 2 from A-D
    assert new_graph.get_valence("B") == 2  # 2 from A-B
    assert new_graph.get_valence("D") == 2  # 2 from A-D

    # Check total valence
    assert new_graph.total_valence == 4

    # Test removing non-existent vertex
    with pytest.raises(ValueError):
        graph.remove_vertex("E")
