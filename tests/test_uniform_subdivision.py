"""Tests for the uniform subdivision process on CFGraph and CFDivisor.

The uniform ``k``-subdivision replaces every edge of a graph with a path of
length ``k`` (inserting ``k - 1`` new vertices on each edge). For a graph with
multi-edges, each parallel copy is subdivided independently. This is the
standard combinatorial way to refine a metric graph into a finite graph.
"""
import pytest

from chipfiring.CFGraph import CFGraph, Vertex
from chipfiring.CFDivisor import CFDivisor


def _path_graph(n):
    """Helper: build a path on ``n`` vertices v0-v1-...-v_{n-1}."""
    vertices = {f"v{i}" for i in range(n)}
    edges = [(f"v{i}", f"v{i+1}", 1) for i in range(n - 1)]
    return CFGraph(vertices, edges)


def test_subdivision_vertex_name_canonical_ordering():
    # Naming should be invariant under swapping the endpoint argument order.
    assert CFGraph.subdivision_vertex_name("A", "B", 1) == "A-B_s1"
    assert CFGraph.subdivision_vertex_name("B", "A", 1) == "A-B_s1"
    assert CFGraph.subdivision_vertex_name("A", "B", 2) == "A-B_s2"


def test_subdivision_vertex_name_with_multi_edge_copies():
    # Different copies of a parallel edge get distinct internal-vertex names.
    n0 = CFGraph.subdivision_vertex_name("A", "B", 1, copy=0)
    n1 = CFGraph.subdivision_vertex_name("A", "B", 1, copy=1)
    n2 = CFGraph.subdivision_vertex_name("A", "B", 1, copy=2)
    assert n0 == "A-B_s1"
    assert n1 == "A-B#c1_s1"
    assert n2 == "A-B#c2_s1"
    assert len({n0, n1, n2}) == 3


def test_uniform_subdivision_k_equals_one_is_identity_like():
    # k=1 should preserve vertex set, edge set, and valences exactly.
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 3)]
    graph = CFGraph(vertices, edges)

    sub = graph.uniform_subdivision(1)

    assert {v.name for v in sub.vertices} == {v.name for v in graph.vertices}
    assert sub.total_valence == graph.total_valence
    assert sub.graph[Vertex("A")][Vertex("B")] == 2
    assert sub.graph[Vertex("B")][Vertex("C")] == 1
    assert sub.graph[Vertex("A")][Vertex("C")] == 3


def test_uniform_subdivision_invalid_k():
    graph = _path_graph(2)
    with pytest.raises(ValueError):
        graph.uniform_subdivision(0)
    with pytest.raises(ValueError):
        graph.uniform_subdivision(-1)
    with pytest.raises(ValueError):
        graph.uniform_subdivision(2.5)  # not an int


def test_uniform_subdivision_simple_graph_counts_and_genus():
    # Triangle: 3 vertices, 3 edges, genus = 1.
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 1), ("B", "C", 1), ("A", "C", 1)]
    graph = CFGraph(vertices, edges)

    k = 4
    sub = graph.uniform_subdivision(k)

    # |V'| = |V| + (k-1) * |E|
    assert len(sub.vertices) == 3 + (k - 1) * 3
    # |E'| = k * |E|
    assert sub.total_valence == k * 3
    # Genus is preserved by uniform subdivision.
    assert sub.get_genus() == graph.get_genus()


def test_uniform_subdivision_preserves_genus_for_multi_edge_graph():
    # Two vertices connected by 3 parallel edges => genus 2.
    vertices = {"A", "B"}
    edges = [("A", "B", 3)]
    graph = CFGraph(vertices, edges)
    assert graph.get_genus() == 2

    for k in [1, 2, 3, 5]:
        sub = graph.uniform_subdivision(k)
        # Each of the 3 parallel edges becomes a path of length k.
        assert sub.total_valence == 3 * k
        assert len(sub.vertices) == 2 + 3 * (k - 1)
        assert sub.get_genus() == graph.get_genus() == 2


def test_uniform_subdivision_internal_vertices_are_degree_two_chains():
    # In the subdivision of a simple edge, every new internal vertex has
    # valence exactly 2 (one edge to its predecessor, one to its successor).
    vertices = {"A", "B"}
    graph = CFGraph(vertices, [("A", "B", 1)])

    k = 5
    sub = graph.uniform_subdivision(k)

    for step in range(1, k):
        name = CFGraph.subdivision_vertex_name("A", "B", step)
        assert sub.get_valence(name) == 2

    # Endpoints retain valence 1 (one edge into the chain).
    assert sub.get_valence("A") == 1
    assert sub.get_valence("B") == 1


def test_uniform_subdivision_parallel_paths_are_disjoint():
    # When subdividing a multi-edge of valence 2, the two resulting paths must
    # share only the endpoints; the internal vertices must be disjoint.
    vertices = {"A", "B"}
    graph = CFGraph(vertices, [("A", "B", 2)])

    k = 3
    sub = graph.uniform_subdivision(k)

    # 2 internal vertices per copy, 2 copies => 4 new vertices, plus A and B.
    assert len(sub.vertices) == 2 + 2 * (k - 1)

    copy0_names = {
        CFGraph.subdivision_vertex_name("A", "B", j, copy=0) for j in range(1, k)
    }
    copy1_names = {
        CFGraph.subdivision_vertex_name("A", "B", j, copy=1) for j in range(1, k)
    }
    assert copy0_names.isdisjoint(copy1_names)
    all_internal = copy0_names | copy1_names
    assert all_internal.issubset({v.name for v in sub.vertices})

    # Each parallel copy's internal vertices have valence 2.
    for name in all_internal:
        assert sub.get_valence(name) == 2

    # The endpoints A and B each receive one edge per copy at each end.
    assert sub.get_valence("A") == 2
    assert sub.get_valence("B") == 2


def test_divisor_uniform_subdivision_preserves_total_and_original_degrees():
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 1), ("B", "C", 1), ("A", "C", 1)]
    graph = CFGraph(vertices, edges)
    divisor = CFDivisor(graph, [("A", 4), ("B", -2), ("C", 1)])

    sub_div = divisor.uniform_subdivision(3)

    # Original chip counts are preserved on the original vertices.
    assert sub_div.get_degree("A") == 4
    assert sub_div.get_degree("B") == -2
    assert sub_div.get_degree("C") == 1
    # New internal vertices carry zero chips.
    for u, v in [("A", "B"), ("B", "C"), ("A", "C")]:
        for j in (1, 2):
            name = CFGraph.subdivision_vertex_name(u, v, j)
            assert sub_div.get_degree(name) == 0
    # Total degree is preserved.
    assert sub_div.get_total_degree() == divisor.get_total_degree()


def test_divisor_uniform_subdivision_invalid_k():
    graph = _path_graph(2)
    divisor = CFDivisor(graph, [("v0", 1), ("v1", -1)])
    with pytest.raises(ValueError):
        divisor.uniform_subdivision(0)
