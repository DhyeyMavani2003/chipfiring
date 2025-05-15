import pytest
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFGraph import CFGraph


@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
    return CFGraph(vertices, edges)


@pytest.fixture
def simple_graph():
    """Provides a simple graph K3 for testing."""
    vertices = {"v1", "v2", "v3"}
    edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
    return CFGraph(vertices, edges)


@pytest.fixture
def graph_with_multi_edges():
    """Provides a graph with multiple edges."""
    vertices = {"a", "b", "c"}
    edges = [("a", "b", 2), ("b", "c", 3)]
    return CFGraph(vertices, edges)


@pytest.fixture
def initial_divisor(simple_graph):
    """Provides an initial divisor for the simple graph."""
    degrees = [("v1", 5), ("v2", 0), ("v3", -2)]
    return CFDivisor(simple_graph, degrees)


def test_divisor_creation(sample_graph):
    """Test basic divisor creation."""
    degrees = [("A", 2), ("B", -1), ("C", 0)]
    divisor = CFDivisor(sample_graph, degrees)

    # Test degrees were set correctly
    assert divisor.get_degree("A") == 2
    assert divisor.get_degree("B") == -1
    assert divisor.get_degree("C") == 0

    # Test total degree calculation
    assert divisor.total_degree == 1  # 2 + (-1) + 0 = 1


def test_divisor_duplicate_vertices(sample_graph):
    """Test that duplicate vertex names in degrees are not allowed."""
    degrees = [("A", 2), ("A", 1), ("B", -1)]

    with pytest.raises(ValueError, match="Duplicate vertex names are not allowed"):
        CFDivisor(sample_graph, degrees)


def test_divisor_invalid_vertex(sample_graph):
    """Test that using non-existent vertices raises an error."""
    degrees = [("A", 2), ("D", 1)]  # D is not in the graph

    with pytest.raises(ValueError, match="Vertex D not found in graph"):
        CFDivisor(sample_graph, degrees)


def test_get_degree_invalid_vertex(sample_graph):
    """Test getting degree of non-existent vertex."""
    divisor = CFDivisor(sample_graph, [("A", 2), ("B", -1), ("C", 0)])

    with pytest.raises(ValueError, match="Vertex D not in divisor"):
        divisor.get_degree("D")


def test_get_total_degree(sample_graph):
    """Test total degree calculation with various configurations."""
    # Test positive total
    divisor1 = CFDivisor(sample_graph, [("A", 2), ("B", 1), ("C", 0)])
    assert divisor1.get_total_degree() == 3

    # Test negative total
    divisor2 = CFDivisor(sample_graph, [("A", -2), ("B", -1), ("C", 0)])
    assert divisor2.get_total_degree() == -3

    # Test zero total
    divisor3 = CFDivisor(sample_graph, [("A", 1), ("B", -1), ("C", 0)])
    assert divisor3.get_total_degree() == 0


def test_empty_degrees(sample_graph):
    """Test creating a divisor with empty degrees list."""
    divisor = CFDivisor(sample_graph, [])

    # All vertices should have degree 0
    assert divisor.get_degree("A") == 0
    assert divisor.get_degree("B") == 0
    assert divisor.get_degree("C") == 0
    assert divisor.get_total_degree() == 0


def test_cfdivisor_init_valid(simple_graph):
    """Test CFDivisor initialization with valid degrees."""
    degrees = [("v1", 10), ("v2", -5)]
    divisor = CFDivisor(simple_graph, degrees)
    assert divisor.get_degree("v1") == 10
    assert divisor.get_degree("v2") == -5
    assert divisor.get_degree("v3") == 0  # Default degree
    assert divisor.get_total_degree() == 5


def test_cfdivisor_init_duplicate_vertex(simple_graph):
    """Test CFDivisor initialization with duplicate vertex names."""
    degrees = [("v1", 1), ("v1", 2)]
    with pytest.raises(
        ValueError, match="Duplicate vertex names are not allowed in degrees"
    ):
        CFDivisor(simple_graph, degrees)


def test_cfdivisor_init_invalid_vertex(simple_graph):
    """Test CFDivisor initialization with a vertex not in the graph."""
    degrees = [("v1", 1), ("v4", 1)]  # v4 not in graph
    with pytest.raises(ValueError, match="Vertex v4 not found in graph"):
        CFDivisor(simple_graph, degrees)


def test_get_degree(initial_divisor):
    """Test the get_degree method."""
    assert initial_divisor.get_degree("v1") == 5
    assert initial_divisor.get_degree("v2") == 0
    assert initial_divisor.get_degree("v3") == -2


