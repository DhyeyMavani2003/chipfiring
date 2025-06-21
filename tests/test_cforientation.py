import pytest
from chipfiring.CFOrientation import CFOrientation
from chipfiring.CFGraph import CFGraph
from chipfiring import CFDivisor
from chipfiring.CFDhar import DharAlgorithm
from chipfiring.algo import EWD


@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
    return CFGraph(vertices, edges)


@pytest.fixture
def simple_graph_k3():
    """Provides a simple K3 graph for testing."""
    vertices = {"v1", "v2", "v3"}
    edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
    return CFGraph(vertices, edges)


@pytest.fixture
def graph_with_multi_edges():
    """Provides a graph with multiple edges."""
    vertices = {"a", "b", "c"}
    # a==(2)==b, b==(3)==c
    edges = [("a", "b", 2), ("b", "c", 3)]
    return CFGraph(vertices, edges)


@pytest.fixture
def fully_oriented_k3(simple_graph_k3):
    """Provides a fully oriented K3 graph (v1->v2, v2->v3, v1->v3)."""
    orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
    return CFOrientation(simple_graph_k3, orientations)


@pytest.fixture
def partially_oriented_k3(simple_graph_k3):
    """Provides a partially oriented K3 graph (v1->v2 only)."""
    orientations = [("v1", "v2")]
    return CFOrientation(simple_graph_k3, orientations)


@pytest.fixture
def fully_oriented_multi(graph_with_multi_edges):
    """Provides a fully oriented graph with multi-edges (a->b, c->b)."""
    orientations = [("a", "b"), ("c", "b")]
    return CFOrientation(graph_with_multi_edges, orientations)


def test_orientation_creation(sample_graph):
    """Test basic orientation creation."""
    orientations = [("A", "B"), ("B", "C")]
    orientation = CFOrientation(sample_graph, orientations)

    # Test orientations were set correctly
    assert orientation.get_orientation("A", "B") == ("A", "B")
    assert orientation.get_orientation("B", "C") == ("B", "C")
    assert orientation.get_orientation("A", "C") is None  # No orientation set


def test_orientation_invalid_edge(sample_graph):
    """Test that using non-existent edges raises an error."""
    orientations = [("A", "B"), ("B", "D")]  # B-D edge doesn't exist

    with pytest.raises(ValueError, match="Edge B-D not found in graph"):
        CFOrientation(sample_graph, orientations)


def test_orientation_duplicate_edges(sample_graph):
    """Test that duplicate edge orientations raise an error."""
    orientations = [("A", "B"), ("B", "A")]  # Same edge, opposite directions

    with pytest.raises(ValueError, match="Multiple orientations specified for edge"):
        CFOrientation(sample_graph, orientations)


def test_orientation_states(sample_graph):
    """Test orientation states and their relationships."""
    orientations = [("A", "B")]
    orientation = CFOrientation(sample_graph, orientations)

    # Test source/sink relationships
    assert orientation.is_source("A", "B") is True
    assert orientation.is_sink("A", "B") is False
    assert orientation.is_source("B", "A") is False
    assert orientation.is_sink("B", "A") is True

    # Test unoriented edge
    assert orientation.is_source("A", "C") is None
    assert orientation.is_sink("A", "C") is None


def test_orientation_degrees(sample_graph):
    """Test in-degree and out-degree calculations."""
    # A->B (valence 2), A->C (valence 1)
    orientations = [("A", "B"), ("A", "C")]
    orientation = CFOrientation(sample_graph, orientations)

    # Test out-degrees
    assert orientation.get_out_degree("A") == 3  # 2 from A->B, 1 from A->C
    assert orientation.get_out_degree("B") == 0
    assert orientation.get_out_degree("C") == 0

    # Test in-degrees
    assert orientation.get_in_degree("A") == 0
    assert orientation.get_in_degree("B") == 2  # From A->B
    assert orientation.get_in_degree("C") == 1  # From A->C


