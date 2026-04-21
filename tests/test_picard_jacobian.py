"""Tests for Smith Normal Form, Picard, and Jacobian groups."""
import numpy as np
import pytest

from chipfiring import (
    CFDivisor,
    CFGraph,
    JacobianGroup,
    PicardGroup,
    elementary_divisors,
    linear_equivalence,
    smith_normal_form,
)


# ---------------------------------------------------------------------------
# Smith Normal Form
# ---------------------------------------------------------------------------


def _check_snf(matrix):
    D, U, V = smith_normal_form(matrix)
    A_np = np.array(matrix, dtype=object)
    U_np = np.array(U, dtype=object)
    V_np = np.array(V, dtype=object)
    D_np = np.array(D, dtype=object)
    # U @ A @ V == D
    assert np.array_equal(U_np @ A_np @ V_np, D_np)
    # U and V are unimodular (det = +/- 1)
    if U:
        assert round(np.linalg.det(np.array(U, dtype=float))) in (1, -1)
    if V:
        assert round(np.linalg.det(np.array(V, dtype=float))) in (1, -1)
    # Diagonal entries non-negative and obey divisibility chain
    n = min(len(D), len(D[0]) if D else 0)
    diag = [D[i][i] for i in range(n)]
    for d in diag:
        assert d >= 0
    nonzero = [d for d in diag if d != 0]
    for i in range(len(nonzero) - 1):
        assert nonzero[i + 1] % nonzero[i] == 0
    # Off-diagonal entries are zero
    for i in range(len(D)):
        for j in range(len(D[0])):
            if i != j:
                assert D[i][j] == 0
    return diag


def test_snf_identity():
    diag = _check_snf([[1, 0], [0, 1]])
    assert diag == [1, 1]


def test_snf_diagonal():
    diag = _check_snf([[2, 0], [0, 6]])
    assert diag == [2, 6]


def test_snf_general():
    diag = _check_snf([[2, 4, 4], [-6, 6, 12], [10, -4, -16]])
    assert diag == [2, 6, 12]


def test_snf_singular():
    diag = _check_snf([[2, 0], [0, 0]])
    assert diag == [2, 0]


def test_snf_single_entry():
    diag = _check_snf([[6]])
    assert diag == [6]
    diag = _check_snf([[0]])
    assert diag == [0]


def test_snf_empty_matrix():
    D, U, V = smith_normal_form([])
    assert D == [] and U == [] and V == []


def test_snf_inconsistent_rows_raises():
    with pytest.raises(ValueError):
        smith_normal_form([[1, 2], [3]])


def test_elementary_divisors():
    assert elementary_divisors([[2, 4, 4], [-6, 6, 12], [10, -4, -16]]) == [2, 6, 12]
    # Laplacian of K_3: invariants [1, 3] (with one 0); non-zero are [1, 3]
    K3 = [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]]
    assert elementary_divisors(K3) == [1, 3]


# ---------------------------------------------------------------------------
# Jacobian / Picard groups
# ---------------------------------------------------------------------------


@pytest.fixture
def k3_graph():
    return CFGraph({"a", "b", "c"}, [("a", "b", 1), ("b", "c", 1), ("a", "c", 1)])


@pytest.fixture
def path_graph():
    # Tree on 3 vertices: a - b - c
    return CFGraph({"a", "b", "c"}, [("a", "b", 1), ("b", "c", 1)])


@pytest.fixture
def k4_graph():
    vertices = {"a", "b", "c", "d"}
    edges = [
        ("a", "b", 1), ("a", "c", 1), ("a", "d", 1),
        ("b", "c", 1), ("b", "d", 1), ("c", "d", 1),
    ]
    return CFGraph(vertices, edges)


def test_jacobian_k3(k3_graph):
    jac = JacobianGroup(k3_graph)
    # K_3 has 3 spanning trees -> Jac = Z/3Z
    assert jac.order == 3
    assert jac.invariant_factors == [3]
    assert jac.structure() == "Z/3Z"
    assert len(jac) == 3


def test_jacobian_tree_is_trivial(path_graph):
    jac = JacobianGroup(path_graph)
    # A tree has exactly 1 spanning tree -> trivial Jacobian
    assert jac.order == 1
    assert jac.invariant_factors == []
    assert jac.structure() == "0"


