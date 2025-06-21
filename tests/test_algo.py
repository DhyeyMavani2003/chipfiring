import pytest
from chipfiring.CFGraph import CFGraph
from chipfiring.CFDivisor import CFDivisor
from chipfiring.algo import (
    EWD,
    linear_equivalence,
    is_winnable,
    q_reduction,
    is_q_reduced,
)
from chipfiring.CFOrientation import CFOrientation


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


def test_ewd_example(sequence_test_graph, sequence_test_initial_divisor):
    """
    Test the EWD function with the example provided in algo.py.
    """
    expected_result = True
    expected_q_reduced_divisor = CFDivisor(
        sequence_test_graph, [("Alice", 2), ("Bob", 0), ("Charlie", 0), ("Elise", 0)]
    )
    is_win, reduced_div, orientation, _ = EWD(
        sequence_test_graph, sequence_test_initial_divisor
    )
    assert is_win == expected_result
    assert reduced_div == expected_q_reduced_divisor
    assert isinstance(orientation, CFOrientation)


def test_ewd_example_optimized(sequence_test_graph, sequence_test_initial_divisor):
    """Test the EWD function with the example provided in algo.py, optimized."""
    expected_result = True
    expected_q_reduced_divisor = CFDivisor(
        sequence_test_graph, [("Alice", 2), ("Bob", 0), ("Charlie", 0), ("Elise", 0)]
    )
    is_win, reduced_div, orientation, _ = EWD(
        sequence_test_graph, sequence_test_initial_divisor, optimized=True
    )
    is_win_non_optimized, reduced_div_non_optimized, orientation_non_optimized, _ = EWD(
        sequence_test_graph, sequence_test_initial_divisor, optimized=False
    )
    assert is_win == expected_result
    assert reduced_div == expected_q_reduced_divisor
    assert isinstance(orientation, CFOrientation)
    assert is_win_non_optimized == expected_result
    assert reduced_div_non_optimized == expected_q_reduced_divisor
    assert isinstance(orientation_non_optimized, CFOrientation)


def test_ewd_optimized_example(sequence_test_graph):
    """Test the EWD function with the example provided in algo.py."""
    expected_result1, expected_result2 = False, True
    extremal_divisor1 = CFDivisor(
        sequence_test_graph, [("Alice", -2), ("Bob", 0), ("Charlie", 0), ("Elise", 0)]
    )
    extremal_divisor2 = CFDivisor(
        sequence_test_graph, [("Alice", 4), ("Bob", -3), ("Charlie", 4), ("Elise", -1)]
    )
    is_win1, reduced_div1, orientation1, _ = EWD(
        sequence_test_graph, extremal_divisor1, optimized=True
    )
    is_win2, reduced_div2, orientation2, _ = EWD(
        sequence_test_graph, extremal_divisor2, optimized=True
    )
    assert is_win1 == expected_result1
    assert is_win2 == expected_result2
    assert reduced_div1 is None
    assert reduced_div2 is None
    assert orientation1 is None
    assert orientation2 is None


def test_q_reduction(sequence_test_graph, sequence_test_initial_divisor):
    """Test the q_reduction function."""
    expected_q_reduced_divisor = CFDivisor(
        sequence_test_graph, [("Alice", 2), ("Bob", 0), ("Charlie", 0), ("Elise", 0)]
    )
    assert q_reduction(sequence_test_initial_divisor) == expected_q_reduced_divisor


def test_is_q_reduced(sequence_test_initial_divisor):
    """Test the is_q_reduced function."""
    expected_result = True
    assert is_q_reduced(sequence_test_initial_divisor) == expected_result


@pytest.fixture
def simple_graph():
    """Provides a simple graph K3 for testing."""
    vertices = {"v1", "v2", "v3"}
    edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
    return CFGraph(vertices, edges)


def test_linear_equivalence_identical_divisors(simple_graph):
    """Test linear equivalence with identical divisors."""
    degrees1 = [("v1", 2), ("v2", 0), ("v3", -1)]
    divisor1 = CFDivisor(simple_graph, degrees1)
    divisor2 = CFDivisor(simple_graph, degrees1)  # Identical
    expected_result = True
    assert linear_equivalence(divisor1, divisor2) == expected_result


