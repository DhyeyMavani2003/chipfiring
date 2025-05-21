import pytest
from chipfiring import CFGraph, CFDivisor, CFiringScript, CFLaplacian, Vertex
from collections import defaultdict


@pytest.fixture
def simple_graph():
    """Provides a simple graph K3 with single edges for testing."""
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
def initial_divisor_simple(simple_graph):
    """Provides an initial divisor for the simple graph."""
    degrees = [("v1", 5), ("v2", 0), ("v3", -2)]
    return CFDivisor(simple_graph, degrees)


@pytest.fixture
def firing_script_simple(simple_graph):
    """Provides a firing script for the simple graph."""
    script = {"v1": 1, "v2": -1}  # v1 fires once, v2 borrows once
    return CFiringScript(simple_graph, script)


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


# --- Test CFLaplacian Initialization ---
def test_cflaplacian_init(simple_graph):
    """Test CFLaplacian initialization."""
    laplacian = CFLaplacian(simple_graph)
    assert laplacian.graph == simple_graph


# --- Test _construct_matrix ---
def test_construct_matrix_simple(simple_graph):
    """Test the _construct_matrix method for a simple K3 graph."""
    laplacian = CFLaplacian(simple_graph)
    matrix = laplacian._construct_matrix()
    v1, v2, v3 = Vertex("v1"), Vertex("v2"), Vertex("v3")

    # Expected Laplacian for K3 (single edges)
    #     v1 v2 v3
    # v1 [ 2 -1 -1 ]
    # v2 [-1  2 -1 ]
    # v3 [-1 -1  2 ]
    expected = {
        v1: defaultdict(int, {v1: 2, v2: -1, v3: -1}),
        v2: defaultdict(int, {v1: -1, v2: 2, v3: -1}),
        v3: defaultdict(int, {v1: -1, v2: -1, v3: 2}),
    }
    assert matrix == expected


def test_construct_matrix_multi_edge(graph_with_multi_edges):
    """Test _construct_matrix with multiple edges."""
    laplacian = CFLaplacian(graph_with_multi_edges)
    matrix = laplacian._construct_matrix()
    a, b, c = Vertex("a"), Vertex("b"), Vertex("c")

    # Expected Laplacian:
    #    a  b  c
    # a [2 -2  0]
    # b [-2 5 -3]
    # c [0 -3  3]
    vertices = {a, b, c}
    # Expected Laplacian values:
    expected_values = {
        (a, a): 2,
        (a, b): -2,
        (a, c): 0,
        (b, a): -2,
        (b, b): 5,
        (b, c): -3,
        (c, a): 0,
        (c, b): -3,
        (c, c): 3,
    }

    assert len(matrix) == len(vertices)  # Check if all vertices are keys

    for v_row in vertices:
        assert v_row in matrix
        assert isinstance(matrix[v_row], defaultdict)
        for v_col in vertices:
            # Accessing matrix[v_row][v_col] uses the defaultdict behavior
            assert (
                matrix[v_row][v_col] == expected_values[(v_row, v_col)]
            ), f"Mismatch at ({v_row.name}, {v_col.name}): Expected {expected_values[(v_row, v_col)]}, got {matrix[v_row][v_col]}"


# --- Test apply method ---
def test_apply_laplacian(simple_graph, initial_divisor_simple, firing_script_simple):
    """Test applying the Laplacian with a firing script."""
    laplacian = CFLaplacian(simple_graph)
    result_divisor = laplacian.apply(initial_divisor_simple, firing_script_simple)

    # D' = D - L*s
    # D = [5, 0, -2]
    # s = [1, -1, 0]
    # L*s = [ 2*1 + (-1)*(-1) + (-1)*0 ] = [ 2 + 1 + 0 ] = [ 3 ]
    #       [(-1)*1 +  2*(-1) + (-1)*0 ] = [-1 - 2 + 0 ] = [-3 ]
    #       [(-1)*1 + (-1)*(-1) +  2*0 ] = [-1 + 1 + 0 ] = [ 0 ]
    # L*s = [3, -3, 0]
    # D' = [5, 0, -2] - [3, -3, 0] = [5-3, 0-(-3), -2-0] = [2, 3, -2]

    assert result_divisor.get_degree("v1") == 2
    assert result_divisor.get_degree("v2") == 3
    assert result_divisor.get_degree("v3") == -2
    assert (
        result_divisor.get_total_degree() == initial_divisor_simple.get_total_degree()
    )


def test_apply_laplacian_zero_script(simple_graph, initial_divisor_simple):
    """Test apply with a zero firing script."""
    laplacian = CFLaplacian(simple_graph)
    zero_script = CFiringScript(simple_graph, {})
    result_divisor = laplacian.apply(initial_divisor_simple, zero_script)

    # D' = D - L*0 = D
    assert result_divisor.get_degree("v1") == 5
    assert result_divisor.get_degree("v2") == 0
    assert result_divisor.get_degree("v3") == -2
    assert (
        result_divisor.get_total_degree() == initial_divisor_simple.get_total_degree()
    )