def test_jacobian_k4(k4_graph):
    jac = JacobianGroup(k4_graph)
    # K_n has n^(n-2) spanning trees; for n=4 this is 16
    assert jac.order == 16
    # K_4 Jacobian is known to be Z/4Z (+) Z/4Z
    assert jac.invariant_factors == [4, 4]
    assert jac.structure() == "Z/4Z (+) Z/4Z"


def test_jacobian_contains_principal(k3_graph):
    jac = JacobianGroup(k3_graph)
    # Firing vertex 'a' once: a loses valence, b and c gain 1.
    # In K_3, valence(a) = 2.  Principal divisor = (-2, 1, 1).
    principal = CFDivisor(k3_graph, [("a", -2), ("b", 1), ("c", 1)])
    assert jac.contains(principal)


def test_jacobian_contains_zero_divisor(k3_graph):
    jac = JacobianGroup(k3_graph)
    zero = CFDivisor(k3_graph, [("a", 0), ("b", 0), ("c", 0)])
    assert jac.contains(zero)


def test_jacobian_does_not_contain_nonzero_total_degree(k3_graph):
    jac = JacobianGroup(k3_graph)
    d = CFDivisor(k3_graph, [("a", 1), ("b", 0), ("c", 0)])
    assert not jac.contains(d)


def test_jacobian_does_not_contain_nonprincipal(k3_graph):
    jac = JacobianGroup(k3_graph)
    # Degree 0, but not principal: e.g. (1, -1, 0). For K_3, principal divisors
    # are integer combinations of the columns of the Laplacian.  The class of
    # (1, -1, 0) has order 3 in Jac(K_3), so it is non-trivial.
    d = CFDivisor(k3_graph, [("a", 1), ("b", -1), ("c", 0)])
    assert not jac.contains(d)
    # However, 3 * (1, -1, 0) = (3, -3, 0) is principal:
    triple = CFDivisor(k3_graph, [("a", 3), ("b", -3), ("c", 0)])
    assert jac.contains(triple)


def test_jacobian_disconnected_graph_raises():
    # Two disjoint edges: order should not be defined.
    g = CFGraph({"a", "b", "c", "d"}, [("a", "b", 1), ("c", "d", 1)])
    jac = JacobianGroup(g)
    with pytest.raises(ValueError):
        _ = jac.order


def test_picard_k3(k3_graph):
    pic = PicardGroup(k3_graph)
    assert pic.free_rank == 1
    assert pic.torsion_order == 3
    assert pic.invariant_factors == [3]
    assert pic.structure() == "Z (+) Z/3Z"


def test_picard_tree(path_graph):
    pic = PicardGroup(path_graph)
    assert pic.free_rank == 1
    assert pic.torsion_order == 1
    assert pic.structure() == "Z"


def test_picard_equivalent_principal(k3_graph):
    pic = PicardGroup(k3_graph)
    d1 = CFDivisor(k3_graph, [("a", 3), ("b", 1), ("c", 0)])
    # Fire vertex a (valence 2): D' = D + (-2, 1, 1) = (1, 2, 1)
    d2 = CFDivisor(k3_graph, [("a", 1), ("b", 2), ("c", 1)])
    assert pic.equivalent(d1, d2)


def test_picard_equivalent_self(k3_graph):
    pic = PicardGroup(k3_graph)
    d = CFDivisor(k3_graph, [("a", 5), ("b", -2), ("c", 0)])
    assert pic.equivalent(d, d)


def test_picard_inequivalent_different_degree(k3_graph):
    pic = PicardGroup(k3_graph)
    d1 = CFDivisor(k3_graph, [("a", 3), ("b", 1), ("c", 0)])
    d2 = CFDivisor(k3_graph, [("a", 3), ("b", 2), ("c", 0)])
    assert not pic.equivalent(d1, d2)


def test_picard_inequivalent_same_degree(k3_graph):
    pic = PicardGroup(k3_graph)
    # Both have degree 1; differ by (1, -1, 0) which is non-principal in K_3.
    d1 = CFDivisor(k3_graph, [("a", 1), ("b", 0), ("c", 0)])
    d2 = CFDivisor(k3_graph, [("a", 0), ("b", 1), ("c", 0)])
    assert not pic.equivalent(d1, d2)