def test_orientation_invalid_vertex(sample_graph):
    """Test operations with invalid vertices."""
    orientation = CFOrientation(sample_graph, [("A", "B")])

    # Test get_orientation with invalid vertex
    with pytest.raises(ValueError, match="Edge D-A not found in graph"):
        orientation.get_orientation("D", "A")

    # Test is_source with invalid vertex
    with pytest.raises(ValueError, match="Edge D-A not found in graph"):
        orientation.is_source("D", "A")

    # Test is_sink with invalid vertex
    with pytest.raises(ValueError, match="Edge D-A not found in graph"):
        orientation.is_sink("D", "A")

    # Test get_in_degree with invalid vertex
    with pytest.raises(ValueError, match="Vertex D not found in graph"):
        orientation.get_in_degree("D")

    # Test get_out_degree with invalid vertex
    with pytest.raises(ValueError, match="Vertex D not found in graph"):
        orientation.get_out_degree("D")


def test_orientation_edge_valence(sample_graph):
    """Test that edge valence is correctly considered in degree calculations."""
    # Orient the edge with valence 2 (A-B)
    orientation = CFOrientation(sample_graph, [("A", "B")])

    assert orientation.get_out_degree("A") == 2  # Valence of A-B is 2
    assert orientation.get_in_degree("B") == 2  # Valence of A-B is 2


def test_empty_orientation(sample_graph):
    """Test orientation with no initial orientations."""
    orientation = CFOrientation(sample_graph, [])

    # All edges should have no orientation
    assert orientation.get_orientation("A", "B") is None
    assert orientation.get_orientation("B", "C") is None
    assert orientation.get_orientation("A", "C") is None

    # All vertices should have zero in/out degrees
    assert orientation.get_in_degree("A") == 0
    assert orientation.get_out_degree("A") == 0
    assert orientation.get_in_degree("B") == 0
    assert orientation.get_out_degree("B") == 0
    assert orientation.get_in_degree("C") == 0
    assert orientation.get_out_degree("C") == 0


def test_cforientation_init_valid(simple_graph_k3):
    """Test CFOrientation initialization with valid orientations."""
    orientations = [("v1", "v2"), ("v3", "v2")]
    orientation = CFOrientation(simple_graph_k3, orientations)
    assert orientation.get_orientation("v1", "v2") == ("v1", "v2")
    assert orientation.get_orientation("v2", "v3") == ("v3", "v2")
    assert orientation.get_orientation("v1", "v3") is None  # Unoriented
    assert not orientation.is_full


def test_cforientation_init_full(fully_oriented_k3):
    """Test that a fully specified orientation is marked as full."""
    assert fully_oriented_k3.is_full


def test_cforientation_init_invalid_edge(simple_graph_k3):
    """Test init with an orientation for a non-existent edge."""
    orientations = [("v1", "v4")]  # v4 is not a vertex
    with pytest.raises(ValueError, match="Edge v1-v4 not found in graph"):
        CFOrientation(simple_graph_k3, orientations)

    orientations = [("v1", "v1")]  # Edge v1-v1 doesn't exist (no self-loops)
    with pytest.raises(ValueError, match="Edge v1-v1 not found in graph"):
        CFOrientation(simple_graph_k3, orientations)


def test_cforientation_init_duplicate_orientation(simple_graph_k3):
    """Test init with multiple orientations for the same edge."""
    orientations = [("v1", "v2"), ("v2", "v1")]
    with pytest.raises(
        ValueError, match="Multiple orientations specified for edge v1-v2"
    ):
        CFOrientation(simple_graph_k3, orientations)
    orientations = [("v1", "v2"), ("v1", "v2")]  # Implicit duplicate
    with pytest.raises(
        ValueError, match="Multiple orientations specified for edge v1-v2"
    ):
        CFOrientation(simple_graph_k3, orientations)


def test_get_orientation(fully_oriented_k3, partially_oriented_k3):
    """Test the get_orientation method."""
    # Fully oriented
    assert fully_oriented_k3.get_orientation("v1", "v2") == ("v1", "v2")
    assert fully_oriented_k3.get_orientation("v2", "v1") == (
        "v1",
        "v2",
    )  # Order doesn't matter
    assert fully_oriented_k3.get_orientation("v2", "v3") == ("v2", "v3")
    assert fully_oriented_k3.get_orientation("v1", "v3") == ("v1", "v3")

    # Partially oriented
    assert partially_oriented_k3.get_orientation("v1", "v2") == ("v1", "v2")
    assert partially_oriented_k3.get_orientation("v2", "v3") is None
    assert partially_oriented_k3.get_orientation("v1", "v3") is None