def test_linear_equivalence_different_total_degree(simple_graph):
    """Test linear equivalence with divisors having different total degrees."""
    degrees1 = [("v1", 2), ("v2", 0), ("v3", -1)]  # Total degree 1
    divisor1 = CFDivisor(simple_graph, degrees1)
    degrees2 = [("v1", 1), ("v2", 1), ("v3", 0)]  # Total degree 2
    divisor2 = CFDivisor(simple_graph, degrees2)
    expected_result = False
    assert linear_equivalence(divisor1, divisor2) == expected_result


def test_linear_equivalence_equivalent_by_firing(simple_graph):
    """Test linear equivalence where one divisor is reachable by a firing move."""
    degrees1 = [("v1", 3), ("v2", 1), ("v3", 0)]
    divisor1 = CFDivisor(simple_graph, degrees1)
    degrees2 = [("v1", 1), ("v2", 2), ("v3", 1)]  # Obtained by firing v1 from divisor1
    divisor2 = CFDivisor(simple_graph, degrees2)
    expected_result = True
    assert linear_equivalence(divisor1, divisor2) == expected_result
    assert linear_equivalence(divisor2, divisor1) == expected_result  # Symmetric


def test_linear_equivalence_cycle_graph_equivalent(simple_graph):
    """Test linear equivalence on a cycle graph (K3 is C3) - known equivalent divisors"""
    d1 = CFDivisor(simple_graph, [("v1", 2), ("v2", 0), ("v3", 0)])
    d2 = CFDivisor(simple_graph, [("v1", 0), ("v2", 1), ("v3", 1)])
    expected_result = True
    assert linear_equivalence(d1, d2) == expected_result


def test_linear_equivalence_path_graph_not_equivalent():
    """Test linear equivalence on a path graph P3 - known non-equivalent divisors."""
    vertices = {"p1", "p2", "p3"}
    edges = [("p1", "p2", 1), ("p2", "p3", 1)]
    p3_graph = CFGraph(vertices, edges)
    d1 = CFDivisor(p3_graph, [("p1", 1), ("p2", 0), ("p3", 0)])
    d2 = CFDivisor(p3_graph, [("p1", 0), ("p2", 0), ("p3", 1)])
    expected_result = True
    assert linear_equivalence(d1, d2) == expected_result


def test_linear_equivalence_on_ABCE(sequence_test_graph):
    """Test linear equivalence on the Alice, Bob, Charlie, Elise graph."""
    # Define the initial divisor
    initial_degrees1 = [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)]
    divisor1 = CFDivisor(sequence_test_graph, initial_degrees1)
    initial_degrees2 = [("Alice", 2), ("Bob", 0), ("Charlie", 0), ("Elise", 0)]
    divisor2 = CFDivisor(sequence_test_graph, initial_degrees2)
    expected_result = True
    assert linear_equivalence(divisor1, divisor2) == expected_result


def test_is_winnable_example_winnable(sequence_test_initial_divisor):
    """Test is_winnable with a known winnable configuration."""
    # sequence_test_initial_divisor is D = (A:2, B:-3, C:4, E:-1) which test_ewd_example expects to be True
    expected_result = True
    assert is_winnable(sequence_test_initial_divisor) == expected_result


def test_is_winnable_simple_graph_not_winnable(simple_graph):
    """Test is_winnable with a simple non-winnable configuration on K3."""
    # D = (v1:0, v2:0, v3:-1) on K3 should not be winnable.
    non_winnable_degrees = [("v1", 0), ("v2", 0), ("v3", -2)]
    divisor = CFDivisor(simple_graph, non_winnable_degrees)
    expected_result = False
    assert is_winnable(divisor) == expected_result


def test_is_winnable_simple_graph_all_zero(simple_graph):
    """Test is_winnable with all zero degrees on K3 (should be winnable)."""
    all_zero_degrees = [("v1", 0), ("v2", 0), ("v3", 0)]
    divisor = CFDivisor(simple_graph, all_zero_degrees)
    expected_result = True
    assert is_winnable(divisor) == expected_result