def test_lending_move(simple_graph):
    """Test the lending_move (firing_move) operation."""
    # K3: v1 -- v2 -- v3 -- v1. All valences are 2.
    degrees = [("v1", 3), ("v2", 1), ("v3", 0)]
    divisor = CFDivisor(simple_graph, degrees)
    initial_total = divisor.get_total_degree()

    # Lend from v1 (valence 2)
    divisor.lending_move("v1")

    # v1 degree decreases by valence (2)
    assert divisor.get_degree("v1") == 3 - 2  # 1
    # Neighbors v2 and v3 increase by 1
    assert divisor.get_degree("v2") == 1 + 1  # 2
    assert divisor.get_degree("v3") == 0 + 1  # 1
    # Total degree should remain the same
    assert divisor.get_total_degree() == initial_total  # 1 + 2 + 1 = 4


def test_lending_move_multi_edge(graph_with_multi_edges):
    """Test lending_move on a graph with multiple edges."""
    # Graph: a ==(2)== b ==(3)== c. Valences: a=2, b=5, c=3
    degrees = [("a", 10), ("b", 5), ("c", 0)]
    divisor = CFDivisor(graph_with_multi_edges, degrees)
    initial_total = divisor.get_total_degree()

    # Lend from b (valence 5)
    divisor.firing_move("b")  # firing_move is an alias for lending_move

    # b degree decreases by 5
    assert divisor.get_degree("b") == 5 - 5  # 0
    # Neighbors a and c increase by 1 (even with multi-edges)
    assert divisor.get_degree("a") == 10 + 2  # 12
    assert divisor.get_degree("c") == 0 + 3  # 3
    # Total degree should remain the same
    assert divisor.get_total_degree() == initial_total  # 12 + 0 + 3 = 15


def test_lending_move_invalid_vertex(initial_divisor):
    """Test lending_move with a vertex not in the graph."""
    with pytest.raises(ValueError, match="Vertex v4 not found in graph"):
        initial_divisor.lending_move("v4")


def test_borrowing_move(simple_graph):
    """Test the borrowing_move operation."""
    degrees = [("v1", 3), ("v2", 1), ("v3", 0)]
    divisor = CFDivisor(simple_graph, degrees)
    initial_total = divisor.get_total_degree()

    # Borrow at v2 (valence 2)
    divisor.borrowing_move("v2")

    # v2 degree increases by valence (2)
    assert divisor.get_degree("v2") == 1 + 2  # 3
    # Neighbors v1 and v3 decrease by 1
    assert divisor.get_degree("v1") == 3 - 1  # 2
    assert divisor.get_degree("v3") == 0 - 1  # -1
    # Total degree should remain the same
    assert divisor.get_total_degree() == initial_total  # 2 + 3 - 1 = 4


def test_borrowing_move_invalid_vertex(initial_divisor):
    """Test borrowing_move with a vertex not in the graph."""
    with pytest.raises(ValueError, match="Vertex v4 not found in graph"):
        initial_divisor.borrowing_move("v4")


def test_chip_transfer(initial_divisor):
    """Test the chip_transfer operation."""
    initial_total = initial_divisor.get_total_degree()
    v1_initial = initial_divisor.get_degree("v1")  # 5
    v2_initial = initial_divisor.get_degree("v2")  # 0
    v3_initial = initial_divisor.get_degree("v3")  # -2

    # Transfer 1 chip v1 -> v2
    initial_divisor.chip_transfer("v1", "v2")
    assert initial_divisor.get_degree("v1") == v1_initial - 1  # 4
    assert initial_divisor.get_degree("v2") == v2_initial + 1  # 1
    assert initial_divisor.get_degree("v3") == v3_initial  # -2
    assert initial_divisor.get_total_degree() == initial_total  # 4 + 1 - 2 = 3

    # Transfer 3 chips v2 -> v3
    initial_divisor.chip_transfer("v2", "v3", amount=3)
    assert initial_divisor.get_degree("v1") == 4  # Unchanged
    assert initial_divisor.get_degree("v2") == 1 - 3  # -2
    assert initial_divisor.get_degree("v3") == -2 + 3  # 1
    assert initial_divisor.get_total_degree() == initial_total  # 4 - 2 + 1 = 3


def test_chip_transfer_invalid_amount(initial_divisor):
    """Test chip_transfer with zero or negative amount."""
    with pytest.raises(ValueError, match="Amount must be positive for chip transfer"):
        initial_divisor.chip_transfer("v1", "v2", amount=0)
    with pytest.raises(ValueError, match="Amount must be positive for chip transfer"):
        initial_divisor.chip_transfer("v1", "v2", amount=-5)