def test_laplacian_equivalent_set_fire_sequence(
    sequence_test_graph, sequence_test_initial_divisor
):
    """Test that applying the Laplacian with a net script achieves the same result as a sequence of set_fire calls."""
    graph = sequence_test_graph
    initial_divisor = sequence_test_initial_divisor
    laplacian = CFLaplacian(graph)

    # This net firing script should yield the same result as the
    # set_fire sequence: fire({A,E,C}), fire({A,E,C}), fire({B,C})
    # Calculated equivalent script: A=0, B=-1, C=1, E=0
    script_dict = {"Alice": 2, "Bob": 1, "Charlie": 3, "Elise": 2}
    firing_script = CFiringScript(graph, script_dict)

    # Apply the script via the Laplacian
    result_divisor = laplacian.apply(initial_divisor, firing_script)

    # Expected final state from test_set_fire_sequence: A=2, B=0, C=0, E=0
    assert result_divisor.get_degree("Alice") == 2
    assert result_divisor.get_degree("Bob") == 0
    assert result_divisor.get_degree("Charlie") == 0
    assert result_divisor.get_degree("Elise") == 0
    assert result_divisor.get_total_degree() == initial_divisor.get_total_degree()


def test_laplacian_apply_specific_script(
    sequence_test_graph, sequence_test_initial_divisor
):
    """Test applying the Laplacian with a specific firing script."""
    graph = sequence_test_graph
    initial_divisor = sequence_test_initial_divisor
    laplacian = CFLaplacian(graph)

    # Specific script to test
    script_dict = {"Alice": -1, "Bob": -2, "Charlie": 0, "Elise": -1}
    firing_script = CFiringScript(graph, script_dict)

    # Apply the script via the Laplacian
    # D' = D0 - L*s
    # D0 = (A=2, B=-3, C=4, E=-1)
    # s = (A=-1, B=-2, C=0, E=-1)
    # L*s = (A=0, B=-3, C=4, E=-1)  (Calculated separately)
    # D' = D0 - L*s = (A=2-0, B=-3-(-3), C=4-4, E=-1-(-1)) = (A=2, B=0, C=0, E=0)
    result_divisor = laplacian.apply(initial_divisor, firing_script)

    # Expected final state
    assert result_divisor.get_degree("Alice") == 2
    assert result_divisor.get_degree("Bob") == 0
    assert result_divisor.get_degree("Charlie") == 0
    assert result_divisor.get_degree("Elise") == 0
    assert result_divisor.get_total_degree() == initial_divisor.get_total_degree()


# --- Test get_matrix_entry ---
def test_get_matrix_entry_simple(simple_graph):
    """Test get_matrix_entry for the simple K3 graph."""
    laplacian = CFLaplacian(simple_graph)
    # Diagonal
    assert laplacian.get_matrix_entry("v1", "v1") == 2
    assert laplacian.get_matrix_entry("v2", "v2") == 2
    assert laplacian.get_matrix_entry("v3", "v3") == 2
    # Off-diagonal (neighbors)
    assert laplacian.get_matrix_entry("v1", "v2") == -1
    assert laplacian.get_matrix_entry("v2", "v1") == -1
    assert laplacian.get_matrix_entry("v2", "v3") == -1
    assert laplacian.get_matrix_entry("v3", "v2") == -1
    assert laplacian.get_matrix_entry("v1", "v3") == -1
    assert laplacian.get_matrix_entry("v3", "v1") == -1


def test_get_matrix_entry_multi_edge(graph_with_multi_edges):
    """Test get_matrix_entry with multiple edges."""
    laplacian = CFLaplacian(graph_with_multi_edges)
    assert laplacian.get_matrix_entry("a", "a") == 2
    assert (
        laplacian.get_matrix_entry("b", "b") == 5
    )  # valence(a,b) + valence(b,c) = 2 + 3
    assert laplacian.get_matrix_entry("c", "c") == 3
    assert laplacian.get_matrix_entry("a", "b") == -2
    assert laplacian.get_matrix_entry("b", "a") == -2
    assert laplacian.get_matrix_entry("b", "c") == -3
    assert laplacian.get_matrix_entry("c", "b") == -3
    # Off-diagonal (non-neighbors)
    assert laplacian.get_matrix_entry("a", "c") == 0
    assert laplacian.get_matrix_entry("c", "a") == 0


def test_get_matrix_entry_invalid_vertex(simple_graph):
    """Test get_matrix_entry with non-existent vertices."""
    laplacian = CFLaplacian(simple_graph)
    with pytest.raises(
        ValueError, match="Both vertex names must correspond to vertices in the graph."
    ):
        laplacian.get_matrix_entry("v1", "v4")
    with pytest.raises(
        ValueError, match="Both vertex names must correspond to vertices in the graph."
    ):
        laplacian.get_matrix_entry("v4", "v1")
    with pytest.raises(
        ValueError, match="Both vertex names must correspond to vertices in the graph."
    ):
        laplacian.get_matrix_entry("v4", "v5")