def test_get_orientation_invalid_edge(fully_oriented_k3):
    """Test get_orientation for non-existent edges."""
    with pytest.raises(ValueError, match="Edge v1-v4 not found in graph"):
        fully_oriented_k3.get_orientation("v1", "v4")
    with pytest.raises(ValueError, match="Edge v1-v1 not found in graph"):
        fully_oriented_k3.get_orientation("v1", "v1")


def test_is_source_sink(fully_oriented_k3, partially_oriented_k3):
    """Test the is_source and is_sink methods."""
    # Fully oriented (v1->v2, v2->v3, v1->v3)
    assert fully_oriented_k3.is_source("v1", "v2") is True
    assert fully_oriented_k3.is_sink("v1", "v2") is False
    assert fully_oriented_k3.is_source("v2", "v1") is False  # v1 is source
    assert fully_oriented_k3.is_sink("v2", "v1") is True

    assert fully_oriented_k3.is_source("v2", "v3") is True
    assert fully_oriented_k3.is_sink("v3", "v2") is True

    assert fully_oriented_k3.is_source("v1", "v3") is True
    assert fully_oriented_k3.is_sink("v3", "v1") is True

    # Partially oriented (v1->v2 only)
    assert partially_oriented_k3.is_source("v1", "v2") is True
    assert partially_oriented_k3.is_sink("v2", "v1") is True
    assert partially_oriented_k3.is_source("v2", "v3") is None  # Unoriented
    assert partially_oriented_k3.is_sink("v2", "v3") is None
    assert partially_oriented_k3.is_source("v1", "v3") is None
    assert partially_oriented_k3.is_sink("v1", "v3") is None


def test_get_in_out_degree(fully_oriented_k3, fully_oriented_multi):
    """Test get_in_degree and get_out_degree."""
    # K3: v1->v2, v2->v3, v1->v3
    assert fully_oriented_k3.get_in_degree("v1") == 0
    assert fully_oriented_k3.get_out_degree("v1") == 2
    assert fully_oriented_k3.get_in_degree("v2") == 1  # from v1
    assert fully_oriented_k3.get_out_degree("v2") == 1  # to v3
    assert fully_oriented_k3.get_in_degree("v3") == 2  # from v1, v2
    assert fully_oriented_k3.get_out_degree("v3") == 0

    # Multi-graph: a ->(2) b <-(3) c
    assert fully_oriented_multi.get_in_degree("a") == 0
    assert fully_oriented_multi.get_out_degree("a") == 2  # edge a-b has valence 2
    assert fully_oriented_multi.get_in_degree("b") == 2 + 3  # from a (2), from c (3)
    assert fully_oriented_multi.get_out_degree("b") == 0
    assert fully_oriented_multi.get_in_degree("c") == 0
    assert fully_oriented_multi.get_out_degree("c") == 3  # edge c-b has valence 3


def test_get_degree_invalid_vertex(fully_oriented_k3):
    """Test get_in_degree and get_out_degree with invalid vertex."""
    with pytest.raises(ValueError, match="Vertex v4 not found in graph"):
        fully_oriented_k3.get_in_degree("v4")
    with pytest.raises(ValueError, match="Vertex v4 not found in graph"):
        fully_oriented_k3.get_out_degree("v4")


def test_reverse_orientation(fully_oriented_k3, fully_oriented_multi):
    """Test reversing a full orientation."""
    # K3: v1->v2, v2->v3, v1->v3
    reversed_k3 = fully_oriented_k3.reverse()
    assert reversed_k3.is_full
    # Check reversed edges
    assert reversed_k3.get_orientation("v1", "v2") == ("v2", "v1")
    assert reversed_k3.get_orientation("v2", "v3") == ("v3", "v2")
    assert reversed_k3.get_orientation("v1", "v3") == ("v3", "v1")
    # Check degrees
    assert reversed_k3.get_in_degree("v1") == 2  # Original out-degree
    assert reversed_k3.get_out_degree("v1") == 0
    assert reversed_k3.get_in_degree("v2") == 1  # Original out-degree
    assert reversed_k3.get_out_degree("v2") == 1
    assert reversed_k3.get_in_degree("v3") == 0  # Original out-degree
    assert reversed_k3.get_out_degree("v3") == 2

    # Multi-graph: a ->(2) b <-(3) c
    reversed_multi = fully_oriented_multi.reverse()
    assert reversed_multi.is_full
    # Check reversed edges
    assert reversed_multi.get_orientation("a", "b") == ("b", "a")
    assert reversed_multi.get_orientation("b", "c") == ("b", "c")
    # Check degrees
    assert reversed_multi.get_in_degree("a") == 2  # Original out-degree
    assert reversed_multi.get_out_degree("a") == 0
    assert reversed_multi.get_in_degree("b") == 0  # Original out-degree
    assert reversed_multi.get_out_degree("b") == 2 + 3  # Original in-degree
    assert reversed_multi.get_in_degree("c") == 3  # Original out-degree
    assert reversed_multi.get_out_degree("c") == 0