def test_chip_transfer_invalid_vertex(initial_divisor):
    """Test chip_transfer with vertices not in the divisor."""
    with pytest.raises(ValueError, match="Vertex v4 not in divisor"):
        initial_divisor.chip_transfer("v1", "v4")
    with pytest.raises(ValueError, match="Vertex v4 not in divisor"):
        initial_divisor.chip_transfer("v4", "v1")


def test_set_fire_single_vertex(graph_with_multi_edges):
    """Test set_fire with a single vertex in the firing set."""
    # Graph: a ==(2)== b ==(3)== c. Valences: a=2, b=5, c=3
    degrees = [("a", 10), ("b", 5), ("c", 0)]
    divisor = CFDivisor(graph_with_multi_edges, degrees)
    initial_total = divisor.get_total_degree()

    # Fire set {a}
    # Edges from a: (a, b, 2). b is not in the set. Transfer 2 chips a -> b.
    divisor.set_fire({"a"})
    assert divisor.get_degree("a") == 10 - 2  # 8
    assert divisor.get_degree("b") == 5 + 2  # 7
    assert divisor.get_degree("c") == 0  # 0
    assert divisor.get_total_degree() == initial_total  # 8 + 7 + 0 = 15


def test_set_fire_multiple_vertices(graph_with_multi_edges):
    """Test set_fire with multiple vertices in the firing set."""
    degrees = [("a", 10), ("b", 5), ("c", 0)]
    divisor = CFDivisor(graph_with_multi_edges, degrees)
    initial_total = divisor.get_total_degree()  # 15

    # Fire set {a, b}
    # Edges from a: (a, b, 2). b is in the set. No transfer.
    # Edges from b: (b, a, 2). a is in the set. No transfer.
    # Edges from b: (b, c, 3). c is not in the set. Transfer 3 chips b -> c.
    divisor.set_fire({"a", "b"})
    assert divisor.get_degree("a") == 10  # 10
    assert divisor.get_degree("b") == 5 - 3  # 2
    assert divisor.get_degree("c") == 0 + 3  # 3
    assert divisor.get_total_degree() == initial_total  # 10 + 2 + 3 = 15


def test_set_fire_empty_set(initial_divisor):
    """Test set_fire with an empty firing set."""
    v1_initial = initial_divisor.get_degree("v1")
    v2_initial = initial_divisor.get_degree("v2")
    v3_initial = initial_divisor.get_degree("v3")
    initial_total = initial_divisor.get_total_degree()

    initial_divisor.set_fire(set())

    assert initial_divisor.get_degree("v1") == v1_initial
    assert initial_divisor.get_degree("v2") == v2_initial
    assert initial_divisor.get_degree("v3") == v3_initial
    assert initial_divisor.get_total_degree() == initial_total


def test_set_fire_invalid_vertex(initial_divisor):
    """Test set_fire with a vertex not in the graph."""
    with pytest.raises(ValueError, match="Vertex v4 not found in graph"):
        initial_divisor.set_fire({"v1", "v4"})


def test_set_fire_sequence():
    """Test a sequence of set_fire operations on a specific graph."""
    # Define the graph
    vertices = {"Alice", "Bob", "Charlie", "Elise"}
    edges = [
        ("Alice", "Bob", 1),
        ("Bob", "Charlie", 1),
        ("Charlie", "Elise", 1),
        ("Alice", "Elise", 2),
        ("Alice", "Charlie", 1),
    ]
    graph = CFGraph(vertices, edges)

    # Define the initial divisor
    initial_degrees = [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)]
    divisor = CFDivisor(graph, initial_degrees)
    initial_total = divisor.get_total_degree()
    assert initial_total == 2

    # --- Perform set_fire operations ---

    # Operation 1: fire{"Alice", "Elise", "Charlie"}
    # Edges out: (Alice, Bob, 1), (Charlie, Bob, 1)
    # Expected changes: A: -1, B: +2, C: -1, E: 0
    # Expected result: A=1, B=-1, C=3, E=-1
    divisor.set_fire({"Alice", "Elise", "Charlie"})
    assert divisor.get_degree("Alice") == 1
    assert divisor.get_degree("Bob") == -1
    assert divisor.get_degree("Charlie") == 3
    assert divisor.get_degree("Elise") == -1
    assert divisor.get_total_degree() == initial_total

    # Operation 2: fire{"Alice", "Elise", "Charlie"} (same set again)
    # Edges out: (Alice, Bob, 1), (Charlie, Bob, 1)
    # Expected changes: A: -1, B: +2, C: -1, E: 0
    # Expected result: A=0, B=1, C=2, E=-1
    divisor.set_fire({"Alice", "Elise", "Charlie"})
    assert divisor.get_degree("Alice") == 0
    assert divisor.get_degree("Bob") == 1
    assert divisor.get_degree("Charlie") == 2
    assert divisor.get_degree("Elise") == -1
    assert divisor.get_total_degree() == initial_total

    # Operation 3: fire{"Bob", "Charlie"}
    # Edges out: (Bob, Alice, 1), (Charlie, Alice, 1), (Charlie, Elise, 1)
    # Expected changes: A: +2, B: -1, C: -2, E: +1
    # Expected final result: A=2, B=0, C=0, E=0
    divisor.set_fire({"Bob", "Charlie"})
    assert divisor.get_degree("Alice") == 2
    assert divisor.get_degree("Bob") == 0
    assert divisor.get_degree("Charlie") == 0
    assert divisor.get_degree("Elise") == 0
    assert divisor.get_total_degree() == initial_total