# --- Test get_reduced_matrix ---
def test_get_reduced_matrix(simple_graph):
    """Test get_reduced_matrix for a simple graph."""
    laplacian = CFLaplacian(simple_graph)
    # Reduce matrix with respect to v1
    reduced = laplacian.get_reduced_matrix(Vertex("v1"))

    # The original full Laplacian for K3 (simple_graph) is:
    #     v1 v2 v3
    # v1 [ 2 -1 -1 ]
    # v2 [-1  2 -1 ]
    # v3 [-1 -1  2 ]

    # The reduced Laplacian (without v1) should be:
    #     v2 v3
    # v2 [ 2 -1 ]
    # v3 [-1  2 ]

    v2, v3 = Vertex("v2"), Vertex("v3")
    assert v2 in reduced
    assert v3 in reduced
    assert Vertex("v1") not in reduced

    assert reduced[v2][v2] == 2
    assert reduced[v2][v3] == -1
    assert reduced[v3][v2] == -1
    assert reduced[v3][v3] == 2


def test_get_reduced_matrix_multi_edge(graph_with_multi_edges):
    """Test get_reduced_matrix with multiple edges."""
    laplacian = CFLaplacian(graph_with_multi_edges)
    # Reduce matrix with respect to b
    reduced = laplacian.get_reduced_matrix(Vertex("b"))

    # The original full Laplacian is:
    #    a  b  c
    # a [2 -2  0]
    # b [-2 5 -3]
    # c [0 -3  3]

    # The reduced Laplacian (without b) should be:
    #    a  c
    # a [2  0]
    # c [0  3]

    a, c = Vertex("a"), Vertex("c")
    assert a in reduced
    assert c in reduced
    assert Vertex("b") not in reduced

    assert reduced[a][a] == 2
    assert reduced[a][c] == 0
    assert reduced[c][a] == 0
    assert reduced[c][c] == 3


# --- Test apply_reduced_matrix ---
def test_apply_reduced_matrix_simple(simple_graph, initial_divisor_simple):
    """Test applying a reduced Laplacian matrix on a simple graph."""
    laplacian = CFLaplacian(simple_graph)
    q = Vertex("v1")

    # Get the reduced matrix (removing v1)
    reduced_matrix = laplacian.get_reduced_matrix(q)

    # Apply the reduced matrix to the divisor
    result_degrees = laplacian.apply_reduced_matrix_inv_floor_optimization(
        initial_divisor_simple, reduced_matrix, q
    )

    # Convert result list to dict for easier testing
    result_dict = {name: degree for name, degree in result_degrees}

    assert "v1" not in result_dict
    assert result_dict["v2"] == 0
    assert result_dict["v3"] == 1


def test_apply_reduced_matrix_multi_edge(graph_with_multi_edges):
    """Test applying a reduced Laplacian matrix on a graph with multiple edges."""
    laplacian = CFLaplacian(graph_with_multi_edges)

    # Create a divisor
    divisor = CFDivisor(graph_with_multi_edges, [("a", 3), ("b", 0), ("c", -1)])

    # Reduce with respect to vertex 'b'
    q = Vertex("b")
    reduced_matrix = laplacian.get_reduced_matrix(q)

    # Apply the reduced matrix
    result_degrees = laplacian.apply_reduced_matrix_inv_floor_optimization(divisor, reduced_matrix, q)

    # Convert result list to dict for easier testing
    result_dict = {name: degree for name, degree in result_degrees}

    assert "b" not in result_dict
    assert result_dict["a"] == 1
    assert result_dict["c"] == 2


def test_apply_reduced_matrix_complex_graph(
    sequence_test_graph, sequence_test_initial_divisor
):
    """Test applying a reduced Laplacian matrix on a more complex graph."""
    laplacian = CFLaplacian(sequence_test_graph)

    # Reduce with respect to vertex 'Bob'
    q = Vertex("Bob")
    reduced_matrix = laplacian.get_reduced_matrix(q)

    # Apply the reduced matrix
    result_degrees = laplacian.apply_reduced_matrix_inv_floor_optimization(
        sequence_test_initial_divisor, reduced_matrix, q
    )
    # Initial divisor: Alice=2, Bob=-3, Charlie=4, Elise=-1

    # Convert result list to dict for easier testing
    result_dict = {name: degree for name, degree in result_degrees}

    assert "Bob" not in result_dict
    assert "Alice" in result_dict
    assert "Charlie" in result_dict
    assert "Elise" in result_dict

    # Expected values based on actual implementation
    expected = {"Alice": 0, "Charlie": 2, "Elise": -1}

    for vertex, expected_degree in expected.items():
        assert (
            result_dict[vertex] == expected_degree
        ), f"For vertex {vertex}, expected {expected_degree} but got {result_dict[vertex]}"
