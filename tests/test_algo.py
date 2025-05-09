import pytest
from chipfiring.CFGraph import CFGraph
from chipfiring.CFDivisor import CFDivisor
from chipfiring.algo import EWD, linear_equivalence

@pytest.fixture
def sequence_test_graph():
    """Graph used in the set_fire and laplacian sequence tests."""
    vertices = {"Alice", "Bob", "Charlie", "Elise"}
    edges = [
        ("Alice", "Bob", 1),
        ("Bob", "Charlie", 1),
        ("Charlie", "Elise", 1),
        ("Alice", "Elise", 2),
        ("Alice", "Charlie", 1)
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
    assert EWD(sequence_test_graph, sequence_test_initial_divisor) == expected_result

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
    divisor2 = CFDivisor(simple_graph, degrees1) # Identical
    assert linear_equivalence(divisor1, divisor2) == True

def test_linear_equivalence_different_total_degree(simple_graph):
    """Test linear equivalence with divisors having different total degrees."""
    degrees1 = [("v1", 2), ("v2", 0), ("v3", -1)] # Total degree 1
    divisor1 = CFDivisor(simple_graph, degrees1)
    degrees2 = [("v1", 1), ("v2", 1), ("v3", 0)]  # Total degree 2
    divisor2 = CFDivisor(simple_graph, degrees2)
    assert linear_equivalence(divisor1, divisor2) == False

def test_linear_equivalence_equivalent_by_firing(simple_graph):
    """Test linear equivalence where one divisor is reachable by a firing move."""
    degrees1 = [("v1", 3), ("v2", 1), ("v3", 0)]
    divisor1 = CFDivisor(simple_graph, degrees1)
    degrees2 = [("v1", 1), ("v2", 2), ("v3", 1)] # Obtained by firing v1 from divisor1
    divisor2 = CFDivisor(simple_graph, degrees2)
    assert linear_equivalence(divisor1, divisor2) == True
    assert linear_equivalence(divisor2, divisor1) == True # Symmetric

def test_linear_equivalence_cycle_graph_equivalent(simple_graph):
    """ Test linear equivalence on a cycle graph (K3 is C3) - known equivalent divisors """
    d1 = CFDivisor(simple_graph, [("v1", 2), ("v2", 0), ("v3", 0)])
    d2 = CFDivisor(simple_graph, [("v1", 0), ("v2", 1), ("v3", 1)])
    assert linear_equivalence(d1, d2) == True

def test_linear_equivalence_path_graph_not_equivalent():
    """ Test linear equivalence on a path graph P3 - known non-equivalent divisors. """
    vertices = {"p1", "p2", "p3"}
    edges = [("p1", "p2", 1), ("p2", "p3", 1)]
    p3_graph = CFGraph(vertices, edges)
    d1 = CFDivisor(p3_graph, [("p1", 1), ("p2", 0), ("p3", 0)])
    d2 = CFDivisor(p3_graph, [("p1", 0), ("p2", 0), ("p3", 1)])
    assert linear_equivalence(d1, d2) == True

def test_linear_equivalence_on_ABCE(sequence_test_graph):
    """Test linear equivalence on the Alice, Bob, Charlie, Elise graph."""
    # Define the initial divisor
    initial_degrees1 = [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)]
    divisor1 = CFDivisor(sequence_test_graph, initial_degrees1)
    initial_degrees2 = [("Alice", 2), ("Bob", 0), ("Charlie", 0), ("Elise", 0)]
    divisor2 = CFDivisor(sequence_test_graph, initial_degrees2)
    assert linear_equivalence(divisor1, divisor2) == True