def test_is_effective(simple_graph):
    """Test is_effective method."""
    # Create an effective divisor
    effective_divisor = CFDivisor(simple_graph, [("v1", 1), ("v2", 0), ("v3", 3)])
    expected_result = True
    assert effective_divisor.is_effective() == expected_result


def test_is_effective_zero_degree(simple_graph):
    """Test is_effective method with a vertex with zero degree."""
    zero_divisor = CFDivisor(simple_graph, [("v1", 0), ("v2", 0), ("v3", 0)])
    expected_result = True
    assert zero_divisor.is_effective() == expected_result


def test_is_effective_negative_degree(simple_graph):
    """Test is_effective method with a vertex withnegative degree."""
    negative_divisor = CFDivisor(simple_graph, [("v1", 1), ("v2", 2), ("v3", -3)])
    expected_result = False
    assert negative_divisor.is_effective() == expected_result


def test_divisor_addition(simple_graph):
    """Test vertex-wise addition of two divisors."""
    degrees1 = [("v1", 1), ("v2", 2), ("v3", 3)]
    divisor1 = CFDivisor(simple_graph, degrees1)

    degrees2 = [("v1", 4), ("v2", 5), ("v3", 0)]  # v3 has 0 here
    divisor2 = CFDivisor(simple_graph, degrees2)

    sum_divisor = divisor1 + divisor2

    assert sum_divisor.get_degree("v1") == 1 + 4
    assert sum_divisor.get_degree("v2") == 2 + 5
    assert sum_divisor.get_degree("v3") == 3 + 0
    assert sum_divisor.get_total_degree() == (1 + 2 + 3) + (4 + 5 + 0)
    assert sum_divisor.graph == simple_graph  # Should be on the same graph


def test_divisor_subtraction(simple_graph):
    """Test vertex-wise subtraction of two divisors."""
    degrees1 = [("v1", 5), ("v2", 0), ("v3", -2)]
    divisor1 = CFDivisor(simple_graph, degrees1)

    degrees2 = [("v1", 1), ("v2", -1), ("v3", 3)]
    divisor2 = CFDivisor(simple_graph, degrees2)

    diff_divisor = divisor1 - divisor2

    assert diff_divisor.get_degree("v1") == 5 - 1
    assert diff_divisor.get_degree("v2") == 0 - (-1)
    assert diff_divisor.get_degree("v3") == -2 - 3
    assert diff_divisor.get_total_degree() == (5 + 0 - 2) - (1 - 1 + 3)
    assert diff_divisor.graph == simple_graph  # Should be on the same graph


def test_divisor_addition_with_unspecified_degrees(simple_graph):
    """Test addition where one divisor doesn't explicitly list all vertices (they default to 0)."""
    # graph has v1, v2, v3. All default to 0 in CFDivisor constructor if not specified.
    degrees1 = [("v1", 10)]  # v2, v3 are 0
    divisor1 = CFDivisor(simple_graph, degrees1)

    degrees2 = [("v2", 5)]  # v1, v3 are 0
    divisor2 = CFDivisor(simple_graph, degrees2)

    sum_divisor = divisor1 + divisor2
    assert sum_divisor.get_degree("v1") == 10 + 0
    assert sum_divisor.get_degree("v2") == 0 + 5
    assert sum_divisor.get_degree("v3") == 0 + 0