def test_reverse_orientation_not_full(partially_oriented_k3):
    """Test that reversing a non-full orientation raises an error."""
    assert not partially_oriented_k3.is_full
    with pytest.raises(RuntimeError, match="Cannot reverse a not full orientation"):
        partially_oriented_k3.reverse()


def test_divisor_from_orientation(fully_oriented_k3, fully_oriented_multi):
    """Test creating a divisor from a full orientation."""
    # K3: v1->v2, v2->v3, v1->v3
    # In-degrees: v1=0, v2=1, v3=2
    divisor_k3 = fully_oriented_k3.divisor()
    assert isinstance(divisor_k3, CFDivisor)
    assert (
        divisor_k3.get_degree("v1") == fully_oriented_k3.get_in_degree("v1") - 1
    )  # 0 - 1 = -1
    assert (
        divisor_k3.get_degree("v2") == fully_oriented_k3.get_in_degree("v2") - 1
    )  # 1 - 1 = 0
    assert (
        divisor_k3.get_degree("v3") == fully_oriented_k3.get_in_degree("v3") - 1
    )  # 2 - 1 = 1
    # Total degree = -1 + 0 + 1 = 0. Genus = |E|-|V|+1 = 3-3+1 = 1. Expected total degree = 2g-2 = 0.
    assert divisor_k3.get_total_degree() == 0

    # Multi-graph: a ->(2) b <-(3) c
    # In-degrees: a=0, b=5, c=0
    divisor_multi = fully_oriented_multi.divisor()
    assert isinstance(divisor_multi, CFDivisor)
    assert (
        divisor_multi.get_degree("a") == fully_oriented_multi.get_in_degree("a") - 1
    )  # 0 - 1 = -1
    assert (
        divisor_multi.get_degree("b") == fully_oriented_multi.get_in_degree("b") - 1
    )  # 5 - 1 = 4
    assert (
        divisor_multi.get_degree("c") == fully_oriented_multi.get_in_degree("c") - 1
    )  # 0 - 1 = -1
    # Total degree = -1 + 4 - 1 = 2. Genus = |E|-|V|+1 = (2+3)-3+1 = 3. Expected total degree = 2g-2 = 2*3-2 = 4.
    # Hmm, the total degree formula 2g-2 might only apply for specific divisor classes?
    # Let's just check the sum directly.
    assert divisor_multi.get_total_degree() == 2


def test_divisor_from_orientation_not_full(partially_oriented_k3):
    """Test that creating a divisor from a non-full orientation raises an error."""
    assert not partially_oriented_k3.is_full
    with pytest.raises(
        RuntimeError, match="Cannot create divisor: Orientation is not full"
    ):
        partially_oriented_k3.divisor()


def test_canonical_divisor(simple_graph_k3, graph_with_multi_edges):
    """Test creating the canonical divisor."""
    # K3: Valences v1=2, v2=2, v3=2
    orientation_k3 = CFOrientation(simple_graph_k3, [])  # Orientation doesn't matter
    canonical_k3 = orientation_k3.canonical_divisor()
    assert isinstance(canonical_k3, CFDivisor)
    assert (
        canonical_k3.get_degree("v1") == simple_graph_k3.get_valence("v1") - 2
    )  # 2 - 2 = 0
    assert (
        canonical_k3.get_degree("v2") == simple_graph_k3.get_valence("v2") - 2
    )  # 2 - 2 = 0
    assert (
        canonical_k3.get_degree("v3") == simple_graph_k3.get_valence("v3") - 2
    )  # 2 - 2 = 0
    assert canonical_k3.get_total_degree() == 0

    # Multi-graph: Valences a=2, b=5, c=3
    orientation_multi = CFOrientation(
        graph_with_multi_edges, []
    )  # Orientation doesn't matter
    canonical_multi = orientation_multi.canonical_divisor()
    assert isinstance(canonical_multi, CFDivisor)
    assert (
        canonical_multi.get_degree("a") == graph_with_multi_edges.get_valence("a") - 2
    )  # 2 - 2 = 0
    assert (
        canonical_multi.get_degree("b") == graph_with_multi_edges.get_valence("b") - 2
    )  # 5 - 2 = 3
    assert (
        canonical_multi.get_degree("c") == graph_with_multi_edges.get_valence("c") - 2
    )  # 3 - 2 = 1
    assert canonical_multi.get_total_degree() == 0 + 3 + 1  # 4
    # Check against 2g-2: g = |E|-|V|+1 = (2+3)-3+1 = 3. 2g-2 = 2*3-2 = 4. Matches.


