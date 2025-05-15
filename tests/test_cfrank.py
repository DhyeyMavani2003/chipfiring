import pytest
from chipfiring import rank
from chipfiring.CFGraph import CFGraph
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFOrientation import CFOrientation
from chipfiring.algo import is_winnable


@pytest.fixture
def simple_graph():
    """Provides a simple graph K3 for testing."""
    vertices = {"v1", "v2", "v3"}
    edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
    return CFGraph(vertices, edges)


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


# Tests for rank function
def test_rank_initially_unwinnable(simple_graph):
    """Test rank returns -1 for an initially unwinnable divisor."""
    # D = (v1:0, v2:0, v3:-2) on K3 is unwinnable
    unwinnable_degrees = [("v1", 0), ("v2", 0), ("v3", -2)]
    divisor = CFDivisor(simple_graph, unwinnable_degrees)
    assert rank(divisor).rank == -1


def test_rank_0_k3_winnable_but_k1_removal_unwinnable(simple_graph):
    """Test rank is 0 if divisor is winnable, but removing 1 chip makes it unwinnable."""
    # D = (v1:1, v2:0, v3:0) on K3. Winnable.
    # Removing 1 chip from v2 gives (1, -1, 0), which is unwinnable.
    degrees = [("v1", 1), ("v2", 0), ("v3", 0)]
    divisor = CFDivisor(simple_graph, degrees)
    assert is_winnable(divisor)  # Pre-condition check
    # EWD((1,-1,0)) with q=v2 gives deg_q = -1, so unwinnable
    assert rank(divisor).rank == 0


def test_rank_0_k3_zero_divisor(simple_graph):
    """Test rank is 0 for the zero divisor on K3."""
    # D = (v1:0, v2:0, v3:0) on K3. Winnable.
    # Removing 1 chip (k=1) results in total_degree < 0 for subtracted divisor,
    # so generator yields nothing, processed_at_least_one_valid_divisor is false. Returns k-1 = 0.
    degrees = [("v1", 0), ("v2", 0), ("v3", 0)]
    divisor = CFDivisor(simple_graph, degrees)
    assert is_winnable(divisor)  # Pre-condition check
    assert rank(divisor).rank == 0


def test_rank_1_single_vertex_graph():
    """Test rank is 1 for D=(1) on a single vertex graph."""
    g = CFGraph({"v1"}, [])
    d = CFDivisor(g, [("v1", 1)])
    assert is_winnable(d)
    # k=1: remove 1 from v1 -> (0). Winnable.
    # k=2: remove 2 from v1 -> (-1). Total degree < 0. Gen yields nothing. Returns k-1 = 1.
    assert rank(d).rank == 1


@pytest.fixture
def k2_graph():
    """Provides a K2 graph."""
    vertices = {"v1", "v2"}
    edges = [("v1", "v2", 1)]
    return CFGraph(vertices, edges)


def test_rank_1_k2_graph(k2_graph):
    """Test rank for D=(1,1) on K2."""
    d = CFDivisor(k2_graph, [("v1", 1), ("v2", 1)])  # Total 2
    assert is_winnable(d)
    # k=1: (0,1) winnable, (1,0) winnable.
    # k=2: (-1,1) winnable, (1,-1) winnable.
    # k=3: (-2,1) unwinnable, (1,-2) unwinnable. Returns k-1 = 2.
    assert rank(d).rank == 2


def test_rank_1_k2_graph_riemann_roch_theorem(k2_graph):
    """Test rank for D=(1,1) on K2 using Riemann-Roch theorem."""
    D = CFDivisor(k2_graph, [("v1", 1), ("v2", 1)])  # Total 2
    orientation = CFOrientation(k2_graph, [])
    K = orientation.canonical_divisor()
    K_minus_D = K - D

    # Check if Riemann-Roch theorem holds
    assert (
        rank(K_minus_D).rank
        == rank(D).rank - 1 - D.get_total_degree() + k2_graph.get_genus()
    )


def test_rank_0_k2_graph_asymmetric(k2_graph):
    """Test rank for D=(2,0) on K2."""
    d = CFDivisor(k2_graph, [("v1", 2), ("v2", 0)])  # Total 2
    assert is_winnable(d)
    # k=1: (1,0) winnable. (2,-1) winnable.
    # k=2: (-1,1) winnable, (1,-1) winnable.
    # k=3: (-2,1) unwinnable, (1,-2) unwinnable. Returns k-1 = 2.
    assert rank(d).rank == 2


def test_rank_0_k2_graph_asymmetric_riemann_roch_theorem(k2_graph):
    """Test rank for D=(2,0) on K2 using Riemann-Roch theorem."""
    D = CFDivisor(k2_graph, [("v1", 2), ("v2", 0)])  # Total 2
    orientation = CFOrientation(k2_graph, [])
    K = orientation.canonical_divisor()
    K_minus_D = K - D

    # Check if Riemann-Roch theorem holds
    assert (
        rank(K_minus_D).rank
        == rank(D).rank - 1 - D.get_total_degree() + k2_graph.get_genus()
    )