def test_divisor_op_different_graphs():
    """Test that add/sub with divisors on different graphs raises ValueError."""
    g1_vertices = {"A", "B"}
    graph1 = CFGraph(g1_vertices, [])
    divisor1 = CFDivisor(graph1, [("A", 1)])

    g2_vertices = {"X", "Y"}  # Different vertex set
    graph2 = CFGraph(g2_vertices, [])
    divisor2 = CFDivisor(graph2, [("X", 1)])

    with pytest.raises(
        ValueError, match="Divisors must be on graphs with the same set of vertices"
    ):
        _ = divisor1 + divisor2
    with pytest.raises(
        ValueError, match="Divisors must be on graphs with the same set of vertices"
    ):
        _ = divisor1 - divisor2


def test_divisor_op_compatible_graphs_different_structure():
    """Test add/sub with divisors on graphs that have same vertices but different edge structure."""
    # This should still work as __add__/__sub__ only care about vertex set compatibility for op itself.
    # The result uses self.graph.
    vertices = {"v1", "v2"}
    graph_a = CFGraph(vertices, [("v1", "v2", 1)])
    graph_b = CFGraph(
        vertices, [("v1", "v2", 2)]
    )  # Same vertices, different edge weight

    div_a = CFDivisor(graph_a, [("v1", 1), ("v2", 1)])
    div_b = CFDivisor(graph_b, [("v1", 2), ("v2", 2)])

    sum_div = div_a + div_b
    assert sum_div.get_degree("v1") == 3
    assert sum_div.get_degree("v2") == 3
    assert sum_div.graph == graph_a  # Resulting graph is from the left operand

    diff_div = div_a - div_b
    assert diff_div.get_degree("v1") == -1
    assert diff_div.get_degree("v2") == -1
    assert diff_div.graph == graph_a

    # Test that the result uses self.graph
    assert sum_div.graph == graph_a
    assert diff_div.graph == graph_a


def test_remove_vertex(sample_graph):
    """Test the remove_vertex method."""
    # Create a divisor with some degrees
    divisor = CFDivisor(sample_graph, [("A", 3), ("B", -1), ("C", 2)])

    # Remove vertex B
    new_divisor = divisor.remove_vertex("B")

    # Check the new divisor has one less vertex
    assert "B" not in [v.name for v in new_divisor.graph.vertices]
    assert len(new_divisor.graph.vertices) == 2

    # Check degrees are preserved for remaining vertices
    assert new_divisor.get_degree("A") == 3
    assert new_divisor.get_degree("C") == 2

    # Check total degree is updated
    assert new_divisor.get_total_degree() == 5  # 3 + 2 = 5


def test_remove_vertex_invalid(sample_graph):
    """Test remove_vertex with a non-existent vertex."""
    divisor = CFDivisor(sample_graph, [("A", 1), ("B", 1), ("C", 1)])

    with pytest.raises(ValueError, match="Vertex D not found in graph"):
        divisor.remove_vertex("D")


def test_divisor_equality(simple_graph):
    """Test equality comparison between divisors."""
    # Create two identical divisors
    div1 = CFDivisor(simple_graph, [("v1", 1), ("v2", 2), ("v3", 3)])
    div2 = CFDivisor(simple_graph, [("v1", 1), ("v2", 2), ("v3", 3)])

    # They should be equal
    assert div1 == div2

    # Create a divisor with different degrees
    div3 = CFDivisor(simple_graph, [("v1", 5), ("v2", 2), ("v3", 3)])
    assert div1 != div3

    # Create a divisor with same degrees but different graph structure
    different_graph = CFGraph(
        {"v1", "v2", "v3"}, [("v1", "v2", 2), ("v2", "v3", 2), ("v1", "v3", 2)]
    )
    div4 = CFDivisor(different_graph, [("v1", 1), ("v2", 2), ("v3", 3)])
    assert div1 != div4

    # Test comparison with non-CFDivisor object
    assert div1 != "not a divisor"


def test_divisor_equality_different_vertices():
    """Test equality comparison between divisors with different vertex sets."""
    # Create graphs with different vertex sets
    g1 = CFGraph({"A", "B"}, [("A", "B", 1)])
    g2 = CFGraph({"A", "B", "C"}, [("A", "B", 1), ("B", "C", 1)])

    div1 = CFDivisor(g1, [("A", 1), ("B", 2)])
    div2 = CFDivisor(g2, [("A", 1), ("B", 2), ("C", 3)])

    # Different vertex sets should make the divisors unequal
    assert div1 != div2