# Add tests for orientation tracking in Dhar's algorithm
@pytest.fixture
def dhar_test_graph():
    """Create a simple graph for testing orientation tracking."""
    G = CFGraph({"A", "B", "C", "D"}, [])
    G.add_edge("A", "B", 1)
    G.add_edge("B", "C", 1)
    G.add_edge("C", "D", 1)
    G.add_edge("D", "A", 1)
    G.add_edge("A", "C", 1)
    return G


def test_dhar_with_orientation_tracking(dhar_test_graph):
    """Test that Dhar's algorithm correctly tracks orientations."""
    # Create a configuration where some vertices should burn
    config = CFDivisor(dhar_test_graph, [("A", 2), ("B", 0), ("C", 0), ("D", 0)])

    # Run Dhar's algorithm with orientation tracking
    dhar = DharAlgorithm(dhar_test_graph, config, "B")
    _, orientation = dhar.run()

    assert orientation.get_orientation("A", "B") == ("B", "A")
    assert orientation.get_orientation("B", "C") == ("B", "C")
    assert orientation.get_orientation("C", "D") == ("C", "D")
    assert orientation.get_orientation("D", "A") == ("D", "A")
    assert orientation.get_orientation("A", "C") == ("C", "A")


def test_ewd_with_orientation_tracking(dhar_test_graph):
    """Test that EWD returns a full orientation."""
    # Create a configuration that should be winnable
    config = CFDivisor(dhar_test_graph, [("A", 3), ("B", -1), ("C", 0), ("D", 0)])

    # Run EWD
    is_winnable, q_reduced, orientation, _ = EWD(dhar_test_graph, config)

    # Check that the orientation is full
    assert orientation.check_fullness()

    # Check that orientations follow our burning process expectations
    assert orientation.get_orientation("A", "B") == ("B", "A")
    assert orientation.get_orientation("A", "C") == ("A", "C")
    assert orientation.get_orientation("A", "D") == ("A", "D")
    assert orientation.get_orientation("B", "C") == ("B", "C")
    assert orientation.get_orientation("C", "D") == ("C", "D")

    # Every edge should have an orientation
    for v1 in dhar_test_graph.vertices:
        for v2 in dhar_test_graph.graph[v1]:
            if v1 < v2:  # Check each edge only once
                assert orientation.get_orientation(v1.name, v2.name) is not None


def test_ewd_orientation_fire_spread(dhar_test_graph):
    """Test that orientation follows the fire spread direction."""
    # B will be fire source
    config = CFDivisor(dhar_test_graph, [("A", 2), ("B", 0), ("C", 1), ("D", 2)])

    # Run EWD
    _, _, orientation, _ = EWD(dhar_test_graph, config)

    assert orientation.get_orientation("A", "B") == ("B", "A")
    assert orientation.get_orientation("A", "C") == ("C", "A")
    assert orientation.get_orientation("A", "D") == ("D", "A")
    assert orientation.get_orientation("B", "C") == ("B", "C")
    assert orientation.get_orientation("C", "D") == ("C", "D")