def test_picard_repr(k3_graph):
    pic = PicardGroup(k3_graph)
    s = repr(pic)
    assert "PicardGroup" in s
    assert "free_rank=1" in s
    assert "torsion_order=3" in s


def test_jacobian_repr(k3_graph):
    jac = JacobianGroup(k3_graph)
    s = repr(jac)
    assert "JacobianGroup" in s
    assert "order=3" in s


# ---------------------------------------------------------------------------
# Smith-Normal-Form-based linear equivalence
# ---------------------------------------------------------------------------


@pytest.fixture
def small_triangle():
    g = CFGraph({"v1", "v2", "v3"}, [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)])
    return g


def test_linear_equivalence_smith_matches_ewd_equivalent(small_triangle):
    d1 = CFDivisor(small_triangle, [("v1", 3), ("v2", 1), ("v3", 0)])
    # Fire v1 (valence 2): adds -2 to v1, +1 to v2, +1 to v3.
    d2 = CFDivisor(small_triangle, [("v1", 1), ("v2", 2), ("v3", 1)])
    assert linear_equivalence(d1, d2, method="smith") is True
    assert linear_equivalence(d1, d2, method="ewd") is True


def test_linear_equivalence_smith_inequivalent(small_triangle):
    d1 = CFDivisor(small_triangle, [("v1", 3), ("v2", 1), ("v3", 0)])
    d3 = CFDivisor(small_triangle, [("v1", 0), ("v2", 0), ("v3", 4)])
    assert linear_equivalence(d1, d3, method="smith") is False
    assert linear_equivalence(d1, d3, method="ewd") is False


def test_linear_equivalence_smith_different_total_degree(small_triangle):
    d1 = CFDivisor(small_triangle, [("v1", 3), ("v2", 1), ("v3", 0)])
    d4 = CFDivisor(small_triangle, [("v1", 3), ("v2", 2), ("v3", 0)])
    assert linear_equivalence(d1, d4, method="smith") is False


def test_linear_equivalence_smith_self(small_triangle):
    d1 = CFDivisor(small_triangle, [("v1", 3), ("v2", 1), ("v3", 0)])
    assert linear_equivalence(d1, d1, method="smith") is True


def test_linear_equivalence_smith_different_graphs(small_triangle):
    other = CFGraph({"x", "y"}, [("x", "y", 1)])
    d1 = CFDivisor(small_triangle, [("v1", 3), ("v2", 1), ("v3", 0)])
    d_other = CFDivisor(other, [("x", 2), ("y", 2)])
    assert linear_equivalence(d1, d_other, method="smith") is False


def test_linear_equivalence_invalid_method(small_triangle):
    d1 = CFDivisor(small_triangle, [("v1", 3), ("v2", 1), ("v3", 0)])
    d2 = CFDivisor(small_triangle, [("v1", 1), ("v2", 2), ("v3", 1)])
    with pytest.raises(ValueError):
        linear_equivalence(d1, d2, method="bogus")


def test_linear_equivalence_smith_consistency_random(k4_graph):
    """SNF-based and EWD-based linear equivalence should agree on K_4."""
    cases = [
        ([("a", 0), ("b", 0), ("c", 0), ("d", 0)],
         [("a", 0), ("b", 0), ("c", 0), ("d", 0)]),
        ([("a", 3), ("b", -1), ("c", 0), ("d", 0)],
         [("a", 0), ("b", -1), ("c", 1), ("d", 2)]),
        ([("a", 1), ("b", 0), ("c", 0), ("d", 0)],
         [("a", 0), ("b", 1), ("c", 0), ("d", 0)]),
        ([("a", 4), ("b", 0), ("c", 0), ("d", 0)],
         [("a", 1), ("b", 1), ("c", 1), ("d", 1)]),
    ]
    for left, right in cases:
        d1 = CFDivisor(k4_graph, left)
        d2 = CFDivisor(k4_graph, right)
        assert (
            linear_equivalence(d1, d2, method="smith")
            == linear_equivalence(d1, d2, method="ewd")
        )