def test_rank_k3_slightly_more_chips(simple_graph):
    """Test rank for a divisor with more chips on K3."""
    # D = (1,1,0) on K3. Total 2. Winnable.
    # is_winnable(1,1,0) on K3: True (can reduce to (0,0,0))
    degrees = [("v1", 1), ("v2", 1), ("v3", 0)]
    divisor = CFDivisor(simple_graph, degrees)
    assert is_winnable(divisor)

    # k=1:
    # rem v1: (0,1,0) -> winnable
    # rem v2: (1,0,0) -> winnable
    # rem v3: (1,1,-1) -> winnable (q=v3, deg_q=1 at the end of EWD)
    # k = 2:
    # (0,0,0) -> winnable
    # (0,1,-1) -> unwinnable (checked by EWD). Returns k-1 = 1.
    assert rank(divisor).rank == 1


def test_rank_k3_slightly_more_chips_riemann_roch_theorem(simple_graph):
    """Test rank for (1,1,0) on K3 using Riemann-Roch theorem."""
    D = CFDivisor(simple_graph, [("v1", 1), ("v2", 1), ("v3", 0)])  # Total 2
    orientation = CFOrientation(simple_graph, [])
    K = orientation.canonical_divisor()
    K_minus_D = K - D

    # Check if Riemann-Roch theorem holds
    assert (
        rank(K_minus_D).rank
        == rank(D).rank - 1 - D.get_total_degree() + simple_graph.get_genus()
    )


def test_rank_k3_even_more_chips(simple_graph):
    """Test rank for (1,1,1) on K3."""
    degrees = [("v1", 1), ("v2", 1), ("v3", 1)]  # Total 3
    divisor = CFDivisor(simple_graph, degrees)
    assert is_winnable(divisor)
    # k=1:
    # (0,1,1) -> winnable
    # (1,0,1) -> winnable
    # (1,1,0) -> winnable
    # All k=1 subtractions are winnable.

    # k=2:
    # All k=2 subtractions are winnable.

    # k=3:
    # (0,0,0) -> winnable
    # (0,1,-1) -> unwinnable (checked by EWD). Returns k-1 = 2.
    assert rank(divisor).rank == 2


def test_rank_k3_even_more_chips_riemann_roch_theorem(simple_graph):
    """Test rank for (1,1,1) on K3 using Riemann-Roch theorem."""
    D = CFDivisor(simple_graph, [("v1", 1), ("v2", 1), ("v3", 1)])  # Total 3
    orientation = CFOrientation(simple_graph, [])
    K = orientation.canonical_divisor()
    K_minus_D = K - D

    # Check if Riemann-Roch theorem holds
    assert (
        rank(K_minus_D).rank
        == rank(D).rank - 1 - D.get_total_degree() + simple_graph.get_genus()
    )


def test_rank_sequence_test_graph(sequence_test_initial_divisor):
    """Test rank for the sequence test graph."""
    # D = (A:2, B:-3, C:4, E:-1) on sequence_test_graph.
    # Total degree = 2. Winnable as checked by EWD.

    # k=1: (1,-3,4,-1) unwinnable as checked by EWD.
    assert rank(sequence_test_initial_divisor).rank == 0


def test_rank_sequence_test_graph_riemann_roch_theorem(
    sequence_test_graph, sequence_test_initial_divisor
):
    """Test rank for the sequence test graph using Riemann-Roch theorem."""
    D = sequence_test_initial_divisor
    orientation = CFOrientation(sequence_test_graph, [])
    K = orientation.canonical_divisor()
    K_minus_D = K - D

    rank_K_minus_D = rank(K_minus_D)
    rank_D = rank(D)

    # Check if Riemann-Roch theorem holds
    assert (
        rank_K_minus_D.rank
        == rank_D.rank - 1 - D.get_total_degree() + sequence_test_graph.get_genus()
    )


def test_rank_sequence_test_graph_optimized(sequence_test_initial_divisor):
    """Test rank for the sequence test graph using optimized rank calculation."""
    assert rank(sequence_test_initial_divisor, optimized=True).rank == 0


def test_rank_sequence_optimized_corollary_4_4_3(sequence_test_graph):
    """Test rank for the sequence test graph using optimized rank calculation and Corollary 4.4.3."""
    D = CFDivisor(
        sequence_test_graph, [("Alice", 5), ("Bob", -3), ("Charlie", 4), ("Elise", -1)]
    )
    assert (
        rank(D, optimized=True).rank
        == D.get_total_degree() - sequence_test_graph.get_genus()
    )
    print(rank(D, optimized=True).get_log_summary())
    # Check if Corollary 4.4.3 is called in the optimized rank calculation logs
    assert "Corollary 4.4.3" in rank(D, optimized=True).get_log_summary()