def test_set_orientation_directly(sample_graph):
    """Test the set_orientation method directly to ensure proper state transitions."""
    from chipfiring.CFOrientation import OrientationState, Vertex

    orientation = CFOrientation(sample_graph, [])
    v_a = Vertex("A")
    v_b = Vertex("B")

    # Verify initial state
    assert orientation.orientation[v_a][v_b] == OrientationState.NO_ORIENTATION
    assert orientation.get_in_degree("A") == 0
    assert orientation.get_out_degree("A") == 0

    # Set orientation from NO_ORIENTATION to SOURCE_TO_SINK
    orientation.set_orientation(v_a, v_b, OrientationState.SOURCE_TO_SINK)
    assert orientation.orientation[v_a][v_b] == OrientationState.SOURCE_TO_SINK
    assert orientation.orientation[v_b][v_a] == OrientationState.SINK_TO_SOURCE
    assert orientation.get_out_degree("A") == 2  # A-B edge has valence 2
    assert orientation.get_in_degree("B") == 2

    # Change orientation from SOURCE_TO_SINK to SINK_TO_SOURCE
    orientation.set_orientation(v_a, v_b, OrientationState.SINK_TO_SOURCE)
    assert orientation.orientation[v_a][v_b] == OrientationState.SINK_TO_SOURCE
    assert orientation.orientation[v_b][v_a] == OrientationState.SOURCE_TO_SINK
    assert orientation.get_in_degree("A") == 2
    assert orientation.get_out_degree("A") == 0
    assert orientation.get_out_degree("B") == 2
    assert orientation.get_in_degree("B") == 0

    # Change back to NO_ORIENTATION
    orientation.set_orientation(v_a, v_b, OrientationState.NO_ORIENTATION)
    assert orientation.orientation[v_a][v_b] == OrientationState.NO_ORIENTATION
    assert orientation.orientation[v_b][v_a] == OrientationState.NO_ORIENTATION
    assert orientation.get_in_degree("A") == 0
    assert orientation.get_out_degree("A") == 0
    assert orientation.get_in_degree("B") == 0
    assert orientation.get_out_degree("B") == 0
    assert orientation.is_full is False


def test_check_fullness_directly(simple_graph_k3):
    """Test the check_fullness method directly."""
    from chipfiring.CFOrientation import OrientationState, Vertex

    # Create a partially oriented graph
    orientation = CFOrientation(simple_graph_k3, [("v1", "v2")])

    # Verify initial state
    assert not orientation.is_full
    assert orientation.is_full_checked  # Should be set during initialization

    # Reset the flag to test if check_fullness updates it
    orientation.is_full_checked = False
    result = orientation.check_fullness()
    assert result is False
    assert orientation.is_full is False
    assert orientation.is_full_checked is True

    # Complete the orientation
    v2 = Vertex("v2")
    v3 = Vertex("v3")
    orientation.set_orientation(v2, v3, OrientationState.SOURCE_TO_SINK)

    v1 = Vertex("v1")
    orientation.set_orientation(v1, v3, OrientationState.SOURCE_TO_SINK)

    # Reset flag and test again
    orientation.is_full_checked = False
    result = orientation.check_fullness()
    assert result is True
    assert orientation.is_full is True
    assert orientation.is_full_checked is True


def test_is_full_updates(simple_graph_k3):
    """Test that the is_full flag is properly updated when edges are oriented."""
    from chipfiring.CFOrientation import OrientationState, Vertex

    # Create empty orientation
    orientation = CFOrientation(simple_graph_k3, [])
    assert not orientation.is_full

    # Orient all edges
    v1 = Vertex("v1")
    v2 = Vertex("v2")
    v3 = Vertex("v3")

    orientation.set_orientation(v1, v2, OrientationState.SOURCE_TO_SINK)
    # After setting one edge, is_full_checked should be False
    assert orientation.is_full_checked is False

    orientation.set_orientation(v2, v3, OrientationState.SOURCE_TO_SINK)
    orientation.set_orientation(v1, v3, OrientationState.SOURCE_TO_SINK)

    # Check if it's full now
    assert orientation.check_fullness() is True
    assert orientation.is_full is True

    # Now remove an orientation
    orientation.set_orientation(v1, v2, OrientationState.NO_ORIENTATION)
    # Setting to NO_ORIENTATION should directly set is_full to False
    assert orientation.is_full is False
    assert orientation.is_full_checked is True


def test_reverse_updates_fullness_check(fully_oriented_k3):
    """Test that the reverse method properly checks and maintains fullness."""
    reversed_orientation = fully_oriented_k3.reverse()

    # The reversed orientation should be full and have the flag set
    assert reversed_orientation.is_full is True
    assert reversed_orientation.is_full_checked is True
